# write-great-skill

编写与修改 Agent Skill 的端到端工作流与质量标准。

## 功能

- 统一 eval 规则：每个分支与护栏至少一个可校验的 eval，expectations 只断言 skill 带来的增量，至少一个自然语言触发的 eval；
- 按触发方分门控：用户触发在第 1 步后确认，其他 skill 触发全程无人值守，仅改根 `CLAUDE.md`/`AGENTS.md` 时先给 diff 确认且不跑 eval；
- 五步流程：起草（`skill-creator`）→ 润色（`writing-for-agents`）→ 压缩（`caveman-compress`）→ 验证（`skill-optimizer`）→ 交付（提交与推送）；
- 控制 token 成本：eval 一律交给 Sonnet（`effort: high`）subagent 执行，不在主上下文内联；无 skill 基线只为新增或改动的 eval 跑一次，并以 `evals/benchmark.md` 作缓存；迭代只重跑受影响的 eval；执行者看不到 expectations；评分用脚本或 Sonnet grader，主 agent 只读分数表；交付阶段交给新的 Sonnet subagent，避免每次 git 调用都重发整段上下文。
