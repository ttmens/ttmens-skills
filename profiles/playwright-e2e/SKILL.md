---
name: playwright-e2e
description: >-
  Playwright E2E automation profile (jmr85/e2e-agent-skills). Scaffold e2e/
  smoke tests; run npm run test:e2e before ship when profile installed.
version: 1.0.0
author: ttmens (wraps jmr85/e2e-agent-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [qa, e2e, playwright, profile]
    related_skills: [dogfood, ui-acceptance-review, test-driven-development]
---

# Playwright E2E (profile)

Optional profile for **automated** browser regression alongside `dogfood` (exploratory) and `ui_acceptance.py` (rubric).

## When to use

| Stage | Action |
|-------|--------|
| **spec** | If `--profile playwright-e2e` or `package.json` exists → ensure `e2e/` scaffold via `init-project.py --profile playwright-e2e` |
| **mvp** | Add smoke specs for P0 journey paths |
| **ship** | `npm run test:e2e` — **warning** if profile not installed; **recommended** when installed |

## Upstream skill

Load vendor **`playwright-automation-expert`** (from `vendor/e2e-agent-skills/skills/playwright-automation-expert`) for test authoring patterns.

Install bundles upstream under `upstream/` or reference `{SKILLS_ROOT}/vendor/e2e-agent-skills`.

## Project scaffold

Templates SSOT: `{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/assets/templates/`

- `playwright.config.template.ts` → `e2e/playwright.config.ts`
- `e2e-smoke.template.spec.ts` → `e2e/smoke.spec.ts`

Add to `package.json`:

```json
"scripts": {
  "test:e2e": "playwright test"
}
```

## Gate behavior

- **Without profile**: ship gate does not require `npm run test:e2e` (dogfood + ui_acceptance remain)
- **With profile**: agent should run `npm run test:e2e` before `stage-complete --stage ship`; failures block ship

## Submodule

```bash
git submodule update --init vendor/e2e-agent-skills
```
