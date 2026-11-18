---
title: Name Responses by view
impact: HIGH
tags: dto, response, swagger
---

## Name Responses by view

Name responses by view, not by the table: `OrderDetailResponse`, `OrderListItemResponse`, `OrderCreateResponse`. A list row that reuses the detail class ships unused columns on every page.

Every field has `@ApiProperty({ description })` in Chinese. That text is the OpenAPI description. Enable the Nest Swagger CLI plugin so the Controller return type is picked up; the decorator is still required because generics erase the field list.

```ts
export class OrderDetailResponse {
  @ApiProperty({ description: '订单 ID' })
  id!: string;

  @ApiProperty({ description: '订单编号' })
  orderNo!: string;
}
```
