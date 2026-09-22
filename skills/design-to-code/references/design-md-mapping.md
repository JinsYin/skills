# Mapping DESIGN.md onto library tokens

`products/design/DESIGN.md` (produced by `stitch::extract-design-md`) carries a **hex palette
named by role**; the component library uses **CSS variables named by slot, holding HSL
triplets**. Half the names collide while meaning different things — `secondary` is a saturated
fill in DESIGN.md but the pale background of a secondary button in the library. Mapping by name
turns that button into a solid slab.

The key names follow Material Design 3's colour roles, but every project extends them with keys
M3 never had (`success`, `warning`, `focus-ring`, `error-action`, `accent-*`, `chart-*`).
**Do not assume standard M3**, and do not drop a key just because it is missing from the table
below — see section 3.

Reading order: the frontmatter gives values, the prose gives intent, and **both are required**.
Check every row below against the prose: matching names do not mean matching roles (section 2
has three real counter-examples).

---

## 1. Colour mapping

| Library variable | First choice | Fallback | Notes |
|---|---|---|---|
| `--background` | `background` | `surface` | page canvas |
| `--foreground` | `on-background` | `on-surface` | body text |
| `--card` | `surface-container-lowest` | `surface-bright` → `background` | card and panel fill |
| `--card-foreground` | `on-surface` | `on-background` | |
| `--popover`, `--popover-foreground` | same pair as `--card` | | overlays usually share the card fill |
| `--primary` | `primary` | — | primary action fill |
| `--primary-foreground` | `on-primary` | — | |
| `--secondary` | `secondary-container` | `surface-container` | **not** `secondary` |
| `--secondary-foreground` | `on-secondary-container` | `on-surface-variant` | **not** `on-secondary` |
| `--muted` | `surface-dim` / `surface-container-highest` | `surface-variant` | take the deepest of the pale fills, not the barely-there row-hover tint |
| `--muted-foreground` | `on-surface-muted` | `on-surface-variant` | secondary text |
| `--accent` | `primary-container` | `tertiary-container` | hover fill for menu and dropdown items. Use the fallback only where the prose confirms tertiary carries interactive emphasis |
| `--accent-foreground` | `on-primary-container` | `on-tertiary-container` | must come from the same family as `--accent` |
| `--destructive` | `error-action` | `error` | fill of the destructive **button** |
| `--destructive-foreground` | `on-error` | — | |
| `--border` | `outline-variant` | `outline` | panel borders, separators |
| `--input` | `outline` | `outline-variant` | control borders, usually a step darker than `--border` |
| `--ring` | `focus-ring` | `primary` → `surface-tint` | focus ring |
| `--radius` | `rounded.DEFAULT` | — | |
| `--chart-1` … | `chart-1` … | derive from primary/tertiary and have the user confirm | often supplied in full, and sometimes more than five |

## 2. Why every row needs a prose check

A first choice is the likeliest candidate, not the answer. Three counter-examples from a real
project:

- **`--accent`** — its `tertiary-container` is a violet `#f0edff` used only for icon tiles,
  while dropdown items actually hover to `#f1f7ff` and select to `#eaf3ff`, both from the
  primary family. Map to `tertiary-container` and every menu hover turns violet.
- **`--destructive`** — in the same file `error` `#e04a4a` serves status dots, trend figures and
  required-field asterisks, while `error-action` `#c95353` is the fill of the "disable" and
  "reset key" buttons. Only the prose separates them.
- **`--input`** — `outline` `#d8e3ef` is the control border and `outline-variant` `#e1eaf4` is
  the separator. One step of lightness apart: swap them and nothing errors, every field just
  looks washed out.

## 3. Keys the table does not cover

Drop none of them. Where the library has no matching slot, add a variable following the same
naming, and register it explicitly under `colors` in the theme config:

| Kind | Examples | Handling |
|---|---|---|
| Semantic colours the library lacks | `success`, `warning` and their `*-container` | add a `--success` / `--success-foreground` pair. **Never** borrow `--primary` or `--accent` |
| Chart scales | `chart-1` … `chart-8`, `chart-success`, `chart-failure` | map straight to `--chart-n`; register all of them even past five |
| Semantic accents | `accent-blue`, `accent-violet`, … and their containers | register as a group, scoped by the prose — usually icon tiles and avatars only |
| Interaction states | `primary-hover`, `error-action-hover` | where DESIGN.md states a hover colour, register and reference it. **Do not** approximate with `hover:bg-primary/90` |
| Finer text tiers | `on-surface-muted`, `on-surface-faint`, `placeholder` | `--muted-foreground` covers one tier; add the rest |

## 4. hex → HSL

A variable holds a bare triplet — **no `hsl()` wrapper, no commas** — and the theme config
composes it as `hsl(var(--primary))`. One decimal place is enough: `#1477ed` →
`211.7 85.8% 50.4%`. To convert in bulk:

```js
// scripts/hex-to-hsl.mjs
const toHsl = (hex) => {
  const [r, g, b] = hex.replace('#', '').match(/../g).map((x) => parseInt(x, 16) / 255)
  const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2, d = max - min
  const s = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1))
  const h = d === 0 ? 0
    : max === r ? 60 * (((g - b) / d) % 6)
    : max === g ? 60 * ((b - r) / d + 2)
    : 60 * ((r - g) / d + 4)
  const r1 = (n) => Math.round(n * 10) / 10
  return `${r1((h + 360) % 360)} ${r1(s * 100)}% ${r1(l * 100)}%`
}
console.log(toHsl(process.argv[2]))
```

