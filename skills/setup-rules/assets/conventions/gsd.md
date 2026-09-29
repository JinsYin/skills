
## GSD

- Prefer the `gsx` skill (`gsx --<mode>`) over calling `/gsd:*` directly.
- Once `spec-phase`, `discuss-phase`, `plan-phase`, `execute-phase`, `verify-work`, `code-review` or `debug` finishes and commits (direct or via `gsx`), invoke `self-improve` if the run saw a user correction, rework, or repeated failure; skip it on a clean run.
- After `complete-milestone`, invoke `self-improve --sessions` to retrospect the milestone's sessions together.
