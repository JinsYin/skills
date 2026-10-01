# version-release

发版技能。

## 功能

- 显式调用，即手动或由其他 skill / 约定调用；
- 按参数 `major|minor|patch|x.y.z` 升版，默认 `patch`；
- 所有模块（npm / Maven / Gradle 等）统一版本；
- 提升 `CHANGELOG.md` 的 `[Unreleased]`，提交并打 tag；
- 自动 push 当前分支与本次 tag 到 `origin`；无 remote 或无 `origin` 时先询问。

## 参考

- [Lobehub Version Release Workflow](https://www.skills.sh/lobehub/lobehub/version-release)
