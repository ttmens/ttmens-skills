---
name: grill-me
description: "Alignment interrogation: one question at a time, walk the decision tree, no code."
version: 1.0.0
author: PM Pipeline (adapted from mattpocock/skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, alignment, interrogation, discovery]
    related_skills: [grill-with-docs, pm-idea-to-mvp]
---

# Grill Me — Idea Alignment

Use when **no CONTEXT.md exists yet** (greenfield idea). Pressure-test the product thesis before research spend.

## Core behavior

- Ask **one question at a time**. Wait for answer (or infer from brief) before next.
- Walk the decision tree: problem → user → success metric → constraints → non-goals.
- Provide a **recommended answer** when the user is unsure.
- **Do not** research, write code, or build prototypes.

## Outputs (in run dir)

Enrich `00-brief.md` with sections:

- Problem statement (1 paragraph)
- Target user & job-to-be-done
- Success metrics (measurable)
- Constraints & non-goals
- Open assumptions (tag confidence)

## Exit criteria

- No unresolved `TBD` in brief
- At least 3 assumptions explicitly listed
- User/job and success metric are concrete

## Context budget / handoff

- If session is long or user answers are complete: **stop grilling** and write all decisions to disk.
- Mandatory outputs before complete: enriched `00-brief.md`, `CONTEXT.md` (glossary ≥3), initial `decisions.md` if any irreversible choice.
- Run `stage-complete.py --stage align` — do not hand off to research yourself.

## When to hand off

After align gate passes, pm-researcher takes over (via Kanban parent complete). Do not start competitor research here.
