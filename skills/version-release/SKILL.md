---
name: version-release
description: Cut a local SemVer release — bump every module's version (npm/pnpm package.json, Maven pom.xml, Gradle, others) in lockstep, promote CHANGELOG.md, commit, and tag. Args `major|minor|patch|<x.y.z>`, default `patch`. Explicit invocation only — run when the user or another skill/convention calls it; never auto-invoke.
---

# version-release

Turn the commits since the last tag into one versioned, tagged release. Everything stays local until the user approves a push.

## 1. Gate

Stop with a one-line note when any holds:

- Not a git repo, or no commits since the last tag (`git describe --tags --abbrev=0`; no tag → all history).
- The project delegates releases to CI tooling — `.releaserc*`, `release-please-config.json`, `.changeset/`, `maven-release-plugin`, `axion-release`. Hand-bumping would fight it.

Uncommitted changes: if they belong to the just-finished work, commit them first; otherwise stop and ask.

## 2. Version

Bump the last tag (or, with no tag, the current project version minus `-SNAPSHOT`) by the argument; no argument → `patch`. An explicit `x.y.z` is used as-is. Follow the existing tag style (`v1.2.3` vs `1.2.3`); default to `v`.

## 3. Bump every module to the same version

One project, one version: update all modules, even ones the change never touched, so artifacts from the same commit always agree. Find every version declaration first (`git ls-files` for `package.json`, `pom.xml`, `build.gradle*`, `gradle.properties`, `pyproject.toml`, `Cargo.toml`, `VERSION`, ...), then:

| Stack | How |
|---|---|
| npm/pnpm/yarn | `npm version <v> --no-git-tag-version` in root and each workspace (`--workspaces --include-workspace-root`); refresh the lockfile with the project's package manager. |
| Maven | From the topmost `pom.xml` directory: `mvn -q versions:set -DnewVersion=<v> -DprocessAllModules -DgenerateBackupPoms=false`. If the build uses `${revision}`, edit the `<revision>` property instead. |
| Gradle | Edit `version=` in `gradle.properties`, or `version = "..."` in root `build.gradle(.kts)` / `allprojects {}`; check subprojects that override it. |
| Other | Edit the manifest's version field; refresh its lockfile. |

Release versions drop `-SNAPSHOT`. Verify: grep tracked manifests for the old version — any hit that is this project's own version is a missed module.

## 4. CHANGELOG.md

Day-to-day entries accumulate under `[Unreleased]` in root `CHANGELOG.md` ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/), in the file's existing language); releasing closes that section. Create the file if missing.

- Backfill notable changes from commits since the last tag that `[Unreleased]` missed.
- Rename `[Unreleased]` to `[<tag>] - <YYYY-MM-DD>` and open a new empty one above it.

## 5. Commit and tag

```bash
git add -A && git commit -m "chore(release): <tag>"   # follow the project's commit-language convention
git tag -a <tag> -m "<tag>"
```

## 6. Push — only with consent

No `git remote` → stop and report. Otherwise summarise (version, files changed, changelog excerpt) and ask whether to push. On yes:

```bash
git push --all <remote> && git push --tags <remote>
```

A pushed tag may trigger deploys and cannot be quietly withdrawn, so never push without that answer.
