---
title: Name Requests by action and enforce Jakarta Validation
impact: HIGH
tags: dto, request, validation
---

## Name Requests by action and enforce Jakarta Validation

Name requests `{Name}{Action}Request` — `OrderCreateRequest`, `OrderUpdateRequest`, `OrderCancelRequest`. Avoid catch-all `OrderRequest` unless resource has only one write action: create and update differ in required fields, so sharing one class forces looser constraints on both.

Every constrained field **must** carry Jakarta Validation annotations with Chinese `message` (returned directly to frontend).

**Right:**

```java
@Data
@Schema(description = "创建订单请求")
public class OrderCreateRequest {
    @Schema(description = "产品 ID", example = "1001")
    @NotNull(message = "产品 ID 不能为空")
    private Long productId;

    @Schema(description = "数量", example = "2")
    @NotNull(message = "数量不能为空")
    @Min(value = 1, message = "数量必须大于等于 1")
    @Max(value = 999, message = "数量必须小于等于 999")
    private Integer quantity;
}
```

Handle `MethodArgumentNotValidException` centrally in `GlobalExceptionHandler` — never write manual null/range `if` checks in Controllers.
