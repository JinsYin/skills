---
title: Keep Dto internal; split dual-purpose objects
impact: HIGH
tags: dto, layering, api-contract
---

## Keep Dto internal; split dual-purpose objects

Use `{Name}Dto` only across Services, between internal Service methods, and in MQ payloads. Controllers **neither accept nor return** `Dto` types.

Split any dual-purpose internal/external class into `Dto` + `Response`. Sharing one class means adding an internal field silently widens public HTTP output with zero compile-time warning.

```
Service ←→ Service      use Dto
MQ payload              use Dto
Controller ←→ External  use Request / Response
```
