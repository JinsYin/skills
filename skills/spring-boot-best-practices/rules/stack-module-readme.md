---
title: Maintain a README at the repository root and in every module
impact: MEDIUM
impactDescription: Module boundaries live only in tribal knowledge, forcing newcomers to guess from package trees
tags: stack, structure, docs, readme
---

## Maintain a README at the repository root and in every module

In multi-module builds, **maintain `README.md` at repo root and in every submodule**. Root README covers system purpose, capabilities, and module map; submodule README covers what that module owns, exposes, and depends on. **Single-module projects need only root README** with a package-layout section.

Without module READMEs, boundaries are reverse-engineered from `pom.xml` and package trees — mistaking current accidents for intended design until new code lands in wrong modules and erodes dependency direction.

Add `README.md` when creating a module, and update it in the **same commit** whenever public APIs, dependencies, or responsibilities change.

When citing internal Maven/Gradle coordinates in docs, reference parent dependency management or use `${project.version}` / version-catalog placeholders — never hardcode current project version.

**Wrong (code without boundary docs):**

```text
myapp/
├── README.md              ← only says "mvn spring-boot:run"
├── myapp-common/          ← no README; becomes a dumping ground for random helpers
├── myapp-user/            ← no README; unclear whether other modules may depend on it
└── myapp-gateway/         ← no README
```

**Right (self-explanatory at every level):**

```text
myapp/
├── README.md              ← capabilities + module map + getting started
├── myapp-common/
│   └── README.md          ← domain-agnostic utilities only; must never depend on domain modules
├── myapp-user/
│   └── README.md          ← user domain: registration, auth, orgs; expose via UserService only
└── myapp-gateway/
    └── README.md          ← routing, edge auth, rate limiting; zero domain logic
```

Root README minimum sections:

| Section | Content |
|---|---|
| Overview | 1–2 sentences: problem this system solves |
| Capabilities | Main externally visible features |
| Modules | Multi-module: module table with one-line responsibilities linked to module READMEs. Single-module: "Package layout" section |
| Stack | Version baseline for Java, Spring Boot, DB, middleware |
| Getting started | Prerequisites, build/start commands, default port |

Submodule README minimum sections (multi-module builds):

| Section | Content |
|---|---|
| Responsibility | What module owns — **and what explicitly does not belong here** |
| Public surface | Exposed endpoints, Services, extension points, and consumers |
| Dependencies | Internal modules and external middleware depended on, plus why |
| Local commands | Standalone build/run/test commands, where applicable |

`README.md` does not replace `CLAUDE.md`: `README.md` explains capabilities and boundaries to humans; `CLAUDE.md` states locked project decisions for agents. Never duplicate text across both.
