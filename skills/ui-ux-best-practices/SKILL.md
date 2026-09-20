---
name: ui-ux-best-practices
description: UI and interaction rules for Chinese-language admin consoles built with React or Vue. Covers validation timing and error display, modal/drawer reset and destructive confirmation, pagination and table alignment, date and number formats, icon, toast, control-density, theme, path-copy and statistic-card consistency, console layout, prototype data and sensitive configuration display. Use when writing, reviewing or refactoring frontend pages — forms, list pages, modals and drawers, destructive actions, UI copy and formats — and equally when designing the product before any code exists: product specs, PRDs, page and interaction specs, UI design contracts (UI-SPEC), prototypes and design reviews are bound by the same rules.
license: MIT
metadata:
  author: JinsYin
  version: "1.1.0"
---

# UI/UX Best Practices

Interface rules for Chinese-language admin consoles (React or Vue): 27 rules in 6 categories,
ordered by **what a violation costs the user**.

The rules bind design artifacts as much as code. A product spec, UI design contract or
prototype that contradicts them gets built wrong, and correcting an interaction after
implementation costs far more than writing the spec correctly.

Scope: `**/*.vue`, `**/*.jsx`, `**/*.tsx`, `**/*.css`, plus product and design documents —
specs, PRDs, UI design contracts, prototypes.

## How to use this skill

**Do not read every rule.** Locate the entries relevant to the task in the index below, then
`Read` those files on demand:

```
rules/form-validation-timing.md
rules/overlay-reset-on-close.md
```

| What you are doing | Read first |
|---|---|
| Specifying product design (spec, PRD, UI-SPEC, prototype) | the whole index; `overlay-*` and `form-*` first |
| Building a form (create / edit) | `form-*`, `overlay-reset-on-close` |
| Building a list page | `list-*`, `format-date-number` |
| Building a modal / drawer | `overlay-*` |
| Delete or other destructive action | `overlay-confirm-destructive` |
| Adjusting copy and formats | `format-*` |
| Adding an icon or a toast | `consistency-*` |
| Console shell and navigation | `console-*` |
| UI review | the categories the diff touches |

## Categories and impact

CRITICAL = data loss or an irreversible wrong action; HIGH = the user cannot finish the task or
is actively misled; MEDIUM = doable, at extra cognitive cost; LOW = inconsistent look and feel.

| Priority | Category | Impact | Prefix | Rules |
|---|---|---|---|---|
| 1 | Overlays & destructive actions | CRITICAL | `overlay-` | 3 |
| 2 | Forms | HIGH | `form-` | 5 |
| 3 | Lists & tables | HIGH | `list-` | 5 |
| 4 | Formats & wording | MEDIUM | `format-` | 2 |
| 5 | Visual consistency | LOW | `consistency-` | 7 |
| 6 | Console layout | LOW | `console-` | 5 |

## Rule index

### 1. Overlays & destructive actions (CRITICAL)

- `overlay-confirm-destructive` — custom confirmation modal for irreversible actions, never native `confirm`
- `overlay-reset-on-close` — clear values and errors on close, or the next open submits stale data
- `overlay-consistent-size` — create/edit/view share one size; drawer backdrop matches modal backdrop

### 2. Forms (HIGH)

- `form-validation-timing` — blur first, change after an error, submit as fallback
- `form-error-display` — error border + message under the field + cleared as the user types
- `form-disable-autofill` — `autocomplete="off"`, and `new-password` on password fields
- `form-readonly-styling` — gray the text, not the input; `not-allowed` cursor
- `form-input-affordances` — required marks, placeholder rules, searchable dropdowns, password eye toggle

### 3. Lists & tables (HIGH)

- `list-filter-dropdown` — filter dropdowns use a custom menu, never the default HTML `<select>`
- `list-empty-state` — show `暂无数据` centered when a table has no data
- `list-windowed-pagination` — paginate and show the total count at top right
- `list-table-alignment` — headers and cells left-aligned, `-` for empty values
- `list-toolbar-order` — search → filters → reset search and filters → icon-only refresh; omit reset and refresh when space is insufficient

### 4. Formats & wording (MEDIUM)

- `format-date-number` — `2026-04-23` / `2026-04-23 09:00:00`, no comma separators
- `format-language-naming` — Chinese UI, public platform name only, `@shdatagroup.com` email domain

### 5. Visual consistency (LOW)

- `consistency-control-density` — controls default to compact height and small corner radius
- `consistency-light-theme` — use a light theme unless explicitly specified otherwise
- `consistency-path-copy` — path values have a copy icon immediately after the value by default
- `consistency-stat-card-unit` — statistic card units sit at the bottom right of the value
- `consistency-toast` — icon + text, icon color by severity, specific error reasons
- `consistency-icons` — one icon, style, size, and color per function product-wide, exported from one module
- `consistency-page-chrome` — favicon on every page, 32x32 logo

### 6. Console layout (LOW)

- `console-mask-sensitive-config` — sensitive configuration values are displayed only in masked form
- `console-single-page` — one HTML page, menu sections reached by anchor
- `console-no-global-search-notifications` — no global search or notification center unless explicitly required
- `console-prototype-local-mock` — interactive prototypes use local mock data
- `console-header` — logo + Chinese platform name + `Console` on a new line; avatar and logout top right

## Relationship to the project's CLAUDE.md

These rules carry organization-specific facts — email domain, platform naming, logo size,
header composition. Where a project's own `CLAUDE.md` states otherwise, `CLAUDE.md` wins.

Do not copy this content into a project `CLAUDE.md`: that file is resident in every session, so
the cost of duplicated content accumulates per session, and the two copies inevitably drift.

## Full compiled version

To take in every rule at once, read `AGENTS.md`. It is generated from `rules/` by
`scripts/build.sh` — **do not edit it by hand**.
