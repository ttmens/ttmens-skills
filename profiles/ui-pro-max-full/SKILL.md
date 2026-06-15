---
name: ui-pro-max-full
description: >-
  Full design intelligence (CSV search, 161 palettes, stack guidelines) from
  nextlevelbuilder/ui-ux-pro-max-skill. Use when slim ui-ux-pro-max tokens are
  insufficient. Optional profile — core ui-ux-pro-max unchanged.
version: 1.0.0
author: ttmens (wraps nextlevelbuilder/ui-ux-pro-max-skill)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design-system, ui, ux, profile]
    related_skills: [ui-ux-pro-max, open-design, user-journey]
---

# UI UX Pro Max — Full (profile)

**When to use full vs slim**

| Situation | Skill |
|-----------|--------|
| Standard pm-{slug}, DESIGN.md tokens from PRD/journey | Core **`ui-ux-pro-max`** (slim) |
| Industry palette, multi-stack reasoning, CSV design search | **`ui-pro-max-full`** (this profile) |

Install: `./install.sh --profile ui-pro-max-full --platform cursor`

## Upstream path

SSOT: [`references/upstream-path.md`](references/upstream-path.md)

After install, bundled upstream lives under `upstream/` in this skill directory; in source mode use `{SKILLS_ROOT}/vendor/ui-ux-pro-max-skill`.

## Workflow (spec / mvp)

1. Read `03-prd.md`, `03b-user-journey.md`, existing `04-mvp/DESIGN.md`
2. Run design-system search (from upstream scripts):

```bash
python "{UPSTREAM_ROOT}/scripts/search.py" "<product-type>" --domain product --design-system
python "{UPSTREAM_ROOT}/scripts/search.py" "<style>" --domain style
python "{UPSTREAM_ROOT}/scripts/search.py" "<stack>" --domain stack
```

`{UPSTREAM_ROOT}` = installed `upstream/` or `vendor/ui-ux-pro-max-skill/.claude/skills/ui-ux-pro-max` or `src/ui-ux-pro-max` in vendor checkout.

3. Persist tokens to `04-mvp/DESIGN.md` (same contract as slim skill)
4. **pm-builder** must cite DESIGN.md in implementation prompts

## Submodule init

```bash
git submodule update --init vendor/ui-ux-pro-max-skill
# pinned tag: v2.5.0 — see borrowed/ATTRIBUTION.md
```

## Verification

- DESIGN.md reflects search output (palette, typography, UX rules)
- MVP CSS uses token values from DESIGN.md
- No CDN drift if project forbids it in `decisions.md`
