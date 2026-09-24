
## Design

- If the main workspace already has a prototype, modify it there without repeated confirmation; otherwise, create the draft in a new isolated worktree for the session. Final prototypes belong in the main workspace.
- Keep workspaces independent: never inspect, reference, or modify a different workspace.
- When creating a draft prototype worktree, copy the `setup-rules` template `assets/templates/prototype/AGENTS.md` to `products/prototype/AGENTS.md` in that worktree only.
- Store prototypes in `products/prototype/` and UI designs in `products/design/`; read `products/prototype/` only when changing a prototype.
- The `stitch-extract-design-md` skill MUST extract `DESIGN.md` from `products/prototype/` into `products/design/`, except in a `restyle` app (per `.design-to-code/progress.md`): its `DESIGN.md` is authored, never re-extracted; new looks are designed in it directly, and the prototype carries structure only.
- MUST record or consolidate every addition or change to the product prototype in `products/prototype/CHANGELOG.md`.
- Once `design-to-code` has built the app, record every new feature with `product-spec add` first.
- A new page, or a look `DESIGN.md` lacks, goes prototype → `DESIGN.md` → `design-to-code`; any other UI change goes straight into the code, leaving the prototype untouched.
- Before that chain starts, backport into `products/prototype/`, in one pass, everything the landed frontend shows and the prototype lacks, logged as a backport in its `CHANGELOG.md`.
- Plans only swap data implementations, wire APIs and add guards (hiding or disabling existing elements) and never touch classes, variants, tokens, layout or copy; `scripts/visual-freeze.sh` MUST pass on every plan branch, and a visual need found mid-plan stops the task and routes as above.
- A page may ship on mock until its backend is ready; taking it live replaces its `src/api/` forwarder and deletes the mock twin in the same task.
- Commit after `stitch-extract-design-md` or `design-to-code`.