---
name: ux-optimize
description: "Apply UX-REVIEW findings to MVP templates, styles, and interactions."
version: 1.0.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, ux, optimization]
    related_skills: [design-review, ui-ux-pro-max, dogfood]
---

# UX Optimize — Fix UX Review Findings

Close the loop after `design-review`. Implement fixes in MVP UI layer.

## Input

- `04-mvp/UX-REVIEW.md` (P0 and P1 items)
- `04-mvp/DESIGN.md`
- `03b-user-journey.md`

## Output

- Updated `04-mvp/templates/*.html`, CSS, JS/HTMX partials
- Updated `04-mvp/DESIGN.md` if tokens change
- Append **复测记录** section to `UX-REVIEW.md`:

```markdown
## 复测记录
| UX-ID | 状态 | 备注 |
|-------|------|------|
| UX-001 | fixed | ... |
```

## Process

1. Fix all **P0** issues first (blocking gate)
2. Fix **P1** where feasible within MVP scope
3. Re-run affected user paths (dogfood or smoke)
4. Update UX-REVIEW 复测记录 — P0 must all be `fixed` or `waived`

## Rules

- Do not change backend contracts unless UX issue requires it (then update openspec/tasks.md note)
- Preserve DESIGN.md palette unless review explicitly requests re-theme
- 用户可见文案使用**简体中文**
