---
title: Choose R, RList, or RPage by payload shape
impact: HIGH
tags: envelope, response, pagination
---

## Choose R, RList, or RPage by payload shape

| Payload shape | Return type |
|---|---|
| Single object | `R<{Name}Response>` |
| Unpaginated list | `RList<{Name}Response>` |
| Paginated list | `RPage<{Name}Response>` |
| Success/failure flag | `R<Boolean>` |
| Empty success | `R<Void>` + `R.ok()` |

Wrong wrapper strips `total` / `pageNo` metadata or forces callers to unwrap extra nesting.

**Wrong:**

```java
public R<List<UserResponse>> page(UserPageQuery q) { // ❌ drops pagination metadata
    return R.ok(userService.page(q).getData());
}
```

**Right:**

```java
public RPage<UserResponse> page(@Valid UserPageQuery q) {
    return RPage.ok(userService.page(q));
}
```

Services return `PageResult<T>` for paginated queries; Controllers wrap via `RPage.ok(...)`.
