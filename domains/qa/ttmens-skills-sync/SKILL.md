---
name: ttmens-skills-sync
description: "Sync ttmens-skills GitHub repo to local Hermes skills directory. Covers network fallback (API zip when git blocked), path mapping, vendor/submodule handling, Kanban profile installation, deprecated skill cleanup, and verification. Use when upgrading pipeline version or syncing skill library."
version: 1.2.0
author: Hermes Agent
platforms: [windows]
metadata:
  hermes:
    tags: [skills, sync, upgrade, hermes, ttmens-skills, kanban, network-fallback, vendor-submodules]
---

# ttmens-skills Sync to Local Hermes

Sync the ttmens-skills GitHub repo (D:/workspace/ttmens-skills) to local Hermes skills directory (D:/hermes-data/skills/).

## Critical Path Issue

**DO NOT use `install.sh` directly** — it targets `~/.hermes/skills/` but Hermes loads from `D:/hermes-data/skills/` (HERMES_HOME). The install script's path mapping is wrong for this setup.

**Correct approach**: Manual copy with path mapping.

## Path Mapping (Repo → Local)

The repo uses `domains/` structure; local uses category structure:

| Repo Path | Local Path |
|-----------|------------|
| `domains/product/*` | `product-management/*` |
| `domains/design/*` | `design/*` |
| `domains/engineering/*` | `software-development/*` |
| `domains/agents/*` | `workflow/*` |
| `domains/qa/*` | `devops/*` |
| `software-development/*` | `software-development/*` (top-level, direct copy) |
| `pipelines/pm-idea-to-mvp/*` | `pipelines/pm-idea-to-mvp/*` |
| `profiles/hermes-kanban/*` | `profiles/hermes-kanban/*` |
| `borrowed/*` | `borrowed/*` (metadata only; actual skills from vendor/) |
| `vendor/*` | Not synced directly; used as source for borrowed/ |
| `scripts/*` | `scripts/*` |

## Network Fallback (CRITICAL — GitHub often blocked on this host)

`git pull` to github.com:443 frequently fails (connection reset/timeout). **Always try git first**, but if it fails, use the API zip fallback:

```bash
# Test connectivity first
curl -sI --connect-timeout 10 https://api.github.com | head -1
# If api.github.com works (HTTP 200), use zip download:
cd /tmp
curl -L -s -o ttmens-skills.zip "https://api.github.com/repos/ttmens/ttmens-skills/zipball/main"
unzip -q -o ttmens-skills.zip -d ttmens-skills-new
REPO=/tmp/ttmens-skills-new/ttmens-ttmens-skills-*/
# Then proceed with sync steps using $REPO instead of D:/workspace/ttmens-skills
# After sync, copy back to D:/workspace/ttmens-skills: rm -rf D:/workspace/ttmens-skills/* && cp -r $REPO/* D:/workspace/ttmens-skills/
```

**Mirror proxies** (try in order if api.github.com also fails): gitclone.com, kkgithub.com, ghproxy.net — reliability varies.

## Sync Procedure

### 1. Pull Latest from Repo

```bash
cd D:/workspace/ttmens-skills
git pull
git submodule update --init --recursive  # for borrowed skills (requires GitHub access)
```

**If git fails** → use the Network Fallback above to download via API zip.

### 2. Upgrade Pipeline Core

```bash
REPO=D:/workspace/ttmens-skills
LOCAL=D:/hermes-data/skills

# Pipeline SKILL.md
cp "$REPO/pipelines/pm-idea-to-mvp/SKILL.md" "$LOCAL/pipelines/pm-idea-to-mvp/"

# All pipeline scripts
cp "$REPO/pipelines/pm-idea-to-mvp/scripts/"*.py "$LOCAL/pipelines/pm-idea-to-mvp/scripts/"

# Pipeline assets
cp "$REPO/pipelines/pm-idea-to-mvp/assets/"* "$LOCAL/pipelines/pm-idea-to-mvp/assets/"

# stage-skills.yaml
cp "$REPO/pipelines/pm-idea-to-mvp/stage-skills.yaml" "$LOCAL/pipelines/pm-idea-to-mvp/"
```

### 3. Upgrade Native Skills (with path mapping)

