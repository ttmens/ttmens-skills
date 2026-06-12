---
name: competitor-tracker
description: >-
  Thin wrapper: delegates to pm-competitor-analysis (phuryn). Output to
  01-research.md competitor section. Use during research phase.
version: 2.0.0
author: ttmens
license: MIT
wraps: pm-competitor-analysis
---

# Competitor Tracker (wrapper)

**委托** borrowed skill `pm-competitor-analysis` 做结构化竞品分析，并入调研文档。

## Output path

- **pm-idea-to-mvp**: `{PROJECT_ROOT}/01-research.md` 的「竞品」章节
- **通用**: `docs/research/competitors.md`

## Workflow

1. 加载 `pm-competitor-analysis`，选定 2–3 个直接/间接竞品
2. 产出：优势、劣势、差异化机会、对我们的启示
3. 合并入 `01-research.md`（保留 ≥5 URLs 门禁）
4. 可选：`pm-market-sizing` 补充 TAM/SAM/SOM

## Fallback

若未安装 borrowed skill，使用简表：产品 | 定位 | 优势 | 劣势 | 可借鉴 | 应避免
