---
title: One icon per function, everywhere
impact: LOW
tags: consistency, icon, ux
---

## One icon per function, everywhere

The same function uses the **same icon** across the whole product — same style, size, and color
unless stated otherwise: create, edit, delete, copy, refresh, close drawer/modal, search,
disable, publish/unpublish, password reveal.

Icons are visual vocabulary the user learns once and reuses. If "delete" is a trash can on one
page and a cross on another, they have to learn it again on every page.

Export icons from one module and reference them, instead of letting each page pick its own:

```ts
// icons.ts — single source of truth
export const ActionIcon = {
  create: Plus, edit: Pencil, delete: Trash2,
  copy: Copy, refresh: RotateCw, search: Search,
} as const;
```
