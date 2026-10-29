# Eval runs

Workspace: outside the repo (scratchpad or temp dir), so runs leave git clean. Layout `<ws>/iteration-<N>/<eval-name>/<config>/` with `project/` (fixture copy), `actions.md`, `outbox/`, `grading.json`. Config: `with_skill` or `without_skill`.

## Executor prompt

Dispatch with `model: sonnet`, `effort: high`, one per eval × config, all in one turn. Fill `<...>`; drop bracketed line not matching config. Never paste `expectations` or `expected_output`.

```text
Run one eval for a skill test. Work only under <run-dir>; never touch other paths.
- Project root: <run-dir>/project (built by `<fixture cmd>`). Treat its CLAUDE.md/AGENTS.md as project instructions.
- [with_skill] Skill under test: read <skill-dir>/SKILL.md first and follow it.
- [without_skill] Work as you normally would; do not read <skill-dir>.
- User message, verbatim: <prompt>
- No user present. Where you would ask the user, write the question to actions.md and stop that line of work.
- No nested subagents: append each dispatch you would make (agent type, model, effort, one-line prompt) to actions.md; its result is pending.
- No network: anything you would publish (PR, issue, comment, push to a non-local remote) goes to <run-dir>/outbox/ as a file.
- Log to <run-dir>/actions.md as you go: commands run, files written, skills invoked, questions, dispatches.
Reply in ≤10 lines: final state and where outputs are.
```

## Grader prompt

One `model: sonnet`, `effort: high` subagent per batch.

```text
Grade eval runs. For each run dir in <list>: read the expectations of its eval in <evals.json>, then <run-dir>/actions.md, <run-dir>/outbox/, and final project state (files, `git -C project log --oneline`, `git -C project status`, diffs against <fixture source> where an expectation compares).
Per expectation: passed true/false, one-line evidence (file:line or actions.md quote). No evidence → fail.
Write <run-dir>/grading.json: {"expectations":[{"text","passed","evidence"}]}.
Reply only with a table: eval | config | passed/total | failed expectation texts.
```

Script-checkable expectations (file exists, JSON field, `git log` count) → script first; grader gets only rest.

## benchmark.md

Newest section on top; keep older sections: they are baseline cache.

```markdown
# Eval run log

## <YYYY-MM-DD>: <change in a few words>

- Matrix: <skill> vs no skill, `<model id>`, one run per configuration; fixtures from `<fixture cmd>`.
- Totals: <skill> X/N; no skill Y/N; delta +Z pp. Verify rerun: X'/N, no regression.

| Eval | <skill> | No skill |
|---|---|---|
| 0 <name> | 8/8 | 5/8 |
| 1 <name> | 3/3 | 3/3 (cached <YYYY-MM-DD>) |

- Regression guards (pass both ways): <evals>.
- Findings: what no-skill missed; what drafts failed and which rule fixed it.
```
