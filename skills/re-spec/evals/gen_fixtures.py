"""生成 re-spec eval fixture：evals/files/<fixture>/steps/NN-<slug>/ 叠加目录。"""
import os
import shutil
import sys

OUT = sys.argv[1]

CLAUDE_MD = """# Project Conventions

- Outward product name: 「开放平台」. Never show the internal codename Hermes in any outward document or UI copy.
- Frontend apps: `console` (运营控制台).
- Issue tracker: {tracker}.
"""

# matt to-spec 模板的审计日志 spec；故意与 V2 存在偏差
MATT_SPEC = """# 审计日志与数据空间

Status: ready-for-agent

## Problem Statement

监管检查要求能追溯每一次密钥重置、应用停用与机构停用，但控制台目前没有任何操作记录；另外机构已改为按数据空间组织应用，列表里的「关联应用」数量不再有意义。

## Solution

新增审计日志页，记录关键操作并支持筛选与查看详情；机构列表改为展示机构加入的数据空间。

## User Stories

1. As a 平台管理员, I want 按时间范围筛选审计日志, so that 迎检时快速定位记录
2. As a 平台管理员, I want 查看一次操作的变更前后, so that 判断操作是否合规
3. As a 平台管理员, I want 把筛选结果导出为 Excel, so that 提交给检查组
4. As a 运营人员, I want 在机构列表看到机构的关联应用数量, so that 了解机构接入规模

## Implementation Decisions

- 审计记录只追加、不可删除，保留 180 天。
- 新增审计记录模块，关键操作完成后同步写入一条记录。

## Testing Decisions

- 通过 API 验证每类关键操作都会产生一条审计记录。

## Out of Scope

- 审计告警推送。

## Further Notes

无。
"""

MATT_COMMENTS = """
## Comments

- to-spec：创建 spec，见 .scratch/audit-log/spec.md。
"""

SP_SPEC = """# m2 · 审计日志 设计

**Status:** reviewed

## Goal

满足监管迎检：控制台可追溯密钥重置、应用停用与机构停用等关键操作。

## User-facing Behavior

- 平台管理员在「安全审计 → 审计日志」按时间范围筛选记录。
- 点击记录查看变更前后。
- 平台管理员可批量删除过期审计记录，避免列表过长。

## Architecture & Decisions

- 审计记录只追加，保留 90 天后归档到对象存储。
- 审计写入与业务操作在同一事务内完成。

## Testing

- 集成测试：每类关键操作写入一条审计记录。

## Non-goals

- 审计告警推送。
"""

V1 = """---
product: console
version: 1
slug: baseline
title: 控制台功能基线
type: baseline
status: active
created: 2026-09-02
---

# V1 · 控制台功能基线

## 一、产品定位与角色

开放平台控制台供平台运营人员管理接入机构及其应用。

## 二、信息架构

```
客户管理
  ├─ 机构管理            (id: orgs)
  └─ 应用管理            (id: apps)
```

## 三、全局约定

列表页筛选区在表格上方；无写权限时隐藏写操作按钮。

## 四、页面规格

### 4.1 机构管理

**标识**：id `orgs` · 路由 `console/orgs`

**目标**：查看接入机构并管理其启停状态。

**布局骨架**：筛选区 → 主表格。

**数据与字段**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 机构名称 | 文本 | 华东理赔服务中心 | 否 | — |
| 关联应用 | 数字 | 3 | 否 | 该机构下的应用数量 |
| 状态 | 枚举 | 正常 / 已停用 | 否 | — |

**操作**：

| 操作 | 触发位置 | 前置条件 | 结果 | 二次确认 |
|---|---|---|---|---|
| 停用 | 行操作 | 状态为正常 | 机构及其全部应用停止调用 | 是 |

**状态与流转**：空态「暂无机构」；加载骨架屏。

### 4.2 应用管理

**标识**：id `apps` · 路由 `console/apps`

**目标**：创建机构应用并管理其密钥与启停状态。

**布局骨架**：筛选区 → 主表格 → 新建/编辑抽屉。

**数据与字段**：

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 应用名称 | 文本 | 理赔核验应用 | 是 | 最长 40 字 |
| AppKey | 文本 | ak_7f3e…c21 | 否 | 脱敏展示 |

**操作**：

| 操作 | 触发位置 | 前置条件 | 结果 | 二次确认 |
|---|---|---|---|---|
| 重置密钥 | 行操作 | 状态为启用 | 生成新密钥并一次性展示 | 是 |

**状态与流转**：空态「暂无应用」。

## 五、关键流程

无。

## 六、术语表

| 中文 | 英文 / id | 定义 | 备注 |
|---|---|---|---|
| 机构 | org | 接入开放平台的企业或单位 | — |
| 应用 | app | 机构调用开放接口的凭证主体 | — |

## 七、明确不做

- 机构自助注册：由运营线下审核后录入。
"""

