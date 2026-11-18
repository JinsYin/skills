---
title: Keep HTTP types out of Services
impact: CRITICAL
tags: layer, service, http, request
---

## Keep HTTP types out of Services

Services take typed arguments. `Express.Request`, `@Req()`, headers, and status codes stay in the Controller. A Service that reads the request cannot be called from a cron job, a queue worker, or a unit test without spinning up HTTP.

**Wrong:**

```ts
async updateProfile(req: Request) { // ❌
  const userId = (req.user as JwtUser).sub;
}
```

**Right:**

```ts
// Controller
@Patch('profile')
async update(@CurrentUser() user: JwtUser, @Body() body: UserUpdateProfileRequest) {
  return R.ok(await this.userService.updateProfile(user.sub, body));
}

// Service — reusable from HTTP, jobs, and tests
async updateProfile(userId: bigint, body: UserUpdateProfileRequest) { /* ... */ }
```

Read the authenticated principal in the Controller (or a param decorator) and pass `userId` explicitly.
