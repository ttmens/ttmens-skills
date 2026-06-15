# Feishu Grill Preflight Protocol (v6.1.0)

> Align 阶段的**交互式** grill 在飞书 gateway 完成；Kanban `pm-aligner` 随后**自主**写 CONTEXT。

## 何时触发

| 条件 | Grill |
|------|-------|
| `/goal 产品想法：…`（greenfield） | ✅ 1–2 轮 |
| `/goal 继续优化…`（brownfield/resume） | ❌ 跳过 |
| `00-brief.md` 已含 `## 飞书 Grill` 且非空 | ❌ 跳过 |
| 项目目录已存在 + CONTEXT.md | ❌ 跳过（走 brownfield） |

## 状态机

```
idle
  → question_1 (success_metric)
  → question_2 (non_goals)   [max 2 rounds]
  → grill_done → write 00-brief.md → start_pm_pipeline
```

状态文件：`{HERMES_HOME}/feishu-grill/{session_key}.json`

## 问题（默认）

1. **成功标准**：怎样算做完？
2. **非目标**：明确不做什么？

配置见 `assets/trigger-routing.yaml` → `grill.questions`。

## Brief 写入格式

Grill 完成后在 `{PROJECT_ROOT}/00-brief.md` 追加：

```markdown
## 飞书 Grill

**成功标准**（Grill 1）:
{user answer}

**非目标**（Grill 2）:
{user answer}

**Grill 完成时间**: {ISO8601}
```

## Gateway 集成

`pm_pipeline.handle_pm_gateway_message(text, session_key=...)`：

- `route=pm_grill` — 返回问题，不 decompose
- `route=pm_grill_reply` — 收集回答
- `route=pm_kanban` — grill 完成后 decompose

普通消息（非 `/goal`）若 session 有 active grill，优先当作 grill 回答处理。

## Kanban align worker

Grill 完成后 align worker：

- 读 enriched `00-brief.md`
- 用 `grill-with-docs` **自主**产出 CONTEXT.md / decisions.md
- **不**在 worker 内等待飞书用户回复

见 `references/hermes-stage-cards/align.md` 与 `feishu-grill.md`。
