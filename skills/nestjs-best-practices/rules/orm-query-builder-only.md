---
title: Build queries with the Drizzle builder, not full-statement SQL
impact: CRITICAL
tags: orm, drizzle, sql, query
---

## Build queries with the Drizzle builder, not full-statement SQL

Repository methods use the Drizzle builder (`select` / `insert` / `update` / `delete`, `eq`, `and`, joins). A full SQL string binds one dialect, and a concatenated value is injection. A `sql` fragment is only for a predicate the builder cannot express; every value in it is a bound parameter. Migration files and overlays are SQL on purpose: follow `db-migration-*` and `db-gauss-dialect` there.

**Wrong:**

```ts
await this.txHost.tx.execute(sql.raw(`select * from t_user where name = '${name}'`)); // ❌
```

**Right:**

```ts
await this.txHost.tx
  .select()
  .from(userTable)
  .where(and(eq(userTable.deleted, false), eq(userTable.name, name)));
```

```ts
// Bound fragment when the builder has no operator for it
sql`${userTable.name} ILIKE ${'%' + name + '%'}`;
```

Upsert in the Service, or with `INSERT ... SELECT ... WHERE NOT EXISTS` in a migration. `.onConflictDoUpdate()` and `.onConflictDoNothing()` emit `ON CONFLICT`, which Gauss rejects (`db-gauss-dialect`).
