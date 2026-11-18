---
title: Three openGauss SQL dialect rules
impact: HIGH
tags: db, migration, opengauss, gaussdb, sql
---

## Three openGauss SQL dialect rules

On Gauss-family DBs (openGauss / GaussDB), rewrite these **unsupported** PostgreSQL constructs:

| Unsupported | Rewrite as |
|---|---|
| `ON CONFLICT` | `INSERT ... SELECT ... WHERE NOT EXISTS`, or explicit deduplication |
| `sys_guid()` / `gen_random_uuid()` | `md5(...)::uuid` |
| `jsonb_build_object` | JSON literal cast: `'[...]'::jsonb` |

**Wrong:**

```sql
INSERT INTO t_config(k, v) VALUES ('a', '1')
ON CONFLICT (k) DO UPDATE SET v = '1'; -- ❌ unsupported on openGauss
```

**Right:**

```sql
INSERT INTO t_config(k, v)
SELECT 'a', '1'
WHERE NOT EXISTS (SELECT 1 FROM t_config WHERE k = 'a');
```

All three come from real migration failures — check before writing SQL rather than debugging broken Flyway runs.
