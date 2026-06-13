---
name: pm-planner
description: "Hermes Kanban profile for spec stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-planner
    stage: spec
---

# pm-planner

**Stage**: spec

## Boundaries
- Only write artifacts for **spec** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage spec --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
open-design, prd-red-team-panel
