---
title: 6-digit error codes prefixed with the 3-digit HTTP status
impact: HIGH
tags: envelope, error-code
---

## 6-digit error codes prefixed with the 3-digit HTTP status

Business error codes are 6 digits. The first 3 are the HTTP status; the last 3 sequence errors in that class. Gateways and clients bucket failures by prefix without a lookup table. Each constant carries a default Chinese `message` so throw sites do not invent copy.

**Wrong:**

```ts
AUTH_INVALID = 1001, // ❌ category is not visible in the number
```

**Right:**

```ts
export class ErrorCode {
  static readonly AUTH_INVALID = new ErrorCode(401001, 401, '账号或密码错误');
  static readonly AUTH_EXPIRED = new ErrorCode(401002, 401, '登录已过期');
  static readonly NOT_FOUND = new ErrorCode(404001, 404, '资源不存在');
  static readonly BAD_REQUEST = new ErrorCode(400001, 400, '请求参数错误');

  private constructor(
    readonly code: number,
    readonly httpStatus: number,
    readonly message: string,
  ) {}
}
```

The HTTP status on the response and the prefix of `code` stay equal. A `401001` body with HTTP 200 trains every client to ignore status.
