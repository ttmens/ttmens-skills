---
name: open-design
description: "Generate clickable static HTML prototype in 02b-prototype/ for stakeholder alignment."
version: 1.0.0
author: PM Pipeline (adapted from nexu-io/open-design)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, prototype, design, html]
    related_skills: [ui-ux-pro-max, excalidraw, pm-idea-to-mvp]
---

# Open Design — Static Clickable Prototype

Make the idea tangible before engineering. Output lives in GitHub Pages via `02b-prototype/`.

## Output

```
02b-prototype/
  index.html      # Entry: main user flow (≤3 screens)
  styles.css
  DESIGN.md       # Brand constraints, colors, typography
```

## Rules

- **Static HTML/CSS/JS only** — no build step, no backend
- Prototype ≤3 core paths matching PRD MVP scope
- Each screen links via `<a href="...">` or simple JS `showScreen()`
- Mobile-responsive CSS (Feishu phone review)

## DESIGN.md template

```markdown
# Design Contract
## Product feel
## Colors (hex)
## Typography
## Component notes
## Out of scope for prototype
```

## Process

1. **Must read** `03b-user-journey.md` — screens and touchpoints drive prototype scope
2. Read `02-analysis.md` + `03-prd.md`; align each screen to journey touchpoint IDs
3. Optional: use `sketch` for 2–3 UI directions before committing
4. Write `DESIGN.md` then `index.html` — core paths must match journey 核心路径
5. Screen count ≤3 for default gate; Refine may add tabs for audit/import if journey requires
6. Run `build-run-report.py` so Pages embeds prototype in iframe

## Who

- **pm-planner** owns this artifact (before or with PRD)
