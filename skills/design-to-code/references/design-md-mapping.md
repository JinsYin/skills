# Mapping DESIGN.md onto library tokens

`products/design/DESIGN.md` (from `stitch::extract-design-md`) has **hex palette named by role**; component library has **slot-named CSS variables holding HSL triplets**. Names collide: DESIGN.md `secondary` saturated, library's is pale secondary-button background. Name-only mapping → button becomes solid slab.

Keys follow Material Design 3 colour roles, but projects add non-M3 keys (`success`, `warning`, `focus-ring`, `error-action`, `accent-*`, `chart-*`). **Do not assume standard M3** or drop keys absent from table; see section 3.

Frontmatter = values, prose = intent; **both required**. Check every row against prose: same name ≠ same role (section 2: three counter-examples).

---

## 1. Colour mapping

| Library variable | First choice | Fallback | Notes |
|---|---|---|---|
| `--background` | `background` | `surface` | page canvas |
| `--foreground` | `on-background` | `on-surface` | body text |
| `--card` | `surface-container-lowest` | `surface-bright` → `background` | card/panel fill |
| `--card-foreground` | `on-surface` | `on-background` | |
| `--popover`, `--popover-foreground` | same pair as `--card` | | overlays usually share card fill |
| `--primary` | `primary` | — | primary action fill |
| `--primary-foreground` | `on-primary` | — | |
| `--secondary` | `secondary-container` | `surface-container` | **not** `secondary` |
| `--secondary-foreground` | `on-secondary-container` | `on-surface-variant` | **not** `on-secondary` |
| `--muted` | `surface-dim` / `surface-container-highest` | `surface-variant` | deepest pale fill, not barely-there row-hover tint |
| `--muted-foreground` | `on-surface-muted` | `on-surface-variant` | secondary text |
| `--accent` | `primary-container` | `tertiary-container` | menu/dropdown item hover fill. Fallback only if prose confirms tertiary carries interactive emphasis |
| `--accent-foreground` | `on-primary-container` | `on-tertiary-container` | same family as `--accent` |
| `--destructive` | `error-action` | `error` | destructive **button** fill |
| `--destructive-foreground` | `on-error` | — | |
| `--border` | `outline-variant` | `outline` | panel borders, separators |
| `--input` | `outline` | `outline-variant` | control borders, usually one step darker than `--border` |
| `--ring` | `focus-ring` | `primary` → `surface-tint` | focus ring |
| `--radius` | `rounded.DEFAULT` | — | |
| `--chart-1` … | `chart-1` … | derive from primary/tertiary, user confirms | often full set, sometimes >5 |

## 2. Why every row needs a prose check

First choice = likeliest candidate, not answer. Three real counter-examples:

- **`--accent`** — `tertiary-container` is violet `#f0edff` for icon tiles; dropdown hover `#f1f7ff` and select `#eaf3ff` are primary family. Mapping to `tertiary-container` → every menu hover violet.
- **`--destructive`** — `error` `#e04a4a` for status dots, trend figures, required-field asterisks; `error-action` `#c95353` fills "disable" and "reset key" buttons. Prose separates them.
- **`--input`** — `outline` `#d8e3ef` = control border; `outline-variant` `#e1eaf4` = separator. One lightness step apart; swap looks washed out, no errors.

## 3. Keys the table does not cover

Drop none. Library lacks slot → add same-named variable, register under `colors` in theme config:

| Kind | Examples | Handling |
|---|---|---|
| Semantic colours library lacks | `success`, `warning` + their `*-container` | add `--success` / `--success-foreground` pair. **Never** borrow `--primary` or `--accent` |
| Chart scales | `chart-1` … `chart-8`, `chart-success`, `chart-failure` | map straight to `--chart-n`; register all, even past five |
| Semantic accents | `accent-blue`, `accent-violet`, … + containers | register as group, scoped by prose — usually icon tiles/avatars only |
| Interaction states | `primary-hover`, `error-action-hover` | DESIGN.md states hover colour → register and reference. **Do not** approximate with `hover:bg-primary/90` |
| Finer text tiers | `on-surface-muted`, `on-surface-faint`, `placeholder` | `--muted-foreground` covers one tier; add rest |

