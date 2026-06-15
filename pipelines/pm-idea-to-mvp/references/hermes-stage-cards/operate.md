# Operate — Stage Card (v7.0)

**Profile**: `pm-operator` | **Stage**: `operate`

## Outputs

- `07-ops-notes.md` (on-call, monitoring, rollback)

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 6（验证）**：监控配置必须实际可运行，不是纸上谈兵

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "运维笔记随便写写" | 最低 30 行。运维是持续活动 |
| "告警规则后面再配" | 上线第一天就可能出事 |
| "SLA 不重要" | 没有 SLA = 没有服务承诺 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | ops-notes 低于 30 行 | 敷衍产物 | 最低行数检查 |
| 2 | 无告警规则 | 故障发现延迟 | 告警规则必需 |
| 3 | 无 SLA 定义 | 服务质量无标准 | SLA 必需 |

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage operate --task-id <this_task_id>
```
