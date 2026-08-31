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

Optional subagents map to project-level directories as follows:

| Agent bundle | Source | Project target | Condition |
|---|---|---|---|
| Cursor general-purpose | `assets/subagents/cursor/general-purpose.md` | `.cursor/agents/general-purpose.md` | independently selectable |
| Superpowers agents | `assets/subagents/<tool>/superpowers-*.md` | `.<tool>/agents/` | only when Superpowers is selected |

Only offer bundles whose source files exist; do not hard-code unavailable tools.

## Workflow

**1. Locate project root.** Git root, else working directory; user-given path wins.

**2. Show Core, then ask.** Print `assets/core.md` in full. Ask whether to include Karpathy, GSD, Matt, and Superpowers in one user-facing question, summarizing each in a sentence; include only opted-in fragments, and include GSD/Matt/Superpowers only if the project runs those workflows.

**3. Ask about Cursor general-purpose.** Independently ask whether to install `assets/subagents/cursor/general-purpose.md` to `.cursor/agents/general-purpose.md`.

**4. If Superpowers was selected, ask about its subagents.** Offer only available tool bundles, allow any combination including none, and explain that each selected bundle installs its `superpowers-*.md` files to `.<tool>/agents/`.

**5. Assemble and write `CLAUDE.local.md`.** Always replace it with the selected fragments in fixed order; do not read or preserve the old file. Add the trailing blank line and verify the result matches the selected concatenation.

**6. Install selected subagents.** Create target directories if needed and copy files byte-for-byte. Leave identical files untouched. Before replacing a different existing file, show the conflict and ask for confirmation; never silently overwrite active edits or delete unrelated files.

**7. Ensure `CLAUDE.md` and `AGENTS.md`.** Leave existing files unchanged. Otherwise create `CLAUDE.md` with only `# Development Guidelines`, and `AGENTS.md` with exactly:

```text
@CLAUDE.local.md
@CLAUDE.md
```

**8. Report** written/untouched files, included/declined sections, selected subagent bundles, exact target directories, and unresolved conflicts.
