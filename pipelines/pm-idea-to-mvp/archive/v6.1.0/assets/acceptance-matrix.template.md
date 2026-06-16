# 验收矩阵模板

每个 Phase 计划 **必须** 声明三域验收，避免「后端全绿、UI 零检」。

## functional（功能）

| 检查项 | 标准 | 命令 |
|--------|------|------|
| 单元测试 | 全部通过 | `python -m pytest tests/ -q` |
| 自检 | error 为零 | `python scripts/self_check.py --quick` |
| [特性] | ... | ... |

## ux（产品 / 交互）

| 检查项 | 标准 | 命令 |
|--------|------|------|
| 3 秒原则 | 首屏见结论/信号 | `ui_acceptance.py --full` |
| 交互组件 | 筛选/展开/详情可用 | 手动 + script |
| token 一致 | DESIGN.md ↔ theme.css | `ui_acceptance.py --quick` |
| pre/post | 大改有快照 | `docs/archive/*-pre/post*` |

## ops（运维）

| 检查项 | 标准 | 命令 |
|--------|------|------|
| API | /health ok | `curl localhost:8000/health` |
| 发布 | docs sync | RUNBOOK |
| 文档 | SSOT 无漂移 | `check_docs_ssot.py` |

## Gate 映射

- G1 通过 → research.md 双轴完成
- G2 通过 → design.md + 线框 + DESIGN.md 草案
- G3 通过 → ui-acceptance-report.md ≥85 分 + 用户确认
