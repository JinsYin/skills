"""Generate write-fspec eval fixtures: evals/files/<fixture>/steps/NN-<slug>/ overlays."""
import os
import shutil
import sys

OUT = sys.argv[1]

CLAUDE_MD = """# Project Conventions

- Outward product name: 「开放平台」. Never show the internal codename Hermes or the internal service name hermes-gateway in any outward document or UI copy.
- Frontend apps: `console` (运营控制台).
"""

CLAUDE_MD_MULTI = CLAUDE_MD.replace(
    "- Frontend apps: `console` (运营控制台).",
    "- Frontend apps: `console` (运营控制台), `portal` (开发者门户).",
)


def console_html(backport=False, audits=False, spaces=None):
    """spaces: None -> 关联应用 count; 'count' -> 关联空间 count; 'list' -> 关联空间 list."""
    org_th = "关联应用" if spaces is None else "关联空间"
    org_td = {None: "3", "count": "2", "list": "系统空间、理赔空间"}[spaces]
    copy_action = " <a>复制 AppKey</a>" if backport else ""
    audit_nav = """
    <div class="group">安全审计
      <a data-page="audits">审计日志</a>
    </div>""" if audits else ""
    audit_page = """
  <section data-page="audits">
    <h1>审计日志</h1>
    <form class="filters">
      <input type="date"> 至 <input type="date">
      <select><option>全部操作类型</option><option>新建应用</option><option>重置密钥</option><option>停用应用</option><option>停用机构</option></select>
      <input placeholder="操作人">
      <button>查询</button><button>重置</button>
    </form>
    <table>
      <thead><tr><th>时间</th><th>操作人</th><th>操作类型</th><th>操作对象</th><th>结果</th><th>操作</th></tr></thead>
      <tbody>
        <tr><td>2026-10-18 14:02:11</td><td>王敏</td><td>重置密钥</td><td>理赔核验应用</td><td>成功</td><td><a>查看详情</a></td></tr>
        <tr><td>2026-10-18 09:40:57</td><td>李强</td><td>停用机构</td><td>华南医保结算中心</td><td class="tag-fail">失败</td><td><a>查看详情</a></td></tr>
      </tbody>
    </table>
    <div class="drawer" hidden>
      <h2>操作详情</h2>
      <dl><dt>变更前</dt><dd>状态：启用</dd><dt>变更后</dt><dd>状态：停用</dd><dt>来源 IP</dt><dd>10.12.3.45</dd></dl>
    </div>
  </section>""" if audits else ""
    return f"""<!doctype html>
<!-- Hermes 控制台原型；数据来自 hermes-gateway mock -->
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>开放平台控制台</title>
<style>
  body {{ font-family: "PingFang SC"; color: #1F2328; }}
  aside {{ width: 220px; }}
  .primary {{ background: #1F6FEB; color: #fff; padding: 6px 16px; border-radius: 6px; }}
  .tag-fail {{ color: #CF222E; }}
</style>
</head>
<body>
<aside>
  <div class="logo">开放平台</div>
  <nav>
    <div class="group">客户管理
      <a data-page="orgs">机构管理</a>
      <a data-page="apps">应用管理</a>
    </div>{audit_nav}
  </nav>
</aside>
<main>
  <section data-page="orgs">
    <h1>机构管理</h1>
    <form class="filters">
      <input placeholder="机构名称">
      <select><option>全部状态</option><option>正常</option><option>已停用</option></select>
      <button>查询</button><button>重置</button>
    </form>
    <table>
      <thead><tr><th>机构名称</th><th>统一社会信用代码</th><th>{org_th}</th><th>状态</th><th>操作</th></tr></thead>
      <tbody><tr><td>华东理赔服务中心</td><td>91310000MA1FL0XXXX</td><td>{org_td}</td><td>正常</td><td><a>查看</a> <a>停用</a></td></tr></tbody>
    </table>
  </section>
  <section data-page="apps">
    <h1>应用管理</h1>
    <form class="filters">
      <input placeholder="应用名称">
      <select><option>全部状态</option><option>启用</option><option>停用</option></select>
      <button>查询</button><button>重置</button>
    </form>
    <button class="primary">新建应用</button>
    <table>
      <thead><tr><th>应用名称</th><th>所属机构</th><th>AppKey</th><th>状态</th><th>创建时间</th><th>操作</th></tr></thead>
      <tbody><tr><td>理赔核验应用</td><td>华东理赔服务中心</td><td>ak_7f3e…c21</td><td>启用</td><td>2026-08-12 10:24</td><td><a>编辑</a> <a>重置密钥</a> <a>停用</a>{copy_action}</td></tr></tbody>
    </table>
    <div class="drawer" hidden>
      <h2>新建应用</h2>
      <label>应用名称 <input required maxlength="40"></label>
      <label>所属机构 <select required><option>华东理赔服务中心</option></select></label>
      <label>回调地址 <input type="url"></label>
      <button class="primary">保存</button><button>取消</button>
    </div>
    <div class="modal" hidden>
      <p>重置后旧密钥立即失效，请输入应用名称确认。</p>
      <input><button>确认重置</button>
    </div>
  </section>{audit_page}
</main>
</body>
</html>
"""


