# spec-triage

整顿**存量项目**的编码规范。**核心是分诊，不是生成文件。**

空仓或刚跑完脚手架的新项目用 `spec-setup`——那里没有代码可取证，本 skill 的每一步都会落空。

## 与其他规范 skill 的关系

| Skill | 是什么 |
|---|---|
| `spring-boot-best-practices` | 规范**内容**（跨项目通用的后端规则） |
| `frontend-ui-best-practices` | 规范**内容**（跨项目通用的前端规则） |
| `spec-setup` | 规范的**流程·新项目**：从访谈定形态与栈，只固化已裁决的，其余留白 |
| `spec-triage` | 规范的**流程·存量**：决定每条约定该放哪层、检测漂移、整顿既有规范 |

前两者是被读的，后两者是被执行的。

`spec-setup` 治**猜写**（代码还没写就铺满规则），本 skill 治**漂移**（规范与代码对不上）。新项目跑完 `spec-setup`，首个模块合并后就换成 `spec-triage --check`。

## 分诊的四层

```
CLAUDE.md            每会话常驻    本项目已裁决的具体约束、锁定决策
通用 skill           触发读索引    跨项目通用的规范
.claude/rules+paths  路径注入      窄领域、内容极少、不值得建 skill
项目文档/references  显式查阅      长尾查表
```

**第一问永远是「这条约定换个项目还成立吗」。** 通用规范塞进 `CLAUDE.md`，每个会话都要为其他项目也适用的内容付费；项目决策塞进通用 skill，则会污染其他项目。

## 流程

```
勘察（先取证）→ 分诊（路由表）→ 访谈（只问定不了的）→ 落地（过硬闸）→ 校验
```

`--check` 只报漂移不改文件，适合在阶段收尾、发版前，或大改动合并后跑。

skill 本身不依赖任何特定工作流。勘察阶段会先查清本项目实际的高频产物路径，再据此判定 `paths:`。

## references

| 文件 | 位置 | 内容 |
|---|---|---|
| `interview-bank.md` | 本 skill | 问题库，按通用/按栈分类；含「不要问的」 |
| `tier-routing.md` | `../spec-setup/references/` | 分诊判例、五种常见误判、拆分时机、何时不动 |
| `guards.md` | `../spec-setup/references/` | 硬闸，每条对应一次实际故障 |
| `rule-authoring.md` | `../spec-setup/references/` | 规则写法：为什么必须写「后果」、原子化判据、影响级别 |

后三份是两个 skill 的共用地基，由 `spec-setup` 持有。**两者同属 `sdd` plugin，成对安装**；单独安装本 skill 会让这三处引用悬空且不报错，若确实要单独用，先把文件复制进本 skill 的 `references/`。

## 硬闸从哪来

`guards.md` 的 G1～G10 都不是推演的，是实际踩出来的（G11 是 `spec-setup` 专属，不适用于本 skill）。几个例子：

- **G1**（`paths:` 禁止覆盖高频文档与工作流产物）：11 个规则文件都带着工作流产物通配，任意规划命令无差别注入 36788 B，子代理各付一遍。无论项目采用哪种工作流都一样中招——只是路径换成具体的规划目录、`docs/**` 或 `**/*.md`。
- **G3**（glob 必须真能命中）：某前端规则 `paths` 写 `**/*.vue`，项目零个 `.vue`、组件全是 `.tsx`——从未命中过，且描述里写着另一个框架的名字。两种失效都不报错。
- **G6**（删除前覆盖度比对）：一次迁移差点丢三处，其中一条是明确写着「不得删除」的锁定决策。
- **G7**（删除后查悬空引用）：删掉 UI 规则文件后，某 skill 传给下游的约束块仍引用它——约束静默消失，不报错。

这类故障的共同点是**沉默**。硬闸的作用就是把沉默变成显式失败。

## 启用

```bash
# 在仓库根目录执行；两者必须成对链接
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/spec-triage" "$HOME/.claude/skills/spec-triage"
ln -s "$(pwd)/skills/spec-setup"  "$HOME/.claude/skills/spec-setup"
```

用符号链接而非拷贝，本仓才是唯一事实来源。
