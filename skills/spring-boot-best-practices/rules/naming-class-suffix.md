---
title: Class suffix reference table
impact: MEDIUM
tags: naming, class
---

## Class suffix reference table

| Role | Pattern | Example | Package |
|---|---|---|---|
| Entry point | `{Project}Application` | `OrderServerApplication` | root package |
| Controller | `{Name}Controller` | `OrderController` | `controller/` |
| Service interface | `{Name}Service` | `OrderService` | `service/` |
| Service implementation | `{Name}ServiceImpl` | `OrderServiceImpl` | `service/impl/` |
| Mapper | `{Name}Mapper` | `OrderMapper` | `mapper/` |
| Entity | `{Name}Entity` | `OrderEntity` | `entity/` |
| Request body | `{Name}{Action}Request` | `OrderCreateRequest` | `dto/{domain}/` |
| Response body | `{Name}{View}Response` | `OrderDetailResponse` | `dto/{domain}/` |
| Query parameters | `{Name}Query` / `{Name}PageQuery` | `OrderPageQuery` | `dto/{domain}/` |
| Internal DTO | `{Name}Dto` | `OrderSummaryDto` | `dto/{domain}/` |
| Exception | `{Name}Exception` | `OrderLockedException` | `exception/` |
| MapStruct converter | `{Name}Converter` | `OrderConverter` | `converter/` |
| Configuration | `{Name}Config` / `{Name}Properties` | `RedisConfig` | `config/` |
| Enum | Domain noun | `OrderStatus` | `enums/` |
| Constants | `{Name}Constants` | `AuthConstants` | `constants/` |
| Utilities | `{Name}Utils` | `DateUtils` | `utils/` |

`{Name}` = **singular** domain noun (`User`, never `Users`); keep verbs on methods, not class names (never `OrderCreator`). Spell words in full outside standard industry acronyms (`Order`, never `Ord`).
