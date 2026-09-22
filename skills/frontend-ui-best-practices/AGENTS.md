# Frontend UI Best Practices

> Generated from `rules/` by `scripts/build.sh`. Do not edit by hand.
> Generated at: 2026-09-21 23:46:43

## 1. Stack & Structure


### Frontend stack baseline

| Layer | Choice |
|---|---|
| Package manager | pnpm |
| Build | Vite |
| Framework | React + TypeScript |
| Components | shadcn/ui (on Radix UI) |
| Styling | Tailwind CSS |
| Icons | lucide-react |
| Testing | Vitest |

shadcn/ui components are **copied into the project** rather than installed as a dependency: the
component code belongs to the project and can be edited directly, but upgrades never happen on
their own — upstream changes have to be pulled in deliberately.

One icon set product-wide: lucide-react is what shadcn/ui already ships with, so a second
library buys nothing but a second visual style.

Directory layout, routing and state management are left to the project's own `CLAUDE.md`; they
differ too much between projects to be fixed here.


### A README at the root and in every module

The repository root must have a `README.md`; in a monorepo every `apps/*` and `packages/*`
needs one of its own. **A single-package project needs only the root README** — describe the
top-level directories in one "structure" section there, rather than splitting them into files
that drift apart.

An unwritten boundary can only be guessed: whether the shadcn components in `packages/ui` may
be edited directly, which capabilities are shared, which internal packages an app depends on. A
guessed boundary reflects the current implementation rather than the intent, so the same
component ends up copied three times and fixed in one.

Add the README together with the package, and update it in the **same commit** as any change to
its exported components, hooks or APIs.

Root README, minimum sections:

| Section | Content |
|---|---|
| Overview | One or two sentences: which business this UI serves |
| Capabilities | The main pages and features |
| Modules | Monorepo: a table of packages with a one-line responsibility each, linked to their README. Single package: a "structure" section covering the top-level directories |
| Stack | Version baseline of package manager, build, framework, component library, styling |
| Getting started | Node/pnpm versions, install, `dev` / `build` / `test`, default port, backend URL config |

Package README in a monorepo, minimum sections:

| Section | Content |
|---|---|
| Responsibility | What belongs in this package — **and what explicitly does not** |
| Exports | The components, hooks and utilities it exposes, and who consumes them |
| Dependencies | Which internal packages and key third-party libraries, and why |
| Local commands | How to `dev` / `build` / `test` this package on its own, where possible |

A README does not replace `CLAUDE.md`, and the audiences differ: the README is for people and
states capabilities and boundaries; `CLAUDE.md` is for agents and states the decisions this
project has locked in. Never keep the same paragraph in both.


### Baseline project scaffold

Initialise a new project against the baseline stack in one pass. Retrofitting any of these
later means touching config, tests and imports at the same time.

```bash
pnpm create vite@latest <app> --template react-ts
cd <app> && pnpm install
pnpm add -D tailwindcss postcss autoprefixer @types/node
pnpm dlx tailwindcss init -p
pnpm dlx shadcn@latest init
pnpm add -D vitest jsdom @testing-library/react @testing-library/jest-dom
```

Every command is `pnpm` / `pnpm dlx`. Reaching for `npm` / `npx` / `yarn` writes a second
lockfile, and the two then resolve different versions of the same dependency.

Four settings have to be right from the start:

| Setting | Where | Why |
|---|---|---|
| `@/` → `./src` | **both** `vite.config.ts` and `tsconfig.json` / `tsconfig.app.json` | shadcn generates `@/` imports; configure only the first and type-checking breaks, only the second and the dev server throws `Failed to resolve import` |
| `content: ['./index.html', './src/**/*.{ts,tsx}']` | `tailwind.config.ts` | a path missing here strips every class underneath it — the component renders unstyled, with no error |
| `darkMode: 'class'` | `tailwind.config.ts` | leave it out and switching a shipped project to dark mode means revisiting every token |
| `environment: 'jsdom'`, `globals: true`, `setupFiles` | the `test` block of `vite.config.ts` | without it the first component test fails on `document is not defined` rather than on its assertion |

TypeScript runs in `strict` mode with `any` disabled — use `unknown` plus a type guard where a
value genuinely is not known yet.


### Styles split into tailwind.css and tokens.css

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

