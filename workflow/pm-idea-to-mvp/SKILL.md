---
name: pm-idea-to-mvp
description: "E2E product pipeline v4: align → research → analysis(C4) → spec(journey) → MVP(UX review) → retro. Refine loop."
version: 4.0.0
author: PM Pipeline
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [product-management, pipeline, research, mvp, kanban, github, pages, alignment, openspec]
    related_skills:
      - kanban-orchestrator
      - kanban-worker
      - grill-me
      - grill-with-docs
      - openspec
      - open-design
      - ui-ux-pro-max
      - c4-architecture
      - user-journey
      - design-review
      - ux-optimize
      - industry-benchmark
      - pm-git-publish
      - plan
      - opencode
      - test-driven-development
      - requesting-code-review
      - dogfood
---

# PM Idea-to-MVP Pipeline v4

End-to-end workflow for IT product managers. Each idea = **one GitHub repo** + **GitHub Pages** + **gated pipeline** with C4 architecture, user-journey-driven UX, design-review/optimize, and optional **Refine** sprint.

## 语言（强制）

- 所有面向用户的产物（brief、调研、分析、PRD、retro、UI 文案）使用**简体中文**
- 代码、URL、技术标识符可保留英文
- 每阶段 `eval-stage.py` 含中文锚点检查

## Project directory (git repo root)

```
D:/workspace/projects/pm-{slug}/
```

| Link | URL |
|------|-----|
| Pages | `https://ttmens.github.io/pm-{slug}/` |
| GitHub | `https://github.com/ttmens/pm-{slug}` |
| Index | `https://ttmens.github.io/pm-pipeline-index/` |

## Pipeline stages (strict gates)

| Stage | Profile | Artifacts | Skills | Gate |
|-------|---------|-----------|--------|------|
| 0 Brief | User / orchestrator | `00-brief.md` | — | Idea captured |
| 1 Align | `pm-aligner` | `CONTEXT.md`, `decisions.md` | `grill-me`, `grill-with-docs` | No TBD; glossary ≥3 |
| 2 Research | `pm-researcher` | `01-research.md` | Tavily, arxiv | ≥5 URLs; competitor table |
| 3 Analysis | `pm-analyst` | `02-analysis.md`, `architecture/c4-*.md` | `c4-architecture`, `openspec` | C4 L1–L3 + ADR |
| 4 Spec | `pm-planner` | `03b-user-journey.md`, `02b-prototype/`, `03-prd.md` | `user-journey`, `sketch`, `open-design` | journey + prototype |
| 5 MVP | `pm-builder` | `04-mvp/`, `UX-REVIEW.md` | `design-review`, `ux-optimize` chain | P0=0 UX gate |
| 6 Retro | `pm-builder` | `05-retro.md`, `evolution-notes.md` | pipeline-knowledge | evolution section |
| Report | any | `docs/index.html` | `pm-git-publish` | Pages dashboard |

After each stage: `validate-gates.py --write` → `pm-git-publish` (build report → commit → push).

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
    UX-REVIEW.md          # design-review acceptance
    README.md
  05-retro.md
  06-refine-retro.md      # Refine sprint only
  evolution-notes.md
  gates.json
  feedback.jsonl
  RUN.md                  # 中文运行说明（decompose 时生成）
  docs/index.html
