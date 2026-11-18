---
title: Keep HTTP types out of Services
impact: HIGH
tags: layer, service, http, testability
---

## Keep HTTP types out of Services

Pass typed parameters into Services; keep `HttpServletRequest`, `request.getParameter()`, and HTTP headers/status codes out. Servlet types inside Service couple domain logic to web container — unit tests then require `MockMvc`, and cron jobs or MQ consumers cannot reuse logic.

**Wrong:**

```java
public boolean create(HttpServletRequest request) { // ❌
    String name = request.getParameter("name");
}
```

**Right (Controller parses HTTP and auth context; Service takes typed parameters):**

```java
public boolean create(UserCreateRequest request, Long operatorId) {
    // pure domain logic reusable across Controllers, cron jobs, and MQ consumers
}
```

Extract caller context (e.g., operator ID) in Controller and pass explicitly, or read via transport-agnostic context holder — never read Servlet objects in Service.
