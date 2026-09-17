#!/usr/bin/env python3
"""Install the bundled Claude or Codex agents and skills."""

import argparse
import filecmp
import json
import os
from pathlib import Path
import shutil
import sys


class InstallError(Exception):
    pass


def safe_path(path):
    """Return an absolute path after rejecting traversal and symlink components."""
    path = Path(path).expanduser()
    if ".." in path.parts:
        raise InstallError(f"unsafe path traversal: {path}")
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise InstallError(f"symlink path component is not allowed: {current}")
    return path


def require_directory(path, label):
    path = safe_path(path)
    if not path.is_dir():
        raise InstallError(f"missing {label} directory: {path}")
    return path


def source_files(source, destination):
    """Build copy pairs while refusing links and non-regular bundle entries."""
    pairs = []
    for root, directories, filenames in os.walk(source, followlinks=False):
        directories[:] = [name for name in directories if name != "__pycache__"]
        root_path = Path(root)
        for name in directories:
            candidate = root_path / name
            if candidate.is_symlink():
                raise InstallError(f"bundle contains a symlink: {candidate}")
        for name in filenames:
            if name == ".DS_Store" or name.endswith(".pyc"):
                continue
            candidate = root_path / name
            if candidate.is_symlink() or not candidate.is_file():
                raise InstallError(f"bundle entry is not a regular file: {candidate}")
            relative = candidate.relative_to(source)
            if ".." in relative.parts:
                raise InstallError(f"unsafe bundle path: {candidate}")
            pairs.append((candidate, destination / relative))
    return pairs


def check_destination(path):
    path = safe_path(path)
    current = Path(path.anchor)
    for part in path.parts[1:-1]:
        current /= part
        if current.exists() and not current.is_dir():
            raise InstallError(f"destination parent is not a directory: {current}")
    return path


def load_json(path, label):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InstallError(f"cannot read {label} JSON at {path}: {error}") from error
    if not isinstance(value, dict):
        raise InstallError(f"{label} JSON must contain an object: {path}")
    return value


def merged_settings(bundle_root, settings_path):
    hook_path = safe_path(bundle_root / "hooks" / "compact-reminder.json")
    if not hook_path.is_file():
        raise InstallError(f"missing hook file: {hook_path}")
    hook_config = load_json(hook_path, "hook")
    hook_groups = hook_config.get("hooks")
    handlers = hook_groups.get("SessionStart") if isinstance(hook_groups, dict) else None
    if not isinstance(handlers, list):
        raise InstallError(f"hook JSON must contain hooks.SessionStart list: {hook_path}")

    if settings_path.exists():
        settings = load_json(settings_path, "Claude settings")
    else:
        settings = {}
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError(f"Claude settings hooks must be an object: {settings_path}")
    existing = hooks.setdefault("SessionStart", [])
    if not isinstance(existing, list):
        raise InstallError(
            f"Claude settings hooks.SessionStart must be a list: {settings_path}"
        )
    for handler in handlers:
        if handler not in existing:
            existing.append(handler)
    return settings


def destinations(args):
    if args.project is not None:
        base = safe_path(args.project)
        if args.runtime == "claude":
            return base / ".claude" / "agents", base / ".claude" / "skills"
        return base / ".codex" / "agents", base / ".agents" / "skills"

    home = safe_path(os.environ.get("HOME", str(Path.home())))
    if args.runtime == "claude":
        claude_home = safe_path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude")
        return claude_home / "agents", claude_home / "skills"
    codex_home = safe_path(os.environ.get("CODEX_HOME") or home / ".codex")
    return codex_home / "agents", home / ".agents" / "skills"


def install(args):
    package_root = safe_path(Path(__file__).parent.parent)
    agents_dest, skills_dest = destinations(args)
    pairs = []
    if args.package in ("operations", "all"):
        bundle_root = require_directory(package_root / args.runtime, args.runtime + " bundle")
        pairs += source_files(require_directory(bundle_root / "agents", "agents"), agents_dest)
        pairs += source_files(require_directory(bundle_root / "skills", "skills"), skills_dest)
        pairs += source_files(
            require_directory(package_root / "evaluation-loop" / "skills", "evaluation loop"),
            skills_dest,
        )
    if args.package in ("red-team", "all"):
        red_root = package_root / "red-team"
        pairs += source_files(
            require_directory(red_root / args.runtime / "agents", "red-team agents"), agents_dest
        )
        pairs += source_files(require_directory(red_root / "skills", "red-team skill"), skills_dest)
    pending = []
    for source, raw_destination in pairs:
        destination = check_destination(raw_destination)
        if destination.exists():
            if not destination.is_file() or not filecmp.cmp(
                source, destination, shallow=False
            ):
                raise InstallError(
                    f"collision at {destination}; move or remove the existing file and retry"
                )
        else:
            pending.append((source, destination))

    settings_update = None
    if args.with_context_hook:
        settings_path = check_destination(agents_dest.parent / "settings.json")
        settings = merged_settings(bundle_root, settings_path)
        rendered = json.dumps(settings, ensure_ascii=False, indent=2) + "\n"
        if not settings_path.exists() or settings_path.read_text(encoding="utf-8") != rendered:
            settings_update = (settings_path, rendered)

    roots = sorted({agents_dest, skills_dest}, key=str)
    if args.dry_run:
        for root in roots:
            print(f"would install: {root}")
        if settings_update:
            print(f"would update: {settings_update[0]}")
        return

    for source, destination in pending:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    if settings_update:
        path, contents = settings_update
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    for root in roots:
        print(f"installed: {root}")
    if settings_update:
        print(f"updated: {settings_update[0]}")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", choices=("claude", "codex"))
    parser.add_argument("--package", choices=("operations", "red-team", "all"), default="operations")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--project", metavar="PATH")
    target.add_argument("--user", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--with-context-hook",
        action="store_true",
        help="merge the optional Claude context reminder hook",
    )
    args = parser.parse_args()
    if args.with_context_hook and args.runtime != "claude":
        parser.error("--with-context-hook is available only for claude")
    if args.with_context_hook and args.package == "red-team":
        parser.error("--with-context-hook requires the operations package")
    return args


def main():
    try:
        install(parse_args())
    except InstallError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
