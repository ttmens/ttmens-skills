# Third-Party Skill Attribution

Borrowed skills are copied at install time from vendor submodules. Do not edit files under installed skill directories; update `borrowed/manifest.yaml` and re-run `./install.sh`.

## phuryn/pm-skills

- Repository: https://github.com/phuryn/pm-skills
- Version pin: v2.0.0 (see `borrowed/manifest.yaml`)
- License: MIT
- Author: Paweł Huryn / Product Compass

## anthropics/knowledge-work-plugins

- Repository: https://github.com/anthropics/knowledge-work-plugins
- Version pin: main (see `borrowed/manifest.yaml`)
- License: Apache-2.0 (per plugin; see vendor LICENSE files)
- Author: Anthropic

## Update procedure

```bash
cd vendor/phuryn-pm-skills && git fetch && git checkout v2.0.0
cd ../knowledge-work-plugins && git pull
cd ../..
./install.sh --borrowed-only --all
python scripts/validate_skills.py
```

## nextlevelbuilder/ui-ux-pro-max-skill (profile: ui-pro-max-full)

- Repository: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Version pin: **v2.5.0** (submodule `vendor/ui-ux-pro-max-skill`)
- License: MIT
- Install: `./install.sh --profile ui-pro-max-full --platform cursor`

## jmr85/e2e-agent-skills (profile: playwright-e2e)

- Repository: https://github.com/jmr85/e2e-agent-skills
- Version pin: main (submodule `vendor/e2e-agent-skills`)
- License: MIT
- Install: `./install.sh --profile playwright-e2e --platform cursor`

## uxuiprinciples/agent-skills (profile: ux-principles)

- Repository: https://github.com/uxuiprinciples/agent-skills
- Version pin: main (submodule `vendor/uxuiprinciples-agent-skills`)
- License: see vendor LICENSE
- Install: `./install.sh --profile ux-principles --platform cursor`
- Optional API key for enriched output — non-blocking