PORTAL_HTML = """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>开放平台开发者门户</title></head>
<body>
<nav><a data-page="docs">接口文档</a> <a data-page="myApps">我的应用</a>{sdk_nav}</nav>
<main>
  <section data-page="docs">
    <h1>接口文档</h1>
    <aside>接口目录：理赔核验 / 医保结算</aside>
    <article>接口说明、请求参数、响应示例</article>
  </section>
  <section data-page="myApps">
    <h1>我的应用</h1>
    <table>
      <thead><tr><th>应用名称</th><th>AppKey</th><th>状态</th></tr></thead>
      <tbody><tr><td>理赔核验应用</td><td>ak_7f3e…c21</td><td>启用</td></tr></tbody>
    </table>
  </section>{sdk_page}
</main>
</body>
</html>
"""


def portal_html(sdk=False):
    return PORTAL_HTML.format(
        sdk_nav=' <a data-page="sdk">SDK 下载</a>' if sdk else "",
        sdk_page="""
  <section data-page="sdk">
    <h1>SDK 下载</h1>
    <table>
      <thead><tr><th>语言</th><th>版本</th><th>发布日期</th><th>操作</th></tr></thead>
      <tbody><tr><td>Java</td><td>2.3.0</td><td>2026-10-01</td><td><a>下载</a></td></tr></tbody>
    </table>
  </section>""" if sdk else "",
    )


CL_HEAD = """# Changelog

本文件记录产品原型的所有重要变更。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。
"""

# 条目：(Keep a Changelog 类别, 文案)
CL_INIT = ("Added", "初版：机构管理、应用管理两页。")
CL_PORTAL_INIT = ("Added", "初版：接口文档、我的应用两页。")
CL_BACKPORT = ("Added", "回补已上线前端：应用列表行操作新增「复制 AppKey」。")
CL_AUDITS = ("Added", "新增「安全审计 → 审计日志」页面，支持按时间、操作类型、操作人筛选，行内查看操作详情。")
CL_SPACES = ("Changed", "机构列表「关联应用」改为「关联空间」，展示机构加入的数据空间列表。")
CL_RENAME_ONLY = ("Changed", "机构列表「关联应用」改名为「关联空间」，仍展示数量。")
CL_SDK = ("Added", "新增「SDK 下载」页。")


def line(name, entry):
    """多产品线共用 CHANGELOG 时，条目以 **<Line>**： 前缀标明所属产品线。"""
    return entry[0], f"**{name}**：{entry[1]}"


def changelog(unreleased=(), *released):
    """unreleased: [条目]；released: (版本标签, 日期, [条目])，新版本在前。"""
    def body(entries):
        out = ""
        for kind in ("Added", "Changed", "Removed"):
            items = [text for k, text in entries if k == kind]
            if items:
                out += f"\n### {kind}\n\n" + "".join(f"- {t}\n" for t in items)
        return out

    text = CL_HEAD + "\n## [Unreleased]\n" + body(unreleased)
    for label, date, entries in released:
        text += f"\n## [{label}] - {date}\n" + body(entries)
    return text


# 迁移前的旧格式：按日期分节，没有 [Unreleased]
CL_LEGACY = """# 原型变更记录

## 2026-09-01

- 初版：机构管理、应用管理两页。
"""
CL_LEGACY_AUDITS = CL_LEGACY + """
## 2026-10-15

- 新增「安全审计 → 审计日志」页面，支持按时间、操作类型、操作人筛选，行内查看操作详情。
- 机构列表「关联应用」改为「关联空间」，展示机构加入的数据空间列表。
"""

