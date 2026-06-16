---
name: pm-idea-to-mvp
description: "Super-dev pipeline v6.1: Production-tested with knowledge graph visualization, RAG fallback strategy, and end-to-end validation. Based on v6.0 with real-world deployment experience."
version: 6.1.0
author: ttmens
license: MIT
platforms: [cursor, hermes, opencode, linux, macos, windows]
metadata:
  hermes:
    tags: [super-developer, pipeline, kanban, github, pages, openspec, ship, ops, grow, inner-loop]
    related_skills:
      - grill-me
      - grill-with-docs
      - docs-hygiene
      - pm-create-prd
      - pm-opportunity-solution-tree
      - pm-strategy-red-team
      - c4-architecture
      - openspec
      - user-journey
      - open-design
      - ui-ux-pro-max
      - ui-acceptance-review
      - subagent-driven-development
      - opencode
      - kw-deploy-checklist
      - pm-shipping-artifacts
      - pm-gtm-strategy
      - pm-git-publish
      - dogfood
---

# Super Developer Pipeline v6.0 (pm-idea-to-mvp)

**唯一主流水线**（设计文档）。覆盖 PM、工程、运维、运营全链路。每个想法 = **一个 GitHub 仓库** + **GitHub Pages 报告** + **门禁流水线** + MVP **内循环**（Kanban 子任务）。

> **Hermes Kanban 运行时**：gateway/worker 执行 **v6.0** 图（外循环 9 阶段 + MVP Plan/iter1-3 内循环，见 `references/runtime-kanban-v6.0.md`）。脚本路径：`{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/`（唯一真相）。Worker 加载 `references/hermes-stage-cards/` 薄片，非本全文。

环境变量（替代硬编码路径）：

- `{PROJECT_ROOT}` — pm-{slug} 仓库根目录
- `{SKILLS_ROOT}` — ttmens-skills 仓库根目录（或 `~/.cursor/skills` 安装根）

## 语言（强制）

- 所有面向用户的产物（brief、调研、分析、PRD、retro、UI 文案）使用**简体中文**
- 代码、URL、技术标识符可保留英文
- 每阶段 `eval-stage.py` 含中文锚点检查

## Project directory (git repo root)

```
{PROJECT_ROOT}/   # e.g. D:/workspace/projects/pm-{slug}/
```

| Link | URL |
|------|-----|
| Pages | `https://ttmens.github.io/pm-{slug}/` |
| GitHub | `https://github.com/ttmens/pm-{slug}` |
| Index | `https://ttmens.github.io/pm-pipeline-index/` |

## Pipeline stages (strict gates)

| Stage | Profile | Artifacts | Native skills | Borrowed skills | Gate |
|-------|---------|-----------|---------------|-----------------|------|
| 0 brief | User | `00-brief.md` | — | — | Idea captured |
| 1 align | `pm-aligner` | `CONTEXT.md`, `decisions.md` | `grill-me`, `grill-with-docs` | `pm-identify-assumptions-new` | **G1** |
| 2 research | `pm-researcher` | `01-research.md` | — | `pm-opportunity-solution-tree`, `pm-competitor-analysis`, `pm-market-sizing` | ≥5 URLs |
| 3 analysis | `pm-analyst` | `02-analysis.md`, `architecture/c4-*.md` | `c4-architecture`, `openspec`, `docs-hygiene` | `pm-product-strategy`, `pm-strategy-red-team`, `kw-system-design` | C4 L1–L3 |
| 4 spec | `pm-planner` | `03b-user-journey.md`, `02b-prototype/`, `03-prd.md` | `user-journey`, `open-design`, `ui-ux-pro-max` | `pm-create-prd`, `pm-user-stories`, `pm-pre-mortem` | **G2** |
| 5 mvp | `pm-builder` | `04-mvp/`, `UX-REVIEW.md` | `writing-plans`, `subagent-driven-development`, `ui-ux-pro-max`, `ui-acceptance-review` (journey), `test-driven-development`, `requesting-code-review`, `dogfood` | `kw-code-review`, `kw-testing-strategy` | **G3** |
| 6 ship | `pm-shipper` | `RUNBOOK.md`, `docs/ui-acceptance-report.md` | `ui-acceptance-review` (full), `docs-hygiene` | `pm-shipping-artifacts`, `pm-intended-vs-implemented`, `kw-deploy-checklist`, `pm-security-audit-static` | Deploy ready |
| 7 operate | `pm-operator` | `07-ops-notes.md` | — | `kw-incident-response`, `kw-runbook`, `pm-sql-queries` | — |
| 8 grow | `pm-growth` | `06-growth.md` | — | `pm-north-star-metric`, `pm-gtm-strategy` | — |
| 9 retro | `pm-builder` | `05-retro.md`, `evolution-notes.md` | `pm-git-publish` | `pm-retro`, `pm-release-notes` | evolution |
| report | any | `docs/index.html` | `pm-git-publish` | — | Pages dashboard |

