---
title: 6-digit error codes prefixed with the 3-digit HTTP status
impact: HIGH
tags: envelope, error-code, api
---

## 6-digit error codes prefixed with the 3-digit HTTP status

Use fixed 6-digit business error codes: first 3 digits mirror HTTP status code, last 3 digits sequence errors within that class. Callers identify failure category without lookup tables, and gateways/logs aggregate by prefix.

**Wrong:**

```java
AUTH_INVALID(1001, "AK 或 SK 校验失败"), // ❌ category is opaque from the number
```

**Right:**

```java
@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    AUTH_INVALID(401001, 401, "AK 或 SK 校验失败"),
    AUTH_EXPIRED(401002, 401, "AK 已过期"),
    NOT_FOUND   (404001, 404, "资源不存在");

    private final int code;
    private final int httpStatus;
    private final String defaultMessage;
}
```

Each enum constant carries default Chinese `defaultMessage` so throw sites never repeat copy.
