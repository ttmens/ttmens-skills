---
name: ux-principles
description: >-
  UX principles taxonomy audit (uxuiprinciples/agent-skills). Optional pre-layer
  for ui-acceptance-review: uxui-evaluator (journey) + interface-auditor (full).
version: 1.0.0
author: ttmens (wraps uxuiprinciples/agent-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ux, audit, profile]
    related_skills: [ui-acceptance-review, user-journey, dogfood]
---

# UX Principles (profile)

Orchestrates upstream **uxui-evaluator** and **interface-auditor** as optional pre-layers for `ui-acceptance-review`.

## Pipeline wiring

| ui-acceptance mode | Pre-step (this profile) | Output |
|--------------------|-------------------------|--------|
| **journey** | `uxui-evaluator` — 168 principles scan | Append to `04-mvp/UX-REVIEW.md` or `docs/UX-PRINCIPLES-JOURNEY.md` |
| **full** | `interface-auditor` — smell taxonomy | Merge findings into `docs/ui-acceptance-report.md` appendix |

Run **before** `ui_acceptance.py` script rubric.

## Upstream skills

| Skill | Vendor path |
|-------|-------------|
| `uxui-evaluator` | `vendor/uxuiprinciples-agent-skills/uxui-evaluator` |
| `interface-auditor` | `vendor/uxuiprinciples-agent-skills/interface-auditor` |

Installed copies live under `upstream/uxui-evaluator` and `upstream/interface-auditor`.

## API key (optional)

uxuiprinciples supports enriched output with an API key. **Non-blocking** — LLM-only mode works without key. Document key in project `.env` if user provides one; never commit secrets.

## Submodule

```bash
git submodule update --init vendor/uxuiprinciples-agent-skills
```

## Body-test reference

Lightweight supplement (not full submodule): [`references/body-test.md`](references/body-test.md) — posture / ergonomics checklist for desktop flows.
