# Brownfield — Stage Card (v6.1)

**Profile**: `pm-aligner` (audit) + `pm-builder` / `pm-shipper` | **Scenario**: `brownfield`

## When

存量 `pm-{slug}` 项目：优化、重构、审计、继续迭代 — 见 `references/brownfield-audit.md`

## Decompose

`brownfield-bootstrap skill + artifact checklist` → 精简子图（审计 → MVP iter → ship → retro）

## First task (pm-aligner)

1. 构建验证（阻塞）
2. `check_docs_ssot.py` + 全阶段 `validate-gates.py`
3. 补齐 governance / debates
4. 更新 CONTEXT.md 反映现状
5. `verify align artifacts + human checkpoint` → 卡点

## Exit

同 align stage-card；棕地审计产物写入 `feedback.jsonl` + `PROGRESS.md`
