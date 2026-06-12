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
python validate_skills.py
```
