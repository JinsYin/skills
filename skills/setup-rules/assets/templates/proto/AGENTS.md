# Prototype Conventions

## Authoring

- Product prototype design MUST obey `ui-ux-best-practices` skill rules.
- Avoid unnecessary secondary labels and descriptions. Let the layout do the explaining.
- Implement requested prototype changes without asking again.

## Storage & Changelog

- Store prototypes in `products/prototype/` and UI design artifacts in `products/design/`.
- Record and consolidate every addition or change to product prototype under `## [Unreleased]` in `products/prototype/CHANGELOG.md`, per Keep a Changelog; with several product lines, prefix each entry `**<Line>**：`. `fspec` cuts it to `## [V<n>] - <date>` (several lines: `[<Line> V<n>]`) when its V<n> goes active.
- The `stitch-extract-design-md` skill MUST extract `DESIGN.md` from `products/prototype/` into `products/design/`, except in a `restyle` app (per `.design-to-code/progress.md`): its `DESIGN.md` is authored, never re-extracted; new looks are designed in it directly, and the prototype carries structure only.

## Images & Brand Assets

- Store product image design drafts in `products/design/drafts/`, English kebab-case `<lowercased-project-name>-<name>.png`; save each revision as new file with `-v2`, `-v3`… suffix, never overwrite earlier versions.
- Final logo: `assets/logo/logo.png`; other versions: `assets/logo/logo-v2.png`, `-v3`….
- Final favicon: `assets/icon/favicon.ico`, single 64x64; keep unscaled source as `assets/icon/favicon.png`.

## Handoff

- Commit after prototype updates, `backfill-prototype`, `write-fspec`, or `stitch-extract-design-md`.
- Exported deliverables (`DESIGN.md`, `fspec`) are delivered to master; keep master clean of prototype source files.
