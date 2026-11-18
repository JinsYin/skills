---
title: Controllers must never return Drizzle rows
impact: CRITICAL
impactDescription: Password hashes and soft-delete flags reach the client; new columns silently widen public output
tags: layer, controller, response, drizzle, security
---

## Controllers must never return Drizzle rows

Return a view `Response` from Controllers and from Services. A Drizzle row is the table: password hash, `deleted`, audit columns. Adding a column later widens the JSON with no compile error if the return type is the row or `any`.

Service methods return `Response`, `Dto`, or primitives — never the row type inferred from `userTable.$inferSelect`.

**Wrong:**

```ts
@Get(':id')
async get(@Param('id', ParseSnowflakePipe) id: bigint) {
  return R.ok(await this.userService.getRow(id)); // ❌ row includes passwordHash
}
```

**Right:**

```ts
@Get(':id')
async get(@Param('id', ParseSnowflakePipe) id: bigint): Promise<R<UserDetailResponse>> {
  return R.ok(await this.userService.getById(id));
}
```
