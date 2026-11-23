
## Prompts

- Record user prompts sent to LLM into project-root `PROMPTS.md` upon completion of:
  - **SDD workflows**:
    - **Addy**: `/spec-driven-development` (`/spec`), `/planning-and-task-breakdown` (`/plan`), `/incremental-implementation` (`/build`), `/test-driven-development` (`/test`), `/code-simplification` (`/code-simplify`), and their underlying skills (`spec-driven-development`, `planning-and-task-breakdown`, `incremental-implementation`, `test-driven-development`, `code-simplification`).
    - **GSD**: `gsdspec` (`gsdspec --<mode>`), `/gsd:*` commands, and any `gsd-*` skills (e.g. `gsd-fast`, `gsd-quick`).
    - **Matt**: `mattpocock/skills` commands and skills (`/setup-matt-pocock-skills`, `/to-spec`, `/to-tickets`, `/implement`, `/implement-spec`, `/tdd`, `/code-review`, `/retro`).
    - **Superpowers**: `using-superpowers`, `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `test-driven-development`, `systematic-debugging`.
  - **Project skills (`jinsyin/skills`)**: any skill sourced from `jinsyin/skills` (e.g. `write-fspec`, `re-spec`, `design-to-code`, `backfill-prototype`, `self-improve`, `setup-rules`, `version-release`, `ideate`, `doc-to-md`, `github-pr-merge`).
- `PROMPTS.md` format:
  - Header: `# PROMPTS`
  - Two-column table: `| Time | Prompt |`
  - Time column: `YYYY-MM-DD HH:mm` (e.g. `2026-11-23 10:50`), recorded at task completion or stage commit.
  - Prompt column: fix typos and formatting only; preserve original intent; use `<br>` for line breaks; format multiple items as a list.
- Within the same session, if a follow-up prompt amends, clarifies, or refines a previous prompt, merge it directly into the initial entry as a single cohesive list or paragraph rather than appending disconnected fragments.
