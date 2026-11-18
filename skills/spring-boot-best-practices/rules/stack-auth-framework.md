---
title: Choose the auth framework by project scale and scope
impact: MEDIUM
impactDescription: Picking the wrong framework either slows delivery under conceptual overhead or forces a year of custom protocol plumbing
tags: stack, auth, security, spring-security, sa-token
---

## Choose the auth framework by project scale and scope

Pick Spring Security or Sa-Token — **one auth framework per project**.

| Project profile | Choice | Decision criteria |
|---|---|---|
| Infra platforms, external IdPs, multi-service medium/large systems | Spring Security | Standard OAuth2 / OIDC / JWT resource servers, security compliance audits, multi-year lifecycle |
| Admin consoles, internal back-office apps, monoliths or small clusters | Sa-Token | Custom login + RBAC needing turnkey kick-out, account ban, mutex login, or step-up auth |

Two tie-breaker questions: **Must auth speak external standard protocols?** (Yes → Spring Security.) **Do session-management features outweigh protocol standards?** (Yes → Sa-Token.)

Why:

- **Spring Security** integrates natively with Spring Cloud Gateway, Spring Authorization Server, and OAuth2 Resource Server — token issuance, propagation, validation, CSRF, session fixation, security headers, password encoders, and CVE patches are maintained by Spring team. Trade-off: high conceptual overhead (`SecurityFilterChain`, `AuthenticationManager`, `AuthorizationManager`, `SecurityContext`), which medium/large platforms amortize easily.
- **Sa-Token** ships back-office session controls as one-line APIs (login checks, forced kick-out, account ban, single-device mutex login, step-up auth, temporary tokens) that require custom plumbing on Spring Security. Trade-off: weak standard-protocol integration once acting as federated identity provider.

Never mount both in one app: overlapping filter chains obscure allow/deny order and turn permission incidents into guesswork.

Apply to new projects and newly extracted services only — never migrate existing services solely for this rule.

See `layer-controller-auth-annotations` for annotation usage.
