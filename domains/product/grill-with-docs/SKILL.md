---
name: grill-with-docs
description: "Doc-grounded alignment + G1 assumption debate. Update CONTEXT.md, detect drift, then run debate protocol."
version: 1.1.0
author: PM Pipeline (adapted from mattpocock/skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, alignment, context, adr]
    related_skills: [grill-me, openspec, pm-idea-to-mvp]
---

# Grill With Docs — Context-Grounded Alignment

Use when `CONTEXT.md` exists or after first alignment pass. Ground interrogation in project vocabulary.

## Core behavior

- Read `CONTEXT.md`, `00-brief.md`, and prior stage artifacts before questioning.
- One question at a time; challenge terminology drift between brief and downstream docs.
- Write decisions back to disk — alignment without doc updates is incomplete.

## Required files

### CONTEXT.md (create or update)

```markdown
# Context — {project name}
## Glossary
| Term | Definition |
## Stakeholders
## Constraints
## Non-goals
```

### decisions.md (append ADRs)

```markdown
## ADR-{NNN}: {title}
- Status: accepted | proposed
- Context: ...
- Decision: ...
- Consequences: ...
```

## Exit criteria

- CONTEXT.md glossary has ≥3 terms
- Any irreversible choice has an ADR in decisions.md
- No conflicting definitions between brief and CONTEXT

## Handoff

- To pm-analyst when validating research conclusions against CONTEXT
- To pm-planner when PRD terms must match glossary

## G1 Debate Protocol

After CONTEXT/decisions are updated, run the same **Assumption Debate** protocol as `grill-me` (see `grill-me` § G1 Debate Protocol). Required before `stage-complete --stage align`.
