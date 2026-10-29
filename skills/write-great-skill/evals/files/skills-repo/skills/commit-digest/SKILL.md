---
name: commit-digest
description: "Summarize the last 7 days of git commits into a Markdown weekly digest grouped by Conventional Commits type. Use when the user asks for a weekly report, 周报, or commit summary."
---
# commit-digest

1. Collect: `git log --since='7 days ago' --pretty='%h|%an|%s'`.
2. Group by type prefix (`feat`, `fix`, `docs`, other); drop merge commits.
3. Write `digest.md`: one `## <type>` section per group, one bullet per commit: `- <subject> (<hash>, <author>)`.
4. Reply with the count per type.
