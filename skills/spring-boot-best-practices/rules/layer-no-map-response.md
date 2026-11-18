---
title: Never use Map as a response type
impact: HIGH
tags: layer, controller, response, openapi
---

## Never use Map as a response type

Return typed `Response` classes, never `Map<String, Object>`. `Map<String, Object>` lacks compile-time checks and renders empty OpenAPI schema, forcing callers to guess keys or read backend code. Renaming keys gives zero compiler warning.

**Wrong:**

```java
@GetMapping("/stats")
public R<Map<String, Object>> stats() {
    Map<String, Object> m = new HashMap<>();
    m.put("total", 100);
    m.put("active", 80);
    return R.ok(m); // ❌ invisible contract
}
```

**Right:**

```java
@Data
@Schema(description = "统计响应")
public class StatsResponse {
    @Schema(description = "总数") private Long total;
    @Schema(description = "活跃数") private Long active;
}
```

Sole exception: dynamic user-defined schemas (e.g., custom form builders), still wrapped inside typed envelope field.
