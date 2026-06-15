# MVP Plan — Inner Loop Step 1 (v7.0)

**Profile**: `pm-builder` | **Stage**: `mvp-plan`

## Goal

Plan only — no full implementation. Read `openspec/tasks.md` + `03b-user-journey.md`.

## Outputs

- `04-mvp/DESIGN.md` (ui-ux-pro-max), PROGRESS.md plan updated

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 4（简洁）**：plan 阶段就要确定每个 iter ≤300 行变更
- **准则 5（范围纪律）**：plan 只覆盖 openspec/tasks.md 中的任务，不加新任务

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "这个 iter 可以多做几个功能" | 一个 iter 一个垂直切片。贪多嚼不烂 |
| "DESIGN.md 不需要，直接写代码" | DESIGN.md 是 UI 一致性的保障 |
| "测试计划太麻烦，边写边测" | 没有测试计划的 iter = 不可验证的 iter |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | plan 跳过 DESIGN.md | UI 不一致 | ui-ux-pro-max 必须运行 |
| 2 | iter 范围过大 | 300+ 行变更无法审查 | 变更规模约束 |
| 3 | 没有测试策略 | TDD 纪律缺失 | writing-plans 含测试计划 |

## Exit

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage mvp-plan --task-id <this_task_id>
```

Then `kanban_complete` when gates pass.
