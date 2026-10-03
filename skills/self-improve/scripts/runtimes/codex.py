"""Codex (CLI, IDE, desktop): ~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<id>.jsonl.
First record is session_meta (id, cwd, parent_thread_id for subagents); thread names
live in ~/.codex/session_index.jsonl."""
import collections
import glob
import json
import os
import re
import sys

from .common import Session, clip, first_record, iso, records, same_dir, skill_reads, tool_key

ROOT = os.path.expanduser(os.environ.get("CODEX_HOME") or "~/.codex")
# 注入的上下文不是用户输入
NOISE = ("# AGENTS.md instructions", "<environment_context>", "<recommended_plugins>", "<user_instructions>",
         "<app-context>", "<image ", "<turn_aborted>")
POLL = ("wait_agent", "list_agents")
EXIT = re.compile(r"(?:Process exited with code|\"exit_code\":)\s*(-?\d+)")
REJECT = ("Rejected(", "aborted by user", "rejected by user")
MANUAL = re.compile(r"(?:^|\s)\$([\w.:-]+)")


def rollouts():
    return sorted(glob.glob(os.path.join(ROOT, "sessions", "*", "*", "*", "rollout-*.jsonl")),
                  key=os.path.getmtime, reverse=True)


def is_main(meta):
    p = meta.get("payload") or {}
    return meta.get("type") == "session_meta" and p.get("thread_source") != "subagent" and \
        p.get("parent_thread_id") in (None, "", p.get("id"))


def segments(sid):
    """All rollout files of one thread, oldest first: a resumed thread continues in
    rollout-<ts>-<id>_<segment>.jsonl whose session_meta keeps the same id."""
    fs = glob.glob(os.path.join(ROOT, "sessions", "*", "*", "*", f"rollout-*{sid}*.jsonl"))
    return sorted((f for f in fs if (first_record(f).get("payload") or {}).get("id") == sid), key=os.path.getmtime)


def find(cwd, ids):
    out, seen = [], set()
    for f in rollouts():
        m = first_record(f)
        sid = (m.get("payload") or {}).get("id")
        if sid in seen or ids and not any(sid and sid.startswith(s) for s in ids):
            continue
        if not is_main(m) or not same_dir((m.get("payload") or {}).get("cwd"), cwd):
            continue
        seen.add(sid)
        out.append(CodexSession(segments(sid), m["payload"]))
        if not ids:
            break
    if ids and len(out) != len(ids):
        sys.exit(f"codex: {len(ids)} id(s) matched {len(out)} rollouts for {cwd}")
    return out


def from_path(path):
    p = first_record(path).get("payload") or {}
    return CodexSession(segments(p["id"]) if p.get("id") else [path], p)


def thread_name(sid):
    name = ""
    for d in records(os.path.join(ROOT, "session_index.jsonl")) if os.path.exists(
            os.path.join(ROOT, "session_index.jsonl")) else []:
        if d.get("id") == sid:
            name = d.get("thread_name") or name
    return name


def user_text(content):
    t = "".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "input_text")
    # IDE 会把用户原话包在「Files mentioned」说明之后
    m = re.search(r"## My request(?: for Codex)?:\s*(.*)", t, re.S)
    return (m.group(1) if m else t).strip()


def call_key(p):
    if p.get("type") == "custom_tool_call":
        # exec 工具的输入是一段 JS，取其中第一条 shell 命令作标识
        src = p.get("input") or ""
        m = re.search(r"cmd:\s*\"((?:[^\"\\]|\\.)*)\"", src)
        try:
            cmd = json.loads(f'"{m.group(1)}"') if m else src
        except ValueError:
            cmd = m.group(1)
        return clip(cmd, 120), src
    try:
        args = json.loads(p.get("arguments") or "{}")
    except ValueError:
        args = {"arguments": p.get("arguments")}
    return tool_key(args), p.get("arguments") or ""


def output_text(o):
    if isinstance(o, list):
        return "\n".join(b.get("text", "") for b in o if isinstance(b, dict))
    return o if isinstance(o, str) else json.dumps(o, ensure_ascii=False)


