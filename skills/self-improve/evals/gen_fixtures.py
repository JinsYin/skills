#!/usr/bin/env python3
"""Generate synthetic Claude Code, Codex, Cursor and Antigravity transcripts for self-improve evals."""
import itertools
import json
import os
import shutil
import sqlite3
import sys
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

# D. 上游已覆盖（gh pr create 缺 --head）+ 与 stub 的 open Issue #99 重复（digest 截断靠后的 skill-run 行）
home = project("covered-and-duplicate", {"self-improve": LOCK_UP})
s = S("d4c3f5a7-0000-4000-8000-000000000004", "retro-last-week")
s.slash("self-improve")
s.skill_body(f"{SK}/self-improve")
s.tool("Bash", {"command": "python3 scripts/transcript.py digest", "description": "Digest"}, "[cost] main in=40.1M …")
s.tool("Bash", {"command": "python3 - <<'EOF'\n# 临时扫 jsonl 补出 digest 没列的 skill-run\nEOF", "description": "Scan jsonl for missing skill runs"}, "turn 14: 3.2M / 41 calls …")
s.user("digest 只列了前 10 个轮次，后面的 skill-run 都被截掉了，你又临时写脚本扫 jsonl。transcript.py 应该把每个 skill-run 都列出来")
s.tool("Bash", {"command": "gh pr create -R jinsyin/skills --base master --label self-improve --body-file /tmp/pr.md", "description": "Create PR"},
       "must specify --head when running non-interactively from a shallow clone", err=True)
s.user("gh pr create 要显式带 --head <branch>，别让它自己猜")
s.save(home)

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
# G. 无可改进：ideate 顺利完成，仅一次弱信号报错（未过门槛）→ 记录 Issue 后立即关闭
home = project("no-improvement", {"ideate": LOCK_UP}, {"docs/ideas/idea.md": "# 账单助手 - 产品构想\n"})
s = S("a7b8c9d0-0000-4000-8000-000000000009", "idea-tweak")
s.slash("ideate", "补一条：支持导出 PDF 账单")
s.skill_body(f"{SK}/ideate")
s.tool("Read", {"file_path": "/work/demo/docs/idea.md"}, "File does not exist.", err=True)
s.tool("Read", {"file_path": "/work/demo/docs/ideas/idea.md"}, "# 账单助手 - 产品构想 …")
s.tool("Edit", {"file_path": "/work/demo/docs/ideas/idea.md", "old_string": "## 功能", "new_string": "## 功能\n- 导出 PDF 账单"}, "updated")
s.say("已更新 docs/ideas/idea.md。新增：导出 PDF 账单；修改：无；删除：无。待定：无。")
s.user("好的，谢谢")
s.slash("self-improve")
s.save(home)

# ---- 其他 Runtime：同一 cwd /work/demo，按各自存储格式落盘 ----
T0 = datetime(2026, 9, 28, 9, 0, 0)


class Codex:
    """~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<id>.jsonl（exec_command 调用 + token_usage_record）。"""

    def __init__(self, sid, name):
        self.sid, self.name, self.t, self.n = sid, name, T0, itertools.count(1)
        self.recs = []
        self._rec("session_meta", {"id": sid, "cwd": "/work/demo", "cli_version": "0.130.0", "originator": "codex_cli_rs"})
        self._rec("turn_context", {"model": "gpt-5.5", "effort": "high", "cwd": "/work/demo"})

    def _rec(self, typ, payload, secs=20):
        self.t += timedelta(seconds=secs)
        self.recs.append({"timestamp": self.t.isoformat() + "Z", "type": typ, "payload": payload})

    def _usage(self, tok):
        self._rec("token_usage_record", {"response_id": f"resp_{next(self.n)}",
                                         "usage": {"input_tokens": tok, "output_tokens": 400}}, 1)

    def user(self, text, secs=60):
        self._rec("response_item", {"type": "message", "role": "user",
                                    "content": [{"type": "input_text", "text": text}]}, secs)

    def skill_body(self, name, path):
        self.user(f"<skill>\n<name>{name}</name>\n<path>{path}</path>\n# skill body…\n</skill>", 2)

    def say(self, text, tok=20_000):
        self._rec("response_item", {"type": "message", "role": "assistant",
                                    "content": [{"type": "output_text", "text": text}]})
        self._usage(tok)

    def exec(self, cmd, out, code=0, tok=20_000):
        cid = f"call_{next(self.n)}"
        self._rec("response_item", {"type": "function_call", "name": "exec_command", "call_id": cid,
                                    "arguments": json.dumps({"cmd": cmd}, ensure_ascii=False)})
        self._usage(tok)
        self._rec("response_item", {"type": "function_call_output", "call_id": cid,
                                    "output": f"Process exited with code {code}\nOutput:\n{out}"}, 5)

    def save(self, home):
        d = os.path.join(home, ".codex", "sessions", "2026", "09", "28")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"rollout-2026-09-28T09-00-00-{self.sid}.jsonl"), "w") as f:
            for r in self.recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(os.path.join(home, ".codex", "session_index.jsonl"), "w") as f:
            f.write(json.dumps({"id": self.sid, "thread_name": self.name}) + "\n")


