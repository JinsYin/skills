---
name: claude-local
description: Install the bundled agent conventions into a project's CLAUDE.local.md, plus an AGENTS.md entry point. Explicit invocation only.
disable-model-invocation: true
---
# claude-local

Assemble, never author. Conventions live verbatim in `assets/`; `cat` them together → every project gets byte-identical file. No rewrite, translate, trim, reorder, or reproduce from memory.

| Fragment | Section | Required |
|---|---|---|
| `assets/core.md` | title + `## Core` — Language / Safety / Git | yes |
| `assets/gsd.md` | `## GSD` | ask |
| `assets/superpowers.md` | `## Superpowers` | ask |

Order fixed: core → gsd → superpowers. Skip unselected fragments.

## Workflow

**1. Locate project root.** Git root, else working directory; user-given path wins.

**2. Show Core, then ask.** Print `assets/core.md` in full — users opt out only after seeing every rule. Then ask both optional sections in one AskUserQuestion (multi-select), summarizing each in a sentence, not quoting: GSD prefers `gsx-` extended skills; Superpowers sets handoff timing + spec/plan file layout. Take either only if project actually runs that workflow.

**3. Handle existing CLAUDE.local.md.** Always replace with assembled output. No read, compare, preserve, or confirm before overwrite.

**4. Write CLAUDE.local.md.** From `assets/`, dropping declined fragments:

```bash
{ cat core.md gsd.md superpowers.md; echo; } > <project-root>/CLAUDE.local.md
```

`echo` gives trailing blank line every file here ends with. Then `diff` result against same concatenation → confirm nothing mangled blank lines or punctuation.

**5. CLAUDE.md.** Leave alone if exists. Else create holding just heading — AGENTS.md points at it, so must exist even empty:

```markdown
# Development Guidelines
```
**6. AGENTS.md.** Leave alone if exists — no appending. Else create with exactly these two lines:

```markdown
@CLAUDE.md
@CLAUDE.local.md
```

**7. Report** which files written or left untouched, which sections CLAUDE.local.md carries, which optional sections declined → user knows rerun adds them.