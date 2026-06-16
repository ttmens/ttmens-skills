---
name: pm-idea-to-mvp
description: "Super-dev pipeline v7.1: Loop Engineering + enforced governance + agent behavior code + Hermes UX (Feishu grill, trigger routing, brownfield/resume). brief → align → research → analysis → spec → mvp(inner-loop) → ship → operate → grow → retro."
version: 7.2.0
author: ttmens
license: MIT
platforms: [cursor, hermes, opencode, linux, macos, windows]
metadata:
  hermes:
    tags: [super-developer, pipeline, kanban, loop-engineering, goal-primitives, runtime-verification, on-the-loop, github, pages, openspec, ship, ops, grow, browser-verification, rollback, brownfield-audit]
    curator:
      skip: true
    trigger_conditions:
      - "优化"
      - "重构"
      - "E2E"
      - "端到端"
      - "深入分析"
      - "改进"
      - "审查"
      - "审计"
      - "refine"
      - "brownfield"
      - "部署"
      - "上线"
      - "发布"
      - "回退"
      - "回滚"
    related_skills:
      - grill-me
      - grill-with-docs
      - docs-hygiene
      - pm-create-prd
      - pm-opportunity-solution-tree
      - c4-architecture
      - openspec
      - user-journey
      - open-design
      - ui-ux-pro-max
      - prd-red-team-panel
      - ui-acceptance-review
      - subagent-driven-development
      - kw-deploy-checklist
      - pm-shipping-artifacts
      - pm-gtm-strategy
      - pm-git-publish
      - dogfood
      - test-driven-development
      - writing-plans
      - requesting-code-review
---

# Super Developer Pipeline v7.1 (pm-idea-to-mvp)

**唯一主流水线**（live 入口 = 本目录 `pipelines/pm-idea-to-mvp/`；历史快照见 `archive/v6.1.0/`，勿作运行入口）。覆盖 PM、工程、运维、运营全链路。v7.1 融合 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的行为准则体系：6 条不可协商准则 + 每阶段反合理化表格 + 5 轴 Code Review + 浏览器端到端验证 + 回退决策树。

> **设计哲学**：采用 Martin Fowler 的 **双循环框架**（Dual-Loop Framework）——
> - **Why Loop**（战略循环）：持续验证产品方向是否正确（align → research → analysis → retro 反馈）
> - **How Loop**（执行循环）：快速迭代实现路径（spec → MVP inner-loop → ship → operate 反馈）
>
> 两个循环通过 `feedback.jsonl` 与 `evolution-notes.md` 互相驱动，形成自进化闭环。

## 快速判断：何时使用本技能？

**强制规则**：当用户提到以下关键词时，**必须**先调用 `skill_view(name='pm-idea-to-mvp')` 加载技能。

| 用户说 | 场景 | decompose | 说明 |
|--------|------|-----------|------|
| "做一个新产品" / `/goal 产品想法` | greenfield | `--scenario greenfield` | 飞书 grill 1–2 问 → 12 子任务 |
| "优化现有项目" / "继续优化" | brownfield | `--scenario brownfield` | 棕地审计 + 精简子图 |
| "部署" / "修 bug" | optimize | `--scenario optimize` | ship + operate |
| "UX 复审" / "refine" | refine | `--scenario refine` | 深研 + spec + mvp iter |

**触发关键词列表**（出现在用户消息中即触发）：
- 优化、重构、E2E、端到端、深入分析、改进、审查、审计
- refine、brownfield、部署、上线、发布、回退、回滚

环境变量（替代硬编码路径）：

- `{PROJECT_ROOT}` — pm-{slug} 仓库根目录
- `{SKILLS_ROOT}` — ttmens-skills 仓库根目录（或 `~/.cursor/skills` 安装根）

## 语言（强制）

- 所有面向用户的产物（brief、调研、分析、PRD、retro、UI 文案、PROGRESS.md）使用**简体中文**
- 代码、URL、技术标识符、goal YAML 键名可保留英文
- 每阶段 `eval-stage.py` 含中文锚点检查
- `goal-check.py` 输出双语（中文描述 + 英文状态码）

## 6 核心原语映射（Loop Engineering Primitives）

| 原语 | 本流水线对应 | 说明 |
|------|-------------|------|
| **Automations** | `validate-gates.py --runtime`, `goal-check.py`, `progress-tracker.py`, `stage-complete.py` | 门禁 + 目标验证 + 进度追踪全自动化 |
| **Worktrees** | `{PROJECT_ROOT}/04-mvp/` 独立目录 + git worktree（可选） | MVP 实现隔离于项目仓库子目录 |
| **Skills** | 37 core (17 native + 20 borrowed) + optional profiles（见 stages 表） | 每阶段绑定专用 skill |
| **Connectors** | Feishu (`stage-complete.py` → `feishu_notify.py`), GitHub Pages (`pm-git-publish`), Kanban (`hermes kanban`) | 外部系统对接 |
| **Sub-agents** | Profile-based dispatch: `pm-aligner`, `pm-researcher`, `pm-analyst`, `pm-planner`, `pm-builder` | 按阶段分派专业 agent |
| **Memory** | `CONTEXT.md`, `feedback.jsonl`, `pipeline-knowledge/`, `PROGRESS.md`, `evolution-notes.md` | 跨会话持久化记忆 |

## Project directory (git repo root)

```
{PROJECT_ROOT}/   # e.g. D:/workspace/projects/pm-{slug}/
```

| Link | URL |
|------|-----|
| Pages | `https://ttmens.github.io/pm-{slug}/` |
| GitHub | `https://github.com/ttmens/pm-{slug}` |
| Index | `https://ttmens.github.io/pm-pipeline-index/` |

## Pipeline stages (strict gates + runtime verification)

| Stage | Profile | Artifacts | Native skills | Borrowed skills | Gate (artifact + runtime) |
|-------|---------|-----------|---------------|-----------------|--------------------------|
| 0 brief | User | `00-brief.md` | — | — | Idea captured |
| 1 align | `pm-aligner` | `CONTEXT.md`, `decisions.md`, `debates/align-*.md` | `grill-me`, `grill-with-docs` (含 G1 辩论协议) | `pm-identify-assumptions-new` | **G1**: CONTEXT + 假设风险 + `debate_resolved` |
| 2 research | `pm-researcher` | `01-research.md` | — | `pm-opportunity-solution-tree`, `pm-competitor-analysis`, `pm-market-sizing` | ≥5 URLs + 来源可访问（HTTP 200 抽检） |
| 3 analysis | `pm-analyst` | `02-analysis.md`, `architecture/c4-*.md`, `debates/analysis-*.md` | `c4-architecture` (含 PK), `openspec`, `docs-hygiene` | `pm-product-strategy`, `kw-system-design` | C4 L1–L3 + PK 辩论 synthesis |
| 4 spec | `pm-planner` | `03b-user-journey.md`, `02b-prototype/`, `03-prd.md`, `debates/spec-*.md` | `user-journey`, `open-design`, `ui-ux-pro-max`, `prd-red-team-panel` | `pm-create-prd`, `pm-user-stories` | **G2**: PRD + 原型 + `debate_resolved` |

**spec UI 选型**：需行业配色 / 多 stack CSV 推理 → 安装 `--profile ui-pro-max-full`（slim `ui-ux-pro-max` 仍为默认）。
| 5 mvp | `pm-builder` | `04-mvp/`, `UX-REVIEW.md` | `writing-plans`, `subagent-driven-development`, `test-driven-development`, `ui-acceptance-review`, `requesting-code-review`, `dogfood` | `kw-testing-strategy` | **G3**: 测试 + lint + build + health 200 |
| 6 ship | `pm-shipper` | `RUNBOOK.md`, `docs/ui-acceptance-report.md` | `ui-acceptance-review` (full), `docs-hygiene` | `pm-shipping-artifacts`, `pm-intended-vs-implemented`, `kw-deploy-checklist`, `pm-security-audit-static` | Deploy ready + RUNBOOK 可执行 |
| 7 operate | `pm-operator` | ops notes | — | `kw-incident-response`, `kw-runbook`, `pm-sql-queries` | — |
| 8 grow | `pm-growth` | `06-growth.md` | — | `pm-north-star-metric`, `pm-gtm-strategy` | — |
| 9 retro | `pm-builder` | `05-retro.md`, `evolution-notes.md`, `harness-improvements.md` | `pm-git-publish` | `pm-retro`, `pm-release-notes` | evolution proposals 已分类 |
| report | any | `docs/index.html` | `pm-git-publish` | — | Pages dashboard |

