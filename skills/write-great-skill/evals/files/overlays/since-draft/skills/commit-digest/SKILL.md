---
name: commit-digest
description: "Summarize the last 7 days of git commits into a Markdown weekly digest grouped by Conventional Commits type. Use when the user asks for a weekly report, 周报, or commit summary."
---
# commit-digest

Optional argument `--since <date>`: If the user happens to provide a `--since` argument together with a date, then you should make sure to use that date instead of the default value of 7 days ago when you are collecting the commits in step 1. The date can basically be in any format that git itself accepts.

1. Collect: `git log --since='7 days ago' --pretty='%h|%an|%s'`.
2. Group by type prefix (`feat`, `fix`, `docs`, other); drop merge commits.
3. Write `digest.md`: one `## <type>` section per group, one bullet per commit: `- <subject> (<hash>, <author>)`.
4. Reply with the count per type.
