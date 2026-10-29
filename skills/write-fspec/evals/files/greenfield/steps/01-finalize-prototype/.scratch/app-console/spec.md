# 开放平台控制台：机构与应用管理

Status: ready-for-agent

## Problem Statement

平台运营人员目前靠表格和邮件登记接入机构及其应用，密钥发放与停用全靠人工，经常出现停用机构后应用仍可调用的情况。

## Solution

提供运营控制台：运营人员在控制台中维护机构、为机构创建应用并管理密钥与启停状态。

## User Stories

1. As a 平台管理员, I want 按名称和状态筛选机构, so that 快速找到要处理的机构
2. As a 平台管理员, I want 停用机构, so that 该机构的全部应用立即停止调用
3. As a 运营人员, I want 为机构新建应用, so that 机构拿到 AppKey 后即可接入
4. As a 运营人员, I want 重置应用密钥, so that 密钥泄露时能立即止损
5. As a 运营人员, I want 停用应用, so that 不再使用的应用无法调用接口
6. As a 运营人员, I want 编辑应用名称和回调地址, so that 信息变化时能及时更正

## Implementation Decisions

- 机构与应用两个模块；应用归属唯一机构，创建后不可变更归属。
- 停用机构级联停用其下全部应用。
- 重置密钥后旧密钥立即失效，新密钥只展示一次。

## Testing Decisions

- 只测外部行为：通过控制台 API 验证停用级联与密钥失效。

## Out of Scope

- 批量导入应用。
- 应用调用量统计看板。

## Further Notes

无。
