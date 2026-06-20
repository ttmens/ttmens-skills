# Analysis — Stage Card (v7.0)

**Profile**: `pm-analyst` | **Stage**: `analysis`

## Outputs

- `02-analysis.md`, `architecture/c4-*.md`, `openspec/proposal.md`

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 3（推回）**：如果只有一个方案，必须指出并补充替代方案
- **准则 4（简洁）**：架构设计偏好简单方案，不过度工程化

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "方案 A 明显更好，不需要 PK" | 明显 ≠ 论证过。至少 3 个方案 + PK |
| "C4 画到 L1 就够了" | L1-L3 是完整架构的最低标准 |
| "ADR 太形式化了" | 没有 ADR 的决策 = 无法追溯的决策 |
| "openspec/proposal.md 后面再补" | proposal 是 analysis 的核心产物，不能延后 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | 只有 1 个方案就推荐 | 没有对比就没有决策质量 | 至少 3 个方案 |
| 2 | C4 只画 Context 层 | 容器/组件层缺失导致 MVP 阶段混乱 | L1-L3 完整 |
| 3 | 跳过 ADR 映射 | 技术决策无法追溯 | decisions.md 同步更新 |
| 4 | 跨文档不一致 | CONTEXT 说 PostgreSQL，实际用 SQLite | check_docs_ssot.py |

## Exit (mandatory)

Verify artifact paths from the main pipeline SKILL exist under `{PROJECT_ROOT}`.
Update `PROGRESS.md` stage status.
