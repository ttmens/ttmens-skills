# OpenCode

## Install

```bash
./install.sh --core --opencode
./install.sh --profile hermes --opencode   # optional opencode skill
.\install.ps1 -Target OpenCode
```

Global: `~/.config/opencode/skills/`  
Project: `<project>/.opencode/skills/`

```bash
./install.sh --project /path/to/app --opencode
```

## Entry

Project `AGENTS.md` pointing to `pm-idea-to-mvp`.

## PM phases

OpenCode loads skills from `.opencode/skills/`. Run PM stages via conversation + [command-recipes.md](../../pipelines/pm-idea-to-mvp/references/command-recipes.md).

## Coding delegation

For MVP stage:

```bash
opencode run "Implement per openspec/tasks.md and 03-prd.md" --workdir ./04-mvp
```

See `profiles/hermes-opencode/opencode/SKILL.md` (install with `--profile hermes`).

## Note

OpenCode does not expose phuryn slash commands; use plain-language prompt chains from command-recipes.
