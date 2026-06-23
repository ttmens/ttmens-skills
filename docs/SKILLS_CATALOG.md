<!-- AUTO:CATALOG -->
# Skills Catalog

> Maintainer index — auto-generated. Reader-facing docs: [README.md](../README.md).

Generated: 2026-06-16 01:05 UTC

**Counts:** 18 native + 20 borrowed = **38** core skills

## Pipeline

Entry: `pm-idea-to-mvp` — stages: brief, align, research, analysis, spec, mvp, ship, operate, grow, retro

| Stage | Gate |
|-------|------|
| brief | — |
| align | G1 |
| research | — |
| analysis | — |
| spec | G2 |
| mvp | G3 |
| ship | — |
| operate | — |
| grow | — |
| retro | — |

## Native skills (core)

| ID | Path | Role | Stages | Platforms | What | Use when |
|----|------|------|--------|-----------|------|----------|
| `pm-idea-to-mvp` | `pipelines/pm-idea-to-mvp` | pipeline | all | cursor, hermes, opencode | 唯一主流水线，G1/G2/G3 门禁 | 从想法做到上线、继续 pm-{slug} |
| `grill-me` | `domains/product/grill-me` | product | align | cursor, hermes, opencode | 逐问对齐 + G1 假设辩论协议 | 新想法、无 CONTEXT.md |
| `grill-with-docs` | `domains/product/grill-with-docs` | product | align | cursor, hermes, opencode | 基于文档的对齐、术语漂移检测 + G1 辩论 | 已有 CONTEXT.md，续跑对齐 |
| `docs-hygiene` | `domains/product/docs-hygiene` | product | analysis, mvp, ship | cursor, hermes, opencode | SSOT 文档漂移检测与修复 | 阶段开始/结束、棕地项目 |
| `c4-architecture` | `domains/product/c4-architecture` | product | analysis | cursor, hermes, opencode | C4 架构图、ADR + 多方案 PK 模式 | 方案论证阶段 |
| `openspec` | `domains/product/openspec` | product | analysis, spec | cursor, hermes, opencode | 规格驱动：proposal/design/tasks | 分析后写实现规格 |
| `user-journey` | `domains/product/user-journey` | product | spec | cursor, hermes, opencode | 用户旅程驱动页面与 IA | spec 阶段写 03b-user-journey.md |
| `open-design` | `domains/product/open-design` | product | spec | cursor, hermes, opencode | 可点击静态原型 + 可选 sketch 变体 | PRD 前需要可交互原型 |
| `ui-ux-pro-max` | `domains/product/ui-ux-pro-max` | product | spec, mvp | cursor, hermes, opencode | DESIGN.md tokens 生成与漂移维护 | MVP 实现前定视觉 SSOT |
| `ui-acceptance-review` | `domains/design/ui-acceptance-review` | design | mvp, ship | cursor, hermes, opencode | UX 评审 + 脚本 rubric + polish 三合一 | MVP/ship、Gate G3 |
| `writing-plans` | `domains/agents/writing-plans` | agents | mvp | cursor, hermes, opencode | 拆 bite-sized 实现任务 | openspec tasks 落地前 |
| `subagent-driven-development` | `domains/agents/subagent-driven-development` | agents | mvp | cursor, hermes, opencode | 逐 Task 子代理实现与审查 | MVP 编码主循环 |
| `test-driven-development` | `domains/engineering/test-driven-development` | engineering | mvp | cursor, hermes, opencode | RED-GREEN-REFACTOR（obra 衍生） | 实现业务逻辑 |
| `requesting-code-review` | `domains/engineering/requesting-code-review` | engineering | mvp, ship | cursor, hermes, opencode | 提交前安全与质量门 | commit 前 |
| `dogfood` | `domains/qa/dogfood` | qa | mvp, ship | cursor, hermes, opencode | 探索式 Web QA | MVP 走查核心路径 |
| `pm-git-publish` | `domains/product/pm-git-publish` | product | retro | cursor, hermes, opencode | GitHub Pages 阶段报告 | 每阶段结束（Hermes） |
| `prd-red-team-panel` | `domains/product/prd-red-team-panel` | product | spec | cursor, hermes, opencode | G2 PRD 红队面板（需 --profile debate 安装 phuryn 依赖） | spec 阶段 PRD 完成后 |
| `remote-server-deployment` | `devops/remote-server-deployment` | qa | ship | cursor, hermes, opencode | SSH 远程部署：registry 优先、密钥认证、PM2、浏览器 E2E | ship 阶段部署到 VPS |

## Borrowed skills (core)