```bash
# product-management/ (from domains/product/)
for skill in c4-architecture docs-hygiene grill-me grill-with-docs open-design openspec pm-git-publish ui-ux-pro-max user-journey brownfield-bootstrap prd-red-team-panel; do
  cp -r "$REPO/domains/product/$skill/" "$LOCAL/product-management/$skill/"
done

# design/ (from domains/design/)
cp -r "$REPO/domains/design/ui-acceptance-review/" "$LOCAL/design/ui-acceptance-review/"

# software-development/ (from domains/engineering/)
for skill in requesting-code-review test-driven-development; do
  cp -r "$REPO/domains/engineering/$skill/" "$LOCAL/software-development/$skill/"
done

# workflow/ (from domains/agents/)
for skill in subagent-driven-development writing-plans; do
  cp -r "$REPO/domains/agents/$skill/" "$LOCAL/workflow/$skill/"
done

# devops/ (from domains/qa/)
cp -r "$REPO/domains/qa/dogfood/" "$LOCAL/devops/dogfood/"
```

### 4. Install Kanban Profiles (CRITICAL — often missed)

```bash
mkdir -p "$LOCAL/profiles/hermes-kanban"
for profile in pm-aligner pm-researcher pm-analyst pm-planner pm-builder pm-shipper pm-operator pm-growth; do
  cp -r "$REPO/profiles/hermes-kanban/$profile" "$LOCAL/profiles/hermes-kanban/"
done
```

### 3. Vendor Submodules (borrowed skill sources)

The repo uses `vendor/` submodules for borrowed skills. If `git submodule update` failed (network), download each vendor repo via API:

```bash
cd /tmp
for name_repo in "phuryn-pm-skills:phuryn/pm-skills" \
                 "knowledge-work-plugins:anthropics/knowledge-work-plugins" \
                 "ui-ux-pro-max-skill:nextlevelbuilder/ui-ux-pro-max-skill" \
                 "e2e-agent-skills:jmr85/e2e-agent-skills" \
                 "uxuiprinciples-agent-skills:uxuiprinciples/agent-skills"; do
  name="${name_repo%%:*}"; repo="${name_repo##*:}"
  curl -L -s -o "$name.zip" "https://api.github.com/repos/$repo/zipball/main"
  unzip -q -o "$name.zip" -d "${name}-extracted"
done
# Copy extracted dirs into repo vendor/:
REPO=D:/workspace/ttmens-skills
for name in phuryn-pm-skills knowledge-work-plugins ui-ux-pro-max-skill e2e-agent-skills uxuiprinciples-agent-skills; do
  src=$(ls -d /tmp/${name}-extracted/*/ | head -1)
  rm -rf "$REPO/vendor/$name" && cp -r "$src" "$REPO/vendor/$name"
done
```

### 4. Install Borrowed Skills (from vendor/ → local borrowed/)

Source paths in vendor/ repos:

```bash
REPO=D:/workspace/ttmens-skills
LOCAL=D:/hermes-data/skills
mkdir -p "$LOCAL/borrowed"

# From phuryn-pm-skills (pm-* prefix):
cp -r "$REPO/vendor/phuryn-pm-skills/pm-product-discovery/skills/identify-assumptions-new" "$LOCAL/borrowed/pm-identify-assumptions-new"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-product-discovery/skills/opportunity-solution-tree" "$LOCAL/borrowed/pm-opportunity-solution-tree"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-market-research/skills/competitor-analysis" "$LOCAL/borrowed/pm-competitor-analysis"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-market-research/skills/market-sizing" "$LOCAL/borrowed/pm-market-sizing"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-product-strategy/skills/product-strategy" "$LOCAL/borrowed/pm-product-strategy"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-execution/skills/create-prd" "$LOCAL/borrowed/pm-create-prd"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-execution/skills/user-stories" "$LOCAL/borrowed/pm-user-stories"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-ai-shipping/skills/shipping-artifacts" "$LOCAL/borrowed/pm-shipping-artifacts"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-ai-shipping/skills/intended-vs-implemented" "$LOCAL/borrowed/pm-intended-vs-implemented"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-marketing-growth/skills/north-star-metric" "$LOCAL/borrowed/pm-north-star-metric"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-go-to-market/skills/gtm-strategy" "$LOCAL/borrowed/pm-gtm-strategy"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-data-analytics/skills/sql-queries" "$LOCAL/borrowed/pm-sql-queries"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-execution/skills/retro" "$LOCAL/borrowed/pm-retro"
cp -r "$REPO/vendor/phuryn-pm-skills/pm-execution/skills/release-notes" "$LOCAL/borrowed/pm-release-notes"
cp "$REPO/vendor/phuryn-pm-skills/pm-ai-shipping/commands/security-audit-static.md" "$LOCAL/borrowed/pm-security-audit-static.md"

# From knowledge-work-plugins (kw-* prefix):
cp -r "$REPO/vendor/knowledge-work-plugins/engineering/skills/system-design" "$LOCAL/borrowed/kw-system-design"
cp -r "$REPO/vendor/knowledge-work-plugins/engineering/skills/testing-strategy" "$LOCAL/borrowed/kw-testing-strategy"
cp -r "$REPO/vendor/knowledge-work-plugins/engineering/skills/deploy-checklist" "$LOCAL/borrowed/kw-deploy-checklist"
cp -r "$REPO/vendor/knowledge-work-plugins/engineering/skills/incident-response" "$LOCAL/borrowed/kw-incident-response"
cp -r "$REPO/vendor/knowledge-work-plugins/operations/skills/runbook" "$LOCAL/borrowed/kw-runbook"
```

