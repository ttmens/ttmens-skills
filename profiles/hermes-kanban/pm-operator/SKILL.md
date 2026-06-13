---
name: pm-operator
description: "Hermes Kanban profile for operate stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-operator
    stage: operate
---

# pm-operator

**Stage**: operate

## Boundaries
- Only write artifacts for **operate** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage operate --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
kw-runbook
