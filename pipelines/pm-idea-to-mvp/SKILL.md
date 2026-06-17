---
name: pm-idea-to-mvp
description: "产品开发全流程技能：brief → align → research → analysis → spec → MVP → ship → retro。双循环框架 + 内循环迭代 + 行为准则 + 浏览器验证。"
version: 9.0.0
author: ttmens
license: MIT
platforms: [cursor, hermes, opencode, linux, macos, windows]
metadata:
  hermes:
    tags: [super-developer, loop-engineering, browser-verification, openspec, ship, brownfield-audit]
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
      - c4-architecture
      - openspec
      - user-journey
      - open-design
      - ui-ux-pro-max
      - prd-red-team-panel
      - ui-acceptance-review
      - subagent-driven-development
      - pm-git-publish
      - dogfood
      - test-driven-development
      - writing-plans
      - requesting-code-review
---

# Super Developer Pipeline v9.0 (pm-idea-to-mvp)

覆盖 PM、工程、运维、运营全链路。融合 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的行为准则体系。

> **设计哲学**：Martin Fowler 的 **双循环框架**——
> - **Why Loop**（战略循环）：持续验证方向（align → research → analysis → retro 反馈）
> - **How Loop**（执行循环）：快速迭代实现（spec → MVP inner-loop → ship → operate 反馈）
>
> 两个循环通过 `feedback.jsonl` 与 `evolution-notes.md` 互相驱动，形成自进化闭环。

## 语言（强制）

- 所有面向用户的产物使用**简体中文**
- 代码、URL、技术标识符可保留英文

## Pipeline stages

| Stage | 核心产物 | 技能链 |
|-------|---------|--------|
| 0 brief | `00-brief.md` | — |
| 1 align | `CONTEXT.md`, `decisions.md` | `grill-me` / `grill-with-docs` |
| 2 research | `01-research.md` | (borrowed: pm-opportunity-solution-tree, pm-competitor-analysis) |
| 3 analysis | `02-analysis.md`, `architecture/c4-*.md` | `c4-architecture`, `openspec`, `docs-hygiene` |
| 4 spec | `03b-user-journey.md`, `02b-prototype/`, `03-prd.md`, `openspec/` | `user-journey`, `open-design`, `ui-ux-pro-max`, `prd-red-team-panel` |
| 5 mvp | `04-mvp/`, `UX-REVIEW.md` | `writing-plans` → `test-driven-development` → `subagent-driven-development` → `ui-acceptance-review` → `requesting-code-review` → `dogfood` |
| 6 ship | `RUNBOOK.md`, 浏览器验证报告 | `ui-acceptance-review` (full), `docs-hygiene` |
| 7 operate | ops notes | — |
| 8 grow | `06-growth.md` | — |
| 9 retro | `05-retro.md`, `evolution-notes.md` | `pm-git-publish` |

### 场景

| Scenario | 入口 | 说明 |
|----------|------|------|
| `greenfield` | brief | 默认 0→1 |
| `brownfield` | analysis | 跳过 brief/align/research；先执行棕地审计（见 `references/brownfield-audit.md`） |
| `refine` | mvp | 深化循环 |

### 人工协作

| 场景 | 风险 | 行为 |
|------|------|------|
| Align 完成 | Medium | 暂停等待用户确认 |
| Spec 完成 | Medium | 暂停等待用户确认 |
| Deploy | High | 暂停等待用户确认 |
| Research 补充 / MVP 内循环 | Low | 自主完成 |

## Project directory

```
pm-{slug}/
  00-brief.md
  CONTEXT.md
  decisions.md
  01-research.md
  02-analysis.md
  architecture/           # c4-context.md, c4-container.md, c4-component.md
  03b-user-journey.md
  02b-prototype/          # index.html + DESIGN.md
  03-prd.md
  01b-benchmark.md        # Refine only
  openspec/
    proposal.md
    design.md
    tasks.md
    specs/
  04-mvp/
    DESIGN.md
    UX-REVIEW.md
    README.md
  05-retro.md
  06-growth.md
  07-ops-notes.md
  RUNBOOK.md
  feedback.jsonl
  evolution-notes.md
  docs/index.html
```

## Inner Loop Protocol（MVP 阶段核心）

MVP 使用**递归内循环**，而非线性执行：

```
┌─────────────────────────────────────────┐
│  MVP Inner Loop (max 3 iterations)      │
│                                         │
│  Plan → Code → Test → Observe           │
│   ↑                      │              │
│   └── adjust ←── FAIL ←──┘              │
│          PASS → exit → Ship             │
└─────────────────────────────────────────┘
```

### 入口检查（全部通过才能进入内循环）

| # | 检查项 | 通过标准 |
|---|--------|---------|
| 1 | `openspec/tasks.md` 存在 | 文件存在且 > 100 字节 |
| 2 | `04-mvp/DESIGN.md` 存在 | 由 `ui-ux-pro-max` 生成 |
| 3 | 项目可构建 | `pnpm build` exit 0 |

### 循环步骤

| Step | 动作 | 技能 |
|------|------|------|
| **Plan** | 从 `openspec/tasks.md` 提取本轮目标子集 | `writing-plans` |
| **Code** | 实现代码（TDD 先行） | `test-driven-development` + `subagent-driven-development` |
| **Test** | 运行测试 + lint + build | 项目定义的测试/lint/build 命令 |
| **Observe** | 收集信号：test exit code、lint warnings、build output | agent 判断 |
| **Adjust** | 分析失败原因，调整 plan（仅 FAIL 时） | `feedback.jsonl` 记录 |

