---
title: Pick openGauss / GaussDB drivers from the verified allowlist
impact: CRITICAL
impactDescription: Empty or colliding driver JARs compile cleanly, then fail on first connection
tags: db, driver, jdbc, r2dbc, opengauss, gaussdb, maven
---

## Pick openGauss / GaussDB drivers from the verified allowlist

Huawei publishes look-alike Gauss driver coordinates; some versions are empty JARs, one lives only in a third-party repository. Take coordinates from this allowlist and pin the version matching server `select version()` — wrong picks compile cleanly and fail only on first connection, often in target environment.

| Target | API | Coordinate (verified version) | Driver class / provider | URL prefix | MyBatis-Plus `DbType` |
|---|---|---|---|---|---|
| GaussDB distributed or centralized | JDBC | `com.huaweicloud:gaussdbjdbc` (`v2.0-8.218.0`) **or** `com.huaweicloud.gaussdb:gaussdbjdbc` (`506.0.0.b058`) | `com.huawei.gaussdb.jdbc.Driver` | `jdbc:gaussdb://` | `GAUSS` |
| openGauss | JDBC | `org.opengauss:opengauss-jdbc` with `-og` suffix (`5.0.3-og`) | `org.opengauss.Driver` | `jdbc:opengauss://` | `OPENGAUSS` |
| GaussDB or openGauss | R2DBC | `com.huaweicloud.gaussdb:gaussdb-r2dbc` (`1.0.0`) | provider `gaussdb` | `r2dbc:gaussdb://` | — |

- **GaussDB JDBC**: both lines ship classes under `com.huawei.gaussdb.jdbc`. Pick one by server version; one line per classpath, else first-loaded duplicate class wins.
- **openGauss JDBC**: new projects use `-og` suffix matching server version. Unsuffixed variant (`5.0.3`) registers `org.postgresql.Driver`, accepts only `jdbc:postgresql://`, and collides with `org.postgresql:postgresql` — keep only in existing projects, with pgjdbc excluded.
- **R2DBC**: Spring cannot resolve bind markers for driver name `GaussDB` (`NoBindMarkersFactoryException`); declare `DatabaseClient` with `BindMarkersFactory.indexed("$", 1)`. Spring Data R2DBC also needs `com.huaweicloud.gaussdb:gaussdb-spring-data-r2dbc` matching Spring Data minor. Multi-CN clusters use `r2dbc:gaussdb:failover://host1:8000,host2:8000`.

**Denylist:**

| Coordinate | Failure |
|---|---|
| `com.huaweicloud:gaussdbjdbc:V2.0-8.218.0` (uppercase `V`), `:505.2.1.SPC0800` | Empty JARs, zero classes → `ClassNotFoundException: com.huawei.gaussdb.jdbc.Driver` |
| `com.huawei.gaussdb:gaussdb-jdbc` | Hosted only in third-party Rokid repository, absent from Maven Central |
| `com.huaweicloud.gaussdb:gaussdb-r2dbc:1.0.0.RC1` | Pre-release still cited by Huawei ecosystem guides; use `1.0.0` |
| `org.postgresql:r2dbc-postgresql` on Gauss targets | Gauss SHA256 auth fails handshake: `Argument 'serverMechanisms' is not valid` |

macOS / Windows filesystems are case-insensitive: `v2.0-8.218.0` and `V2.0-8.218.0` share one `~/.m2` directory, and whichever downloads first serves both. Driver class suddenly missing → delete `~/.m2/repository/com/huaweicloud/gaussdbjdbc/` and re-resolve.

**Wrong (empty JAR plus second driver line):**

```xml
<dependency>
    <groupId>com.huaweicloud</groupId>
    <artifactId>gaussdbjdbc</artifactId>
    <version>505.2.1.SPC0800</version> <!-- ❌ empty JAR, no Driver class -->
</dependency>
<dependency>
    <groupId>com.huaweicloud.gaussdb</groupId>
    <artifactId>gaussdbjdbc</artifactId>
    <version>506.0.0.b058</version> <!-- ❌ second line, same packages -->
</dependency>
```

**Right (one line, version matches server):**

```xml
<dependency>
    <groupId>com.huaweicloud</groupId>
    <artifactId>gaussdbjdbc</artifactId>
    <version>v2.0-8.218.0</version> <!-- lowercase v; matches Huawei Cloud GaussDB v2.0-8.218.0 instance -->
</dependency>
```

Before adopting any new driver version, confirm JAR registers a driver (`unzip -p <jar> META-INF/services/java.sql.Driver`), then connect through application `DataSource` / `ConnectionFactory` on every target DB.

**Sources:** [GaussDB drivers][] · [GaussDB R2DBC][] · [GaussDB ecosystem][]

<!-- Huawei sample repositories -->
[GaussDB drivers]: https://github.com/huaweicloud-samples/database-gaussdb-drivers
[GaussDB R2DBC]: https://github.com/huaweicloud-samples/database-gaussdb-r2dbc
[GaussDB ecosystem]: https://github.com/huaweicloud-samples/database-gaussdb-ecosystem
