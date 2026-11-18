---
title: Signal business failures with BizException, never by returning null
impact: HIGH
tags: envelope, exception, error-handling
---

## Signal business failures with BizException, never by returning null

Throw `BizException` on business failure — never return `null` for "not found". Returning `null` pushes null-checks onto every caller, where one missed check causes `NullPointerException` and drops failure reason.

**Wrong:**

```java
public UserDetailResponse getById(Long id) {
    UserEntity e = userMapper.selectById(id);
    return e == null ? null : converter.toResponse(e); // ❌
}
```

**Right:**

```java
public UserDetailResponse getById(Long id) {
    UserEntity e = userMapper.selectById(id);
    if (e == null) {
        throw new BizException(ErrorCode.USER_NOT_FOUND);
    }
    return converter.toResponse(e);
}
```

`GlobalExceptionHandler` converts `BizException` into coded `R` envelopes. Return `Optional` only when absence is a normal branch (e.g., optional feature config).
