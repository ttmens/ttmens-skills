---
name: pm-shipper
description: "Hermes Kanban profile for ship stage. Artifact-driven stage boundary (v9.1)."
version: 9.1.0
metadata:
  hermes:
    profile: pm-shipper
    stage: ship
---

# pm-shipper

**Stage**: ship

## Boundaries
- Only write artifacts for **ship** stage
- At stage end: verify SKILL.md artifact paths for **ship** exist; update PROGRESS.md

## Skills
ui-acceptance-review, deploy-verify
