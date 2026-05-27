# ttmens-skills

面向 IT 产品经理与端到端产品交付的 Agent Skills 集合 — 支持 **Cursor** 与 **Hermes**。

## 安装

```bash
git clone https://github.com/ttmens/obsidian-pm-skills.git ttmens-skills
cd ttmens-skills
./install.sh --both                              # ~/.cursor/skills + ~/.hermes/skills
./install.sh --project /path/to/stock-copilot    # 项目 .cursor/skills
```

## 一、Product Workflow（端到端交付）

| Skill | 路径 | 用途 |
|-------|------|------|
| **product-orchestrator** | `workflow/product-orchestrator/` | **主入口**：读 workflow_state，三里程碑门禁 |
| idea-to-product | `workflow/idea-to-product/` | v4 工作流：phase-increment + 自主模式 |
| writing-plans | `workflow/writing-plans/` | 拆 bite-sized 任务 |
| subagent-driven-development | `workflow/subagent-driven-development/` | 逐 Task 执行 + 审查 |
| docs-hygiene | `workflow/docs-hygiene/` | SSOT 漂移检测 |
| prd-template | `skills/product/prd-template/` | PRD 模板 |
| competitor-tracker | `skills/product/competitor-tracker/` | 竞品追踪 |

模板：`workflow/idea-to-product/assets/`（workflow_state、双轴调研、验收矩阵）

## 二、Design QA（UI 验收）

| Skill | 路径 | 用途 |
|-------|------|------|
| design-system-md | `design/design-system-md/` | 维护 docs/DESIGN.md |
| ui-acceptance-review | `design/ui-acceptance-review/` | Gate G3，quick/full rubric |
| frontend-polish | `design/frontend-polish/` | 70–84 分 refinement |

脚本：
- `workflow/docs-hygiene/scripts/check_docs_ssot.py`
- `design/ui-acceptance-review/scripts/ui_acceptance.py`

## 三、Obsidian PM Skills

Canonical 路径：`skills/`（根目录 `productivity/`、`research/` 为 v2 副本，见 DEPRECATED.md）

| Skill | 触发 |
|-------|------|
| obsidian-todo-manager | 记待办、汇总待办 |
| obsidian-deepen-review | 深化笔记、周报、MOC |
| obsidian-note-summarizer | 文章/会议摘要 |

## 三里程碑门禁

| Gate | 产出 |
|------|------|
| G1 | research.md 双轴调研 |
| G2 | design.md + 线框 + DESIGN.md |
| G3 | ui-acceptance-report + pre/post 快照 |

## stock-copilot 绑定

项目已配置：
- `AGENTS.md` → product-orchestrator
- `docs/workflow_state.yaml` → 断点续跑
- `docs/DESIGN.md` → 视觉 SSOT
- `scripts/check_docs_ssot.py` / `scripts/ui_acceptance.py`
- `.cursor/hooks/` → commit 前质量门

## License

MIT
