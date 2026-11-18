---
title: Lombok annotation conventions
impact: LOW
tags: stack, lombok, di
---

## Lombok annotation conventions

| Target | Annotations |
|---|---|
| DTO | `@Data` + `@NoArgsConstructor` |
| Spring bean | `@RequiredArgsConstructor` + `private final` fields for constructor injection |
| Logger | `@Slf4j` (never handwrite `LoggerFactory.getLogger`) |
| Enum fields | `@Getter` |

Use constructor injection, never `@Autowired` field injection: `final` fields enforce immutability and fail fast at startup on missing dependencies instead of throwing `NullPointerException` at runtime.

**Write explicit constructors** in two cases: static utility classes (`private` constructor + `static` methods) and classes with constructor invariant checks — Lombok constructors bypass those checks.
