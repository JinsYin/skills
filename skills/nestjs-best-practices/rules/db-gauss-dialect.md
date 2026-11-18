---
title: Avoid Drizzle features that emit unsupported Gauss SQL
impact: HIGH
tags: db, gauss, opengauss, dialect, drizzle, sql
---

## Avoid Drizzle features that emit unsupported Gauss SQL

Gauss-family servers (GaussDB and openGauss) reject three PostgreSQL constructs. Drizzle's PostgreSQL dialect emits the first two from normal APIs. Review every generated migration for them.

| Source | SQL | Rewrite |
|---|---|---|
| `.onConflictDoUpdate()` / `.onConflictDoNothing()` | `ON CONFLICT` | `INSERT ... SELECT ... WHERE NOT EXISTS`, or do the check in the Service |
| `uuid().defaultRandom()` | `gen_random_uuid()` | Application id (`orm-id-snowflake-bigint`) or `md5(...)::uuid` in a reviewed seed |
| Hand-written `jsonb_build_object(...)` | unsupported function | JSON literal cast: `'{"a":1}'::jsonb` |

**Wrong:**

```ts
await tx.insert(configTable).values(row).onConflictDoNothing(); // ❌ ON CONFLICT
```

**Right:**

```sql
INSERT INTO t_config (k, v)
SELECT 'a', '1'
WHERE NOT EXISTS (SELECT 1 FROM t_config WHERE k = 'a');
```

`drizzle-kit` still speaks PostgreSQL. A green generate does not mean the SQL runs on Gauss. Read the new `.sql` file against this table before merging.