# 版本日期与 init.sh 中对应 step 的提交日期一致
CL_V1 = ("V1", "2026-10-01", [CL_INIT])
CL_V2_RENAME = ("V2", "2026-10-02", [CL_RENAME_ONLY])
CL_MULTI_V1 = [("Console V1", "2026-10-01", [CL_INIT]), ("Portal V1", "2026-10-01", [CL_PORTAL_INIT])]


def orgs_section(field, provenance=None):
    rows = {
        "关联应用": "| 关联应用 | 数字 | 3 | 否 | 该机构下的应用数量 |",
        "关联空间-count": "| 关联空间 | 数字 | 2 | 否 | 该机构加入的数据空间数量 |",
    }[field]
    tail = f"\n\n> 来源：{provenance}" if provenance else ""
    return f"""### 4.1 机构管理

**标识**：id `orgs` · 路由 `console/orgs` · 入口：侧边导航「客户管理 → 机构管理」

**目标**：查看接入机构并管理其启停状态。

**布局骨架**：顶部筛选区（机构名称 + 状态下拉 + 查询/重置）→ 主表格。

**数据与字段**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 机构名称 | 文本 | 华东理赔服务中心 | 否 | — |
| 统一社会信用代码 | 文本 | 91310000MA1FL0XXXX | 否 | — |
{rows}
| 状态 | 枚举 | 正常 / 已停用 | 否 | — |

**操作**：

| 操作 | 触发位置 | 前置条件 | 结果 | 二次确认 |
|---|---|---|---|---|
| 查看 | 行操作 | 无 | 打开机构详情抽屉 | 否 |
| 停用 | 行操作 | 状态为正常 | 机构及其全部应用停止调用 | 是 |

**状态与流转**：

- 空态：暂无机构
- 加载：表格骨架屏
- 无权限：菜单不可见
- 错误：顶部 toast 显示失败原因
- 极值：机构名称超 30 字截断并 tooltip
- 流转：点击「查看」打开详情抽屉{tail}"""


def apps_section(provenance=None):
    tail = f"\n\n> 来源：{provenance}" if provenance else ""
    return f"""### 4.2 应用管理

**标识**：id `apps` · 路由 `console/apps` · 入口：侧边导航「客户管理 → 应用管理」

**目标**：创建机构应用并管理其密钥与启停状态。

**布局骨架**：顶部筛选区（应用名称 + 状态下拉 + 查询/重置，右侧「新建应用」主按钮）→ 主表格 → 右侧新建/编辑抽屉。

**数据与字段**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 应用名称 | 文本 | 理赔核验应用 | 是 | 最长 40 字 |
| 所属机构 | 枚举 | 华东理赔服务中心 | 是 | 仅新建时可选 |
| AppKey | 文本 | ak_7f3e…c21 | 否 | 列表中脱敏展示 |
| 回调地址 | URL | https://example.com/callback | 是 | 选填 |
| 状态 | 枚举 | 启用 / 停用 | 否 | 停用后不可调用 |
| 创建时间 | 时间 | 2026-08-12 10:24 | 否 | — |

**操作**：

| 操作 | 触发位置 | 前置条件 | 结果 | 二次确认 |
|---|---|---|---|---|
| 新建应用 | 筛选区右侧主按钮 | 无 | 打开新建抽屉 | 否 |
| 编辑 | 行操作 | 无 | 打开编辑抽屉 | 否 |
| 重置密钥 | 行操作 | 状态为启用 | 生成新密钥并一次性展示 | 是，需输入应用名称 |
| 停用 | 行操作 | 状态为启用 | 应用停止调用 | 是 |

**状态与流转**：

- 空态：暂无应用，提供「新建应用」按钮
- 加载：表格骨架屏
- 无权限：菜单不可见
- 错误：顶部 toast 显示失败原因
- 极值：应用名称超 20 字截断并 tooltip
- 流转：保存成功后关闭抽屉并刷新列表{tail}"""