**G1/G2/G3**（吸收原 product-orchestrator）：align≈G1、spec≈G2、mvp/ship≈G3。棕地项目阶段开始前运行 `docs-hygiene`。

可选：`docs/workflow_state.yaml`（来自 greenfield-light profile）与 `gates.json` 并存，用于非 Kanban 断点续跑。

After each stage (Hermes): `validate-gates.py --write` → `pm-git-publish` when available.

Borrowed slash-command equivalents: `references/command-recipes.md`.

## Directory layout

```
pm-{slug}/
  00-brief.md
  CONTEXT.md
  decisions.md
  01-research.md
  02-analysis.md
  architecture/           # c4-context.md, c4-container.md, c4-component.md
  03b-user-journey.md
  02b-prototype/          # open-design: index.html + DESIGN.md
  03-prd.md
  01b-benchmark.md        # Refine only
  openspec/
    proposal.md
    design.md
    tasks.md
    specs/
  04-mvp/
    DESIGN.md             # ui-ux-pro-max tokens
    UX-REVIEW.md          # ui-acceptance-review (journey)
    README.md
  05-retro.md
  06-refine-retro.md      # Refine sprint only
  evolution-notes.md
  gates.json              # copy from pipelines/pm-idea-to-mvp/assets/gates.template.json
  docs/workflow_state.yaml  # optional, greenfield/brownfield resume
  feedback.jsonl
  06-growth.md
  07-ops-notes.md
  RUNBOOK.md
  docs/ui-acceptance-report.md
  RUN.md                  # 中文运行说明（decompose 时生成）
  docs/index.html
```

## Kanban task graph (v5.1)

```
Parent: "Idea: {title}"
├── pm-aligner:      "Grill 对齐想法" → CONTEXT.md + enriched brief
├── pm-researcher:   "深度调研" (parent: aligner) → 01-research.md
├── pm-analyst:      "方案论证" (parent: research) → 02-analysis.md + openspec/proposal.md
├── pm-planner:      "原型+PRD+OpenSpec" (parent: analyst) → 02b-prototype + 03-prd + openspec/
├── pm-builder:      "MVP 实现" (parent: planner) → 04-mvp/
├── pm-shipper:      "Ship 部署" (parent: MVP) → RUNBOOK.md + ui-acceptance-report
├── pm-operator:     "Operate 运维" (parent: ship) → 07-ops-notes.md
├── pm-growth:       "Grow 增长" (parent: operate) → 06-growth.md
└── pm-builder:      "Retro+进化" (parent: grow) → 05-retro.md
```

Worker assignees: `pm-aligner`, `pm-researcher`, `pm-analyst`, `pm-planner`, `pm-builder`, `pm-shipper`, `pm-operator`, `pm-growth`, `pm-builder` (retro).  
`pm-orchestrator` 仅负责分解与父任务汇总，**不**写 retro 文件。