### 循环终止

- **PASS**：所有目标满足 → 退出循环，进入 Ship
- **FAIL after 3 iterations**：记录失败原因到 `05-retro.md`，通知人类介入
- **HARNESS ESCALATION**：失败原因是配置问题 → 写入 `evolution-notes.md`

### 反合理化表格

| 常见借口 | 反驳 |
|---------|------|
| "直接写代码，后面再补 tasks.md" | 没有 tasks.md = 盲目编码。先计划再执行。 |
| "构建错误不重要，先写功能" | 构建失败 = 无法部署 = 无法验证。 |
| "测试太耗时，先写功能" | 没有测试的功能 = 未验证的功能。TDD 比后补测试更快。 |

## Stage details

### Align

- `grill-me` if no CONTEXT.md; else `grill-with-docs`
- One question at a time; no code/research/recommendations
- 输出：CONTEXT.md + decisions.md（含假设风险等级标注）

### Research

- Read CONTEXT.md + 00-brief.md
- 01-research.md: competitors, sources with URLs, confidence tags
- ≥5 URLs，来源可访问

### Analysis

- 02-analysis.md: ≥3 options, recommendation, risks
- c4-architecture: architecture/c4-*.md
- Draft openspec/proposal.md; openspec/design.md links C4
- No implementation code

### Spec

- user-journey → 03b-user-journey.md
- open-design prototype (static HTML; optional sketch variants)
- 03-prd.md: ≤5 user stories, acceptance criteria
- openspec/tasks.md + openspec/specs/ delta specs

### MVP (Inner Loop)

见上方 Inner Loop Protocol。

MVP skill chain：

```
writing-plans → ui-ux-pro-max → test-driven-development → subagent-driven-development → ui-acceptance-review → requesting-code-review → dogfood
```

### Ship

- 生成 RUNBOOK.md：部署步骤、回滚方案、监控指标
- `ui-acceptance-review` (full mode)：完整 UX 验收
- `docs-hygiene`：文档一致性检查
- **浏览器端到端验证**（不可跳过）：见 `references/browser-e2e-verification.md`
- Deploy 为 High risk → 必须人工确认

#### 性能基准（推荐）

| 指标 | 目标 |
|------|------|
| Lighthouse Performance | ≥ 90 |
| LCP | ≤ 2.5s |
| CLS | ≤ 0.1 |

#### 安全审计（推荐）

- 检查 XSS、CSRF、SQL 注入、敏感信息泄露
- `npm audit` / `pnpm audit` / `pip-audit`

### Operate

- ops notes：监控配置、告警规则、SLA 定义

### Grow

- 06-growth.md：北极星指标、GTM 策略

### Retro

05-retro.md must include:
- Stage timing & skill hits/misses
- Assumption validation
- Pending items from feedback.jsonl
- 内循环迭代分析（成功/失败原因）
- evolution-notes.md：经验教训 + 改进建议

## Self-evolution

| Layer | Path |
|-------|------|
| Run | `05-retro.md`, `evolution-notes.md` |
| Skills | `pm-idea-to-mvp/CHANGELOG.md` |
| Feedback | `feedback.jsonl` |

`feedback.jsonl` schema:

```json
{"ts":"ISO8601","source":"agent","stage":"mvp","signal":"iter 2 test fail: timeout","proposed_delta":"increase test_timeout","status":"resolved"}
```

## 行为准则

所有阶段共享 `references/agent-behavior-code.md` 中的 6 条不可协商准则：

1. **假设前置** — 非平凡工作前列出假设
2. **主动管理困惑** — STOP，不要猜
3. **必要时推回** — 反谄媚，量化风险
4. **强制简洁** — ~100 行 Good / ~300 行 Acceptable / ~1000 行拆分
5. **范围纪律** — 只触碰被要求的部分
6. **验证而非假设** — 要求具体证据

## 回退决策

修复引入新问题或修复时间过长时，使用 `references/rollback-decision-tree.md`：

| 条件 | 动作 |
|------|------|
| 修复尝试 ≥ 3 次 | 回退 |
| 修复引入新 bug | 回退 |
| 用户要求回退 | 立即回退 |
| 修复时间 > 30 分钟 | 暂停，通知人类 |

## Platform notes

### Cursor / OpenCode

- 读取本 SKILL.md，按阶段表顺序执行
- 在 **align**、**spec**、**deploy** 暂停等待用户确认
- MVP 使用内循环协议（Plan → Code → Test → Observe → adjust/retry）
- 编码：`subagent-driven-development`（Cursor）或 `opencode run`（OpenCode）

### 棕地项目

- 对已有项目执行棕地审计，见 `references/brownfield-audit.md`
- 阶段边界运行 `docs-hygiene`

## 关键参考文件

| 文件 | 用途 |
|------|------|
| `references/agent-behavior-code.md` | 6 条行为准则 + 10 大失败模式 + 变更规模约束 |
| `references/browser-e2e-verification.md` | 浏览器端到端验证清单 |
| `references/browser-tools-ssot.md` | 多平台浏览器工具映射 |
| `references/brownfield-audit.md` | 棕地审计流程 |
| `references/deployment-pitfalls.md` | 部署常见陷阱（standalone、AuthProvider、API 兼容） |
| `references/rollback-decision-tree.md` | 回退决策树 |
| `references/hermes-stage-cards/*.md` | 各阶段详细卡片（含反合理化表格） |
