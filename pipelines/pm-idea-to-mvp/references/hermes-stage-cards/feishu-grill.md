# Feishu Grill — Stage Card (v6.1)

**Scope**: Gateway 前置（非 Kanban worker 任务）

## Protocol

见 `references/feishu-grill-protocol.md`。脚本：`scripts/feishu-grill-preflight.py`

## Flow

1. `/goal 产品想法：…` → gateway 问 1–2 题（成功标准、非目标）
2. 用户飞书回复 → 写入 `00-brief.md` `## 飞书 Grill`
3. `start_pm_pipeline_from_text` → decompose → `pm-aligner` 自主 align

## Not for workers

此 card 供文档与 sync 引用；**不**分配给 Kanban assignee。