V2_BODY = """
# V2 · 审计日志与数据空间

## 一、变更摘要

新增审计日志页；机构列表「关联应用」改为「关联空间」列表；回补已上线的「复制 AppKey」。

**动机**：监管迎检需要追溯关键操作；机构已按数据空间组织应用。

## 二、变更清单

| 操作 | 定位 | 说明 |
|---|---|---|
| ADD | nav.安全审计 | 新导航分组 |
| ADD | nav.安全审计.audits | 审计日志菜单 |
| ADD | page.audits | 审计日志页，只读 |
| RENAME | page.orgs.fields.关联应用 | 改名为「关联空间」 |
| MODIFY | page.orgs.fields.关联空间 | 由数量改为空间名称列表 |
| ADD | page.apps.actions.复制appkey | 回补已上线前端：行操作复制 AppKey |
| ADD | term.操作类型 | 新术语 |
| ADD | term.数据空间 | 新术语 |
| ADD | donts.导出审计日志 | 原型评审决定不做 |

## 三、新增页面规格

### 审计日志

**标识**：id `audits` · 路由 `console/audits` · 入口：侧边导航「安全审计 → 审计日志」

**目标**：迎检时定位并核查关键操作记录。

**布局骨架**：筛选区（时间范围 + 操作类型 + 操作人 + 查询/重置）→ 主表格 → 右侧详情抽屉。

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
| 查询 | 筛选区 | 无 | 按条件刷新列表 | 否 |
| 查看详情 | 行操作 | 无 | 打开详情抽屉，展示变更前、变更后、来源 IP | 否 |

**状态与流转**：

- 空态：所选时间范围内暂无记录
- 无权限：仅平台管理员可见菜单
- 极值：时间范围最长 180 天，仅可查询近 180 天记录

## 四、修改的页面

### 机构管理 · 数据与字段

| 字段 | 类型 | 示例值 | 可编辑 | 说明 |
|---|---|---|---|---|
| 关联空间 | 列表 | 系统空间、理赔空间 | 否 | 机构加入的数据空间 |

### 应用管理 · 操作

| 操作 | 触发位置 | 前置条件 | 结果 | 二次确认 |
|---|---|---|---|---|
| 复制 AppKey | 行操作 | 无 | 复制完整 AppKey 并提示「已复制」 | 否 |

## 五、流程与术语变更

| 中文 | 英文 / id | 定义 | 备注 |
|---|---|---|---|
| 操作类型 | actionType | 审计记录对应的关键操作 | — |
| 数据空间 | dataSpace | 机构组织应用与数据的隔离单元 | — |

明确不做新增：

- 导出审计日志：原型评审决定迎检以页面筛选核查为准，不提供导出。

## 六、影响面

无。
"""


def v2(status="active"):
    return f"""---
product: console
version: 2
slug: audit_log
title: 审计日志与数据空间
type: change
status: {status}
created: 2026-10-02
---
{V2_BODY}"""


def current(versions):
    body = V1.split("---\n", 2)[2].replace("# V1 · 控制台功能基线", "# 控制台功能规格（当前）")
    if 2 in versions:
        # 按 V2 变更清单合并：导航、审计页、字段改名、回补操作、术语、明确不做
        audits = V2_BODY.split("### 审计日志\n", 1)[1].split("## 四、修改的页面", 1)[0]
        body = body.replace("  └─ 应用管理            (id: apps)\n", "  └─ 应用管理            (id: apps)\n安全审计\n  └─ 审计日志            (id: audits)\n")
        body = body.replace("| 关联应用 | 数字 | 3 | 否 | 该机构下的应用数量 |", "| 关联空间 | 列表 | 系统空间、理赔空间 | 否 | 机构加入的数据空间 |")
        body = body.replace("| 重置密钥 | 行操作 | 状态为启用 | 生成新密钥并一次性展示 | 是 |", "| 复制 AppKey | 行操作 | 无 | 复制完整 AppKey 并提示「已复制」 | 否 |\n| 重置密钥 | 行操作 | 状态为启用 | 生成新密钥并一次性展示 | 是 |")
        body = body.replace("## 五、关键流程", "### 4.3 审计日志\n\n" + audits.strip() + "\n\n## 五、关键流程")
        body = body.replace("| 应用 | app | 机构调用开放接口的凭证主体 | — |", "| 应用 | app | 机构调用开放接口的凭证主体 | — |\n| 操作类型 | actionType | 审计记录对应的关键操作 | — |\n| 数据空间 | dataSpace | 机构组织应用与数据的隔离单元 | — |")
        body = body.replace("- 机构自助注册：由运营线下审核后录入。", "- 机构自助注册：由运营线下审核后录入。\n- 导出审计日志：原型评审决定迎检以页面筛选核查为准，不提供导出。")
    return f"""<!-- GENERATED by fspec — 勿手改。要改内容请新增 V 文件。 -->
---
product: console
synthesized_from: {list(versions)}
generated: 2026-10-02
generator: fspec
---
{body}"""


