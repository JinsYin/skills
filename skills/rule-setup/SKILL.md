---
name: rule-setup
description: Install categorized agent workflow conventions and optional Cursor subagent model enforcement into a project. Explicit invocation only.
disable-model-invocation: true
---
# rule-setup

Assemble, never author. Conventions live verbatim in `assets/`; concatenate selected files so every project gets byte-identical content. Do not rewrite, translate, trim, reorder, or reproduce from memory.

| Category | Source | Target | Condition |
|---|---|---|---|
| Core | `assets/core.md` | `CLAUDE.local.md` | required |
| Workflows | `assets/workflows/*.md` | `CLAUDE.local.md` | independently selectable |
| Subagents | `assets/subagents/<tool>/` | `.<tool>/agents/` | per tool/workflow |
| Cursor adapter | `assets/adapters/cursor/` | `.cursor/rules/`, `.cursor/hooks/`, `.cursor/hooks.json` | independently selectable |

Workflow order is fixed: core → karpathy → gsd → matt → superpowers. Skip unselected files.

Workflow files:

- `assets/workflows/karpathy.md`
- `assets/workflows/gsd.md`
- `assets/workflows/matt.md`
- `assets/workflows/superpowers.md`

Subagent bundles:

| Agent bundle | Source | Project target | Condition |
|---|---|---|---|
| Cursor general-purpose | `assets/subagents/cursor/general-purpose.md` | `.cursor/agents/general-purpose.md` | independently selectable |
| Superpowers agents | `assets/subagents/<tool>/superpowers-*.md` | `.<tool>/agents/` | only when Superpowers is selected |

Cursor adapter mapping:

| Adapter file | Project target |
|---|---|
| `assets/adapters/cursor/subagent-model-policy.mdc` | `.cursor/rules/subagent-model-policy.mdc` |
| `assets/adapters/cursor/enforce-subagent-model.sh` | `.cursor/hooks/enforce-subagent-model.sh` |
| `assets/adapters/cursor/hooks.json` | merged into `.cursor/hooks.json` |

The Cursor adapter constrains Cursor subagent `model` and `effort` only. It is not Superpowers-specific; SDD is merely one workflow that may create Cursor subagents. Do not create a Superpowers-specific model rule, command, wrapper, or model profile directory. Only offer bundles whose source files exist.

## Workflow

**1. Locate project root.** Git root, else working directory; user-given path wins.

**2. Show Core, then ask.** Print `assets/core.md` in full. Ask whether to include Karpathy, GSD, Matt, and Superpowers in one user-facing question, summarizing each in a sentence; include GSD and Superpowers only if the project runs those workflows.

**3. Ask about Cursor general-purpose.** Independently ask whether to install `assets/subagents/cursor/general-purpose.md` to `.cursor/agents/general-purpose.md`.

**4. If Superpowers was selected, ask about its subagents.** Offer only available tool bundles, allow any combination including none, and explain that each selected bundle installs its `superpowers-*.md` files to `.<tool>/agents/`.

**5. If the project uses Cursor subagents, ask about the Cursor adapter.** Explain that it installs the model/effort rule and fail-closed hook for every Cursor subagent, regardless of workflow.

**6. Resolve Git ignore status before writing.** Build an exact manifest and check each singleton output separately: `CLAUDE.local.md`, newly created `CLAUDE.md`/`AGENTS.md`, `.cursor/agents/general-purpose.md`, `.cursor/rules/subagent-model-policy.mdc`, `.cursor/hooks/enforce-subagent-model.sh`, and `.cursor/hooks.json`. Only uniform-prefix bundles such as `.<tool>/agents/superpowers-*` may be enumerated by glob; expand them and check each match. Never check or unignore a directory. For every ignored path, show its rule and ask whether to keep it ignored, add the narrowest exception, or add it and commit; never broaden an exception.

**7. Assemble and write `CLAUDE.local.md`.** Always replace it with the selected files in fixed order; do not read or preserve the old file. Add the trailing blank line and verify the result matches the selected concatenation.

**8. Install selected subagents and adapters.** Create target directories if needed and copy files byte-for-byte. Leave identical files untouched. Merge the selected Cursor hook into an existing `.cursor/hooks.json` without dropping unrelated hooks. Before replacing a different existing file, show the conflict and ask for confirmation; never silently overwrite active edits or delete unrelated files.

**9. Ensure `CLAUDE.md` and `AGENTS.md`.** Leave existing files unchanged. Otherwise create `CLAUDE.md` with only `# Development Guidelines`, and `AGENTS.md` with exactly:

```text
@CLAUDE.local.md
@CLAUDE.md
```

**10. Report** written/untouched files, included/declined categories, selected subagent bundles, Cursor adapter status, Git ignore/commit decision, exact target directories, and unresolved conflicts.
