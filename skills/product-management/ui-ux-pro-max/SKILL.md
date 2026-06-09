---
name: ui-ux-pro-max
description: "Design system tokens from PRD; builder must apply when implementing MVP UI."
version: 1.0.0
author: PM Pipeline (adapted from nextlevelbuilder/ui-ux-pro-max-skill)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, design-system, ui, ux]
    related_skills: [open-design, design-md, opencode]
---

# UI UX Pro Max — Design System for MVP

Prevent generic AI UI. Generate cohesive tokens before/during MVP build.

## Output

Write `04-mvp/DESIGN.md` (or update `02b-prototype/DESIGN.md`):

```markdown
# Design System — {product}
## Palette
- primary: #...
- surface: #...
- text: #...
## Typography
- heading: ...
- body: ...
## Spacing scale
## Component patterns
- buttons, cards, tables
## UX rules
- max actions per screen
- empty states
```

## Process

1. Read `03-prd.md` + `03b-user-journey.md` + `02b-prototype/DESIGN.md` if present
2. **UI 选型**：when direction unclear, run `sketch` for 2–3 variants; pick one before final tokens
3. Infer product category (B2B dashboard, consumer app, etc.) from journey personas
4. Generate tokens — avoid default purple-gradient AI aesthetic
4. **pm-builder** must reference DESIGN.md in OpenCode prompt:

```bash
opencode run "Implement MVP per 03-prd.md and 04-mvp/DESIGN.md tokens. ..." --workdir ...
```

## Verification

- MVP CSS uses palette from DESIGN.md
- At least 2 UX rules applied (e.g. clear hierarchy, readable contrast)
