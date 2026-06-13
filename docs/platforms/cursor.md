# Cursor

> Agent 安装与 `{SKILLS_ROOT}` 解析：[AGENT_ONBOARDING.md](AGENT_ONBOARDING.md)

## Install

```bash
./install.sh --core --platform cursor --project /path/to/your-app
# or global skills only:
./install.sh --core --cursor
```

Installs skills to `~/.cursor/skills/` or `<project>/.cursor/skills/`, plus project templates:
- `AGENTS.md`
- `.cursor/hooks.json` + `scripts/stage-gate-hook.py`

## Entry

Say **从想法做到上线**. Agent loads `pm-idea-to-mvp` v6.1 (Loop Engineering).

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
python {SKILLS_ROOT}/scripts/ui_acceptance.py --project-root {PROJECT_ROOT} --mode quick
python scripts/deploy-verify.py --project-root .
```

## Borrowed workflows

[command-recipes.md](../../pipelines/pm-idea-to-mvp/references/command-recipes.md)
