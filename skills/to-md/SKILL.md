---
name: to-md
description: >-
  Convert documents to Markdown using Microsoft's markitdown, auto-clean the
  result with markdownlint, then LLM-refine it against the source to fix
  structure (heading levels, broken tables, multi-column reading order,
  hyphenation) and strip extraction noise (repeated headers/footers, page
  numbers, watermarks) while preserving the original wording verbatim, and save
  it next to the source file with the same base name and a .md extension. Use
  this WHENEVER the user wants a document
  turned into Markdown — PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx),
  HTML, CSV, JSON, XML, EPUB, RTF, .txt, images, or audio. Trigger on phrases
  like "convert this to markdown", "turn this PDF/doc/deck into md", "extract
  the text of this file as markdown", "markitdown this", "make a .md from this",
  or when the user drops a document path and asks for its markdown version —
  even if they don't name markitdown or markdownlint explicitly. Handles a
  single file or a batch (multiple files / a directory).
---

# to-md

把各种文档转成干净、**忠于原文且结构正确**的 Markdown，存到**与源文件相同的目录、相同的主文件名、仅扩展名换成 `.md`**。

底层管线分两段：

1. **确定性段（脚本 `scripts/convert.sh`）**：`markitdown`（提取内容）→ `postprocess.py`（语义级清理）→ `markdownlint-cli2 --fix`（按一份宽松规则清理排版）。这一段已固化在脚本里，**直接调脚本即可，不要手搓 markitdown/lint 命令**——脚本帮你统一处理了输出路径推导、目录批量展开、覆盖保护、语义清理和 lint 配置。
2. **LLM 精修段（你来做，默认执行）**：markitdown 是把版面「拍扁」成文本，标题层级、表格、多栏阅读顺序、断字分页这些**版面结构信息会丢，而脚本修不了**。所以脚本跑完后，由你**对照源文件**把结构修回来、把转换噪声清掉——这是把「能读」的产物变成「忠实」产物的关键一步。详见下文 [LLM 精修阶段](#llm-精修阶段)。

> 一句话记住边界：**精修是还原版面结构、清理提取噪声，不是改写作者的话。** 转换工具的全部价值在于忠于原文，多写一个字、顺手「润色」一句，都是在悄悄污染一份别人会当作可信副本来用的文档。

## 什么时候用

只要用户想把一个文档变成 Markdown 就用，无论他有没有点名 markitdown。典型信号：给出一个 `.pdf` / `.docx` / `.pptx` / `.xlsx` / `.html` / `.csv` / `.epub` / 图片 / 音频等路径，并要它的 markdown 版本。

## 工作流程

### 1. 确认工具就绪

`markitdown` 必须可用（`command -v markitdown`）。若缺失，提示用户安装：`pip install 'markitdown[all]'`，然后停下。
lint 走 `npx markdownlint-cli2`，需要 `npx`（Node）。没有 `npx` 时脚本会自动跳过 lint 并保留转换结果——这是可接受的降级。

### 2. 覆盖保护：先检测，再决定

脚本默认**拒绝覆盖**已存在的同名 `.md`，并以退出码 `3` + `EXISTS\t<路径>` 报告。这是有意为之——“是否覆盖”需要用户判断，不该由脚本擅自决定。

所以正常流程是**先不带 `--force` 跑一次**：

- 如果没有冲突 → 转换照常完成，结束。
- 如果脚本报告了 `EXISTS`（退出码 3）→ 把将被覆盖的文件名告诉用户，**问他是否覆盖**。得到同意后再带 `--force` 重跑（只针对需要覆盖的那些输入）。用户拒绝则保留原文件、跳过。

不要为了省事一上来就 `--force`。

### 3. 调用脚本（确定性段）

先把本 `SKILL.md` 所在目录解析为 `SKILL_DIR`，再通过该变量调用随 skill 分发的脚本；不要假定 skill 安装在某个用户目录。

```bash
# 单个文件
"$SKILL_DIR/scripts/convert.sh" path/to/report.pdf

# 批量：多个文件
"$SKILL_DIR/scripts/convert.sh" a.docx b.pptx c.html

# 批量：一个目录（转换该目录下所有受支持的文档，不递归子目录）
"$SKILL_DIR/scripts/convert.sh" ./docs

# 用户已确认覆盖后
"$SKILL_DIR/scripts/convert.sh" --force path/to/report.pdf
```

输出路径是脚本自己推导的：`report.pdf` → 同目录下的 `report.md`。源文件本身是 `.md` 会被跳过（避免自我覆盖）。

### 4. LLM 精修（默认执行）

脚本产物只是「机器拍扁」的文本，结构和噪声问题它修不了。**默认对每个本次生成的 `.md` 做一轮精修**，照下文 [LLM 精修阶段](#llm-精修阶段) 的方法和边界来做。做完用 `convert.sh --lint-only <那些.md>` 重跑一遍 lint 收尾（精修是手动 Edit，缩进/空行可能乱）。

什么时候**可以跳过**精修：用户明说「只要原始转换 / 不用精修 / 要快」，或转换失败没有产物。批量很大（比如十几个以上文件）时，先告诉用户「精修会逐个过、比较花时间」，问他是要全部精修、只精修关键几个、还是先拿原始产物——别闷头把几十个文件全精修。

### 5. 汇报结果

转换完成后，简洁告诉用户：

- 生成了哪个/哪些 `.md` 文件（完整路径）。
- **精修都改了什么**：一句话概括（如「修正了 3 处标题层级、还原了第 2 页那张被打散的表格、删掉了重复页眉」）。这让用户知道哪些是结构修复而非内容改动，建立信任。
- lint 阶段如果留下了**非可自动修复**的告警（脚本会打印），择要转述一下，并说明这些通常是源文档结构本身导致的、不影响使用——不要因为这些告警就认为转换失败。
- 如果用户想看内容，可以 `Read` 生成的文件给他看，但不必默认这么做。

## 语义清理说明（postprocess.py）

markitdown 抽出的 Markdown 有些结构问题 lint 修不了，`scripts/postprocess.py` 在 lint 之前用确定性规则补上，规则都偏保守（命中不了就原样放过，绝不破坏内容）：

- **目录块** → 规范列表：`目录`/`Table of Contents`/`Contents` 标题后紧邻的连续条目逐行转成 `- ` 列表项，把点引线（`......`）压成单空格、保留页码；已是列表项的目录不动。
- **裸 JSON** → 围栏：一整段能被 `json.loads` 解析的文本用 ` ```json ` 包起来；已围栏的、以及形如 `{占位符}` 的非 JSON 文本不受影响。
- **空表格行** → 删除：单元格全空的表格行（如 `|  |  |`）去掉，分隔行 `| --- |` 和有内容的数据行保留。

该步骤纯 Python、无外部依赖，默认始终执行（即便带 `--no-lint` 也会跑，因为这属于产出结构而非排版）。

## lint 规则说明

`assets/markdownlint.jsonc` 是一份**面向“转换产物”的宽松规则**：关掉了对机器抽取文本无意义的 MD013（行长）、MD033（内联 HTML，表格/上下标会用到）、MD041（首行非标题）、MD025（多个一级标题，PDF 常见），其余排版规则保持默认，让 `--fix` 把真正能修的脏排版（多余空行、列表缩进、行尾空格、文件末尾换行等）自动清理掉。需要更严格时可临时改这个配置，但默认值适配绝大多数文档。

## LLM 精修阶段

**为什么需要这步**：markitdown 把版面线性化成文本，只存在于「版面」里的结构信息（标题层级、表格、多栏顺序、断字分页）会丢，页眉页脚水印这类「非内容」又会被一起抽进来。这些是**提取产物的缺陷，不是文档本身**——把结构修回去、把噪声清掉，产物才真正等于源文档，这正是转换的目的。`postprocess.py` 和 lint 只敢做确定性的小修，剩下的要你对照源文件用判断力来补。

**铁律——改结构、清噪声，绝不改写正文：**

- 你在还原作者已经写好的东西，不是在创作。任何时候你想「把这句改通顺点」「补一句更清楚」，立刻停手——那是内容漂移，会悄悄篡改一份别人当作可信副本来用的文档。
- 拿不准某处是噪声还是内容时，**保留**。宁可多留一行页码，也不要误删一行正文。
- 源文件里读不出的内容**不要编**。markitdown 抽出的乱码 / 缺字，能对照源文件确认就修，确认不了就保持原样，别凭空补。

**怎么做：**

1. 先 `Read` 源文件（PDF、图片、docx 等 Read 都能渲染），它是**唯一事实来源**；再 `Read` 刚生成的 `.md`。
2. 对照着用 `Edit` 做**定点修改**——只改错的地方，别整篇重写。定点改既诚实（改了什么一目了然），又避免整篇重写时手滑丢内容。只有当结构烂到没法定点修时才整篇重写，且重写后要拿源文件核对章节数 / 篇幅，确认没漏。
3. 改完跑 `"$SKILL_DIR/scripts/convert.sh" --lint-only <那些.md>` 收尾排版（精修是手动 Edit，缩进 / 空行 / 行尾空格可能乱，交给 lint 规整；它**不会**重新转换覆盖你的成果）。

**精修清单（适中强度：结构修复 + 清噪，不动正文表达）**

结构修复（对照源文件版面）：

- **标题层级**：markitdown 常把层级压平或定错级。按源文件的视觉层级（字号、编号 `1.` / `1.1` / `一、`）定 `#` 级别。
- **表格**：被打散、串列、合并单元格丢失的表格，对照源文件重建——列数对齐、补回合并 / 空单元格的应有内容、把跨行拆开的一行并回去。
- **列表**：本是条目却被转成普通段落的，改成 `-` / `1.` 列表；修正嵌套层级。
- **阅读顺序**：多栏 PDF 常被交错抽取，按源文件的自然阅读流重排。
- **断字与折行**：行尾连字符断词（`infor-\nmation` → `information`）接回；被硬折行打断的同一段落并回成完整段落。
- **代码 / 公式**：代码块补围栏；公式保持原样（明显是 LaTeX 的保留 LaTeX），不要去「算」或改写。

清噪（删掉提取出来的非内容；删之前确认它在源文件里确实是版面装饰而非正文）：

- 每页重复出现的页眉 / 页脚（书名、章节名跑马灯）。
- 孤立成行的页码。
- 渗入正文的水印文字。
- `postprocess` 没清干净的目录点引线残留。
- **明显且可对照确认**的 OCR 错字（如 `rn`→`m`、`0`↔`O`）——只在源文件让正确写法毫无歧义时才改。

**自检**：精修后，源文件里每个标题、表格、图注、段落都应在产物里有对应。删噪声可以，丢内容不行。

## 边界与降级

- **转换失败**（markitdown 退出非 0，如加密 PDF、损坏文件）：脚本删掉半成品、报退出码 2 并继续处理其余输入。如实把失败的文件告诉用户。
- **格式不支持**：目录展开时只挑 markitdown 支持的扩展名；明确传入的不支持文件交给 markitdown 自己报错。
- **没有 npx**：跳过 lint，转换结果照常保存（已说明）。
- **源文件无法被 `Read` 渲染**（如纯音频转写、超大 PDF）：精修退回「仅基于 `.md`」——只做能从产物本身判断的结构修复（断字、明显的列表 / 标题），不臆测无从核对的表格内容；如实说明没拿到源做核对。
- **跳过精修**：用户要原始产物、要快，或转换失败无产物时，跳过第 4 步直接汇报。
- 脚本退出码：`0` 成功 / `2` 转换失败 / `3` 需确认覆盖 / `4` 无可处理输入；`--lint-only` 同此约定（无 .md 输入报 4）。
