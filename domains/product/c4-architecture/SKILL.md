---
name: c4-architecture
description: "C4 architecture (Context/Container/Component) + multi-option PK debate mode for analysis."
version: 1.1.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, architecture, c4, design]
    related_skills: [openspec, pm-idea-to-mvp]
---

# C4 Architecture — Product Architecture Modeling

Use the **C4 model** for all architecture-level product documentation. Code-level (C4 Level 4) is optional.

## Output (project dir)

```
architecture/
  c4-context.md      # Level 1 — system context
  c4-container.md    # Level 2 — containers
  c4-component.md    # Level 3 — components (≥1 container)
```

## Language

- 面向用户的说明使用**简体中文**
- 技术标识符、API 名可保留英文

## c4-context.md template

```markdown
# C4 Level 1 — 系统上下文

## 系统
{产品名} — 一句话职责

## 外部角色
| 角色 | 说明 |
|------|------|
| ... | ... |

## 上下文图
```mermaid
C4Context
  ...
```
```

## c4-container.md template

```markdown
# C4 Level 2 — 容器

## 容器清单
| 容器 | 技术 | 职责 |
|------|------|------|

## 容器图
```mermaid
flowchart TB
  ...
```

## ADR 映射
| ADR | 影响的容器 |
|-----|-----------|
```

## c4-component.md template

Pick the most complex container (usually API/backend) and decompose into components.

## Process

1. Read `02-analysis.md`, `CONTEXT.md`, `decisions.md`, existing `openspec/design.md`
2. Write L1 → L2 → L3 in order; each level must reference the previous
3. Update `openspec/design.md` to **link** C4 files (do not replace with ASCII-only diagram)
4. New ADRs must note affected C4 Container

## Verification

- ≥2 external actors in context
- ≥3 containers in container doc
- ≥1 component breakdown
- `openspec/design.md` contains `architecture/c4-` links

## Architecture PK mode (multi-option debate)

Run during **analysis**, after draft `02-analysis.md`, when ≥2 viable architecture directions exist.

### Protocol

1. Assign **Option A / B / C** roles: each writes `debates/analysis-option-{A|B|C}.md` with mini-ADR (context, decision, consequences).
2. **Judge** reads all options + `01-research.md`; writes `debates/analysis-synthesis.md` with recommended option, rejected options + why, top 3 risks + mitigations.
3. Update `02-analysis.md` recommendation section and `architecture/c4-*.md` to match the winner.

### Gate

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage analysis --project-root {PROJECT_ROOT}
```

Require ≥2 `debates/analysis-option-*.md` files + `debates/analysis-synthesis.md` before analysis complete.
