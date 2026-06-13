---
name: assumption-debate
description: "G1 dual-agent debate: Advocate vs Skeptic on assumptions. Outputs debates/align-*.md + decisions.md#debate-align."
version: 1.0.0
---

# Assumption Debate (G1)

Run **after** `grill-me` / `grill-with-docs`, **before** G1 gate pass.

## Protocol (2 rounds + synthesis)

1. **Round 1 — Advocate**: Load `CONTEXT.md`; argue why the idea works; list top 5 assumptions as strengths.
2. **Round 1 — Skeptic**: Same assumptions; challenge each with failure mode + cheapest test.
3. **Round 2 — Advocate**: Respond to Skeptic with evidence or revised assumptions.
4. **Round 2 — Skeptic**: Final objections; mark unresolved as `OPEN?` only if human must decide.
5. **Synthesis — Judge**: Write `debates/align-synthesis.md` with resolved conclusions (no `OPEN?` / TBD).

## Outputs

- `debates/align-round1-advocate.md`
- `debates/align-round1-skeptic.md`
- `debates/align-round2-advocate.md`
- `debates/align-round2-skeptic.md`
- `debates/align-synthesis.md`
- Append summary to `decisions.md` under `## Debate Align`

## Gate

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage align --project-root {PROJECT_ROOT}
```

Goal `debate_resolved` must pass before `stage-complete --stage align`.
