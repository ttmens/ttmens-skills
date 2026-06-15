# Hermes Integration — pm-idea-to-mvp (v6.1.0)

> **契约源头**：飞书/gateway 如何触发本技能、与 Ralph `/goal` 的边界、续跑与场景路由。
> **实现层**：`hermes-agent/hermes_cli/pm_pipeline.py`（适配层，非独立技能）。

## 路由决策

| 用户输入示例 | 路由 | 行为 |
|-------------|------|------|
| `/goal 产品想法：xxx` | `pm_grill` → `pm_kanban` | 飞书 grill 1–2 问 → enriched brief → 12 子任务 decompose |
| `/goal 继续优化产品知识库` | `pm_resume` / `brownfield` | 检测 slug → 不新建 12 任务；棕地分解或状态报告 |
| `/goal 继续 pm-product-knowledge` | `pm_resume` | 续跑已有 slug 的 Kanban |
| `按 pm-idea-to-mvp 执行…`（正文） | `pm_kanban` | 同 Kanban，无 Ralph |
| `/goal 帮我写周报` | `ralph` | **不**进 pm-idea-to-mvp；GoalManager 会话循环 |

Gateway 日志格式：`PM route=<route> slug=<slug> scenario=<scenario>`

## 触发词（SSOT）

完整列表见 `assets/trigger-routing.yaml`：

- 字面 markers：`pm-idea-to-mvp`、`想法到产品`、`产品想法`…
- 正则：`使用…想法到…产品`、`projects/pm-{slug}`…
- `/goal` 前缀：`产品想法`、`idea:`

**已知缺口已修复（6.1.0）**：`继续使用想法到产品的这一个技能`（无 `mvp` 字样）仍命中「想法到产品」marker。

## 飞书 Grill 前置

Greenfield `/goal 产品想法` **不立即 decompose**。流程见 `references/feishu-grill-protocol.md`：

1. `feishu-grill-preflight.py` 最多 2 轮问答
2. 写入/更新 `{PROJECT_ROOT}/00-brief.md`（含成功标准、非目标）
3. `start_pm_pipeline_from_text` 在 `grill_done` 后调用 `decompose-pm-pipeline.py`

Kanban `pm-aligner` worker **自主**写 CONTEXT（不等待飞书），因 grill 已在 gateway 完成。

## 续跑语义

| 模式 | 条件 | 动作 |
|------|------|------|
| `pm_resume` | 消息含「继续 pm-{slug}」或项目目录已存在且有 active 子任务 | 返回 `kanban-status-report.py` 摘要；**不**新建 triage |
| `brownfield` | 含优化/重构/存量关键词 + 项目已存在 | `decompose --scenario brownfield`（精简子图） |
| 新建 greenfield | 无存量项目 + 产品想法 | grill → 12 子任务 |

## 与 Ralph `/goal` 边界

- **Kanban 路径**：确定性脚本、worker profile、三卡点（align/spec/ship）
- **Ralph 路径**：单会话 agent、`GoalManager` 续跑 — **不**加载 stage-card / grill-me 链

凡应走 Kanban 的消息必须在 `_handle_goal_command` **之前**被 `pm_pipeline.handle_pm_gateway_message` 拦截。

## 可观测性

- `scripts/kanban-status-report.py` — 按 slug 或 root task 输出飞书友好摘要
- `stage-complete.py` — checkpoint 阶段 block 时必发 Feishu 通知（含 unblock 提示）
- 可选：`PM_HEARTBEAT_MINUTES=5` 对 long-running 任务发 heartbeat

## 脚本路径

```
{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/
  decompose-pm-pipeline.py   # --task-id (gateway) | --project-root (CLI) | --scenario
  feishu-grill-preflight.py
  kanban-status-report.py
  stage-complete.py
```