**Authoritative source**: Always check `borrowed/manifest.yaml` for the latest mapping — vendor paths may change between versions.

### 6. Upgrade SSOT Scripts

```bash
cp "$REPO/scripts/check_docs_ssot.py" "$LOCAL/scripts/"
cp "$REPO/scripts/ui_acceptance.py" "$LOCAL/scripts/"
cp "$REPO/scripts/install_skills.py" "$LOCAL/scripts/"
```

### 7. Cleanup Deprecated Skills

Remove skills that repo has deprecated or replaced:
- `design/design-system-md` (deprecated in repo)
- `workflow/idea-to-product` (replaced by pm-idea-to-mvp v6)
- `workflow/docs-hygiene` (duplicate of product-management/docs-hygiene)
- `devops/kanban-orchestrator` (replaced by Hermes built-in Kanban)
- `devops/kanban-worker` (replaced by Hermes built-in Kanban)
- `borrowed/kw-code-review` (replaced by native requesting-code-review)

### 8. Verify

```bash
# Run repo validation
cd D:/workspace/ttmens-skills
python scripts/validate_skills.py

# Check local counts
echo "Pipeline: $(grep '^version:' $LOCAL/pipelines/pm-idea-to-mvp/SKILL.md | head -1)"
echo "Scripts: $(ls $LOCAL/pipelines/pm-idea-to-mvp/scripts/*.py | wc -l)"
echo "Native: $(find $LOCAL/product-management $LOCAL/design $LOCAL/software-development $LOCAL/workflow $LOCAL/devops/dogfood -name SKILL.md | wc -l)"
echo "Borrowed: $(ls $LOCAL/borrowed/ | wc -l)"
echo "Profiles: $(ls $LOCAL/profiles/hermes-kanban/ | wc -l)"
```

## Expected Counts (v7.2.0)

| Component | Count |
|-----------|-------|
| Pipeline scripts | 35 |
| Native skills | 17 (in domains/) |
| Borrowed skills | 20 (from vendor/) |
| Kanban profiles | 8 |
| SSOT scripts | 3+ (feishu_notify, validate_skills, check_docs_ssot) |
| Vendor repos | 5 (submodules) |

## Reverse sync (local → repo)

When evolving pipeline on `HERMES_HOME/skills/` (e.g. `D:/hermes-data/skills`), **commit changes to ttmens-skills Git first**, then sync repo → local. See [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md).

## Push to GitHub (agent-autonomous)

**Do not ask the user to push manually.** Token SSOT: `D:/hermes-data/.env` → `GITHUB_TOKEN`.

```powershell
cd D:/workspace/ttmens-skills
powershell -NoProfile -File scripts/push_to_github.ps1
```

Remote must be `https://github.com/ttmens/ttmens-skills.git` (script sets this). See [`docs/GIT_WORKFLOW.md`](../../../docs/GIT_WORKFLOW.md).

## Pitfalls

1. **GitHub network blocked** — `git pull` to github.com:443 often fails (connection reset/timeout). Use `api.github.com` zip download as fallback (see Network Fallback section).
2. **install.sh targets wrong path** — always use manual copy with path mapping
3. **Kanban profiles often missed** — they're in `profiles/hermes-kanban/`, not in core install
4. **Nested duplicates** — when copying, check for `skill/skill/` nesting and clean up (e.g., `pm-idea-to-mvp/pm-idea-to-mvp/`)
5. **Borrowed skill renames** — repo may rename (e.g., kw- → pm- prefix), handle manually
6. **Submodule init requires GitHub** — if `git submodule update` fails, download vendor repos via API zip (see step 3)
7. **PyYAML prerequisite** — `install_skills.py` requires `pip install pyyaml`; if unavailable, use manual copy steps above
8. **Version mismatch** — repo may have multiple SKILL.md files (e.g., main v7.1.0 + legacy v6.0 in subdirectory); ensure you copy the correct one

## When to Use

- Upgrading pm-idea-to-mvp pipeline version (e.g., v6.0 → v6.1)
- Syncing after `git pull` on ttmens-skills repo
- Installing new Kanban profiles
- Cleaning up deprecated skills after major version upgrade
