# write-great-skill

编写与修改 Agent Skill 的端到端工作流与质量标准。

## 功能

- 不做评测：不创建 `evals/`，不跑测试 prompt、基线或 benchmark；
- 按触发方分门控：用户触发在第 1 步后确认，其他 skill 触发全程无人值守，仅改根 `CLAUDE.md`/`AGENTS.md` 时先给 diff 确认；
- 五步流程：起草（`skill-creator`，跳过其 eval、HTML viewer 与 description 优化循环）→ 润色（`writing-for-agents`）→ 压缩（`caveman-compress`）→ 静态验证（`skill-optimizer`）→ 交付（提交与推送）；
- 控制 token 成本：交付阶段交给新的 Sonnet（`effort: high`）subagent，避免每次 git 调用都重发整段上下文。
