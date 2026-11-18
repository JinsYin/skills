---
title: Paginated queries must extend PageQuery
impact: HIGH
tags: dto, query, pagination
---

## Paginated queries must extend PageQuery

`{Name}Query` binds `GET` query strings via `@Valid @ModelAttribute`. **Paginated queries must `extends PageQuery`** to inherit `pageNo` / `pageSize` and their bounds (`pageNo >= 1`, `pageSize <= 200`).

Redeclaring pagination fields by hand drops the upper-bound check, letting `pageSize=999999` overload the DB.

**Wrong:**

```java
public class OrderPageQuery {
    private Long pageNo;    // ❌ missing @Min
    private Long pageSize;  // ❌ missing upper bound
}
```

**Right:**

```java
@Data
@Schema(description = "订单分页查询")
public class OrderPageQuery extends PageQuery {
    @Schema(description = "订单编号（模糊查询）")
    private String orderNo;

    @Schema(description = "状态")
    @EnumMatch(enumClass = OrderStatus.class)
    private String status;
}
```

Use plain `{Name}Query` for unpaginated endpoints — never inherit `PageQuery` without pagination.
