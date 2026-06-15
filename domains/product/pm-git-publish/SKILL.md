---
name: pm-git-publish
description: "Git publish for PM pipeline runs: one idea = one public GitHub repo with GitHub Pages report."
version: 3.0.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, git, github, pages, publish]
    related_skills: [pm-idea-to-mvp]
---

# PM Git Publish

Each product idea is a **standalone public GitHub repo** under `ttmens/pm-{slug}` with a **GitHub Pages** static report.

## Paths

| Item | Value |
|------|-------|
| Local repo | `{PROJECT_ROOT}/` (pm-{slug} root) |
| Skills root | `{SKILLS_ROOT}/` (ttmens-skills or install dir) |
| GitHub repo | `https://github.com/ttmens/pm-{slug}` |
| Pages URL | `https://ttmens.github.io/pm-{slug}/` |
| Index | `https://ttmens.github.io/pm-pipeline-index/` |

## Orchestrator: new idea

**Do NOT rely on LLM auto_decompose** for PM pipeline tasks. Use deterministic decompose:

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py \
  --task-id {triage_task_id} --slug {slug} --project-root {PROJECT_ROOT}
```

Bootstrap repo if needed:

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/bootstrap_github_repo.py \
  --dir {PROJECT_ROOT} --slug {slug} --description "PM pipeline: {title}"
```

Kanban comment on parent:

```
repo: https://github.com/ttmens/pm-{slug}
pages: https://ttmens.github.io/pm-{slug}/
```

## Worker: after each stage (MANDATORY)

From `{PROJECT_ROOT}`:

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py \
  --project-root {PROJECT_ROOT} --stage {stage} --message "stage({stage}): summary"
```

`stage-complete.py` runs `validate-gates` + `eval-stage` + `goal-check` + report build + git push. **Exit non-zero → do not mark stage complete.**

### Stage names

| Profile | `--stage` value | Notes |
|---------|-----------------|-------|
| pm-aligner | `align` | G1 debate gate |
| pm-researcher | `research` | |
| pm-analyst | `analysis` | C4 + PK debate |
| pm-planner | `spec` | G2 red-team panel |
| pm-builder | `mvp` | inner-loop |
| pm-shipper | `ship` | human checkpoint default |
| pm-builder | `retro` | harness evolution |

## Retro (pm-builder)

```bash
python {SKILLS_ROOT}/scripts/merge-retro-knowledge.py --project-root {PROJECT_ROOT}
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py \
  --project-root {PROJECT_ROOT} --stage retro --message "stage(retro): pipeline complete"
```

产物使用**简体中文**。

## Feishu notification

`stage-complete.py` 调用 `{SKILLS_ROOT}/scripts/feishu_notify.py` 向 `FEISHU_HOME_CHANNEL` 推送阶段摘要。

## Failure handling

If `stage-complete.py` fails: block with stderr summary. Do not mark complete.
