---
name: github-pr-merge
description: Interactively review and squash-merge open GitHub PRs via `gh` — pick from open PRs (oldest first), summarize PR + linked Issue, review (extra checks for skill edits like `self-improve` PRs), then merge, reject, or request changes, close Issue. Use whenever user wants to review, triage, or merge open PRs, or process PRs `self-improve` opened. Args `[<pr#>] [-R <owner/repo>]`.
---
# github-pr-merge

Pick PR → understand → review → user decides → merge, close Issue → next PR.

Repo: `-R <owner/repo>` if given, else current repo (`gh repo view --json nameWithOwner,defaultBranchRef`). Pass `-R` to every `gh` call.

## 1. Pick a PR

`<pr#>` arg skips step. Else:

```bash
gh pr list -R <repo> --state open --limit 200 \
  --json number,title,createdAt,author,labels,headRefName --jq 'sort_by(.createdAt)'
```

Ask via ask-user tool: 3 oldest PRs as options (`#<n> <title> · <author> · <date> · <labels>`), plus last option "List all open PRs". On that choice, print full numbered list, user picks. No open PRs → say so, stop.

## 2. Understand

```bash
gh pr view <n> -R <repo> --json number,title,body,author,headRefName,headRefOid,baseRefName,isCrossRepository,mergeable,mergeStateStatus,statusCheckRollup,closingIssuesReferences,commits,files
gh pr diff <n> -R <repo>
gh issue view <i> -R <repo> --comments   # each closing Issue, plus any `#<i>` the body only mentions
```

Brief summary: problem (from Issue), what PR changes, files touched.

## 3. Review

Report findings per layer; failed check = finding, not auto-reject.

1. **Gate** — conflicts (`mergeable`), CI (`statusCheckRollup`), files outside PR's stated scope, commit style and `CHANGELOG.md` per repo's `CLAUDE.md`/`AGENTS.md`.
2. **Intent** — diff actually solves Issue, nothing else?
3. **Skill edits** (any `skills/**/SKILL.md` or skill resource changed) — read whole target skill on latest default branch, not just diff:
   - Evidence: Issue evidence meets bar (strong once, weak ≥2), or one-off slip / project-specific fact? Rules fitted to one incident make every future load pay.
   - Duplication/conflict: already covered on default branch, or contradicts other passage/skill?
   - Minimality: smallest owning passage, growth ≤ ~20%, no restructuring, same language/tone, reasons over ALL-CAPS MUSTs.
   - `description` changed: over- or under-trigger?

**Conflicts**: resolve before deciding; merge needs conflict-free branch. Same-repo branches only (`isCrossRepository` → report, stop). In scratchpad `git worktree` of head branch, rebase onto `origin/<base>`; `CHANGELOG.md` → keep both sides' entries in their sections; ask user about other conflicts. Then `git push --force-with-lease`, remove worktree, re-check.

## 4. Decide

Post review as PR comment (`gh pr comment <n> --body-file <f>`) — authors can't approve own PRs, so comment = review record. Then ask user, recommend one:

- **Merge** — `gh pr merge <n> -R <repo> --squash --match-head-commit <reviewed-sha>`. SHA guard refuses unreviewed commits.
- **Request changes** — list concrete edits; with user consent, apply on head branch (worktree as above, commit per repo conventions), push, back to step 3.
- **Reject** — `gh pr close <n> --comment "<reason>"`, then close each linked Issue with `--reason "not planned"` + reason, so `self-improve` dedupe skips it next time.

## 5. Wrap up

- After merge, check each closing Issue; still open → `gh issue close <i> --comment "Fixed by #<n>"`. Issues only mentioned (not `Closes`) → ask before closing.
- cwd is checkout of this repo on clean default branch → `git pull --ff-only`; else just note.
- Back to step 1 for next PR until user stops.
