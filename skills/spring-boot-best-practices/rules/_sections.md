# Sections

定义所有分类、排序、影响级别与描述。括号内的 section ID 即规则文件名前缀。

影响级别按**违反后果**划分，不是按出现频率：

| 级别 | 含义 |
|---|---|
| CRITICAL | 违反即 bug、安全问题，或直接跑不起来 |
| HIGH | 能跑，但审查必打回、后续必返工 |
| MEDIUM | 不一致，但功能正确 |
| LOW | 风格偏好 |

---

## 1. 分层纪律 (layer)

**Impact:** CRITICAL
**Description:** Controller → Service → Mapper 单向依赖。跨层调用是最贵的架构债——一旦渗透，事务边界、可测性、复用性同时失守，返工成本远高于其他任何一类违规。

## 2. 密码学 (crypto)

**Impact:** CRITICAL
**Description:** 国密 SM2/SM3/SM4 的算法选型、密钥管理与日志纪律。违反直接构成安全漏洞，且往往在上线后才被发现。

## 3. 实体与持久化 (entity)

**Impact:** CRITICAL
**Description:** MyBatis Plus 实体的主键策略与字段填充。选错主键类型会在 INSERT 时直接失败，且故障现象与根因相距很远。

## 4. 数据库与迁移 (db)

**Impact:** HIGH
**Description:** 表/列/索引命名，以及多方言、多部署形态的迁移分层与同步。迁移漏一份方言、或唯一约束在分布式下退化成分片本地唯一，故障只在目标环境暴露，通常是生产。

## 5. 响应包装与错误码 (envelope)

**Impact:** HIGH
**Description:** R / RList / RPage 的选型与错误码格式。契约不一致会外溢到所有调用方。

## 6. DTO 约定 (dto)

**Impact:** HIGH
**Description:** Request / Response / Query / Dto 的职责边界、校验与转换。混用会导致敏感字段泄漏或校验缺失。

## 7. 命名约定 (naming)

**Impact:** MEDIUM
**Description:** 包、类、方法、URL 的命名。不一致不影响功能，但持续增加阅读成本。

## 8. 技术栈基线 (stack)

**Impact:** LOW
**Description:** 依赖选型、Lombok 用法、模块文档约定与 Java 语言层面的可读性约定。
