# Parallel work brief

Write a brief before dispatching agents when work crosses more than one ownership boundary.

```text
Goal: [single final outcome]
Acceptance checks: [observable checks]
Inputs: [only the paths, URLs, or facts needed]
Owner: [agent and files/systems it may change]
Task: [bounded question or implementation]
Output: [file path, table, patch, or concise findings]
Stop: [when the requested result is complete]
```

## Safe split patterns

| Pattern | Parallel owners | Join point |
| --- | --- | --- |
| Source-backed content | domestic sources, international sources, visual QA | editor selects verified facts and owns final copy |
| Product change | implementation, independent review | builder applies only accepted review findings |
| Release package | builder produces files, runner checks artifacts | builder fixes reported packaging errors |

## Ownership rules

- Do not give two agents write access to the same file, migration, or external record.
- A reviewer reports a finding with evidence and priority; the designated writer decides and applies the change.
- If two findings conflict, capture the alternatives and evidence in a decision record, then route that bounded judgment to the planning role.
- Cancel redundant work once a stronger source, answer, or artifact makes it unnecessary.

## Closeout format

```text
Delivered: [artifact/path]
Verified: [checks and results]
Decision record: [only material tradeoffs]
Open item: [none, or one concrete next action]
```
