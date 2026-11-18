---
title: Scope DB drivers and Flyway to the modules that use them
impact: CRITICAL
impactDescription: Leaked Flyway or R2DBC artifacts crash unrelated modules at startup
tags: db, maven, flyway, r2dbc, opengauss, gaussdb
---

## Scope DB drivers and Flyway to the modules that use them

Declare each DB artifact only in modules opening that connection type; manage versions once in parent POM. Spring Boot auto-configures from classpath, so leaked artifacts crash modules that never use them:

- Flyway in non-migrating module + `spring.flyway.enabled=true` → startup fails with `Unsupported Database: GaussDB 9.2`.
- R2DBC driver in JDBC module → `R2dbcAutoConfiguration` activates and JDBC `DataSource` / `SqlSessionFactory` wiring fails.

| Artifact | Declare in |
|---|---|
| JDBC driver (see `db-gauss-driver-selection`) | Modules opening JDBC connections |
| `gaussdb-r2dbc` | Modules opening reactive connections only |
| `org.flywaydb:flyway-core` + `org.flywaydb:flyway-database-postgresql` | Module running migrations only, `compile` scope, beside Gauss plugin from `db-gauss-flyway-set-role` |
| Versions of all above | Parent `<properties>` / `<dependencyManagement>` |

Pin Flyway via Spring Boot BOM property `flyway.version` and leave `<version>` off both artifacts: one property moves both together. Versioning one artifact alone splits them across Flyway releases, and Gauss plugin built on internal APIs breaks.

**Maven profile traps:**

- Parent profile `<dependencies>` are inherited by every child; put there only artifacts every child needs.
- `activeByDefault` is deactivated only by another profile active in **same POM**. Child POM adding profile-specific dependencies must repeat every same-named profile from parent, or `-P mysql` still pulls default Gauss artifacts into that child.

**Wrong (parent profile leaks Flyway and R2DBC into every module):**

```xml
<!-- Parent POM -->
<profile>
    <id>distributed-gaussdb</id>
    <activation><activeByDefault>true</activeByDefault></activation>
    <dependencies>
        <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-database-postgresql</artifactId></dependency> <!-- ❌ -->
        <dependency><groupId>com.huaweicloud.gaussdb</groupId><artifactId>gaussdb-r2dbc</artifactId></dependency>   <!-- ❌ -->
    </dependencies>
</profile>
```

**Right (parent pins versions; migrator repeats every DB profile):**

```xml
<!-- Parent POM -->
<properties><flyway.version>10.20.1</flyway.version></properties>

<!-- Migrator module POM -->
<dependencies>
    <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-core</artifactId></dependency>
</dependencies>
<profiles>
    <profile>
        <id>distributed-gaussdb</id>
        <activation><activeByDefault>true</activeByDefault></activation>
        <dependencies>
            <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-database-postgresql</artifactId></dependency>
        </dependencies>
    </profile>
    <!-- centralized-gaussdb / opengauss: same dependency, same ids as parent -->
    <profile>
        <id>mysql</id>
        <dependencies>
            <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-mysql</artifactId></dependency>
        </dependencies>
    </profile>
</profiles>
```

`spring.flyway.enabled: false` in other modules masks leak only; fix is artifact absent from classpath.

Verify every DB profile after dependency changes: `./mvnw -P <profile> dependency:tree -pl <module>`. Non-migrating modules show no `org.flywaydb`; JDBC-only modules show no R2DBC driver or `io.r2dbc:r2dbc-spi`.