class CodexSession(Session):
    runtime = "Codex"

    def __init__(self, paths, payload):
        super().__init__(payload.get("id") or os.path.basename(paths[0])[:-6], paths[-1])
        self.paths, self.info = paths, payload

    def records(self):
        for f in self.paths:
            yield from records(f)

    def meta(self):
        pairs, last = collections.Counter(), ""
        for d in self.records():
            if d.get("type") == "turn_context":
                p = d.get("payload") or {}
                last = f"{p.get('model') or 'unknown'}/{p.get('effort') or 'unknown'}"
                pairs[last] += 1
        i = self.info
        runtime = f"Codex {i.get('cli_version') or ''} ({i.get('originator') or i.get('source') or ''})"
        return {"name": thread_name(self.id), "runtime": re.sub(r"\s+\(\)|\s{2,}", " ", runtime).strip(),
                "pairs": pairs, "last": last}

    def events(self):
        seen = set()
        for d in self.records():
            ts, typ, p = iso(d.get("timestamp")), d.get("type"), d.get("payload") or {}
            yield {"k": "tick", "ts": ts}
            pt = p.get("type") if isinstance(p, dict) else None
            if typ == "token_usage_record":
                rid = p.get("response_id") or id(d)
                if rid not in seen:
                    seen.add(rid)
                    u = p.get("usage") or {}
                    # OpenAI 的 input_tokens 已含缓存命中部分
                    yield {"k": "usage", "ctx": u.get("input_tokens") or 0, "out": u.get("output_tokens") or 0}
            elif typ == "compacted":
                yield {"k": "compact", "text": p.get("message") or "context compacted"}
            elif typ == "event_msg" and pt == "turn_aborted":
                yield {"k": "note", "text": f"INTERRUPTED ({p.get('reason') or 'aborted'})"}
            elif typ != "response_item":
                continue
            elif pt == "message" and p.get("role") == "user":
                raw = "".join(b.get("text", "") for b in p.get("content") or [] if isinstance(b, dict))
                m = re.match(r"\s*<skill>\s*<name>([^<]+)</name>\s*<path>([^<]+)</path>", raw)
                if m:
                    yield {"k": "skill_loaded", "path": m.group(2)}
                    continue
                t = user_text(p.get("content"))
                # 整条被单个 XML 标签包住的消息是客户端注入的上下文
                if t and not t.startswith(NOISE) and not re.fullmatch(r"<([\w-]+)[^>]*>.*</\1>", t, re.S):
                    # Codex 用 `$skill` 手动点名 skill
                    yield {"k": "user", "text": t, "manual": MANUAL.findall(t)}
            elif pt in ("function_call", "custom_tool_call"):
                key, raw = call_key(p)
                name = (p.get("namespace") or "") + (p.get("name") or "?")
                ev = {"k": "call", "id": p.get("call_id"), "name": name, "key": key,
                      # 轮询子 Agent 状态是正常等待，不算重试
                      "sig": p.get("call_id") if name.endswith(POLL) else raw}
                if name.endswith("spawn_agent"):
                    try:
                        a = json.loads(p.get("arguments") or "{}")
                    except ValueError:
                        a = {}
                    ev["agent"] = clip(a.get("task_name") or a.get("agent_type") or "", 120)
                yield ev
                for path, _ in skill_reads(raw):
                    yield {"k": "skill_loaded", "path": path}
            elif pt in ("function_call_output", "custom_tool_call_output"):
                body = output_text(p.get("output"))
                bad = next((m for m in EXIT.finditer(body) if int(m.group(1)) != 0), None)
                err = body.startswith("Script failed") or bad is not None
                # 去掉 exec 包装头；多命令输出从首个非零退出码处截取，摘要才看得到失败那段
                body = re.sub(r"\AScript (?:completed|failed)\s+Wall time [\d.]+ seconds\s+Output:\s*", "", body)
                if bad and len(body) > 200:
                    i = body.find(bad.group(0))
                    body = body[i:] if i > 0 else body
                yield {"k": "result", "id": p.get("call_id"), "body": body, "error": err,
                       "rejected": any(r in body for r in REJECT)}

    def subagents(self):
        """Child rollouts whose session_meta.parent_thread_id is this session."""
        day = os.path.dirname(self.paths[0])
        out = []
        for f in rollouts():
            # 子 Agent 不会早于父会话创建，跳过更早日期的目录
            if os.path.dirname(f) < day:
                continue
            p = first_record(f).get("payload") or {}
            if p.get("parent_thread_id") != self.id or p.get("id") == self.id:
                continue
            tok, calls, model, ts, seen = 0, 0, "", [], set()
            for d in records(f):
                t = iso(d.get("timestamp"))
                if t:
                    ts.append(t)
                q = d.get("payload") or {}
                if d.get("type") == "token_usage_record" and q.get("response_id") not in seen:
                    seen.add(q.get("response_id"))
                    u = q.get("usage") or {}
                    tok += (u.get("input_tokens") or 0) + (u.get("output_tokens") or 0)
                elif d.get("type") == "turn_context":
                    model = q.get("model") or model
                elif isinstance(q, dict) and q.get("type") in ("function_call", "custom_tool_call"):
                    calls += 1
            out.append({"desc": p.get("agent_path") or p.get("agent_nickname") or p.get("id"),
                        "type": p.get("agent_role") or "default", "start": min(ts) if ts else None,
                        "model": model, "tokens": tok, "calls": calls,
                        "wall": int((max(ts) - min(ts)).total_seconds()) if ts else 0})
        return out
