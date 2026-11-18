---
title: Construct response envelopes via static factories only
impact: HIGH
tags: envelope, response, api
---

## Construct response envelopes via static factories only

Construct `R` / `RList` / `RPage` via static factories only — never `new` + setters, which causes `code` drift (`0` vs `200`) and missing `message` fields.

**Wrong:**

```java
R<UserResponse> r = new R<>(); // ❌
r.setCode(0);                  // drifts from factory's 200
r.setData(user);
return r;
```

**Right:**

```java
return R.ok(user);                           // success with payload
return R.ok();                               // success without payload
return R.error(ErrorCode.DUPLICATE_NAME);    // coded failure
throw new BizException(ErrorCode.NOT_FOUND); // wrapped by GlobalExceptionHandler
```

Return `R<T>` directly from Controllers, never `ResponseEntity<R<T>>`. Reserve `ResponseEntity<Resource>` or `void` + `HttpServletResponse` for file downloads and HTTP redirects needing custom status/headers.
