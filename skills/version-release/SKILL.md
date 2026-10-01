---
name: version-release
description: Cut local SemVer release — bump every module's version (npm/pnpm package.json, Maven pom.xml, Gradle, others) in lockstep, promote CHANGELOG.md, commit, tag. Args `major|minor|patch|<x.y.z>`, default `patch`. Explicit invocation only — run when user or another skill/convention calls it; never auto-invoke.
---
# version-release

Turn commits since last tag into one versioned, tagged release. All local until user approve push.

## 1. Gate

Stop with one-line note when any hold:

- Not git repo, or no commits since last tag (`git describe --tags --abbrev=0`; no tag → all history).
- Project delegate releases to CI tooling — `.releaserc*`, `release-please-config.json`, `.changeset/`, `maven-release-plugin`, `axion-release`. Hand-bump would fight it.

Uncommitted changes: belong to just-finished work → commit first; else stop and ask.

## 2. Version

Bump last tag (no tag → current project version minus `-SNAPSHOT`) by argument; no argument → `patch`. Explicit `x.y.z` used as-is. Follow existing tag style (`v1.2.3` vs `1.2.3`); default `v`.

## 3. Bump every module to the same version

One project, one version: update all modules, even untouched ones, so artifacts from same commit always agree. Find every version declaration first (`git ls-files` for `package.json`, `pom.xml`, `build.gradle*`, `gradle.properties`, `pyproject.toml`, `Cargo.toml`, `VERSION`, ...), then:

| Stack | How |
|---|---|
| npm/pnpm/yarn | `npm version <v> --no-git-tag-version` in root and each workspace (`--workspaces --include-workspace-root`); refresh lockfile with project's package manager. |
| Maven | From topmost `pom.xml` dir: `mvn -q versions:set -DnewVersion=<v> -DprocessAllModules -DgenerateBackupPoms=false`. Build uses `${revision}` → edit `<revision>` property instead. |
| Gradle | Edit `version=` in `gradle.properties`, or `version = "..."` in root `build.gradle(.kts)` / `allprojects {}`; check subprojects that override. |
| Other | Edit manifest version field; refresh lockfile. |

Release versions drop `-SNAPSHOT`. Verify: grep tracked manifests for old version — any hit that is this project's own version = missed module.

## 4. CHANGELOG.md

Day-to-day entries accumulate under `[Unreleased]` in root `CHANGELOG.md` ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/), in file's existing language); release closes that section. Missing → create.

- Backfill notable changes from commits since last tag that `[Unreleased]` missed.
- Rename `[Unreleased]` to `[<tag>] - <YYYY-MM-DD>`, open new empty one above.

## 5. Commit and tag

```bash
git add -A && git commit -m "chore(release): <tag>"   # follow the project's commit-language convention
git tag -a <tag> -m "<tag>"
```

## 6. Push — only with consent

No `git remote` → stop and report. Else summarise (version, files changed, changelog excerpt), ask whether push. On yes:

```bash
git push --all <remote> && git push --tags <remote>
```

Pushed tag may trigger deploys, can't quietly withdraw — never push without that answer.
