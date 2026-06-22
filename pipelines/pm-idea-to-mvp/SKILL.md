---
name: pm-idea-to-mvp
description: "产品开发全流程技能：brief → align → research → analysis → spec → MVP → ship → retro。4 层循环架构 + 双层验证 + 自进化系统。"
version: 9.2.0
author: ttmens
license: MIT
platforms: [cursor, hermes, opencode, linux, macos, windows]
metadata:
  hermes:
    tags: [super-developer, loop-engineering, browser-verification, openspec, ship, brownfield-audit, meta-verification, two-tier-verification]
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
      - ui-acceptance-review
---

# Super Developer Pipeline v9.2 (pm-idea-to-mvp)

覆盖 PM、工程、运维、运营全链路。融合 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的行为准则体系。

> **设计哲学**：基于 Loop Engineering 最佳实践的 **4 层循环架构**——
> - **Loop 1: Agent Loop**（自动化工作）：模型重复调用工具直到任务完成
> - **Loop 2: Verification Loop**（确保质量）：双层验证（LLM 改进 + 确定性硬停止）
> - **Loop 3: Event-Driven Loop**（规模化集成）：事件触发代理运行（webhook、cron、新数据）
> - **Loop 4: Hill Climbing Loop**（自动化改进）：分析生产 traces，自动重写 harness 配置
>
> 核心洞察：**验证器才是产品，其他都是管道**。输出质量受限于验证器质量，不会更高。
>
> 两个战略循环（Why Loop + How Loop）通过 `feedback.jsonl` 与 `evolution-notes.md` 互相驱动，形成自进化闭环。

## 语言（强制）

- 所有面向用户的产物使用**简体中文**
- 代码、URL、技术标识符可保留英文

## Pipeline stages

| Stage | 核心产物 | 技能链 | 验收标准 |
|-------|---------|--------|----------|
| 0 brief | `00-brief.md` | — | 用户确认 brief 准确 |
| 1 align | `CONTEXT.md`, `decisions.md` | `grill-me` / `grill-with-docs` | 假设风险等级标注完成 |
| 2 research | `01-research.md` | (borrowed: pm-opportunity-solution-tree, pm-competitor-analysis) | ≥5 URLs，来源可访问 |
| 3 analysis | `02-analysis.md`, `architecture/c4-*.md` | `c4-architecture`, `openspec`, `docs-hygiene` | ≥3 options, recommendation |
| 4 spec | `03b-user-journey.md`, `02b-prototype/`, `03-prd.md`, `openspec/`, `DESIGN.md` | `user-journey`, `open-design`, `ui-ux-pro-max`, `prd-red-team-panel` | ≤5 user stories, acceptance criteria |
| 5 mvp | `04-mvp/`, `UX-REVIEW.md` | `writing-plans` → `test-driven-development` → `subagent-driven-development` → `ui-acceptance-review` → `requesting-code-review` → `dogfood` | 内循环 PASS 或 3 iter 后人工介入 |
| 6 ship | `RUNBOOK.md`, 浏览器验证报告 | `ui-acceptance-review` (full), `docs-hygiene`, `remote-server-deployment` | 5 维度质量门全部通过 |
| 7 operate | ops notes | — | 监控配置完成 |
| 8 grow | `06-growth.md` | — | 北极星指标定义 |
| 9 retro | `05-retro.md`, `evolution-notes.md` | `pm-git-publish` | feedback.jsonl 闭环 |

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
  02b-prototype/          # index.html + DESIGN.md (prototype-level)
  DESIGN.md               # 设计系统文档（Spec 阶段产出）
  03-prd.md
  01b-benchmark.md        # Refine only
  openspec/
    proposal.md
    design.md
    tasks.md
    specs/
  04-mvp/
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
| 2 | `DESIGN.md` 存在 | 由 `ui-ux-pro-max` 生成（Spec 阶段产出） |
| 3 | 项目可构建 | `pnpm build` exit 0 |

### 循环步骤

| Step | 动作 | 技能 |
|------|------|------|
| **Plan** | 从 `openspec/tasks.md` 提取本轮目标子集 | `writing-plans` |
| **Code** | 实现代码（TDD 先行） | `test-driven-development` + `subagent-driven-development` |
| **Test** | 运行测试 + lint + build | 项目定义的测试/lint/build 命令 |
| **Observe** | 收集信号：test exit code、lint warnings、build output | agent 判断 |
| **Adjust** | 分析失败原因，调整 plan（仅 FAIL 时） | `feedback.jsonl` 记录 |

