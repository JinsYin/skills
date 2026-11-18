---
title: Generate reviewed SQL migrations; never push or synchronize
impact: CRITICAL
impactDescription: Schema push drops columns with no migration record
tags: db, migration, drizzle-kit, push, synchronize
---

## Generate reviewed SQL migrations; never push or synchronize

Change schema by editing the Drizzle table, running `drizzle-kit generate`, and committing the SQL plus `meta/_journal.json` and the snapshot. Review the SQL for the Gauss denylist (`db-gauss-dialect`) before merge.

`drizzle-kit push` alters the live database to match the schema and writes no migration. The next environment does not replay that change, and a dropped column is already gone. There is no runtime `synchronize` flag in this stack; do not add one.

**Wrong:**

```json
{ "scripts": { "db:sync": "drizzle-kit push" } }
```

**Right:**

```json
{ "scripts": { "db:generate": "drizzle-kit generate" } }
```

Apply the committed SQL only from the migrator job (`db-migration-dedicated-job`).