# 伪造 gh：view 返回 issue 正文与评论，其余调用记入 .gh-calls.log
GH_STUB = """#!/bin/sh
# eval 用 gh 桩：只模拟 issue 12，所有调用记入 .gh-calls.log
echo "gh $*" >> "$(dirname "$0")/../.gh-calls.log"
case "$1 $2" in
  "issue view")
    cat "$(dirname "$0")/../.gh-fixture/issue-12.md"
    ;;
  "issue edit"|"issue comment")
    echo "https://github.com/acme/open-platform/issues/12"
    ;;
  *)
    echo "gh stub: unsupported: $*" >&2
    exit 1
    ;;
esac
"""

GH_ISSUE = """title:	审计日志与数据空间
state:	OPEN
author:	pm-li
labels:	ready-for-agent
number:	12
--
""" + MATT_SPEC.split("Status: ready-for-agent\n\n", 1)[1] + """
author:	pm-li
association:	owner
created:	2026-09-25T10:00:00Z
--
to-spec：创建 spec。
--
"""


def write(base, rel, text, mode=None):
    p = os.path.join(base, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)
    if mode:
        os.chmod(p, mode)


def step(fixture, n, slug, files):
    base = os.path.join(OUT, fixture, "steps", f"{n:02d}-{slug}")
    for rel, text in files.items():
        if isinstance(text, tuple):
            write(base, rel, *text)
        else:
            write(base, rel, text)


def baseline(tracker="local markdown under `.scratch/`"):
    return {
        "CLAUDE.md": CLAUDE_MD.format(tracker=tracker),
        "products/fspec/console/V1__baseline.md": V1,
        "products/fspec/console/CURRENT.md": current([1]),
    }


def v2_files(status="active"):
    files = {"products/fspec/console/V2__audit_log.md": v2(status)}
    if status == "active":
        files["products/fspec/console/CURRENT.md"] = current([1, 2])
    return files


def matt_local():
    step("matt-local", 1, "baseline-and-audit-log-spec", {**baseline(), ".scratch/audit-log/spec.md": MATT_SPEC + MATT_COMMENTS})
    step("matt-local", 2, "fspec-v2-audit-log", v2_files())


def superpowers():
    step("superpowers", 1, "baseline-and-reviewed-spec", {
        **baseline("none; specs under `docs/superpowers/specs/`"),
        "docs/superpowers/specs/m2-audit-log.SPEC.md": SP_SPEC,
    })
    step("superpowers", 2, "fspec-v2-audit-log", v2_files())


def draft_v():
    step("draft-v", 1, "baseline-and-audit-log-spec", {**baseline(), ".scratch/audit-log/spec.md": MATT_SPEC + MATT_COMMENTS})
    step("draft-v", 2, "fspec-v2-draft", v2_files("draft"))


def github():
    step("github", 1, "baseline-and-gh-stub", {
        **baseline("GitHub Issues (acme/open-platform), via `gh`"),
        "bin/gh": (GH_STUB, 0o755),
        ".gh-fixture/issue-12.md": GH_ISSUE,
    })
    step("github", 2, "fspec-v2-audit-log", v2_files())


def aligned():
    # spec 修订提交晚于 V2，已对齐
    aligned_spec = MATT_SPEC.replace(
        "1. As a 平台管理员, I want 按时间范围筛选审计日志", "1. As a 平台管理员, I want 按时间范围、操作类型和操作人筛选审计日志"
    ).replace(
        "3. As a 平台管理员, I want 把筛选结果导出为 Excel, so that 提交给检查组\n4. As a 运营人员, I want 在机构列表看到机构的关联应用数量, so that 了解机构接入规模",
        "3. As a 运营人员, I want 在机构列表看到机构加入的数据空间, so that 了解机构接入范围",
    ).replace("- 审计告警推送。", "- 审计告警推送。\n- 导出审计日志：原型评审决定迎检以页面筛选核查为准。").replace(
        "## Further Notes\n\n无。", "## Further Notes\n\n界面细节以 products/fspec/console/CURRENT.md 为准（V2）。"
    )
    step("aligned", 1, "baseline-and-audit-log-spec", {**baseline(), ".scratch/audit-log/spec.md": MATT_SPEC + MATT_COMMENTS})
    step("aligned", 2, "fspec-v2-audit-log", v2_files())
    step("aligned", 3, "re-spec-audit-log", {
        ".scratch/audit-log/spec.md": aligned_spec + MATT_COMMENTS + "- re-spec：依据 products/fspec/console/V2__audit_log.md 修订 User Stories、Out of Scope、Further Notes。\n",
    })


if __name__ == "__main__":
    fixtures = {"matt-local": matt_local, "superpowers": superpowers, "draft-v": draft_v, "github": github, "aligned": aligned}
    for name, fn in fixtures.items():
        shutil.rmtree(os.path.join(OUT, name), ignore_errors=True)
        fn()
