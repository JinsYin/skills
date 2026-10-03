# 场景评测：2026-10-03

只覆盖本次改变的决策边界及相邻回归；每种派发配置各一个独立批次，无实际发布操作。提示和检查标准均提供给两组，不能据此推断生产成功率或 Token 节省。

| Model（派发参数） | Without | With | Delta |
|---|---|---|---|
| gpt-6.1-sol/medium | 16/16 | 16/16 | +0.0 pp |
| gpt-6-sol/medium | 16/16 | 16/16 | +0.0 pp |
| gpt-6-luna/medium | 15/16 | 16/16 | +6.2 pp |

| Scenario | A Without/With | B Without/With | C Without/With |
|---|---|---|---|
| native-codex | 7/7 → 7/7 | 7/7 → 7/7 | 7/7 → 7/7 |
| native-missing | 5/5 → 5/5 | 5/5 → 5/5 | 5/5 → 5/5 |
| claude-selection | 4/4 → 4/4 | 4/4 → 4/4 | 3/4 → 4/4 |

旧 skill 对照（A）：11/16；修订后：16/16。

新规则未出现全模型失败项或关键场景退步。无 skill 基线很高，因此修订集中在旧指令的范围干扰，没有扩大流程。耗时与 Token：unknown。

检查记录：writing-for-agents 的单点定义与正向行为已应用；未添加新文件导航，现有段落可直接容纳。caveman-compress 只压缩变更 prose，标题及代码块不变。JSON 解析、唯一 ID 与 CLI skill 发现检查通过。原有未变分支未重跑。
