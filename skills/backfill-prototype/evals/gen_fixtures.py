"""生成 backfill-prototype eval fixture：evals/files/<fixture>/steps/NN-<slug>/ 叠加目录。"""
import os
import shutil
import sys

OUT = sys.argv[1]

CLAUDE_MD = """# Project Conventions

- Outward product name: 「开放平台」. Never show the internal codename Hermes in any outward document or UI copy.
- Frontend apps: `apps/console` (运营控制台){extra}.
"""

DESIGN_MD = """---
name: 开放平台
colors:
  primary: "#1A66E0"
  danger: "#C62828"
  text: "#1F2328"
rounded:
  md: 8px
---

# 开放平台设计系统

主按钮使用 primary，失败状态使用 danger。
"""

DESIGN_MD_RESTYLE = """---
name: 开放平台 · 暖色
colors:
  primary: "#C2410C"
  danger: "#B91C1C"
  text: "#292524"
rounded:
  md: 14px
---

# 开放平台设计系统（restyle 作者版）

暖色系、大圆角；结构沿用原型。
"""


def changelog(unreleased=(), released="## [V1] - 2026-10-01\n\n### Added\n\n- 初版：机构管理、应用管理两页。\n"):
    """unreleased: (group, entry) 列表，按 Keep a Changelog 分组。"""
    out = "# Changelog\n\n本文件记录产品原型的所有重要变更。\n\n格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。\n\n## [Unreleased]\n"
    groups = {}
    for g, e in unreleased:
        groups.setdefault(g, []).append(e)
    for g, es in groups.items():
        out += f"\n### {g}\n\n" + "".join(f"- {e}\n" for e in es)
    return out + "\n" + released


def console_html(org_status="停用", audits=False, bulk_disable=False):
    """org_status: 机构状态下拉文案；audits: 含待开发的审计日志页；bulk_disable: 原型独有的批量停用按钮。"""
    audit_nav = """
    <div class="group">安全审计
      <a data-page="audits">审计日志</a>
    </div>""" if audits else ""
    audit_page = """
  <section data-page="audits">
    <h1>审计日志</h1>
    <table>
      <thead><tr><th>时间</th><th>操作人</th><th>操作类型</th><th>操作对象</th></tr></thead>
      <tbody><tr><td>2026-10-18 14:02</td><td>王敏</td><td>重置密钥</td><td>理赔核验应用</td></tr></tbody>
    </table>
  </section>""" if audits else ""
    bulk = '<button>批量停用</button>' if bulk_disable else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>开放平台控制台</title>
