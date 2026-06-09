---
name: pm-git-publish
description: "Git publish for PM pipeline runs: one idea = one public GitHub repo with GitHub Pages report."
version: 2.0.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, git, github, pages, publish]
    related_skills: [pm-idea-to-mvp, github-repo-management]
---

# PM Git Publish

Each product idea is a **standalone public GitHub repo** under `ttmens/pm-{slug}` with a **GitHub Pages** static report.

## Paths

| Item | Value |
|------|-------|
| Local repo | `D:/workspace/projects/pm-{slug}/` |
| GitHub repo | `https://github.com/ttmens/pm-{slug}` |
| Pages URL | `https://ttmens.github.io/pm-{slug}/` |
| Index | `https://ttmens.github.io/pm-pipeline-index/` |

## Orchestrator: new idea (v3)

**Do NOT rely on LLM auto_decompose** for PM pipeline tasks. Use deterministic decompose:

```powershell
python D:\workspace\pipelines\pm-idea-to-mvp\scripts\decompose-pm-pipeline.py --task-id {triage_task_id} --slug {slug}
```

Then bootstrap repo if needed:

```powershell
python D:\workspace\pipelines\pm-idea-to-mvp\scripts\publish_repo.py --dir D:\workspace\projects\pm-{slug} --slug {slug} --description "PM pipeline: {title}"
```

Kanban comment on parent:

```
repo: https://github.com/ttmens/pm-{slug}
pages: https://ttmens.github.io/pm-{slug}/
```

## Worker: after each stage (MANDATORY)

From repo root `D:\workspace\projects\pm-{slug}`:

```powershell
python D:\workspace\pipelines\pm-idea-to-mvp\scripts\stage-complete.py --run . --slug {slug} --stage {stage} --message "stage({stage}): summary"
```

`stage-complete.py` runs L0 `validate-gates` + L1 `eval-stage` + `build-run-report` + git push. **Exit non-zero → kanban_block, do NOT kanban_complete.**

### Stage names

| Profile | `--stage` value | Notes |
|---------|-----------------|-------|
| pm-aligner | `align` | |
| pm-researcher | `research` | |
| pm-analyst | `analysis` | |
| pm-planner | `spec` | Also runs `prototype` gate |
| pm-builder | `mvp` | |
| pm-builder | `retro` | Then `merge-retro-knowledge.py` |

Planner may iterate on openspec/prototype **within** the spec task before running stage-complete.

## Retro (pm-builder)

```powershell
python D:\workspace\pipelines\pm-idea-to-mvp\scripts\merge-retro-knowledge.py --run .
python D:\workspace\pipelines\pm-idea-to-mvp\scripts\stage-complete.py --run . --slug {slug} --stage retro --message "stage(retro): pipeline complete"
```

产物使用**简体中文**。

## Feishu notification

`stage-complete.py` 调用 `feishu_notify.py` 向 `FEISHU_HOME_CHANNEL` 推送：

```
【PM 流水线】pm-{slug} — {stage} 完成
产物页 / 仓库 / Gate / 摘要
align、spec 阶段附加 ⏸ 人工确认提示
```

## Failure handling

If `stage-complete.py` fails: `kanban_block` with stderr summary. Do not mark complete.