**G1/G2/G3**：align≈G1（含假设辩论）、spec≈G2（含红队面板，需 `--profile debate` 安装 phuryn 依赖）、mvp/ship≈G3。

### 棕地 / 场景

| Scenario | 入口 | 说明 |
|----------|------|------|
| `greenfield` | brief | 默认 0→1 |
| `brownfield` | analysis | 跳过 brief/align/research；见 `references/brownfield-audit.md` + `scenarios.yaml` |
| `refine` | mvp | 深化循环；`refine-decompose.py` |
| `optimize` | analysis | 同 brownfield，无 bootstrap 强制 |

棕地项目阶段开始前运行 `docs-hygiene`。`decompose-pm-pipeline.py --scenario brownfield` 生成 skip map。

**v7.1 新增：强制棕地审计**（不可跳过）：

当用户说"优化"、"重构"、"E2E"、"深入分析"时，**必须**先执行棕地审计（见 `references/brownfield-audit.md`）：

1. **Step 0: 构建验证** — `pnpm build` 必须成功（阻塞性检查）
2. **Step 0.5: 浏览器现状记录** — 截图 + 控制台错误记录
3. **Step 1-6: 完整审计流程** — 见 `references/brownfield-audit.md`

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "直接开始优化" | ❌ 没有审计 = 不知道问题在哪。可能优化了错误的方向。 |
| "审计太耗时" | ❌ 审计只需 15-20 分钟，但可以节省 2 小时的无效工作。 |
| "用户急着要结果" | ❌ 没有审计的结果可能是错误的结果，返工成本更高。 |

v6 变化：每个 Gate 现在包含 **artifact 存在性** + **runtime 验证** 两层检查，由 `validate-gates.py --runtime` 和 `goal-check.py` 协同执行。

### v6.2 变化：Enforced Governance（实战驱动）

基于 pm-knowledge-platform 项目复盘发现的 7 个核心问题，v6.2 引入以下强制执行机制：

| 优化项 | 问题来源 | 解决方案 | 实现位置 |
|--------|---------|---------|---------|
| **强制 runtime 验证** | 任务标记完成但未实际验证 | mvp/ship 阶段自动运行 `--runtime` + `--goal` | `stage-complete.py` MANDATORY_RUNTIME_STAGES |
| **跨文档一致性** | decisions.md 写 PostgreSQL，实际用 SQLite | `check_docs_ssot.py` 新增 tech-stack-conflict 检测 | `scripts/check_docs_ssot.py` |
| **G1/G2 辩论门禁** | Align/Spec 阶段跳过辩论 | `validate-gates.py` 检查 `debates/` 目录 + `debate_resolved` 标记 | `validate-gates.py` debate_required |
| **内循环前置检查** | MVP 内循环缺少 goals/harness 配置 | `inner-loop-driver.py` 启动前验证 prerequisites | `inner-loop-driver.py` check_prerequisites |
| **Retro 量化要求** | Retro 内容空洞，缺乏数据 | `required_sections` 检查量化指标 + 迭代分析 | `validate-gates.py` required_sections |
| **RUNBOOK 章节强制** | Ship 阶段 RUNBOOK 缺回滚/监控 | 检查部署步骤、回滚方案、监控指标三个必需章节 | `validate-gates.py` ship.required_sections |
| **Operate/Grow 产物** | 这两个阶段完全跳过 | operate 要求 `07-ops-notes.md`，grow 提升 min_lines 到 30 | `validate-gates.py` STAGE_FILES |

**最低行数提升**（防止敷衍产物）：

| 阶段 | v6.0 | v6.2 | 原因 |
|------|------|------|------|
| brief | 5 | 20 | 防止一句话 brief |
| align (CONTEXT.md) | 10 | 50 | pm-knowledge-platform 仅 69 行，深度不足 |
| research | 20 | 50 | 确保充分调研 |
| analysis | 30 | 100 | 确保方案论证深入 |
| spec | 20 | 50 | 确保 PRD 完整 |
| ship (RUNBOOK) | 10 | 50 | 确保部署文档可用 |
| retro | 15 | 50 | 确保复盘有数据支撑 |

**新增自动化检查**（`stage-complete.py` 自动触发，无需手动传参）：

```python
MANDATORY_RUNTIME_STAGES = ["mvp", "ship"]      # 自动 --runtime
MANDATORY_GOAL_STAGES = ["mvp", "ship", "retro"] # 自动 --goal
MANDATORY_DOCS_HYGIENE_STAGES = ["align", "analysis", "spec", "mvp", "ship"]  # 自动 docs-hygiene
```

可选：`docs/workflow_state.yaml`（来自 greenfield-light profile）与 `gates.json` 并存，用于非 Kanban 断点续跑。

### v7.0 变化：Agent 行为准则融合（agent-skills 驱动）

融合 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)（56K+ stars）的核心模式，解决 v6.2 遗留的"走得好不好"问题：

| 优化项 | 问题来源 | 解决方案 | 实现位置 |
|--------|---------|---------|---------|
| **6 条不可协商行为准则** | agent 跳过假设/验证/范围纪律 | 共享行为约束文件，所有 profile 引用 | `references/agent-behavior-code.md` |
| **每阶段反合理化表格** | agent 合理化跳过关键步骤 | 每个 stage card 新增"常见借口→反驳"表格 | `references/hermes-stage-cards/*.md` |
| **每阶段失败模式清单** | 同类错误反复出现 | 结构化失败模式 + 后果 + 预防 | `references/hermes-stage-cards/*.md` |
| **5 轴 Code Review** | review 缺乏结构化维度 | 正确性/可读性/架构/安全/性能 + 严重性标签 | `requesting-code-review` v3.0 |
| **变更规模约束** | 单次变更过大无法审查 | ~100行Good/~300行Acceptable/~1000行拆分 | `agent-behavior-code.md` + `requesting-code-review` |
| **路由器决策树** | orchestrator 只做分发不做路由 | 任务特征→技能推荐决策树 | `hermes-stage-cards/orchestrator.md` |

**与 v6.2 的关系**：v7.0 不替代 v6.2 的 Enforced Governance（门禁/runtime 验证），而是在其上层叠加行为标准。v6.2 解决"走不走"，v7.0 解决"走得好不好"。

After each stage (Hermes): `validate-gates.py --runtime --write` → `goal-check.py --stage <current>` → `pm-git-publish` when available.

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
  06-growth.md              # 增长策略（Stage 8）
  07-ops-notes.md           # 运维笔记（Stage 7）
  06-refine-retro.md      # Refine sprint only
  harness-improvements.md # v6: Retro 产出的 harness 改进提案
  evolution-notes.md
  gates.json              # copy from pipelines/pm-idea-to-mvp/assets/gates.template.json
  harness-rules.yaml      # v6: 风险分级 + 自动化规则（从 harness-rules.template.yaml 复制）
  PROGRESS.md             # v6: 任务级进度追踪（由 progress-tracker.py 维护）
  goals/                  # v6: 每阶段目标定义
    align.yaml
    research.yaml
    analysis.yaml
    spec.yaml
    mvp.yaml
    ship.yaml
    retro.yaml
  debates/                  # v6.1: align / analysis / spec debate artifacts
    align-synthesis.md
    analysis-synthesis.md
    spec-synthesis.md
  docs/workflow_state.yaml  # optional, greenfield/brownfield resume
  feedback.jsonl
  06-growth.md
  RUNBOOK.md
  RUN.md                  # 中文运行说明（decompose 时生成）
  docs/index.html
