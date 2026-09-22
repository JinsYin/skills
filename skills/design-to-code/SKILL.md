---
name: design-to-code
description: Rebuild a high-fidelity design or prototype (HTML, React JSX, Figma export, screenshots) as production React code. Stack and engineering rules follow frontend-ui-best-practices, the design system follows products/design/DESIGN.md, and structure and interaction follow the prototype in products/prototype/.
disable-model-invocation: true
---

# Design to Code

Rebuild a high-fidelity design or prototype as production React code.

## Your role

A senior frontend engineer who reproduces a design 1:1 in shippable code:

- Visually identical to the design system — pixel level, "close enough" is not enough
- Production engineering quality: type-safe, accessible, maintainable
- Reuse the component library before writing anything new
- Utility classes and design tokens only, never one-off inline styles
- Strip the prototype's debug UI (Claude Design's Tweaks panel and the like) — it never ships

## Authority

This skill owns neither the stack nor the design system. Each has its own source of truth; the
skill only wires them together.

| Concern | Source of truth |
|---|---|
| Stack, dependencies, scaffold, project structure, module docs | `frontend-ui-best-practices` |
| Design system: palette, type, radii, spacing, elevation, shape language, component specs | `products/design/DESIGN.md` |
| Page structure, layout, copy, interaction flow, state transitions | `products/prototype/` |
| Interface detail: validation timing, overlay state, destructive confirmation, pagination, date and number formats | `ui-ux-best-practices` |
| Anything above that conflicts with the project | the project's `CLAUDE.md` — it wins |

Two boundaries that are easy to blur:

- **Where the prototype and DESIGN.md disagree, the visual layer follows DESIGN.md and the
  structural layer follows the prototype.** Colours, radii and shadows in a prototype are often
  whatever the design tool handed out; DESIGN.md is the converged system. But which blocks a
  page has, in what order, and where a click leads — only the prototype knows.
- **Only derive tokens from the prototype when there is no DESIGN.md** (Step 1, branch B).
  Sampling colours off the prototype while a DESIGN.md exists scatters a system that was
  already converged.

Commands, directory names and component-library names below are written for the baseline's
current choices; where the baseline moves, the baseline wins.

## First principle: tokens before components

**Get the design tokens into the config layer before writing a single component.** They are the
foundation — colours, sizes and spacing scattered across components drift a little in every one
of them, and reworking that later is expensive.

With a DESIGN.md the tokens are not *extracted* but *translated*: the semantic consolidation has
already been done for you.

## Workflow

Step 0 → 4, stopping after each for the user to confirm. Never dump everything at once.

### Step 0 — Scaffold

Initialise per `frontend-ui-best-practices`: scaffold commands, path alias, stylesheet and token
file split, test config, root README. Not repeated here.

If the project already exists, skip — but verify those settings are in place first, and fill any
gaps before moving on.

### Step 1 — Establish design tokens

Which branch to take depends on whether `products/design/DESIGN.md` exists.

#### Branch A — DESIGN.md exists (preferred)

DESIGN.md is the single source of truth for the design system, so this step is translation, not
authorship. Read `references/design-md-mapping.md` first: half the key names collide across the
two schemes while meaning different things, and mapping by name turns the secondary button into
a solid slab of colour.

1. Map `colors` / `typography` / `rounded` / `spacing` from the frontmatter onto library tokens.
   Convert every hex to an HSL triplet with **no `hsl()` wrapper and no commas**
2. Read the prose sections. They carry elevation strategy, shape language, minimum hit area and
   per-component specs — none of it in the frontmatter, all of it deciding how the cva variants
   get cut in Step 3
3. Hand the user a three-column table: DESIGN.md key → token → HSL value
4. **Call out two groups separately**: tokens added because the library has no matching slot
   (`success`, `warning`, semantic accents), and anything DESIGN.md does not cover that the user
   has to decide (the dark palette). Never fill in either silently
5. Diff against the prototype. Report every colour or size that appears there but not in
   DESIGN.md — it is either a throwaway value (drop it) or a gap in the extraction (add it).
   Do not quietly fold them into the tokens

#### Branch B — no DESIGN.md (fallback)

