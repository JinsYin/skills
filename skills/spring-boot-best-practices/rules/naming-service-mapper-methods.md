---
title: Service and Mapper method naming
impact: MEDIUM
tags: naming, service, mapper
---

## Service and Mapper method naming

**Service** — **Include** resource nouns on Service methods so cross-domain call sites stay clear out of context:

- Writes: `create{Name}` / `update{Name}` / `remove{Name}` (soft delete) / `delete{Name}` (hard delete); domain actions: `cancel{Name}` / `approve{Name}`.
- Reads: `getById` / `getBy{Xxx}` (single), `listAll{Name}s` (unpaginated), `list{Name}Options` (dropdown), `list{Name}s` (paginated).
- Return types: `Response`, `Dto`, or primitives — **never** `Entity`.

**Mapper** — Use `MPJBaseMapper` for standard CRUD (`selectById`, `insert`, ...); name custom queries `selectBy{Xxx}` / `listBy{Xxx}` / `countBy{Xxx}` / `existsBy{Xxx}`, and batch writes `insertBatch` / `updateBatchById`.