def console_body(field="关联应用", prov=None, terms_extra=""):
    prov = prov or {}
    return f"""## 一、产品定位与角色

开放平台控制台供平台运营人员管理接入机构及其应用，保障机构应用安全调用开放接口。

### 角色权限矩阵

| 角色 | 机构管理 | 应用管理 |
|---|---|---|
| 平台管理员 | 可写 | 可写 |
| 运营人员 | 只读 | 可写 |

## 二、信息架构

```
客户管理
  ├─ 机构管理            (id: orgs)
  └─ 应用管理            (id: apps)
```

## 三、全局约定

### 布局骨架

左侧固定导航，右侧内容区；内容区自上而下为页面标题、筛选区、主表格。

### 列表页通用模式

筛选区在表格上方，提供查询与重置；分页位于表格底部，每页 20 条；行操作位于最后一列。

### 详情与表单通用模式

新建与编辑使用右侧抽屉；提交时校验必填项，保存成功后关闭抽屉并刷新列表。

### 状态与反馈通则

| 情形 | 表现 |
|---|---|
| 加载中 | 表格骨架屏 |
| 空数据 | 一句话提示 + 主操作按钮 |
| 无权限 | 菜单不可见 |
| 操作成功 | 顶部 toast，3 秒后消失 |
| 操作失败 | 顶部 toast 显示失败原因 |

### 权限可见性规则

无写权限时隐藏写操作按钮。

## 四、页面规格

{orgs_section(field, prov.get("orgs"))}

{apps_section(prov.get("apps"))}

## 五、关键流程

### 5.1 新建应用

1. 运营人员在应用管理点击「新建应用」
2. 填写应用名称、所属机构、回调地址并保存
3. 系统生成 AppKey，应用状态为启用
4. 结束态：列表出现新应用

## 六、术语表

| 中文 | 英文 / id | 定义 | 备注 |
|---|---|---|---|
| 机构 | org | 接入开放平台的企业或单位 | — |
| 应用 | app | 机构调用开放接口的凭证主体 | — |
| AppKey | appKey | 应用的调用标识 | —{terms_extra} |

## 七、明确不做

- **不做批量导入应用**：应用数量少，逐个创建即可
- 界面上**不要**出现面包屑：导航只有两级
- 已否决：机构自助注册：机构由运营人员线下审核后录入
"""


def v1(product="console", status="active", body=None, title="控制台功能基线"):
    return f"""---
product: {product}
version: 1
slug: baseline
title: {title}
type: baseline
status: {status}
created: 2026-09-02
---

# V1 · {title}

{body or console_body()}"""


def current(product, versions, body, title, generator="fspec", comment=None):
    comment = comment or "<!-- GENERATED by fspec — 勿手改。要改内容请新增 V 文件。 -->"
    return f"""{comment}
---
product: {product}
synthesized_from: [{", ".join(map(str, versions))}]
generated: 2026-09-02
generator: {generator}
---

# {title}功能规格说明书（当前态）

{body}"""


CONSOLE_CURRENT_V1 = current("console", [1], console_body(prov={"orgs": "V1", "apps": "V1"}), "控制台")

AUDIT_PAGE_SPEC = """### 3.1 审计日志

**标识**：id `audits` · 路由 `console/audits` · 入口：侧边导航「安全审计 → 审计日志」

**目标**：追溯运营人员对机构与应用的关键操作。

**布局骨架**：顶部筛选区（时间范围 + 操作类型下拉 + 操作人 + 查询/重置）→ 主表格 → 右侧操作详情抽屉。

**数据与字段**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 时间 | 时间 | 2026-10-18 14:02:11 | 否 | 精确到秒 |
| 操作人 | 文本 | 王敏 | 否 | — |
| 操作类型 | 枚举 | 新建应用 / 重置密钥 / 停用应用 / 停用机构 | 否 | — |
| 操作对象 | 文本 | 理赔核验应用 | 否 | — |
| 结果 | 枚举 | 成功 / 失败 | 否 | — |

**操作**：

| 操作 | 触发位置 | 前置条件 | 结果 | 二次确认 |
|---|---|---|---|---|
| 查看详情 | 行操作 | 无 | 打开详情抽屉，展示变更前后与来源 IP | 否 |

**状态与流转**：

- 空态：所选时间范围内暂无操作记录
- 加载：表格骨架屏
- 无权限：菜单不可见
- 错误：顶部 toast 显示失败原因
- 极值：默认查询最近 7 天，时间范围最长 90 天
- 流转：无跳转"""

