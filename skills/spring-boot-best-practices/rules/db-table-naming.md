---
title: Table names use t_ prefix, snake_case, and singular nouns
impact: HIGH
tags: db, naming, sql
---

## Table names use t_ prefix, snake_case, and singular nouns

Name domain tables `t_` + `snake_case` + **singular noun**: `t_order`, `t_user`, `t_order_item`. `t_` separates domain tables from views, staging tables, and framework tables; singular nouns match Entity classes 1-to-1 without `t_users` ↔ `UserEntity` mismatch.

Bind every Entity explicitly via `@TableName`, never implicit camel-to-snake conversion:

```java
@Data
@TableName("t_order_item")
public class OrderItemEntity { }
```
