# OpenCode

> Agent 安装与 MVP 委托：[AGENT_ONBOARDING.md](../AGENT_ONBOARDING.md)

## Install

```bash
./install.sh --core --platform opencode --project /path/to/app
```

Global: `~/.config/opencode/skills/`  
Project: `<project>/.opencode/skills/` + `AGENTS.md` template

## Entry

Say **从想法做到上线**. Loads `pm-idea-to-mvp` v6.1.

## MVP delegation

```bash
opencode run "Implement per openspec/tasks.md" --workdir ./04-mvp
```

Run stage-complete manually after each phase:

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py \
  --stage mvp --project-root . --runtime --verify-goals
```

See `profiles/hermes-opencode/opencode/SKILL.md` (optional `--profile hermes`).

[command-recipes.md](../../pipelines/pm-idea-to-mvp/references/command-recipes.md)