Derive from the prototype and table the result for confirmation: colours grouped by role and
converted to HSL; the type scale, noting what has to be custom; spacing off the default rhythm;
radii, shadows and border widths; font families (watch for CJK); transition timing and duration.

Also suggest running `stitch::extract-design-md` to produce a DESIGN.md and returning to branch
A. Reverse-derived tokens have not been through semantic consolidation, so every new page tends
to introduce fresh colours.

#### Both branches produce the same thing

A token variable file (`:root` plus `.dark`) and a theme config mapping `colors`, `fontSize`,
`fontFamily`, `borderRadius` and `spacing`. File locations and the split follow the baseline.

### Step 2 — Component inventory

Sort every UI element in the prototype into three buckets and table them:

| Bucket | Handling | Examples |
|---|---|---|
| In the library, use directly | `pnpm dlx shadcn@latest add <name>` | Button, Input, Dialog, DropdownMenu, Select, Tabs, Tooltip, Popover, Sheet, Toast, Card, Badge, Avatar, Skeleton |
| In the library, needs a wrapper | add, then wrap in `src/components/` with domain props | icon buttons, a house Dialog template |
| Not in the library, write it | `src/components/<feature>/` | domain cards, bespoke layouts, prototype-only visuals |

Where the prototype needs animation, form validation, routing or data fetching, take the pick
from the project's `CLAUDE.md`. If it is silent, list the candidates and let the user decide —
do not choose for them.

### Step 3 — Build

Bottom up: primitives → domain components → pages. Report each file path as you go, so the user
can check it against the prototype. Follow the code rules below.

### Step 4 — Wrap up

1. Full dependency list and install command
2. Extra setup needed before the first run — font links in `index.html`, for example
3. The directory structure as actually created
4. Dev and test commands, plus the default port
5. Complete the root README per the baseline; capabilities and structure are only accurate now
6. **A DESIGN.md coverage summary**: which tokens came straight from DESIGN.md, which were
   added, and on what grounds. This is the diff baseline for the next DESIGN.md update

## Code rules

### TypeScript

- Props as `interface XxxProps`, never an anonymous `type`
- Handlers named `handleXxx`, callback props named `onXxx`
- Named exports, so refactors stay traceable

### Styling

- **Utility classes only.** No `style={{ ... }}` unless the value is computed, such as a
  transform derived from props
- **Colour, spacing and radius always through tokens** (`bg-primary`, `rounded-md`). A
  hardcoded `bg-[#xxxxxx]` never ships
- **Prefer DESIGN.md's named type styles** (`text-page-title`) over
  `text-[27px] font-bold leading-[1.15] tracking-tight` — spelling it out invites a typo at
  every call site and throws away what the style name meant
- **Never invent a visual value DESIGN.md lacks.** Go back to Step 1, add the token, tell the
  user, then reference it
- **Merge class names with `cn()`** — no string or template concatenation
- **Variants through `cva`** — no chains of ternaries in `className`. Two or more visual
  variants means cva

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
- Split any file past 200 lines
- Layered: `ui/` primitives → `components/<feature>/` → `pages/`
- Magic numbers and strings go to a const at the top of the file, or `@/utils/constants.ts`
- Import through the `@/` alias; no `../../../`
- A list `key` is a stable id, never the index — unless the list is static and never reorders

### Accessibility

- Everything interactive is keyboard reachable; library primitives handle this, custom ones
  are on you
- Icon buttons need `aria-label`; decorative icons need `aria-hidden="true"`
- Every `<img>` needs `alt`; decorative images take `alt=""`
- Every `<label>` is tied to its input, by `htmlFor` or by wrapping it

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
        └── types/
