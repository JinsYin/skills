---
title: Signal business failures with BizException, never by returning null
impact: HIGH
tags: envelope, exception, null
---

## Signal business failures with BizException, never by returning null

Throw `BizException` when the business rule fails, including "not found". `null` pushes the check onto every caller, and the one that forgets throws a `TypeError` with the reason already lost.

**Wrong:**

```ts
async getById(id: bigint) {
  const row = await this.users.findById(id);
  return row ? this.converter.toDetail(row) : null; // ❌
}
```

**Right:**

```ts
async getById(id: bigint): Promise<UserDetailResponse> {
  const row = await this.users.findById(id);
  if (!row) throw new BizException(ErrorCode.NOT_FOUND);
  return this.converter.toDetail(row);
}
```

Return `null` only when absence is a normal branch the caller is written to handle (optional config). The exception filter turns `BizException` into the envelope (`envelope-factory-only`).
