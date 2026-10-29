
## Design

### Workspaces

- If the main workspace already has a prototype, modify it there without repeated confirmation; otherwise, create the draft in a new isolated worktree for the session. Final prototypes belong in the main workspace.
- Keep workspaces independent: never inspect, reference, or modify a different workspace.
- When creating a draft prototype worktree, copy the `setup-rules` template `assets/templates/prototype/AGENTS.md` to `products/prototype/AGENTS.md` in that worktree only.

### Prototype & DESIGN.md

- Store prototypes in `products/prototype/` and UI designs in `products/design/`; read `products/prototype/` only when changing a prototype.
- The `stitch-extract-design-md` skill MUST extract `DESIGN.md` from `products/prototype/` into `products/design/`, except in a `restyle` app (per `.design-to-code/progress.md`): its `DESIGN.md` is authored, never re-extracted; new looks are designed in it directly, and the prototype carries structure only.
- MUST record or consolidate every addition or change to product prototype under `## [Unreleased]` in `products/prototype/CHANGELOG.md`, per Keep a Changelog; with several product lines, prefix each entry `**<Line>**：`. `fspec` cuts it to `## [V<n>] - <date>` (several lines: `[<Line> V<n>]`) when its V<n> goes active, so prototype and spec versions match.

### Images & Brand Assets

- Store product image design drafts in `products/design/drafts/`, English kebab-case `<lowercased-project-name>-<name>.png`; save each revision as new file with `-v2`, `-v3`… suffix, never overwrite earlier versions.
- Final logo: `assets/logo/logo.png`; other versions: `assets/logo/logo-v2.png`, `-v3`….
- Final favicon: `assets/icon/favicon.ico`, single 64x64; keep unscaled source as `assets/icon/favicon.png`.

### Post-Build Changes

- A new page, or a look `DESIGN.md` lacks, goes prototype → `fspec` → `DESIGN.md` → `design-to-code`; any other UI change goes straight into the code, leaving prototype and `fspec` untouched until backported.
- Backport into `products/prototype/`, in one pass, everything landed frontend shows and prototype lacks, logged as backport in its `CHANGELOG.md`, then run that chain. Before new page or look, backport first, so one `fspec` V records both.
- Plans only swap data implementations, wire APIs and add guards (hiding or disabling existing elements) and never touch classes, variants, tokens, layout or copy; `scripts/visual-freeze.sh` MUST pass on every plan branch, and a visual need found mid-plan stops the task and routes as above.
- A page may ship on mock until its backend is ready; taking it live replaces its `src/api/` forwarder and deletes the mock twin in the same task.

### Commit & Retrospective

- Commit after `stitch-extract-design-md`, `fspec` or `design-to-code`.
- Once `design-to-code` finishes and commits, invoke `self-improve`.
