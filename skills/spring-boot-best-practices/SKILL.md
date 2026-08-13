---
name: spring-boot-best-practices
description: Spring Boot 3 + Java 21 + MyBatis Plus 项目的编码规范与架构纪律。涵盖分层依赖、国密 SM2/SM3/SM4、MyBatis Plus 实体与主键策略、多方言数据库迁移、R/RList/RPage 响应包装、DTO 职责边界、命名约定。在编写、审查或重构 Spring Boot 后端代码时使用——尤其是新增 Controller/Service/Mapper、定义 Entity 或 DTO、写数据库迁移、处理加解密与签名、或设计 API 契约时。
license: MIT
metadata:
  author: JinsYin
  version: "1.0.0"
---

# Spring Boot Best Practices

Spring Boot 3 后端的规范集，43 条规则分 8 类，按**违反后果**排序。

## 如何使用本 skill

**不要一次读完所有规则。** 先在下面的索引里定位与当前任务相关的条目，再按需 `Read` 对应文件：

```
rules/layer-one-direction.md
rules/entity-tableid-assign-id.md
```

每条规则含：为什么、错误示例、正确示例。

选取原则——**按你正在改的东西定位，不按分类通读**：

| 你在做什么 | 先读 |
|---|---|
| 新增 Controller | `layer-*`、`naming-controller-methods`、`envelope-r-types` |
| 新增/修改 Entity | `entity-*`、`db-table-naming`、`db-column-naming` |
| 写数据库迁移 | `db-migration-*`、`db-opengauss-dialect`、`db-index-naming` |
| 加唯一约束 / 索引 | `db-distributed-unique-index`、`db-index-naming` |
| 定义 DTO | `dto-*`、`naming-class-suffix` |
| 加解密 / 签名 | `crypto-*`（全部，只有 6 条且互相关联） |
| 设计 API 契约 | `envelope-*`、`naming-url` |
| 代码审查 | 按改动涉及的文件类型选对应分类 |

## 分类与影响级别

影响级别按**违反后果**划分，不按出现频率：CRITICAL = 即 bug/安全问题/跑不起来；HIGH = 审查必打回、必返工；MEDIUM = 不一致但功能正确；LOW = 风格偏好。

| 优先级 | 分类 | 影响 | 前缀 | 条数 |
|---|---|---|---|---|
| 1 | 分层纪律 | CRITICAL | `layer-` | 7 |
| 2 | 密码学 | CRITICAL | `crypto-` | 6 |
| 3 | 实体与持久化 | CRITICAL | `entity-` | 3 |
| 4 | 数据库与迁移 | HIGH | `db-` | 8 |
| 5 | 响应包装与错误码 | HIGH | `envelope-` | 5 |
| 6 | DTO 约定 | HIGH | `dto-` | 5 |
| 7 | 命名约定 | MEDIUM | `naming-` | 6 |
| 8 | 技术栈基线 | LOW | `stack-` | 3 |

## 规则索引

### 1. 分层纪律 (CRITICAL)

- `layer-one-direction` — Controller → Service → Mapper 单向依赖，每层只依赖紧邻下层
- `layer-controller-no-entity` — Controller 不得返回 Entity，会泄漏敏感字段
- `layer-no-map-response` — 不用 `Map<String,Object>` 当响应类型，契约不可见
- `layer-controller-auth-annotations` — 权限用 Sa-Token 注解声明，手写 if 判断是默认放行
- `layer-cross-service-via-service` — 跨领域注入对方 Service，不注入对方 Mapper
- `layer-service-no-http` — Service 不碰 `HttpServletRequest`，否则绑死 Web 容器
- `layer-no-silent-catch` — 禁止 catch 后不处理不重抛，把失败伪装成成功

### 2. 密码学 (CRITICAL)

- `crypto-approved-algorithms` — SM2 C1C3C2 / SM3 / SM4-GCM；禁 ECB、MD5、SHA1、自实现原语
- `crypto-provider-registration` — BouncyCastle 启动时注册一次，勿在热路径重复注册
- `crypto-sign-canonical-bytes` — 只对规范字节签名，禁止签 `toString()`
- `crypto-unique-iv-nonce` — IV/nonce 每次 `SecureRandom` 生成，GCM 重用 nonce 会使加密完全失效
- `crypto-no-hardcoded-secrets` — 密钥不入代码，加密/签名/MAC 分离密钥，携带 keyId
- `crypto-no-secret-logging` — 明文与密钥不进日志，密码学失败按安全错误处理

