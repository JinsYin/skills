---
title: Index naming with uk_ and idx_ prefixes
impact: MEDIUM
tags: db, naming, index
---

## Index naming with uk_ and idx_ prefixes

- Unique index: `uk_{table}_{field...}`
- Non-unique index: `idx_{table}_{field...}`

Include `{table}` so index names stay unique schema-wide — DBs with schema-scoped index namespaces fail DDL on duplicate names across tables.

```sql
CREATE UNIQUE INDEX uk_user_email ON t_user(email);
CREATE INDEX idx_order_created_at ON t_order(created_at);
```

On new tables, declare uniqueness inline in `CREATE TABLE` via `CONSTRAINT uk_x UNIQUE(...)` rather than adding a separate index afterward — inline constraints keep global-uniqueness semantics across distributed and standalone deployments.
