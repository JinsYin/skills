---
title: Paginated queries must extend PageQuery
impact: HIGH
tags: dto, query, pagination
---

## Paginated queries must extend PageQuery

`{Name}PageQuery` binds the query string and `extends PageQuery`. `PageQuery` owns `pageNo` and `pageSize` with `@Min(1)` and `@Max(200)` on `pageSize`. A query that redeclares the fields drops the cap, and `pageSize=999999` reaches the database.

**Wrong:**

```ts
export class OrderPageQuery {
  pageNo!: number;   // ❌ no @Min
  pageSize!: number; // ❌ no upper bound
}
```

**Right:**

```ts
export class PageQuery {
  @Type(() => Number)
  @IsInt()
  @Min(1, { message: '页码必须大于等于 1' })
  pageNo: number = 1;

  @Type(() => Number)
  @IsInt()
  @Min(1, { message: '每页条数必须大于等于 1' })
  @Max(200, { message: '每页条数必须小于等于 200' })
  pageSize: number = 20;
}

export class OrderPageQuery extends PageQuery {
  @IsOptional()
  @IsString()
  orderNo?: string;
}
```

An unpaginated query is `{Name}Query` and does not extend `PageQuery`. The Controller method is `page` vs `list` (`naming-controller-methods`).
