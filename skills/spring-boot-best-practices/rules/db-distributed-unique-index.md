---
title: Distributed unique constraints must include the distribution key or use a global index
impact: HIGH
impactDescription: Plain unique indexes enforce uniqueness per shard only, allowing cross-shard duplicates
tags: db, migration, distributed, unique-index, gaussdb
---

## Distributed unique constraints must include the distribution key or use a global index

Distributed DBs (GaussDB Distributed, TiDB, OceanBase) shard rows by distribution key. **Plain unique indexes are shard-local**: if unique column omits distribution key, identical values on different shards insert silently without error.

Choose DDL by whether table is new in this migration:

**New table — inline table constraint (portable across topologies):**

```sql
CREATE TABLE t_authcode_agreement (
    auth_code   VARCHAR(64) NOT NULL,
    ...
    CONSTRAINT uk_authcode_agreement_auth_code UNIQUE (auth_code)
);
```

Distributed engines build a global index automatically; standalone engines build a normal unique constraint — **one SQL file works everywhere** without overlay fork (see `db-migration-base-overlay`).

**Existing table — explicit Global Unique Index (GSI):**

```sql
-- ❌ Shard-local on distributed DBs; duplicates slip in across shards
CREATE UNIQUE INDEX uk_org_name ON t_org(org_name);

-- ✅ Distributed: GSI distributed on the indexed column
CREATE GLOBAL UNIQUE INDEX uk_org_name ON t_org(org_name) DISTRIBUTE BY HASH(org_name);
```

Standalone/centralized engines reject `CREATE GLOBAL UNIQUE INDEX`, so **only this case** forks into topology overlays where centralized overlay uses plain `CREATE UNIQUE INDEX`.

`ALTER TABLE ... ADD UNIQUE` on existing distributed tables carries same distribution-key requirement and does not bypass this rule.
