---
title: Enum and constant naming
impact: MEDIUM
tags: naming, enum, constants, jackson
---

## Enum and constant naming

- Constants: `UPPER_SNAKE_CASE` inside `final` `{Xxx}Constants` class.
- Enum types: `PascalCase`; enum constants: `UPPER_SNAKE_CASE`.

Control wire serialization explicitly via `@JsonValue` (and `@JsonCreator` when needed), never `Enum.name()` — else renaming a Java enum constant breaks HTTP/JSON contracts.

```java
@Getter
@RequiredArgsConstructor
public enum OrderStatus {
    PENDING("pending", "待支付"),
    PAID("paid", "已支付"),
    CANCELLED("cancelled", "已取消");

    private final String value;
    private final String label;

    @JsonValue
    public String getValue() { return value; }
}
```
