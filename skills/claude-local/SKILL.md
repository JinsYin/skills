---
name: claude-local
description: Install the bundled agent conventions into a project's CLAUDE.local.md, plus an AGENTS.md entry point. Explicit invocation only.
disable-model-invocation: true
---

# claude-local

Assemble, never author. The conventions live verbatim in `assets/`; `cat` them together so every project gets a byte-identical file. Do not rewrite, translate, trim, reorder, or reproduce them from memory.

| Fragment | Section | Required |
|---|---|---|
| `assets/core.md` | title + `## Core` — Language / Safety / Git | yes |
| `assets/gsd.md` | `## GSD` | ask |
| `assets/superpowers.md` | `## Superpowers` | ask |

Order is fixed: core → gsd → superpowers. Skip unselected fragments.

## Workflow

**1. Locate the project root.** Git root, else the working directory; a user-given path wins.

**2. Show Core, then ask.** Print `assets/core.md` in full — users can only opt out knowingly after seeing every rule. Then ask about both optional sections in one AskUserQuestion (multi-select), summarizing each in a sentence rather than quoting it: GSD prefers `gsx-` extended skills; Superpowers sets handoff timing and spec/plan file layout. Either is worth taking only if the project actually runs that workflow.

**3. Handle an existing CLAUDE.local.md.** Always replace it with the assembled output. Do not read, compare, preserve, or ask for confirmation before overwriting it.

**4. Write CLAUDE.local.md.** From `assets/`, dropping declined fragments:

```bash
{ cat core.md gsd.md superpowers.md; echo; } > <project-root>/CLAUDE.local.md
```

The `echo` gives the trailing blank line every file written here ends with. Then `diff` the result against the same concatenation to confirm nothing mangled the blank lines or punctuation.

**5. CLAUDE.md.** Leave it alone if it exists. If not, create it holding just a heading — AGENTS.md points at it, so it has to exist even while empty:

```markdown
# Development Guidelines
```
**6. AGENTS.md.** Leave it alone if it exists — no appending. If not, create it with exactly these two lines:

```markdown
@CLAUDE.md
@CLAUDE.local.md
```

**7. Report** which files were written or left untouched, which sections CLAUDE.local.md carries, and which optional sections were declined so the user knows they can rerun to add them.
