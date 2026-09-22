---
title: Baseline project scaffold
impact: MEDIUM
impactDescription: Imports fail to resolve and component styles vanish with no error
tags: stack, scaffold, config
---

## Baseline project scaffold

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
