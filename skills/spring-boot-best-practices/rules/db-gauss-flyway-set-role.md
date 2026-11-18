---
title: Register a Flyway plugin on Gauss-family DBs to skip SET ROLE
impact: CRITICAL
impactDescription: Every migration aborts at startup under non-sysadmin accounts
tags: db, migration, flyway, opengauss, gaussdb
---

## Register a Flyway plugin on Gauss-family DBs to skip SET ROLE

Flyway treats openGauss / GaussDB as PostgreSQL and runs `SET ROLE '<CURRENT_USER>'` after each step to restore state. Gauss-family DBs deny `SET ROLE` to non-`sysadmin` users (even back to self without `PASSWORD`, SQLState `42602` `set role denied`), aborting Flyway with `Unable to restore connection to its original state` while reading history table — before any migration runs. Never grant `sysadmin`; register a project-owned Flyway Plugin SPI that turns role restoration into a no-op.

**Wrong (role switching in SQL, or bypass workarounds):**

```sql
SET ROLE app_owner PASSWORD '...'; -- ❌ pooled connection retains this role and pollutes later requests
```

- `com.github.mengweijin:db-migration-gauss-flyway` shadows `PostgreSQLConnection` and silently loses to `flyway-database-postgresql` on classpath order.
- `spring.flyway.validate-on-migrate: false` hides schema drift along with symptom (see `db-migration-immutable-after-apply`).

**Right (three classes; dependencies per `db-gauss-dependency-scope`):**

```java
// 1. DatabaseType: higher priority than built-in PostgreSQL (0); match product name or fall back to super
public class GaussDBDatabaseType extends PostgreSQLDatabaseType {
    @Override public String getName() { return "GaussDB"; }
    @Override public int getPriority() { return 100; }
    @Override public boolean handlesDatabaseProductNameAndVersion(String name, String ver, Connection c) {
        String n = name == null ? "" : name.toLowerCase(Locale.ROOT);
        return n.contains("gaussdb") || n.contains("opengauss") || super.handlesDatabaseProductNameAndVersion(name, ver, c);
    }
    // URL hooks: only for direct-URL runs (Flyway Maven plugin / CLI)
    @Override public boolean handlesJDBCUrl(String url) {
        return url.startsWith("jdbc:gaussdb:") || url.startsWith("jdbc:opengauss:") || super.handlesJDBCUrl(url);
    }
    @Override public String getDriverClass(String url, ClassLoader cl) {
        if (url.startsWith("jdbc:gaussdb:")) return "com.huawei.gaussdb.jdbc.Driver";
        if (url.startsWith("jdbc:opengauss:")) return "org.opengauss.Driver";
        return super.getDriverClass(url, cl);
    }
    @Override public Database createDatabase(Configuration cfg, JdbcConnectionFactory f, StatementInterceptor si) {
        return new GaussDBDatabase(cfg, f, si);
    }
}
// 2. Database: swap only the Connection wrapper
public class GaussDBDatabase extends PostgreSQLDatabase {
    // Constructor forwards all three arguments to super
    @Override protected PostgreSQLConnection doGetConnection(Connection c) { return new GaussDBConnection(this, c); }
}
// 3. Connection: make role restoration a no-op
public class GaussDBConnection extends PostgreSQLConnection {
    @Override protected void doRestoreOriginalState() { /* Gauss-family DBs reject SET ROLE; no role to restore */ }
}
```

```text
# META-INF/services/org.flywaydb.core.extensibility.Plugin
com.example.config.GaussDBDatabaseType
```

Key constraints:

- **Match product name first.** Spring passes Flyway a `DataSource`, so detection reads `getDatabaseProductName()`: GaussDB driver reports `GaussDB` (`PostgreSQL` if `driverInfoMode` changed); both openGauss driver variants always report `PostgreSQL`. `priority = 100` + `super` fallback covers both — and also claims plain PostgreSQL, so keep plugin off pure-PostgreSQL deployments.
- **No-op restore is safe** provided migrations never run `SET ROLE`: superclass method only runs `SET ROLE`, while `schema`, `search_path`, and `autocommit` reset on `close()`.
- **Ship plugin in module that runs migrations.** Shared starters/libraries shipping migrations must bundle SPI registration too.
- **No Gauss connector on Maven Central** (checked 2026-11); adopt third-party connectors (e.g. `flyway-database-opengauss`) only after verifying they resolve and pass migrations on the pinned Flyway version.
- Plugin imports internal `org.flywaydb.core.internal.*` APIs: comment in code that Flyway upgrades require re-running Gauss migration ITs on every DB profile.
