---
name: backfill-prototype
description: "Backfill landed frontend into product prototype (products/prototype/): compare every page structurally, add what frontend shows and prototype lacks in one pass, log it under [Unreleased] in prototype CHANGELOG, then hand off to /write-fspec. Use when user says 回补原型 or backport, or before starting new page or look on app whose frontend was changed directly. Not for designing new pages (edit prototype directly) or porting prototype changes into code (design-to-code)."
argument-hint: "[<app>]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# Backfill Prototype

After build, small UI changes land straight in code; prototype falls behind. `write-fspec`, `stitch-extract-design-md` and `design-to-code` all read prototype, so stale one makes next forward feature redraw or undo landed work. This skill levels prototype with frontend in one pass. Reply in Chinese.

Codex: `$ARGUMENTS` = text after command. No interactive picker → print numbered options, stop for user's reply; never answer own question.

## Rules

1. Frontend is truth for what exists; prototype only follows. Write only under `products/prototype/`; frontend, `products/fspec/` and `products/design/` stay read-only.
2. Compare structure, never history. Git ranges miss drift landed before last prototype commit; read both sides in full for every page.
3. Backfill what user sees: pages, nav entries, blocks and their order, fields and table columns, filters, actions, overlays, copy, enum labels, drawn states. Skip what prototype never carries:
   - Data and wiring: `src/api/`, `src/hooks/`, `src/mocks/`, sample row values.
   - Visual values DESIGN.md explains, and deviations `.design-to-code/progress.md` sanctions; `restyle` app (per `progress.md`): all visuals, structure only.
   - Guards hiding or disabling element prototype already draws: list as `fspec` 前置条件 material, don't draw.
   - Interaction conventions `ui-ux-best-practices` owns (destructive confirmation, validation timing, overlay reset): component behaviour, not page structure.
4. Prototype has something frontend lacks → not backfill. Listed as non-backfill entry under `## [Unreleased]` in prototype CHANGELOG, or as gap in `progress.md` → pending forward work, leave silently. Else → ask whether code removed it; delete from prototype only on yes.
5. Match prototype's own idiom: same files, markup style, page ids (`data-page`), class names; obey `ui-ux-best-practices`. Page ids come from frontend routes, never invented.

## Workflow

**1. Locate.**
- Prototype: `products/prototype/`; product lines = its app dirs (`console/`, `portal/`).
- App: `$ARGUMENTS` if given; else dirs with `.design-to-code/` (repo root, `apps/*`, `packages/*`). Several → backfill each to its line, matched by `.design-to-code/index.md` or name; none → ask for frontend path.
- Read project `CLAUDE.md` for outward terms and banned codenames: frontend copy using a codename → backfill outward term, report it.

**2. Inventory both sides** per line. Frontend: routes, nav, `src/pages/` and components they render: blocks, columns, filters, actions, overlays, copy, conditional UI. Prototype: every `data-page` section, with `.design-to-code/index.md` ranges as map. Read `progress.md` for mode, gaps, sanctioned deviations; prototype CHANGELOG `## [Unreleased]`.

**3. Diff** into a table per page id: element · frontend · prototype · verdict (`backfill` / `skip: <rule 3 reason>` / `pending forward` / `ask`). Done when every frontend route and every prototype `data-page` has its rows. Nothing to backfill, no `ask` → report "原型与前端一致", stop without edits.

**4. Backfill** every `backfill` row into prototype in one pass, without waiting on `ask` rows: they are independent. New page: full section plus nav entry, sample data realistic and outward-termed.

**5. Ask** every `ask` row in one round. Yes → remove from prototype, log under `### Removed`. No answer (unattended) → leave untouched, list in report.

**6. Log** under `## [Unreleased]` in `products/prototype/CHANGELOG.md` (Keep a Changelog; create file with that heading if missing), in `### Added` / `### Changed` / `### Removed`. Start each entry `回补已上线前端：`, so `design-to-code` re-entry skips it as already landed. Several lines sharing file: prefix `**<Line>**：` before it (`**Console**：回补已上线前端：…`).

**7. Report** per line: backfilled rows, skipped rows with reason, `fspec` 前置条件 material, open `ask` rows. End with next command: `/write-fspec products/prototype/`; forward 1→2 feature → iterate prototype first, `write-fspec` records both in one V.
