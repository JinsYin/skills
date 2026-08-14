# Spring Boot Best Practices

> 本文件由 `scripts/build.sh` 从 `rules/` 自动生成，请勿手工编辑。
> 生成时间：2026-08-14 01:36:22

## 1. 分层纪律


### 权限校验用注解，不写在方法体里

鉴权用 Sa-Token 注解声明，不在方法体里手写 if 判断。声明式的好处是**默认拒绝**：类上标了 `@SaCheckLogin`，新加的方法自动继承；手写判断则是默认放行，新方法忘了写就是裸奔，而且这种遗漏在测试里通常发现不了。

| 注解 | 用途 |
|---|---|
| `@SaCheckLogin` | 要求已登录，通常标在类上 |
| `@SaCheckPermission("user:query")` | 要求具体权限点 |
| `@SaCheckRole("admin")` | 要求角色 |
| `@SaIgnore` | 显式放行公开接口 |

公开接口必须用 `@SaIgnore` **显式**标注，而不是靠「类上没加校验」隐式放行——显式标注让审查者一眼看出这是有意为之。

**正确：**

```java
@Tag(name = "用户")
@SaCheckLogin
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


### Controller 不得返回 Entity

Entity 映射数据库全字段，含密码散列、软删标记、内部审计列等。直接返回等于把这些字段暴露给调用方，且今后给表加一列就会静默扩大接口输出。

**错误（把整行数据抛给前端）：**

```java
@GetMapping("/users/{id}")
public R<UserEntity> get(@PathVariable Long id) {
    return R.ok(userService.getEntityById(id)); // ❌ 含 password / deleted
}
```

**正确（用视图专属 Response，字段显式列举）：**

```java
@GetMapping("/users/{id}")
public R<UserDetailResponse> get(@PathVariable Long id) {
    return R.ok(userService.getById(id));
}
```

Service 的返回类型也必须是 `Response` / `Dto` / 原始类型，**不能**是 Entity——否则 Controller 只是把泄漏点上移一层。


### 跨领域调 Service，不调对方 Mapper

一个 Service 可以注入另一个 Service，但**不能**注入另一个领域的 Mapper。绕过对方 Service 等于绕过它的业务校验、缓存失效和事务约定，这类 bug 只在对方逻辑变更时才暴露。

**错误：**

```java
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;
    private final RoleMapper roleMapper; // ❌ 越过 RoleService
}
```

**正确：**

```java
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;   // 自己领域的 Mapper
    private final RoleService roleService; // 别人领域走 Service
}
```


### 不用 Map 当响应类型

`Map<String, Object>` 没有编译期约束，也生成不出 OpenAPI schema，调用方只能靠猜或翻源码。改字段时无任何提示。

**错误：**

```java
@GetMapping("/stats")
public R<Map<String, Object>> stats() {
    Map<String, Object> m = new HashMap<>();
    m.put("total", 100);
    m.put("active", 80);
    return R.ok(m); // ❌ 契约不可见
}
```

**正确：**

```java
@Data
@Schema(description = "统计响应")
public class StatsResponse {
    @Schema(description = "总数") private Long total;
    @Schema(description = "活跃数") private Long active;
}
```

仅当 schema 真正动态（如用户自定义表单）时才例外，且仍应包一层带类型的信封。


### 禁止静默吞异常

`catch` 后不处理也不重抛，会把失败伪装成成功：调用方收到 200 和空数据，故障延后到下游才暴露，且现场已丢失。

**错误：**

```java
try {
    userMapper.insert(entity);
} catch (Exception e) {
    // ❌ 什么都不做，调用方以为成功
}
```

**正确（要么转成有业务含义的错误，要么交给全局处理器）：**

```java
try {
    externalClient.sync(entity);
} catch (RestClientException e) {
    log.warn("上游同步失败, entityId={}", entity.getId(), e);
    throw new BizException(ErrorCode.UPSTREAM_UNAVAILABLE);
}
```

只有明确「失败可忽略」的旁路逻辑（如埋点上报）才允许吞，且必须留日志并注释原因。


### 分层单向依赖

`Controller → Service → Mapper`，每层只依赖紧邻的下一层。反向或跨层调用会同时破坏事务边界、可测性与复用性。

| 层 | 职责 | 禁止 |
|---|---|---|
| Controller | HTTP 契约：路径、参数、校验、鉴权 | 访问 Mapper、调用其他 Controller |
| Service | 业务逻辑、事务、编排、外部调用、缓存 | 处理视图关注点、直接调别的 Service 的 Mapper |
| Mapper | 数据库访问、ORM 映射 | 业务逻辑、校验、事务 |

**错误（Controller 直连 Mapper，绕过事务与业务校验）：**

```java
@RestController
@RequiredArgsConstructor
public class UserController {
    private final UserMapper userMapper; // ❌ 跨层
    @GetMapping("/users/{id}")
    public R<UserEntity> get(@PathVariable Long id) {
        return R.ok(userMapper.selectById(id));
    }
}
```

**正确：**

```java
@RestController
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;
    @GetMapping("/users/{id}")
    public R<UserDetailResponse> get(@PathVariable Long id) {
        return R.ok(userService.getById(id));
    }
}
```


### Service 不碰 HTTP

Service 里出现 `HttpServletRequest`、`request.getParameter()`、手工构造响应头或状态码，会让业务逻辑绑死在 Web 容器上——单测必须起 MockMvc，定时任务和 MQ 消费者也没法复用同一段逻辑。

**错误：**

```java
public boolean create(HttpServletRequest request) { // ❌
    String name = request.getParameter("name");
}
```

**正确（Controller 完成解析与鉴权，Service 只收类型化入参）：**

```java
public boolean create(UserCreateRequest request, Long operatorId) {
    // 纯业务逻辑，可被 Controller / 定时任务 / MQ 消费者共用
}
```

当前登录人这类上下文由 Controller 取出后作为参数传入，或经由显式的上下文持有者，不要让 Service 直接读 HTTP。

## 2. 密码学


### 只用批准的国密算法与模式

| 用途 | 必须 | 禁止 |
|---|---|---|
| 非对称加密 | SM2 `C1C3C2` | `C1C2C3`（仅隔离的兼容层可留） |
| 签名 | SM2 + SM3 摘要 | — |
| 摘要 | SM3 | MD5、SHA1 |
| 对称加密 | `SM4/GCM/NoPadding` | **任何 `SM4/ECB/*`** |
| 兼容场景 | `SM4/CBC/PKCS5Padding` | DES、3DES、RC4 |

ECB 对相同明文块产生相同密文块，结构直接从密文可见——这不是强度问题，是模式本身不提供语义安全。

同样禁止自己实现密码学原语。需要什么就用 Bouncy Castle 已有的实现。


### 密钥不入代码，按用途分离

私钥、对称密钥、IV、nonce、盐、生产 secret 一律不得硬编码。进了 git history 就等于永久泄漏——即使后续删除文件，历史提交里仍在。

- 加密、签名、MAC/完整性**各用独立密钥**，一把钥匙多用会让一处泄漏波及全部安全属性
- SM2 密钥用 PEM/DER，SM4 用 16 字节二进制
- 密文生命周期可能长于密钥轮换周期时，随载荷携带 `keyId`
- 二进制传输默认 Base64，除非对端协议要求 hex

没有 `keyId` 的历史密文在轮换后将无法解密，而这通常在轮换当天才被发现。


### 密钥与明文不进日志

**禁止**记录明文、私钥、对称密钥、完整密文、完整签名、解密后载荷。日志往往被集中采集、长期留存，且访问权限比数据库宽得多——写进日志等于扩大了泄漏面。

解密失败、认证标签不匹配、密文格式非法、验签失败一律按**安全错误**处理：返回稳定的业务错误码，不要把密码学细节透给调用方（那等于给攻击者提供预言机）。

**错误：**

```java
log.error("解密失败, ciphertext={}, key={}", cipherText, keyHex, e); // ❌
```

**正确：**

```java
log.warn("解密失败, keyId={}, len={}", keyId, cipherText.length);
throw new BizException(ErrorCode.DECRYPT_FAILED);
```

测试需覆盖：SM2 `C1C3C2` 加解密往返、签名验证的成功与失败、SM3 已知答案摘要、SM4 nonce 唯一性与篡改检测。


### BouncyCastle Provider 注册一次

优先用 `org.bouncycastle:bcprov-jdk18on`，在应用启动时注册一次，不要在每次加解密时重复注册——`addProvider` 有同步开销，热路径上反复调用会成为瓶颈。

**正确：**

```java
@Configuration
public class CryptoConfig {
    @PostConstruct
    public void registerProvider() {
        if (Security.getProvider(BouncyCastleProvider.PROVIDER_NAME) == null) {
            Security.addProvider(new BouncyCastleProvider());
        }
    }
}
```

模块若已使用其他合规 provider，沿用即可，不要混装两个。


### 只对规范字节签名与摘要

签名和摘要的输入必须是**确定性字节序列**。对 `Map.toString()`、对象 `toString()` 或字段顺序不固定的 JSON 签名，会产生同一份数据在不同 JVM、不同版本下签出不同结果——表现为验签随机失败，且极难复现。

**错误：**

```java
byte[] data = payload.toString().getBytes(); // ❌ 顺序不保证
byte[] sig = signSm2Sm3(privateKey, data);
```

**正确（固定字段顺序的规范化序列化）：**

```java
byte[] canonical = canonicalize(payload); // 字段排序 + 固定编码 + UTF-8
byte[] sig = signSm2Sm3(privateKey, canonical);
```

对外来数据，**先验签再信任**。SM2 解密前先校验 `C1`、`C3`、`C2` 三段结构；`C1` 需含未压缩点前缀 `0x04`，除非对端协议明确不带。

摘要比较用常量时间比较，不要用 `Arrays.equals` 之外的短路比较暴露时序信息。


### IV / nonce 每次随机且唯一

- SM4 密钥必须恰好 128 位 / 16 字节
- GCM nonce 96 位 / 12 字节，**每次加密唯一**
- CBC IV 16 字节，每次用 `SecureRandom` 生成

GCM 下重用 nonce 不只是削弱强度——它让攻击者能恢复认证密钥，从而伪造任意密文的标签，加密保护完全失效。

**错误：**

```java
private static final byte[] IV = "1234567890123456".getBytes(); // ❌ 固定
```

**正确：**

```java
byte[] nonce = new byte[12];
SecureRandom.getInstanceStrong().nextBytes(nonce); // 每次新生成，随密文一起传输
```

也不要靠截断字符串派生密钥——那会把密钥空间压缩到口令的熵，而非 128 位。

## 3. 实体与持久化


### 审计时间字段用 @TableField(fill)

不能依赖数据库的 `ON UPDATE CURRENT_TIMESTAMP`——该语法是 MySQL 特有的，迁移到 gauss 系时会被移除，字段随即变成 NULL 或永不更新。填充必须由应用层的 `MetaObjectHandler` 驱动。

**错误（指望数据库自动维护）：**

```java
private LocalDateTime createdAt; // ❌ 无 fill，靠 DDL 默认值
private LocalDateTime updatedAt;
```

**正确：**

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createdAt;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updatedAt;
```

规则固定：含 `createdAt` 必标 `INSERT`，含 `updatedAt` 必标 `INSERT_UPDATE`。


### Mapper 不写 XML 和整句 SQL

Mapper 继承 `MPJBaseMapper<Entity>`，查询优先用 MyBatis-Plus wrapper 与 MPJ API（`selectJoinPage`、`leftJoin`、`selectAs`）。手写整句 SQL 会绑死方言，在多数据库目标下必然分叉。

**错误：**

```java
@Mapper
public interface UserMapper extends MPJBaseMapper<UserEntity> {
    @Select("SELECT * FROM t_user WHERE status = #{status} LIMIT 10") // ❌ 方言绑定
    List<UserEntity> listByStatus(String status);
}
```

**正确：**

```java
@Mapper
public interface UserMapper extends MPJBaseMapper<UserEntity> {
}

// Service 内用 wrapper
LambdaQueryWrapper<UserEntity> w = Wrappers.lambdaQuery(UserEntity.class)
        .eq(UserEntity::getStatus, status)
        .last("LIMIT 10");
```

复杂投影/聚合确实无法用 wrapper 表达时，允许在 wrapper 内嵌小段 SQL 片段，但必须参数化，并在旁边用注释写出等价 SQL 形状供审查者阅读。


### 主键用 ASSIGN_ID，禁用 AUTO

`IdType.AUTO` 依赖数据库端的自增列。当目标库不是 MySQL 时（openGauss 的 `BIGSERIAL` 语义与 `AUTO_INCREMENT` 并不等价），应用层不填 ID，INSERT 撞上 NOT NULL 直接失败——而报错信息指向字段约束，与真正的根因（主键策略）相距很远，排查代价很高。

用 `ASSIGN_ID` 由应用层雪花算法生成，与数据库无关。

**错误：**

```java
@TableId(type = IdType.AUTO) // ❌ 绑死数据库自增
private Long id;
```

**正确：**

```java
@TableId(type = IdType.ASSIGN_ID)
private Long id;
```

**例外**——主键直接复用业务 ID 时用 `INPUT`：

```java
@TableId(value = "app_id", type = IdType.INPUT)
private Long appId;
```

## 4. 数据库与迁移


### 列名与审计字段约定

- 列名 `snake_case`（`order_no`）
- 主键 `id`，`BIGINT` 或 `VARCHAR(32)`，与主键策略一致
- 外键列 `fk_{ref}_id`
- 布尔用语义名（`enabled`、`is_default`、`deleted`），类型 `TINYINT(1)`，`0=false / 1=true`
- 审计四件套：`created_at`、`updated_at`、`created_by`、`updated_by`
- 软删：`deleted TINYINT(1) NOT NULL DEFAULT 0`，`1` 为已删除

布尔列不要用 `flag`、`type` 这类无语义名——半年后没人知道 `flag=1` 是启用还是禁用。


### 分布式库的唯一约束必须含分布键，否则要全局索引

分布式数据库（GaussDB Distributed、TiDB、OceanBase 等）把数据按分布键散到各个分片。**普通唯一索引是分片本地的**——只保证同一分片内不重复。若唯一列不是分布键，两条同值记录落在不同分片时，本地索引各自看不到对方，重复数据照样写得进去。

这类故障最坏的形态是**静默**：不报错、不回滚，直到某天查出两条本该唯一的记录。

两种写法，按「表是不是本次新建」选：

**新建表——写成表内联约束，两种形态共通：**

```sql
CREATE TABLE t_authcode_agreement (
    auth_code   VARCHAR(64) NOT NULL,
    ...
    CONSTRAINT uk_authcode_agreement_auth_code UNIQUE (auth_code)
);
```

分布式下引擎自动建全局索引，单机下就是普通唯一约束——**一份 SQL 通吃**，无需在 overlay 里分叉（见 `db-migration-base-overlay`）。

**对既有表追加——必须显式全局唯一索引：**

```sql
-- ❌ 分布式下只在分片内唯一，跨分片可写入重复值
CREATE UNIQUE INDEX uk_org_name ON t_org(org_name);

-- ✅ 分布式：GSI，DISTRIBUTE BY 列与索引列一致
CREATE GLOBAL UNIQUE INDEX uk_org_name ON t_org(org_name) DISTRIBUTE BY HASH(org_name);
```

`CREATE GLOBAL UNIQUE INDEX` 语法在单机/集中式下不被认识，所以这一种情形——**且只有这一种**——需要分叉出集中式 overlay，改回普通 `CREATE UNIQUE INDEX`（无数据分布时它本身就是全表唯一）。

同理，`ALTER TABLE ... ADD UNIQUE` 在分布式下同样受「唯一键必须包含分布键」约束，不能当作绕过手段。


### 索引命名 uk_ / idx_

- 唯一索引：`uk_{table}_{field...}`
- 普通索引：`idx_{table}_{field...}`

带表名是为了让索引名全库唯一——某些数据库的索引名是 schema 级而非表级，重名会在建表时直接冲突。

```sql
CREATE UNIQUE INDEX uk_user_email ON t_user(email);
CREATE INDEX idx_order_created_at ON t_order(created_at);
```

新建表的唯一约束写成 `CREATE TABLE` 内联 `CONSTRAINT uk_x UNIQUE(...)`，而不是建表后再补索引——内联写法在分布式与单机部署下语义一致。


### 同库多形态用 base + overlay，不复制整套迁移

同一个数据库产品有多种部署形态（分布式集群 / 集中式主备 / 单机），而某些 DDL 只在其中一种形态下合法时，**不要为每种形态各维护一份完整迁移集**。N 份完整副本里绝大多数文件逐字相同，改一条要同步改 N 处——漏改不会在本地报错，只在另一形态的环境启动时炸。

拆成两层：

| 层 | 放什么 |
|---|---|
| `<db>-base` | **共通基线**：建表、种子、ALTER、注释——凡两种形态语法一致的，全部放这里 |
| `<db>-<形态>` overlay | **只放确实分叉的那几条**，每种形态一份，版本号与名称严格一致 |

**overlay 之间互斥**：激活的 location 恒为 `base + 恰好一个 overlay`，构建期与运行期都不得同时挂两个。因此同一版本号**只能出现在一个激活 location**——base 与 overlay 之间绝不能重复版本号，否则 Flyway 报重复版本直接启动失败。

分层要回答两个不同的问题，别混为一谈：

**问题一：这条迁移放 base 还是 overlay？** 判据是「有没有两端共通的写法」，不是「这条迁移涉不涉及分布式概念」：

- 有共通写法 → 留在 base。例：新建表的唯一约束写成表内联 `CONSTRAINT uk_x UNIQUE(...)`，分布式下自动建全局索引、单机下是普通约束，一份通吃。
- 确无共通写法 → 才分叉。例：对**既有**表追加非分布键唯一索引，分布式必须用 `CREATE GLOBAL UNIQUE INDEX ... DISTRIBUTE BY HASH(...)`，而单机不认这个语法。

**问题二：overlay 分几份？** 按**部署目标**分，一个目标一份——即便其中两份当下的可执行 SQL 完全相同。这与问题一的「能共通就别分」不矛盾：那条管的是 base 与 overlay 的边界，这条管的是 overlay 的粒度。

理由是 profile ↔ location 保持一一对应。两个目标共用一个 overlay 时，目录名会对其中一个说谎（`gauss-centralized` 实际同时服务集中式 GaussDB 和单机 openGauss），运维改 `SPRING_FLYWAY_LOCATIONS` 时得先在脑子里做一次映射，而这个映射没有任何地方能校验。代价是多一份等价副本——用 `diff` 核可执行 SQL 一致即可，比一次接错 location 便宜。

> 等价副本里**注释可以按产品归属分别写**（这往往正是拆分的直接动因），但改注释会改 Flyway checksum，见 `db-migration-immutable-after-apply`。

**错误（同一张新表在两个 overlay 里各写一遍）：**

```
gauss-distributed/V25__add_authcode_agreement.sql   -- 建表 60 行 + 唯一索引 3 行
gauss-centralized/V25__add_authcode_agreement.sql   -- 建表 60 行 + 唯一索引 2 行
```

60 行建表体重复两份。下次给这张表加字段，改一处漏一处。

**正确（能共通的下沉到 base）：**

```
gauss-base/V25__add_authcode_agreement.sql          -- 建表，唯一约束写表内联 CONSTRAINT
```

只有真的无法共通时才留在 overlay，且**各份 overlay 除分叉语句与产品归属注释外必须逐字一致**（建表体、ALTER、DROP 同步维护）。新增或修改 overlay 后逐对 `diff` 一遍是最省事的校验方式。

配套见 `db-migration-parity`（多方言同版本同步）、`db-migration-locations-injection`（location 怎么注入）、`db-distributed-unique-index`（分叉的根因）、`db-migration-immutable-after-apply`（改已执行的迁移要 repair）。


### 已执行的迁移不可编辑，改注释也算改

Flyway 对每个迁移文件存一份 checksum，算的是**整个文件内容**——注释、空行、缩进全在内。改一个已经执行过的版本，下次启动 validate 阶段就会报 checksum 失配并拒绝继续，而**只在已经跑过该版本的环境上报**：新环境从零 migrate 一路绿灯，老环境（通常是生产）起不来。

所以默认纪律是：**已执行的版本只读，要改就发新版本**。给列改类型、补索引、修数据，都写 `V<n+1>__fix_xxx.sql`。

例外只有一类：改动**不影响已执行结果**，纯粹是注释、格式、或产品归属标注（例如把一份 overlay 的注释从「集中式 GaussDB」改成「社区 openGauss」）。这时重发一个新版本毫无意义——它什么也不做。正确做法是接受 checksum 变化，然后让每个已执行过该版本的环境**先 repair 再 migrate**：

```bash
flyway repair   # 用当前文件内容重写 flyway_schema_history 里的 checksum
flyway migrate
```

Spring Boot 侧对应 `spring.flyway.repair-on-migrate`（或部署流程里先跑一次 repair 任务）。**这一步必须写进变更说明**——漏掉它的环境会在下一次滚动发布时才炸，那时已经和这次改动隔了很久。

**不要用关闭校验来绕过：**

```yaml
# ❌ 把真实的结构漂移一起关掉了
spring.flyway.validate-on-migrate: false
```

`validate-on-migrate: false` 不只放过你这次的注释改动，也放过「有人手工改过生产表结构」「某个版本文件被误删」这类真问题——而这些正是 validate 唯一能替你抓到的东西。若项目因历史原因已经关着它，那更要在变更说明里显式写清 repair 步骤：此时没有任何自动检查会提醒执行者。


### locations 构建期注入，未激活的 overlay 也要打进产物

Flyway 的 `spring.flyway.locations` 不要在配置文件里写死，用构建期 profile 注入占位符——哪套方言/形态由出包时决定，源码里保持单一写法。

```xml
<!-- 父 pom：一个部署目标一个 profile，各自注入自己的 locations -->
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

**关键一条：注入的是「激活哪些 location」，不是「打包哪些文件」。** 所有 overlay 目录都在 `src/main/resources` 下，无论当次构建激不激活，都会一并进 jar 的 classpath。这不是冗余，而是运行期覆盖的前提：

profile 名字带上部署目标（`distributed-` / `centralized-`），比笼统的 `gaussdb` 更难接错——它和 location 目录名一一对应，肉眼就能核。

**错误（按 profile 裁剪资源目录）：**

```xml
<!-- ❌ 只把激活的 overlay 打进包 -->
<resources><resource>
  <directory>src/main/resources</directory>
  <excludes><exclude>db/migration/gauss-centralized/**</exclude></excludes>
</resource></resources>
```

这样一来，同一个镜像换个形态的环境就跑不了，只能为该环境单独出一次包——而重新出包意味着上线的不是已经过测的那个产物。

**正确：全部打进去，部署时用环境变量覆盖。**

```bash
# 该环境形态与构建期 profile 不一致时，运行期改激活的 location 即可
SPRING_FLYWAY_LOCATIONS=classpath:db/migration/gauss-base,classpath:db/migration/gauss-centralized
```

典型场景：预发与生产用同一镜像，但预发是集中式主备、生产是分布式集群。构建期只能选一个 profile，差异靠部署清单里的这个 env 补齐。


### 迁移必须多方言同步同版本

项目同时支持多个数据库时，每条 migration 必须为**每个激活的 location 各维护一份**，版本号与名称严格一致。漏一份的后果是：开发环境全绿，目标环境启动时 Flyway 报缺失版本或表结构不一致——而这通常发生在生产。

关键约束：

- 同一版本号**只能出现在一个激活 location**，否则 Flyway 报重复版本
- 各份之间除方言差异外，内容必须逐字一致（建表体、ALTER、注释同步维护）
- 激活哪些 location 由构建期 profile 注入，不要在代码里硬编码

**改动清单**——加一条迁移时，逐个确认每个方言目录都有对应文件，再确认版本号无冲突。

同一数据库产品还有多种部署形态（分布式 / 集中式 / 单机）时，不要再按形态复制整套，见 `db-migration-base-overlay`。项目具体有几层 location、各层叫什么，以该项目 CLAUDE.md 为准。


### openGauss 方言三定律

写 gauss 系迁移时，以下 PostgreSQL 语法**不可用**，必须改写：

| 不支持 | 改写为 |
|---|---|
| `ON CONFLICT` | `INSERT ... WHERE NOT EXISTS`，或显式去重 |
| `sys_guid()` / `gen_random_uuid()` | `md5(...)::uuid` 合成 |
| `jsonb_build_object` | `'[...]'::jsonb` 字面量 |

**错误：**

```sql
INSERT INTO t_config(k, v) VALUES ('a', '1')
ON CONFLICT (k) DO UPDATE SET v = '1'; -- ❌ openGauss 不支持
```

**正确：**

```sql
INSERT INTO t_config(k, v)
SELECT 'a', '1'
WHERE NOT EXISTS (SELECT 1 FROM t_config WHERE k = 'a');
```

这三条是踩坑实证，不是理论限制——写之前先对照，比迁移失败后回查便宜得多。


### 表名 t_ 前缀 + snake_case + 单数

表名统一 `t_` 前缀、`snake_case`、**单数**：`t_order`、`t_user`、`t_order_item`。前缀把业务表与视图、中间表、框架表区分开；单数与实体类一一对应，避免 `t_users` ↔ `UserEntity` 这种单复数错位。

实体用 `@TableName` 显式映射，不依赖驼峰自动转换：

```java
@Data
@TableName("t_order_item")
public class OrderItemEntity { }
```

## 5. 响应包装与错误码


### 用 BizException 表达业务失败，不返回 null

用 `null` 表示「没找到」会把判空责任推给每个调用点，漏一处就是 NPE，而且丢失了失败原因。

**错误：**

```java
public UserDetailResponse getById(Long id) {
    UserEntity e = userMapper.selectById(id);
    return e == null ? null : converter.toResponse(e); // ❌
}
```

**正确：**

```java
public UserDetailResponse getById(Long id) {
    UserEntity e = userMapper.selectById(id);
    if (e == null) {
        throw new BizException(ErrorCode.USER_NOT_FOUND);
    }
    return converter.toResponse(e);
}
```

由 `GlobalExceptionHandler` 统一转成带码的 `R`。仅当「不存在」本身是正常分支（如可选配置查询）时才返回 `Optional`。


### 错误码 6 位，前 3 位是 HTTP 状态

错误码固定 6 位，前 3 位复用对应的 HTTP 状态码，后 3 位是该状态下的序号。这样调用方不查表也能判断错误大类，网关和日志也能按前缀聚合。

**错误：**

```java
AUTH_INVALID(1001, "AK 或 SK 校验失败"), // ❌ 看不出属于哪类
```

**正确：**

```java
@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    AUTH_INVALID(401001, 401, "AK 或 SK 校验失败"),
    AUTH_EXPIRED(401002, 401, "AK 已过期"),
    NOT_FOUND   (404001, 404, "资源不存在");

    private final int code;
    private final int httpStatus;
    private final String defaultMessage;
}
```

每个码自带默认中文 message，调用点不重复写文案。


### 信封只用工厂方法构造

`R` / `RList` / `RPage` 一律用静态工厂构造，不要 `new` 后逐字段赋值——手工赋值必然出现 code 取值不一致、message 漏填。

**错误：**

```java
R<UserResponse> r = new R<>(); // ❌
r.setCode(0);                  // 与工厂的 200 不一致
r.setData(user);
return r;
```

**正确：**

```java
return R.ok(user);                        // 成功带数据
return R.ok();                            // 成功无数据
return R.error(ErrorCode.DUPLICATE_NAME); // 带码错误
throw new BizException(ErrorCode.NOT_FOUND); // 交给全局处理器包装
```

Controller 直接返回 `R<T>`，不要套 `ResponseEntity<R<T>>`。仅文件下载与重定向需要自定 HTTP 状态时才用 `ResponseEntity<Resource>` 或 `void` + `HttpServletResponse`。


### 字段类型约定

| 用途 | 用 | 不用 |
|---|---|---|
| 日期时间 | `LocalDate` / `LocalDateTime` / `OffsetDateTime` | `java.util.Date` |
| 金额 | `BigDecimal`，标度固定 2 位 | `double` / `float` |
| 主键与 ID | `Long`（雪花）**或** `String`（UUID） | 同一实体上两者混用 |
| 枚举 | `@JsonValue` 显式指定序列化值 | 依赖 `name()` |

三条理由：

- `Date` 同时携带日期与时区语义且可变，跨时区序列化行为不确定；`LocalDateTime` 由 commons 里的 Jackson 序列化器统一格式化为 `yyyy-MM-dd HH:mm:ss`。
- 浮点数无法精确表示十进制小数，金额累加必然产生偏差——这类 bug 在对账时才暴露，且难以追溯。
- 同一实体上 ID 类型混用（有的字段 `Long`、有的 `String`）会让调用方无法统一处理，序列化后前端还可能因 JS 数字精度截断长整型。

**错误：**

```java
private Date createdAt;      // ❌
private double amount;       // ❌ 精度丢失
private Long id;
private String parentId;     // ❌ 与 id 类型不一致
```

**正确：**

```java
private LocalDateTime createdAt;
private BigDecimal amount;   // 标度 2
private Long id;
private Long parentId;
```


### R / RList / RPage 按形状选型

| 返回形状 | 类型 |
|---|---|
| 单对象 | `R<{Name}Response>` |
| 不分页列表 | `RList<{Name}Response>` |
| 分页列表 | `RPage<{Name}Response>` |
| 仅成功/失败 | `R<Boolean>` |
| 成功无数据 | `R<Void>` + `R.ok()` |

选错类型会让前端拿不到 `total` / `pageNo`，或被迫解包多余的一层。

**错误：**

```java
public R<List<UserResponse>> page(UserPageQuery q) { // ❌ 分页信息丢失
    return R.ok(userService.page(q).getData());
}
```

**正确：**

```java
public RPage<UserResponse> page(@Valid UserPageQuery q) {
    return RPage.ok(userService.page(q));
}
```

Service 层分页返回 `PageResult<T>`，由 Controller 转成 `RPage<T>`。

## 6. DTO 约定


### 用 MapStruct 转换，不手写赋值

Entity / Dto / Request / Response 之间的转换一律走 MapStruct。手写 `setXxx` 的问题是加字段时不会报错，只是静默丢值。

每个功能一个 `{Feature}Converter`，标 `@Mapper(componentModel = "spring")`：

```java
@Mapper(componentModel = "spring")
public interface UserConverter {
    UserDetailResponse toResponse(UserEntity entity);
    List<UserListItemResponse> toListItems(List<UserEntity> entities);
    UserEntity toEntity(UserCreateRequest request);
    void updateEntity(@MappingTarget UserEntity entity, UserUpdateRequest request);
}
```

实际用到的每种转换都要显式声明方法，不要在 Service 里临时拼装。


### Dto 不外露，双角色必须拆开

`{Name}Dto` 只用于 Service 之间、Service 内部方法之间，或 MQ 载荷。Controller **既不接收也不返回** Dto。

一个对象若同时承担「内部传输」和「接口返回」，必须拆成 Dto + Response 两个类。图省事合并的代价是：内部加一个字段就意外扩大了对外契约，且没有任何编译期提示。

```
Service ←→ Service     用 Dto
MQ 载荷                用 Dto
Controller ←→ 外部      用 Request / Response
```


### 分页查询必须 extends PageQuery

`{Name}Query` 用于 GET，通过 `@Valid @ModelAttribute` 绑定查询串。**需要分页就必须 `extends PageQuery`**，拿到统一的 `pageNo` / `pageSize` 及其边界校验（页码 ≥ 1、每页 ≤ 200）。

自己声明分页字段会漏掉上限校验，前端传 `pageSize=999999` 直接拖垮数据库。

**错误：**

```java
public class OrderPageQuery {
    private Long pageNo;    // ❌ 无 @Min
    private Long pageSize;  // ❌ 无上限
}
```

**正确：**

```java
@Data
@Schema(description = "订单分页查询")
public class OrderPageQuery extends PageQuery {
    @Schema(description = "订单编号（模糊查询）")
    private String orderNo;

    @Schema(description = "状态")
    @EnumMatch(enumClass = OrderStatus.class)
    private String status;
}
```

不分页的查询用普通 `{Name}Query`，不要为了统一而硬加分页字段。


### Request 按动作命名并强制校验

`{Name}{Action}Request`——`OrderCreateRequest`、`OrderUpdateRequest`、`OrderCancelRequest`。除非资源确实只有一个动作，否则不要用笼统的 `OrderRequest`：创建和更新的必填字段几乎从不相同，共用一个类就只能把校验全放宽。

字段**必须**带 Jakarta Validation，`message` 用中文（会直接透给前端）。

**正确：**

```java
@Data
@Schema(description = "创建订单请求")
public class OrderCreateRequest {
    @Schema(description = "产品 ID", example = "1001")
    @NotNull(message = "产品 ID 不能为空")
    private Long productId;

    @Schema(description = "数量", example = "2")
    @NotNull(message = "数量不能为空")
    @Min(value = 1, message = "数量必须大于等于 1")
    @Max(value = 999, message = "数量必须小于等于 999")
    private Integer quantity;
}
```

校验失败由 `GlobalExceptionHandler` 捕获 `MethodArgumentNotValidException` 统一处理，不在 Controller 里手写判空。


### Response 按视图命名

按**使用场景**命名而非按实体：`OrderDetailResponse`、`OrderListItemResponse`、`OrderCreateResponse`。列表页和详情页需要的字段量差异往往很大，共用一个类会让列表接口传输大量无用字段。

```java
@Data
@Schema(description = "订单详情响应")
public class OrderDetailResponse {
    @Schema(description = "订单 ID") private Long id;
    @Schema(description = "订单编号") private String orderNo;
}
```

每个字段都要有 `@Schema(description = ...)`，中文描述——这是 Knife4j 文档的唯一来源。

## 7. 命名约定


### 类名后缀对照表

| 种类 | 模式 | 示例 | 位置 |
|---|---|---|---|
| 启动类 | `{Project}Application` | `OrderServerApplication` | 根包 |
| Controller | `{Name}Controller` | `OrderController` | `controller/` |
| Service 接口 | `{Name}Service` | `OrderService` | `service/` |
| Service 实现 | `{Name}ServiceImpl` | `OrderServiceImpl` | `service/impl/` |
| Mapper | `{Name}Mapper` | `OrderMapper` | `mapper/` |
| Entity | `{Name}Entity` | `OrderEntity` | `entity/` |
| 请求体 | `{Name}{Action}Request` | `OrderCreateRequest` | `dto/{业务}/` |
| 响应体 | `{Name}{View}Response` | `OrderDetailResponse` | `dto/{业务}/` |
| 查询参数 | `{Name}Query` / `{Name}PageQuery` | `OrderPageQuery` | `dto/{业务}/` |
| 内部传输 | `{Name}Dto` | `OrderSummaryDto` | `dto/{业务}/` |
| 异常 | `{Name}Exception` | `OrderLockedException` | `exception/` |
| MapStruct | `{Name}Converter` | `OrderConverter` | `converter/` |
| 配置 | `{Name}Config` / `{Name}Properties` | `RedisConfig` | `config/` |
| 枚举 | 名词 | `OrderStatus` | `enums/` |
| 常量 | `{Name}Constants` | `AuthConstants` | `constants/` |
| 工具 | `{Name}Utils` | `DateUtils` | `utils/` |

`{Name}` 是业务名词且**用单数**（`User` 而非 `Users`）；动词放方法名，不进类名（不要 `OrderCreator`）。除行业通用缩写外不缩写（`Order` 不写 `Ord`）。


### Controller 方法名与排列顺序

标准 CRUD 用固定动词，**不带资源名**（用 `create` 而非 `createUser`——类名已经说明了资源）：

`page`（分页）/ `list`（全量）/ `select`（下拉选项）/ `get` / `create` / `update` / `delete`（硬删）/ `remove`（软删）

非 CRUD 用业务动词 + 资源名：`cancelProcess`、`resetPassword`。

**排列顺序固定**：先全部 CRUD，再非 CRUD；CRUD 内部按 `page → list → select → get → create → update → delete/remove`。顺序固定后，翻任何一个 Controller 都能在相同位置找到相同种类的方法。

```java
@GetMapping                    public RPage<UserListItemResponse> page(...)
@GetMapping("/all")            public RList<UserListItemResponse> list(...)  // 需限制最大条数防 OOM
@GetMapping("/options")        public RList<UserOptionResponse> select()
@GetMapping("/{id}")           public R<UserDetailResponse> get(...)
@PostMapping                   public R<UserCreateResponse> create(...)
@PutMapping("/{id}")           public R<Boolean> update(...)
@DeleteMapping("/{id}")        public R<Boolean> remove(...)
```

同一个 Controller 里不允许同时存在 `delete` 和 `remove`——两个删除语义并存必然被误用。


### 枚举与常量命名

- 常量：`UPPER_SNAKE_CASE`，放在 `{Xxx}Constants` final 类里
- 枚举类型：`PascalCase`；枚举值：`UPPER_SNAKE_CASE`

枚举若需序列化成业务字符串，用 `@JsonValue` + `@JsonCreator` 显式控制，不要依赖 `name()`——那会让 Java 侧改名直接破坏 API 契约。

```java
@Getter
@RequiredArgsConstructor
public enum OrderStatus {
    PENDING("pending", "待支付"),
    PAID("paid", "已支付"),
    CANCELLED("cancelled", "已取消");

    private final String value;
    private final String label;

    @JsonValue
    public String getValue() { return value; }
}
```


### 包结构按类型分一级，按业务分二级

- 一级子包按**类型**：`controller`、`service`、`mapper`、`entity`、`converter`、`config`、`constants`、`enums`、`exception`、`utils`
- 二级子包按**业务名词**：只有 `dto` 需要再按业务分（`dto/order/`、`dto/user/`）

Controller、Service、Mapper 直接放在各自类型包根下，不再按业务嵌套——这类文件本就一个业务一个类，再套一层只增加路径深度。

```
com.example.app
├── controller/OrderController.java
├── service/OrderService.java
├── service/impl/OrderServiceImpl.java
├── mapper/OrderMapper.java
├── entity/OrderEntity.java
└── dto/order/OrderCreateRequest.java
```


### Service 与 Mapper 方法名

**Service** —— 与 Controller 不同，这里**带**资源名，因为一个 Service 可能被多处调用，脱离上下文也要可读：

- 写：`create{Name}` / `update{Name}` / `remove{Name}`（软删）/ `delete{Name}`（硬删），业务动作用 `cancel{Name}` / `approve{Name}`
- 读：`getById` / `getBy{Xxx}`（单个）、`listAll{Name}s`（全量）、`list{Name}Options`（下拉）、`list{Name}s`（分页）
- 返回类型必须是 `Response` / `Dto` / 原始类型，**绝不是** Entity

**Mapper** —— 简单 CRUD 由 `MPJBaseMapper` 提供（`selectById`、`insert`…），自定义方法用 `selectBy{Xxx}` / `listBy{Xxx}` / `countBy{Xxx}` / `existsBy{Xxx}`，批量用 `insertBatch` / `updateBatchById`。


### URL 全小写 kebab-case 复数

- 全小写，多词用 **kebab-case**：`/order-items`
- 资源名用**复数**：`/orders`、`/users`、`/roles`
- 单个资源 `GET /orders/{id}`，集合 `GET /orders`
- 非 CRUD 动作：`POST /orders/{id}/cancel`，**不要** `/cancelOrder` 这种把动词塞进路径的写法

分页、全量、下拉三种查询的路径约定：

| 用途 | 路径 | 说明 |
|---|---|---|
| 分页 | `GET /roles` | 不要 `/roles/page` |
| 全量 | `GET /roles/all` | 必须限制最大返回条数防 OOM |
| 下拉选项 | `GET /roles/options` | 只返回 `{id, name}` |

注意 URL 用复数，而类名和实体用单数——这不矛盾：URL 指的是资源集合，类指的是单个对象。

## 8. 技术栈基线


### 技术栈基线

| 层面 | 选型 |
|---|---|
| 基础 | Java 21 + Spring Boot 3.5 + Spring Cloud 2025.0（或兼容版本） |
| 网关 | Spring Cloud Gateway（WebFlux / Netty） |
| ORM | MyBatis Plus + mybatis-plus-join，**不用 XML 映射** |
| 连接池 | HikariCP |
| Web 容器 | Undertow |
| 鉴权 | Sa-Token |
| API 文档 | Knife4j（集成 SpringDoc OpenAPI 3） |
| 对象映射 | MapStruct |
| 样板消除 | Lombok |
| 构建 | Maven 3.8+，附带 Wrapper |
| 日志 | SLF4J + Logback，生产用 JSON 结构化输出 |

数据库与缓存的具体版本、以及多数据库支持策略，以项目自身的 CLAUDE.md 为准——这部分项目间差异大，不适合写死在通用规则里。


### 避免复杂 lambda 表达式

多行、嵌套或带副作用的 lambda 在异常栈轨迹里只显示为 `lambda$methodName$0`——这个名字既不表达意图，也不指向具体哪一行。方法里若有多个 lambda，序号还会随代码顺序变动，跨版本对比栈轨迹时对不上。

抽成具名方法后，栈轨迹直接指向出错处，方法名本身也说明了在做什么。

**错误（异常只会报在 `lambda$process$0`，看不出是哪一步失败）：**

```java
list.stream()
    .map(item -> {
        var dto = new ItemDTO();
        dto.setName(item.getName());
        if (item.getParent() != null) {
            dto.setParentName(item.getParent().getName());
        }
        return dto;
    })
    .toList();
```

**正确（栈轨迹指向 `toDTO`，且该方法可单独测试与复用）：**

```java
list.stream()
    .map(this::toDTO)
    .toList();

private ItemDTO toDTO(Item item) {
    var dto = new ItemDTO();
    dto.setName(item.getName());
    if (item.getParent() != null) {
        dto.setParentName(item.getParent().getName());
    }
    return dto;
}
```

**判据**：超过一行就提取。单表达式 lambda（`x -> x.getId()`、`x -> x > 0`）保持内联，方法引用优先于等价的 lambda。


### Lombok 注解约定

| 场景 | 注解 |
|---|---|
| DTO | `@Data` + `@NoArgsConstructor` |
| Spring bean | `@RequiredArgsConstructor` + `final` 字段做构造注入 |
| 日志 | `@Slf4j`（禁止手写 `LoggerFactory.getLogger`） |
| Enum 字段 | `@Getter` |

构造注入优于 `@Autowired` 字段注入：`final` 字段保证依赖不可变，且缺依赖时在启动期就失败，而不是运行到那行才 NPE。

**保留显式实现**的两种情况：工具类（私有构造 + 全静态方法）、构造函数含参数校验的类——这两种情况 Lombok 生成的构造器反而会绕过约束。


### 根目录与每个模块都要有 README

多模块工程里，**项目根目录和每一个子模块都必须有 `README.md`**。根 README 描述整个项目是什么、提供哪些能力、由哪些模块组成；模块 README 描述这一个模块负责什么、对外提供什么、依赖谁。**单模块工程只需要根 README**，包结构在根 README 里用一节说清即可。

没有 README 时，模块边界只能靠读 `pom.xml` 的依赖和翻包结构反推。反推出来的边界是当前实现的样子，不是设计意图——于是新代码被放进"看起来差不多"的模块，分层和依赖方向就是这样一点点烂掉的。

新增模块时同步新增 README；模块能力发生变化（新增对外接口、依赖关系调整、职责搬迁）时同步更新 README，与改代码在同一个提交里。

**错误（模块只有代码，没有说明）：**

```text
myapp/
├── README.md              ← 只写了 "mvn spring-boot:run"
├── myapp-common/          ← 没有 README，谁都往里塞工具类
├── myapp-user/            ← 没有 README，不知道是否允许被别的模块依赖
└── myapp-gateway/         ← 没有 README
```

**正确（每层都能自解释）：**

```text
myapp/
├── README.md              ← 项目能力 + 模块清单 + 快速开始
├── myapp-common/
│   └── README.md          ← 只放无业务语义的通用能力，禁止依赖业务模块
├── myapp-user/
│   └── README.md          ← 用户域：注册、认证、组织关系；对外只经 UserService
└── myapp-gateway/
    └── README.md          ← 路由、鉴权前置、限流；不含业务逻辑
```

根 README 至少包含：

| 小节 | 内容 |
|---|---|
| 项目简介 | 一两句话说清这个系统解决什么问题 |
| 核心能力 | 对外提供的主要能力清单 |
| 模块清单 | 多模块：表格列出各模块及其一句话职责，链接到模块 README；单模块：一节"包结构"说明各包放什么 |
| 技术栈 | 语言、框架、数据库、中间件的版本基线 |
| 快速开始 | 环境要求、构建命令、启动命令、默认端口 |

子模块 README（多模块工程）至少包含：

| 小节 | 内容 |
|---|---|
| 模块职责 | 这个模块负责什么，**以及明确不负责什么** |
| 对外能力 | 提供的接口、Service、扩展点；供谁调用 |
| 依赖说明 | 依赖了哪些内部模块与外部中间件，为什么 |
| 本地运行 | 单独构建/启动/测试该模块的命令（如果可以单独跑） |

写法遵循 `doc-writing-best-practices`：示例可直接粘贴执行、写清为什么、中西文之间加空格。

README 不是 `CLAUDE.md` 的替代品，两者受众不同：README 面向人，讲能力与边界；CLAUDE.md 面向 AI，讲当前项目锁定的决策与约束。不要把同一段内容抄两份。