V2_DRAFT_AUDIT = f"""---
product: console
version: 2
slug: audit_log
title: 新增审计日志并改为关联空间
type: change
status: draft
created: 2026-10-20
---

# V2 · 新增审计日志并改为关联空间

## 一、变更摘要

新增审计日志页；机构列表的「关联应用」改为「关联空间」。

**动机**：监管检查要求可追溯每次密钥重置与停用操作；机构改按数据空间组织应用。

## 二、变更清单

| 操作 | 定位符 | 说明 |
|---|---|---|
| `ADD` | `nav.安全审计` | 新增导航分组 |
| `ADD` | `nav.安全审计.audits` | 新增「审计日志」导航项 |
| `ADD` | `page.audits` | 新增「审计日志」页面 |
| `RENAME` | `page.orgs.fields.关联应用` | 改叫「关联空间」 |
| `MODIFY` | `page.orgs.fields.关联空间` | 由应用数量改为展示空间名称列表 |
| `ADD` | `term.数据空间` | 新增术语 |

## 三、新增页面规格

{AUDIT_PAGE_SPEC}

## 四、修改的页面

### 4.1 机构管理（`page.orgs`）

**替换「数据与字段」小节中的该行**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 关联空间 | 列表 | 系统空间、理赔空间 | 否 | 该机构加入的数据空间 |

## 五、流程与术语变更

**术语新增**：

| 中文 | 英文 / id | 定义 |
|---|---|---|
| 数据空间 | dataSpace | 机构之间共享数据的协作单元 |

## 六、影响面

- `page.apps`：本次不改
"""

V2_ACTIVE_RENAME = """---
product: console
version: 2
slug: data_space
title: 关联应用改为关联空间
type: change
status: active
created: 2026-09-21
---

# V2 · 关联应用改为关联空间

## 一、变更摘要

机构列表「关联应用」改名为「关联空间」，仍展示数量。

**动机**：机构改按数据空间组织应用。

## 二、变更清单

| 操作 | 定位符 | 说明 |
|---|---|---|
| `RENAME` | `page.orgs.fields.关联应用` | 改叫「关联空间」 |
| `MODIFY` | `page.orgs.fields.关联空间` | 说明改为「该机构加入的数据空间数量」 |

## 三、新增页面规格

无

## 四、修改的页面

### 4.1 机构管理（`page.orgs`）

**替换「数据与字段」小节中的该行**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 关联空间 | 数字 | 2 | 否 | 该机构加入的数据空间数量 |

## 五、流程与术语变更

无

## 六、影响面

无
"""

SPEC_APP_CONSOLE = """# 开放平台控制台：机构与应用管理

Status: ready-for-agent

## Problem Statement

平台运营人员目前靠表格和邮件登记接入机构及其应用，密钥发放与停用全靠人工，经常出现停用机构后应用仍可调用的情况。

## Solution

提供运营控制台：运营人员在控制台中维护机构、为机构创建应用并管理密钥与启停状态。

## User Stories

1. As a 平台管理员, I want 按名称和状态筛选机构, so that 快速找到要处理的机构
2. As a 平台管理员, I want 停用机构, so that 该机构的全部应用立即停止调用
3. As a 运营人员, I want 为机构新建应用, so that 机构拿到 AppKey 后即可接入
4. As a 运营人员, I want 重置应用密钥, so that 密钥泄露时能立即止损
5. As a 运营人员, I want 停用应用, so that 不再使用的应用无法调用接口
6. As a 运营人员, I want 编辑应用名称和回调地址, so that 信息变化时能及时更正

## Implementation Decisions

- 机构与应用两个模块；应用归属唯一机构，创建后不可变更归属。
- 停用机构级联停用其下全部应用。
- 重置密钥后旧密钥立即失效，新密钥只展示一次。

## Testing Decisions

- 只测外部行为：通过控制台 API 验证停用级联与密钥失效。

## Out of Scope

- 批量导入应用。
- 应用调用量统计看板。

## Further Notes

无。
"""

