---
title: Styles split into tailwind.css and tokens.css
impact: MEDIUM
impactDescription: Undefined CSS variables render the page unstyled and raise no error
tags: stack, styling, tokens
---

## Styles split into tailwind.css and tokens.css

Stylesheets live under `src/styles/`, split by responsibility:

| File | Holds |
|---|---|
| `src/styles/tailwind.css` | `@tailwind` directives, `@layer` extensions, global base rules |
| `src/styles/tokens.css` | design tokens — the CSS variables under `:root` and `.dark` |

In one file a palette change and a base-style change are indistinguishable in a diff, and the
palette is the part most often reviewed on its own.

`tailwind.css` pulls in the tokens; `main.tsx` imports only `tailwind.css`:

```css
/* src/styles/tailwind.css */
@import "./tokens.css";

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * { @apply border-border; }
  body { @apply bg-background text-foreground; }
}
```

The `@import` must come **before** the `@tailwind` directives — CSS requires it, and when it is
missing every `hsl(var(--primary))` resolves to nothing and the page renders unstyled, silently.

Point the `tailwind.css` field of `components.json` at `src/styles/tailwind.css` before running
`shadcn add`, or generated components will import a path that does not exist. `shadcn init`
writes its `:root` block into whichever file that field names — move that block into
`tokens.css` and leave `tailwind.css` holding directives and `@layer` rules only.
