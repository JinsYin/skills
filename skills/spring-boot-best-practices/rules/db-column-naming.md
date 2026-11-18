---
title: Column naming and standard audit columns
impact: HIGH
tags: db, naming, audit, soft-delete
---

## Column naming and standard audit columns

- Column names: `snake_case` (`order_no`).
- Primary key: `id`, `BIGINT` or `VARCHAR(32)` matching primary-key strategy.
- Foreign-key columns: `fk_{ref}_id`.
- Booleans: semantic names (`enabled`, `is_default`, `deleted`), `TINYINT(1)` (`0 = false` / `1 = true`).
- Four audit columns: `created_at`, `updated_at`, `created_by`, `updated_by`.
- Soft delete: `deleted TINYINT(1) NOT NULL DEFAULT 0` (`1` = deleted).

Use semantic boolean names; never name columns `flag` or `type` where `flag = 1` loses meaning over time.
