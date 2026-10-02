#!/usr/bin/env python3
"""Generate synthetic Claude Code transcripts for self-improve evals."""
import json, os, sys, itertools
from datetime import datetime, timedelta

OUT = sys.argv[1]  # skills/self-improve/evals/files
SLUG = "-work-demo"  # = transcript.py slug of --cwd /work/demo
MODEL, EFFORT, VER = "claude-opus-5-5", "high", "2.1.290"
LOCK_UP = {"source": "jinsyin/skills", "sourceType": "github", "computedHash": "0" * 64}
LOCK_3P = {"source": "obra/superpowers", "sourceType": "github", "computedHash": "1" * 64}


class S:
    def __init__(self, sid, title):
        self.sid, self.recs, self.t = sid, [], datetime(2026, 9, 28, 9, 0, 0)
        self.n = itertools.count(1)
        self.recs.append({"type": "custom-title", "customTitle": title, "sessionId": sid})

    def _base(self, typ, secs=20):
        self.t += timedelta(seconds=secs)
        return {"type": typ, "sessionId": self.sid, "version": VER, "entrypoint": "cli",
                "timestamp": self.t.isoformat() + "Z", "cwd": "/work/demo"}

    def user(self, text, secs=60):
        d = self._base("user", secs)
        d["message"] = {"role": "user", "content": text}
        self.recs.append(d)

    def slash(self, name, args=""):
        tail = f"<command-args>{args}</command-args>" if args else ""
        self.user(f"<command-message>{name}</command-message>\n<command-name>/{name}</command-name>\n{tail}")

    def skill_body(self, path):
        d = self._base("user", 2)
        d["isMeta"] = True
        d["message"] = {"role": "user", "content": [{"type": "text", "text": f"Base directory for this skill: {path}\n\n# skill body…"}]}
        self.recs.append(d)

    def say(self, text, tok=20_000, secs=20):
        d = self._base("assistant", secs)
        d["effort"] = EFFORT
        d["message"] = {"id": f"msg_{self.sid[:4]}{next(self.n)}", "role": "assistant", "model": MODEL,
                        "content": [{"type": "text", "text": text}],
                        "usage": {"input_tokens": 50, "cache_read_input_tokens": tok, "output_tokens": 400}}
        self.recs.append(d)

    def tool(self, name, inp, result, err=False, tok=20_000, secs=20):
        tid = f"tu_{self.sid[:4]}{next(self.n)}"
        d = self._base("assistant", secs)
        d["effort"] = EFFORT
        d["message"] = {"id": f"msg_{tid}", "role": "assistant", "model": MODEL,
                        "content": [{"type": "tool_use", "id": tid, "name": name, "input": inp}],
                        "usage": {"input_tokens": 50, "cache_read_input_tokens": tok, "output_tokens": 300}}
        self.recs.append(d)
        r = self._base("user", 5)
        r["message"] = {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tid,
                                                    "content": result, "is_error": err}]}
        self.recs.append(r)

    def save(self, home, mtime_offset=0):
        d = os.path.join(home, ".claude", "projects", SLUG)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, self.sid + ".jsonl")
        with open(p, "w") as f:
            for r in self.recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        ts = datetime(2026, 9, 28).timestamp() + mtime_offset
        os.utime(p, (ts, ts))