```

## Inner Loop Protocol（v6 核心，v7.1 强化）

MVP 阶段（Stage 5）不再是线性链，而是**递归内循环**：

```
┌─────────────────────────────────────────────────┐
│  MVP Inner Loop (max 3 iterations)              │
│                                                 │
│  Plan → Code → Test → Observe                   │
│   ↑                      │                      │
│   └── adjust ←── FAIL ←──┘                      │
│          PASS → exit loop → Gate G3              │
└─────────────────────────────────────────────────┘
```

### v7.1 新增：入口检查（必须全部通过才能进入内循环）

| # | 检查项 | 检查命令 | 通过标准 | 失败处理 |
|---|--------|---------|---------|---------|
| 1 | `openspec/tasks.md` 存在 | `test -f openspec/tasks.md` | 文件存在且 > 100 字节 | 阻塞，先生成 tasks.md |
| 2 | `goals/mvp.yaml` 存在 | `test -f goals/mvp.yaml` | 文件存在且定义了 runtime goals | 阻塞，先生成 goals |
| 3 | `harness-rules.yaml` 存在 | `test -f harness-rules.yaml` | 文件存在且定义了测试/lint/build 命令 | 阻塞，先生成 harness-rules |
| 4 | `04-mvp/DESIGN.md` 存在 | `test -f 04-mvp/DESIGN.md` | 文件存在（由 `ui-ux-pro-max` 生成） | 阻塞，先运行 ui-ux-pro-max |
| 5 | 项目可构建 | `pnpm build` | exit_code == 0 | 阻塞，先修复构建错误 |

**入口检查命令**：

```bash
# 一键检查所有入口条件
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/inner-loop-driver.py \
  --project-root {PROJECT_ROOT} \
  check_prerequisites
```

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "直接写代码，后面再补 tasks.md" | ❌ 没有 tasks.md = 没有计划 = 盲目编码。内循环的核心是先计划再执行。 |
| "goals 不重要" | ❌ goals 是验证标准。没有 goals = 无法判断 PASS/FAIL = 内循环失效。 |
| "harness-rules 太麻烦" | ❌ harness-rules 定义了测试/lint/build 命令。没有它 = 无法自动化验证。 |
| "DESIGN.md 可以后面再写" | ❌ DESIGN.md 定义了设计 token。没有它 = UI 不一致 = 返工。 |
| "构建错误不重要，先写功能" | ❌ 构建失败 = 无法部署 = 无法验证。构建错误是阻塞性问题。 |

### 循环步骤

| Step | 动作 | 信号来源 |
|------|------|---------|
| **Plan** | 从 `openspec/tasks.md` 提取本轮目标子集；生成 `phase-plan.md` | `writing-plans` skill |
| **Code** | 实现代码（subagent 或 opencode） | `subagent-driven-development` / `opencode run` |
| **Test** | 运行测试套件 + lint + build | `test-driven-development` + `harness-rules.yaml` 中定义的命令 |
| **Observe** | 收集运行时信号：test exit code、lint warnings、build output、health endpoint | `goal-check.py --runtime` |
| **Adjust** | 分析失败原因，调整 plan（仅当 Observe 判定 FAIL） | agent 推理 + `feedback.jsonl` 记录 |

### 循环终止条件

- **PASS**：所有 `goals/mvp.yaml` 中定义的 runtime goals 满足 → 退出循环，进入 Gate G3
- **FAIL after 3 iterations**：记录失败原因到 `05-retro.md`，标记 `mvp: partial`，通知人类介入
- **HARNESS ESCALATION**：如果失败原因是 harness 配置问题（如测试命令错误），写入 `harness-improvements.md` 并暂停

### 循环与 Harness 交互

```yaml
# harness-rules.yaml 中的 inner-loop 配置
inner_loop:
  max_iterations: 3
  test_command: "cd 04-mvp && python -m pytest tests/ -v"
  lint_command: "cd 04-mvp && ruff check ."
  build_command: "cd 04-mvp && npm run build"  # or python setup.py build
  health_endpoint: "http://localhost:8080/health"
  signals:
    - type: test_exit_code
      pass: 0
    - type: lint_warnings
      pass_threshold: 0
    - type: build_exit_code
      pass: 0
    - type: http_status
      url: "http://localhost:8080/health"
      pass: 200
```

## Harness Rules（风险分级自动化）

v6 用 `harness-rules.yaml` 取代固定的 3 个人工检查点，实现**基于风险的自动化**（On-the-Loop 模式）：

### 风险等级定义

| 等级 | 场景示例 | 行为 | 人类介入 |
|------|---------|------|---------|
| **Low** | research 补充、code refactor、文档修正 | agent 自主决策，harness 验证结果 | 无（异步通知） |
| **Medium** | 技术选型、架构变更、PRD 范围调整 | agent 提出 ADR，harness 检查一致性，异步通知人类 | 异步通知（不阻塞） |
| **High** | 部署、数据迁移、安全敏感操作 | 保留人工检查点 | 阻塞等待确认 |

### harness-rules.yaml 结构

```yaml
# harness-rules.yaml — 从 harness-rules.template.yaml 复制并定制
version: "6.0"
project: pm-{slug}

risk_rules:
  research_addition:
    level: low
    auto_apply: true
    verify: "goal-check.py --stage research"

  architecture_change:
    level: medium
    auto_apply: false
    require_adr: true
    notify: feishu_async
    verify: "goal-check.py --stage analysis --check adr-consistency"

  prd_scope_change:
    level: medium
    auto_apply: false
    require_adr: true
    notify: feishu_async
    verify: "goal-check.py --stage spec --check story-count"

  deploy:
    level: high
    auto_apply: false
    require_human: true
    block_reason: "等待用户确认部署"
    verify: "validate-gates.py --runtime --stage ship"

  data_migration:
    level: high
    auto_apply: false
    require_human: true
    block_reason: "等待用户确认数据迁移"

gates:
  G1: { stage: align, risk: medium, default_block: true }
  G2: { stage: spec, risk: medium, default_block: true }
  G3: { stage: mvp, risk: low, default_block: false, runtime_verify: true }

inner_loop:
  max_iterations: 3
  # ... (see Inner Loop Protocol section)
```

### 默认行为

- **G1 (align)** 和 **G2 (spec)** 默认保留为 medium risk + block（用户首次确认）
- **G3 (mvp)** 降级为 low risk + runtime verify（内循环自动验证，无需人工阻塞）
- **Deploy** 始终为 high risk + require_human（唯一硬检查点）

## Goal Primitives（目标原语）

每个阶段定义**可验证目标**（verifiable goals），取代单纯的"文件存在"检查。目标存储在 `goals/{stage}.yaml`，由 `goal-check.py` 执行验证。

### 目标格式

```yaml
# goals/mvp.yaml
stage: mvp
goals:
  - id: mvp-tests-pass
    description: "所有单元测试通过"
    check_type: runtime
    command: "cd 04-mvp && python -m pytest tests/ -v --tb=short"
    pass_condition: "exit_code == 0"
    weight: critical

  - id: mvp-lint-clean
    description: "代码 lint 无错误"
    check_type: runtime
    command: "cd 04-mvp && ruff check . --select E,F"
    pass_condition: "exit_code == 0"
    weight: required

  - id: mvp-build-success
    description: "项目构建成功"
    check_type: runtime
    command: "cd 04-mvp && npm run build"
    pass_condition: "exit_code == 0"
    weight: required

  - id: mvp-health-ok
    description: "健康检查端点返回 200"
    check_type: runtime
    command: "curl -sf http://localhost:8080/health"
    pass_condition: "exit_code == 0"
    weight: required

  - id: mvp-readme-exists
    description: "README.md 存在且非空"
    check_type: artifact
    path: "04-mvp/README.md"
    pass_condition: "exists && size > 100"
    weight: required

  - id: mvp-ux-review
    description: "UX 验收报告已生成"
    check_type: artifact
    path: "04-mvp/UX-REVIEW.md"
    pass_condition: "exists && contains('PASS')"
    weight: required
```

### 目标验证命令

```bash
# 验证单个阶段的所有目标
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage mvp --project-root {PROJECT_ROOT}

# 仅验证 runtime 目标（用于内循环）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage mvp --runtime-only --project-root {PROJECT_ROOT}

