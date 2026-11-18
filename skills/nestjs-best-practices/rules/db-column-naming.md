---
title: Explicit snake_case column names and standard audit columns
impact: HIGH
tags: db, naming, column, drizzle, audit, soft-delete
---

## Explicit snake_case column names and standard audit columns

Pass the physical column name as the first argument. A casing plugin that derives the name from the property hides a rename inside a refactor.

- Columns: `snake_case` (`order_no`).
- Primary key: `id`, `bigint`, application-generated (see `orm-id-snowflake-bigint`).
- Foreign keys: `fk_{ref}_id`, same `bigint` mode as `id`.
- Booleans: semantic names (`enabled`, `deleted`), Drizzle `boolean`. `deleted = true` means soft-deleted.
- Audit columns: `created_at`, `updated_at`, `created_by`, `updated_by` (see `orm-audit-columns-app-filled`).

```ts
orderNo: varchar('order_no', { length: 32 }).notNull(),
fkUserId: bigint('fk_user_id', { mode: 'bigint' }).notNull(),
```

Do not name a column `flag` or `type` when the value is a boolean or a status. The name has to carry the meaning after the row is read in a log.
