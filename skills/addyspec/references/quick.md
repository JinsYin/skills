# Quick Task (`addyspec quick`)

Run standalone quick slice via `incremental-implementation`, saving artifacts under `tasks/quick/` instead of `tasks/plan.md` or `tasks/todo.md`.

## Artifacts

```text
tasks/quick/
├── README.md                # Index table (created if missing)
└── <id>-<slug>/             # One directory per quick task
    ├── plan.md              # Before coding: goal, decisions, scope, acceptance
    └── summary.md           # After code commit: status, changes, verification, commit
```

- `<id>`: `YYMMDD-xxx` — local date + seconds since midnight ÷ 2 in base36, zero-padded to 3 chars (e.g. `261125-k3x`).
- `<slug>`: lowercase kebab-case summary (`[a-z0-9-]`, max 40 chars).
- Leave `tasks/plan.md` and `tasks/todo.md` untouched (do not require, read, or update them).

## Workflow

1. **Clarify scope.** Empty `$ARGUMENTS` → ask what to do. Interview user to confirm any unclear requirement, boundary, or acceptance criterion before writing `plan.md` or code; skip if already clear.

2. **Write `plan.md`.** Generate `<id>` and `<slug>`, create `tasks/quick/<id>-<slug>/plan.md` (do not commit yet):

   ```markdown
   # <Task Title>

   - **ID**: `<id>`
   - **Date**: `YYYY-MM-DD`

   ## Goal
   <Problem and desired outcome>

   ## Decisions
   - <Confirmed interview answers or constraints; omit section if none>

   ## Scope & Steps
   - <Target files/areas and vertical steps>

   ## Acceptance
   - <Observable verification criteria / commands>
   ```

3. **Implement and commit code.** Invoke `incremental-implementation` against `plan.md` (small verified slice, tests, build/checks, atomic code commit). Stage session code and project-required logs (e.g. `CHANGELOG.md`, `PROMPTS.md`) — exclude `tasks/quick/` so code rollback stays clean and code commit hash exists before `summary.md`. User cancels or no code lands → stop without writing `summary.md` or updating `tasks/quick/README.md`.

4. **Write `summary.md` and update index.** Capture code commit short hash (`git rev-parse --short HEAD`; multiple code commits → final short hash in frontmatter/table, list all in `Changes`):
   - Create `tasks/quick/<id>-<slug>/summary.md`:

     ```markdown
     ---
     status: complete
     id: <id>
     date: YYYY-MM-DD
     commit: <short-hash>
     ---

     # Summary: <Task Title>

     ## Changes
     - <Files and behavior changes>

     ## Verification
     - <Checks/commands run and observed results>

     ## Follow-ups
     - <Deferred items or caveats; omit section if none>
     ```

     Partial code landed → set `status: incomplete` and list remaining work in `## Follow-ups`.

   - Append row to `tasks/quick/README.md` (create with heading + table if missing); escape literal `|` in description as `\|`; match `Status` to `summary.md`:

     ```markdown
     # Quick Tasks

     | ID | Description | Date | Commit | Status | Path |
     |---|---|---|---|---|---|
     | <id> | <one-line title> | YYYY-MM-DD | <short-hash> | <status> | [<id>-<slug>](./<id>-<slug>/) |
     ```

5. **Commit docs and report.** Stage only `tasks/quick/<id>-<slug>/plan.md`, `tasks/quick/<id>-<slug>/summary.md`, and `tasks/quick/README.md`; commit per project conventions (e.g. `docs(quick): <summary>`). Report task ID, `plan.md` / `summary.md` paths, code commit hash, and docs commit hash.
