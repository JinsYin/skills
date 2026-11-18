---
title: Standard field types across payloads
impact: HIGH
tags: envelope, json, decimal, id, date
---

## Standard field types across payloads

| Domain | On the wire | In the Service | Never |
|---|---|---|---|
| Timestamps | `string` `yyyy-MM-dd HH:mm:ss` | `Date` (column `withTimezone: false`) | `Date.toISOString()`, a raw `Date` in the response |
| Money | decimal `string` scale 2 (`"12.50"`) | `string` or `Big` | `number` |
| Ids | decimal `string` | `bigint` | `number`, a raw `bigint` in JSON |
| Enums | the declared wire value | the enum | default numeric enum |

`Date.toISOString()` emits a UTC `Z` instant. The Spring side emits `LocalDateTime` with no offset. A shared client then parses two different strings for one column. One serializer in the envelope module formats and parses `yyyy-MM-dd HH:mm:ss`.

`number` cannot hold 64-bit snowflakes or base-10 money. A JSON number that looks right in a small fixture rounds in production. Decimal strings survive both.

One entity uses one id representation. Do not mix `string` and `number` ids on the same resource.
