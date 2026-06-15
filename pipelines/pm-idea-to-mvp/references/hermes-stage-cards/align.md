# Align — Stage Card (v7.0)

**Profile**: `pm-aligner` | **Stage**: `align` | **Checkpoint**: human (two-phase)

## Outputs

- `CONTEXT.md`, `decisions.md` under `{PROJECT_ROOT}`

## Skills

`grill-me`, `grill-with-docs`

## 行为准则

加载 `references/agent-behavior-code.md` — 6 条不可协商准则全部适用，特别是：
- **准则 1（假设前置）**：grill 开始前先列出对用户意图的假设
- **准则 3（反谄媚）**：如果用户想法有明显缺陷，必须指出并量化风险

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "用户想法已经很清楚了，不需要 grill" | 清楚 ≠ 验证过。至少 3 个深度问题 |
| "这个问题太细节了，跳过" | 细节里藏着致命假设 |
| "用户说不用问了，直接开始" | 用户的"不用问"往往是测试你的耐心。确认关键假设后再停 |
| "CONTEXT.md 写个大概就行" | 最低 50 行是底线。69 行的 CONTEXT 在 pm-knowledge-platform 中被证明深度不足 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | 假设用户意图而非验证 | 整个流水线方向错误 | grill-me 至少 3 轮 |
| 2 | 跳过假设风险标注 | analysis 阶段才发现矛盾 | decisions.md 必须含风险等级 |
| 3 | 过度追问（>10 个问题） | 用户疲劳放弃 | 合并相关问题，聚焦核心假设 |
| 4 | 谄媚式对齐（"好想法！"） | 有缺陷的想法被带入下游 | 反谄媚准则强制推回 |

## Exit (mandatory)

```powershell
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --project-root {PROJECT_ROOT} --stage align --task-id <this_task_id> --runtime
```

**First run**: exit 0 → `kanban_block` reason `等待用户确认 align 产物` → **do NOT** `kanban_complete`.
**Resume** (after unblock): verify gates → `kanban_complete`.
