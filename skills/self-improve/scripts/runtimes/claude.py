"""Claude Code: ~/.claude/projects/<slug>/<session-id>.jsonl, slug = cwd with every
non-alphanumeric char replaced by '-'; subagents under <session-id>/subagents/."""
import collections
import json
import os
import re
import sys

from .common import Session, clip, iso, records

ROOT = os.path.expanduser("~/.claude/projects")
NOISE = ("<local-command", "<command-name>", "<command-message>", "<system-reminder>", "<task-notification>", "Caveat:")
INTERRUPT = ("[Request interrupted", "doesn't want to proceed", "user rejected", "was rejected")
BUILTIN = {"clear", "compact", "resume", "model", "config", "cost", "exit", "help", "init", "status"}


def project_dir(cwd):
    return os.path.join(ROOT, re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(cwd)))


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            b.get("text", "") if b.get("type") == "text" else text_of(b.get("content"))
            for b in content
            if isinstance(b, dict)
        )
    return ""


def human_prompt(d):
    """Return the text of a genuine user-typed message, else None."""
    # promptSource=system：后台任务完成通知等由 harness 注入的消息，不是用户提问，计成新一轮会把同一 skill 的开销拆走
    if d.get("type") != "user" or d.get("isMeta") or d.get("isSidechain") or d.get("promptSource") == "system":
        return None
    c = (d.get("message") or {}).get("content")
    if isinstance(c, list) and any(b.get("type") == "tool_result" for b in c if isinstance(b, dict)):
        return None
    # IDE 附带的选区/打开文件提示不是用户意图，剔除以省 Token
    t = re.sub(r"<ide_\w+>.*?</ide_\w+>|</?pasted_content[^>]*>", "", text_of(c), flags=re.S).strip()
    m = re.search(r"<command-name>/?([^<]+)</command-name>(?:.*?<command-args>(.*?)</command-args>)?", t, re.S)
    if m:
        # 斜杠命令：保留命令名与参数（无参数时没有 command-args 标签），内置的清屏等命令无复盘价值
        return None if m.group(1) in BUILTIN else f"/{m.group(1)} {(m.group(2) or '').strip()}".rstrip()
    if not t or t.startswith(NOISE) or t.startswith("Base directory for this skill"):
        return None
    return t


def skill_loaded(d):
    """Path of a skill whose body was injected into this user record, if any."""
    if d.get("type") != "user":
        return None
    m = re.match(r"\s*Base directory for this skill: (\S+)", text_of((d.get("message") or {}).get("content")))
    return m and m.group(1)


def find(cwd, ids):
    pdir = project_dir(cwd)
    if not os.path.isdir(pdir):
        return []
    files = [os.path.join(pdir, f) for f in os.listdir(pdir) if f.endswith(".jsonl")]
    if not ids:
        return [ClaudeSession(max(files, key=os.path.getmtime))] if files else []
    out = []
    for s in ids:
        hit = [f for f in files if os.path.basename(f).startswith(s)]
        if len(hit) != 1:
            sys.exit(f"session '{s}' matched {len(hit)} files in {pdir}")
        out.append(ClaudeSession(hit[0]))
    return out


def from_path(path):
    return ClaudeSession(path)


class ClaudeSession(Session):
    runtime = "Claude Code"

    def __init__(self, path):
        super().__init__(os.path.basename(path)[:-6], path)

    def meta(self):
        name, ai, ver, entry, last = "", "", "", "", ""
        # model 与 effort 会话中途都可能被切换：按对计数，最后一对才是当前档位
        pairs = collections.Counter()
        for d in records(self.path):
            # 手动 /rename 的 customTitle 优先于自动生成的 aiTitle，取最后一次
            name = d.get("customTitle") or name
            ai = d.get("aiTitle") or ai
            ver, entry = d.get("version") or ver, d.get("entrypoint") or entry
            m = (d.get("message") or {}).get("model")
            if m and not m.startswith("<"):
                last = f"{m}/{d.get('effort') or 'unknown'}"
                pairs[last] += 1
        runtime = f"Claude Code {ver} ({entry})".replace(" ()", "") if ver else "Claude Code"
        return {"name": name or ai, "runtime": runtime, "pairs": pairs, "last": last}

    def events(self):
        seen = set()  # 同一 message.id 会拆成多条记录，usage 只计一次
        for d in records(self.path):
            yield {"k": "tick", "ts": iso(d.get("timestamp"))}
            msg = d.get("message") or {}
            u, mid = msg.get("usage"), msg.get("id")
            if u and mid not in seen and not d.get("isSidechain"):
                seen.add(mid)
                ctx = sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
                yield {"k": "usage", "ctx": ctx, "out": u.get("output_tokens") or 0}
            if d.get("isCompactSummary"):
                yield {"k": "compact", "text": text_of(msg.get("content"))}
                continue
            loaded = skill_loaded(d)
            if loaded:
                yield {"k": "skill_loaded", "path": loaded}
                continue
            t = human_prompt(d)
            if t:
                # 用户手敲的斜杠命令 = 手动触发；Skill 工具调用则是模型或其他 skill 自动触发
                yield {"k": "user", "text": t, "manual": [t[1:].split()[0].split(":")[-1]] if t.startswith("/") else []}
                continue
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    name, inp = b.get("name", "?"), b.get("input") or {}
                    key = inp.get("skill") or inp.get("command") or inp.get("file_path") or inp.get("description") or ""
                    ev = {"k": "call", "id": b.get("id"), "name": name, "key": clip(str(key), 120),
                          # 同一文件的不同 Edit、不同段落的 Read 不是重试：签名带上改动内容或偏移
                          # 签名用完整输入：截断后的 key 前缀相同不代表同一调用
                          "sig": f'{key}\0{inp.get("old_string") or inp.get("offset") or ""}'}
                    if name == "Skill":
                        ev["skill"] = (inp.get("skill"), clip(str(inp.get("args") or ""), 120))
                    elif name in ("Agent", "Task"):
                        ev["agent"] = clip(inp.get("description") or "", 120)
                    yield ev
                elif b.get("type") == "tool_result":
                    body = text_of(b.get("content"))
                    yield {"k": "result", "id": b.get("tool_use_id"), "body": body, "error": bool(b.get("is_error")),
                           "rejected": any(m in body for m in INTERRUPT)}

    def subagents(self):
        """Per-subagent totals from <session>/subagents/agent-*.jsonl (sync and async alike)."""
        sdir = os.path.join(self.path[:-6], "subagents")
        out = []
        for f in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
            if not f.endswith(".jsonl"):
                continue
            tok, calls, seen, model, ts = 0, 0, set(), "", []
            for d in records(os.path.join(sdir, f)):
                m = d.get("message") or {}
                t = iso(d.get("timestamp"))
                if t:
                    ts.append(t)
                if m.get("id") and m.get("usage") and m["id"] not in seen:
                    seen.add(m["id"])
                    u = m["usage"]
                    tok += sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                         "cache_read_input_tokens", "output_tokens"))
                    model = m.get("model") or model
                if isinstance(m.get("content"), list):
                    calls += sum(1 for b in m["content"] if isinstance(b, dict) and b.get("type") == "tool_use")
            try:
                info = json.load(open(os.path.join(sdir, f[:-6] + ".meta.json")))
            except (OSError, ValueError):
                info = {}
            out.append({"desc": info.get("description") or f[:-6], "type": info.get("agentType"),
                        "start": min(ts) if ts else None, "model": model, "tokens": tok, "calls": calls,
                        "wall": int((max(ts) - min(ts)).total_seconds()) if ts else 0})
        return out
