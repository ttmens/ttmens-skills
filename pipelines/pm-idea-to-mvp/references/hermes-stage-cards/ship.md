# Ship — Stage Card (v7.0)

**Profile**: `pm-shipper` | **Stage**: `ship` | **Checkpoint**: human (G3)

## Outputs

- `RUNBOOK.md`, `docs/ui-acceptance-report.md`

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 3（推回）**：如果 MVP 还有已知问题，推回不允许 ship
- **准则 6（验证）**：RUNBOOK 必须可执行（回滚步骤必须实际测试过）

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "RUNBOOK 写个大概就行" | 回滚方案缺失 = 不可 ship |
| "监控后面再加" | 没有监控 = 盲人开车 |
| "安全审计太慢了" | 安全漏洞上线后修复成本 100x |
| "UX 验收差不多就行了" | 差不多 = 用户流失 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | RUNBOOK 缺回滚方案 | 出事故无法恢复 | 必需章节检查 |
| 2 | 缺监控指标 | 问题发现延迟 | RUNBOOK 含监控章节 |
| 3 | 跳过安全审计 | 安全漏洞上线 | security-and-hardening 技能 |
| 4 | 部署后不验证 | 部署成功 ≠ 运行正常 | health endpoint 检查 |

## Pre-Gates (Infrastructure Ready)

Before entering Ship stage, verify infrastructure readiness:

1. **SSH Connectivity**: `ssh_probe` — all target servers reachable
2. **Git Remote**: `git_remote_check` — push reachable and token valid
3. **Local Health**: `infra_health_check` — Gateway environment healthy (source/venv/config)

If any check fails:
- Attempt auto-fix (Level 1 issues)
- Retry the check
- If still failing, report to user and block Ship stage

## Exit (mandatory)

Verify artifact paths from the main pipeline SKILL exist under `{PROJECT_ROOT}`.
Update `PROGRESS.md` stage status.

**Human checkpoint**: notify user and wait for confirmation before marking stage done.
