# Spec — Stage Card (v7.0)

**Profile**: `pm-planner` | **Stage**: `spec` | **Checkpoint**: human (two-phase)

## Outputs

- `03b-user-journey.md`, `02b-prototype/`, `03-prd.md`, `openspec/tasks.md`

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 1（假设前置）**：PRD 开始前列出关于用户/场景/技术约束的假设
- **准则 5（范围纪律）**：user stories ≤5 个，不要偷偷加功能

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "PRD 太长用户不会看" | 最低 50 行是底线，不是目标 |
| "原型不需要，直接写代码" | 原型是验证交互的最低成本方式 |
| "user story 的验收标准太细节了" | 没有验收标准的 story = 无法验证的 story |
| "openspec/tasks.md 后面再拆" | tasks 是 MVP 内循环的输入，必须先有 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | PRD 低于 50 行 | 深度不足，MVP 阶段频繁返工 | 最低行数检查 |
| 2 | 原型 HTML 不可渲染 | 用户无法验证交互 | 渲染检查 |
| 3 | user stories >5 | 范围蔓延 | 强制 ≤5 |
| 4 | 无验收标准 | MVP 无法判断完成 | 每条 story 必须有 AC |

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage spec --task-id <this_task_id> --runtime
```

**First run**: `kanban_block` `等待用户确认 PRD/原型范围`. **Resume**: `kanban_complete`.
