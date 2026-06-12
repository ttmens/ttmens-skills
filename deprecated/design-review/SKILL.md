---
name: design-review
description: "UX acceptance review against journey, DESIGN.md, prototype, and MVP (not code review)."
version: 1.0.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, ux, review, qa]
    related_skills: [user-journey, ui-ux-pro-max, dogfood, ux-optimize]
---

# Design Review — UX Acceptance

Structured **UX acceptance** before MVP stage complete. This is NOT `requesting-code-review` (code/security).

## Output

Write `04-mvp/UX-REVIEW.md` with: 对照基准, 发现问题 table (ID/级别/页面/问题/建议), P0/P1/P2 stats, optional Waived table.

## Review checklist

1. Journey coverage — each core path walkable in MVP
2. Information hierarchy — first screen shows journey priorities
3. DESIGN consistency — palette/typography match DESIGN.md
4. Prototype parity — no regression vs 02b-prototype
5. Empty/error states — friendly messages
6. Role visibility — persona actions reachable

## Process

1. Read journey + DESIGN + prototype
2. Use dogfood / browser to walk core paths
3. Record P0/P1/P2 issues
4. P0 must be fixed by ux-optimize before stage-complete mvp

## Gate

- File exists; P0 = 0 or each P0 waived with reason
