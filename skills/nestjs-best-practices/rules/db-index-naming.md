---
title: Index naming with uk_ and idx_ prefixes
impact: HIGH
tags: db, naming, index
---

## Index naming with uk_ and idx_ prefixes

- Unique constraint: `uk_{table}_{field...}` without the `t_` prefix (`uk_user_email`).
- Non-unique index: `idx_{table}_{field...}`.

Include the table so names stay unique in schemas that share one index namespace. A duplicated name fails DDL only on that engine.

```ts
(t) => [
  unique('uk_user_email').on(t.email),
  index('idx_order_created_at').on(t.createdAt),
],
```

Uniqueness on a new table is a `unique()` constraint, not `uniqueIndex()` — see `db-distributed-unique-index`.
