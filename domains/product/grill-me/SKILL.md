---
name: grill-me
description: "Alignment interrogation + G1 assumption debate protocol. One question at a time, then Advocate vs Skeptic before G1."
version: 1.1.0
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
- Run `verify align artifacts (CONTEXT.md, decisions.md)` — do not hand off to research yourself.

## When to hand off

After align gate passes, pm-researcher takes over (via Kanban parent complete). Do not start competitor research here.

## G1 Debate Protocol (Assumption Debate)

Run **after** grilling completes and `CONTEXT.md` / `decisions.md` exist, **before** human align checkpoint.

Optional borrowed: `pm-identify-assumptions-new` to tabulate assumptions before debate.

### Protocol (2 rounds + synthesis)

1. **Round 1 — Advocate**: Load `CONTEXT.md`; argue why the idea works; list top 5 assumptions as strengths.
2. **Round 1 — Skeptic**: Same assumptions; challenge each with failure mode + cheapest test.
3. **Round 2 — Advocate**: Respond to Skeptic with evidence or revised assumptions.
4. **Round 2 — Skeptic**: Final objections; mark unresolved as `OPEN?` only if human must decide.
5. **Synthesis — Judge**: Write `debates/align-synthesis.md` with resolved conclusions (no `OPEN?` / TBD).

### Debate outputs

- `debates/align-round1-advocate.md`
- `debates/align-round1-skeptic.md`
- `debates/align-round2-advocate.md`
- `debates/align-round2-skeptic.md`
- `debates/align-synthesis.md`
- Append summary to `decisions.md` under `## Debate Align`

### Gate (G1)

Verify `debates/align-synthesis.md` exists under `{PROJECT_ROOT}` (no unresolved `OPEN?` / TBD).

