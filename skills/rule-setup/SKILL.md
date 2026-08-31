---
name: rule-setup
description: Install the bundled agent conventions into a project's CLAUDE.local.md, plus an AGENTS.md entry point. Explicit invocation only.
disable-model-invocation: true
---
# rule-setup

Assemble, never author. Conventions live verbatim in `assets/`; `cat` them together → every project gets byte-identical file. No rewrite, translate, trim, reorder, or reproduce from memory.

| Fragment | Section | Required |
|---|---|---|
| `assets/core.md` | title + `## Core` — Language / Safety / Git | yes |
| `assets/karpathy.md` | `## Karpathy` | ask |
| `assets/gsd.md` | `## GSD` | ask |
| `assets/matt.md` | `## Matt` | ask |
| `assets/superpowers.md` | `## Superpowers` | ask |

Order fixed: core → karpathy → gsd → matt → superpowers. Skip unselected fragments.

When Superpowers is selected, its optional subagent bundles map to project-level directories as follows:

| Bundle | Source | Project target |
|---|---|---|
| Claude Code | `assets/subagents/claude/` | `.claude/agents/` |
| Codex | `assets/subagents/codex/` | `.codex/agents/` |
| Cursor | `assets/subagents/cursor/` | `.cursor/agents/` |

## Workflow

**1. Locate project root.** Git root, else working directory; user-given path wins.

**2. Show Core, then ask.** Print `assets/core.md` in full. Ask whether to include Karpathy, GSD, Matt, and Superpowers in one user-facing question, summarizing each in a sentence; include only opted-in fragments, and include GSD/Matt/Superpowers only if the project runs those workflows.

**3. If Superpowers was selected, ask about subagents.** Ask a separate user-facing question with three checkboxes — Claude Code, Codex, and Cursor — and allow any combination, including none. Explain that each selected option installs every file in its corresponding `assets/subagents/<tool>/` bundle to the project target in the table above.

**4. Assemble and write `CLAUDE.local.md`.** Always replace it with the selected fragments in fixed order; do not read or preserve the old file. Add the trailing blank line and verify the result matches the selected concatenation.

**5. Install selected subagents.** For each checked tool, create its project target directory if needed and copy every file under the matching `assets/subagents/<tool>/` directory to it, preserving each filename and file contents byte-for-byte. Leave identical existing files untouched. Before replacing any existing file with different contents, show the conflict and ask for confirmation; never silently overwrite active edits or delete unrelated files. Skip this step when Superpowers is not selected or no subagent checkbox is checked.

**6. Ensure `CLAUDE.md` and `AGENTS.md`.** Leave existing files unchanged. Otherwise create `CLAUDE.md` with only `# Development Guidelines`, and `AGENTS.md` with exactly:

```text
@CLAUDE.md
@CLAUDE.local.md
```

**7. Report** written/untouched files, included/declined sections, selected subagent bundles, and the exact project target directories installed (or any conflicts left unresolved).