### 3. 实体与持久化 (CRITICAL)

- `entity-tableid-assign-id` — 主键用 `IdType.ASSIGN_ID`，`AUTO` 在非 MySQL 下 INSERT 直接失败
- `entity-field-fill` — `createdAt`/`updatedAt` 用 `@TableField(fill=...)`，勿依赖数据库默认值
- `entity-mapper-no-xml` — Mapper 不写 XML 和整句 SQL，用 wrapper 与 MPJ API

### 4. 数据库与迁移 (HIGH)

- `db-migration-parity` — 多方言迁移必须同版本号同步维护，漏一份只在目标环境炸
- `db-migration-base-overlay` — 同库多形态用 base + overlay 分层，只把无共通写法的那几条分叉
- `db-migration-locations-injection` — locations 构建期 profile 注入，未激活的 overlay 也要打进产物
- `db-distributed-unique-index` — 分布式库唯一约束须含分布键，追加索引用 GSI，新建表用内联约束
- `db-opengauss-dialect` — openGauss 三定律：无 `ON CONFLICT` / 无 `gen_random_uuid()` / 无 `jsonb_build_object`
- `db-table-naming` — 表名 `t_` 前缀 + snake_case + 单数
- `db-column-naming` — 列名 snake_case，审计四件套，软删 `deleted`
- `db-index-naming` — `uk_{table}_{field}` / `idx_{table}_{field}`

### 5. 响应包装与错误码 (HIGH)

- `envelope-r-types` — 按返回形状选 `R` / `RList` / `RPage`
- `envelope-factory-only` — 只用静态工厂构造，禁 `new R<>()` 后逐字段赋值
- `envelope-error-code-format` — 错误码 6 位，前 3 位复用 HTTP 状态码
- `envelope-bizexception-not-null` — 用 `BizException` 表达业务失败，不返回 `null`
- `envelope-field-types` — 时间用 `LocalDateTime`、金额用 `BigDecimal`、ID 类型不混用

### 6. DTO 约定 (HIGH)

- `dto-request-by-action` — Request 按动作命名，字段必带 Jakarta Validation + 中文 message
- `dto-query-extends-pagequery` — 分页查询必须 `extends PageQuery`，否则漏掉 pageSize 上限
- `dto-internal-not-exposed` — Dto 不外露，双角色对象必须拆成 Dto + Response
- `dto-response-by-view` — Response 按视图命名，全字段带 `@Schema`
- `dto-converter-mapstruct` — 用 MapStruct 转换，手写赋值加字段时会静默丢值

### 7. 命名约定 (MEDIUM)

- `naming-class-suffix` — 类名后缀对照表
- `naming-controller-methods` — CRUD 动词不带资源名，且排列顺序固定
- `naming-service-mapper-methods` — Service 方法带资源名，Mapper 用 `selectBy`/`listBy`/`countBy`
- `naming-url` — 全小写 kebab-case，资源复数，动作走子路径
- `naming-package-layout` — 一级按类型分包，二级按业务分包（仅 dto）
- `naming-enum-constants` — 枚举用 `@JsonValue` 显式控制序列化

### 8. 技术栈基线 (LOW)

- `stack-baseline` — 依赖选型基线
- `stack-lambda-simple` — 超过一行的 lambda 要提取；栈轨迹里只显示 `lambda$xxx$0`
- `stack-lombok` — DTO 用 `@Data`，bean 用 `@RequiredArgsConstructor` + final

## 与项目 CLAUDE.md 的关系

本 skill 是**跨项目通用**规范。凡涉及具体项目的包名、模块划分、数据库层数、锁定的业务决策，一律以该项目的 `CLAUDE.md` 为准——冲突时 CLAUDE.md 优先。

不要把这里的内容复制进项目的 `CLAUDE.md`：那会让同一条约定有两份可能漂移的副本，而 CLAUDE.md 是每会话常驻的，重复内容的成本按会话数累计。

## 全量编译版

需要一次性获取全部规则时读 `AGENTS.md`（约 31 KB）。该文件由 `scripts/build.sh` 从 `rules/` 生成，**不要手工编辑**。
