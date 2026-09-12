---
name: setup-rules
description: Install categorized agent workflow conventions and optional agent adapters into a project. Explicit invocation only.
disable-model-invocation: true
---

# setup-rules

Assemble, never author. Conventions live verbatim in `assets/conventions/`; concatenate selected files so every project gets byte-identical content. Do not rewrite, translate, trim, reorder, or reproduce from memory.

| Category | Source | Target | Condition |
|---|---|---|---|
| Conventions | `assets/conventions/*.md` | `CLAUDE.local.md` | core required; others independently selectable |
| Subagents | `assets/subagents/<tool>/` | `.<tool>/agents/` | per tool/workflow |
| Cursor adapter | `assets/adapters/cursor/` | `.cursor/rules/`, `.cursor/hooks/`, `.cursor/hooks.json` | independently selectable |
| Antigravity adapter | `assets/adapters/antigravity/rules/` | `.agent/rules/` | all files, independently selectable |

Convention order is fixed: core → vibecoding → ponytail → karpathy → gsd → matt → superpowers. Skip unselected files.

Convention files:

- `assets/conventions/core.md`
- `assets/conventions/vibecoding.md`
- `assets/conventions/ponytail.md`
- `assets/conventions/karpathy.md`
- `assets/conventions/gsd.md`
- `assets/conventions/matt.md`
- `assets/conventions/superpowers.md`

Subagent bundles:

| Agent bundle | Source | Project target | Condition |
|---|---|---|---|
| Cursor general-purpose | `assets/subagents/cursor/general-purpose.md` | `.cursor/agents/general-purpose.md` | independently selectable |
| Superpowers agents | `assets/subagents/<tool>/superpowers-*.md` | `.<tool>/agents/` | only when Superpowers is selected |

Cursor adapter mapping:

| Adapter file | Project target |
|---|---|
| `assets/adapters/cursor/rules/subagent-model-policy.mdc` | `.cursor/rules/subagent-model-policy.mdc` |
| `assets/adapters/cursor/hooks/enforce-subagent-model.sh` | `.cursor/hooks/enforce-subagent-model.sh` |
| `assets/adapters/cursor/hooks.json` | merged into `.cursor/hooks.json` |

The Cursor adapter constrains Cursor subagent `model` and `effort` only. It is not Superpowers-specific; SDD is merely one workflow that may create Cursor subagents. Do not create a Superpowers-specific model rule, command, wrapper, or model profile directory. Only offer bundles whose source files exist.

The Antigravity adapter copies all files from `assets/adapters/antigravity/rules/` to `.agent/rules/`, preserving relative paths. Rules must be general and composable.

## Workflow

**1. Locate project root.** Git root, else working directory; user-given path wins.

**2. Show Core convention, then ask.** Print `assets/conventions/core.md` in full. Ask whether to include optional conventions (Vibecoding, Ponytail, Karpathy, GSD, Matt and Superpowers) in one user-facing question, summarizing each in a sentence; include GSD and Superpowers only if the project runs those workflows.

**3. Ask about Cursor general-purpose.** Independently ask whether to install `assets/subagents/cursor/general-purpose.md` to `.cursor/agents/general-purpose.md`.

**4. If Superpowers was selected, ask about its subagents.** Offer only available tool bundles, allow any combination including none, and explain that each selected bundle installs its `superpowers-*.md` files to `.<tool>/agents/`.

**5. If the project uses Cursor subagents, ask about the Cursor adapter.** Explain that it installs the model/effort rule and fail-closed hook for every Cursor subagent, regardless of workflow.

**6. Ask about the Antigravity adapter.** Ask whether to install all files in `assets/adapters/antigravity/rules/` to `.agent/rules/`.

**7. Resolve Git ignore status before writing.** Build an exact manifest and check each singleton output separately: `CLAUDE.local.md`, newly created `CLAUDE.md`/`AGENTS.md`, `.cursor/agents/general-purpose.md`, `.cursor/rules/subagent-model-policy.mdc`, `.cursor/hooks/enforce-subagent-model.sh`, and `.cursor/hooks.json`. Map each Antigravity source file to `.agent/rules/<relative-path>` and check each target separately. Only uniform-prefix bundles such as `.<tool>/agents/superpowers-*` may be enumerated by glob; expand them and check each match. Never check or unignore a directory. For every ignored path, show its rule and ask whether to keep it ignored, add the narrowest exception, or add it and commit; never broaden an exception.

**8. Assemble and write `CLAUDE.local.md`.** Always replace it with the selected files in fixed order; do not read or preserve the old file. Add the trailing blank line and verify the result matches the selected concatenation.

**9. Install selected subagents, adapters, and rules.** Create target directories if needed and copy files byte-for-byte. Leave identical files untouched. For the Antigravity adapter, copy all source rules to `.agent/rules/`, preserving relative paths and leaving other rules untouched. Merge the selected Cursor hook into an existing `.cursor/hooks.json` without dropping unrelated hooks. Before replacing a different existing file, show the conflict and ask for confirmation; never silently overwrite active edits or delete unrelated files.

**10. Ensure `CLAUDE.md` and `AGENTS.md`.** Leave existing files unchanged. Otherwise create `CLAUDE.md` with only `# Project Conventions`, and `AGENTS.md` with exactly:

```text
@CLAUDE.local.md
@CLAUDE.md
```

**11. Report** written/untouched files, included/declined categories, selected subagent bundles, Cursor and Antigravity adapter status, Git ignore/commit decision, exact target directories, and unresolved conflicts.
