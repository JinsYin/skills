---
title: Construct response envelopes via static factories only
impact: HIGH
tags: envelope, factory, exception-filter
---

## Construct response envelopes via static factories only

Build `R`, `RList`, and `RPage` only through static factories. A public constructor plus property assignment drifts `code` (`0` vs `200`) and omits `message`. The constructor is `private`.

| Factory | Body |
|---|---|
| `R.ok(data)` | `code` 200, `message` `'OK'`, `data` |
| `R.okEmpty()` | `code` 200, `data` null |
| `RList.ok(items)` | `code` 200, `data` array |
| `RPage.ok(page)` | `code` 200 plus pagination fields |
| `R.error(errorCode)` | `code` from the enum, `message` from the enum, `data` null |

Controllers return the envelope directly. Do not return `HttpException` for a business failure, and do not `@Res()` the Express response to hand-write JSON — that skips the exception filter and the shared serializer.

One `@Catch()` filter maps `BizException` to `R.error` and sets the HTTP status from the error code. Validation failures become `code` `400001` with the Chinese messages joined by `；` into one `message` string, so the field stays a string, same as the Spring contract. Unknown errors become `500001` and a generic message; the stack stays in the log.