SPEC_AUDIT = """# 审计日志与数据空间

Status: ready-for-agent

## Problem Statement

监管检查要求能追溯每一次密钥重置、应用停用与机构停用，但控制台目前没有任何操作记录；另外机构已改为按数据空间组织应用，列表里的「关联应用」数量不再有意义。

## Solution

新增审计日志页，记录关键操作并支持筛选与查看详情；机构列表改为展示机构加入的数据空间。

## User Stories

1. As a 平台管理员, I want 按时间范围、操作类型和操作人筛选审计日志, so that 迎检时快速定位记录
2. As a 平台管理员, I want 查看一次操作的变更前后与来源 IP, so that 判断操作是否合规
3. As a 运营人员, I want 在机构列表看到机构加入的数据空间, so that 不必逐个点开详情

## Implementation Decisions

- 审计记录只追加、不可删除，保留 180 天。
- 审计日志页只读。

## Testing Decisions

- 通过 API 验证每类关键操作都会产生一条审计记录。

## Out of Scope

- 导出审计日志。
- 审计告警推送。

## Further Notes

无。
"""

PORTAL_BODY = """## 一、产品定位与角色

开发者门户供接入机构的开发者查阅接口文档、查看自己的应用。

### 角色权限矩阵

| 角色 | 接口文档 | 我的应用 |
|---|---|---|
| 开发者 | 可见 | 只读 |

## 二、信息架构

```
门户
  ├─ 接口文档            (id: docs)
  └─ 我的应用            (id: myApps)
```

## 三、全局约定

### 布局骨架

顶部导航，下方内容区。

### 列表页通用模式

无分页，单页展示。

### 详情与表单通用模式

无表单。

### 状态与反馈通则

| 情形 | 表现 |
|---|---|
| 加载中 | 骨架屏 |
| 空数据 | 一句话提示 |

### 权限可见性规则

未登录只能看接口文档。

## 四、页面规格

### 4.1 接口文档

**标识**：id `docs` · 路由 `portal/docs` · 入口：顶部导航「接口文档」

**目标**：查阅接口说明。

**布局骨架**：左侧接口目录 → 右侧文档正文。

**数据与字段**：无

**操作**：无

**状态与流转**：

- 空态：无
- 流转：点击目录切换正文

> 来源：V1

### 4.2 我的应用

**标识**：id `myApps` · 路由 `portal/apps` · 入口：顶部导航「我的应用」

**目标**：查看本机构应用与 AppKey。

**布局骨架**：主表格。

**数据与字段**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 应用名称 | 文本 | 理赔核验应用 | 否 | — |
| AppKey | 文本 | ak_7f3e…c21 | 否 | 脱敏 |
| 状态 | 枚举 | 启用 / 停用 | 否 | — |

**操作**：无

**状态与流转**：

- 空态：暂无应用，请联系平台运营开通
- 流转：无

> 来源：V1

## 五、关键流程

无

## 六、术语表

| 中文 | 英文 / id | 定义 | 备注 |
|---|---|---|---|
| 应用 | app | 机构调用开放接口的凭证主体 | — |

## 七、明确不做

- **不做在线调试**：首期只提供文档
"""


