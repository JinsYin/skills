---
title: Never silently swallow errors
impact: CRITICAL
tags: layer, exception, promise, async
---

## Never silently swallow errors

A swallowed error becomes HTTP 200 with an empty or partial body. Translate it into `BizException` or rethrow. The same hole is an empty `catch`, `catch` that returns `null`, and a floating promise (`.catch(() => {})` or `void` without handling).

**Wrong:**

```ts
try {
  await this.orderRepository.insert(row);
} catch {
  // ❌ caller assumes the insert succeeded
}
```

**Right:**

```ts
try {
  await this.paymentClient.charge(order);
} catch (err) {
  this.logger.warn({ err, orderId: String(order.id) }, 'Upstream charge failed');
  throw new BizException(ErrorCode.UPSTREAM_UNAVAILABLE);
}
```

A non-critical side channel (metrics, audit best-effort) may catch, and then it must log at `warn` and carry a comment that says why the failure is safe to ignore.
