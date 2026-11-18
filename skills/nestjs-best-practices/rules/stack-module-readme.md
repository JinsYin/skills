---
title: Maintain a README at the repository root and in every package
impact: LOW
tags: stack, readme, pnpm, workspace
---

## Maintain a README at the repository root and in every package

A pnpm workspace has a root `README.md` and one `README.md` per package. The root README says what the system does, lists packages, records the stack line from `stack-baseline`, and shows `pnpm` install / dev / test / migrate commands. A package README says what that package owns, what it must not contain, and what it exports.

A single-package app has only the root README, with a "Package layout" section that matches `naming-module-layout`.

Update the README in the same change as a new package, a new public provider, or a new script. When a doc mentions a version, point at the catalog or `stack-baseline`, not a second hardcoded number.

`README.md` is for people. Project `CLAUDE.md` locks decisions for agents (topology, JWT algorithm, worker-id scheme). Do not paste these rules into `CLAUDE.md`.