def project(name, lock, extra=None):
    root = os.path.join(OUT, name)
    os.makedirs(os.path.join(root, "project"), exist_ok=True)
    with open(os.path.join(root, "project", "skills-lock.json"), "w") as f:
        json.dump({"version": 1, "skills": lock}, f, indent=2)
    for rel, body in (extra or {}).items():
        p = os.path.join(root, "project", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(body)
    return os.path.join(root, "home")


SK = "/work/demo/.claude/skills"

# A. ideate: 强信号缺口（更新后未列变更）+ 规则存在未生效（自行补选型）+ 单次弱信号报错
home = project("ideate-gap", {"ideate": LOCK_UP, "caveman-commit": {**LOCK_3P, "source": "JuliusBrussee/caveman"}},
               {"docs/ideas/idea.md": "# 账单助手 - 产品构想\n", "docs/requirements/raw.md": "- 支持多币种\n"})
s = S("a1f0c2d4-0000-4000-8000-000000000001", "update-idea")
s.slash("ideate", "加上多币种，并把 raw.md 迁进来")
s.skill_body(f"{SK}/ideate")
s.tool("Read", {"file_path": "/work/demo/docs/ideas/idea.md"}, "# 账单助手 - 产品构想 …")
s.tool("Read", {"file_path": "/work/demo/docs/requirements/raw.md"}, "- 支持多币种")
s.tool("Write", {"file_path": "/work/demo/docs/ideas/idea.md", "content": "…2. 产品交付矩阵\n1. **billing-spring-boot-starter**：基于 Redis 缓存汇率…"}, "written")
s.tool("Bash", {"command": "git rm docs/requirements/raw.md", "description": "Remove migrated source"},
       "fatal: pathspec 'docs/requirements/raw.md' did not match any files", err=True)
s.tool("Bash", {"command": "rm docs/requirements/raw.md", "description": "Remove migrated source"}, "")
s.say("已更新 docs/ideas/idea.md，已删除 docs/requirements/raw.md。待定：无。")
s.user("交付矩阵里的 Spring Boot Starter 和 Redis 是你自己加的吧？我从没说过，没定的选型要问我，不要替我补")
s.tool("Edit", {"file_path": "/work/demo/docs/ideas/idea.md", "old_string": "1. **billing-spring-boot-starter**：基于 Redis 缓存汇率", "new_string": "待定：交付形态与技术约束"}, "updated")
s.user("另外你这次到底改了 idea.md 哪些地方？每次更新完要列出新增、修改、删除了哪几条，不然我只能自己 diff")
s.tool("Bash", {"command": "git diff docs/ideas/idea.md", "description": "Show idea changes"}, "+ 支持多币种 …")
s.say("本次新增：1.2 多币种结算；修改：无；删除：无。")
s.slash("self-improve")
s.save(home)

# B. github-pr-merge: 规则存在但两次未生效（CI 失败仍推荐 Merge）
home = project("pr-merge-rule-not-fired", {"github-pr-merge": LOCK_UP})
s = S("b2e1d3c5-0000-4000-8000-000000000002", "merge-prs")
s.user("帮我把 acme/tools 上那两个待合并的 PR 处理掉")
s.tool("Skill", {"skill": "github-pr-merge", "args": "-R acme/tools"}, "Launching skill: github-pr-merge")
s.skill_body(f"{SK}/github-pr-merge")
s.tool("Bash", {"command": "gh pr view 12 -R acme/tools --json statusCheckRollup,mergeable", "description": "View PR 12"},
       '{"mergeable":"MERGEABLE","statusCheckRollup":[{"name":"test","conclusion":"FAILURE"}]}')
s.say("PR #12 改动清晰，建议 Merge。")
s.user("CI 是红的你怎么还推荐合并？先看 statusCheckRollup")
s.tool("Bash", {"command": "gh pr view 13 -R acme/tools --json statusCheckRollup,mergeable", "description": "View PR 13"},
       '{"mergeable":"MERGEABLE","statusCheckRollup":[{"name":"lint","conclusion":"FAILURE"}]}')
s.say("PR #13 只改了文档，建议 Merge。")
s.user("又来了，#13 的 lint 也挂了。CI 失败要先在评审里写出来再给建议")
s.slash("self-improve")
s.save(home)

# C. 手动重度第三方 skill（brainstorming）+ 自动轻量第三方 skill（caveman-commit）
home = project("heavy-third-party", {"brainstorming": LOCK_3P, "caveman-commit": {**LOCK_3P, "source": "JuliusBrussee/caveman"},
                                     "setup-rules": LOCK_UP})
s = S("c3d2e4f6-0000-4000-8000-000000000003", "brainstorm-export")
s.slash("brainstorming", "给报表模块加 CSV 导出")
s.skill_body(f"{SK}/brainstorming")
qs = ["导出编码用 UTF-8 还是 GBK？", "分隔符用逗号吗？", "要不要带表头？", "日期格式用 ISO 8601 吗？",
      "空值写空串还是 NULL？", "文件名要不要带时间戳？", "超过 10 万行要不要分片？", "要不要异步导出？"]
# brainstorming 在同一轮内逐个用 AskUserQuestion 发问，开销全归入手动触发的第 1 轮
for q in qs:
    s.tool("AskUserQuestion", {"questions": [{"question": q}]}, "User answered: 按常规来", tok=900_000, secs=400)
s.user("这些有行业默认值的问题你自己定，别一个个问我，整个过程拖了快一个小时")
s.tool("Write", {"file_path": "/work/demo/docs/specs/csv-export.md", "content": "spec"}, "written", tok=30_000)
s.tool("Skill", {"skill": "caveman-commit"}, "Launching skill: caveman-commit", tok=30_000)
s.tool("Bash", {"command": "git commit -m 'docs(spec): 报表 CSV 导出'", "description": "Commit spec"}, "1 file changed", tok=30_000)
s.user("顺便把 README 里的链接修一下", secs=60)
s.tool("Edit", {"file_path": "/work/demo/README.md", "old_string": "(docs/spec)", "new_string": "(docs/specs)"}, "updated", tok=30_000)
s.slash("self-improve")
s.save(home)

# D. 上游已覆盖（gh pr create 缺 --head）+ 与 open Issue #9 重复（digest 按调用统计开销）
home = project("covered-and-duplicate", {"self-improve": LOCK_UP})
s = S("d4c3f5a7-0000-4000-8000-000000000004", "retro-last-week")
s.slash("self-improve")
s.skill_body(f"{SK}/self-improve")
s.tool("Bash", {"command": "python3 scripts/transcript.py digest", "description": "Digest"}, "[cost] main in=40.1M …")
s.tool("Bash", {"command": "python3 - <<'EOF'\n# 临时扫 jsonl 统计每次调用开销\nEOF", "description": "Scan jsonl per-call cost"}, "turn 3: 16.8M / 125 calls …")
s.user("digest 看不出每次调用的开销，你又临时写脚本扫 jsonl。这个应该内建到 transcript.py 里")
s.tool("Bash", {"command": "gh pr create -R jinsyin/skills --base master --label self-improve --body-file /tmp/pr.md", "description": "Create PR"},
       "must specify --head when running non-interactively from a shallow clone", err=True)
s.user("gh pr create 要显式带 --head <branch>，别让它自己猜")
s.save(home)

# E. --sessions：同项目三个会话
home = project("multi-session", {"ideate": LOCK_UP})
for i, (title, prompt) in enumerate([("idea-billing", "把账单助手的想法整理一下"),
                                     ("fix-ci", "CI 上 lint 挂了帮我看看"),
                                     ("idea-export", "idea 里再加一个导出功能")]):
    s = S(f"e5{i}a6b8c-0000-4000-8000-00000000000{5 + i}", title)
    s.user(prompt)
    s.say("好的。")
    s.save(home, mtime_offset=i * 3600)

# F. 无归属、可跨项目复用的经验 → 新 skill
home = project("new-skill-no-owner", {"ideate": LOCK_UP})
s = S("f6e5a7b9-0000-4000-8000-000000000008", "arch-diagrams")
s.user("给 docs/architecture.md 画一张服务调用的 Mermaid 时序图")
s.tool("Edit", {"file_path": "/work/demo/docs/architecture.md", "old_string": "## 调用链", "new_string": "## 调用链\n```mermaid\nsequenceDiagram\n  A->>B: call()\n```"}, "updated")
s.say("已添加时序图。")
s.user("GitHub 上渲染报错了：Parse error on line 3。以后画完 Mermaid 先用 mmdc 渲染校验一遍再交给我，所有项目都这样")
s.tool("Bash", {"command": "npx -y @mermaid-js/mermaid-cli -i docs/architecture.md -o /tmp/out.md", "description": "Validate mermaid"}, "Parse error on line 3", err=True)
s.tool("Edit", {"file_path": "/work/demo/docs/architecture.md", "old_string": "A->>B: call()", "new_string": "A->>B: call"}, "updated")
s.tool("Bash", {"command": "npx -y @mermaid-js/mermaid-cli -i docs/architecture.md -o /tmp/out.md", "description": "Validate mermaid"}, "Generated 1 diagram")
s.user("再在 docs/deploy.md 加一张部署拓扑的 flowchart")
s.tool("Edit", {"file_path": "/work/demo/docs/deploy.md", "old_string": "## 拓扑", "new_string": "## 拓扑\n```mermaid\nflowchart LR\n  lb[LB] --> app(App)\n```"}, "updated")
s.say("已添加。")
s.user("你又没校验就交了，上次刚说过要先 mmdc 跑一遍")
s.slash("self-improve")
s.save(home)
print("ok")
