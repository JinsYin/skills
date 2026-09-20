#!/usr/bin/env python3
"""
对 markitdown 的原始 Markdown 产物做语义级清理（lint 之前跑）。

markdownlint 只能修机械排版（空行、缩进、行尾空格），下面这几类问题它管不了，
所以在这里用确定性规则处理掉：

  1. 目录块  —— “目录 / Table of Contents” 标题后的连续条目，整理成 markdown 列表，
                把点引线（......）压成单空格。
  2. 裸 JSON —— 一整段能被解析为 JSON 的文本，用 ```json 围栏包起来。
  3. 空表格行 —— 单元格全空的表格行（如 `|  |  |`）删掉，但保留分隔行 `| --- |`。

设计原则：宁可少改也不要改错。规则都偏保守，命中不了就原样放过，绝不破坏内容。
用法：postprocess.py <file.md>  （原地改写）
"""

import json
import re
import sys


FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
TOC_HEADING_RE = re.compile(
    r"^\s{0,3}#{1,6}\s*(目录|目錄|table of contents|contents)\s*$",
    re.IGNORECASE,
)
LIST_ITEM_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
# 点引线 + 末尾页码，例如 "引言 ........... 3"
LEADER_RE = re.compile(r"[.…\s]{2,}(\d+)\s*$")


def iter_fenced_flags(lines):
    """逐行标记是否处于代码围栏内部（含围栏行本身）。"""
    inside = False
    flags = []
    for ln in lines:
        if FENCE_RE.match(ln):
            flags.append(True)      # 围栏行算“内部”，不参与改写
            inside = not inside
        else:
            flags.append(inside)
    return flags


def fence_json_blocks(lines):
    """把未围栏的、可被 json.loads 解析的连续块用 ```json 包起来。"""
    flags = iter_fenced_flags(lines)
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        # 只在非围栏区、且这一行像 JSON 开头时尝试
        if not flags[i] and stripped[:1] in "{[":
            depth = 0
            j = i
            block_end = None
            while j < n and not flags[j]:
                for ch in lines[j]:
                    if ch in "{[":
                        depth += 1
                    elif ch in "}]":
                        depth -= 1
                # 括号收平 → 尝试解析
                if depth <= 0:
                    candidate = "\n".join(lines[i : j + 1]).strip()
                    try:
                        json.loads(candidate)
                        block_end = j
                    except ValueError:
                        block_end = None
                    break
                j += 1
            # 至少两行、或单行但确实是 JSON，才值得围栏（避免把 `{` 一类碎片包进去）
            if block_end is not None and len(lines[i : block_end + 1]) >= 1 and depth <= 0:
                out.append("```json")
                out.extend(lines[i : block_end + 1])
                out.append("```")
                i = block_end + 1
                continue
        out.append(line)
        i += 1
    return out


def drop_empty_table_rows(lines):
    """删掉单元格全为空的表格行；分隔行（含 - 或 :）保留。"""
    out = []
    for line in lines:
        if TABLE_ROW_RE.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # 全空 → 丢弃；分隔行的单元格是 '---'/':--' 非空，自然保留
            if all(c == "" for c in cells):
                continue
        out.append(line)
    return out


def _looks_like_toc_entry(stripped):
    """判断一行是否像目录条目：带点引线/页码，或足够短（标题不会太长）。"""
    if LEADER_RE.search(stripped):
        return True
    return len(stripped) <= 80


def reformat_toc(lines):
    """目录区域（目录标题 → 下一个标题之间）的条目整理成列表。

    markitdown 常把条目转成“空行分隔的独立段落”，所以终止符用“下一个标题”，
    而不是空行。区域内：已是列表项的保留；像条目的转成 `- `（压平点引线、留页码）；
    明显是长正文的原样放过，避免误伤。空行丢弃，交给 lint 重新排布。
    """
    flags = iter_fenced_flags(lines)
    out = []
    i = 0
    n = len(lines)
    while i < n:
        out.append(lines[i])
        if not flags[i] and TOC_HEADING_RE.match(lines[i]):
            j = i + 1
            entries = []
            while j < n and not HEADING_RE.match(lines[j]) and not flags[j]:
                stripped = lines[j].strip()
                if stripped == "":
                    j += 1
                    continue
                if LIST_ITEM_RE.match(lines[j]):
                    entries.append(lines[j])
                elif _looks_like_toc_entry(stripped):
                    entry = LEADER_RE.sub(r" \1", stripped)
                    entry = re.sub(r"\s{2,}", " ", entry).strip()
                    entries.append(f"- {entry}")
                else:
                    # 不像条目的长正文：原样保留
                    entries.append(lines[j])
                j += 1
            # 标题与列表、列表与下一个标题之间各补一个空行，保证幂等且 lint 友好
            if entries:
                out.append("")
                out.extend(entries)
                out.append("")
            i = j
            continue
        i += 1
    return out


def main():
    if len(sys.argv) != 2:
        print("usage: postprocess.py <file.md>", file=sys.stderr)
        return 1
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")

    lines = drop_empty_table_rows(lines)
    lines = fence_json_blocks(lines)
    lines = reformat_toc(lines)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
