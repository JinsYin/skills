---
title: Fill audit columns in the Repository, not with database defaults
impact: CRITICAL
tags: orm, drizzle, audit, timestamp
---

## Fill audit columns in the Repository, not with database defaults

Set `createdAt`, `updatedAt`, `createdBy`, and `updatedBy` in the Repository on every insert and update. A database `ON UPDATE CURRENT_TIMESTAMP` is MySQL-only; on Gauss `updated_at` stays at its insert value. Drizzle `$onUpdate` does not run for a statement that sets columns through a raw fragment and skips the column list, so the Repository assignment is the source of truth.

**Wrong:**

```ts
updatedAt: timestamp('updated_at').default(sql`CURRENT_TIMESTAMP`), // ❌ never moves on UPDATE
```

**Right:**

```ts
createdAt: timestamp('created_at', { mode: 'date', withTimezone: false }).notNull(),
updatedAt: timestamp('updated_at', { mode: 'date', withTimezone: false }).notNull(),
createdBy: bigint('created_by', { mode: 'bigint' }).notNull(),
updatedBy: bigint('updated_by', { mode: 'bigint' }).notNull(),
deleted: boolean('deleted').notNull().default(false),
```

```ts
async insert(values: NewUser, actorId: bigint) {
  const now = new Date();
  await this.txHost.tx.insert(userTable).values({
    ...values,
    createdAt: now,
    updatedAt: now,
    createdBy: actorId,
    updatedBy: actorId,
  });
}
```

`withTimezone: false` matches the Spring `LocalDateTime` contract (no offset). Format it on the wire as `yyyy-MM-dd HH:mm:ss` — see `envelope-field-types`. `deleted` is boolean on Gauss; do not emit MySQL `TINYINT(1)`.
