# OpenCode

> Agent 安装与 MVP 委托：[AGENT_ONBOARDING.md](../AGENT_ONBOARDING.md)

## Install

```bash
./install.sh --core --profile debate --platform opencode --project /path/to/app
```

Global: `~/.config/opencode/skills/`  
Project: `<project>/.opencode/skills/` + `AGENTS.md` template (v9.1.0)

## Path variables

| Variable | Meaning |
|----------|---------|
| `{SKILLS_ROOT}` | ttmens-skills install root (skills + pipeline scripts) |
| `{PROJECT_ROOT}` | pm-{slug} product repo (artifacts, gates.json) |

Detect:

```bash
python {SKILLS_ROOT}/scripts/detect_agent_env.py --json
python {SKILLS_ROOT}/scripts/validate_skills.py
```

## Entry

Say **从想法做到上线**. Loads `pm-idea-to-mvp` v9.1.0.

## MVP delegation

```bash
opencode run "Implement per openspec/tasks.md" --workdir ./04-mvp
```

Run stage-complete manually after each phase:

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/SKILL.md 产物路径验证 \
  --stage mvp --project-root . --runtime --verify-goals
```

See `profiles/hermes-opencode/opencode/SKILL.md` (optional `--profile hermes`).

[CODING_CONVENTIONS.md](../../pipelines/pm-idea-to-mvp/references/CODING_CONVENTIONS.md)
