---
name: design-to-code
description: "Rebuild high-fidelity design or prototype (HTML, React JSX, Figma export, screenshots) as production React code. Stack/engineering rules → frontend-ui-best-practices; design system → products/design/DESIGN.md (restyle mode: one authored from style brief); structure/interaction → products/prototype/."
argument-hint: "[full | lite | restyle [style brief]]"
disable-model-invocation: true
---
# Design to Code

Rebuild high-fidelity design or prototype as production React code.

## Your role

Senior frontend engineer; ship design as production code:

- Token-exact design system: every value traces to DESIGN.md; prototype sets structure, not pixels
- Type-safe, accessible, maintainable code
- Reuse component library before new code
- Utility classes + design tokens; no one-off inline styles
- Strip prototype debug UI (Claude Design's Tweaks panel); never ship

## Authority

Skill owns neither stack nor design system; wires their sources of truth together.

| Concern | Source of truth |
|---|---|
| Stack, deps, scaffold, project structure, module docs | `frontend-ui-best-practices` |
| Design system: palette, type, radii, spacing, elevation, shape language, component specs | `products/design/DESIGN.md` |
| Page structure, layout, copy, interaction flow, state transitions | `products/prototype/` |
| States/preconditions prototype leaves undrawn: loading, empty, error, no-permission, disabled | `products/specs/<product>/CURRENT.md`: `状态与流转` and `前置条件` column; on conflict prototype and DESIGN.md win, drift goes to `product-spec add` |
| Interface detail: validation timing, overlay state, destructive confirmation, pagination, date/number formats | `ui-ux-best-practices` |
| Anything above conflicting with project | project's `CLAUDE.md` — wins |

Easy-to-blur boundaries:

- **Prototype vs DESIGN.md:** visual layer → DESIGN.md; structural layer → prototype. DESIGN.md wins colours, radii, shadows; prototype wins page blocks, order, click destinations.
- **Derive tokens from prototype only without DESIGN.md** (Step 1, branch B). Sampling prototype when DESIGN.md exists scatters converged system.
- **`restyle` replaces design-system row:** Step 1 branch C authors new DESIGN.md, which then rules like any other; prototype keeps only structural rows.

Commands, dir names, component-library names follow baseline; baseline wins when it changes.

## Mode

First word of `$ARGUMENTS` picks mode; anything else runs `full` and says so. Text after `restyle` = style brief. `.design-to-code/progress.md` records mode; re-entry keeps it.

| | full (default) | lite | restyle |
|---|---|---|---|
| Visual source | DESIGN.md | DESIGN.md | DESIGN.md authored in Step 1, branch C |
| Prototype supplies | structure + visuals | structure + visuals | structure only: blocks, relative layout, flows, overlay types, copy, states, responsive collapse |
| Each Step 3 slice | typecheck, lint, test, build; hardcoded-value grep; checklist read from code | same | same |
| Step 4, once | `smoke`, then `diff` with triage | `smoke` | `smoke`, then `diff --structure` |

No mode renders, screenshots or measures prototype before Step 4. Difference DESIGN.md explains (type scale, line height, icon style, token colour) is sanctioned: record, never measure. `restyle` reads prototype JSX and CSS layout props only, never colours or sizes. `high` effort enough; `max` mostly buys extra measuring.

## First principle: tokens before components

**Put design tokens in config layer before components.** Else colours, sizes, spacing drift across components; rework expensive.

With DESIGN.md, tokens *translated*, not *extracted*; semantic consolidation done.

## Workflow

Step 0 → 5; implement continuously. At each optional choice use recommended best-fit option from sources of truth, report choice, continue without waiting for confirmation. Pause only when missing info makes work impossible or unsafe.

### Step 0 — Scaffold

Init per `frontend-ui-best-practices`: scaffold commands, path alias, stylesheet and token split, test config, root README. Not repeated here.

Project exists → skip only after verifying settings; fill gaps first.

### Step 1 — Establish design tokens

`restyle` takes branch C; else branch depends on whether `products/design/DESIGN.md` exists.

#### Branch A — DESIGN.md exists (preferred)

DESIGN.md = design-system source of truth: translate, not author. Read `references/design-md-mapping.md` first; colliding key names mean name-only mapping can turn secondary button into solid colour slab.

1. Map `colors` / `typography` / `rounded` / `spacing` from frontmatter to library tokens; convert every hex to HSL triplet with **no `hsl()` wrapper and no commas**
2. Read prose for elevation, shape, min hit area, component specs; these decide Step 3 cva variants
3. Show three-column table: DESIGN.md key → token → HSL value
4. **Separate two groups:** tokens with no library slot (`success`, `warning`, semantic accents) and uncovered decisions (dark palette). Pick recommended best-fit for uncovered decisions, state assumption, continue; never fill either silently
5. Grep prototype source for colour/size literals absent from DESIGN.md; list as gaps, never fold into tokens quietly. No rendering, no DESIGN.md re-extraction, no prototype edits during port; gaps route to prototype chain at Step 5

#### Branch B — no DESIGN.md (fallback)

Derive from prototype; table role-grouped HSL colours, type scale and custom values, default-rhythm spacing, radii, shadows, border widths, CJK-aware fonts, transition timing/duration.

Suggest `stitch::extract-design-md` to produce DESIGN.md, then return to branch A. Reverse-derived tokens lack semantic consolidation → new pages add fresh colours.

#### Branch C — `restyle`

1. Direction from style brief; none → pick from product positioning and users in `CURRENT.md`. State in one line, continue
2. Author DESIGN.md in existing format: frontmatter `colors` / `typography` / `rounded` / `spacing`; prose for elevation, shape, min hit area, component specs, every state. One pass; components keep shadcn structure, differ via tokens unless brief demands more
3. Replace `products/design/DESIGN.md` after one confirmation (git keeps old), commit, then run branch A steps 1–4 on it

#### All branches produce the same thing

Token variable file (`:root` plus `.dark`) and theme config mappings for `colors`, `fontSize`, `fontFamily`, `borderRadius`, `spacing`. File locations/split follow baseline.

### Step 2 — Component inventory

Sort every prototype UI element into three buckets, table them:

| Bucket | Handling | Examples |
|---|---|---|
| In library, use directly | `pnpm dlx shadcn@latest add <name>` | Button, Input, Dialog, DropdownMenu, Select, Tabs, Tooltip, Popover, Sheet, Toast, Card, Badge, Avatar, Skeleton |
| In library, needs wrapper | add, then wrap in `src/components/` with domain props | icon buttons, house Dialog template |
| Not in library, write it | `src/components/<feature>/` | domain cards, bespoke layouts, prototype-only visuals |

Prototype animation, form validation, routing, data fetching → project's `CLAUDE.md`. Silent → pick best-fit from prototype, project conventions, a11y requirements; report alternatives when useful, continue without waiting.

Mark every component shared by 2+ pages; Step 3 settles them before any page. Then write:

- `.design-to-code/index.md`: per page id, prototype source line ranges, CSS selectors, states, shared components; `restyle` records structure only. Note CSS overrides hiding/moving a block; hidden blocks not ported
- `.design-to-code/progress.md`: slices done with commits, decisions, gaps, sanctioned deviations; updated per slice. After context compaction read these two, not prototype
- `scripts/visual-targets.mjs` (format in `visual-check.mjs` header): every page, first drawer, dialog, toast, menu, and each spec state reachable by flag

### Step 3 — Build

Bottom-up: primitives → shared components → one committed slice per page (domain components → data seam → page), reading only that page's `index.md` ranges. Per slice run mode table's checks; hardcoded-value grep is `grep -rnE '\[#[0-9a-fA-F]{3,8}\]|-\[[0-9.]+px\]|style=\{\{' src`, silent except computed styles. Report each file path so user can compare to prototype. Later shared-component change reruns its pages' tests, not visual pass. Follow code rules below.

### Step 4 — Verify

Copy skill's `scripts/visual-check.mjs` to `<app>/scripts/`, gitignore `.visual-check/`. Serve built app; `full` or `restyle` also serve prototype built into `.visual-check/`, never under `products/`.

1. `node scripts/visual-check.mjs smoke <appUrl>`: every class generates CSS, no console error, no horizontal overflow at 1280 and 1440. Fix or justify each finding. `lite` stops here
2. `full`: `node scripts/visual-check.mjs diff <protoUrl> <appUrl>`, view diffs largest first, sort each: sanctioned → `progress.md`; defect → fix, measuring computed styles on that element only
3. `restyle`: `node scripts/visual-check.mjs diff --structure <protoUrl> <appUrl>`; every prototype text appears in order, side-by-side shots show same blocks and overlay types. Fix omissions only; visual differences are the point
4. Rerun `diff --only <names>` on fixed targets. Max two rounds; leftover defects go to handoff

### Step 5 — Wrap up

1. Full dep list + install command
2. Extra first-run setup, e.g. font links in `index.html`
3. Actual dir structure
4. Dev and test commands + default port
5. Complete root README per baseline; capabilities and structure now accurate
6. **DESIGN.md coverage summary:** direct tokens, additions, grounds, Step 1 gaps; baseline for next DESIGN.md update
7. **Verification:** mode, smoke result; `full` or `restyle`: `.visual-check/report.md`, sanctioned deviations, leftover defects
8. **Plan handoff:** copy skill's `scripts/visual-freeze.sh` to `<app>/scripts/`, report `grep -rn '@/mocks' src/api` as starting mock list

### Re-entry on a wired app

Prototype changes after plans wired code:

- Port only changes user names, default newest `products/prototype/CHANGELOG.md` entries minus those backporting landed code. Skip Step 0, and Step 1 unless DESIGN.md changed
- Rewrite only visual layer: JSX structure, classes, variants, copy. Existing `src/api/` and `src/hooks/` files untouched; new page gets new mock twins
- Report every binding new prototype orphans (e.g. removed field); never delete silently
- Update `index.md` and `visual-targets.mjs` for changed pages; Step 4 runs `--only` them
- Built app, unchanged prototype: run Step 4 alone

## Code rules

### TypeScript

- Props as `interface XxxProps`, never anonymous `type`
- Handlers `handleXxx`, callback props `onXxx`
- Named exports, refactors stay traceable

### Styling

- **Utility classes only.** No `style={{ ... }}` unless computed, e.g. transform from props
- **Colour, spacing, radius via tokens** (`bg-primary`, `rounded-md`). Hardcoded `bg-[#xxxxxx]` never ships
- **Prefer DESIGN.md named type styles** (`text-page-title`) over `text-[27px] font-bold leading-[1.15] tracking-tight`; names prevent typos, keep intent
- **Never invent visual value DESIGN.md lacks.** Back to Step 1, add token, tell user, reference it
- **Merge class names with `cn()`**; no string/template concatenation
- **Variants via `cva`**; no ternary chains in `className`. 2+ visual variants → cva

```tsx
// ❌
<button className={`px-4 py-2 ${variant === 'primary' ? 'bg-blue-500' : 'bg-gray-200'}`}>

// ✅
const buttonVariants = cva('px-4 py-2', {
  variants: {
    variant: {
      primary: 'bg-primary text-primary-foreground',
      secondary: 'bg-secondary text-secondary-foreground',
    },
    size: { lg: 'text-lg', sm: 'text-sm' },
  },
  defaultVariants: { variant: 'primary', size: 'sm' },
})
```

### Components

- Function components + hooks; no class components
- Split files past 200 lines
- Layer: `ui/` primitives → `components/<feature>/` → `pages/`
- Magic numbers/strings in top-level const or `@/utils/constants.ts`
- Import via `@/` alias; no `../../../`
- List `key` = stable id, never index unless static and never reordered
- Keep prototype page ids in routes and page names; specs and plans address pages by them

### Data seam

Plans later swap data, wire APIs, add guards without touching markup; leave seam:

- Pages hold no data literals, never call HTTP. Anything backend will own, enum labels included, goes through `src/api/<feature>.ts`, read via hooks
- Each `src/api/` function async, typed by `src/types/`, maps any backend shape itself; until backend ready it forwards to same-signature twin in `src/mocks/<feature>.ts`, going live replaces only that right-hand side. `grep -rn '@/mocks' src/api` lists what's still mock
- Every state/precondition prototype or spec defines renders from flag, so wiring flips state, never adds UI. State neither defines = gap: list it, never invent

```ts
// src/api/orders.ts
export const listOrders: (q: OrderQuery) => Promise<Page<Order>> = mock.listOrders
```

### Accessibility

- All interactive elements keyboard reachable; primitives handle it, custom ones must
- Icon buttons need `aria-label`; decorative icons `aria-hidden="true"`
- Every `<img>` needs `alt`; decorative `alt=""`
- Tie every `<label>` to input via `htmlFor` or wrapping

## Where things live

Config files and stylesheet dir follow baseline. Skill adds only `products/` inputs and where `src/` sits relative:

```
<repo>/
├── products/
│   ├── design/DESIGN.md    # design system — source of truth, read-only
│   └── prototype/          # prototype — structure and interaction, read-only
└── <app>/                  # the repo root itself in a single-package project;
    │                       # apps/<name> or packages/<name> in a monorepo
    ├── .design-to-code/    # index.md, progress.md — committed, reused on re-entry
    ├── .visual-check/      # Step 4 dependencies, screenshots, report — gitignored
    ├── scripts/            # visual-check.mjs, visual-targets.mjs, visual-freeze.sh
    └── src/
        ├── components/
        │   ├── ui/         # library primitives
        │   ├── common/     # shared components: pagination bar, status badge, …
        │   └── <feature>/  # domain components
        ├── layouts/
        ├── pages/
        ├── hooks/
        ├── api/            # data seam, one file per feature
        ├── mocks/          # same-signature twins, deleted as each goes live
        └── types/
```

`products/` is **input** — never write during port, except `restyle`'s confirmed DESIGN.md replacement. Wrong DESIGN.md value = design-system problem: regenerate with `stitch::extract-design-md`, or change only after user approval.

## Fidelity checklist

Check each finished component by reading code against DESIGN.md and prototype source; `full` confirms rendered defects at Step 4:

- [ ] shadow direction, blur, colour; don't default to `shadow-md`
- [ ] exact radius (`rounded-md` ≠ `rounded-lg`)
- [ ] visible hover, focus, active, disabled feedback
- [ ] weight (`font-medium` ≠ `font-semibold` ≠ `font-bold`)
- [ ] letter spacing; rare for CJK, common as `tracking-tight` on Latin headings
- [ ] opacity and overlays (`bg-black/50` scrims)
- [ ] gradient direction, stops, opacity
- [ ] transition duration and easing survive port
- [ ] responsive behaviour across breakpoints

With DESIGN.md, three more:

- [ ] every colour, size, radius, spacing traces to mapped token; no prototype leftovers
- [ ] depth matches Elevation; "hairline borders, almost no shadow" and glassmorphism rule out stock `shadow-md`
- [ ] hit areas meet Layout's minimum, not just visual size

## Traps

### 1. The prototype uses a component the library lacks

Combobox, DataTable, DatePicker, Calendar. shadcn documents these as examples, not registry components; copy structure, restyle to design.

### 2. Heavy custom animation

Use `motion` (framer-motion) when built-in transitions run out. Simple hover/focus stay on `transition-*`; no animation library for them.

### 3. Hardcoded prototype colours reaching production

`bg-[#3b82f6]` doesn't survive port. With DESIGN.md, look up in mapping; else identify role, extract token. Prototype near-duplicates usually incidental: DESIGN.md already merged `#333` and `#2C2C2C`; resampling undoes that.

### 4. Dark mode left undecided at Step 1

Prototypes usually light-only, frontmatter carries one palette; neither proves dark mode unneeded. Use best-supported project/design choice; dark palette needed but absent → derive `.dark` from `inverse-*` when supported, report assumption. Retrofit after components costs more.

### 5. Sprawling prototype class names

Normal for prototype, not worth preserving. Past 80 chars, cut variants with cva or split component; same combination three times = component.

### 6. Mapping tokens by name

Names collide: DESIGN.md's `secondary` is saturated; library `--secondary` is pale secondary button background, so use `secondary-container`. Name-only mapping makes solid slab.

First choice is likeliest, not final. `--accent` usually maps to `primary-container`, but some systems route interactive emphasis through tertiary; `--destructive` separates status `error` from button `error-action`; `--input` and `--border` differ one lightness step. Swapping looks washed out, no errors. **Check each row against prose** via `references/design-md-mapping.md`.

### 7. Hex dropped straight into a CSS variable

Theme config reads `hsl(var(--primary))`, so variables hold bare triplets (`0 75.1% 41.6%`). Raw `#ba1a1a` becomes `hsl(#ba1a1a)`, fails silently; page turns black or transparent. Mapping file includes conversion script.

## Output protocol

Deliver incrementally while continuing; don't wait for confirmation between steps.

- Report mode (`restyle`: plus direction), whether `products/design/DESIGN.md` found, which Step 1 branch applies
- After Step 0: "Scaffold ready. Continuing to establish the design tokens."
- After Step 1: show three-column table — "Tokens are in. I used the recommended mapping; uncovered rows carry explicit assumptions." Branch B: "Tokens are in; I used prototype evidence for the colours and sizes."
- After Step 2: "Inventory above. I used the recommended split and am starting with the primitives."
- During Step 3: report every 3–5 components for traceability, continue
- After Step 4: smoke result; `full` or `restyle`: diff table with each row's verdict
- Step 5 is handoff

Each file in own code block, **full path on first line**:

```tsx
// src/components/ui/button.tsx
import * as React from "react"
```

## Non-standard input

- **Screenshots only**: same workflow; verify sampled colours with eyedropper at Step 1. Step 4 `diff` has no prototype to serve; view app screenshots beside originals.
- **Prototype not React**: HTML: `class` → `className`, self-closing tags, `for` → `htmlFor`, `tabindex` → `tabIndex`, inline handlers → React events. Vue: `v-if` → conditional rendering, `v-for` → map, `v-model` → controlled component, scoped slots → render props or children. Figma/screenshots: infer each region's meaning and interaction from visible evidence and standard conventions, record assumptions, continue.

## References

| File | When |
|---|---|
| `references/design-md-mapping.md` | Required before Step 1 branch A: key-by-key mapping from DESIGN.md role palette to library tokens, hex→HSL conversion, how type, radii, spacing land in theme config |
| `scripts/visual-check.mjs` | Step 4 copies into app: `smoke` checks app alone, `diff` pairs with prototype, `--structure` for `restyle`; targets format in header |
| `scripts/visual-freeze.sh` | Step 5 copies into app; plans run it to prove they left tokens, classes, layout, copy alone |