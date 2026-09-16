---
name: gsx-ui-spec
description: "Wrap /gsd:ui-phase to generate a UI design contract (UI-SPEC.md) for a frontend phase, anchored screen-by-screen to the high-fidelity prototype. Use whenever the user wants to start, plan, or spec the UI/frontend work of a GSD phase — 'UI spec for phase 3', 'generate the UI design contract for phase X', 'frontend spec for Phase X', 'ui-phase 3', 'design the UI for phase X', or just a phase number in a frontend/design context. Prefer over /gsd:ui-phase directly — this enforces the project's prototype-fidelity rules and the ui-ux-best-practices skill."
argument-hint: "[GSD Phase Number]"
---

# gsx-ui-spec

## Codex Adapter

In Codex, translate this Claude wrapper instead of rewriting it:

- `$ARGUMENTS` = text after `$gsx-*`.
- `/gsd:<name> ...` or `Skill("gsd:<name>", args="...")` = run `.codex/skills/gsd-<name>/SKILL.md` with args as `{{GSD_ARGS}}`.
- `AskUserQuestion`: only map to `request_user_input` if your Codex build truly renders an interactive picker; otherwise (the usual Codex case) do **not** force it. Before any choice among options/plans, first print each option's core content in your reply, then list the choices as a numbered Markdown list and **stop and wait** for the user's text reply. Never self-answer a prompt the user never saw.
- Claude tool names are intent labels; use equivalent Codex tools.
- Preserve wrapper boundaries; if GSD owns edits, do not edit source here.


Thin wrapper around `/gsd:ui-phase` that always attaches the project's prototype-fidelity + UI/UX constraint.

1. `$ARGUMENTS` = GSD Phase Number (single number). If empty, ask *"要为哪个 Phase 生成 UI 设计契约？给我 Phase 编号。"* and wait.

2. Invoke with the number + this verbatim constraint block:

```
Skill("gsd:ui-phase", args: "<phase-number> 必须逐屏引用 @.product/design/ 高保真（视觉+交互）原型（包括但不限于列表、卡片、弹窗、抽屉等视觉文案，以及产品交互），同时遵守 ui-ux-best-practices skill 的视觉和交互规范（先读其 SKILL.md 索引，再按需读取相关规则文件），以及 CLAUDE.md「本项目专属的 UI 约定」一节。如果页面中存在依赖后续 Phase 的功能，前端内容也必须先占位（比如用 disable、数字 0 占位）。如果有功能逻辑调整确需调整页面、不对齐原型的，必须采访我询问意见。最后如果前后端对接好了，前端必须清除相关页面的 mock 数据。")
```

Keep the constraint text exactly as written. Don't read the prototype or draft UI-SPEC yourself — hand off to `gsd:ui-phase`. Reply in Chinese.
