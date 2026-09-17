#!/usr/bin/env python3
"""Validate, score, and append one independent evaluation round."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
MAX_ATTEMPTS = 3
PASS_THRESHOLD = 85.0
DIMENSIONS = {
    "intent": 30,
    "correctness": 30,
    "verification": 20,
    "clarity": 10,
    "efficiency": 10,
}
SEVERITIES = {"fatal", "high", "medium", "low"}
PROGRESS_KINDS = {"baseline", "resolved_defect", "added_evidence", "none"}
FINDING_STATUSES = {"confirmed", "needs_evidence", "refuted"}
STRONGEST_REVIEWERS = {"gpt-6-astra", "claude-fable-5-1"}


class EvaluationError(ValueError):
    pass


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvaluationError(f"{field} must be an object")
    return value


def _list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise EvaluationError(f"{field} must be an array")
    return value


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvaluationError(f"{field} must be a non-empty string")
    return value


def _nullable_number(value: Any, field: str) -> float | int | None:
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or (isinstance(value, float) and not math.isfinite(value))
        or value < 0
    ):
        raise EvaluationError(f"{field} must be a non-negative number or null")
    return value


def _evidence(value: Any, field: str) -> list[str]:
    items = _list(value, field)
    for index, item in enumerate(items):
        _text(item, f"{field}[{index}]")
    return items


def _validate_routing(doc: dict[str, Any]) -> dict[str, Any]:
    routing = _mapping(doc.get("routing"), "routing")
    for field in (
        "required_reviewer_model",
        "required_reviewer_effort",
        "actual_reviewer_model",
        "actual_reviewer_effort",
    ):
        _text(routing.get(field), f"routing.{field}")
    if not isinstance(routing.get("isolation_confirmed"), bool):
        raise EvaluationError("routing.isolation_confirmed must be boolean")
    if routing["required_reviewer_model"] not in STRONGEST_REVIEWERS:
        raise EvaluationError("required reviewer model is not a configured strongest reviewer")
    if routing["required_reviewer_effort"] != "xhigh":
        raise EvaluationError("required reviewer effort must be xhigh")
    if routing["required_reviewer_model"] != routing["actual_reviewer_model"]:
        raise EvaluationError("actual reviewer model does not match required model")
    if routing["required_reviewer_effort"] != routing["actual_reviewer_effort"]:
        raise EvaluationError("actual reviewer effort does not match required effort")
    return routing


def _validate_dimensions(doc: dict[str, Any]) -> tuple[dict[str, Any], float | None, bool]:
    dimensions = _mapping(doc.get("dimensions"), "dimensions")
    if set(dimensions) != set(DIMENSIONS):
        raise EvaluationError("dimensions must contain exactly the fixed rubric dimensions")
    weighted_total = 0.0
    has_unknown = False
    all_at_least_three = True
    for name, weight in DIMENSIONS.items():
        item = _mapping(dimensions[name], f"dimensions.{name}")
        score = item.get("score")
        evidence = _evidence(item.get("evidence"), f"dimensions.{name}.evidence")
        if score is None:
            has_unknown = True
            all_at_least_three = False
            continue
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 4:
            raise EvaluationError(f"dimensions.{name}.score must be an integer 0..4 or null")
        if not evidence:
            raise EvaluationError(f"dimensions.{name} has a score without evidence")
        weighted_total += score / 4 * weight
        all_at_least_three = all_at_least_three and score >= 3
    return dimensions, None if has_unknown else round(weighted_total, 2), all_at_least_three


def _validate_mandatory(doc: dict[str, Any]) -> tuple[list[dict[str, Any]], bool, bool]:
    criteria = _list(doc.get("mandatory_criteria"), "mandatory_criteria")
    if not criteria:
        raise EvaluationError("mandatory_criteria must not be empty")
    seen: set[str] = set()
    all_passed = True
    has_unknown = False
    for index, raw in enumerate(criteria):
        item = _mapping(raw, f"mandatory_criteria[{index}]")
        criterion_id = _text(item.get("id"), f"mandatory_criteria[{index}].id")
        if criterion_id in seen:
            raise EvaluationError(f"duplicate mandatory criterion: {criterion_id}")
        seen.add(criterion_id)
        passed = item.get("passed")
        if passed is not None and not isinstance(passed, bool):
            raise EvaluationError(f"mandatory_criteria[{index}].passed must be boolean or null")
        evidence = _evidence(item.get("evidence"), f"mandatory_criteria[{index}].evidence")
        if passed is not None and not evidence:
            raise EvaluationError(f"mandatory criterion {criterion_id} has a result without evidence")
        has_unknown = has_unknown or passed is None
        all_passed = all_passed and passed is True
    return criteria, all_passed, has_unknown


def _validate_findings(doc: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], bool]:
    findings = _list(doc.get("findings"), "findings")
    seen: set[str] = set()
    blockers: list[str] = []
    needs_evidence = False
    for index, raw in enumerate(findings):
        item = _mapping(raw, f"findings[{index}]")
        finding_id = _text(item.get("id"), f"findings[{index}].id")
        if finding_id in seen:
            raise EvaluationError(f"duplicate finding: {finding_id}")
        seen.add(finding_id)
        severity = item.get("severity")
        if severity not in SEVERITIES:
            raise EvaluationError(f"findings[{index}].severity is invalid")
        status = item.get("status")
        if status not in FINDING_STATUSES:
            raise EvaluationError(f"findings[{index}].status is invalid")
        for field in ("reproducible", "resolved"):
            if not isinstance(item.get(field), bool):
                raise EvaluationError(f"findings[{index}].{field} must be boolean")
        confidence = item.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise EvaluationError(f"findings[{index}].confidence must be between 0 and 1")
        evidence = _evidence(item.get("evidence"), f"findings[{index}].evidence")
        if status in {"confirmed", "refuted"} and not evidence:
            raise EvaluationError(f"{status} finding {finding_id} requires evidence")
        if status == "refuted" and not item["resolved"]:
            raise EvaluationError(f"refuted finding {finding_id} must be resolved")
        if status == "needs_evidence" and item["resolved"]:
            raise EvaluationError(f"finding {finding_id} cannot be resolved while evidence is missing")
        needs_evidence = needs_evidence or status == "needs_evidence"
        if status == "confirmed" and not item["resolved"] and severity in {"fatal", "high", "medium"}:
            blockers.append(finding_id)
    return findings, blockers, needs_evidence


def _history_for_evaluation(history: list[dict[str, Any]], evaluation_id: str) -> list[dict[str, Any]]:
    return sorted(
        (record for record in history if record.get("evaluation_id") == evaluation_id),
        key=lambda record: record.get("attempt", 0),
    )


def evaluate_round(doc: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    if doc.get("schema_version") != SCHEMA_VERSION:
        raise EvaluationError(f"schema_version must be {SCHEMA_VERSION}")
    identifiers = {
        field: _text(doc.get(field), field)
        for field in (
            "evaluation_id",
            "task_id",
            "task_fingerprint",
            "candidate_fingerprint",
            "evidence_fingerprint",
            "rubric_version",
        )
    }
    attempt = doc.get("attempt")
    if isinstance(attempt, bool) or not isinstance(attempt, int) or not 1 <= attempt <= MAX_ATTEMPTS:
        raise EvaluationError(f"attempt must be an integer 1..{MAX_ATTEMPTS}")
    prior = _history_for_evaluation(history, identifiers["evaluation_id"])
    if any(record.get("attempt") == attempt for record in prior):
        raise EvaluationError("duplicate evaluation round; existing records are never overwritten")
    if attempt != len(prior) + 1:
        raise EvaluationError("attempts must be appended in order without gaps")
    if prior and prior[-1].get("decision") in {"PASS", "STOP_NOT_COMPLETE"}:
        raise EvaluationError("the evaluation already has a terminal round")

    progress_kind = doc.get("progress_kind")
    if progress_kind not in PROGRESS_KINDS:
        raise EvaluationError(f"progress_kind must be one of {sorted(PROGRESS_KINDS)}")
    if attempt == 1 and progress_kind != "baseline":
        raise EvaluationError("attempt 1 must be the baseline")
    if attempt > 1 and progress_kind == "baseline":
        raise EvaluationError("only attempt 1 may be the baseline")
    if prior:
        previous = prior[-1]
        for field in ("task_id", "task_fingerprint", "rubric_version"):
            if previous.get(field) != identifiers[field]:
                raise EvaluationError(f"{field} changed; start a new evaluation_id and baseline")
        same_candidate = previous.get("candidate_fingerprint") == identifiers["candidate_fingerprint"]
        same_evidence = previous.get("evidence_fingerprint") == identifiers["evidence_fingerprint"]
        if same_candidate and same_evidence:
            raise EvaluationError("candidate and evidence are unchanged; score-only retries are forbidden")
        if progress_kind == "resolved_defect" and same_candidate:
            raise EvaluationError("resolved_defect requires a new candidate fingerprint")
        if progress_kind == "added_evidence" and same_evidence:
            raise EvaluationError("added_evidence requires a new evidence fingerprint")

    routing = _validate_routing(doc)
    loop = _mapping(doc.get("loop"), "loop")
    _text(loop.get("model"), "loop.model")
    _text(loop.get("effort"), "loop.effort")
    dimensions, weighted_total, dimensions_pass = _validate_dimensions(doc)
    criteria, mandatory_pass, mandatory_unknown = _validate_mandatory(doc)
    findings, finding_blockers, finding_needs_evidence = _validate_findings(doc)
    fix_targets = _evidence(doc.get("fix_targets"), "fix_targets")
    runtime = _mapping(doc.get("runtime"), "runtime")
    duration = _nullable_number(runtime.get("duration_seconds"), "runtime.duration_seconds")
    cost = _nullable_number(runtime.get("cost_usd"), "runtime.cost_usd")
    input_tokens = _nullable_number(runtime.get("input_tokens"), "runtime.input_tokens")
    output_tokens = _nullable_number(runtime.get("output_tokens"), "runtime.output_tokens")

    if prior:
        previous_routing = _mapping(prior[-1].get("routing"), "history.routing")
        for field in ("required_reviewer_model", "required_reviewer_effort"):
            if previous_routing.get(field) != routing[field]:
                raise EvaluationError(f"routing.{field} changed; start a new evaluation_id and baseline")
        previous_criteria = {
            item.get("id") for item in _list(prior[-1].get("mandatory_criteria"), "history.mandatory_criteria")
        }
        current_criteria = {item["id"] for item in criteria}
        if previous_criteria != current_criteria:
            raise EvaluationError("mandatory criterion IDs changed; start a new evaluation_id and baseline")

    unknown = (
        weighted_total is None
        or mandatory_unknown
        or finding_needs_evidence
        or not routing["isolation_confirmed"]
    )
    gates = {
        "threshold_met": weighted_total is not None and weighted_total >= PASS_THRESHOLD,
        "dimensions_met": dimensions_pass,
        "mandatory_met": mandatory_pass,
        "no_unresolved_high_or_medium": not finding_blockers,
        "required_evidence_complete": not unknown,
        "review_isolation_confirmed": routing["isolation_confirmed"],
        "reviewer_routing_confirmed": True,
    }
    passed = all(gates.values())
    stall_count = 0
    for record in reversed(prior + [{"progress_kind": progress_kind}]):
        if record.get("progress_kind") != "none":
            break
        stall_count += 1

    if stall_count >= 2:
        decision = "STOP_NOT_COMPLETE"
    elif passed:
        decision = "PASS"
    elif attempt >= MAX_ATTEMPTS:
        decision = "STOP_NOT_COMPLETE"
    elif unknown:
        decision = "NEEDS_EVIDENCE"
    else:
        decision = "IMPROVE"
    if decision != "PASS" and not fix_targets:
        raise EvaluationError("a non-PASS round requires at least one bounded fix target")

    return {
        "schema_version": SCHEMA_VERSION,
        **identifiers,
        "attempt": attempt,
        "routing": routing,
        "loop": loop,
        "progress_kind": progress_kind,
        "rubric": {"weights": DIMENSIONS, "pass_threshold": PASS_THRESHOLD},
        "dimensions": dimensions,
        "weighted_total": weighted_total,
        "mandatory_criteria": criteria,
        "findings": findings,
        "gates": gates,
        "evaluation_status": "NEEDS_EVIDENCE" if unknown else ("PASS" if passed else "FAIL"),
        "decision": decision,
        "fix_targets": fix_targets,
        "stall_count": stall_count,
        "runtime": {
            "duration_seconds": duration,
            "cost_usd": cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
        "synthetic_example": doc.get("synthetic_example") is True,
    }


def _reject_nonfinite(value: str) -> None:
    raise EvaluationError(f"non-finite JSON number is not allowed: {value}")


def _json_loads(value: str) -> Any:
    return json.loads(value, parse_constant=_reject_nonfinite)


def _lock(handle: Any) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _unlock(handle: Any) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _read_history(handle: Any) -> list[dict[str, Any]]:
    handle.seek(0)
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(handle, 1):
        if not line.strip():
            continue
        try:
            record = _json_loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"invalid history JSON on line {line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise EvaluationError(f"history line {line_number} must be an object")
        records.append(record)
    return records


def append_round(input_path: Path, history_path: Path) -> dict[str, Any]:
    try:
        doc = _json_loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read input: {exc}") from exc
    if not isinstance(doc, dict):
        raise EvaluationError("input must be a JSON object")
    history_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = history_path.with_name(history_path.name + ".lock")
    with lock_path.open("a+b") as lock_handle:
        _lock(lock_handle)
        try:
            with history_path.open("a+", encoding="utf-8") as handle:
                history = _read_history(handle)
                record = evaluate_round(doc, history)
                handle.seek(0, os.SEEK_END)
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            _unlock(lock_handle)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--history", required=True, type=Path)
    args = parser.parse_args()
    try:
        record = append_round(args.input, args.history)
    except EvaluationError as exc:
        parser.error(str(exc))
    print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