## Validation scripts

```bash
python {SKILLS_ROOT}/scripts/check_docs_ssot.py --project-root {PROJECT_ROOT}
python {SKILLS_ROOT}/scripts/ui_acceptance.py --project-root {PROJECT_ROOT} --mode quick
# Hermes pipeline scripts (when present):
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/validate-gates.py --run {PROJECT_ROOT} --write
```

Gate failure → `kanban_block` + Feishu notify; do not promote next stage.

## 人工检查点（Human-in-the-loop）

默认在 **align**、**spec**、**ship（G3 部署）** 三处暂停；飞书通知含任务 ID 与 `unblock` 命令（`stage-complete` 在 git push **之前**发送，push 失败不吞通知）。

### 两段式协议

| 场景 | 判定 | 动作 |
|------|------|------|
| **首次运行** | `kanban_show` **无** unblock 评论 | 产物就绪 → `stage-complete --task-id <本任务ID>` → `kanban_block` → **不要** `kanban_complete` |
| **Resume** | `kanban_show` **有** unblock 评论且任务为 `ready` | 验证 gates 仍 pass → `kanban_complete`（可选 `stage-complete --skip-git`）→ **禁止**再次 `kanban_block` |

| 阶段 | block 理由 |
|------|-----------|
| **align** | `等待用户确认 align 产物` |
| **spec** | `等待用户确认 PRD/原型范围` |
| **ship** | `等待用户确认部署范围` |

`stage-complete.py` 每阶段向飞书 `FEISHU_HOME_CHANNEL` 推送真实消息；checkpoint 阶段 push 失败仅警告，不阻止 notify。

## Stage details

### Align (`pm-aligner`)

- `grill-me` if no CONTEXT.md; else `grill-with-docs`
- One question at a time; no code/research/recommendations
- Exit: `gates.json` → `align: pass`
- 完成后：见人工检查点两段式协议（首次 block，resume complete）

### Research (`pm-researcher`)

- Read `CONTEXT.md` + `00-brief.md`
- Tavily primary; browser fallback
- **必须** `write_file` 落盘 `01-research.md`；禁止仅 `kanban_comment`
- `01-research.md`: competitors, sources with URLs, confidence tags
- `stage-complete --stage research` 失败则 block，不得 complete

### Analysis (`pm-analyst`)

- Read `01-research.md` + `CONTEXT.md`
- `02-analysis.md`: ≥3 options, recommendation, risks
- `c4-architecture`: `architecture/c4-*.md`; ADRs map to containers
- Draft `openspec/proposal.md`; `openspec/design.md` links C4
- No implementation code

### Spec (`pm-planner`)

- `user-journey` → `03b-user-journey.md` first
- `open-design` prototype (static HTML; optional sketch variants inside skill)
- `03-prd.md`: ≤5 user stories, acceptance criteria
- `openspec/tasks.md` + `openspec/specs/` delta specs
- 完成后：见人工检查点两段式协议（首次 block，resume complete）

### MVP (`pm-builder`)

MVP chain (mandatory order):

```
writing-plans → ui-ux-pro-max → test-driven-development → subagent-driven-development → ui-acceptance-review (journey) → requesting-code-review → dogfood
```

Hermes 编码可追加 `profiles/hermes-opencode/opencode`（`opencode run`）。

- Require `openspec/tasks.md` before coding
- Generate `04-mvp/DESIGN.md` via `ui-ux-pro-max`
- OpenCode:

```bash
opencode run "Implement MVP per openspec/tasks.md and 03-prd.md. Apply 04-mvp/DESIGN.md tokens. ≤3 flows." --workdir {PROJECT_ROOT}/04-mvp
```

- Smoke test locally; Pages shows static report (MVP runs on localhost)

### Retro (`pm-builder`)

`05-retro.md` must include（**简体中文**）:

- Stage timing & skill hits/misses
- Assumption validation
- `skill_patch_proposals[]` for pipeline evolution
- Pending items from `feedback.jsonl`

Append distilled lessons to `{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/pipeline-knowledge/` when present.

## Self-evolution

| Layer | Path |
|-------|------|
| Run | `05-retro.md`, `evolution-notes.md` |
| Pipeline | `pipeline-knowledge/patterns.md`, `anti-patterns.md` |
| Skills | `pm-idea-to-mvp/CHANGELOG.md` (human-approved patches) |

`feedback.jsonl` schema:

```json
{"ts":"ISO8601","source":"feishu","stage":"analysis","signal":"用户否定方案B","proposed_delta":"ADR-003","status":"pending"}
```

## Orchestrator (`pm-orchestrator`)

- Route only — no align/research/analyze/plan/code/**retro file I/O**
- On new idea: gateway / `kanban_decompose` runs `decompose-pm-pipeline.py` (9 subtasks) before orchestrator worker starts (**no terminal** on orchestrator profile)
- Script path (authoritative): `D:/hermes-data/skills/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py`
- Kanban comment: `repo:` + `pages:` URLs + `RUN.md` 路径
- 父任务全部子任务 done 后汇总中文摘要
- Feishu 由 `stage-complete.py` → `feishu_notify.py` 自动推送

### Manual decompose fallback（仅当脚本缺失或 gateway 未拦截时）

若 `decompose-pm-pipeline.py` 不可用，用 `hermes kanban create` 手动创建，按依赖顺序创建父任务再子任务，用 `--parent` 链接：

```bash
# T1: Align (no parent, ready)
hermes kanban create "Stage 0+1: 对齐想法" --assignee pm-aligner --body "..."

# T2: Research (parent: T1)
hermes kanban create "Stage 2: 深度调研" --assignee pm-researcher --body "..." --parent <t1_id>

# T3..T6: 依次创建，每个 parent 为上一阶段任务 ID
```

创建完成后无需额外 dispatch — dispatcher 会自动拾取 ready 状态的任务。

## Refine 深化循环（v4，手动 CLI）

对已有 `pm-{slug}` 实现不满意时：

```powershell
hermes kanban refine {slug} --reason "实现不满意：需业界深研与优化"
hermes kanban dispatch
```

创建 4 子任务：业界深研 → C4 架构差距 → 旅程/UX 复审 → MVP 优化。Refine-3 含人工检查点。完成写 `06-refine-retro.md`。

### Refine 常见陷阱

**重复 Refine**：在 `hermes kanban refine` 之前先运行 `hermes kanban list` 检查是否已有同 slug 的 Refine 任务在跑（status: running/ready/todo，body 含 "Refine"）。如果已有，**不要**再创建一个新的 — 用 `hermes kanban show <root_id>` 跟踪已有 Refine 即可。重复 Refine 会产生两套独立任务树，浪费 token 并导致冲突。

**Refine-4 迭代超时恢复**：Refine-4（MVP 定向优化）任务 body 含 `writing-plans → ui-ux-pro-max → ui-acceptance-review (fix) → dogfood` 超长链，**极易**在 60 次迭代内无法完成，导致 `timed_out` → `gave_up`。但注意：超时前 agent 写入的代码/文件**通常已持久化**（write_file/patch 是原子操作）。恢复步骤：

1. `hermes kanban log <task_id>` 查看 agent 最后做了什么（读了哪些文件、写了哪些 patch）
2. 用 `read_file`、`terminal(grep)`、`sqlite3 PRAGMA` 确认代码变更已落盘
3. `write_file` 补写缺失的产物文件（通常是 `UX-REVIEW.md`、`06-refine-retro.md`）
4. 运行 `stage-complete.py --stage refine` 手动触发门禁验证
5. `hermes kanban complete <task_id> --summary "..."` 完成任务
6. `hermes kanban dispatch` 唤醒 orchestrator 根任务

**终止正在跑的旧任务**：`hermes kanban kill` 不存在。正确做法：
- 对 **running** 任务 → `hermes kanban reclaim <task_id>`（abort + reset to ready）
- 对 **todo/done** 任务 → `hermes kanban archive <task_id>`
- 注意：`reclaim` 只能用于当前正在运行的任务；如果任务已自动完成，`reclaim` 会返回 "not running or unknown id"。

**Refine 前端大规模升级陷阱**：Refine 涉及前端 CSS/JS/HTML 全面升级时（如设计系统 v2→v3），文件通常 >1000 行。此时：
- **禁止**一次性 `write_file` 整个大文件（stream 超时风险极高）
- **禁止**连续多次 `patch` 不做验证（`patch` 在 Windows 上可能报告 `success: true` 但内容未实际写入）
- **正确模式**：`read_file(offset, limit)` 获取精确上下文 → `patch` 单次修改 → `terminal(grep)` 验证关键 token 确实存在 → 下一个 patch
- 每完成一个文件的升级后，用 `terminal(grep -c "keyToken" file)` 做批量验证
- 最终必须运行项目自身的构建/生成命令（如 `python generator.py`）确认模板语法无误，再跑测试

**dispatch 延迟**：`hermes kanban dispatch` 可能返回 `Deferred (<profile> at per-profile cap, 1 running): <task_id>`。这是因为该 profile 已有一个任务在跑（并发上限）。这是正常行为 — dispatcher 会在当前任务完成后自动拾取 deferred 任务，无需手动干预。

## Upgrade History

See `references/v5.1-upgrade.md` for the v4→v5.1 upgrade procedure, directory restructure, borrowed skill installation, and name mapping tables.

## Platform notes

### Cursor / OpenCode

- 读取本 SKILL.md，按阶段表顺序执行；无 Kanban。
- 在 **align（G1）**、**spec（G2）**、**mvp（G3）** 暂停等待用户确认。
- 编码：`subagent-driven-development`（Cursor）或 `opencode run`（OpenCode）。
- phuryn 工作流：使用 `references/command-recipes.md` 中的 prompt 链。

### Hermes Agent

- 使用 Kanban 分解（见上文 task graph）；profile 分派各阶段。
- 人工卡点：align、spec；飞书 `stage-complete` / `kanban_block` 协议不变。
- MVP 链：`writing-plans` → `ui-ux-pro-max` → `test-driven-development` → `subagent-driven-development` → `ui-acceptance-review` → `opencode`（可选）→ …

### 棕地 / 轻量模式

- 无 Kanban 时：见 `references/greenfield-light.md`，用 `docs/workflow_state.yaml` 断点续跑。
- 阶段边界运行 `docs-hygiene`。

## Feishu trigger (Kanban — gateway v6.0)

Gateway **已拦截**下列消息并创建 Kanban triage + 运行 `decompose-pm-pipeline.py`（**不是**会话内 Ralph `/goal` 循环）：

```
/goal 产品想法：{描述}
/goal 使用最新的想法到产品mvp技能 {描述}
```

正文含以下任一关键词也会触发：`pm-idea-to-mvp`、`想法到产品mvp`、`想法到 mvp`、`产品想法`、`按 pm-idea-to-mvp`。

可选在正文中指定：`slug: product-knowledge` 或 `D:/workspace/projects/pm-{slug}/`。

中文主题自动 slug：`产品知识库` → `product-knowledge`。

Kanban 运行时见 `references/runtime-kanban-v6.0.md`（v6.0 外循环 + MVP 内循环）。脚本路径：

```
D:/hermes-data/skills/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py
```

Pull 技能后同步 profile：

```
python D:/hermes-data/skills/pipelines/pm-idea-to-mvp/scripts/sync-hermes-profiles.py
```
