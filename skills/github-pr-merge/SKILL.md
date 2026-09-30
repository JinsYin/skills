---
name: github-pr-merge
description: Interactively review and squash-merge open GitHub PRs via `gh` — pick from open PRs (oldest first), summarize the PR and its linked Issue, review it (with extra checks for skill edits such as `self-improve` PRs), then merge, reject, or request changes, and close the Issue. Use whenever the user wants to review, triage, or merge open PRs, or process the PRs `self-improve` opened. Args `[<pr#>] [-R <owner/repo>]`.
---

# github-pr-merge

Pick a PR → understand it → review → user decides → merge and close the Issue → next PR.

Repo: `-R <owner/repo>` if given, else the current repo (`gh repo view --json nameWithOwner,defaultBranchRef`). Pass `-R` to every `gh` call.

## 1. Pick a PR

A `<pr#>` argument skips this step. Otherwise:

```bash
gh pr list -R <repo> --state open --limit 200 \
  --json number,title,createdAt,author,labels,headRefName --jq 'sort_by(.createdAt)'
```

Ask with the ask-user tool: the 3 oldest PRs as options (`#<n> <title> · <author> · <date> · <labels>`), plus a last option "List all open PRs". On that choice, print the full numbered list and let the user pick. No open PRs → say so and stop.

## 2. Understand

```bash
gh pr view <n> -R <repo> --json number,title,body,author,headRefName,headRefOid,baseRefName,isCrossRepository,mergeable,mergeStateStatus,statusCheckRollup,closingIssuesReferences,commits,files
gh pr diff <n> -R <repo>
gh issue view <i> -R <repo> --comments   # each closing Issue, plus any `#<i>` the body only mentions
```

Summarize briefly: the problem (from the Issue), what the PR changes, files touched.

## 3. Review

Report findings per layer; a failed check is a finding, not an automatic reject.

1. **Gate** — conflicts (`mergeable`), CI (`statusCheckRollup`), files outside the PR's stated scope, commit style and `CHANGELOG.md` per the repo's `CLAUDE.md`/`AGENTS.md`.
2. **Intent** — does the diff actually solve the Issue, and nothing else?
3. **Skill edits** (any `skills/**/SKILL.md` or skill resource changed) — read the whole target skill on the latest default branch, not just the diff:
   - Evidence: does the Issue's evidence meet the bar (strong once, weak ≥2), or is it a one-off slip or project-specific fact? Rules fitted to one incident make every future load pay for them.
   - Duplication/conflict: already covered on the default branch, or contradicts another passage or skill?
   - Minimality: smallest owning passage, growth ≤ ~20%, no restructuring, same language and tone, reasons over ALL-CAPS MUSTs.
   - `description` changed: would it over- or under-trigger?

**Conflicts**: resolve before deciding, since the merge needs a conflict-free branch. Same-repo branches only (`isCrossRepository` → report and stop). In a scratchpad `git worktree` of the head branch, rebase onto `origin/<base>`; for `CHANGELOG.md` keep both sides' entries in their sections; ask the user about any other conflict. Then `git push --force-with-lease`, remove the worktree, and re-check.

## 4. Decide

Post the review as a PR comment (`gh pr comment <n> --body-file <f>`) — authors cannot approve their own PRs, so the comment is the review record. Then ask the user, recommending one:

- **Merge** — `gh pr merge <n> -R <repo> --squash --match-head-commit <reviewed-sha>`. The SHA guard refuses to merge commits you did not review.
- **Request changes** — list the concrete edits; with the user's consent, apply them on the head branch (worktree as above, commit per repo conventions), push, and return to step 3.
- **Reject** — `gh pr close <n> --comment "<reason>"`, then close each linked Issue with `--reason "not planned"` and the reason, so `self-improve`'s dedupe skips it next time.

## 5. Wrap up

- After a merge, check each closing Issue; if still open, `gh issue close <i> --comment "Fixed by #<n>"`. Issues only mentioned (not `Closes`) → ask before closing.
- If cwd is a checkout of this repo on a clean default branch, `git pull --ff-only`; otherwise just note it.
- Return to step 1 for the next PR until the user stops.
