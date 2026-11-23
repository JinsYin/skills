
## Addy

- Commit after `/spec-driven-development` (`/spec`), `/planning-and-task-breakdown` (`/plan`), `/incremental-implementation` (`/build`), `/test-driven-development` (`/test`), or `/code-simplification` (`/code-simplify`).
- Once `/incremental-implementation` (or `/build`) or `/code-simplification` (or `/code-simplify`) finishes and commits, invoke `self-improve`, clean runs too: its record Issue keeps below-gate observations later runs count toward weak gate.

### Spec & Plan

- Multi-capability initiative: write `spec/capability-map.md` module graph before module specs; single capability: `spec/SPEC-<feature>.md` or `spec/SPEC.md`.
- Read-only plan mode: write active spec plan to `tasks/plan.md` and tasks to `tasks/todo.md`.
- Plan archiving: when moving to new or completed spec, move finished plan and todo to `tasks/done/<module>-plan.md` and `tasks/done/<module>-todo.md`. Never overwrite incomplete tasks without asking.
- Slice vertically into testable S/M units (1-5 files); each task specifies acceptance criteria, verification commands, and dependencies.

### Incremental Implementation

- Build in thin vertical slices: implement smallest piece → test → verify → commit → next slice.
- Scope discipline: touch only what task requires; never refactor adjacent code or add speculative features.
- Task tracking: each completed task, tick checkbox in `tasks/todo.md` (`- [x]`), sync task status and concise summary in `tasks/plan.md`.
- Browser verification: tasks requiring browser verification (UI rendering, layout, interaction, DOM, console or network behavior) MUST verify runtime via `/browser-testing-with-devtools` before declaring done.
- Keep codebase compilable and test-clean across increments.

### Test & Simplify

- TDD: RED (write failing test) → GREEN (minimal code) → REFACTOR. Discover project native test commands first.
- Bug fixes: Prove-It Pattern — reproduce with failing test before fixing.
- Code simplification: preserve behavior exactly, follow project conventions, clarity over cleverness; verify with tests before and after.
