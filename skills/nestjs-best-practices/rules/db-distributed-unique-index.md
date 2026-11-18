---
title: Distributed unique constraints must include the distribution key or use a global index
impact: HIGH
impactDescription: Duplicates insert silently across shards
tags: db, gaussdb, distributed, unique, index, drizzle
---

## Distributed unique constraints must include the distribution key or use a global index

On distributed GaussDB a plain unique index is shard-local. If the unique columns do not include the distribution key, the same value inserts on two shards and no error is raised.

**New table — inline table constraint (portable, stays in base):**

```ts
export const agreement = pgTable(
  't_authcode_agreement',
  { authCode: varchar('auth_code', { length: 64 }).notNull() },
  (t) => [unique('uk_authcode_agreement_auth_code').on(t.authCode)],
);
```

The generated SQL must contain `CONSTRAINT uk_authcode_agreement_auth_code UNIQUE ("auth_code")` inside `CREATE TABLE`. Distributed Gauss builds a global index from that inline constraint; standalone Gauss builds a normal constraint. One base file, no overlay.

**Existing table — explicit global unique index, overlay only:**

```sql
-- distributed overlay
CREATE GLOBAL UNIQUE INDEX uk_org_name ON t_org(org_name) DISTRIBUTE BY HASH(org_name);

-- centralized / openGauss overlay
CREATE UNIQUE INDEX uk_org_name ON t_org(org_name);
```

`uniqueIndex()` in the Drizzle schema emits a standalone `CREATE UNIQUE INDEX`, which is shard-local on a distributed cluster. Do not use it for a uniqueness rule. `ALTER TABLE ... ADD UNIQUE` on an existing distributed table has the same distribution-key requirement.
