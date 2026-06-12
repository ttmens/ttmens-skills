# Cursor

## Install

```bash
./install.sh --core --cursor
# Windows:
.\install.ps1 -Target Cursor
```

Skills install to `~/.cursor/skills/` (global) or `<project>/.cursor/skills/` (project).

## Entry

Add to your project root `AGENTS.md` (copy from ttmens-skills or symlink):

```
Load pm-idea-to-mvp as the default pipeline. See ttmens-skills/AGENTS.md.
```

## Pipeline

Conversation-driven: say「从想法到上线」. Agent reads `pm-idea-to-mvp` v5.1 and follows the stage table. Pause at G1 (align), G2 (spec), G3 (mvp).

## Borrowed workflows

No slash commands. Use [command-recipes.md](../../pipelines/pm-idea-to-mvp/references/command-recipes.md).

## Quality gates

```bash
python scripts/check_docs_ssot.py --project-root .
python scripts/ui_acceptance.py --project-root . --mode quick
```

Optional `.cursor/hooks/` for pre-commit checks.
