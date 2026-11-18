---
title: Service and Repository method naming
impact: MEDIUM
tags: naming, service, repository
---

## Service and Repository method naming

**Service** methods include the resource noun so a cross-module call reads clearly:

- Writes: `create{Name}` / `update{Name}` / `remove{Name}` (soft) / `delete{Name}` (hard). Domain actions: `cancel{Name}` / `approve{Name}`.
- Reads: `getById` / `getBy{Xxx}` (one), `listAll{Name}s` (unpaginated), `list{Name}Options`, `list{Name}s` (paginated).
- Returns: `Response`, `Dto`, or a primitive. Never a Drizzle row (`layer-controller-no-row`).

**Repository** methods: `findById` / `findBy{Xxx}` (one or null), `listBy{Xxx}`, `countBy{Xxx}`, `existsBy{Xxx}`, `insert`, `updateById`, `insertMany`. A Repository returns rows or a count, not a `Response`.