| Install as | Source | Stage | Platforms |
|------------|--------|-------|-----------|
| `pm-identify-assumptions-new` | `phuryn/pm-product-discovery/skills/identify-assumptions-new` | align | cursor, hermes, opencode |
| `pm-opportunity-solution-tree` | `phuryn/pm-product-discovery/skills/opportunity-solution-tree` | research | cursor, hermes, opencode |
| `pm-competitor-analysis` | `phuryn/pm-market-research/skills/competitor-analysis` | research | cursor, hermes, opencode |
| `pm-market-sizing` | `phuryn/pm-market-research/skills/market-sizing` | research | cursor, hermes, opencode |
| `pm-product-strategy` | `phuryn/pm-product-strategy/skills/product-strategy` | analysis | cursor, hermes, opencode |
| `pm-create-prd` | `phuryn/pm-execution/skills/create-prd` | spec | cursor, hermes, opencode |
| `pm-user-stories` | `phuryn/pm-execution/skills/user-stories` | spec | cursor, hermes, opencode |
| `pm-shipping-artifacts` | `phuryn/pm-ai-shipping/skills/shipping-artifacts` | ship | cursor, hermes, opencode |
| `pm-intended-vs-implemented` | `phuryn/pm-ai-shipping/skills/intended-vs-implemented` | ship | cursor, hermes, opencode |
| `pm-north-star-metric` | `phuryn/pm-marketing-growth/skills/north-star-metric` | grow | cursor, hermes, opencode |
| `pm-gtm-strategy` | `phuryn/pm-go-to-market/skills/gtm-strategy` | grow | cursor, hermes, opencode |
| `pm-sql-queries` | `phuryn/pm-data-analytics/skills/sql-queries` | operate | cursor, hermes, opencode |
| `pm-retro` | `phuryn/pm-execution/skills/retro` | retro | cursor, hermes, opencode |
| `pm-release-notes` | `phuryn/pm-execution/skills/release-notes` | retro | cursor, hermes, opencode |
| `pm-security-audit-static` | `phuryn/pm-ai-shipping/commands/security-audit-static.md` | ship | cursor, hermes, opencode |
| `kw-system-design` | `anthropic/engineering/skills/system-design` | analysis | cursor, hermes, opencode |
| `kw-testing-strategy` | `anthropic/engineering/skills/testing-strategy` | mvp | cursor, hermes, opencode |
| `kw-deploy-checklist` | `anthropic/engineering/skills/deploy-checklist` | ship | cursor, hermes, opencode |
| `kw-incident-response` | `anthropic/engineering/skills/incident-response` | operate | cursor, hermes, opencode |
| `kw-runbook` | `anthropic/operations/skills/runbook` | operate | cursor, hermes, opencode |

## Optional profiles

### obsidian — Obsidian 笔记

Path: `profiles/obsidian` — skills: `obsidian-todo-manager`, `obsidian-deepen-review`, `obsidian-note-summarizer`

Install: `./install.sh --profile {pid} --all`

### deep-research — 深度行业调研

Path: `profiles/deep-research` — skills: `industry-benchmark`

Install: `./install.sh --profile {pid} --all`

### hermes — Hermes 编排

Path: `profiles` — skills: `plan`, `opencode`

Install: `./install.sh --profile {pid} --all`

### hermes-kanban — Hermes Kanban 阶段 Profile

Path: `profiles/hermes-kanban` — skills: `pm-aligner`, `pm-researcher`, `pm-analyst`, `pm-planner`, `pm-builder`, `pm-shipper`, `pm-operator`, `pm-growth`

Install: `./install.sh --profile {pid} --all`

### debate — G2 红队面板依赖 (phuryn)

Path: `borrowed` — skills: `pm-strategy-red-team`, `pm-pre-mortem`

Install: `./install.sh --profile {pid} --all`

### ui-pro-max-full — UI UX Pro Max 完整版 (nextlevelbuilder)

Path: `profiles/ui-pro-max-full` — skills: `ui-pro-max-full`

Install: `./install.sh --profile {pid} --all`

### playwright-e2e — Playwright E2E (jmr85/e2e-agent-skills)

Path: `profiles/playwright-e2e` — skills: `playwright-e2e`

Install: `./install.sh --profile {pid} --all`

### ux-principles — UX 原则审计 (uxuiprinciples)

Path: `profiles/ux-principles` — skills: `ux-principles`

Install: `./install.sh --profile {pid} --all`


## Native by stage

### brief

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`

### align

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`
- `grill-me` — `domains/product/grill-me`
- `grill-with-docs` — `domains/product/grill-with-docs`

### research

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`

### analysis

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`
- `docs-hygiene` — `domains/product/docs-hygiene`
- `c4-architecture` — `domains/product/c4-architecture`
- `openspec` — `domains/product/openspec`

### spec

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`
- `openspec` — `domains/product/openspec`
- `user-journey` — `domains/product/user-journey`
- `open-design` — `domains/product/open-design`
- `ui-ux-pro-max` — `domains/product/ui-ux-pro-max`
- `prd-red-team-panel` — `domains/product/prd-red-team-panel`

### mvp

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`
- `docs-hygiene` — `domains/product/docs-hygiene`
- `ui-ux-pro-max` — `domains/product/ui-ux-pro-max`
- `ui-acceptance-review` — `domains/design/ui-acceptance-review`
- `writing-plans` — `domains/agents/writing-plans`
- `subagent-driven-development` — `domains/agents/subagent-driven-development`
- `test-driven-development` — `domains/engineering/test-driven-development`
- `requesting-code-review` — `domains/engineering/requesting-code-review`
- `dogfood` — `domains/qa/dogfood`

### ship

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`
- `docs-hygiene` — `domains/product/docs-hygiene`
- `ui-acceptance-review` — `domains/design/ui-acceptance-review`
- `requesting-code-review` — `domains/engineering/requesting-code-review`
- `dogfood` — `domains/qa/dogfood`
- `remote-server-deployment` — `devops/remote-server-deployment`

### operate

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`

### grow

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`

### retro

- `pm-idea-to-mvp` — `pipelines/pm-idea-to-mvp`
- `pm-git-publish` — `domains/product/pm-git-publish`


## Platforms

| Platform | Global | Project | Docs |
|----------|--------|---------|------|
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` | [cursor.md](platforms/cursor.md) |
| Hermes | `~/.hermes/skills/` | — | [hermes.md](platforms/hermes.md) |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` | [opencode.md](platforms/opencode.md) |

## Vendor attribution

Borrowed skills copy from `vendor/` at install. See [borrowed/ATTRIBUTION.md](../borrowed/ATTRIBUTION.md).

<!-- /AUTO:CATALOG -->