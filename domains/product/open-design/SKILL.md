---
name: open-design
description: >-
  Clickable static HTML prototype in 02b-prototype/. Optional sketch step: 2-3
  throwaway variants before committing one direction.
version: 2.0.0
author: ttmens
license: MIT
platforms: [cursor, hermes, opencode]
metadata:
  hermes:
    tags: [product-management, prototype, design, html]
    related_skills: [ui-ux-pro-max, user-journey, pm-idea-to-mvp]
---

# Open Design — Static Clickable Prototype

Make the idea tangible before engineering. Output in `02b-prototype/` for GitHub Pages.

## Output

```
02b-prototype/
  index.html      # ≤3 core screens
  styles.css
  DESIGN.md       # Brand constraints
```

## Rules

- Static HTML/CSS/JS only — no build step, no backend
- ≤3 core paths matching PRD MVP scope
- Mobile-responsive (Feishu phone review)
- 用户可见文案：**简体中文**

## Process

1. Read `03b-user-journey.md` — screens drive scope
2. Read `02-analysis.md` + `03-prd.md`
3. **Optional sketch** (below) — 2–3 variants, pick winner
4. Write `DESIGN.md` then `index.html`
5. Core paths match journey 核心路径

## Optional: sketch variants (absorbed from sketch skill)

Before committing one prototype, explore **2–3 design stances** (not just color tweaks):

| Axis | Examples |
|------|----------|
| Density | compact vs airy |
| Emphasis | content-first vs action-first |
| Layout | single-column vs sidebar |

**Output:** `02b-prototype/sketches/NNN-stance-name/index.html` + short README per variant.

Each variant: self-contained HTML, inline styles, realistic fake content, one interactive state (toggle/filter/open).

Present head-to-head comparison; user picks winner → promote into `index.html`.

**Do not** use sketch when design is locked or user wants production code.

## DESIGN.md template

```markdown
# Design Contract
## Product feel
## Colors (hex)
## Typography
## Component notes
## Out of scope for prototype
```

## Who

**pm-planner** owns this artifact (spec phase, G2).
