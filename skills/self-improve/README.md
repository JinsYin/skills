# self-improve

> **会话复盘与 skill 自进化**（self-evolving / RSI 反馈循环）

- 从当前会话（或 `--sessions` 挑选的本项目多个会话）中找出失败、用户纠正、绕路、重复问题，以及耗 Token、耗时过长的轮次与子 Agent，按「强信号 1 次、弱信号 ≥2 次」门槛提炼可复用经验，对照 `jinsyin/skills` 最新版做根因分析，以最小且精炼的修改改进已加载的 skill（含删减、合并无效步骤以缩短流程）或新建 skill；
- 每个 skill 先建 Issue（即复盘报告）再发关联 PR，由人工合并；正文用中文撰写，模板骨架（标题、字段键、表头、`model/effort`、Signal）保持英文；
- 对手动触发且重度调用（Token 或耗时占全会话 ≥25%）的第三方 skill，复盘其调用细节，把驾驭它的规则写入 `setup-rules` 对应约定（无则新建），并入 `setup-rules` 的 Issue + PR；
- 随后复盘本次运行对 `self-improve` 自身做同样的改进（自我改进）；最后询问是否同步到当前项目的已安装副本；
- `--dry-run` 只出报告。

`scripts/transcript.py` 流式解析 `~/.claude/projects/<slug>/*.jsonl`，输出精简的信号摘要（纠正候选、报错、拒绝、重试、skill 加载路径、主/子 Agent 的 Token 与耗时热点、按 skill 聚合的开销及触发方式），避免把原始 transcript 灌进上下文。

## 参考

- [zhaono1/agent-playbook · self-improving-agent](https://github.com/zhaono1/agent-playbook/blob/main/skills/self-improving-agent/SKILL.md) - 只沉淀面向未来行为的可复用经验，重复次数不等于正确性
- [eai-org/agent-toolkit · self-improve](https://github.com/eai-org/agent-toolkit/blob/main/skills/self-improve/SKILL.md) - 规则已存在却未生效时修「为什么没生效」，而非重复加规则
- [Dwsy/agent · improve-skill](https://github.com/Dwsy/agent/blob/main/skills/improve-skill/SKILL.md) - 定位并解析会话 transcript，在全新上下文中分析以避免自我合理化
- [giannimassi/agent-retro](https://github.com/giannimassi/agent-retro) - 逐行流式读取 JSONL 保留完整会话脉络，产出可直接落地的修改文本
- [anthropics/claude-plugins-official · session-report](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/session-report/skills/session-report/SKILL.md) - 基于阈值的异常信号与输出体积上限
- [cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering) - 分级信任的自主回路，人必须审阅回路产出
- [Carlo1911/skill-evolution](https://github.com/Carlo1911/skill-evolution/blob/main/SKILL.md) - 信号分类、单次增长上限、分析与应用分离
- [borghei/Claude-Skills · self-improving-agent](https://github.com/borghei/Claude-Skills/blob/main/engineering/self-improving-agent/SKILL.md) - 最少出现次数的晋升门槛与经验去向分类
