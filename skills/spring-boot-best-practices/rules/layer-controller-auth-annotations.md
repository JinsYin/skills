---
title: Declare permission checks with annotations, not inside method bodies
impact: HIGH
impactDescription: A missed check leaves the endpoint wide open
tags: layer, controller, auth, security, spring-security, sa-token
---

## Declare permission checks with annotations, not inside method bodies

Enforce auth via declarative framework config and annotations — never inline `if` checks inside controller methods. Declarative security **fails closed**: once fallback rule is wired, new endpoints stay protected automatically. Imperative checks **fail open**: one forgotten `if` exposes endpoint unauthenticated, and privileged test tokens still get 200.

See `stack-auth-framework` for framework selection. Equivalent forms:

| Requirement | Spring Security | Sa-Token |
|---|---|---|
| Authenticated user | `.anyRequest().authenticated()` fallback in `SecurityFilterChain` | `@SaCheckLogin` at class level |
| Permission code | `@PreAuthorize("hasAuthority('user:query')")` | `@SaCheckPermission("user:query")` |
| Role | `@PreAuthorize("hasRole('admin')")` | `@SaCheckRole("admin")` |
| Public endpoint | `.requestMatchers("/auth/login").permitAll()` | `@SaIgnore` |

Silent failure modes (neither throws an exception):

- **Spring Security**: `@PreAuthorize` requires `@EnableMethodSecurity` (replaces `@EnableGlobalMethodSecurity` since Spring Security 6); without it, method annotations are ignored and all methods allow access. Also, `hasRole('admin')` matches authority `ROLE_admin` — stored authorities missing `ROLE_` prefix always evaluate `false`.
- **Sa-Token**: allows requests by default, checking only annotated or intercepted handlers. Put `@SaCheckLogin` on controller class so new methods inherit login check.

Register public endpoints **explicitly** (`permitAll()` in Spring Security, `@SaIgnore` in Sa-Token), never by omitting annotations — explicit opt-out proves openness is intentional.

**Wrong (inline check inside method body — fails open):**

```java
@GetMapping
public RPage<UserListItemResponse> page(@Valid UserPageQuery query) {
    if (!StpUtil.hasPermission("user:query")) {   // relies on human memory; next method forgotten = exposed
        throw new BizException(ErrorCode.FORBIDDEN);
    }
    return RPage.ok(userService.listUsers(query));
}
```

**Right (Spring Security):**

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity   // without this, @PreAuthorize below is silently ignored
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                // Pure Bearer token with no Cookie session: CSRF adds nothing; keep enabled if token is in a Cookie
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/auth/login").permitAll()   // register public endpoints explicitly
                        .anyRequest().authenticated())                // default deny fallback
                .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
                .build();
    }
}

@Tag(name = "用户")
@RestController
@RequestMapping("/users")
@Validated
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "分页查询用户")
    @GetMapping
    @PreAuthorize("hasAuthority('user:query')")
    public RPage<UserListItemResponse> page(@Valid UserPageQuery query) {
        return RPage.ok(userService.listUsers(query));
    }
}
```

**Right (Sa-Token):**

```java
@Tag(name = "用户")
@SaCheckLogin   // class-level so new methods inherit login check automatically
@RestController
@RequestMapping("/users")
@Validated
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @Operation(summary = "分页查询用户")
    @GetMapping
    @SaCheckPermission("user:query")
    public RPage<UserListItemResponse> page(@Valid UserPageQuery query) {
        return RPage.ok(userService.listUsers(query));
    }
}
```
