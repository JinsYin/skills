---
title: Inject Flyway locations at build time and package all inactive overlays
impact: HIGH
impactDescription: Excluding inactive overlays prevents runtime topology overrides, forcing a rebuild per environment
tags: db, migration, flyway, build, deploy
---

## Inject Flyway locations at build time and package all inactive overlays

Inject `spring.flyway.locations` from Maven build profile placeholder instead of hardcoding in `application.yml`:

```xml
<!-- Parent POM: one profile per deployment target, each injecting its own locations -->
<profiles>
  <profile><id>distributed-gaussdb</id>
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-distributed</spring.flyway.locations></properties>
  </profile>
  <profile><id>centralized-gaussdb</id>
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-centralized</spring.flyway.locations></properties>
  </profile>
  <profile><id>opengauss</id>
    <properties><spring.flyway.locations>classpath:db/migration/gauss-base,classpath:db/migration/gauss-opengauss</spring.flyway.locations></properties>
  </profile>
</profiles>
```

```yaml
# application.yml
spring:
  flyway:
    locations: "@spring.flyway.locations@"
```

**Profile selects *active* locations, not *packaged* files.** Keep all overlay directories under `src/main/resources` so every overlay ships inside JAR classpath regardless of build profile — prerequisite for runtime overrides.

Name profiles after exact deployment targets (`distributed-gaussdb`, `centralized-gaussdb`) rather than generic `gaussdb` so profile IDs match location directories 1-to-1.

**Wrong (excluding inactive overlays from JAR):**

```xml
<!-- ❌ Packages only the build-time active overlay -->
<resources><resource>
  <directory>src/main/resources</directory>
  <excludes><exclude>db/migration/gauss-centralized/**</exclude></excludes>
</resource></resources>
```

Stripping overlays breaks runtime topology switching, forcing a separate untested build per environment.

**Right (package all overlays; override via env var at deploy time):**

```bash
# Override active Flyway locations when an environment's topology differs from the build profile
SPRING_FLYWAY_LOCATIONS=classpath:db/migration/gauss-base,classpath:db/migration/gauss-centralized
```

Example: staging runs centralized primary-standby while prod runs distributed cluster on identical image; `SPRING_FLYWAY_LOCATIONS` switches staging in deployment manifest.
