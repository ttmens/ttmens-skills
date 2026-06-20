# Align — Stage Card (v6.1)

**Profile**: `pm-aligner` | **Stage**: `align` | **Checkpoint**: human (two-phase)

## Feishu grill 已完成

Gateway `feishu-grill-preflight` 已在 Kanban 前完成 1–2 轮交互 grill，`00-brief.md` 含 `## 飞书 Grill` 节。

**Kanban worker 模式**：读 enriched brief → 用 `grill-with-docs` **自主**写 CONTEXT/decisions → **不**等待飞书回复。

## Outputs

- `CONTEXT.md`, `decisions.md` under `{PROJECT_ROOT}`

## Skills

`grill-with-docs`（优先，brief 已 enriched）, `grill-me`（仅无 CONTEXT 且无 grill 节时）

## Exit (mandatory)

Verify artifact paths from the main pipeline SKILL exist under `{PROJECT_ROOT}`.
Update `PROGRESS.md` stage status.

**Human checkpoint**: notify user and wait for confirmation before marking stage done.
