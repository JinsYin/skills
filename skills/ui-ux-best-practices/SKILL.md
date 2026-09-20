---
name: ui-ux-best-practices
description: UI/UX rules for Chinese-language React/Vue admin consoles and their product/design specs. Use when designing, building, reviewing, or refactoring forms, lists, modals/drawers, destructive actions, copy, formats, or console layout.
license: MIT
metadata:
  author: JinsYin
  version: "1.1.0"
---
# UI/UX Best Practices

Interface rules for Chinese admin consoles (React/Vue): 24 rules, 6 categories,
ordered by **what violation cost user**.

Rules bind design artifacts same as code. Spec, UI design contract, or
prototype that break them get built wrong. Fix interaction after
build cost way more than write spec right.

Scope: `**/*.vue`, `**/*.jsx`, `**/*.tsx`, `**/*.css`, plus product and design documents —
specs, PRDs, UI design contracts, prototypes.

## How to use this skill

**No read every rule.** Find entries for task in index below, then
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

CRITICAL = data lost or wrong action no take back; HIGH = user no finish task or
get misled; MEDIUM = can do, but brain hurt; LOW = look-feel not match.

| Priority | Category | Impact | Prefix | Rules |
|---|---|---|---|---|
| 1 | Overlays & destructive actions | CRITICAL | `overlay-` | 3 |
| 2 | Forms | HIGH | `form-` | 5 |
| 3 | Lists & tables | HIGH | `list-` | 4 |
| 4 | Formats & wording | MEDIUM | `format-` | 2 |
| 5 | Visual consistency | LOW | `consistency-` | 6 |
| 6 | Console layout | LOW | `console-` | 4 |

## Rule index

### 1. Overlays & destructive actions (CRITICAL)

- `overlay-confirm-destructive` — custom confirm modal for no-take-back action, never native `confirm`
- `overlay-reset-on-close` — wipe values and errors on close, else next open send stale data
- `overlay-consistent-size` — create/edit/view share one size; drawer backdrop match modal backdrop

### 2. Forms (HIGH)

- `form-validation-timing` — blur first, change after error, submit as fallback
- `form-error-display` — error border + message under field + wipe as user type
- `form-disable-autofill` — `autocomplete="off"`, and `new-password` on password fields
- `form-readonly-styling` — gray the text, not the input; `not-allowed` cursor
- `form-input-affordances` — required marks, placeholder rules, searchable dropdowns, password eye toggle

### 3. Lists & tables (HIGH)

- `list-filter-dropdown` — filter dropdown use custom menu, never default HTML `<select>`
- `list-pagination` — paginate and show total count top right
- `list-table-content` — align table content; show `-` for empty value and centered localized empty state
- `list-toolbar-order` — search → filters → reset search and filters → icon-only refresh; drop reset and refresh when no space

### 4. Formats & wording (MEDIUM)

- `format-date-number` — `2026-04-23` / `2026-04-23 09:00:00`, no comma separators
- `format-language-naming` — Chinese UI, public platform name only, `@shdatagroup.com` email domain

### 5. Visual consistency (LOW)

- `consistency-control-density` — controls default to compact height and small corner radius
- `consistency-light-theme` — use light theme unless said otherwise
- `consistency-stat-card-unit` — stat card unit sit bottom right of value
- `consistency-toast` — icon + text, icon color by severity, specific error reasons
- `consistency-icons` — one icon, style, size, color per function product-wide, exported from one module
- `consistency-page-chrome` — favicon on every page, 32x32 logo

### 6. Console layout (LOW)

- `console-mask-sensitive-config` — sensitive config value show masked only
- `console-single-page` — one HTML page, menu sections reached by anchor
- `console-prototype-local-mock` — interactive prototypes use local mock data
- `console-header` — logo + Chinese platform name + `Console`; avatar, logout and minimal global chrome

## Relationship to the project's CLAUDE.md

These rules hold org-specific facts — email domain, platform naming, logo size,
header parts. Where project `CLAUDE.md` say otherwise, `CLAUDE.md` win.

No copy this content into project `CLAUDE.md`: that file sit in every session, so
duplicate cost pile up per session, and two copies drift apart for sure.

## Full compiled version

To eat every rule at once, read `AGENTS.md`. It born from `rules/` by
`scripts/build.sh` — **no edit by hand**.
