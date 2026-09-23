---
name: design-to-code
description: Rebuild a high-fidelity design or prototype (HTML, React JSX, Figma export, screenshots) as production React code. Stack and engineering rules follow frontend-ui-best-practices, the design system follows products/design/DESIGN.md, and structure and interaction follow the prototype in products/prototype/.
disable-model-invocation: true
---

# Design to Code

Rebuild a high-fidelity design or prototype as production React code.

## Your role

Senior frontend engineer; reproduce design 1:1 in shippable code:

- Pixel-identical design system; "close enough" fails
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

## First principle: tokens before components

**Put design tokens in the config layer before components.** Otherwise colours, sizes and spacing
drift across components, making later rework expensive.

With a DESIGN.md, tokens are *translated*, not *extracted*; semantic consolidation is done.

## Workflow

Step 0 → 4; pause after each for user confirmation. Never dump everything at once.

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
3. Hand the user a three-column table: DESIGN.md key → token → HSL value
4. **Separate two groups:** tokens with no library slot (`success`, `warning`, semantic accents)
   and uncovered decisions (dark palette). Never fill either silently
5. Diff prototype; report every colour and size absent from DESIGN.md. Drop throwaway values or add
   extraction gaps; never fold them into tokens quietly

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
If silent, list candidates; let the user decide.

### Step 3 — Build

Build bottom-up: primitives → domain components → data seam → pages. Report each file path for
prototype comparison. Follow code rules below.

### Step 4 — Wrap up

1. Full dependency list + install command
2. Extra first-run setup, e.g. font links in `index.html`
3. Actual directory structure
4. Dev and test commands + default port
5. Complete root README per baseline; capabilities and structure are now accurate
6. **DESIGN.md coverage summary:** direct tokens, additions and grounds; baseline for the next
   DESIGN.md update
7. **Plan handoff:** copy this skill's `scripts/visual-freeze.sh` to `<app>/scripts/`, and report
   `grep -rn '@/mocks' src/api` as the starting mock list

### Re-entry on a wired app

When the prototype changes after plans have wired the code:

- Port only the changes the user names, defaulting to the newest `products/prototype/CHANGELOG.md`
  entries minus any that backport landed code. Skip Step 0, and Step 1 unless DESIGN.md changed
- Rewrite only the visual layer: JSX structure, classes, variants, copy. Existing `src/api/` and
  `src/hooks/` files stay untouched; a new page gets new mock twins
- Report every binding the new prototype orphans, such as a removed field; never delete one
  silently

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
    └── src/                # apps/<name> or packages/<name> in a monorepo
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

Check each finished component against the design:

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
unnecessary. Ask at Step 1. If needed, derive `.dark` from `inverse-*` and confirm. Retrofitting
after components exist costs more.

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

Deliver incrementally; pause for confirmation.

- Report whether `products/design/DESIGN.md` was found and which Step 1 branch applies
- After Step 0: "Scaffold ready. Confirm the config and I'll establish the design tokens."
- After Step 1: show three-column table — "Tokens are in. Check the mapping; the last rows
  aren't covered by DESIGN.md and need your call." Branch B: "check the colours and sizes
  against the prototype."
- After Step 2: "Inventory above. If the split looks right I'll start with the primitives."
- During Step 3: report every 3–5 components for user review
- Step 4 is handoff

Each file goes in its own code block, with **the full path on the first line**:

```tsx
// src/components/ui/button.tsx
import * as React from "react"
```

## Non-standard input

- **Screenshots only**: same workflow; verify sampled colours with an eyedropper at Step 1.
- **Prototype is not React**: from HTML map `class` → `className`, self-closing tags, `for` →
  `htmlFor`, `tabindex` → `tabIndex`, inline handlers → React events. From Vue, `v-if` →
  conditional rendering, `v-for` → map, `v-model` → controlled component, scoped slots → render
  props or children. From Figma or screenshots, confirm each region's meaning and interaction first.

## References

| File | When |
|---|---|
| `references/design-md-mapping.md` | Required before Step 1 branch A: key-by-key mapping from DESIGN.md's role palette to library tokens, hex→HSL conversion, and how type, radii and spacing land in the theme config |
| `scripts/visual-freeze.sh` | Step 4 copies it into the app; plans run it to prove they left tokens, classes, layout and copy alone |
