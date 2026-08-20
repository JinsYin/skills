---
title: 权限校验用注解，不写在方法体里
impact: HIGH
impactDescription: 漏判等于接口裸奔
tags: layer, controller, auth, security, spring-security, sa-token
---

## 权限校验用注解，不写在方法体里

鉴权用框架的声明式配置与注解，不在方法体里手写 if 判断。声明式的好处是**默认拒绝**：兜底规则一旦立起来，新加的方法自动被覆盖；手写判断则是默认放行，新方法忘了写就是裸奔，而且这种遗漏在测试里通常发现不了——测试大多带着有权限的身份跑，缺校验的接口照样返回 200。

框架选型见 `stack-auth-framework`，两套的写法对照：

| 需求 | Spring Security | Sa-Token |
|---|---|---|
| 要求已登录 | SecurityFilterChain 里 `.anyRequest().authenticated()` 兜底 | 类上标 `@SaCheckLogin` |
| 要求权限点 | `@PreAuthorize("hasAuthority('user:query')")` | `@SaCheckPermission("user:query")` |
| 要求角色 | `@PreAuthorize("hasRole('admin')")` | `@SaCheckRole("admin")` |
| 公开接口 | `.requestMatchers("/auth/login").permitAll()` | `@SaIgnore` |

两套各有一个静默失效点，都不报错：

- **Spring Security**：`@PreAuthorize` 依赖 `@EnableMethodSecurity`（Spring Security 6 起取代 `@EnableGlobalMethodSecurity`），没开启时注解被完全忽略，方法级校验全部放行。另外 `hasRole('admin')` 实际匹配的权限串是 `ROLE_admin`，权限数据里没这个前缀就永远判 false——一个失效方向是放行，一个是全拒，都不会有异常提示你。
- **Sa-Token**：默认放行，只有被注解或拦截器覆盖到的方法才校验。所以 `@SaCheckLogin` 要标在类上，让后加的方法自动继承。

公开接口必须**显式**登记（Spring Security 的 `permitAll()`、Sa-Token 的 `@SaIgnore`），而不是靠「这儿没加校验」隐式放行——显式标注让审查者一眼看出这是有意为之，而不是漏了。

**错误（判断散落在方法体里，默认放行）：**

```java
@GetMapping
public RPage<UserListItemResponse> page(@Valid UserPageQuery query) {
    if (!StpUtil.hasPermission("user:query")) {   // 全靠人记得写；下一个方法忘了就是裸奔
        throw new BizException(ErrorCode.FORBIDDEN);
    }
    return RPage.ok(userService.listUsers(query));
}
```

**正确（Spring Security）：**

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity   // 缺这行，下面的 @PreAuthorize 全部静默失效
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
                // 纯 Bearer 令牌、无 Cookie 会话时 CSRF 保护无意义；若把令牌放进 Cookie，必须保留
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/auth/login").permitAll()   // 公开接口显式登记
                        .anyRequest().authenticated())                // 兜底默认拒绝
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

**正确（Sa-Token）：**

```java
@Tag(name = "用户")
@SaCheckLogin   // 标在类上，新增方法自动继承
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