# 验证特定目标
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage mvp --goal mvp-tests-pass --project-root {PROJECT_ROOT}
```

### 目标权重

| Weight | 含义 | Gate 行为 |
|--------|------|----------|
| `critical` | 必须通过，否则整个 stage fail | 阻塞下一阶段 |
| `required` | 应当通过，失败产生 warning | 可人工 override |
| `recommended` | 建议通过，失败仅记录 | 不阻塞 |

## Progress Tracking（细粒度进度追踪，v7.1 强化）

v6 引入 `PROGRESS.md` 作为项目级任务追踪文件，取代仅靠 Kanban 状态的方式。

### v7.1 新增：强制更新协议（不可跳过）

**每个阶段完成后必须**：

1. 运行 `progress-tracker.py --project-root {PROJECT_ROOT} update --task <id> --status done`
2. 运行 `progress-tracker.py --project-root {PROJECT_ROOT} show` 确认更新
3. 提交 PROGRESS.md 到 git：`git add PROGRESS.md && git commit -m "chore: update progress"`

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "Kanban 已经记录了状态" | ❌ Kanban 是粗粒度（todo/ready/done），PROGRESS.md 是细粒度（子步骤、阻塞、内循环历史）。两者互补，不是替代。 |
| "更新 PROGRESS.md 太麻烦" | ❌ 使用 `progress-tracker.py` 自动化，不需要手动编辑。一条命令完成。 |
| "用户不关心进度" | ❌ 用户关心。PROGRESS.md 是用户了解项目状态的窗口。没有它 = 用户需要反复询问。 |
| "下次再更新" | ❌ "下次" = "永远不"。立即更新，否则你会忘记做了什么。 |
| "PROGRESS.md 不重要" | ❌ PROGRESS.md 是跨会话恢复的关键。没有它 = 下次会话需要重新理解项目状态。 |

**用户信号**（看到这些信号说明你跳过了 PROGRESS.md 更新）：
- "现在做到哪了？"
- "上次做了什么？"
- "为什么又要重新做？"

### PROGRESS.md 格式

```markdown
# 项目进度：{slug}

最后更新：2026-06-12T14:30:00+08:00（by progress-tracker.py）

## 阶段状态

| Stage | Status | Started | Completed | Notes |
|-------|--------|---------|-----------|-------|
| align | ✅ done | 06-12 10:00 | 06-12 10:15 | CONTEXT.md 已确认 |
| research | ✅ done | 06-12 10:15 | 06-12 10:45 | 7 sources, confidence: high |
| analysis | 🔄 running | 06-12 10:45 | — | C4 L2 进行中 |
| spec | ⏳ todo | — | — | — |
| mvp | ⏳ todo | — | — | — |
| ship | ⏳ todo | — | — | — |
| retro | ⏳ todo | — | — | — |

## 当前任务

- **任务**: 完成 C4 Container 图
- **子步骤**: [x] 识别外部系统 [x] 定义容器 [ ] 标注协议 [ ] ADR 映射
- **阻塞**: 无
- **内循环进度**: N/A（尚未进入 MVP）

## 内循环历史（MVP 阶段）

| Iteration | Plan | Code | Test | Observe | Result |
|-----------|------|------|------|---------|--------|
| — | — | — | — | — | — |
```

### 进度追踪命令

```bash
# 初始化 PROGRESS.md（从 openspec/tasks.md 提取任务）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} init

# 更新任务状态
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} update --task 3 --status done

# 显示当前进度摘要
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} show

# 获取恢复点（最后未完成的任务）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} resume
```

### Session Resume 协议

每次 Hermes session 启动时：
1. 读取 `{PROJECT_ROOT}/PROGRESS.md`
2. 检查最后状态，确定恢复点
3. 如果 MVP inner loop 中断，从最后一次 iteration 的 Observe 结果继续

## Kanban task graph (v6)

```
Parent: "Idea: {title}"
├── pm-aligner:      "Grill 对齐想法" → CONTEXT.md + enriched brief
├── pm-researcher:   "深度调研" (parent: aligner) → 01-research.md
├── pm-analyst:      "方案论证" (parent: research) → 02-analysis.md + openspec/proposal.md
├── pm-planner:      "原型+PRD+OpenSpec" (parent: analyst) → 02b-prototype + 03-prd + openspec/
├── pm-builder:      "MVP 实现（内循环）" (parent: planner) → 04-mvp/
│   ├── subtask: "MVP Plan" → phase-plan.md
│   ├── subtask: "MVP Code + Test (iter 1)" → 代码 + 测试结果
│   ├── subtask: "MVP Code + Test (iter 2)" → 修复 + 测试结果（if needed）
│   └── subtask: "MVP Code + Test (iter 3)" → 最终修复（if needed）
├── pm-shipper:      "Ship 准备" (parent: builder/MVP) → RUNBOOK.md
└── pm-builder:      "Retro+进化" (parent: shipper) → 05-retro.md + harness-improvements.md
```

Worker assignees: `pm-aligner`, `pm-researcher`, `pm-analyst`, `pm-planner`, `pm-builder` (MVP + retro), `pm-shipper`。
`pm-orchestrator` 仅负责分解与父任务汇总，**不**写 retro 文件。

v6 变化：MVP 阶段拆分为 Plan + 最多 3 次 Code/Test 迭代子任务；新增 `pm-shipper` 独立角色；Retro 增加 harness 改进输出。

## Validation scripts

```bash
# 门禁验证（含 runtime 检查）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/validate-gates.py --runtime --run {PROJECT_ROOT} --write

# 目标验证
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/goal-check.py --stage <current> --project-root {PROJECT_ROOT}

# 进度追踪（子命令模式）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} init    # 初始化
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} update --task <id> --status <status>  # 更新任务
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} show    # 显示进度
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/progress-tracker.py --project-root {PROJECT_ROOT} resume  # 恢复点

# 阶段完成（含目标验证）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage <stage> --project-root {PROJECT_ROOT} --verify-goals

# v7.0: 行为准则检查（自动执行，也可手动触发）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py --stage <stage> --project-root {PROJECT_ROOT} --check-behavior

# 全流水线验证（v6.2 新增）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/validate-gates.py --all-stages --run {PROJECT_ROOT} --write

# 消费反馈（v6.2.1 新增，retro 阶段必须运行）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/consume-feedback.py --project-root {PROJECT_ROOT} --write --append-retro

# 项目初始化（v6.2.1 新增）
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/init-project.py --project-root {PROJECT_ROOT} --slug {slug}

