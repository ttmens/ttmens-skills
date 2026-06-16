# Hermes Integration — pm-idea-to-mvp (v7.1.1)

> **契约源头**：飞书/gateway 如何触发本技能、与 Ralph `/goal` 的边界、续跑与场景路由。
> **实现层**：`hermes-agent/hermes_cli/pm_pipeline.py`（适配层，非独立技能）。
> **版本 SSOT**：`assets/pipeline-version.yaml`（与 `stage-skills.yaml` 同步）。

## 路由决策

| 用户输入示例 | 路由 | 行为 |
|-------------|------|------|
| `/goal 产品想法：xxx` | `pm_grill` → `pm_kanban` | 飞书 grill 1–2 问 → enriched brief → 12 子任务 decompose |
| `总结一下 pm-idea-to-mvp 能力` | `ralph` | **咨询对话**，不启动 Kanban（`query_exclusions`） |
| `/goal 继续优化产品知识库` | `pm_resume` / `brownfield` | 检测 slug + `project_exists` → 棕地分解或状态报告 |
| `/goal 继续 pm-product-knowledge` | `pm_resume` | 续跑已有 slug 的 Kanban |
| `按 pm-idea-to-mvp 优化 xxx 项目` | `pm_kanban` / `brownfield` | 强执行意图 → Kanban decompose |
| `/goal 帮我写周报` | `ralph` | **不**进 pm-idea-to-mvp；GoalManager 会话循环 |

Gateway 日志格式：`PM route=<route> (plain-text handler|/goal fallback)`

## 触发词（SSOT）

完整列表见 **`assets/trigger-routing.yaml`**（Gateway 唯一路由源；SKILL.md metadata 仅为 agent 提示）：

- 字面 markers：`pm-idea-to-mvp`、`想法到产品`、`产品想法`…
- 正则：`使用…想法到…产品`、`projects/pm-{slug}`…
- `/goal` 前缀：`产品想法`、`idea:`
- **query_exclusions**：`总结/介绍/能力/版本` + 技能名 → Ralph
- **strong_intent_markers**：`优化/部署/按 pm-idea/产品想法` 等覆盖 exclusions
- **reserved_slugs**：`idea-to-mvp` 不可作为 `pm-{slug}` 项目目录名

## 飞书 Grill 前置

Greenfield `/goal 产品想法` **不立即 decompose**。流程见 `references/feishu-grill-protocol.md`：

1. `feishu-grill-preflight.py start` → 1–2 轮问题
2. 用户回复 → `reply` → 写入 `00-brief.md`（含 `## 飞书 Grill`）
3. `start_pm_pipeline_from_text` → `pm_kanban` decompose

## Kanban 集成

- Triage root assignee：`pm-orchestrator`
- Decompose：`scripts/decompose-pm-pipeline.py --task-id … --scenario {greenfield|brownfield|optimize|refine}`
- 子任务 **skills 预加载**：`stage-skills.yaml` → `pm-idea-to-mvp` + 阶段 native/borrowed
- 进度通知：`stage-complete.py` → `skills/scripts/feishu_notify.py`
- 状态报告：`scripts/kanban-status-report.py`

## 路径与环境

| 变量 | 默认（本机） |
|------|-------------|
| `HERMES_HOME` | `D:/hermes-data` |
| `SKILLS_ROOT` | `{HERMES_HOME}/skills` |
| `PROJECTS_ROOT` | `D:/workspace/projects` |

`pipeline_paths.resolve_*()` 与 `pm_pipeline.py` 对齐上述默认值。

## Profile 同步

```bash
HERMES_HOME=D:/hermes-data python skills/pipelines/pm-idea-to-mvp/scripts/sync-hermes-profiles.py --prune-hub
```

写入 9 个 `profiles/pm-*/skills/pm-idea-to-mvp/SKILL.md` stage cards（v7.1）。

## 验证

```bash
python skills/scripts/validate_skills.py
python skills/scripts/validate_skills.py --fix-nested --dry-run
```
