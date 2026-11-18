---
title: Standard field types across payloads
impact: HIGH
tags: envelope, response, jackson, types, money
---

## Standard field types across payloads

| Domain | Use | Never use |
|---|---|---|
| Dates & timestamps | `LocalDate` / `LocalDateTime` / `OffsetDateTime` | `java.util.Date` |
| Monetary amounts | `BigDecimal` (fixed scale 2) | `double` / `float` |
| Primary & foreign IDs | `Long` (Snowflake) **or** `String` (UUID) | Mixing both on one entity |
| Enums | `@JsonValue` with explicit wire value | Implicit `name()` |

Why:

- `java.util.Date` conflates instant and timezone while mutable, causing cross-timezone JSON drift; `LocalDateTime` formats as `yyyy-MM-dd HH:mm:ss` via shared Jackson serializer in `commons`.
- Binary floats cannot represent base-10 decimals, causing money rounding drift caught only at reconciliation.
- Mixing `Long` and `String` IDs on one entity breaks uniform client handling and risks JS IEEE-754 precision loss on unquoted 64-bit Snowflake IDs.

**Wrong:**

```java
private Date createdAt;      // ❌
private double amount;       // ❌ loses decimal precision
private Long id;
private String parentId;     // ❌ inconsistent with id type
```

**Right:**

```java
private LocalDateTime createdAt;
private BigDecimal amount;   // scale = 2
private Long id;
private Long parentId;
```
