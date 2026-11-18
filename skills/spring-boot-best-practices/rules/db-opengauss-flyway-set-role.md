---
title: Register a Flyway plugin on Gauss-family DBs to skip SET ROLE
impact: CRITICAL
impactDescription: Every migration aborts at startup under non-sysadmin accounts
tags: db, migration, flyway, opengauss, gaussdb
---

## Register a Flyway plugin on Gauss-family DBs to skip SET ROLE

Flyway treats openGauss / GaussDB as PostgreSQL and runs `SET ROLE '<CURRENT_USER>'` after each step to restore state. Gauss-family DBs deny `SET ROLE` to non-`sysadmin` users (even back to self without `PASSWORD`, SQLState `42602` `set role denied`), aborting Flyway with `Unable to restore connection to its original state` while reading history table — before any migration runs. Never grant `sysadmin`; register a Flyway Plugin SPI that turns role restoration into a no-op.

**Wrong (relying on built-in PostgreSQL support or switching roles in SQL):**

```sql
SET ROLE app_owner PASSWORD '...'; -- ❌ pooled connection retains this role and pollutes later requests
```

**Right (three classes with `flyway-database-postgresql` in `compile` scope):**

```java
// 1. DatabaseType: higher priority than built-in PostgreSQL (0); match product name or fall back to super
public class GaussDBDatabaseType extends PostgreSQLDatabaseType {
    @Override public String getName() { return "GaussDB"; }
    @Override public int getPriority() { return 100; }
    @Override public boolean handlesDatabaseProductNameAndVersion(String name, String ver, Connection c) {
        String n = name == null ? "" : name.toLowerCase(Locale.ROOT);
        return n.contains("gaussdb") || n.contains("opengauss") || super.handlesDatabaseProductNameAndVersion(name, ver, c);
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

- **Match product name, never JDBC URL.** Spring passes Flyway a `DataSource` without URL matching. Official openGauss driver returns `PostgreSQL` from `getDatabaseProductName()`, so matching relies on `priority = 100` + `super.handlesDatabaseProductNameAndVersion(...)` (plain PostgreSQL also hits this type, acceptable in MySQL + Gauss projects).
- **No-op restore is safe** provided migrations never run `SET ROLE`: superclass method only runs `SET ROLE`, while `schema`, `search_path`, and `autocommit` reset on `close()`.
- **Ship plugin in module that runs migrations.** Shared starters/libraries shipping migrations must bundle SPI registration too.
- Plugin imports internal `org.flywaydb.core.internal.*` APIs: comment in code that Flyway upgrades require re-running openGauss migration ITs.
