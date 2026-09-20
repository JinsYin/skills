---
title: Date and number formats
impact: MEDIUM
impactDescription: Values get misread
tags: format, date, number, i18n
---

## Date and number formats

| Type | Format | Example |
|---|---|---|
| Date | `YYYY-MM-DD` | `2026-04-23` |
| Datetime | `YYYY-MM-DD HH:mm:ss` | `2026-04-23 09:00:00` |
| Number | **no comma separators** | `1234567`, not `1,234,567` |

ISO order, not `04/23/2026` — the latter reads as April 23 in one region and as month 23
(invalid) in another, the most common misreading in cross-region work.

Numbers must not use comma separators because these values get copied into Excel or an API client,
where the separator breaks parsing. If one screen genuinely needs thousands separators for
readability, make it an explicit local exception rather than the global default.
