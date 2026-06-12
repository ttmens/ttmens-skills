---
name: prd-template
description: >-
  Thin wrapper: delegates to pm-create-prd (phuryn). Output to 03-prd.md per
  pm-idea-to-mvp layout. Use during spec phase or when user asks for PRD.
version: 2.0.0
author: ttmens
license: MIT
wraps: pm-create-prd
---

# PRD Template (wrapper)

**委托** borrowed skill `pm-create-prd` 生成 8 段完整 PRD，再按 ttmens 路径落盘。

## Output path

- **pm-idea-to-mvp 项目**: `{PROJECT_ROOT}/03-prd.md`
- **通用项目**: `docs/prd/YYYY-MM-DD-<feature>.md`

## Workflow

1. 加载 `pm-create-prd` skill，读取 `CONTEXT.md`、`02-analysis.md`
2. 使用 phuryn 8-section PRD 结构（简体中文）
3. 补充验收矩阵：`functional` / `ux` / `ops`（对齐 idea-to-product 验收域）
4. 可选：加载 `pm-user-stories` 补充 INVEST 故事表
5. 写入输出路径；更新 `gates.json` → `spec`

## Fallback

若 `pm-create-prd` 未安装，使用最小模板（背景、用户故事表、功能需求表、验收标准）。