### 循环终止（v9.2 增强：最优停止条件）

- **PASS**：所有目标满足 → 退出循环，进入 Ship
- **FAIL after 3 iterations**：记录失败原因到 `05-retro.md`，通知人类介入
- **HARNESS ESCALATION**：失败原因是配置问题 → 写入 `evolution-notes.md`

#### 最优停止策略（v9.2 新增）

**问题**：固定 3 次迭代，缺少质量-效率权衡  
**方案**：动态迭代 + 质量收敛判断

**迭代次数决策树**：
- Iteration 1: 基础功能通过 → 继续
- Iteration 2: 边界情况覆盖 → 继续
- Iteration 3: 性能优化 → 评估
- Iteration 4+: 仍有问题 → 记录到 feedback.jsonl，人工介入

**质量收敛判断**：
- 如果 Iteration N 的改进 < 10%（测试通过率提升 < 10%），停止
- 如果连续 2 次迭代无新测试通过，停止

**产物**：`iteration-summary.md`（每次迭代的改进摘要）

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
- **DESIGN.md**：设计系统文档（颜色、字体、组件、间距），参考 `references/design-md-template.md`
- 03-prd.md: ≤5 user stories, acceptance criteria
- openspec/tasks.md + openspec/specs/ delta specs

### MVP (Inner Loop)

见上方 Inner Loop Protocol。

MVP skill chain：

```
writing-plans → ui-ux-pro-max → test-driven-development → subagent-driven-development → ui-acceptance-review → requesting-code-review → dogfood
```

### Ship（6 维度质量门 + 双层验证架构）

| 维度 | 检查项 | 技能/工具 | 通过标准 | 验证类型 |
|------|--------|-----------|----------|---------|
| 1. 视觉规范 | 设计系统一致性、品牌色、字体 | `ui-acceptance-review` | 0 critical issues | 概率性（LLM） |
| 2. 组件结构 | 代码质量、lint、构建、TypeScript 类型 | 项目 lint/build 命令 | exit 0, 0 errors | **确定性（硬停止）** |
| 3. 交互体验 | 可访问性、焦点状态、键盘导航 | `ui-acceptance-review` | 0 WCAG violations | 概率性（LLM） |
| 4. 移动端适配 | 响应式布局、触摸目标、viewport | browser E2E + viewport 测试 | 320px-1440px 无布局破坏 | **确定性（硬停止）** |
| 5. 上线把关 | RUNBOOK.md、回滚方案、监控指标 | 人工确认 | 用户签字 | **确定性（硬停止）** |
| 6. 验证器健康度 | 质量门本身是否被测试过 | Meta-Verification | 0 未测试的质量门 | **确定性（硬停止）** |

#### 双层验证架构（v9.2 新增）

**Layer 1: LLM 验证器（改进层，概率性）**
- 角色：改进草稿，提供语义级反馈
- 工具：`ui-acceptance-review`（LLM 判断）、`prd-red-team-panel`、`dogfood`
- 输出：改进建议（非硬停止）
- 特点：可变，每次运行可能不同

**Layer 2: 确定性验证（硬停止层，确定性）**
- 角色：最终发货门
- 工具：lint/build/test/browser-e2e/security-audit
- 输出：PASS/FAIL（硬停止）
- 特点：可重现，每次运行结果相同

**工作流**：
```
LLM 验证器改进草稿 → 确定性验证决定是否发货
```

**原则**：
- 概率性验证用于改进
- 确定性验证用于发货
- 两者结合：LLM 改进 → 确定性决定
- **"两个乐观主义者"陷阱**（Sonar）：如果验证来自做了工作的同一个模型（自评分），或者来自被礼貌要求"审查"的第二个模型（友善偏差），结果是**两个乐观主义者达成一致**——自信的错误答案传播到下一次迭代。永远不要让概率性检查成为最终门。
- **斯坦福发现**：AI 准确率在中等 token 消耗时达到峰值。更多循环可能让结果更差。预算上限和重试限制是必需的。

#### Meta-Verification Gate（v9.2 新增）

