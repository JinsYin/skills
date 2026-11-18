---
title: Choose R, RList, or RPage by payload shape
impact: HIGH
tags: envelope, response, pagination
---

## Choose R, RList, or RPage by payload shape

The JSON envelope matches the Spring backends: `code`, `message`, and `data`. Pagination fields sit on `RPage`, not on a side `meta` object and not on a `success` boolean. Callers branch on `code`.

| Payload | Type |
|---|---|
| One object | `R<NameResponse>` |
| Unpaginated list | `RList<NameResponse>` |
| Paginated list | `RPage<NameResponse>` |
| Flag | `R<boolean>` |
| Empty success | `R<null>` via `R.okEmpty()` |

```ts
export class RPage<T> {
  code!: number;
  message!: string;
  data!: T[];
  total!: number;
  pageNo!: number;
  pageSize!: number;
}
```

**Wrong:**

```ts
return R.ok(page.data); // ❌ drops total / pageNo / pageSize
```

**Right:**

```ts
@Get()
async page(@Query() query: UserPageQuery): Promise<RPage<UserListItemResponse>> {
  return RPage.ok(await this.userService.listUsers(query));
}
```

Services return `PageResult<T>` (`data`, `total`, `pageNo`, `pageSize`). Controllers wrap it with `RPage.ok`. Do not add a response interceptor that wraps a second time — the Controller return value is already the body.
