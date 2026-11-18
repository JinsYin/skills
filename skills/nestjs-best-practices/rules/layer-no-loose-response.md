---
title: Never use loose types as response payloads
impact: CRITICAL
tags: layer, response, openapi, typescript
---

## Never use loose types as response payloads

The payload inside `R` / `RList` / `RPage` is a named class, not `any`, `object`, `Record<string, unknown>`, or `Map`. Loose types erase the OpenAPI schema and let a renamed field ship without a compiler error.

**Wrong:**

```ts
@Get('stats')
async stats(): Promise<R<Record<string, unknown>>> {
  return R.ok({ total: 100, active: 80 }); // ❌ invisible contract
}
```

**Right:**

```ts
export class StatsResponse {
  @ApiProperty({ description: '总数' })
  total!: number;

  @ApiProperty({ description: '活跃数' })
  active!: number;
}
```

File downloads return `StreamableFile` and skip the envelope. That is the only untyped payload.
