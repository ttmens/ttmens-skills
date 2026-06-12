---
name: ui-acceptance-review
description: >-
  Unified UX/UI acceptance: journey review (UX-REVIEW.md), script rubric (quick/full),
  fix loop, and polish mode (70-84). Gate G3. Replaces design-review, ux-optimize,
  frontend-polish.
version: 2.0.0
author: ttmens
license: MIT
---

# UI Acceptance Review (unified)

**Gate G3** skill. Combines journey-based UX review, automated rubric, fix loop, and polish.

## Modes

| Mode | When | Output |
|------|------|--------|
| **journey** | MVP stage, before script rubric | `04-mvp/UX-REVIEW.md` (P0/P1/P2) |
| **quick** | Each UI commit / mid-phase | terminal check via script |
| **full** | Ship phase, G3 | `docs/ui-acceptance-report.md`, ≥85 pass |
| **polish** | full score 70–84 or user asks | CSS/structure refinement, no scope creep |

## Mode: journey (was design-review)

Structured UX acceptance against journey, DESIGN.md, prototype, MVP. **Not** code review.

**Checklist:** journey coverage, IA hierarchy, DESIGN consistency, prototype parity, empty/error states, role visibility.

**Process:**
1. Read `03b-user-journey.md`, `04-mvp/DESIGN.md`, `02b-prototype/`
2. dogfood / browser walk core paths
3. Write `04-mvp/UX-REVIEW.md`: 对照基准, issues table, P0/P1/P2 stats

**Gate:** P0 = 0 or each waived with reason.

## Mode: fix loop (was ux-optimize)

After journey review, fix P0/P1 in MVP UI:

1. Fix all **P0** first
2. Update templates/CSS; append **复测记录** to `UX-REVIEW.md`
3. Re-walk paths; P0 must be `fixed` or `waived`
4. 用户可见文案：**简体中文**

## Mode: quick / full (script rubric)

```bash
python3 scripts/ui_acceptance.py --quick --project-root .
python3 scripts/ui_acceptance.py --full --project-root .
```

Full pass: **≥85** and compliance critical all pass.

**Pre/post snapshots:** `docs/ui-snapshots/pre.png` + `post.png` → attach to report.

**Fix loop (max 3 rounds, no user interrupt):**
1. Read report failures → fix token/sync/compliance
2. Re-run `--full`
3. 70–84 → **polish** mode
4. Still fail → blocker at G3

## Mode: polish (was frontend-polish)

When functional but "AI-generated" look, or score 70–84:

1. **Review** — list hierarchy/spacing/motion issues
2. **Refactor** — tighten CSS without scope creep
3. **Component polish** — single component focus

Rules: hierarchy before decoration; keep DESIGN.md tokens; no new CDN; hover/focus-visible/disabled on interactives.

After polish → `--full` again; ≥85 → G3 user confirm.

## Rubric (full mode)

| Dimension | Points |
|-----------|--------|
| information_architecture | 20 |
| interaction | 15 |
| static_dynamic | 15 |
| design_token_sync | 15 |
| responsive | 10 |
| a11y | 10 |
| compliance (critical) | 10 |
| performance | 5 |