## 4. hex → HSL

Variable holds bare triplet — **no `hsl()` wrapper, no commas** — theme config composes as `hsl(var(--primary))`. One decimal enough: `#1477ed` → `211.7 85.8% 50.4%`. Bulk convert:

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

Frontmatter carries **one** palette. Prose describes dark → build it; else derive `.dark` from `inverse-surface` / `inverse-on-surface` / `inverse-primary` and **have user confirm result**. No dark mode needed → `tokens.css` holds only `:root`; keep `darkMode: 'class'` in theme config.

## 6. Type: `typography` → `fontSize`

Each named style carries `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing` → one utility carries all:

```ts
fontSize: {
  'page-title': ['27px', { lineHeight: '1.15', letterSpacing: '-0.045em', fontWeight: '700' }],
  'stat-value': ['25px', { lineHeight: '1.1',  letterSpacing: '-0.04em',  fontWeight: '700' }],
  'body-base':  ['12px', { lineHeight: '1.6',  letterSpacing: '0',        fontWeight: '400' }],
}
```

`lineHeight` may be length or unitless ratio. Both valid — **copy verbatim**, never convert.

Use `className="text-page-title"`, not `text-[27px] font-bold leading-[1.15] tracking-tight`; spelled out invites typos, loses style name intent.

`fontFamily` arrives comma-separated (`Inter, Noto Sans SC`). Split to array, append system fallbacks, register by role, load fonts in `index.html`:

```ts
fontFamily: {
  sans: ['Inter', 'Noto Sans SC', 'system-ui', 'sans-serif'],
  mono: ['SFMono-Regular', 'Consolas', 'monospace'],
}
```

Chinese interface with no CJK face listed → raise it; small CJK text without glyphs immediately visible.

## 7. Radii: `rounded` → `borderRadius`

DESIGN.md explicit scale wins. Put `rounded.DEFAULT` into `--radius` for library references, then override full scale explicitly:

```ts
borderRadius: { xs: '3px', sm: '4px', DEFAULT: '6px', md: '7px', lg: '10px', full: '999px' }
```

Keep `sm` / `md` / `lg` keys: components hardcode `rounded-md`, `rounded-lg`; missing keys silently square corners.

## 8. Spacing: `spacing` → `theme.extend.spacing`

`spacing.unit` = nominal base. At `4px` shares default scale origin: keep numeric steps, extend named keys. Otherwise state at Step 1, confirm replace scale or run both.

**Register named values exactly; never round to default scale.** `7px`, `14px`, `22px` often optical tuning; rounding to `8px` / `16px` / `24px` visibly loosens page.

**Multi-value string ≠ spacing token.** `drawer-padding: 24px 27px 38px` is CSS shorthand; spacing value must be one length. Split by direction, recombine at component:

```ts
spacing: { 'drawer-t': '24px', 'drawer-x': '27px', 'drawer-b': '38px' }
// className="pt-drawer-t px-drawer-x pb-drawer-b"
```

## 9. What the prose sections are for

Frontmatter can't hold everything; prose lands as:

| DESIGN.md section | Lands in |
|---|---|
| Visual Theme & Atmosphere | overall density/whitespace → fixes control size tier |
| Color Palette & Roles | each colour's **boundary** ("status colours appear on dots and trend figures, never as large fills") — basis for cutting cva variants, source for section 2 checks |
| Typography Rules | weight bias, letter-spacing direction, line-height tiers |
| Layout Principles | max container width, breakpoints, **minimum hit area** → decides Button size variants |
| Elevation & Depth | shadow strategy. "Hairline borders, almost no shadow" rules out `shadow-md`; glassmorphism → `backdrop-blur-*` over translucent fill with border |
| Shapes | shape language, corroborates section 7 radii |
| Component Stylings | per-component specs, direct implementation basis |
| Closing "inconsistencies" appendix, if present | extraction gaps. **Do not implement** — relay to user to decide |

Prose vs frontmatter conflict → **frontmatter wins** (machine extracted); send conflict to user.

## 10. The Step 1 table

Hand over scan-friendly table, not config file:

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

List last two kinds separately: **tokens added beyond library slots** and **anything DESIGN.md doesn't cover needing user decision**. Neither buried in config.