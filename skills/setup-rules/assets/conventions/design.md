
## Design

- If the main workspace already has a prototype, modify it there without repeated confirmation; otherwise, create the draft in a new isolated worktree for the session. Final prototypes belong in the main workspace.
- Keep workspaces independent: never inspect, reference, or modify a different workspace.
- When creating a draft prototype worktree, copy the `setup-rules` template `assets/templates/prototype/AGENTS.md` to `products/prototype/AGENTS.md` in that worktree only.
- Store prototypes in `products/prototype/` and UI designs in `products/design/`; read `products/prototype/` only when changing a prototype.
- The `stitch-extract-design-md` skill MUST extract `DESIGN.md` from `products/prototype/` into `products/design/`.
- MUST record or consolidate every addition or change to the product prototype in `products/prototype/CHANGELOG.md`.
- Commit after `stitch-extract-design-md`.