**问题**：质量门本身没有自我验证机制  
**方案**：增加第 6 维度"验证器健康度"

**检查项**：
- 质量门本身是否被测试过？
- 是否有假阳性/假阴性案例？
- 验证器是否随项目演进更新？
- 通过标准：0 未测试的质量门

**产物**：`verification-gate-health.md`

- **浏览器端到端验证**（不可跳过）：见 `references/browser-e2e-verification.md`
- Deploy 为 High risk → 必须人工确认

**深度交互测试要求**：用户明确要求"深入点击都要检查"时，不能只验证页面加载成功。必须测试所有可交互元素：
- 列表项 → 详情页
- 按钮 → 模态框/表单
- 标签页 → 内容切换
- 编辑 → 保存 → 取消
- 所有深层交互路径都必须验证，不能停留在"页面无报错"层面

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

## Self-evolution（v9.2 增强：外循环自动化）

### 信号收集
- `feedback.jsonl`：内循环迭代中的失败/调整记录
- 用户纠正：Agent 行为偏离预期时的反馈
- `loop-cost-tracker.jsonl`：每次循环的 token 消耗和时长

### 规则转化流程
1. **记录 Signal**：feedback.jsonl 中记录具体失败场景
2. **抽象规则**：从 3+ 次相似失败中提取模式
3. **规则建议**：写入 `evolution-notes.md` 的 "Proposed Rules" 章节
4. **人工确认**：Retro 阶段与用户确认规则有效性
5. **更新规则库**：确认后写入 `references/agent-behavior-code.md` 或 stage cards

### 外循环自动化（v9.2 新增）

**问题**：feedback.jsonl 手动记录，缺少模式识别  
**方案**：每个项目完成后自动分析

**触发条件**：
- 每个项目完成 retro 阶段后立即启动
- 或 feedback.jsonl 新增记录时

**自动化流程**：
1. 运行 `consume-feedback.py --pattern-detection`
2. 识别重复失败模式（≥3 次相似失败）
3. 生成新规则建议
4. 写入 `evolution-notes.md` 的 "Auto-Detected Patterns" 章节
5. 人工确认后，更新 `agent-behavior-code.md`

**产物**：
- `auto-detected-patterns.md`

### 规则来源原则
- 规则应来自真实失败，而非理论最佳实践
- 每条规则必须关联至少 1 个 feedback.jsonl 记录
- 规则更新需人工确认，不自动生效

`feedback.jsonl` schema:

```json
{"ts":"ISO8601","source":"agent","stage":"mvp","signal":"iter 2 test fail: timeout","proposed_delta":"increase test_timeout","status":"resolved"}
```

## 行为准则

所有阶段共享 `references/agent-behavior-code.md` 中的 7 条不可协商准则：

1. **假设前置** — 非平凡工作前列出假设
2. **主动管理困惑** — STOP，不要猜
3. **必要时推回** — 反谄媚，量化风险
4. **强制简洁** — ~100 行 Good / ~300 行 Acceptable / ~1000 行拆分
5. **范围纪律** — 只触碰被要求的部分
6. **验证而非假设** — 要求具体证据
7. **规则来自失败** — 规则应源自真实失败场景（feedback.jsonl），而非理论最佳实践

## 4 层循环架构（v9.2 新增）

基于 Loop Engineering 最佳实践，明确区分 4 种循环类型：

### Loop 1: Agent Loop（自动化工作）
- **功能**：模型重复调用工具直到任务完成
- **实现**：MVP Inner Loop（Plan→Code→Test→Observe→Adjust）
- **产物**：代码、测试、文档
- **特点**：单任务级别，自动迭代

### Loop 2: Verification Loop（确保质量）
- **功能**：包装 Agent Loop，评分输出 vs 标准
- **实现**：6 维度质量门 + 双层验证（LLM + 确定性）+ Meta-Verification
- **产物**：验证报告、改进建议
- **特点**：质量把关，硬停止

### Loop 3: Event-Driven Loop（规模化集成）
- **功能**：事件触发代理运行（webhook、cron、新数据）
- **实现**：`/goal` 命令 + cron jobs + Hermes Gateway
- **产物**：自动化工作流
- **特点**：后台运行，事件驱动

