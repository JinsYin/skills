---
name: frontend-ui-best-practices
description: Stack baseline and module documentation rules for React + shadcn/ui frontend projects. Covers the package manager, build tool, framework, component library, icon set, styling and testing choices, the scaffold settings that must be right from the start, the split between stylesheet and design-token files, and the README structure required at the repository root and in every monorepo package. Use when initialising a frontend project, changing dependency choices, setting up styles and tokens, adding a package, or writing module documentation. Interface and interaction rules — forms, overlays, lists, formats, icons — are out of scope.
license: MIT
metadata:
  author: JinsYin
  version: "2.2.0"
---

# Frontend UI Best Practices

**Stack and structure** rules for React + shadcn/ui frontend projects: 4 rules.

Interface and interaction rules (validation timing, overlay state, destructive confirmation,
pagination and alignment, date and number formats, icon and toast consistency) belong to
`ui-ux-best-practices` and are not repeated here.

## How to use this skill

| What you are doing | Read |
|---|---|
| Choosing or changing a dependency | `rules/stack-baseline.md` |
| Scaffolding a new project | `rules/stack-scaffold.md` |
| Setting up styles and design tokens | `rules/stack-style-files.md` |
| Adding a package / writing module docs | `rules/stack-module-readme.md` |

Each rule states what to do and **why**.

## Rule index

### 1. Stack & structure (LOW)

- `stack-baseline` — pnpm + Vite + React + TS + shadcn/ui + Tailwind + lucide + Vitest
- `stack-module-readme` — a README at the root, and one per package in a monorepo
- `stack-scaffold` — init commands, plus the four settings that must be right from the start
- `stack-style-files` — `src/styles/` split into `tailwind.css` and `tokens.css`

## Relationship to the project's CLAUDE.md

This is a **cross-project** baseline. Directory layout, routing and state management follow the
project's own `CLAUDE.md`; where they conflict, `CLAUDE.md` wins.

## Full compiled version

To take in every rule at once, read `AGENTS.md`. It is generated from `rules/` by
`scripts/build.sh` — **do not edit it by hand**.
