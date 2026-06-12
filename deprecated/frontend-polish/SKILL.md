---
name: frontend-polish
description: >-
  Refine UI when functional but looks AI-generated. Use when ui_acceptance scores
  70-84 before Gate G3, or user asks to polish visual craft.
version: 1.0.0
author: ttmens
license: MIT
---

# Frontend Polish

功能正确但「AI 味重」时的 refinement skill。仅在 **ui_acceptance 70–84 分** 或用户明确要求时触发。

## Modes

1. **Review** — 列出 hierarchy/spacing/motion 问题，不改代码
2. **Refactor** — 在 **不扩 scope** 前提下收紧 CSS 与结构
3. **Component polish** — 单组件（卡片/筛选条/详情页）

## Rules

- 先修 hierarchy，再修 decoration
- 保持 DESIGN.md token，不引入新 CDN/框架
- 保留 A 股价格色 vs 信号色语义
- 每个 interactive 元素：hover / focus-visible / disabled
- 改完后：`ui_acceptance.py --full`

## Anti-patterns to fix

- 过多等宽渐变边框
- 不一致圆角/间距
- 首屏信息过载（违反 3 秒原则）
- 缺失 empty/loading 态

## Hand off

Polish 完成后重跑 full acceptance；≥85 → 进入 G3 用户确认。
