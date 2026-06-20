---
name: pm-operator
description: "Hermes Kanban profile for operate stage. Artifact-driven stage boundary (v9.1)."
version: 9.1.0
metadata:
  hermes:
    profile: pm-operator
    stage: operate
---

# pm-operator

**Stage**: operate

## Boundaries
- Only write artifacts for **operate** stage
- At stage end: verify SKILL.md artifact paths for **operate** exist; update PROGRESS.md

## Skills
kw-runbook