# 通用文档检查（位于 SKILLS_ROOT/scripts/ 而非 pipeline scripts/）
python {SKILLS_ROOT}/scripts/check_docs_ssot.py --project-root {PROJECT_ROOT}
python {SKILLS_ROOT}/scripts/ui_acceptance.py --project-root {PROJECT_ROOT} --quick
```

Gate failure → `kanban_block` + Feishu notify; do not promote next stage.
Runtime failure in inner loop → adjust & retry (up to 3 iterations); after 3 failures → human escalation.

## 人工协作（On-the-Loop，v6 升级）

v6 从 **In-the-loop**（固定 3 个检查点）升级为 **On-the-loop**（基于风险分级）：

### 默认检查点

| 场景 | 风险等级 | 行为 | 飞书通知 |
|------|---------|------|---------|
| **Align 完成（G1）** | Medium | block 等待确认 | 同步通知 + unblock 命令 |
| **Spec 完成（G2）** | Medium | block 等待确认 | 同步通知 + unblock 命令 |
| **Deploy（ship 阶段）** | High | block 等待确认 | 同步通知 + unblock 命令 |
| **Research 补充** | Low | agent 自主完成 | 异步通知（不阻塞） |
| **架构调整（ADR）** | Medium | agent 提案 + harness 验证 | 异步通知 |
| **MVP 内循环** | Low | 自动迭代，harness 验证 | 仅失败时通知 |

### 两段式协议（保留用于 Medium/High risk）

| 场景 | 判定 | 动作 |
|------|------|------|
| **首次运行** | `kanban_show` **无** unblock 评论 | 产物就绪 → `stage-complete --task-id <本任务ID>` → `kanban_block` → **不要** `kanban_complete` |
| **Resume** | `kanban_show` **有** unblock 评论且任务为 `ready` | 验证 gates 仍 pass → `kanban_complete`（可选 `stage-complete --skip-git`）→ **禁止**再次 `kanban_block` |

`stage-complete.py` 每阶段向飞书 `FEISHU_HOME_CHANNEL` 推送真实消息；checkpoint 阶段 push 失败仅警告，不阻止 notify。

### 全自主模式（Full Autonomous）

当 `harness-rules.yaml` 中所有 gates 设为 `default_block: false` 时，流水线全自主运行：
- 所有 Low/Medium risk 决策由 agent + harness 自动处理
- 仅 High risk（deploy）保留人工检查点
- 适用于：已验证的技术栈、重复性项目模板、低风险内部工具

## Stage details

### Align (`pm-aligner`)

- `grill-me` if no CONTEXT.md; else `grill-with-docs`
- One question at a time; no code/research/recommendations
- Exit: `goals/align.yaml` 所有目标满足 → `goal-check.py --stage align` PASS
- 完成后：见人工协作（Medium risk → block 等待确认）
- v6 新增：假设风险等级标注（写入 `decisions.md`）

### Research (`pm-researcher`)

- Read `CONTEXT.md` + `00-brief.md`
- Tavily primary; browser fallback
- **必须** `write_file` 落盘 `01-research.md`；禁止仅 `kanban_comment`
- `01-research.md`: competitors, sources with URLs, confidence tags
- v6 新增：URL 可访问性抽检（HTTP 200 check）
- `goal-check.py --stage research` 验证目标
- `stage-complete --stage research` 失败则 block，不得 complete
- 风险等级：Low（补充调研可自主进行）

### Analysis (`pm-analyst`)

- Read `01-research.md` + `CONTEXT.md`
- `02-analysis.md`: ≥3 options, recommendation, risks
- `c4-architecture`: `architecture/c4-*.md`; ADRs map to containers
- Draft `openspec/proposal.md`; `openspec/design.md` links C4
- No implementation code
- v6 新增：ADR 与 C4 container 一致性检查（`goal-check.py --check adr-consistency`）
- 风险等级：Medium（架构变更需 ADR + 异步通知）

### Spec (`pm-planner`)

- `user-journey` → `03b-user-journey.md` first
- `open-design` prototype (static HTML; optional sketch variants inside skill)
- `03-prd.md`: ≤5 user stories, acceptance criteria
- `openspec/tasks.md` + `openspec/specs/` delta specs
- 完成后：见人工协作（Medium risk → block 等待确认）
- v6 新增：原型 HTML 可渲染检查、user story 数量验证

### MVP (`pm-builder`) — Inner Loop

MVP 使用**内循环协议**（见 Inner Loop Protocol 章节），不再线性执行。

MVP skill chain（每次迭代内使用）：

```
writing-plans → ui-ux-pro-max → test-driven-development → subagent-driven-development → ui-acceptance-review (journey) → requesting-code-review → dogfood
```

Hermes 编码可追加 `profiles/hermes-opencode/opencode`（`opencode run`）。

- Require `openspec/tasks.md` before coding
- Generate `04-mvp/DESIGN.md` via `ui-ux-pro-max`
- 内循环执行：
  1. **Plan**: 从 `openspec/tasks.md` 提取子集，生成 `phase-plan.md`
  2. **Code**: OpenCode 或 subagent 实现
  3. **Test**: 运行 `harness-rules.yaml` 中定义的测试/lint/build 命令
  4. **Observe**: `goal-check.py --stage mvp --runtime-only` 收集信号
  5. **判断**: 全部 PASS → 退出循环；FAIL → 分析原因，调整 plan，回到 Step 1（max 3 次）

OpenCode:

```bash
opencode run "Implement MVP per openspec/tasks.md and 03-prd.md. Apply 04-mvp/DESIGN.md tokens. ≤3 flows." --workdir {PROJECT_ROOT}/04-mvp
```

- Smoke test locally; Pages shows static report (MVP runs on localhost)
- 内循环失败 3 次后：写入 `harness-improvements.md`，通知人类介入

#### v7.1 新增：自动化测试集成（强制执行）

**测试要求**（在 `goals/mvp.yaml` 中定义）：

| # | 测试类型 | 命令 | 权重 | 说明 |
|---|---------|------|------|------|
| 1 | 单元测试 | `npm test` | critical | 必须全部通过 |
| 2 | E2E 测试 | `npm run test:e2e` | required | 关键用户流程必须覆盖 |
| 3 | 测试覆盖率 | `npm run test:coverage` | recommended | 目标 ≥ 80% |
| 4 | 代码审查 | `requesting-code-review` skill | required | 5 轴 Code Review |

**测试集成流程**：

1. **Plan 阶段**：在 `phase-plan.md` 中定义本轮测试目标
2. **Code 阶段**：使用 TDD（先写测试，再写代码）
3. **Test 阶段**：运行所有测试命令，收集结果
4. **Observe 阶段**：检查测试通过率、覆盖率、审查报告

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "测试太耗时，先写功能" | ❌ 没有测试的功能 = 未验证的功能。TDD 比后补测试更快。 |
| "覆盖率不重要" | ❌ 覆盖率低 = 未测试路径多 = 潜在 bug 多。80% 是最低标准。 |
| "E2E 测试太慢" | ❌ E2E 测试验证关键用户流程。没有它 = 不知道系统是否可用。 |
| "代码审查不重要" | ❌ 代码审查发现隐藏问题。5 轴审查（正确性/可读性/架构/安全/性能）是质量保证的关键。 |

#### v7.1 新增：AI 辅助代码审查（强制执行）

**5 轴 Code Review**（使用 `requesting-code-review` skill）：

| 轴 | 检查项 | 严重性 | 工具 |
|----|--------|--------|------|
| **正确性** | 逻辑错误、边界条件、空指针 | Critical | 静态分析 + AI 审查 |
| **可读性** | 命名规范、注释、代码结构 | Required | AI 审查 |
| **架构** | 模块划分、依赖关系、设计模式 | Required | AI 审查 |
| **安全** | XSS、CSRF、SQL 注入、敏感信息泄露 | Critical | 静态分析 + AI 审查 |
| **性能** | 算法复杂度、内存泄漏、N+1 查询 | Recommended | 性能分析工具 + AI 审查 |

**代码审查流程**：

1. **运行代码审查**：
   ```bash
   # 使用 requesting-code-review skill
   skill_view(name='requesting-code-review')
   ```

2. **生成代码审查报告**：`04-mvp/CODE-REVIEW.md`

3. **修复 Critical 问题**（阻塞 MVP 完成）

4. **记录 Required/Recommended 问题**到 backlog

**代码审查报告格式**：

```markdown
# 代码审查报告 — {slug}

生成时间：{timestamp}

## 审查摘要

- 总问题数：15
- Critical：2
- Required：8
- Recommended：5

## 问题清单

### Critical

1. **XSS 漏洞** — src/app/query/page.tsx:42
   - 问题：用户输入未清理直接渲染
   - 修复：使用 DOMPurify 清理输入
   - 代码示例：
     ```tsx
     // Before
     <div dangerouslySetInnerHTML={{__html: userInput}} />
     
     // After
     <div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
     ```

### Required

1. **函数过长** — src/lib/api.ts:18-150
   - 问题：函数超过 100 行，难以维护
   - 修复：拆分为多个小函数

### Recommended

1. **魔法数字** — src/app/dashboard/page.tsx:25
   - 问题：使用魔法数字 `86400000`
   - 修复：定义为常量 `const MS_PER_DAY = 86400000`
