---
title: Enum wire values are explicit
impact: MEDIUM
tags: naming, enum, json
---

## Enum wire values are explicit

Persist and serialize an explicit string value, not the TypeScript enum member name and not a numeric enum. Renaming a member must not change JSON or the column.

```ts
export enum OrderStatus {
  Pending = 'pending',
  Paid = 'paid',
  Cancelled = 'cancelled',
}
```

```ts
status: varchar('status', { length: 32 }).notNull().$type<OrderStatus>(),
```

Validate input with `@IsEnum(OrderStatus, { message: '订单状态不合法' })`. A numeric enum (`Pending = 0`) becomes `0` in JSON the moment a decorator is forgotten, and the client cannot tell a new member from a shift.
