---
title: A README at the root and in every module
impact: MEDIUM
impactDescription: Package boundaries become guesswork and components get copied instead of reused
tags: stack, structure, docs, readme
---

## A README at the root and in every module

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
