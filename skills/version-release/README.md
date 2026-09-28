# version-release

仅显式调用（手动或由其他 skill / 约定调用）的本地发版：按参数 `major|minor|patch|x.y.z` 升版（默认 `patch`），所有模块（npm / Maven / Gradle 等）统一版本，提升 `CHANGELOG.md` 的 `[Unreleased]`，提交并打 tag；push 前必须征得同意。

## 参考

- [Lobehub Version Release Workflow](https://www.skills.sh/lobehub/lobehub/version-release)
