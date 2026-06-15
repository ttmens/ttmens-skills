# Cursor

> Agent 安装与 `{SKILLS_ROOT}` 解析：[AGENT_ONBOARDING.md](../AGENT_ONBOARDING.md)

## Install

```bash
./install.sh --core --profile debate --platform cursor --project /path/to/your-app
# or global skills only:
./install.sh --core --profile debate --cursor
```

Installs skills to `~/.cursor/skills/` or `<project>/.cursor/skills/`, plus project templates:
- `AGENTS.md` (v7.1.0)
- `.cursor/hooks.json` + `scripts/stage-gate-hook.py`

## Detect environment

```bash
python {SKILLS_ROOT}/scripts/detect_agent_env.py --json
python {SKILLS_ROOT}/scripts/validate_skills.py
```

## Entry

Say **从想法做到上线**. Agent loads `pm-idea-to-mvp` v7.1.0 (Loop Engineering + behavior code).

Human checkpoints: per `harness-rules.yaml` (default: **ship** only). G1/G2 debate gates via `grill-me` (debate protocol) / `prd-red-team-panel`.

## Stage exit (required)

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py \
  --stage mvp --project-root . --runtime --verify-goals
```

Writes `.cursor/stage-status.json` for hooks.

## Quality gates

```bash
python {SKILLS_ROOT}/scripts/check_docs_ssot.py --project-root {PROJECT_ROOT}
python {SKILLS_ROOT}/scripts/ui_acceptance.py --project-root {PROJECT_ROOT} --quick
python {SKILLS_ROOT}/scripts/deploy-verify.py --project-root {PROJECT_ROOT}
```

## Borrowed workflows

[command-recipes.md](../../pipelines/pm-idea-to-mvp/references/command-recipes.md)
