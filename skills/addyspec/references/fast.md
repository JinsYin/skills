# Fast Task (`addyspec fast`)

Run trivial edit inline in current context: atomic commit, zero planning artifacts.

## Guardrails

- Edit inline only (no subagents, no `tasks/quick/<id>-<slug>/` dir, `plan.md`, or `summary.md`); leave `tasks/plan.md` and `tasks/todo.md` untouched.
- Trivial = ≤3 file edits, ≤2 min, no new deps, no architecture change, no research (e.g. typo/copy fix, config value, version bump, missing import, `.gitignore` entry, simple rename, isolated style tweak).
- Escalate to `/addyspec quick` when >3 file edits, research/planning needed, cross-layer or API/value-semantics logic touched (e.g. status/enum/format mapping owned by backend rather than UI), or approach uncertain.

## Workflow

1. **Parse task.** Empty `$ARGUMENTS` → ask in one sentence what to change.

2. **Check scope and cleanliness (read-only).** Scope via grep/paths first; defer full-file reads and other skills until scope passes, so escalations stay cheap:
   - Exceeds guardrails → stop immediately, suggest `/addyspec quick "<task description>"`.
   - Within guardrails → run `git status --short` on target path(s): any target file has uncommitted changes → stop, ask user whether to stash/commit first or combine before editing.

3. **Edit inline and verify.** Read target file(s), apply change directly, run minimal sanity check (relevant existing tests, typecheck, or build if applicable).

4. **Commit code atomically.** Stage only exact modified file(s) (never `git add -A`); commit per project conventions (e.g. `fix:` / `style:` / `chore:` / `docs:` / `refactor:`). No changes landed → stop and report.

5. **Log to `tasks/quick/README.md` (if present).** If `tasks/quick/README.md` exists with `# Quick Tasks` table (`| ID | Description | Date | Commit | Status | Path |`), capture code commit short hash (`git rev-parse --short HEAD`), append one row (escape literal `|` in title as `\|`), and commit `tasks/quick/README.md` alone (`docs(quick): ...`):

   ```markdown
   | fast | <one-line title> | YYYY-MM-DD | <short-hash> | complete | — |
   ```

   Otherwise skip silently (do not create it).

6. **Report.** Output concisely and stop (no next-step routing):
   - Change summary
   - Code commit short hash (plus docs commit hash if logged)
   - Modified file(s)
