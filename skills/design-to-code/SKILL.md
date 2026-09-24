---
name: design-to-code
description: Rebuild a high-fidelity design or prototype (HTML, React JSX, Figma export, screenshots) as production React code. Stack and engineering rules follow frontend-ui-best-practices, the design system follows products/design/DESIGN.md, and structure and interaction follow the prototype in products/prototype/.
argument-hint: "[full | lite]"
disable-model-invocation: true
---

# Design to Code

Rebuild a high-fidelity design or prototype as production React code.

## Your role

Senior frontend engineer; reproduce design 1:1 in shippable code:

- Token-exact design system: every value traces to DESIGN.md; the prototype sets structure, not
  pixels
- Type-safe, accessible, maintainable production code
- Reuse component library before new code
- Utility classes + design tokens; no one-off inline styles
- Strip prototype debug UI (Claude Design's Tweaks panel); never ship it

## Authority

This skill owns neither stack nor design system; it wires their sources of truth together.

| Concern | Source of truth |
|---|---|
| Stack, dependencies, scaffold, project structure, module docs | `frontend-ui-best-practices` |
| Design system: palette, type, radii, spacing, elevation, shape language, component specs | `products/design/DESIGN.md` |
| Page structure, layout, copy, interaction flow, state transitions | `products/prototype/` |
| States and preconditions the prototype leaves undrawn: loading, empty, error, no-permission, disabled | `products/specs/<product>/CURRENT.md`: `状态与流转` and the `前置条件` column |
| Interface detail: validation timing, overlay state, destructive confirmation, pagination, date and number formats | `ui-ux-best-practices` |
| Anything above that conflicts with the project | the project's `CLAUDE.md` — it wins |

Two boundaries that are easy to blur:

- **Prototype vs DESIGN.md:** visual layer follows DESIGN.md; structural layer follows the
  prototype. DESIGN.md wins colours, radii and shadows; prototype wins page blocks, order and
  click destinations.
- **Derive tokens from the prototype only without DESIGN.md** (Step 1, branch B). Sampling an
  existing DESIGN.md's prototype scatters an already-converged system.

Commands, directory names and component-library names follow baseline choices; baseline wins
when it changes.

## Verification mode

First word of `$ARGUMENTS`: `full` (default) or `lite`; anything else runs `full` and says so.

| | lite | full |
|---|---|---|
| Each Step 3 slice | typecheck, lint, test, build; hardcoded-value grep; checklist read from code | same |
| Step 4, once | `visual-check.mjs smoke` | `smoke`, then `visual-check.mjs diff` with triage |

Neither mode renders, screenshots or measures the prototype before Step 4. A difference
DESIGN.md explains (type scale, line height, icon style, token colour) is sanctioned: record it,
never measure it. `high` effort suffices; `max` mostly buys extra measuring.

## First principle: tokens before components

**Put design tokens in the config layer before components.** Otherwise colours, sizes and spacing
drift across components, making later rework expensive.

With a DESIGN.md, tokens are *translated*, not *extracted*; semantic consolidation is done.

## Workflow

Step 0 → 5; implement continuously. At each optional choice, use the recommended best-fit
option from the sources of truth, report the choice, and continue without waiting for user
confirmation. Pause only when missing information makes the work impossible or unsafe.

### Step 0 — Scaffold

Initialise per `frontend-ui-best-practices`: scaffold commands, path alias, stylesheet and token
split, test config and root README. Not repeated here.

If project exists, skip only after verifying settings; fill gaps before continuing.

### Step 1 — Establish design tokens

Branch depends on whether `products/design/DESIGN.md` exists.

#### Branch A — DESIGN.md exists (preferred)

DESIGN.md is the design-system source of truth: translate, do not author. Read
`references/design-md-mapping.md` first; colliding key names mean name-only mapping can turn the
secondary button into a solid colour slab.

1. Map `colors` / `typography` / `rounded` / `spacing` from frontmatter to library tokens;
   convert every hex to an HSL triplet with **no `hsl()` wrapper and no commas**
2. Read prose for elevation, shape, minimum hit area and component specs; these decide Step 3
   cva variants
3. Show a three-column table: DESIGN.md key → token → HSL value
4. **Separate two groups:** tokens with no library slot (`success`, `warning`, semantic accents)
   and uncovered decisions (dark palette). Choose the recommended best-fit option for uncovered
   decisions, state the assumption, and continue; never fill either silently
5. Grep the prototype source for colour and size literals absent from DESIGN.md; list them as
   gaps, never fold them into tokens quietly. No rendering, no DESIGN.md re-extraction and no
   prototype edits during a port; gaps route to the prototype chain at Step 5

#### Branch B — no DESIGN.md (fallback)

Derive from prototype; table role-grouped HSL colours, type scale and custom values, default-rhythm
spacing, radii, shadows, border widths, CJK-aware fonts, transition timing and duration.

Suggest running `stitch::extract-design-md` to produce DESIGN.md, then return to branch A.
Reverse-derived tokens lack semantic consolidation, so new pages tend to add fresh colours.

#### Both branches produce the same thing

A token variable file (`:root` plus `.dark`) and theme config mappings for `colors`, `fontSize`,
`fontFamily`, `borderRadius` and `spacing`. File locations and split follow baseline.

### Step 2 — Component inventory

Sort every UI element in the prototype into three buckets and table them:

| Bucket | Handling | Examples |
|---|---|---|
| In the library, use directly | `pnpm dlx shadcn@latest add <name>` | Button, Input, Dialog, DropdownMenu, Select, Tabs, Tooltip, Popover, Sheet, Toast, Card, Badge, Avatar, Skeleton |
| In the library, needs a wrapper | add, then wrap in `src/components/` with domain props | icon buttons, a house Dialog template |
| Not in the library, write it | `src/components/<feature>/` | domain cards, bespoke layouts, prototype-only visuals |

For prototype animation, form validation, routing or data fetching, use project's `CLAUDE.md`.
If silent, choose the best-fit candidate from the prototype, project conventions and accessibility
requirements; report alternatives when useful and continue without waiting for user selection.

Mark every component two or more pages share; Step 3 settles them before any page. Then write:

- `.design-to-code/index.md`: per page id, its prototype source line ranges, CSS selectors,
  states and shared components
- `.design-to-code/progress.md`: slices done with commits, decisions, gaps and sanctioned
  deviations; updated per slice. After a context compaction, read these two, not the prototype
- `scripts/visual-targets.mjs` (format in the `visual-check.mjs` header): every page, the first
  drawer, dialog, toast and menu, and each spec state reachable by flag

### Step 3 — Build

Build bottom-up: primitives → shared components → one committed slice per page (domain
components → data seam → page), reading only that page's `index.md` ranges. Per slice run the
mode table's checks; the hardcoded-value grep is
`grep -rnE '\[#[0-9a-fA-F]{3,8}\]|-\[[0-9.]+px\]|style=\{\{' src`, silent except computed styles.
Report each file path so the user can compare against the prototype. A later change to a shared
component reruns its pages' tests, not a visual pass. Follow code rules below.

### Step 4 — Verify

Copy this skill's `scripts/visual-check.mjs` to `<app>/scripts/` and gitignore `.visual-check/`.
Serve the built app; for `full`, also serve the prototype built into `.visual-check/`, never
under `products/`.

1. `node scripts/visual-check.mjs smoke <appUrl>`: every class generates CSS, no console error,
   no horizontal overflow at 1280 and 1440. Fix or justify each finding. `lite` stops here
2. `full`: `node scripts/visual-check.mjs diff <protoUrl> <appUrl>`, then view diffs largest
   first and sort each difference: sanctioned → `progress.md`; defect → fix, measuring computed
   styles on that element only
3. Rerun `diff --only <names>` on fixed targets. Two rounds at most; leftover defects go to the
   handoff

### Step 5 — Wrap up

1. Full dependency list + install command
2. Extra first-run setup, e.g. font links in `index.html`
3. Actual directory structure
4. Dev and test commands + default port
5. Complete root README per baseline; capabilities and structure are now accurate
6. **DESIGN.md coverage summary:** direct tokens, additions, grounds and Step 1 gaps; baseline
   for the next DESIGN.md update
7. **Verification:** mode, smoke result; for `full`, `.visual-check/report.md`, sanctioned
   deviations and leftover defects
8. **Plan handoff:** copy this skill's `scripts/visual-freeze.sh` to `<app>/scripts/`, and report
   `grep -rn '@/mocks' src/api` as the starting mock list

### Re-entry on a wired app

When the prototype changes after plans have wired the code:

- Port only the changes the user names, defaulting to the newest `products/prototype/CHANGELOG.md`
  entries minus any that backport landed code. Skip Step 0, and Step 1 unless DESIGN.md changed
- Rewrite only the visual layer: JSX structure, classes, variants, copy. Existing `src/api/` and
  `src/hooks/` files stay untouched; a new page gets new mock twins
- Report every binding the new prototype orphans, such as a removed field; never delete one
  silently
- Update `index.md` and `visual-targets.mjs` for changed pages; Step 4 runs with `--only` them
- Built app, unchanged prototype: run Step 4 alone

## Code rules

### TypeScript

- Props as `interface XxxProps`, never an anonymous `type`
- Handlers named `handleXxx`, callback props named `onXxx`
- Named exports, so refactors stay traceable

### Styling

- **Utility classes only.** No `style={{ ... }}` unless computed, e.g. a transform from props
- **Colour, spacing and radius through tokens** (`bg-primary`, `rounded-md`). Hardcoded
  `bg-[#xxxxxx]` never ships
- **Prefer DESIGN.md named type styles** (`text-page-title`) over
  `text-[27px] font-bold leading-[1.15] tracking-tight`; style names prevent typos and preserve
  intent
- **Never invent a visual value DESIGN.md lacks.** Return to Step 1, add token, tell user,
  reference it
- **Merge class names with `cn()`**; no string or template concatenation
- **Variants through `cva`**; no ternary chains in `className`. Two or more visual variants mean
  cva

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

- Function components and hooks; no class components
- Split files past 200 lines
- Layer: `ui/` primitives → `components/<feature>/` → `pages/`
- Put magic numbers and strings in a top-level const or `@/utils/constants.ts`
- Import through `@/` alias; no `../../../`
- List `key` is a stable id, never index unless static and never reordered
- Keep the prototype's page ids in routes and page names; specs and plans address pages by them

### Data seam

Plans later swap data, wire APIs and add guards without touching markup; leave them a seam:

- Pages hold no data literals and never call HTTP. Anything the backend will own, enum labels
  included, goes through `src/api/<feature>.ts`, read via hooks
- Each `src/api/` function is async, typed by `src/types/`, and maps any backend shape itself;
  until its backend is ready it forwards to a same-signature twin in `src/mocks/<feature>.ts`,
  and going live replaces only that right-hand side. `grep -rn '@/mocks' src/api` lists what is
  still mock
- Every state and precondition the prototype or spec defines renders from a flag, so wiring flips
  state and never adds UI. A state neither defines is a gap: list it, never invent it

```ts
// src/api/orders.ts
export const listOrders: (q: OrderQuery) => Promise<Page<Order>> = mock.listOrders
```

### Accessibility

- All interactive elements are keyboard reachable; primitives handle this, custom ones must
- Icon buttons need `aria-label`; decorative icons need `aria-hidden="true"`
- Every `<img>` needs `alt`; decorative images use `alt=""`
- Tie every `<label>` to its input with `htmlFor` or wrapping

## Where things live

Config files and the stylesheet directory follow the baseline. This skill adds only the
`products/` inputs and where `src/` sits relative to them:

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

`products/` is **input** — never write to it during a port. A wrong DESIGN.md value is a
design-system problem: regenerate with `stitch::extract-design-md`, or change only after user
approval.

## Fidelity checklist

Check each finished component by reading its code against DESIGN.md and the prototype source;
`full` confirms rendered defects at Step 4:

- [ ] shadow direction, blur and colour; do not default to `shadow-md`
- [ ] exact radius (`rounded-md` ≠ `rounded-lg`)
- [ ] visible hover, focus, active and disabled feedback
- [ ] weight (`font-medium` ≠ `font-semibold` ≠ `font-bold`)
- [ ] letter spacing; rare for CJK, common as `tracking-tight` on Latin headings
- [ ] opacity and overlays (`bg-black/50` scrims)
- [ ] gradient direction, stops and opacity
- [ ] transition duration and easing survive the port
- [ ] responsive behaviour across breakpoints

With a DESIGN.md, three more:

- [ ] every colour, size, radius and spacing traces to a mapped token; no prototype leftovers
- [ ] depth matches Elevation; "hairline borders, almost no shadow" and glassmorphism rule out
      stock `shadow-md`
- [ ] hit areas meet Layout's minimum, not just visual size

## Traps

### 1. The prototype uses a component the library lacks

Combobox, DataTable, DatePicker, Calendar. shadcn documents these as examples, not registry
components; copy structure, then restyle to the design.

### 2. Heavy custom animation

Use `motion` (framer-motion) when built-in transitions run out. Keep simple hover and focus on
`transition-*`; do not add an animation library for them.

### 3. Hardcoded prototype colours reaching production

`bg-[#3b82f6]` does not survive the port. With DESIGN.md, look it up in the mapping; otherwise
identify its role, then extract a token. Prototype near-duplicates are usually incidental:
DESIGN.md already merged `#333` and `#2C2C2C`; resampling undoes that.

### 4. Dark mode left undecided at Step 1

Prototypes are usually light-only and frontmatter carries one palette; neither proves dark mode
unnecessary. Use the best-supported project/design choice; if a dark palette is needed but absent,
derive `.dark` from `inverse-*` when supported and report the assumption. Retrofitting after
components exist costs more.

### 5. Sprawling prototype class names

Normal for a prototype, and not worth preserving. Past 80 characters, cut variants with cva or
split the component; the same combination appearing three times is a component.

### 6. Mapping tokens by name

Names collide: DESIGN.md's `secondary` is saturated; library `--secondary` is the pale secondary
button background, so use `secondary-container`. Name-only mapping makes a solid slab.

First choice is likeliest, not final. `--accent` usually maps to `primary-container`, but some
systems route interactive emphasis through tertiary; `--destructive` separates status `error`
from button `error-action`; `--input` and `--border` differ one lightness step. Swapping them
looks washed out without errors. **Check each row against prose** via
`references/design-md-mapping.md`.

### 7. Hex dropped straight into a CSS variable

Theme config reads `hsl(var(--primary))`, so variables hold bare triplets
(`0 75.1% 41.6%`). Raw `#ba1a1a` becomes `hsl(#ba1a1a)` and silently fails; the page turns
black or transparent. The mapping file includes a conversion script.

## Output protocol

Deliver incrementally while continuing; do not wait for confirmation between steps.

- Report the verification mode, whether `products/design/DESIGN.md` was found and which Step 1
  branch applies
- After Step 0: "Scaffold ready. Continuing to establish the design tokens."
- After Step 1: show the three-column table — "Tokens are in. I used the recommended mapping;
  uncovered rows carry explicit assumptions." Branch B: "Tokens are in; I used prototype
  evidence for the colours and sizes."
- After Step 2: "Inventory above. I used the recommended split and am starting with the
  primitives."
- During Step 3: report every 3–5 components for traceability, then continue
- After Step 4: smoke result; for `full`, the diff table with each row's verdict
- Step 5 is handoff

Each file goes in its own code block, with **the full path on the first line**:

```tsx
// src/components/ui/button.tsx
import * as React from "react"
```

## Non-standard input

- **Screenshots only**: same workflow; verify sampled colours with an eyedropper at Step 1.
  Step 4 `diff` has no prototype to serve; view app screenshots beside the originals instead.
- **Prototype is not React**: from HTML map `class` → `className`, self-closing tags, `for` →
  `htmlFor`, `tabindex` → `tabIndex`, inline handlers → React events. From Vue, `v-if` →
  conditional rendering, `v-for` → map, `v-model` → controlled component, scoped slots → render
  props or children. From Figma or screenshots, infer each region's meaning and interaction from
  visible evidence and standard conventions, record assumptions, and continue.

## References

| File | When |
|---|---|
| `references/design-md-mapping.md` | Required before Step 1 branch A: key-by-key mapping from DESIGN.md's role palette to library tokens, hex→HSL conversion, and how type, radii and spacing land in the theme config |
| `scripts/visual-check.mjs` | Step 4 copies it into the app: `smoke` checks the app alone, `diff` pairs it with the prototype; targets format in its header |
| `scripts/visual-freeze.sh` | Step 5 copies it into the app; plans run it to prove they left tokens, classes, layout and copy alone |
