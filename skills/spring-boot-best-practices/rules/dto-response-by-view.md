---
title: Name Responses by view
impact: MEDIUM
tags: dto, response, openapi
---

## Name Responses by view

Name responses after **view / use case**, not entity alone: `OrderDetailResponse`, `OrderListItemResponse`, `OrderCreateResponse`. List and detail views need different field sets; reusing detail class for list rows ships heavy unused fields on every page load.

```java
@Data
@Schema(description = "订单详情响应")
public class OrderDetailResponse {
    @Schema(description = "订单 ID") private Long id;
    @Schema(description = "订单编号") private String orderNo;
}
```

Annotate every field with `@Schema(description = ...)` in Chinese — sole documentation source for Knife4j.