<style>
  body {{ font-family: "PingFang SC"; color: #1F2328; }}
  .primary {{ background: #1F6FEB; color: #fff; border-radius: 6px; }}
  .tag-fail {{ color: #CF222E; }}
</style>
</head>
<body>
<aside>
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
      <select><option>全部状态</option><option>正常</option><option>已{org_status}</option></select>
      <button>查询</button><button>重置</button>
    </form>
    <table>
      <thead><tr><th>机构名称</th><th>统一社会信用代码</th><th>状态</th><th>操作</th></tr></thead>
      <tbody><tr><td>华东理赔服务中心</td><td>91310000MA1FL0XXXX</td><td>正常</td><td><a>查看</a> <a>停用</a></td></tr></tbody>
    </table>
  </section>
  <section data-page="apps">
    <h1>应用管理</h1>
    <form class="filters">
      <input placeholder="应用名称">
      <select><option>全部状态</option><option>启用</option><option>停用</option></select>
      <button>查询</button><button>重置</button>
      <button class="primary">新建应用</button>{bulk}
    </form>
    <table>
      <thead><tr><th>应用名称</th><th>所属机构</th><th>AppKey</th><th>状态</th><th>创建时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr><td>理赔核验应用</td><td>华东理赔服务中心</td><td>ak_7f3e…c21</td><td>启用</td><td>2026-08-12 10:24</td><td><a>编辑</a> <a>重置密钥</a> <a>停用</a></td></tr>
        <tr><td>医保结算应用</td><td>华南医保结算中心</td><td>ak_19ab…e07</td><td class="tag-fail">停用</td><td>2026-08-20 16:05</td><td><a>编辑</a> <a>重置密钥</a> <a>停用</a></td></tr>
      </tbody>
    </table>
  </section>{audit_page}
</main>
</body>
</html>
"""


def portal_html():
    return """<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>开放平台开发者门户</title></head>
<body>
<nav><a data-page="docs">接口文档</a></nav>
<main>
  <section data-page="docs">
    <h1>接口文档</h1>
    <ul><li>鉴权</li><li>理赔核验</li></ul>
  </section>
</main>
</body>
</html>
"""


def orgs_tsx(org_status="停用", restyle=False):
    badge = "rounded-md bg-primary/10" if not restyle else "rounded-[var(--radius-md)] bg-primary/15 font-medium"
    return f"""import {{ Button }} from '@/components/ui/button';
import {{ Input }} from '@/components/ui/input';
import {{ Select }} from '@/components/ui/select';
import {{ DataTable }} from '@/components/common/data-table';
import {{ useOrgs }} from '@/hooks/use-orgs';

// 机构管理页，page id: orgs
export function OrgsPage() {{
  const {{ data, loading }} = useOrgs();
  return (
    <div className="space-y-4">
      <h1 className="text-xl">机构管理</h1>
      <form className="flex gap-2">
        <Input placeholder="机构名称" />
        <Select options={{['全部状态', '正常', '已{org_status}']}} />
        <Button>查询</Button>
        <Button variant="outline">重置</Button>
      </form>
      <DataTable
        loading={{loading}}
        rows={{data}}
        columns={{[
          {{ key: 'name', title: '机构名称' }},
          {{ key: 'creditCode', title: '统一社会信用代码' }},
          {{ key: 'status', title: '状态', render: (s) => <span className="{badge}">{{s}}</span> }},
        ]}}
        actions={{[{{ label: '查看' }}, {{ label: '停用' }}]}}
      />
    </div>
  );
}}
"""


def apps_tsx(copy_key=False, last_call=False, guard=False, org_filter=False, restyle=False):
    """copy_key: 行操作「复制 AppKey」；last_call: 「最近调用时间」列；guard: 无写权限隐藏「重置密钥」；org_filter: 「所属机构」筛选。"""
    imports = "import { useAuth } from '@/hooks/use-auth';\n" if guard else ""
    auth = "  const { canWrite } = useAuth();\n" if guard else ""
    reset = "...(canWrite ? [{ label: '重置密钥', confirm: true }] : [])" if guard else "{ label: '重置密钥', confirm: true }"
    copy = "\n          { label: '复制 AppKey', onClick: (row) => navigator.clipboard.writeText(row.appKey) }," if copy_key else ""
    last = "\n          { key: 'lastCalledAt', title: '最近调用时间' }," if last_call else ""
    org_sel = "\n        <Select options={['全部机构', ...orgOptions]} />" if org_filter else ""
    org_hook = "  const orgOptions = useOrgOptions();\n" if org_filter else ""
    org_imp = "import { useOrgOptions } from '@/hooks/use-orgs';\n" if org_filter else ""
    primary = "bg-primary text-primary-foreground" if not restyle else "bg-primary text-primary-foreground rounded-[var(--radius-md)] shadow-sm"
    return f"""import {{ Button }} from '@/components/ui/button';
import {{ Input }} from '@/components/ui/input';
import {{ Select }} from '@/components/ui/select';
import {{ DataTable }} from '@/components/common/data-table';
import {{ useApps }} from '@/hooks/use-apps';
{imports}{org_imp}
// 应用管理页，page id: apps
export function AppsPage() {{
  const {{ data, loading }} = useApps();
{auth}{org_hook}  return (
    <div className="space-y-4">
      <h1 className="text-xl">应用管理</h1>
      <form className="flex gap-2">
        <Input placeholder="应用名称" />{org_sel}
        <Select options={{['全部状态', '启用', '停用']}} />
        <Button>查询</Button>
        <Button variant="outline">重置</Button>
        <Button className="{primary}">新建应用</Button>
      </form>
      <DataTable
        loading={{loading}}
        rows={{data}}
        columns={{[
          {{ key: 'name', title: '应用名称' }},
          {{ key: 'orgName', title: '所属机构' }},
          {{ key: 'appKey', title: 'AppKey', masked: true }},
          {{ key: 'status', title: '状态' }},
          {{ key: 'createdAt', title: '创建时间' }},{last}
        ]}}
        actions={{[
          {{ label: '编辑' }},{copy}
          {reset},
          {{ label: '停用', confirm: true }},
        ]}}
      />
    </div>
  );
}}
"""


def routes_tsx(audits=False):
    return """import { OrgsPage } from '@/pages/orgs';
import { AppsPage } from '@/pages/apps';

// 路由 path 沿用原型 page id
export const routes = [
  { group: '客户管理', path: 'orgs', title: '机构管理', element: <OrgsPage /> },
  { group: '客户管理', path: 'apps', title: '应用管理', element: <AppsPage /> },
];
"""


def api_apps(live=False):
    if live:
        return """import { http } from '@/lib/http';

// 应用列表已接真实接口
export const listApps = () => http.get('/console/apps');
"""
    return """export { listApps } from '@/mocks/apps';
"""


MOCK_APPS = """// 应用 mock 数据
export const listApps = async () => [
  { name: '理赔核验应用', orgName: '华东理赔服务中心', appKey: 'ak_7f3e9c21', status: '启用', createdAt: '2026-08-12 10:24' },
];
"""

MOCK_APPS_RESTYLE = """// 应用 mock 数据（restyle 后换了示例数据）
export const listApps = async () => [
  { name: '车险定损应用', orgName: '西北车险服务中心', appKey: 'ak_0b1d77aa', status: '启用', createdAt: '2026-09-03 08:12' },
];
"""


def index_md(app="console"):
    return f"""# design-to-code index · {app}

| page id | prototype source | selectors |
|---|---|---|
| orgs | products/prototype/{app}/index.html `section[data-page=orgs]` | `.filters`, `table` |
| apps | products/prototype/{app}/index.html `section[data-page=apps]` | `.filters`, `table` |
"""


def progress_md(mode="full", gaps=""):
    devs = (
        "- 主按钮颜色取 DESIGN.md primary #1A66E0，不取原型 #1F6FEB。\n- 失败状态颜色取 danger token，不取原型 #CF222E。\n"
        if mode == "full"
        else "- restyle：配色、圆角、阴影全部取作者版 DESIGN.md，原型只给结构。\n"
    )
    return f"""# design-to-code progress

Mode: {mode}

## Slices

| slice | commit |
|---|---|
| orgs | 1a2b3c4 |
| apps | 5d6e7f8 |

## Sanctioned deviations

{devs}
## Gaps

{gaps or "无。"}
"""


def app_files(base, app="console", mode="full", **apps_kw):
    restyle = mode == "restyle"
    return {
        f"{base}/.design-to-code/index.md": index_md(app),
        f"{base}/.design-to-code/progress.md": progress_md(mode, apps_kw.pop("gaps", "")),
        f"{base}/src/routes.tsx": routes_tsx(),
        f"{base}/src/pages/orgs.tsx": orgs_tsx(apps_kw.pop("org_status", "停用"), restyle),
        f"{base}/src/pages/apps.tsx": apps_tsx(restyle=restyle, **apps_kw),
        f"{base}/src/api/apps.ts": api_apps(),
        f"{base}/src/mocks/apps.ts": MOCK_APPS_RESTYLE if restyle else MOCK_APPS,
    }


def portal_app():
    base = "apps/portal"
    return {
        f"{base}/.design-to-code/index.md": "# design-to-code index · portal\n\n| page id | prototype source |\n|---|---|\n| docs | products/prototype/portal/index.html `section[data-page=docs]` |\n",
        f"{base}/.design-to-code/progress.md": "# design-to-code progress\n\nMode: full\n\n## Gaps\n\n无。\n",
        f"{base}/src/routes.tsx": "import { DocsPage } from '@/pages/docs';\n\nexport const routes = [{ path: 'docs', title: '接口文档', element: <DocsPage /> }];\n",
        f"{base}/src/pages/docs.tsx": "// 接口文档页，page id: docs\nexport function DocsPage() {\n  return (\n    <div>\n      <h1>接口文档</h1>\n      <ul><li>鉴权</li><li>理赔核验</li></ul>\n    </div>\n  );\n}\n",
    }


def write(base, rel, text):
    p = os.path.join(base, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)


def step(fixture, n, slug, files):
    base = os.path.join(OUT, fixture, "steps", f"{n:02d}-{slug}")
    for rel, text in files.items():
        write(base, rel, text)


def drift():
    # 复制 AppKey 落地早于最近一次原型提交，只靠 git 区间会漏掉
    step("drift", 1, "prototype-and-built-console", {
        "CLAUDE.md": CLAUDE_MD.format(extra=""),
        "products/design/DESIGN.md": DESIGN_MD,
        "products/prototype/CHANGELOG.md": changelog(),
        "products/prototype/console/index.html": console_html(),
        **app_files("apps/console"),
    })
    step("drift", 2, "copy-appkey-in-frontend", {
        "apps/console/src/pages/apps.tsx": apps_tsx(copy_key=True),
    })
    step("drift", 3, "rename-org-status-everywhere", {
        "products/prototype/console/index.html": console_html(org_status="暂停"),
        "products/prototype/CHANGELOG.md": changelog([("Changed", "机构状态「已停用」改为「已暂停」。")]),
        "apps/console/src/pages/orgs.tsx": orgs_tsx("暂停"),
    })
    step("drift", 4, "last-call-column-guard-and-live-api", {
        "apps/console/src/pages/apps.tsx": apps_tsx(copy_key=True, last_call=True, guard=True),
        "apps/console/src/api/apps.ts": api_apps(live=True),
    })


def multi_line():
    unreleased = [("Added", "**Console**：新增「安全审计 → 审计日志」页面。")]
    gaps = "- audits：原型新增，待下个迭代 design-to-code。\n"
    step("multi-line", 1, "two-lines-built", {
        "CLAUDE.md": CLAUDE_MD.format(extra=", `apps/portal` (开发者门户)"),
        "products/design/DESIGN.md": DESIGN_MD,
        "products/prototype/CHANGELOG.md": changelog(released="## [Console V1] - 2026-10-01\n\n### Added\n\n- 初版：机构管理、应用管理两页。\n\n## [Portal V1] - 2026-10-01\n\n### Added\n\n- 初版：接口文档页。\n"),
        "products/prototype/console/index.html": console_html(bulk_disable=True),
        "products/prototype/portal/index.html": portal_html(),
        **app_files("apps/console"),
        **portal_app(),
    })
    step("multi-line", 2, "audit-log-prototype-and-org-filter-in-code", {
        "products/prototype/console/index.html": console_html(audits=True, bulk_disable=True),
        "products/prototype/CHANGELOG.md": changelog(unreleased, released="## [Console V1] - 2026-10-01\n\n### Added\n\n- 初版：机构管理、应用管理两页。\n\n## [Portal V1] - 2026-10-01\n\n### Added\n\n- 初版：接口文档页。\n"),
        "apps/console/src/pages/apps.tsx": apps_tsx(org_filter=True),
        "apps/console/.design-to-code/progress.md": progress_md("full", gaps),
    })


def restyle_no_drift():
    step("restyle-no-drift", 1, "prototype-and-restyled-console", {
        "CLAUDE.md": CLAUDE_MD.format(extra=""),
        "products/design/DESIGN.md": DESIGN_MD_RESTYLE,
        "products/prototype/CHANGELOG.md": changelog(),
        "products/prototype/console/index.html": console_html(),
        **app_files("apps/console", mode="restyle"),
    })
    step("restyle-no-drift", 2, "wire-apps-api", {
        "apps/console/src/api/apps.ts": api_apps(live=True),
    })


if __name__ == "__main__":
    for fx in ["drift", "multi-line", "restyle-no-drift"]:
        shutil.rmtree(os.path.join(OUT, fx), ignore_errors=True)
    drift()
    multi_line()
    restyle_no_drift()
