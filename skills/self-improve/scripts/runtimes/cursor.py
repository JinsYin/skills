"""Cursor IDE and cursor-agent CLI: ~/.cursor/projects/<slug>/agent-transcripts/<id>/<id>.jsonl,
slug = cwd with runs of non-alphanumeric chars collapsed to '-'. Subagents sit in
<id>/subagents/. Transcripts hold prompts and tool calls only: no tool results,
token usage, model or per-call timestamps."""
import collections
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

from .common import Session, clip, records, skill_reads, tool_key

ROOT = os.path.expanduser("~/.cursor")
STAMP = re.compile(r"<timestamp>\w+, (\w+ \d+, \d+, \d+:\d+ [AP]M) \(UTC([+-]\d+)(?::?(\d+))?\)</timestamp>")
ATTACHED = re.compile(r"Skill Name: ([^\n]+)\nPath: ([^\n]+)")


def project_dir(cwd):
    return os.path.join(ROOT, "projects", re.sub(r"[^A-Za-z0-9]+", "-", os.path.abspath(cwd)).strip("-"),
                        "agent-transcripts")


def transcripts(cwd):
    d = project_dir(cwd)
    files = [os.path.join(d, s, s + ".jsonl") for s in os.listdir(d)] if os.path.isdir(d) else []
    return sorted((f for f in files if os.path.isfile(f)), key=os.path.getmtime, reverse=True)


def sid_of(path):
    return os.path.basename(path)[:-6].removeprefix("agent-")


def find(cwd, ids):
    files = transcripts(cwd)
    if not ids:
        return [CursorSession(files[0])] if files else []
    out = []
    for s in ids:
        hit = [f for f in files if sid_of(f).startswith(s)]
        if len(hit) != 1:
            sys.exit(f"cursor: session '{s}' matched {len(hit)} transcripts for {cwd}")
        out.append(CursorSession(hit[0]))
    return out


def from_path(path):
    return CursorSession(path)


def stamp(text):
    m = STAMP.search(text)
    if not m:
        return None
    try:
        t = datetime.strptime(m.group(1), "%b %d, %Y, %I:%M %p")
    except ValueError:
        return None
    off = int(m.group(2))
    tz = timezone(timedelta(hours=off, minutes=(int(m.group(3) or 0) * (1 if off >= 0 else -1))))
    return t.replace(tzinfo=tz)


def query(text):
    m = re.search(r"<user_query>\s*(.*?)\s*</user_query>", text, re.S)
    return (m.group(1) if m else re.sub(r"<(\w+)>.*?</\1>", "", text, flags=re.S)).strip()


def text_blocks(d):
    c = (d.get("message") or {}).get("content")
    return [b for b in c if isinstance(b, dict)] if isinstance(c, list) else []


class CursorSession(Session):
    runtime = "Cursor"

    def __init__(self, path):
        super().__init__(sid_of(path), path)

    def meta(self):
        first = next((query(b.get("text", "")) for d in records(self.path) if d.get("role") == "user"
                      for b in text_blocks(d) if b.get("type") == "text"), "")
        # cursor-agent CLI 另在 ~/.cursor/chats/<hash>/<id>/ 留有会话库；IDE 没有
        cli = any(os.path.isdir(os.path.join(ROOT, "chats", h, self.id))
                  for h in (os.listdir(os.path.join(ROOT, "chats")) if os.path.isdir(os.path.join(ROOT, "chats")) else []))
        return {"name": clip(first, 60), "runtime": "Cursor CLI (cursor-agent)" if cli else "Cursor IDE",
                "pairs": collections.Counter(), "last": ""}

    def events(self):
        n = 0
        for d in records(self.path):
            if d.get("type") == "turn_ended":
                if d.get("status") not in (None, "success"):
                    yield {"k": "note", "text": f"TURN-ERROR status={d.get('status')}"}
                continue
            role = d.get("role")
            for b in text_blocks(d):
                if role == "user" and b.get("type") == "text":
                    raw = b.get("text", "")
                    yield {"k": "tick", "ts": stamp(raw)}
                    att = ATTACHED.findall(raw)
                    t = query(raw)
                    manual = [n.strip() for n, _ in att] + ([t[1:].split()[0]] if t.startswith("/") else [])
                    if t:
                        yield {"k": "user", "text": t, "manual": manual}
                    # 附加的 skill 随本条提问注入，归入该轮
                    for _, path in att:
                        yield {"k": "skill_loaded", "path": path.strip()}
                elif role == "assistant" and b.get("type") == "tool_use":
                    n += 1
                    name, inp = b.get("name", "?"), b.get("input") or {}
                    ev = {"k": "call", "id": f"c{n}", "name": name, "key": tool_key(inp),
                          "sig": json.dumps(inp, ensure_ascii=False, sort_keys=True)}
                    if name in ("Task", "Subagent"):
                        ev["agent"] = clip(inp.get("description") or inp.get("prompt") or "", 120)
                    yield ev
                    for path, _ in skill_reads(f"view_file {inp.get('path') or inp.get('file_path') or ''}"):
                        yield {"k": "skill_loaded", "path": path}

    def subagents(self):
        sdir = os.path.join(os.path.dirname(self.path), "subagents")
        out = []
        for f in sorted(os.listdir(sdir)) if os.path.isdir(sdir) else []:
            if not f.endswith(".jsonl"):
                continue
            calls, desc, start = 0, "", None
            for d in records(os.path.join(sdir, f)):
                for b in text_blocks(d):
                    if d.get("role") == "user" and not desc:
                        desc, start = query(b.get("text", "")), stamp(b.get("text", ""))
                    calls += b.get("type") == "tool_use"
            out.append({"desc": desc or f[:-6], "type": "subagent", "start": start, "model": "unknown",
                        "tokens": 0, "calls": calls, "wall": 0})
        return out