## 5. Dark mode

The frontmatter carries **one** palette. Where the prose describes a dark scheme, build that;
otherwise derive `.dark` starting from `inverse-surface` / `inverse-on-surface` /
`inverse-primary` and **have the user confirm the result**. Where the user says dark mode is not
needed, `tokens.css` holds only `:root` — but keep `darkMode: 'class'` in the theme config.

## 6. Type: `typography` → `fontSize`

Each named style carries its own `fontFamily`, `fontSize`, `fontWeight`, `lineHeight` and
`letterSpacing`, so one utility can carry all of it:

```ts
fontSize: {
  'page-title': ['27px', { lineHeight: '1.15', letterSpacing: '-0.045em', fontWeight: '700' }],
  'stat-value': ['25px', { lineHeight: '1.1',  letterSpacing: '-0.04em',  fontWeight: '700' }],
  'body-base':  ['12px', { lineHeight: '1.6',  letterSpacing: '0',        fontWeight: '400' }],
}
```

`lineHeight` may be a length or a unitless ratio. Both are valid — **copy it verbatim**, never
convert.

Call it as `className="text-page-title"`, not
`text-[27px] font-bold leading-[1.15] tracking-tight`: spelling it out invites a typo at every
call site and throws away what the style name meant.

`fontFamily` arrives as a comma-separated string (`Inter, Noto Sans SC`). Split it into an array,
append system fallbacks, register by role, and load the fonts in `index.html`:

```ts
fontFamily: {
  sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
  mono: ['SFMono-Regular', 'Consolas', 'monospace'],
}
```

Where no CJK face is listed but the product ships a Chinese interface, raise it — small CJK text
falling through to a face without the glyphs is immediately visible.

## 7. Radii: `rounded` → `borderRadius`

DESIGN.md states an explicit scale, and it wins. Put `rounded.DEFAULT` into `--radius` for the
library's internal references, then override the whole scale with the explicit values:

```ts
borderRadius: { xs: '3px', sm: '4px', DEFAULT: '6px', md: '7px', lg: '10px', full: '999px' }
```

Keep the `sm` / `md` / `lg` keys whatever else changes: library components hardcode
`rounded-md` and `rounded-lg`, and a missing key silently drops them to square corners.

## 8. Spacing: `spacing` → `theme.extend.spacing`

`spacing.unit` is the nominal base. At `4px` it shares an origin with the default scale, so keep
the numeric steps and only extend the named keys. At anything else, say so at Step 1 and confirm
whether to replace the scale or run both.

**Register named values exactly as given; never round them to the default scale.** Values like
`7px`, `14px` and `22px` are usually the result of round after round of optical tuning, and
rounding them to `8px` / `16px` / `24px` visibly loosens the whole page.

**A multi-value string is not a spacing token.** `drawer-padding: 24px 27px 38px` is a CSS
shorthand, while a spacing value has to be a single length. Split it by direction and recombine
at the component:

```ts
spacing: { 'drawer-t': '24px', 'drawer-x': '27px', 'drawer-b': '38px' }
// className="pt-drawer-t px-drawer-x pb-drawer-b"
```

## 9. What the prose sections are for

Everything the frontmatter cannot hold lives in the prose, and each section lands somewhere:

| DESIGN.md section | Lands in |
|---|---|
| Visual Theme & Atmosphere | overall density and whitespace, which fixes the control size tier |
| Color Palette & Roles | the **boundary** of each colour ("status colours appear on dots and trend figures, never as large fills") — the basis for cutting cva variants, and the source for the section 2 checks |
| Typography Rules | weight bias, the direction of letter-spacing, line-height tiers |
| Layout Principles | max container width, breakpoints, **minimum hit area** — which decides the Button size variants |
| Elevation & Depth | shadow strategy. "Hairline borders, almost no shadow" rules out `shadow-md`; glassmorphism calls for `backdrop-blur-*` over a translucent fill with a border |
| Shapes | shape language, corroborating the radii in section 7 |
| Component Stylings | per-component specs, the direct basis for implementation |
| A closing "inconsistencies" appendix, if present | gaps found during extraction. **Do not implement them** — relay them for the user to decide |

Where the prose and the frontmatter disagree, **the frontmatter wins** (it was machine
extracted), and the conflict goes to the user.

## 10. The Step 1 table

Hand over a table the user can scan, rather than a config file:

```
| DESIGN.md              | token                  | HSL               |
|------------------------|------------------------|-------------------|
| primary #1477ed        | --primary              | 211.7 85.8% 50.4% |
| secondary-container    | --secondary            | 0 0% 100%         |
| outline #d8e3ef        | --input                | 210 35.5% 89.2%   |
| focus-ring #cfe3ff     | --ring                 | 213.8 100% 90.6%  |
| success #16a464        | --success (added)      | 154.5 76.5% 36.1% |
| (not covered)          | the whole .dark scheme | needs a decision  |
```

List the last two kinds separately: **tokens added beyond the library's slots**, and **anything
DESIGN.md does not cover that the user has to decide**. Neither belongs buried in a config file.
