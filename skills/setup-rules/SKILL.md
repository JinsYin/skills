---
name: setup-rules
description: Conduct an interactive interview, then install selected agent conventions, adapters, and sensitive-file read restrictions into a project. Explicit invocation only.
disable-model-invocation: true
---

# setup-rules

Assemble, never author. Conventions live verbatim in `assets/conventions/`; concatenate selected files byte-for-byte in the fixed order. Merge sensitive-file restrictions into native Agent configuration without replacing unrelated settings.

Interactive interview required: ask, wait, clarify, and confirm the final manifest before writing. Never infer optional selections from project evidence or defaults. Ask at most four focused questions per round; leave ambiguous items pending.

| Category | Source | Target | Condition |
|---|---|---|---|
| Conventions | `assets/conventions/*.md` | `CLAUDE.local.md` | core required; others independently selectable |
| Subagents | `assets/adapters/<tool>/agents/` | `.<tool>/agents/` | per tool/workflow |
| Cursor adapter | `assets/adapters/cursor/rules/`, `assets/adapters/cursor/hooks/`, `assets/adapters/cursor/hooks.json` | `.cursor/rules/`, `.cursor/hooks/`, `.cursor/hooks.json` | independently selectable |
| Antigravity adapter | `assets/adapters/antigravity/gemini.md` | `GEMINI.md` | independently selectable |
| Sensitive-file restrictions | `references/sensitive-file-access.md` | native Agent configuration | default set plus optional extras |

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
| Cursor general-purpose | `assets/adapters/cursor/agents/general-purpose.md` | `.cursor/agents/general-purpose.md` | independently selectable |
| Superpowers agents | `assets/adapters/<tool>/agents/superpowers-*` | `.<tool>/agents/` | only when Superpowers is selected |

Cursor adapter mapping:

| Adapter file | Project target |
|---|---|
| `assets/adapters/cursor/rules/subagent-model-policy.mdc` | `.cursor/rules/subagent-model-policy.mdc` |
| `assets/adapters/cursor/hooks/enforce-subagent-model.sh` | `.cursor/hooks/enforce-subagent-model.sh` |
| `assets/adapters/cursor/hooks.json` | merged into `.cursor/hooks.json` |

The Cursor adapter constrains Cursor subagent `model` and `effort` only. It is not Superpowers-specific; SDD is merely one workflow that may create Cursor subagents. Its selection is independent from agent definitions under `assets/adapters/cursor/agents/`. Do not create a Superpowers-specific model rule, command, wrapper, or model profile directory.

The Antigravity adapter copies `assets/adapters/antigravity/gemini.md` to the project-root `GEMINI.md`. The file contains general, composable rules.

## Workflow

**1. Locate project root.** Git root, else working directory; user-given path wins.

**2. Start the interview with Core.** Print `assets/conventions/core.md` in full. Ask whether to include optional conventions (Vibecoding, Ponytail, Karpathy, GSD, Matt and Superpowers), briefly summarize each, and offer GSD/Superpowers only when used. Wait for the response.

**3. Ask about Cursor general-purpose.** Independently ask whether to install `assets/adapters/cursor/agents/general-purpose.md` to `.cursor/agents/general-purpose.md`.

**4. If Superpowers was selected, ask about its subagents.** Offer only bundles with files under `assets/adapters/<tool>/agents/`; allow any combination, and copy each match to `.<tool>/agents/`.

**5. If Cursor subagents are in scope from the interview, ask about the Cursor adapter.** Explain that it installs the model/effort rule and fail-closed hook for every Cursor subagent.

**6. Ask about the Antigravity adapter.** Ask whether to install `assets/adapters/antigravity/gemini.md` as the project-root `GEMINI.md`.

**7. Collect sensitive files.** Preselect every project file named `.env`, `.env.dev`, `.env.test`, or `.env.prod`. Ask for extra project-relative files or directories. Empty means only this set; remove it only by explicit opt-out. Never infer beyond it or read protected contents. Follow [sensitive-file access controls](references/sensitive-file-access.md).

**8. Ask about Git tracking.** For applicable `.<tool>/`, `.agent/` (Antigravity) and `.agents/`, offer: (1) track all; (2) ignore all and untrack with `git rm -r --cached`, preserving local files; (3) track all except each `skills/` subtree—add those exact directories to `.gitignore` and untrack their tracked files; (4) custom. Never infer a choice.

**9. Confirm the manifest.** List outputs, sensitive targets, external settings, per-directory Git choices, exact ignore entries, and tracked removals. Confirm before writing.

**10. Assemble and write `CLAUDE.local.md`.** Always replace it with the selected files in fixed order; do not read or preserve the old file. Add the trailing blank line and verify the result matches the selected concatenation.

**11. Install selected subagents, adapters, and rules.** Copy only selected agent files and exact adapter mappings; never recursively copy an `assets/adapters/<tool>/` directory. Create target directories if needed and copy files byte-for-byte. For the Antigravity adapter, copy `assets/adapters/antigravity/gemini.md` to the project-root `GEMINI.md`. Merge the selected Cursor hook into an existing `.cursor/hooks.json` without dropping unrelated hooks. Before replacing a different existing file, show the conflict and ask for confirmation; never silently overwrite active edits or delete unrelated files.

**12. Apply Git decisions.** Add confirmed ignore entries and run `git rm -r --cached` on declined tracked files, preserving local files and unrelated rules. Stop for unmanaged active files; never rewrite history, delete worktree files, or commit/push without authorization.

**13. Install sensitive-file restrictions.** Merge the confirmed denies per the reference. Preserve unrelated or stricter settings; stop on incompatible policy. Report unenforced Antigravity UI and Cursor terminal/MCP paths.

**14. Ensure `CLAUDE.md` and `AGENTS.md`.** Leave existing files unchanged. Otherwise create `CLAUDE.md` with only `# Project Conventions`, and `AGENTS.md` with exactly:

```text
@CLAUDE.local.md
@CLAUDE.md
```

**15. Validate and report.** Parse changed JSON/TOML, run available offline config-load checks, and test ignore matching without reading secrets. Report selections, changes, protected paths, limitations, Git decisions, and conflicts.
