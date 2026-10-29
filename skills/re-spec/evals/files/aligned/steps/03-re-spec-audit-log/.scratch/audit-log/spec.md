# 审计日志与数据空间

Status: ready-for-agent

## Problem Statement

监管检查要求能追溯每一次密钥重置、应用停用与机构停用，但控制台目前没有任何操作记录；另外机构已改为按数据空间组织应用，列表里的「关联应用」数量不再有意义。

## Solution

新增审计日志页，记录关键操作并支持筛选与查看详情；机构列表改为展示机构加入的数据空间。

## User Stories

1. As a 平台管理员, I want 按时间范围、操作类型和操作人筛选审计日志, so that 迎检时快速定位记录
2. As a 平台管理员, I want 查看一次操作的变更前后, so that 判断操作是否合规
3. As a 运营人员, I want 在机构列表看到机构加入的数据空间, so that 了解机构接入范围

## Implementation Decisions

- 审计记录只追加、不可删除，保留 180 天。
- 新增审计记录模块，关键操作完成后同步写入一条记录。

## Testing Decisions

- 通过 API 验证每类关键操作都会产生一条审计记录。

## Out of Scope

- 审计告警推送。
- 导出审计日志：原型评审决定迎检以页面筛选核查为准。

## Further Notes

界面细节以 products/fspec/console/CURRENT.md 为准（V2）。

## Comments

- to-spec：创建 spec，见 .scratch/audit-log/spec.md。
- re-spec：依据 products/fspec/console/V2__audit_log.md 修订 User Stories、Out of Scope、Further Notes。
