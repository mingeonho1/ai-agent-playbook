---
name: claude-agent-operations
description: Plan and run bounded multi-agent work with the configured Fable and Claude models. Use for work that benefits from parallel research, implementation, review, or mechanical execution.
metadata:
  short-description: Efficient Fable and Claude agent orchestration
---

# Claude Agent Operations

Use this skill to turn a concrete request into a small, auditable agent plan. Optimize for a correct deliverable with the least repeated context, tool use, and high-reasoning time.

## Route work by judgment cost

| Work | Route | Configured model | Effort |
| --- | --- | --- | --- |
| Scope, plan, source conflicts, architecture, difficult tradeoffs | `deep-reasoner` through Fable | Claude Opus 5.1 | max |
| Implementation, fixes, rendering, substantive verification | `executor` | Claude Opus 5.0 | xhigh |
| File inventory, commands, builds, exports, dimensions, packaging | `runner` | Claude Sonnet 5 | medium |

Treat this as the configured operating profile, not a claim that every task needs every model. Keep simple edits local or give them to one builder; use Fable only when its decision quality changes the result.

## Operating contract

1. Define the final artifact, acceptance checks, files or systems each agent owns, and the stopping condition before dispatch.
2. Split only independent work. Good splits include separate primary-source checks, separate visual QA, or an implementation task alongside an unrelated research task.
3. Give every agent the minimum relevant input, a bounded question, and its required output format. Pass a selected fact sheet or decision record forward instead of a raw conversation or repeated web pages.
4. Name one writer for each mutable file. Reviewers may report changes, but do not edit the builder's file concurrently.
5. Reconcile results once. Escalate only a real conflict or missing evidence to the Opus 5.1 planning role; otherwise keep the next action with the owner.
6. Stop when the acceptance checks pass. Do not run extra agents to create alternatives without a decision they can improve.

## Token discipline

- Start with a short fact sheet: goal, constraints, known decisions, input paths, and expected output.
- Use Sonnet 5 for inventory and repeatable commands. Reserve Opus 5.1 for ambiguous or consequential judgment, and Opus 5.0 for work that changes the deliverable.
- Ask research agents for cited conclusions and relevant excerpts, not exhaustive summaries.
- Reuse files, structured data, screenshots, and prior findings across stages. Do not ask each agent to rediscover the same context.
- Keep a failed result only when it changes the next design or engineering choice; record that choice in a decision log.

## Safety and completion

Do not delegate credentials, irreversible external actions, or decisions that require user approval. A task owner confirms its own acceptance checks, then an independent reviewer checks only material risks. Report the artifact, checks run, unresolved limits, and the exact next action if anything remains.

Read [parallel-contracts.md](references/parallel-contracts.md) when writing a multi-agent work brief or resolving ownership.
