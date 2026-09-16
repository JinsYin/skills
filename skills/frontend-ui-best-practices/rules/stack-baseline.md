---
title: Frontend stack baseline
impact: LOW
tags: stack, dependencies
---

## Frontend stack baseline

| Layer | Choice |
|---|---|
| Package manager | pnpm |
| Build | Vite |
| Framework | React + TypeScript |
| Components | shadcn/ui (on Radix UI) |
| Styling | Tailwind CSS |
| Testing | Vitest |

shadcn/ui components are **copied into the project** rather than installed as a dependency: the
component code belongs to the project and can be edited directly, but upgrades never happen on
their own — upstream changes have to be pulled in deliberately.

Directory layout, routing and state management are left to the project's own `CLAUDE.md`; they
differ too much between projects to be fixed here.
