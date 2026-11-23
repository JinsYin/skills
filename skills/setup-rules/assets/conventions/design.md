
## Design

### Workspaces & Pipeline

- Prototypes and UI drafts live in `.worktrees/proto` on the `proto` branch; master tracks only exported design deliverables (`products/design/DESIGN.md`) and never prototype source files.
- Missing prototype worktree → `git worktree add .worktrees/proto proto` (create with `-b proto` if missing); copy `assets/templates/proto/AGENTS.md` to `.worktrees/proto/products/prototype/AGENTS.md` and commit to `proto`.
- A new page, or a look `DESIGN.md` lacks, goes prototype in `.worktrees/proto` → `write-fspec` → `re-spec` (feature spec exists) → `DESIGN.md` → `design-to-code`; any other UI change goes straight into code, leaving prototype and `fspec` untouched until backfilled.
- Backfill with `backfill-prototype`: everything landed frontend shows and prototype lacks, in one pass, then run that chain. Before new page or look, backfill first, so one `fspec` V records both.

### Code Constraints

- Plans only swap data implementations, wire APIs, and add guards (hiding or disabling existing elements) and never touch classes, variants, tokens, layout, or copy.
- `scripts/visual-freeze.sh` MUST pass on every plan branch, and a visual need found mid-plan stops the task and routes to the prototype chain above.
- A page may ship on mock until its backend is ready; taking it live replaces its `src/api/` forwarder and deletes the mock twin in the same task.
- Commit after `backfill-prototype` or `design-to-code`, then invoke `self-improve`.