```

**代码审查失败时的处理**：
- **Critical 问题**：阻塞 MVP 完成，必须修复
- **Required 问题**：记录到 backlog，下个迭代修复
- **Recommended 问题**：记录到 backlog，择机修复

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "代码审查太耗时" | ❌ 代码审查发现隐藏问题。现在花 15 分钟审查，节省未来 1 天 debug。 |
| "AI 审查不可靠" | ❌ AI 审查是辅助工具，不是替代人工。AI 发现 80% 的问题，人工发现 20% 的深层问题。 |
| "我的代码没问题" | ❌ 每个人都认为自己的代码没问题。代码审查是质量保证的标准流程。 |

### Ship (`pm-shipper`) — v6 新增独立阶段

- 生成 `RUNBOOK.md`：部署步骤、回滚方案、监控指标
- `ui-acceptance-review` (full mode)：完整 UX 验收
- `docs-hygiene`：文档一致性检查
- Deploy 为 High risk → **必须**人工确认
- `goal-check.py --stage ship` 验证 RUNBOOK 可执行性

#### v7.1 新增：强制浏览器端到端验证（不可跳过）

**工具 SSOT**：[`references/browser-tools-ssot.md`](references/browser-tools-ssot.md) — Cursor / Hermes 工具名映射，勿硬编码单一平台 API。

**为什么**：curl 200 不代表 CSS 加载、JS 执行、登录流程正常。常见陷阱：
- standalone 模式漏拷静态文件（CSS 404 但 HTML 200）
- 中间件 auth 无限重定向
- API 代理路径错误
- React hydration 失败

**验证清单**（必须逐项完成，截图保存证据）：

| # | 验证项 | 工具 | 通过标准 | 证据 |
|---|--------|------|---------|------|
| 1 | 登录页渲染 | `browser_navigate` | 样式正常（按钮有背景色、布局正确） | 截图 |
| 2 | 登录流程 | `browser_type` + `browser_click` | 跳转到首页（非停留在登录页） | URL 变化 |
| 3 | 首页渲染 | `browser_snapshot` | 侧边栏、统计卡片、快捷入口正常 | 快照 |
| 4 | 核心页面 | `browser_click` 2-3 个页面 | 无白屏、无 JS 错误 | 快照 |
| 5 | 认证状态 | `browser_console` | `localStorage.getItem('token')` 存在 | 控制台输出 |
| 6 | API 响应 | `browser_console` fetch | 关键 API 返回正确格式 | 响应 JSON |

**验证失败时的处理**：
1. 截图保存证据
2. 记录失败原因到 `feedback.jsonl`
3. 进入修复循环（最多 3 次）
4. 3 次失败后，通知人类介入或回退到稳定版本

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "curl 返回 200 了应该没问题" | ❌ 200 只证明服务器在响应，不证明前端可用。必须亲眼看到页面。 |
| "PM2 状态是 online" | ❌ 进程在线不代表应用可用。CSS 可能 404，JS 可能报错。 |
| "本地测试没问题" | ❌ 本地 ≠ 生产。网络、代理、环境变量可能不同。 |
| "用户没报告问题" | ❌ 用户可能还没发现。主动验证比被动修复成本低 10x。 |
| "时间紧迫，先上线再说" | ❌ 上线后发现问题，修复成本更高。现在花 5 分钟验证，节省未来 2 小时修复。 |

**用户信号**（看到这些信号说明你跳过了浏览器验证）：
- "我登陆看到样式全部没了"
- "页面一直转圈"
- "点击没反应"
- "你自己检测好 确保最终可用"

#### v7.1 新增：性能基准测试（推荐执行）

**性能指标**（在 `goals/ship.yaml` 中定义）：

| # | 指标 | 目标 | 工具 | 权重 |
|---|------|------|------|------|
| 1 | Lighthouse Performance Score | ≥ 90 | `lighthouse` | recommended |
| 2 | LCP (Largest Contentful Paint) | ≤ 2.5s | `lighthouse` | recommended |
| 3 | FID (First Input Delay) | ≤ 100ms | `lighthouse` | recommended |
| 4 | CLS (Cumulative Layout Shift) | ≤ 0.1 | `lighthouse` | recommended |

**性能测试命令**（可执行 SSOT）：

```bash
python {SKILLS_ROOT}/scripts/lighthouse_check.py --url {DEPLOY_URL} --min-performance 90 --project-root {PROJECT_ROOT}
# 或从 gates.json / harness 读取 URL：
python {SKILLS_ROOT}/scripts/lighthouse_check.py --project-root {PROJECT_ROOT}
```

输出：`docs/lighthouse-report.json`；摘要可追加到 `docs/ui-acceptance-report.md`。无 Node/npx 时 **warning 非阻塞**（与 recommended 权重一致）。

```bash
# 手动 Lighthouse（fallback）
lighthouse {DEPLOY_URL} --output=json --output-path=./docs/lighthouse-report.json
```

**性能优化建议**：
- 图片优化：使用 WebP 格式，懒加载
- 代码分割：使用 Next.js 动态导入
- 缓存策略：配置 CDN 缓存头
- 减少第三方脚本

#### v7.1 新增：安全审计集成（强制执行）

**安全审计流程**（使用 `pm-security-audit-static` skill）：

1. **运行安全审计**：
   ```bash
   # 使用 pm-security-audit-static skill
   skill_view(name='pm-security-audit-static')
   ```

2. **检查常见漏洞**：
   - XSS（跨站脚本攻击）
   - CSRF（跨站请求伪造）
   - SQL 注入
   - 敏感信息泄露（API Key、密码）

3. **检查依赖漏洞**：
   ```bash
   # npm 项目
   npm audit
   
   # pnpm 项目
   pnpm audit
   
   # Python 项目
   pip-audit
   ```

4. **生成安全报告**：`docs/security-audit-report.md`

**安全报告格式**：

```markdown
# 安全审计报告 — {slug}

生成时间：{timestamp}

## 漏洞清单

| 严重性 | 漏洞 | 位置 | 修复建议 |
|--------|------|------|---------|
| High | XSS | src/app/query/page.tsx:42 | 使用 DOMPurify 清理输入 |
| Medium | CSRF | src/lib/api.ts:18 | 添加 CSRF token |

## 依赖漏洞

| 包名 | 版本 | 漏洞 | 修复版本 |
|------|------|------|---------|
| lodash | 4.17.20 | Prototype Pollution | 4.17.21 |

## 修复状态