### Loop 4: Hill Climbing Loop（自动化改进）
- **功能**：分析生产 traces，自动重写 harness 配置
- **实现**：外循环自动化（consume-feedback.py --pattern-detection）
- **产物**：更新的技能、规则、模板
- **特点**：持续改进，自进化

### 循环关系
```
Loop 4 (Hill Climbing) ──更新──→ Loop 2 (Verification)
         ↑                              ↓
         └──────分析 traces──────── Loop 1 (Agent)
                                    ↓
                              Loop 3 (Event-Driven)
```

## 验证器分类（v9.2 新增）

明确区分概率性验证和确定性验证：

### 概率性验证（LLM 判断，可变）
- `ui-acceptance-review`（视觉规范）
- `prd-red-team-panel`（需求审查）
- `dogfood`（探索性测试）
- **用途**：改进草稿，提供语义级反馈
- **特点**：每次运行可能不同，不能作为硬停止

### 确定性验证（硬停止，可重现）
- lint（代码质量）
- build（构建成功）
- test（测试通过）
- browser-e2e（端到端测试）
- security-audit（安全扫描）
- **用途**：最终发货门
- **特点**：每次运行结果相同，是硬停止

### 原则
- 概率性验证用于改进
- 确定性验证用于发货
- 两者结合：LLM 改进 → 确定性决定
- **核心洞察**：输出质量受限于验证器质量，不会更高

## 回退决策

修复引入新问题或修复时间过长时，使用 `references/rollback-decision-tree.md`：

| 条件 | 动作 |
|------|------|
| 修复尝试 ≥ 3 次 | 回退 |
| 修复引入新 bug | 回退 |
| 用户要求回退 | 立即回退 |
| 修复时间 > 30 分钟 | 暂停，通知人类 |

## Platform notes

### Agent 编排原则

- **默认单 Agent**：一个主 Agent 负责全流程执行
- **拆子 Agent 的两种情况**：
  1. **需要独立审查**：Code Review、安全审计等需要独立视角的任务
  2. **互不依赖可并行**：多模块分析（Go + React + Flutter）可并行执行
- **上下文传递**：子 Agent 通过文档（而非口头指令）接收任务，确保环节不丢上下文

### Cursor / OpenCode

- 读取本 SKILL.md，按阶段表顺序执行
- 在 **align**、**spec**、**deploy** 暂停等待用户确认
- MVP 使用内循环协议（Plan → Code → Test → Observe → adjust/retry）
- 编码：`subagent-driven-development`（Cursor）或 `opencode run`（OpenCode）

### 棕地项目

- 对已有项目执行棕地审计，见 `references/brownfield-audit.md`
- 阶段边界运行 `docs-hygiene`
- **多模块项目**（Go + React + Flutter + Python 等）：使用 `delegate_task` 并行分析所有模块，按安全审计清单逐项检查（硬编码密钥、CORS、N+1 查询、API Key 外部化、敏感信息脱敏）。详见 `references/brownfield-audit.md` 的 "Multi-Module Deep Optimization" 章节。

## 关键参考文件

| 文件 | 用途 |
|------|------|
| `references/agent-behavior-code.md` | 7 条行为准则 + 10 大失败模式 + 变更规模约束 |
| `references/browser-e2e-verification.md` | 浏览器端到端验证清单 |
| `references/browser-tools-ssot.md` | 多平台浏览器工具映射 |
| `references/brownfield-audit.md` | 棕地审计流程 |
| `references/deployment-pitfalls.md` | 部署常见陷阱（standalone、AuthProvider、API 兼容） |
| `references/design-md-template.md` | DESIGN.md 设计系统文档模板（Google Stitch 格式） |
| `references/web-optimization-patterns.md` | Web 性能优化：React 代码分割、Redis Pipeline、CORS、脱敏、表单验证 |
| `references/rollback-decision-tree.md` | 回退决策树 |
| `references/fullstack-debugging-nextjs-prisma.md` | Next.js+Prisma+SQLite 全栈调试：JSON字段解析、Tailwind safelist、PM2 env、Vision配置 |
| `references/loop-engineering-research.md` | Loop Engineering 业界研究：关键引言、4层循环、双层验证、"两个乐观主义者"陷阱、斯坦福发现、Bun案例 |
| `references/hermes-stage-cards/*.md` | 各阶段详细卡片（含反合理化表格） |
