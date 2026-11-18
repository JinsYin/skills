---
title: Register auth guards globally and opt out explicitly
impact: CRITICAL
impactDescription: A Controller without its guard decorator ships unauthenticated
tags: auth, guard, jwt, permission, decorator
---

## Register auth guards globally and opt out explicitly

Register `JwtAuthGuard` and `PermissionGuard` with `APP_GUARD`. Default is deny. A route is public only when it carries `@Public()`. A route that is not public must carry `@RequirePermissions(...)`. Missing metadata is 401 or 403, not an open route.

`useGlobalGuards()` in `main.ts` does not run under `@nestjs/testing`. `APP_GUARD` does.

| Guard | No `@Public()` | `@Public()` |
|---|---|---|
| `JwtAuthGuard` | Valid access token required, else 401 | Skip |
| `PermissionGuard` | `@RequirePermissions` required, else 403 | Skip |

**Wrong (opt-in guard — the next handler is public):**

```ts
@Controller('users')
export class UserController {
  @Get(':id')
  @UseGuards(JwtAuthGuard) // ❌ sibling methods forget this and stay open
  async get() { /* ... */ }
}
```

**Right:**

```ts
@Module({
  providers: [
    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: APP_GUARD, useClass: PermissionGuard },
  ],
})
export class AuthModule {}

@Controller('users')
export class UserController {
  @Get(':id')
  @RequirePermissions('user:query')
  async get() { /* ... */ }
}

@Controller('auth')
export class AuthController {
  @Post('login')
  @Public()
  async login() { /* ... */ }
}
```

Do not mount a second auth stack (Passport session + a hand-rolled guard). One mechanism, so allow/deny order stays readable.