```

## Kanban task graph (v3)

```
Parent: "Idea: {title}"
├── pm-aligner:      "Grill 对齐想法" → CONTEXT.md + enriched brief
├── pm-researcher:   "深度调研" (parent: aligner) → 01-research.md
├── pm-analyst:      "方案论证" (parent: research) → 02-analysis.md + openspec/proposal.md
├── pm-planner:      "原型+PRD+OpenSpec" (parent: analyst) → 02b-prototype + 03-prd + openspec/
├── pm-builder:      "MVP 实现" (parent: planner) → 04-mvp/
└── pm-builder:      "Retro+进化" (parent: builder/MVP) → 05-retro.md
```

Worker assignees: `pm-aligner`, `pm-researcher`, `pm-analyst`, `pm-planner`, `pm-builder` (MVP + retro).  
`pm-orchestrator` 仅负责分解与父任务汇总，**不**写 retro 文件。

## Validation scripts

```powershell
python D:\workspace\pipelines\pm-idea-to-mvp\scripts\validate-gates.py --run D:\workspace\projects\pm-{slug} --write
python D:\workspace\pipelines\pm-idea-to-mvp\scripts\build-run-report.py --run D:\workspace\projects\pm-{slug} --slug {slug}
```

Gate failure → `kanban_block` + Feishu notify; do not promote next stage.

## 人工检查点（Human-in-the-loop）

默认在 **align** 与 **spec** 两处暂停；飞书通知含任务 ID 与 `unblock` 命令（`stage-complete` 在 git push **之前**发送，push 失败不吞通知）。

### 两段式协议

| 场景 | 判定 | 动作 |
|------|------|------|
| **首次运行** | `kanban_show` **无** unblock 评论 | 产物就绪 → `stage-complete --task-id <本任务ID>` → `kanban_block` → **不要** `kanban_complete` |
| **Resume** | `kanban_show` **有** unblock 评论且任务为 `ready` | 验证 gates 仍 pass → `kanban_complete`（可选 `stage-complete --skip-git`）→ **禁止**再次 `kanban_block` |

| 阶段 | block 理由 |
|------|-----------|
| **align** | `等待用户确认 align 产物` |
| **spec** | `等待用户确认 PRD/原型范围` |

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
- `sketch` → `open-design` prototype (static HTML)
- `03-prd.md`: ≤5 user stories, acceptance criteria
- `openspec/tasks.md` + `openspec/specs/` delta specs
- 完成后：见人工检查点两段式协议（首次 block，resume complete）

### MVP (`pm-builder`)

Superpowers chain (mandatory order):

```
plan → ui-ux-pro-max → test-driven-development → opencode → design-review → ux-optimize → requesting-code-review → dogfood
```

- Require `openspec/tasks.md` before coding
- Generate `04-mvp/DESIGN.md` via `ui-ux-pro-max`
- OpenCode:

```bash
opencode run "Implement MVP per openspec/tasks.md and 03-prd.md. Apply 04-mvp/DESIGN.md tokens. ≤3 flows." --workdir D:/workspace/projects/pm-{slug}/04-mvp
```

- Smoke test locally; Pages shows static report (MVP runs on localhost)

### Retro (`pm-builder`)

`05-retro.md` must include（**简体中文**）:

- Stage timing & skill hits/misses
- Assumption validation
- `skill_patch_proposals[]` for pipeline evolution
- Pending items from `feedback.jsonl`

Append distilled lessons to `D:\workspace\pipelines\pm-idea-to-mvp\pipeline-knowledge\`.

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
- On new idea: try `decompose-pm-pipeline.py` first; if missing, fall back to manual kanban creates (see below)
- Kanban comment: `repo:` + `pages:` URLs + `RUN.md` 路径
- 父任务全部子任务 done 后汇总中文摘要
- Feishu 由 `stage-complete.py` → `feishu_notify.py` 自动推送

### Manual decompose fallback（当 `decompose-pm-pipeline.py` 不存在时）

该脚本在 `D:\workspace\pipelines\pm-idea-to-mvp\scripts\` 下可能不存在。此时用 `hermes kanban create` 手动创建，按依赖顺序创建父任务再子任务，用 `--parent` 链接：

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

**Refine-4 迭代超时恢复**：Refine-4（MVP 定向优化）任务 body 含 `plan → ui-ux-pro-max → design-review → ux-optimize → dogfood` 超长链，**极易**在 60 次迭代内无法完成，导致 `timed_out` → `gave_up`。但注意：超时前 agent 写入的代码/文件**通常已持久化**（write_file/patch 是原子操作）。恢复步骤：

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

## Feishu trigger

```
/goal 产品想法：{描述}

按 pm-idea-to-mvp v4 执行。项目目录：D:/workspace/projects/pm-{slug}/
含 C4 架构、用户旅程、UX 验收与自进化 Retro。完成后发 GitHub Pages 链接。
```
