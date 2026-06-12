---
name: product-orchestrator
description: >-
  Meta-skill for end-to-end product delivery. Use when the user says 从想法到产品,
  帮我做 X, 自主构建, 端到端交付, 继续 stock-copilot, or 下一 Phase. Reads
  workflow_state.yaml and routes to idea-to-product, writing-plans, or UI acceptance.
version: 1.0.0
author: ttmens
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, orchestrator, product-development, autonomous]
    related_skills:
      - idea-to-product
      - writing-plans
      - subagent-driven-development
      - docs-hygiene
      - design-system-md
      - ui-acceptance-review
---

# Product Orchestrator

端到端产品交付的 **唯一入口 skill**。自动读取项目状态，路由到正确 phase，仅在三个里程碑门禁停等用户。

## Step 1: Detect project mode

1. 若项目根存在 `docs/workflow_state.yaml` → 读取并 **从 `current_phase` 续跑**
2. 若存在 `docs/design/08-CURRENT-STATUS.md` 或类似 SSOT → 默认 **`phase_increment` 模式**
3. 否则 → **`greenfield` 模式**

## Step 2: Initialize or update workflow state

若不存在 `docs/workflow_state.yaml`，从 `workflow/idea-to-product/assets/workflow_state.template.yaml` 复制并填写。

每完成一个 sub-phase **必须**更新：
- `current_phase`
- `gates.*` 状态（`pending` | `awaiting_user` | `approved`）
- `acceptance.functional/ux/ops`
- `checkpoints[]` 与 `blockers[]`

## Step 3: Run docs-hygiene (phase start/end)

加载 `docs-hygiene` skill，执行：

```bash
python3 scripts/check_docs_ssot.py --project-root .
```

棕地项目必须先通过 SSOT 检查或修复漂移，再进入 Design/Build。

## Step 4: Route by current_phase

| Phase | Load skill | Auto-advance? |
|-------|------------|---------------|
| extract | idea-to-product §Phase 1 | Yes |
| research | idea-to-product §Phase 2 + `research-two-axis.template.md` | **Stop at G1** |
| design, grill | idea-to-product §Phase 3-4 | **Stop at G2** |
| plan | writing-plans | Yes |
| build | subagent-driven-development | Yes |
| ship | ui-acceptance-review + self_check | **Stop at G3** (if UI changed) |
| learn | idea-to-product §Phase 8 + DECISIONS.md | Yes |

## Milestone gates (ONLY stop points)

| Gate | Condition | User action |
|------|-----------|-------------|
| **G1** | `docs/research.md` 含信息价值轴 + 交互设计轴 | 确认 / 调整方向 |
| **G2** | `docs/design.md` + ASCII 线框 + `docs/DESIGN.md` 草案 | 确认 / 改范围 |
| **G3** | `docs/ui-acceptance-report.md` + pre/post 快照 | 确认交付 / 打回 |

**禁止** 在 G1/G2/G3 之外询问「要不要继续」。

## Step 5: Blocker protocol

遇阻塞时：

1. 记录到 `workflow_state.yaml` → `blockers`
2. 查项目 `docs/`、`DECISIONS.md`、`RUNBOOK.md`
3. 尝试 **2 种备选方案**
4. 仍阻塞 → 向用户汇报 blocker + 已尝试方案 + 建议

## Step 6: Acceptance matrix (every phase)

每个 Phase 计划必须声明三域验收（模板：`workflow/idea-to-product/assets/acceptance-matrix.template.md`）：

- **functional** → pytest + self_check
- **ux** → `python3 scripts/ui_acceptance.py --quick`（含 UI 改动时）
- **ops** → RUNBOOK 命令

## Brownfield default (stock-copilot)

1. 读 `docs/design/08-CURRENT-STATUS.md` + `docs/DECISIONS.md`
2. 定义 **target_phase**（如 phase_d）
3. 输出 `docs/plans/YYYY-MM-DD-phase-X.md`（模板：`phase-plan.template.md`）
4. 只执行该 Phase 子流程，不重写全局 design

## Related assets

- `workflow/idea-to-product/assets/workflow_state.template.yaml`
- `workflow/idea-to-product/assets/research-two-axis.template.md`
- `workflow/idea-to-product/assets/phase-plan.template.md`
- `workflow/idea-to-product/assets/acceptance-matrix.template.md`