class Cursor:
    """~/.cursor/projects/work-demo/agent-transcripts/<id>/<id>.jsonl：只有提问与工具调用，无 token、模型、工具结果。"""

    def __init__(self, sid):
        self.sid, self.t, self.recs = sid, T0, []

    def user(self, text, skills=(), mins=2):
        self.t += timedelta(minutes=mins)
        att = "".join(f"Skill Name: {n}\nPath: {p}\n" for n, p in skills)
        att = f"<manually_attached_skills>\n{att}</manually_attached_skills>\n" if att else ""
        stamp = self.t.strftime("%A, %b %d, %Y, %I:%M %p").replace(" 0", " ")
        self.recs.append({"role": "user", "message": {"content": [{"type": "text", "text":
                          f"<timestamp>{stamp} (UTC+8)</timestamp>\n{att}<user_query>\n{text}\n</user_query>"}]}})

    def tool(self, name, inp):
        self.recs.append({"role": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}})

    def say(self, text):
        self.recs.append({"role": "assistant", "message": {"content": [{"type": "text", "text": text}]}})
        self.recs.append({"type": "turn_ended", "status": "success"})

    def save(self, home):
        d = os.path.join(home, ".cursor", "projects", "work-demo", "agent-transcripts", self.sid)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, self.sid + ".jsonl"), "w") as f:
            for r in self.recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")


def pb(*fields):
    """最小 protobuf 编码：int → varint，str/bytes → 定长，tuple → 嵌套消息。"""
    def var(n):
        out = b""
        while True:
            b, n = n & 0x7F, n >> 7
            out += bytes([b | (0x80 if n else 0)])
            if not n:
                return out
    out = b""
    for f, v in fields:
        if isinstance(v, int):
            out += var(f << 3) + var(v)
        else:
            v = pb(*v) if isinstance(v, tuple) else v.encode() if isinstance(v, str) else v
            out += var(f << 3 | 2) + var(len(v)) + v
    return out


class Agy:
    """~/.gemini/antigravity/conversations/<id>.db：steps（14 用户输入、15 工具调用、field 140 工具结果）
    + gen_metadata（每次模型调用的模型名与 token）；conversation_summaries.db 记录工作区与标题。"""

    def __init__(self, cid, title):
        self.cid, self.title, self.t, self.steps, self.gens, self.n = cid, title, T0, [], [], itertools.count(1)

    def _step(self, typ, payload, secs=20, err=None):
        self.t += timedelta(seconds=secs)
        meta = pb((1, ((1, int(self.t.timestamp())), (2, 0))))
        self.steps.append((len(self.steps), typ, meta, err, payload))

    def user(self, text, secs=60):
        self._step(14, pb((19, ((2, text),))), secs)

    def _gen(self, tok):
        kv = ((20, ((1, "last_step_index"), (2, str(len(self.steps) - 1)))),)
        self.gens.append(pb((1, ((19, "gemini-3.8-flash"), (4, ((2, tok), (3, 500))),
                                 (11, ((1, int(self.t.timestamp())),)), *kv))))

    def tool(self, name, args, out, tok=30_000, err=False):
        cid = f"toolu_{next(self.n)}"
        self._step(15, pb((20, ((7, ((1, cid), (2, name), (3, json.dumps(args, ensure_ascii=False)))),))))
        self._gen(tok)
        self._step(21, pb((140, ((2, ((1, out),)),))), 5, b"\x0a\x01x" if err else None)

    def save(self, home):
        root = os.path.join(home, ".gemini", "antigravity")
        os.makedirs(os.path.join(root, "conversations"), exist_ok=True)
        c = sqlite3.connect(os.path.join(root, "conversations", self.cid + ".db"))
        c.execute("create table steps (idx integer primary key, step_type integer, metadata blob, error_details blob, step_payload blob)")
        c.execute("create table gen_metadata (idx integer primary key, data blob)")
        c.executemany("insert into steps values (?,?,?,?,?)", self.steps)
        c.executemany("insert into gen_metadata values (?,?)", enumerate(self.gens))
        c.commit()
        c = sqlite3.connect(os.path.join(root, "conversation_summaries.db"))
        c.execute("create table conversation_summaries (conversation_id text primary key, title text, "
                  "last_modified_time datetime, workspace_uris text, agent_name text default '', "
                  "parent_conversation_id text default '', nesting_depth integer default 0)")
        c.execute("insert into conversation_summaries (conversation_id, title, last_modified_time, workspace_uris) "
                  "values (?,?,?,?)", (self.cid, self.title, self.t.isoformat(), '["file:///work/demo"]'))
        c.commit()