- [ ] High 漏洞已修复
- [ ] Medium 漏洞已修复
- [ ] 依赖已更新
```

**安全审计失败时的处理**：
- **High 漏洞**：阻塞 Ship，必须修复
- **Medium 漏洞**：记录到 backlog，下个迭代修复
- **Low 漏洞**：记录到 backlog，择机修复

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "安全审计太耗时" | ❌ 安全漏洞修复成本远高于预防成本。现在花 10 分钟审计，节省未来 2 天修复。 |
| "内部工具不需要安全" | ❌ 内部工具也有敏感数据。安全无小事。 |
| "用户不关心安全" | ❌ 用户关心数据安全。一个安全漏洞可以毁掉整个产品。 |

### Operate (`pm-operator`)

- ops notes：监控配置、告警规则、SLA 定义
- `kw-incident-response`：故障响应流程
- `kw-runbook`：运维手册补充
- 风险等级：Low（日常运维 agent 自主）

### Grow (`pm-growth`)

- `06-growth.md`：北极星指标、GTM 策略
- `pm-north-star-metric`：指标定义
- `pm-gtm-strategy`：上市策略
- 风险等级：Low（策略调整可自主进行）

### Retro (`pm-builder`)

`05-retro.md` must include（**简体中文**）:

- Stage timing & skill hits/misses
- Assumption validation
- `skill_patch_proposals[]` for pipeline evolution
- Pending items from `feedback.jsonl`
- **v6 新增**：内循环迭代分析（成功/失败原因、harness 配置问题）
- **v6 新增**：`harness-improvements.md` — harness 改进提案

Append distilled lessons to `{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/pipeline-knowledge/` when present.

## Self-Improving Harness（v6 新增）

Retro 阶段现在包含 **harness 自我改进**机制：

### 改进提案分类

| 风险等级 | 示例 | 处理方式 |
|---------|------|---------|
| Low | 调整 lint 阈值、修改测试超时时间 | 自动应用到 `harness-rules.yaml` |
| Medium | 新增 goal、修改 gate 风险等级 | 写入 backlog，等待下次 retro 确认 |
| High | 删除 stage、修改双循环结构 | 写入 backlog，需人工审批 |

### harness-improvements.md 格式

```markdown
# Harness 改进提案 — {slug}

生成时间：2026-06-12T16:00:00+08:00

## 自动应用（Low risk）

- [x] 将 `mvp-lint-clean` 的 `pass_threshold` 从 0 调整为 5（允许少量 warning）
  - 原因：iter 2 中 ruff 报告 3 个 false positive
  - 影响：减少不必要的内循环迭代

## Backlog（Medium risk）

- [ ] 新增 goal `mvp-coverage-80`：测试覆盖率 ≥ 80%
  - 原因：当前无覆盖率检查，可能存在未测试路径
  - 影响：增加测试编写负担，但提高质量

## Backlog（High risk）

- [ ] 将 G2 (spec) 从 Medium 降级为 Low risk
  - 原因：本项目 PRD 变更频率低，无需每次人工确认
  - 影响：减少人工介入，但增加范围蔓延风险
```

### 自动应用流程

1. Retro 阶段生成 `harness-improvements.md`
2. Low risk 提案：`patch` 直接修改 `harness-rules.yaml`，记录到 `evolution-notes.md`
3. Medium/High risk 提案：保留在 backlog，下次 retro 重新评估
4. 连续 3 次 retro 未被采纳的 High risk 提案：标记为 `rejected`，从 backlog 移除

## Self-evolution

| Layer | Path |
|-------|------|
| Run | `05-retro.md`, `evolution-notes.md`, `harness-improvements.md` |
| Pipeline | `pipeline-knowledge/patterns.md`, `anti-patterns.md` |
| Skills | `pm-idea-to-mvp/CHANGELOG.md` (human-approved patches) |
| Harness | `harness-rules.yaml` (auto-applied improvements) |
| External fusion | `references/external-frameworks-analysis.md` (已分析的外部框架 + 融合决策) |

`feedback.jsonl` schema:

```json
{"ts":"ISO8601","source":"feishu","stage":"analysis","signal":"用户否定方案B","proposed_delta":"ADR-003","status":"pending"}
{"ts":"ISO8601","source":"inner-loop","stage":"mvp","signal":"iter 2 test fail: timeout","proposed_delta":"harness: increase test_timeout to 30s","status":"auto-applied"}
```

## Orchestrator (`pm-orchestrator`)

- Route only — no align/research/analyze/plan/code/**retro file I/O**
- On new idea: try `decompose-pm-pipeline.py` first; if missing, fall back to manual kanban creates (see below)
- Kanban comment: `repo:` + `pages:` URLs + `RUN.md` 路径
- 父任务全部子任务 done 后汇总中文摘要
- Feishu 由 `stage-complete.py` → `feishu_notify.py` 自动推送
- v6 新增：内循环子任务监控（检查 iteration 进度，超时告警）

### Manual decompose fallback（当 `decompose-pm-pipeline.py` 不存在时）

该脚本在 `{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/` 下可能不存在。此时用 `hermes kanban create` 手动创建，按依赖顺序创建父任务再子任务，用 `--parent` 链接：

```bash
# T1: Align (no parent, ready)
hermes kanban create "Stage 0+1: 对齐想法" --assignee pm-aligner --body "..."

# T2: Research (parent: T1)
hermes kanban create "Stage 2: 深度调研" --assignee pm-researcher --body "..." --parent <t1_id>

# T3: Analysis (parent: T2)
hermes kanban create "Stage 3: 方案论证" --assignee pm-analyst --body "..." --parent <t2_id>

# T4: Spec (parent: T3)
hermes kanban create "Stage 4: 原型+PRD+OpenSpec" --assignee pm-planner --body "..." --parent <t3_id>

# T5: MVP Inner Loop (parent: T4) — 拆分为子任务
hermes kanban create "Stage 5: MVP 实现（内循环）" --assignee pm-builder --body "..." --parent <t4_id>
hermes kanban create "MVP Plan" --assignee pm-builder --body "..." --parent <t5_id>
hermes kanban create "MVP Code+Test iter 1" --assignee pm-builder --body "..." --parent <t5_id>
# iter 2, iter 3 按需创建

# T6: Ship (parent: T5)
hermes kanban create "Stage 6: Ship 准备" --assignee pm-shipper --body "..." --parent <t5_id>

# T7: Retro (parent: T6)
hermes kanban create "Stage 9: Retro+进化" --assignee pm-builder --body "..." --parent <t6_id>
```

创建完成后无需额外 dispatch — dispatcher 会自动拾取 ready 状态的任务。

## Refine 深化循环（v6 升级）

对已有 `pm-{slug}` 实现不满意时：

```powershell
hermes kanban refine {slug} --reason "实现不满意：需业界深研与优化"
hermes kanban dispatch
```

创建 4 子任务：业界深研 → C4 架构差距 → 旅程/UX 复审 → MVP 优化（使用内循环）。Refine-3 含人工检查点。完成写 `06-refine-retro.md`。

v6 升级：
- Refine-4（MVP 优化）使用**内循环协议**，而非线性链
- Refine retro 增加 harness 改进提案
- 内循环失败时，自动检查是否为 harness 配置问题，写入 `harness-improvements.md`

### Refine 常见陷阱

**重复 Refine**：在 `hermes kanban refine` 之前先运行 `hermes kanban list` 检查是否已有同 slug 的 Refine 任务在跑（status: running/ready/todo，body 含 "Refine"）。如果已有，**不要**再创建一个新的 — 用 `hermes kanban show <root_id>` 跟踪已有 Refine 即可。重复 Refine 会产生两套独立任务树，浪费 token 并导致冲突。

**Refine-4 内循环超时恢复**：Refine-4（MVP 定向优化）使用内循环，max 3 iterations。如果 3 次迭代后仍 FAIL：
1. 检查 `PROGRESS.md` 中内循环历史，定位失败 iteration
2. `hermes kanban log <task_id>` 查看 agent 最后做了什么
3. 分析失败原因：代码问题 or harness 配置问题？
4. 如果是 harness 问题：写入 `harness-improvements.md`，调整 `harness-rules.yaml`
5. 如果是代码问题：用 `read_file`、`terminal(grep)` 确认代码变更已落盘，手动修复
6. 运行 `goal-check.py --stage mvp --runtime-only` 验证修复
7. `hermes kanban complete <task_id>` 完成任务

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

**Refine 前端重构后必须审计所有 API 调用路径**：UI 重构（换设计系统、改配色、重组布局）时，很容易只关注视觉层而忽略功能层的 API 调用。常见陷阱：
- **SSE/流式请求使用原生 `fetch()` 而非 axios**：`fetch()` 不经过 axios 拦截器，不会自动附加 `Authorization` header。重构后这些调用会 401。
- **审计方法**：`grep -rn "fetch(" packages/web/src/` 找出所有原生 fetch 调用，逐一确认是否携带 auth token
- **修复模式**：在 fetch headers 中显式添加 `...(token ? { 'Authorization': \`Bearer ${token}\` } : {})`
- **更深层检查**：重构后必须端到端测试每个页面的核心功能（不只是视觉），特别是：流式聊天、文件上传、WebSocket 连接等不走标准 axios 管线的功能

**Refine 部署后必须做浏览器端到端验证**：curl 健康检查通过 ≠ 应用可用。部署后必须：
1. 浏览器打开公开 URL，验证 CSS 样式正常渲染
2. 登录测试账号，验证跳转到首页（非重定向循环）
3. 逐页检查所有功能页面是否正常渲染
4. 检查浏览器控制台无 JS 错误
5. **特别检查 API 响应格式匹配**：后端返回 `{feedbacks:[]}` 但前端用 `r.data.items` → `undefined.map()` 崩溃。部署前必须 `curl` 检查每个 API 的实际响应 key，前端代码使用正确的字段名
- **用户信号**："你自己检测好 确保最终可用" = 你部署后没做浏览器验证

**Refine 系统性 UI 重构模式**（多页面 <500 行场景）：当重构目标是整个应用的交互页面（如 8 个 Next.js 页面），且每个文件 <500 行时，采用以下高效模式：
1. **全量阅读**：先用 `search_files` + `read_file` 读取所有页面代码，理解当前状态
2. **设计系统先行**：先写 tailwind.config + globals.css（设计 token），这是一切页面的基础
3. **共享组件次之**：重写 sidebar/layout 等影响所有页面的组件
4. **批量写页面**：用 `execute_code` 包裹多个 `write_file` 调用，一次性重写所有页面（比逐个 patch 快 5x）
5. **统一构建验证**：所有页面写完后 `pnpm build`，一次性修复 TypeScript 跨文件错误
6. **部署**：tar 打包上传 → 服务器 build → PM2 restart

关键洞察：对于中等规模文件（200-500 行），`write_file` 比连续 `patch` 更可靠且更快。TypeScript 严格模式会捕获跨文件类型错误（如 union type 比较），统一构建比逐文件验证更高效。

**回退决策树**（v7.1 新增）：当修复引入新问题或修复时间过长时，使用 `references/rollback-decision-tree.md` 判断是否回退。核心原则：
- 修复尝试 ≥ 3 次仍未解决 → 回退
- 修复引入新的 bug → 回退
- 用户明确要求回退 → 立即回退
- 修复时间 > 30 分钟 → 暂停，通知人类决策

**Next.js standalone + PM2 部署配置**：当 `next.config.js` 设置 `output: 'standalone'` 时，PM2 ecosystem.config.js 必须指向 standalone server.js，不能用 `next start`：
```js
// ecosystem.config.js — standalone 模式正确配置
{
  name: 'pm-web',
  script: 'packages/web/.next/standalone/packages/web/server.js',  // ← 关键路径
  cwd: '/path/to/project',  // ← 必须是项目根目录
  env: { NODE_ENV: 'production', PORT: 3000, HOSTNAME: '0.0.0.0' },
}
```
构建后必须手动同步静态文件：`cp -r .next/static .next/standalone/.next/`。否则 CSS/JS 全部 404（HTML 200 但页面白屏）。
常见错误：PM2 日志出现 `⚠ "next start" does not work with "output: standalone"` 说明配置指向了错误的 script。

**AuthProvider 加载卡死诊断**：页面一直显示 loading spinner（AppShell 的 `if (isLoading)` 分支），但 API 全部正常时的排查路径：
1. `localStorage.getItem('token')` 是否存在？→ 不存在则登录流程有问题
2. `fetch('/api/auth/me', {headers: {Authorization: ...}})` 是否返回正确格式？→ 检查响应 key 是否匹配前端期望（`res.data.user` vs `res.data` 直接是 user）
3. AuthProvider useEffect 中 `.catch()` 是否静默删除 token？→ 加 `console.error` 看实际错误
4. 浏览器控制台 `document.body.innerHTML` 如果只有 spinner div，说明 React hydration 未完成或 useEffect 卡在 await
关键：`curl` 200 + 浏览器 spinner = 前端 JS 执行问题，不是服务器问题。不要反复重启 PM2。

**API 参数兼容性过渡**：前后端并行开发时，前端发送的字段名可能与后端 schema 不一致（如 `query` vs `question`）。后端 zod schema 应同时接受两种名称：
```ts
const schema = z.object({
  question: z.string().min(1).optional(),
  query: z.string().min(1).optional(),
});
// 路由处理中：const q = question || query;
```
避免前端改一个字段名就导致 400 错误。迁移完成后再移除兼容。

**部署后必须浏览器端到端验证（不可跳过）**：部署完成后，仅靠 `curl` 检查 HTTP 状态码（200/307）和 PM2 状态（online）是**不够的**。必须使用浏览器工具实际验证页面渲染和功能可用性：

- **为什么**：curl 200 不代表 CSS 加载、JS 执行、登录流程正常。常见陷阱：standalone 模式漏拷静态文件（CSS 404 但 HTML 200）、中间件 auth 无限重定向、API 代理路径错误等。
- **验证清单**：
  1. `browser_navigate` 到登录页 → 确认样式正常（按钮有背景色、布局正确）
  2. 输入凭据登录 → 确认跳转到首页（不是停留在登录页）
  3. 首页加载 → 确认侧边栏、统计卡片、快捷入口渲染正常
  4. 点击 2-3 个核心页面 → 确认无白屏、无 JS 错误
  5. `browser_console` 检查 `localStorage.getItem('token')` 确认认证工作
- **用户信号**："我登陆看到样式全部没了" — 这就是跳过了浏览器验证的后果。
- **反合理化**："curl 返回 200 了应该没问题" → ❌ 200 只证明服务器在响应，不证明前端可用。必须亲眼看到页面。

**dispatch 延迟**：`hermes kanban dispatch` 可能返回 `Deferred (<profile> at per-profile cap, 1 running): <task_id>`。这是因为该 profile 已有一个任务在跑（并发上限）。这是正常行为 — dispatcher 会在当前任务完成后自动拾取 deferred 任务，无需手动干预。

## Platform notes

### Pipeline Self-Audit

When resuming work on an existing pm-{slug} project or diagnosing pipeline execution quality, use the self-audit methodology: `references/pipeline-self-audit.md`. It provides a 3-layer audit (artifact inventory → automated validation → quality assessment) with ready-to-run diagnostic commands and common findings table.

**Known pitfalls from past audits**: See `references/self-audit-pitfalls.md` for Python gotchas (subprocess timeout ordering, read_file corruption, regex quote nesting), version drift patterns, hardcoded path detection, and quick audit commands.

### Cursor / OpenCode

- 读取本 SKILL.md，按阶段表顺序执行；无 Kanban。
- 在 **align（G1）**、**spec（G2）**、**deploy（High risk）** 暂停等待用户确认。
- MVP 使用内循环协议（Plan → Code → Test → Observe → adjust/retry）。
- 编码：`subagent-driven-development`（Cursor）或 `opencode run`（OpenCode）。
- phuryn 工作流：使用 `references/command-recipes.md` 中的 prompt 链。

### Hermes Agent

- 使用 Kanban 分解（见上文 task graph）；profile 分派各阶段。
- 人工协作：基于 `harness-rules.yaml` 风险分级（On-the-loop 模式）。
- MVP 内循环：`writing-plans` → `ui-ux-pro-max` → `test-driven-development` → `subagent-driven-development` → `ui-acceptance-review` → `opencode`（可选）→ goal-check 验证 → adjust/retry。
- 每阶段完成后：`validate-gates.py --runtime --run {PROJECT_ROOT} --write` → `goal-check.py --stage <current> --project-root {PROJECT_ROOT}` → `progress-tracker.py --project-root {PROJECT_ROOT} show`。

### 棕地 / 轻量模式

- 无 Kanban 时：见 `references/greenfield-light.md`，用 `docs/workflow_state.yaml` 断点续跑。
- 阶段边界运行 `docs-hygiene`。
- v6 新增：可从 `PROGRESS.md` 恢复，无需依赖 `workflow_state.yaml`。
- **棕地审计**：对已有项目执行 v6.2 合规检查，见 `references/brownfield-audit.md`（含诊断命令、产物清单、常见陷阱）。

## Feishu trigger (v6.1 Hermes UX)

**契约 SSOT**: `references/hermes-integration.md` + `assets/trigger-routing.yaml`

| 输入 | 路由 |
|------|------|
| `/goal 产品想法：{描述}` | 飞书 grill 1–2 问 → Kanban greenfield 12 子任务 |
| `/goal 继续优化…` / `继续 pm-{slug}` | `pm_resume` 或 `--scenario brownfield` |
| 正文含 `想法到产品` / `pm-idea-to-mvp` | Kanban（非 Ralph） |

```
/goal 产品想法：{描述}
```

Grill 完成后 gateway 调用 `decompose-pm-pipeline.py --task-id … --scenario greenfield`。
人工卡点 **align + ship**（v7.2 双卡点）— 飞书 `确认 <task-id>` 或 `hermes kanban unblock <task-id>`。spec G2 由脚本 gate，不人工 unblock。

## Upgrade history

| Version | Date | Key changes |
|---------|------|-------------|
| 7.1.0 | 2026-06-15 | **实战强化版**：基于 pm-knowledge-platform E2E 优化复盘 — 强化技能触发机制（trigger_conditions + 快速判断表）、强制浏览器端到端验证（Ship 阶段不可跳过）、回退决策树（`references/rollback-decision-tree.md`）、强化棕地审计流程（构建验证 + 浏览器现状记录）、强化 Inner Loop Protocol（入口检查 + 反合理化表格）、PROGRESS.md 强制更新协议、自动化测试集成（测试覆盖率 + E2E 测试）、性能基准测试（Lighthouse）、安全审计集成（`pm-security-audit-static`）、AI 辅助代码审查（5 轴 Code Review）。每阶段新增反合理化表格，防止 agent 合理化跳过关键步骤。 |
| 7.0.0 | 2026-06-15 | **Agent 行为准则融合**：融合 addyosmani/agent-skills 核心模式 — 6 条不可协商行为准则（`agent-behavior-code.md`）、每阶段反合理化表格 + 失败模式清单（stage cards v7.0）、5 轴 Code Review + 严重性标签（`requesting-code-review` v3.0）、变更规模约束、路由器决策树（orchestrator）。v6.2 解决"走不走"，v7.0 解决"走得好不好"。 |
| 6.2.0 | 2026-06-13 | **Enforced Governance**：强制 runtime 验证（mvp/ship 自动 --runtime/--goal）、G1/G2 辩论门禁（debates/ 目录检查）、跨文档一致性（tech-stack-conflict 检测）、内循环前置检查（goals/harness prerequisites）、RUNBOOK 必需章节（部署/回滚/监控）、Retro 量化要求、Operate 产物强制、最低行数全面提升。基于 pm-knowledge-platform 实战复盘。 |
| 6.1.0 | 2026-06-12 | Production-tested: knowledge graph visualization, RAG fallback, tag management |
| 6.0.0 | 2026-06-12 | **Loop Engineering 集成**：内循环 MVP、runtime verification、goal primitives、on-the-loop human collaboration、fine-grained progress tracking、self-improving harness |
| 5.1.0 | 2026-06-11 | Super Developer pipeline: add ship, operate, grow stages; merge G1/G2/G3 gates |
| 5.0.0 | 2026-06-11 | Cross-platform (Cursor/Hermes/OpenCode); borrowed skills; command-recipes |
| 3.0.0 | 2026-06-07 | Merge V2 + v2.1; pm-aligner; openspec/ui skills; superpowers chain |
| 2.1.0 | 2026-06-07 | GitHub repo + Pages per idea |
| 2.0.0 | (planned) | Superseded by 3.0.0 |
