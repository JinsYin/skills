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

## Workflow

**1. Locate project root.** Git root, else working directory; user-given path wins.

**2. Show Core, then ask.** Print `assets/core.md` in full. Ask whether to include Karpathy, GSD, Matt, and Superpowers in one user-facing question, summarizing each in a sentence; include only opted-in fragments, and include GSD/Matt/Superpowers only if the project runs those workflows.

**3. Assemble and write `CLAUDE.local.md`.** Always replace it with the selected fragments in fixed order; do not read or preserve the old file. Add the trailing blank line and verify the result matches the selected concatenation.

**4. Ensure `CLAUDE.md` and `AGENTS.md`.** Leave existing files unchanged. Otherwise create `CLAUDE.md` with only `# Development Guidelines`, and `AGENTS.md` with exactly:

```text
@CLAUDE.md
@CLAUDE.local.md
```

**5. Report** written/untouched files and included/declined sections.