def fresh(name):
    """二进制 SQLite 无法覆盖写，重新生成前清掉旧 fixture。"""
    shutil.rmtree(os.path.join(OUT, name), ignore_errors=True)


# H. Codex：github-pr-merge 规则未生效（CI 红仍推荐 Merge，两次纠正），有 token 数据
fresh("codex-pr-merge")
home = project("codex-pr-merge", {"github-pr-merge": LOCK_UP})
c = Codex("019a0000-0000-7000-8000-00000000000a", "merge-prs")
c.user("$github-pr-merge 把 acme/tools 上待合并的 PR 处理掉")
c.skill_body("github-pr-merge", "/work/demo/.agents/skills/github-pr-merge/SKILL.md")
c.exec("gh pr view 12 -R acme/tools --json statusCheckRollup,mergeable",
       '{"mergeable":"MERGEABLE","statusCheckRollup":[{"name":"test","conclusion":"FAILURE"}]}')
c.say("PR #12 改动清晰，建议 Merge。")
c.user("CI 是红的你怎么还推荐合并？先看 statusCheckRollup")
c.exec("gh pr view 13 -R acme/tools --json statusCheckRollup,mergeable",
       '{"mergeable":"MERGEABLE","statusCheckRollup":[{"name":"lint","conclusion":"FAILURE"}]}')
c.say("PR #13 只改了文档，建议 Merge。")
c.user("又来了，#13 的 lint 也挂了。CI 失败要先在评审里写出来再给建议")
c.user("$self-improve")
c.save(home)

# I. Cursor IDE：手动附加 ideate，两次替用户补选型被纠正；transcript 无 token
home = project("cursor-ideate", {"ideate": LOCK_UP}, {"docs/ideas/idea.md": "# 账单助手 - 产品构想\n"})
u = Cursor("6c0e0000-0000-4000-8000-00000000000b")
IDEATE = [("ideate", "/work/demo/.cursor/skills/ideate/SKILL.md")]
u.user("加上多币种结算", IDEATE)
u.tool("ReadFile", {"path": "/work/demo/docs/ideas/idea.md"})
u.tool("Write", {"path": "/work/demo/docs/ideas/idea.md", "contents": "…多币种结算：基于 Redis 缓存汇率…"})
u.say("已更新 idea.md。")
u.user("Redis 是你自己加的吧？没定的选型要问我，不要替我补", IDEATE)
u.tool("Write", {"path": "/work/demo/docs/ideas/idea.md", "contents": "…多币种结算：汇率每日由 Kafka 同步…"})
u.say("已改为 Kafka 同步汇率。")
u.user("又替我选了 Kafka。选型没定就写「待定」并问我", IDEATE)
u.tool("Write", {"path": "/work/demo/docs/ideas/idea.md", "contents": "…多币种结算：汇率来源待定…"})
u.say("已改为待定。")
u.user("/self-improve")
u.save(home)

# J. Antigravity (agy)：version-release 打 tag 前不查已存在 tag，同一报错两次后被纠正
fresh("agy-version-release")
home = project("agy-version-release", {"version-release": LOCK_UP})
g = Agy("a9e70000-0000-4000-8000-00000000000c", "Release v1.3.0")
g.user("/version-release 发 v1.3.0")
g.tool("view_file", {"AbsolutePath": "/work/demo/.agents/skills/version-release/SKILL.md"}, "# version-release …")
g.tool("run_command", {"CommandLine": "git tag v1.3.0"}, "fatal: tag 'v1.3.0' already exists\nCommand exited with code 128", err=True)
g.tool("run_command", {"CommandLine": "git tag v1.3.0 && git push origin v1.3.0"}, "fatal: tag 'v1.3.0' already exists\nCommand exited with code 128", err=True)
g.user("v1.3.0 上周就发过了。打 tag 前先 git tag -l 查一下版本是否已存在，存在就停下来问我")
g.tool("run_command", {"CommandLine": "git tag -l 'v1.3*'"}, "v1.3.0\nCommand exited with code 0")
g.user("/self-improve")
g.save(home)
print("ok")
