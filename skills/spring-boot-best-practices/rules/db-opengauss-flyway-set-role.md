---
title: gauss 系跑 Flyway 须注册插件跳过 SET ROLE
impact: CRITICAL
impactDescription: 非 sysadmin 账号下任何迁移都跑不到，启动即失败
tags: db, migration, flyway, opengauss, gaussdb
---

## gauss 系跑 Flyway 须注册插件跳过 SET ROLE

Flyway 把 openGauss / GaussDB 当 PostgreSQL，每次操作后执行 `SET ROLE '<CURRENT_USER>'` 还原角色。gauss 系拒绝非 sysadmin 执行 `SET ROLE`，即使切回自己也要 `PASSWORD`，报 SQLState 42602 `set role denied`。Flyway 随即以 `Unable to restore connection to its original state` 中止，这一步发生在查历史表时，任何迁移都跑不到。给账号 sysadmin 权限不是解法。应当用 Flyway Plugin SPI 换掉连接实现，只把还原步骤置空。

**错误（沿用内置 PostgreSQL 类型，或在迁移脚本里切角色）：**

```sql
SET ROLE app_owner PASSWORD '...'; -- ❌ 连接还回池时仍是这个角色，会污染后续请求
```

**正确（三个类，依赖 `flyway-database-postgresql`，compile scope）：**

```java
// 1. DatabaseType：优先级高于内置 PostgreSQL（0），按产品名接管，否则回落父类
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
// 2. Database：只替换连接实现
public class GaussDBDatabase extends PostgreSQLDatabase {
    // 构造器透传三个参数
    @Override protected PostgreSQLConnection doGetConnection(Connection c) { return new GaussDBConnection(this, c); }
}
// 3. Connection：置空角色还原
public class GaussDBConnection extends PostgreSQLConnection {
    @Override protected void doRestoreOriginalState() { /* gauss 系拒绝 SET ROLE；无角色可还原 */ }
}
```

```text
# META-INF/services/org.flywaydb.core.extensibility.Plugin
com.example.config.GaussDBDatabaseType
```

要点：

- **只能按产品名识别，不能靠 URL。** Spring 交给 Flyway 的是 DataSource，用不到 URL 识别。openGauss 官方驱动 `getDatabaseProductName()` 返回 `PostgreSQL`，所以实际是靠「优先级 100 + 回落父类」命中的。副作用是普通 PostgreSQL 也会被这个类型接管，只支持 MySQL + gauss 系的项目可以接受。
- **置空是安全的。** 父类的这个方法只做 `SET ROLE` 一件事，而 Flyway 自身不切换角色。schema、search_path、autocommit 由 `close()` 还原，与这里无关。前提是迁移脚本里禁写 `SET ROLE`。
- **放在执行迁移的那个模块。** 通过 Starter 或库对外提供迁移时，插件也要跟着下沉，否则只有带插件的应用能在 gauss 系上迁移。
- 插件依赖 `org.flywaydb.core.internal.*`，这些是内部 API，没有兼容承诺。代码里要标注：升级 Flyway 必须重跑 openGauss 的迁移 IT。
