
## Addy

- Commit after `spec-driven-development`, `planning-and-task-breakdown`, `incremental-implementation`, `test-driven-development` or `code-simplification`.
- Invoke `/ponytail full` upon `planning-and-task-breakdown`, `incremental-implementation`, `test-driven-development`, `code-simplification` and quick slices.
- Once `incremental-implementation` or `code-simplification` finishes and commits, invoke `self-improve`, clean runs too: its record Issue keeps below-gate observations later runs count toward weak gate.
- 0→1 with UI: after project skeleton and infrastructure, before frontend feature code, run standalone UI restoration stage — `spec-driven-development` (`<spec.md>`) only, then `/design-to-code <spec.md>` directly to restore `proto` branch/worktree prototype to frontend code per `fspec` (skip `planning-and-task-breakdown` and `incremental-implementation`).
- First SPEC involves deployment/delivery → split delivery into standalone stage after all business features complete: `spec-driven-development` (`spec/SPEC-delivery.md`) → `planning-and-task-breakdown` → `incremental-implementation`.
- Active plan lives in `tasks/plan.md`, tasks in `tasks/todo.md`; archive completed pairs to `tasks/done/<module>-plan.md` and `tasks/done/<module>-todo.md`.
- In `incremental-implementation`: per completed task, tick checkbox in `tasks/todo.md` (`- [x]`) and sync status + summary in `tasks/plan.md`; verify browser tasks via `browser-testing-with-devtools`.
- Record user prompts to `PROMPTS.md` upon completion of skills with source `addyosmani/agent-skills` or `jinsyin/skills` in `skills-lock.json`.