def write(base, rel, text):
    p = os.path.join(base, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


def step(fixture, n, slug, files):
    """slug 用英文 kebab-case；init.sh 把它转成提交信息。"""
    base = os.path.join(OUT, fixture, "steps", f"{n:02d}-{slug}")
    for rel, text in files.items():
        write(base, rel, text)


PROTO = "products/prototype/console/index.html"
PORTAL = "products/prototype/portal/index.html"
PCL = "products/prototype/CHANGELOG.md"
FS = "products/fspec/console/"

# 移除旧的 fixture 目录（只动本脚本生成的那些）
FIXTURES = ["greenfield", "incremental", "merge-draft", "legacy-changelog", "multi-line", "legacy-specs", "no-change", "stale-current"]
for name in FIXTURES:
    shutil.rmtree(os.path.join(OUT, name), ignore_errors=True)

baseline_files = {
    "CLAUDE.md": CLAUDE_MD,
    PROTO: console_html(),
    PCL: changelog((), CL_V1),
    FS + "V1__baseline.md": v1(),
    FS + "CURRENT.md": CONSOLE_CURRENT_V1,
}

# 0→1：只有原型和 spec，没有任何功能规格；原型改动都还在 [Unreleased]
step("greenfield", 1, "finalize-prototype", {
    "CLAUDE.md": CLAUDE_MD,
    PROTO: console_html(),
    PCL: changelog([CL_INIT]),
    ".scratch/app-console/spec.md": SPEC_APP_CONSOLE,
})

# 1→2：V1 之后先回补前端漂移，再加新功能
step("incremental", 1, "prototype-and-fspec-baseline", baseline_files)
step("incremental", 2, "backport-copy-appkey", {
    PROTO: console_html(backport=True),
    PCL: changelog([CL_BACKPORT], CL_V1),
})
step("incremental", 3, "add-audit-log-and-data-spaces", {
    PROTO: console_html(backport=True, audits=True, spaces="list"),
    PCL: changelog([CL_BACKPORT, CL_AUDITS, CL_SPACES], CL_V1),
    ".scratch/audit-log/spec.md": SPEC_AUDIT,
})

# 已有 draft V2 等待确认
step("merge-draft", 1, "prototype-and-fspec-baseline", baseline_files)
step("merge-draft", 2, "add-audit-log-and-draft-v2", {
    PROTO: console_html(audits=True, spaces="list"),
    PCL: changelog([CL_AUDITS, CL_SPACES], CL_V1),
    FS + "V2__audit_log.md": V2_DRAFT_AUDIT,
})

# 原型 CHANGELOG 仍是旧格式（无 [Unreleased]），确认 draft V2 时不得改写它
legacy_cl_baseline = dict(baseline_files)
legacy_cl_baseline[PCL] = CL_LEGACY
step("legacy-changelog", 1, "prototype-and-fspec-baseline", legacy_cl_baseline)
step("legacy-changelog", 2, "add-audit-log-and-draft-v2", {
    PROTO: console_html(audits=True, spaces="list"),
    PCL: CL_LEGACY_AUDITS,
    FS + "V2__audit_log.md": V2_DRAFT_AUDIT,
})

# 两条产品线共用原型 CHANGELOG，版本标签带产品线
multi1 = dict(baseline_files)
multi1["CLAUDE.md"] = CLAUDE_MD_MULTI
multi1[PORTAL] = portal_html()
multi1[PCL] = changelog((), *CL_MULTI_V1)
multi1["products/fspec/portal/V1__baseline.md"] = v1("portal", body=PORTAL_BODY.replace("\n> 来源：V1\n", ""), title="开发者门户功能基线")
multi1["products/fspec/portal/CURRENT.md"] = current("portal", [1], PORTAL_BODY, "开发者门户")

# 两条产品线都有原型改动，未指明哪条
step("multi-line", 1, "two-product-line-baselines", multi1)
step("multi-line", 2, "update-both-prototypes", {
    PROTO: console_html(backport=True),
    PORTAL: portal_html(sdk=True),
    PCL: changelog([line("Console", CL_BACKPORT), line("Portal", CL_SDK)], *CL_MULTI_V1),
})

# 旧 product-spec 目录布局
legacy_current = current(
    "console", [1], console_body(prov={"orgs": "V1", "apps": "V1"}), "控制台",
    generator="product-spec skill",
    comment="<!-- GENERATED by product-spec sync — 勿手改。要改内容请新增 V 文件后重新 sync。 -->",
)
step("legacy-specs", 1, "prototype-and-fspec-baseline", {
    "CLAUDE.md": CLAUDE_MD,
    PROTO: console_html(),
    PCL: changelog((), CL_V1),
    "products/specs/console/V1__baseline.md": v1(),
    "products/specs/console/CURRENT.md": legacy_current,
})
step("legacy-specs", 2, "add-audit-log", {
    PROTO: console_html(audits=True),
    PCL: changelog([CL_AUDITS], CL_V1),
})

# V2 已 active，但 CURRENT.md 还停在 [1]
step("stale-current", 1, "prototype-and-fspec-baseline", baseline_files)
step("stale-current", 2, "rename-to-data-spaces", {
    PROTO: console_html(spaces="count"),
    PCL: changelog((), CL_V2_RENAME, CL_V1),
    FS + "V2__data_space.md": V2_ACTIVE_RENAME,
})

# V1 之后原型没有变化
step("no-change", 1, "prototype-and-fspec-baseline", baseline_files)
print("ok")
