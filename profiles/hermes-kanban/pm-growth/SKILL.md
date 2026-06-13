---
name: pm-growth
description: "Hermes Kanban profile for grow stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-growth
    stage: grow
---

# pm-growth

**Stage**: grow

## Boundaries
- Only write artifacts for **grow** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage grow --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
pm-gtm-strategy
