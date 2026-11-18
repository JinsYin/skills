---
title: Table names use t_ prefix, snake_case, and singular nouns
impact: HIGH
tags: db, naming, table, drizzle
---

## Table names use t_ prefix, snake_case, and singular nouns

Name domain tables `t_` + `snake_case` + a **singular** noun: `t_order`, `t_user`, `t_order_item`. The prefix separates domain tables from `drizzle.__drizzle_migrations` and from views. Singular names match the module name without a `t_users` / `User` plural mismatch.

Pass the table name explicitly. Do not rely on a global `casing: 'snake_case'` to invent it — renaming the TypeScript binding would rename the physical table on the next generate.

```ts
export const orderItem = pgTable('t_order_item', { /* ... */ });
```