```

`products/` is **input** — never write to it during a port. A wrong value in DESIGN.md is a
design-system problem: regenerate with `stitch::extract-design-md`, or change it only once the
user says so.

## Fidelity checklist

Check each finished component against the design:

- [ ] shadow direction, blur and colour — do not reach for `shadow-md` by default
- [ ] the exact radius (`rounded-md` ≠ `rounded-lg`)
- [ ] hover / focus / active / disabled all have visible feedback
- [ ] weight (`font-medium` ≠ `font-semibold` ≠ `font-bold`)
- [ ] letter spacing — rare for CJK, common as `tracking-tight` on Latin headings
- [ ] opacity and overlays (`bg-black/50` scrims)
- [ ] gradients: direction, stops, opacity
- [ ] transitions survive the port, duration and easing intact
- [ ] responsive behaviour across breakpoints

With a DESIGN.md, three more:

- [ ] every colour, size, radius and spacing traces back to a mapped token — no prototype
      leftovers
- [ ] depth matches the Elevation section; both "hairline borders, almost no shadow" and
      glassmorphism are betrayed by a stock `shadow-md`
- [ ] hit areas meet the Layout section's minimum, which is not the same as the visual size

## Traps

### 1. The prototype uses a component the library lacks

Combobox, DataTable, DatePicker, Calendar. shadcn documents these as examples rather than
registry components — copy the structure, then restyle to the design.

### 2. Heavy custom animation

Reach for `motion` (framer-motion) when built-in transitions run out. Simple hover and focus
transitions stay on `transition-*`; do not add an animation library for those.

### 3. Hardcoded prototype colours reaching production

`bg-[#3b82f6]` does not survive the port. With a DESIGN.md, look the value up in the mapping;
without one, identify the role first — primary or accent? — and extract a token. Near-duplicates
in a prototype are usually incidental: DESIGN.md has already merged `#333` and `#2C2C2C`, and
resampling from the prototype undoes that.

### 4. Dark mode left undecided at Step 1

Prototypes usually ship light only, and the extracted frontmatter carries a single palette.
Neither means the project does not need dark mode, only that nothing covered it. Ask at Step 1;
if it is needed, derive `.dark` starting from the `inverse-*` keys and have the user confirm.
Retrofitting once the components exist costs several times as much.

### 5. Sprawling prototype class names

Normal for a prototype, and not worth preserving. Past 80 characters, cut variants with cva or
split the component; the same combination appearing three times is a component.

### 6. Mapping tokens by name

Half the names collide while meaning different things: DESIGN.md's `secondary` is a saturated
fill, the library's `--secondary` is the pale background of a secondary button — that is
`secondary-container`. Map by name and the button becomes a solid slab.

The first choice is also only the likeliest one, not the answer. `--accent` usually maps to
`primary-container`, but some systems really do route interactive emphasis through tertiary;
`--destructive` has to separate the status colour `error` from the button colour `error-action`;
`--input` and `--border` sit one step apart in lightness, so swapping them raises no error and
merely leaves every field looking washed out. **Check each row against the prose**, using
`references/design-md-mapping.md`.

### 7. Hex dropped straight into a CSS variable

The theme config reads `hsl(var(--primary))`, so the variable must hold a bare triplet
(`0 75.1% 41.6%`). A raw `#ba1a1a` composes into `hsl(#ba1a1a)`, which fails silently — the page
just turns black or transparent. The mapping file has a conversion script.

## Output protocol

Deliver incrementally, pausing for confirmation.

- Open by reporting whether `products/design/DESIGN.md` was found, and which branch Step 1 takes
- After Step 0: "Scaffold ready. Confirm the config and I'll establish the design tokens."
- After Step 1: show the three-column table — "Tokens are in. Check the mapping; the last rows
  aren't covered by DESIGN.md and need your call." Branch B instead: "check the colours and
  sizes against the prototype."
- After Step 2: "Inventory above. If the split looks right I'll start with the primitives."
- During Step 3: report every 3–5 components, so the user has a window to check
- Step 4 is the handoff

Each file goes in its own code block, with **the full path on the first line**:

```tsx
// src/components/ui/button.tsx
import * as React from "react"
```

## Non-standard input

- **Screenshots only**: harder, same workflow. At Step 1, have the user verify the sampled
  colours with an eyedropper.
- **Prototype is not React**: from HTML watch `class` → `className`, self-closing tags, `for` →
  `htmlFor`, `tabindex` → `tabIndex`, inline handlers → React events. From Vue, `v-if` →
  conditional rendering, `v-for` → map, `v-model` → controlled component, scoped slots → render
  props or children. From Figma or screenshots, confirm the meaning and interaction of each
  region before building anything.

## References

| File | When |
|---|---|
| `references/design-md-mapping.md` | Required before Step 1 branch A: key-by-key mapping from DESIGN.md's role palette to library tokens, hex→HSL conversion, and how type, radii and spacing land in the theme config |
