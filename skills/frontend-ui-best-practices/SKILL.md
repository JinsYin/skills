---
name: frontend-ui-best-practices
description: Stack baseline and module documentation rules for React + shadcn/ui frontend projects. Covers the package manager, build tool, framework, component library, styling and testing choices, plus the README structure required at the repository root and in every monorepo package. Use when initialising a frontend project, changing dependency choices, adding a package, or writing module documentation. Interface and interaction rules — forms, overlays, lists, formats, icons — are out of scope.
license: MIT
metadata:
  author: JinsYin
  version: "2.1.0"
---

# Frontend UI Best Practices

**Stack and structure** rules for React + shadcn/ui frontend projects: 2 rules.

Interface and interaction rules (validation timing, overlay state, destructive confirmation,
pagination and alignment, date and number formats, icon and toast consistency) belong to
`ui-ux-best-practices` and are not repeated here.

## How to use this skill

| What you are doing | Read |
|---|---|
| Initialising a project / changing dependencies | `rules/stack-baseline.md` |
| Adding a package / writing module docs | `rules/stack-module-readme.md` |

Each rule states what to do and **why**.

## Rule index

### 1. Stack & structure (LOW)

- `stack-baseline` — pnpm + Vite + React + TS + shadcn/ui + Tailwind + Vitest
- `stack-module-readme` — a README at the root, and one per package in a monorepo

## Relationship to the project's CLAUDE.md

This is a **cross-project** baseline. Directory layout, routing and state management follow the
project's own `CLAUDE.md`; where they conflict, `CLAUDE.md` wins.

## Full compiled version

To take in every rule at once, read `AGENTS.md`. It is generated from `rules/` by
`scripts/build.sh` — **do not edit it by hand**.
