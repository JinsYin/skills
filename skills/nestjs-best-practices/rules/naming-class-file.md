---
title: Class suffix and file name reference
impact: MEDIUM
tags: naming, file, class
---

## Class suffix and file name reference

| Role | Class | File |
|---|---|---|
| Module | `{Name}Module` | `{name}.module.ts` |
| Controller | `{Name}Controller` | `{name}.controller.ts` |
| Service | `{Name}Service` | `{name}.service.ts` |
| Repository | `{Name}Repository` | `{name}.repository.ts` |
| Drizzle table | `{name}Table` | `{name}.table.ts` |
| Request | `{Name}{Action}Request` | `{name}-{action}.request.ts` |
| Response | `{Name}{View}Response` | `{name}-{view}.response.ts` |
| Query | `{Name}Query` / `{Name}PageQuery` | `{name}.query.ts` / `{name}-page.query.ts` |
| Internal DTO | `{Name}Dto` | `{name}.dto.ts` |
| Converter | `{Name}Converter` | `{name}.converter.ts` |
| Exception | `BizException` or `{Name}Exception` | `{name}.exception.ts` |
| Guard | `{Name}Guard` | `{name}.guard.ts` |
| Config | `{name}Config` | `{name}.config.ts` |

`{Name}` is a singular noun (`User`, not `Users`). Verbs stay on methods (`OrderService.create`, not `OrderCreator`). Spell words in full outside standard acronyms (`Order`, not `Ord`). File names are kebab-case; multi-word modules use `order-item.service.ts` and class `OrderItemService`.
