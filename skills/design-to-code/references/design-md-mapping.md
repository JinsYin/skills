# Mapping DESIGN.md onto library tokens

`products/design/DESIGN.md` (produced by `stitch::extract-design-md`) has a **hex palette named
by role**; the component library has **slot-named CSS variables holding HSL triplets**. Names
collide: DESIGN.md `secondary` is saturated, while the library's is a pale secondary-button
background. Name-only mapping turns that button into a solid slab.

Keys follow Material Design 3 colour roles, but projects add keys M3 never had (`success`,
`warning`, `focus-ring`, `error-action`, `accent-*`, `chart-*`). **Do not assume standard M3**
or drop keys absent from this table; see section 3.

Read frontmatter for values and prose for intent; **both are required**. Check every row against
the prose: matching names do not guarantee matching roles (section 2 has three counter-examples).

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

A first choice is the likeliest candidate, not the answer. Three real counter-examples:

- **`--accent`** — `tertiary-container` is violet `#f0edff` for icon tiles; dropdown hover
  `#f1f7ff` and select `#eaf3ff` are primary-family colours. Mapping to `tertiary-container`
  makes every menu hover violet.
- **`--destructive`** — `error` `#e04a4a` serves status dots, trend figures and required-field
  asterisks; `error-action` `#c95353` fills "disable" and "reset key" buttons. Prose separates
  them.
- **`--input`** — `outline` `#d8e3ef` is the control border; `outline-variant` `#e1eaf4` is the
  separator. One lightness step apart; swapping them looks washed out without errors.

## 3. Keys the table does not cover

Drop none. If the library lacks a slot, add a same-named variable and register it under `colors`
in the theme config:

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
`211.7 85.8% 50.4%`. Convert in bulk:

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

Frontmatter carries **one** palette. If prose describes dark, build it; otherwise derive `.dark`
from `inverse-surface` / `inverse-on-surface` / `inverse-primary` and **have the user confirm the
result**. If dark mode is not needed, `tokens.css` holds only `:root`; keep `darkMode: 'class'` in
theme config.

## 6. Type: `typography` → `fontSize`

Each named style carries `fontFamily`, `fontSize`, `fontWeight`, `lineHeight` and
`letterSpacing`, so one utility can carry all of it:

```ts
fontSize: {
  'page-title': ['27px', { lineHeight: '1.15', letterSpacing: '-0.045em', fontWeight: '700' }],
  'stat-value': ['25px', { lineHeight: '1.1',  letterSpacing: '-0.04em',  fontWeight: '700' }],
  'body-base':  ['12px', { lineHeight: '1.6',  letterSpacing: '0',        fontWeight: '400' }],
}
```

`lineHeight` may be a length or unitless ratio. Both are valid — **copy it verbatim**, never
convert.

Use `className="text-page-title"`, not
`text-[27px] font-bold leading-[1.15] tracking-tight`; spelling it out invites typos and loses
the style name's intent.

`fontFamily` arrives as a comma-separated string (`Inter, Noto Sans SC`). Split into an array,
append system fallbacks, register by role, and load fonts in `index.html`:

```ts
fontFamily: {
  sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
  mono: ['SFMono-Regular', 'Consolas', 'monospace'],
}
```

If no CJK face is listed for a Chinese interface, raise it; small CJK text without glyphs is
immediately visible.

## 7. Radii: `rounded` → `borderRadius`

DESIGN.md's explicit scale wins. Put `rounded.DEFAULT` into `--radius` for library references,
then override the full scale with explicit values:

```ts
borderRadius: { xs: '3px', sm: '4px', DEFAULT: '6px', md: '7px', lg: '10px', full: '999px' }
```

Keep `sm` / `md` / `lg` keys: components hardcode `rounded-md` and `rounded-lg`; missing keys
silently make corners square.

## 8. Spacing: `spacing` → `theme.extend.spacing`

`spacing.unit` is nominal base. At `4px` it shares the default scale's origin: keep numeric steps
and extend named keys. Otherwise state it at Step 1 and confirm whether to replace the scale or
run both.

**Register named values exactly; never round to the default scale.** `7px`, `14px` and `22px`
often reflect optical tuning; rounding to `8px` / `16px` / `24px` visibly loosens the page.

**A multi-value string is not a spacing token.** `drawer-padding: 24px 27px 38px` is CSS
shorthand; a spacing value must be one length. Split by direction and recombine at the component:

```ts
spacing: { 'drawer-t': '24px', 'drawer-x': '27px', 'drawer-b': '38px' }
// className="pt-drawer-t px-drawer-x pb-drawer-b"
```

## 9. What the prose sections are for

Frontmatter cannot hold everything; prose sections land as follows:

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

Where prose and frontmatter disagree, **frontmatter wins** (machine extracted); send the conflict
to the user.

## 10. The Step 1 table

Hand over a scan-friendly table, not a config file:

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

List the last two kinds separately: **tokens added beyond library slots** and **anything DESIGN.md
does not cover that needs a user decision**. Neither belongs buried in config.
