---
title: Controller method names and declaration order
impact: MEDIUM
tags: naming, controller, method
---

## Controller method names and declaration order

CRUD methods use the resource-free verb. The class name already says which resource.

`page` (paginated) / `list` (full list) / `select` (dropdown) / `get` / `create` / `update` / `delete` (hard delete) / `remove` (soft delete).

Non-CRUD actions use `{verb}{Resource}`: `cancelProcess`, `resetPassword`.

Declare CRUD methods first, in the order `page → list → select → get → create → update → delete/remove`. Do not declare both `delete` and `remove` on one Controller.

```ts
@Get()                 async page(@Query() query: UserPageQuery): Promise<RPage<UserListItemResponse>>
@Get('all')            async list(): Promise<RList<UserListItemResponse>>
@Get('options')        async select(): Promise<RList<UserOptionResponse>>
@Get(':id')            async get(@Param('id', ParseSnowflakePipe) id: bigint): Promise<R<UserDetailResponse>>
@Post()                async create(@Body() body: UserCreateRequest): Promise<R<UserCreateResponse>>
@Put(':id')            async update(...): Promise<R<boolean>>
@Delete(':id')         async remove(...): Promise<R<boolean>>
```

`list` queries cap the row count in the Repository. An unbounded `select()` is an outage.
