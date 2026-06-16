# 轻量模式（无 Kanban）

无 Hermes Kanban 时，用 `docs/workflow_state.yaml` 断点续跑。

## 初始化

从 `pipelines/pm-idea-to-mvp/assets/workflow_state.template.yaml` 复制到 `{PROJECT_ROOT}/docs/workflow_state.yaml`。

## 字段

- `current_phase`: brief | align | research | analysis | spec | mvp | ship | operate | grow | retro
- `gates`: G1/G2/G3 状态
- `blockers`: 阻塞列表

## 与 gates.json

`gates.json`（`assets/gates.template.json`）为 pm-{slug} 标准；`workflow_state.yaml` 为通用项目可选补充。

## 棕地

启动任意 phase 前运行 `docs-hygiene` + `check_docs_ssot.py`。
