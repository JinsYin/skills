---
name: version-release
description: "Cut a SemVer release — bump every module's version in lockstep, promote CHANGELOG.md, commit, tag, push to origin. Args `major|minor|patch|<x.y.z>`; none → level inferred from `[Unreleased]`, confirmed with user. Invoke only on explicit request: the user, another skill, or a project convention asking for a release."
---
# version-release

## 1. Gate

Stop with a one-line note when any holds:

- Not a git repo, or HEAD detached.
- No commits since the last tag (`git describe --tags --abbrev=0`; no tag → all history counts).
- CI tooling owns releases — `.releaserc*`, `release-please-config.json`, `.changeset/`, `maven-release-plugin`, `axion-release`. A hand bump would fight it.

Uncommitted changes from the just-finished work → commit them on their own first. Any other uncommitted change → stop and ask, leaving it untouched.

## 2. Version

Explicit `x.y.z` used as-is; `major|minor|patch` bumps last tag. No tag yet → no argument releases current project version minus `-SNAPSHOT` as-is; argument bumps it. Follow the existing tag style (`v1.2.3` vs `1.2.3`); default `v`. Tag already exists → stop.

No argument, tag exists → infer level:

- Evidence: `[Unreleased]` in root `CHANGELOG.md`, plus user-facing commits since last tag missing from it (Conventional Commits type).
- `minor`: any `Added`, `Changed`, `Removed`, `feat`, or breaking change. Else `patch` (`Fixed`, `Security`, `Deprecated`, `fix`, `perf`, ...).
- `major` needs explicit argument: 1.0+ major is a deliberate call; 0.x breaks stay `minor`. Breaking change on ≥1.0.0 → note `major` may fit.
- Ask user to confirm level, next version, and the entries behind it; change nothing until answered. Answer names another level → use it.

## 3. Bump every module in lockstep

One project, one version: every module gets the new version, untouched ones included, so artifacts built from one commit always agree. Find every version declaration first (`git ls-files` for `package.json`, `pom.xml`, `build.gradle*`, `gradle.properties`, `pyproject.toml`, `Cargo.toml`, `VERSION`, ...), then:

| Stack | How |
|---|---|
| npm/pnpm/yarn | `npm version <v> --no-git-tag-version` in root and each workspace (`--workspaces --include-workspace-root`); refresh lockfile with project's package manager. |
| Maven | From topmost `pom.xml` dir: `mvn -q versions:set -DnewVersion=<v> -DprocessAllModules -DgenerateBackupPoms=false`. Build uses `${revision}` → edit `<revision>` property instead. |
| Gradle | Edit `version=` in `gradle.properties`, or `version = "..."` in root `build.gradle(.kts)` / `allprojects {}`; check subprojects that override. |
| Other | Edit manifest version field; refresh lockfile. |

Release versions drop `-SNAPSHOT`. Done when grepping tracked manifests for the old version finds no hit that is this project's own version.

## 4. CHANGELOG.md

Day-to-day entries accumulate under `[Unreleased]` in root `CHANGELOG.md` ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/), in the file's existing language); the release closes that section. Missing → create.

- Backfill until every user-facing commit since the last tag (feat, fix, perf, breaking change) has an entry.
- Rename `[Unreleased]` to `[<tag>] - <YYYY-MM-DD>`, open a new empty one above.
- Bottom link refs present (`[Unreleased]: .../compare/...`) → point `[Unreleased]` at `<tag>...HEAD`, add a `[<tag>]` compare link.

## 5. Commit and tag

```bash
git add -u && git add CHANGELOG.md   # tracked edits + CHANGELOG only, so untracked strays stay out of the release
git commit -m "chore(release): <tag>"   # follow the project's commit-language convention
git tag -a <tag> -m "<tag>"
```

## 6. Push to `origin`

`origin` exists → push without asking, only this branch and this tag:

```bash
git push origin HEAD <tag>
```

No `origin` (no remote, or other remotes only) → ask which remote to push to, or whether to skip; push only after the answer.

Push rejected → stop and report, keeping the local commit and tag as-is; reconciling with the remote is the user's call.

Finish with a summary: version, files changed, changelog excerpt, push result.
