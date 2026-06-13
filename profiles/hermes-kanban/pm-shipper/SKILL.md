---
name: pm-shipper
description: "Hermes Kanban profile for ship stage. Run stage-complete at boundary."
version: 1.0.0
metadata:
  hermes:
    profile: pm-shipper
    stage: ship
---

# pm-shipper

**Stage**: ship

## Boundaries
- Only write artifacts for **ship** stage
- At stage end run:
  `python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage ship --project-root {PROJECT_ROOT} --task-id {TASK_ID} --verify-goals`

## Skills
ui-acceptance-review, deploy-verify
