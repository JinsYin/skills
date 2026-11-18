---
title: Split multi-topology migrations into generated base plus custom overlays
impact: HIGH
tags: db, migration, drizzle, gauss, topology, overlay
---

## Split multi-topology migrations into generated base plus custom overlays

Drizzle generates one PostgreSQL journal. Topologies (distributed GaussDB, centralized GaussDB, openGauss) share that journal as the **base**. SQL that has no portable form — a global unique index on an existing table — lives in an **overlay**, one directory per target. Do not copy the whole schema into each overlay.

```text
drizzle/                          # drizzle-kit output, portable DDL only
  0007_order.sql
  meta/_journal.json
drizzle/overlay/
  distributed/0007_org_name.sql   # CREATE GLOBAL UNIQUE INDEX ...
  centralized/0007_org_name.sql   # CREATE UNIQUE INDEX ...
  opengauss/0007_org_name.sql
```

The migrator runs base, then exactly one overlay chosen by required config `DB_TOPOLOGY`. No default topology. Overlay files are not listed in `_journal.json` — Drizzle would skip or mis-order them by `when`.

The runner creates `drizzle.__sql_overlays` (`name`, `sha256`) itself (`CREATE TABLE IF NOT EXISTS`) and records each applied overlay file. If the hash of an already applied file changes, the job fails. Do not put that bookkeeping table in a generated migration or an overlay. That is the check Drizzle does not do for base files (`db-migration-immutable-after-apply`).

A version number appears in every overlay or in none. Sibling files match outside the divergent statement and a header comment. Portable DDL (inline `CONSTRAINT uk_... UNIQUE` on a new table) stays in base and does not get an overlay copy.

See `db-distributed-unique-index` for which statement is portable.
