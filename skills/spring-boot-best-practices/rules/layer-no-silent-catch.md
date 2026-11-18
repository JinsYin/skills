---
title: Never silently swallow exceptions
impact: HIGH
impactDescription: Failures propagate silently
tags: layer, exception, error-handling
---

## Never silently swallow exceptions

Translate caught exceptions into domain errors or rethrow — never catch without handling or rethrowing. Silent `catch` masks failure as 200 OK with empty/partial state, pushing crash downstream after root-cause context is lost.

**Wrong:**

```java
try {
    userMapper.insert(entity);
} catch (Exception e) {
    // ❌ does nothing; caller assumes insert succeeded
}
```

**Right (translate to domain error or let global handler wrap):**

```java
try {
    externalClient.sync(entity);
} catch (RestClientException e) {
    log.warn("Upstream sync failed, entityId={}", entity.getId(), e);
    throw new BizException(ErrorCode.UPSTREAM_UNAVAILABLE);
}
```

Swallowing allowed only on non-critical side channels (e.g., telemetry), and must log warning plus comment explaining why failure is safe to ignore.
