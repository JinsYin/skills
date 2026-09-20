# product-spec

管理产品功能规范：功能清单、交互逻辑、以及 Flyway 式版本化的变更记录。**产出物的第一读者是 AI 设计工具**（Claude Design、v0、Figma Make、Lovable），第二读者才是人。

## 核心：V 链 + 合成快照，两轨分离

产品规范有两个互相打架的诉求：

- **追溯**——「关联应用这列什么时候改叫关联空间的、为什么」，要的是增量链
- **喂设计工具**——要的是当前全量态

纯 Flyway 增量链只满足前者。当前态得靠脑内重放 V1→Vn，人能做，设计工具做不了：把 V1 和 V2 一起丢给 v0，它会照着 V1 里那个已被 V2 改名的字段画。反过来每版存全量，则 diff 全是噪音，追溯等于没有。

```
.product/spec/console/
├── CURRENT.md          ← 合成的当前全量态，generated，喂设计工具
├── V1__baseline.md     ← 全量基线
└── V2__data_space.md   ← 只写增量
```

`V*.md` 管演进，`CURRENT.md` 管当前态，后者由 `sync` 重放前者生成。这条分离抄自 [OpenSpec](https://github.com/Fission-AI/OpenSpec) 的 `specs/` + `changes/`。

## 与相邻方案的分工

| 层 | 谁管 |
|---|---|
| 为什么做、验收标准 | PRD / [ProductSpec](https://github.com/gokulrajaram/ProductSpec) |
| **有什么功能、怎么交互** | **本 skill** |
| 长什么样（色值、字体、间距） | `design.md` / `tokens.css` |
| 怎么实现 | 代码与工程 skill |

规范正文里出现十六进制色值或 `px` 一律是越界，`check` 会报。

## 子命令

| 命令 | 做什么 |
|---|---|
| `init` | 勘察原型与代码 → 访谈 → 建目录与 `V1__baseline.md` |
| `add <title>` | 新建 `V{n+1}__<slug>.md`，访谈填变更清单，自动 sync |
| `sync` | 重放 V 链生成 `CURRENT.md` |
| `check` | 版本连续性、快照新鲜度、定位符可解析、悬空引用、视觉污染 |
| `export --tool <v0\|figma-make\|claude-design\|lovable>` | 按工具方言裁剪 prompt 包 |

## 六条纪律

1. `CURRENT.md` 只能由 `sync` 写——手改会被下次 sync 静默覆盖
2. `status: active` 的 V 文件不回改，改需求就发下一个 V
3. 定位符解析不到就报错停下，**绝不猜**——猜错会留下没人发现的幽灵页面
4. 不写像素、色值、字号，那层归 `.product/design/`
5. 对外文案以项目 CLAUDE.md 为准，内部代号不得进正文
6. 写完必须 sync

## references

| 文件 | 内容 |
|---|---|
| `spec-format.md` | 格式权威定义：目录、frontmatter、定位符语法、章节清单、五种变更操作 |
| `templates.md` | baseline / change / CURRENT / README 四份可直接抄的骨架 |
| `synthesis.md` | 合成算法、边界条件（链式改名、删后重建、draft 纳入）、检查判据表 |
| `tool-dialects.md` | v0 / Figma Make / Claude Design / Lovable 各自吃什么 |

## 两个设计要点

**「前置条件」列**——`spec-format.md` 的页面规格模板里最容易被略过的一列，也是设计工具画不对的主因。按钮什么时候是灰的、什么时候根本不显示，不写它就只能靠猜。

**「明确不做」章**——借鉴 [design.md](https://designproject.io/blog/design-md-file/)：约束比描述更能定形。AI 设计工具的失败模式不是画不出来，而是自作主张多画了。「不要过度设计」是废话，「列表页不要用卡片布局，一律用表格」才有用。

## 启用

```bash
# 在仓库根目录执行
mkdir -p "$HOME/.claude/skills"
ln -s "$(pwd)/skills/product-spec" "$HOME/.claude/skills/product-spec"
```

用符号链接而非拷贝，源仓才是唯一事实来源。
