---
name: pm-git-publish
description: "Git publish for PM pipeline runs: one idea = one public GitHub repo with GitHub Pages report."
version: 3.1.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, git, github, pages, publish]
    related_skills: [pm-idea-to-mvp]
---

# PM Git Publish

Each product idea is a **standalone public GitHub repo** under `ttmens/pm-{slug}` with **GitHub Pages** report.

## Paths

| Item | Value |
|------|-------|
| Local repo | `{PROJECT_ROOT}/` |
| GitHub repo | `https://github.com/ttmens/pm-{slug}` |
| Pages URL | `https://ttmens.github.io/pm-{slug}/` |

## New project bootstrap

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/init-project.py \
  --project-root {PROJECT_ROOT} --slug {slug}
```

Use `{SKILLS_ROOT}/scripts/publish_repo.py` to create GitHub repo when needed.

## After each stage (v9.1)

1. Verify stage artifacts per `pm-idea-to-mvp/SKILL.md`
2. Commit and push to `pm-{slug}` repo
3. Optional: `python {SKILLS_ROOT}/scripts/feishu_notify.py --stage {stage} --status done --project-root {PROJECT_ROOT}`

**No** `stage-complete.py` in v9 — artifact paths are the SSOT.

## Retro

```bash
python {SKILLS_ROOT}/scripts/merge-retro-knowledge.py --project-root {PROJECT_ROOT}
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/consume-feedback.py \
  --project-root {PROJECT_ROOT} --append-retro --write
```

产物使用**简体中文**。
