---
title: 鉴权框架按项目规模选型
impact: MEDIUM
impactDescription: 选错要么被概念成本拖慢交付，要么在接标准协议时补一年轮子
tags: stack, auth, security, spring-security, sa-token
---

## 鉴权框架按项目规模选型

Spring Security 与 Sa-Token 二选一，**一个项目只用一套**。

| 项目类型 | 选型 | 判断依据 |
|---|---|---|
| 基础设施平台、对外认证中心、多服务的中大型系统 | Spring Security | 要接 OAuth2 / OIDC / JWT 资源服务器，要过安全合规审计，生命周期以年计 |
| 后台业务系统、内部管理端、单体或少量服务的中小项目 | Sa-Token | 自有登录体系 + RBAC 权限点，要的是踢人下线、账号封禁、同端互斥登录这类现成能力 |

拿不准时看两个问题：**认证协议要不要对外标准化**（要 → Spring Security）、**登录态管理的花样是不是比协议更多**（是 → Sa-Token）。

为什么这么分：

- Spring Security 与 Spring Cloud Gateway、Spring Authorization Server、OAuth2 Resource Server 同源，令牌的签发、透传、校验都有官方实现，CSRF、会话固定、安全响应头、密码编码器默认成体系，CVE 响应也由 Spring 团队兜。代价是概念密度高——Filter Chain、AuthenticationManager、AuthorizationManager、SecurityContext 得先理顺，做个登录也要写一坨配置。中大型项目摊得起这份前期成本，而且合规审计和长期维护本来就需要它。
- Sa-Token 把后台系统的高频需求做成了开箱 API：登录鉴权、踢人下线、账号封禁、同端互斥登录、二级认证、临时令牌，这些用 Spring Security 都得自己实现。代价是标准协议与生态整合弱，一旦要对外当认证中心就得补轮子。中小项目大多走不到那一步，先把业务跑起来更重要。

不要混用。两套都挂在过滤器链上时，放行与拒绝的判定顺序没人说得清，权限出事故时也难复盘——这种「两套都在但都不完整」的状态比任何一套单独用都危险。

已有项目不因这条规则迁移：换鉴权框架要动登录态、令牌格式和全部权限注解，风险远大于收益。这条约束的是新项目和新拆出的服务。

具体注解写法见 `layer-controller-auth-annotations`。
