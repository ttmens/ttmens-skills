---
name: pm-idea-to-mvp
description: "Super-dev pipeline v6.2: Loop Engineering + enforced governance. brief → align → research → analysis → spec → mvp(inner-loop) → ship → operate → grow → retro. Dual-loop, goal primitives, runtime verification, debate gates G1/G2, cross-document consistency."
version: 6.2.0
author: ttmens
license: MIT
platforms: [cursor, hermes, opencode, linux, macos, windows]
metadata:
  hermes:
    tags: [super-developer, pipeline, kanban, loop-engineering, goal-primitives, runtime-verification, on-the-loop, github, pages, openspec, ship, ops, grow]
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

# Super Developer Pipeline v6.2 (pm-idea-to-mvp)

**唯一主流水线**。覆盖 PM、工程、运维、运营全链路。v6.2 引入 **Enforced Governance**：基于 pm-knowledge-platform 实战复盘，强制 runtime 验证、辩论门禁、跨文档一致性检查，杜绝"纸面完成"。

> **设计哲学**：采用 Martin Fowler 的 **双循环框架**（Dual-Loop Framework）——
> - **Why Loop**（战略循环）：持续验证产品方向是否正确（align → research → analysis → retro 反馈）
> - **How Loop**（执行循环）：快速迭代实现路径（spec → MVP inner-loop → ship → operate 反馈）
>
> 两个循环通过 `feedback.jsonl` 与 `evolution-notes.md` 互相驱动，形成自进化闭环。

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
| `brownfield` | analysis | 跳过 brief/align/research；见 `domains/product/brownfield-bootstrap` + `scenarios.yaml` |
| `refine` | mvp | 深化循环；`refine-decompose.py` |
| `optimize` | analysis | 同 brownfield，无 bootstrap 强制 |

棕地项目阶段开始前运行 `docs-hygiene`。`decompose-pm-pipeline.py --scenario brownfield` 生成 skip map。

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

## Inner Loop Protocol（v6 核心）

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

## Progress Tracking（细粒度进度追踪）

v6 引入 `PROGRESS.md` 作为项目级任务追踪文件，取代仅靠 Kanban 状态的方式。

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

### Ship (`pm-shipper`) — v6 新增独立阶段

- 生成 `RUNBOOK.md`：部署步骤、回滚方案、监控指标
- `ui-acceptance-review` (full mode)：完整 UX 验收
- `docs-hygiene`：文档一致性检查
- Deploy 为 High risk → **必须**人工确认
- `goal-check.py --stage ship` 验证 RUNBOOK 可执行性

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

**dispatch 延迟**：`hermes kanban dispatch` 可能返回 `Deferred (<profile> at per-profile cap, 1 running): <task_id>`。这是因为该 profile 已有一个任务在跑（并发上限）。这是正常行为 — dispatcher 会在当前任务完成后自动拾取 deferred 任务，无需手动干预。

## Platform notes

### Pipeline Self-Audit

When resuming work on an existing pm-{slug} project or diagnosing pipeline execution quality, use the self-audit methodology: `references/pipeline-self-audit.md`. It provides a 3-layer audit (artifact inventory → automated validation → quality assessment) with ready-to-run diagnostic commands and common findings table.

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

## Feishu trigger

```
/goal 产品想法：{描述}

按 pm-idea-to-mvp v6 超级开发者流水线执行。项目目录：{PROJECT_ROOT}
含 C4、旅程、UX 验收、MVP 内循环、Ship/Ops/Grow 与 Retro。
使用 On-the-loop 风险分级（仅 deploy 需人工确认）。
完成后发 GitHub Pages 链接。
```

## Upgrade history

| Version | Date | Key changes |
|---------|------|-------------|
| 6.2.0 | 2026-06-13 | **Enforced Governance**：强制 runtime 验证（mvp/ship 自动 --runtime/--goal）、G1/G2 辩论门禁（debates/ 目录检查）、跨文档一致性（tech-stack-conflict 检测）、内循环前置检查（goals/harness prerequisites）、RUNBOOK 必需章节（部署/回滚/监控）、Retro 量化要求、Operate 产物强制、最低行数全面提升。基于 pm-knowledge-platform 实战复盘。 |
| 6.1.0 | 2026-06-12 | Production-tested: knowledge graph visualization, RAG fallback, tag management |
| 6.0.0 | 2026-06-12 | **Loop Engineering 集成**：内循环 MVP、runtime verification、goal primitives、on-the-loop human collaboration、fine-grained progress tracking、self-improving harness |
| 5.1.0 | 2026-06-11 | Super Developer pipeline: add ship, operate, grow stages; merge G1/G2/G3 gates |
| 5.0.0 | 2026-06-11 | Cross-platform (Cursor/Hermes/OpenCode); borrowed skills; command-recipes |
| 3.0.0 | 2026-06-07 | Merge V2 + v2.1; pm-aligner; openspec/ui skills; superpowers chain |
| 2.1.0 | 2026-06-07 | GitHub repo + Pages per idea |
| 2.0.0 | (planned) | Superseded by 3.0.0 |
