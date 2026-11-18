---
title: One-way layered dependencies
impact: CRITICAL
tags: layer, architecture, controller, service, repository
---

## One-way layered dependencies

`Controller → Service → Repository`: each layer depends only on the adjacent lower layer. Only Repositories touch Drizzle. Reverse or skip-layer calls skip transaction boundaries, validation, and make the use case untestable without a database.

| Layer | Responsibility | Forbidden |
|---|---|---|
| Controller | HTTP contract: routing, binding, auth metadata, envelope | Injecting a Repository, `TransactionHost`, or the Drizzle handle; calling other Controllers |
| Service | Business rules, `@Transactional()` boundaries, orchestration, external calls | HTTP types; another module's Repository |
| Repository | Drizzle queries on this module's tables | Business rules, HTTP, opening its own transaction |

**Wrong (Controller queries Drizzle and skips the Service transaction):**

```ts
@Controller('users')
export class UserController {
  constructor(@Inject(DRIZZLE) private readonly db: AppDatabase) {} // ❌

  @Get(':id')
  async get(@Param('id') id: string) {
    return this.db.select().from(userTable).where(eq(userTable.id, BigInt(id)));
  }
}
```

**Right:**

```ts
@Controller('users')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Get(':id')
  async get(@Param('id', ParseSnowflakePipe) id: bigint): Promise<R<UserDetailResponse>> {
    return R.ok(await this.userService.getById(id));
  }
}
```
