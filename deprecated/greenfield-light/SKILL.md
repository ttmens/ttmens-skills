---
name: idea-to-product
description: >-
  将想法从概念推进到可交付产品：自主模式、phase-increment、三里程碑门禁、分域验收。
  由 product-orchestrator 路由调用。
version: 4.0.0
author: ttmens
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, product-development, ideation, research, design, grill, implementation, release, autonomous]
    related_skills:
      - product-orchestrator
      - writing-plans
      - subagent-driven-development
      - docs-hygiene
      - design-system-md
      - ui-acceptance-review
---

# Idea-to-Product 工作流

将想法从概念推进到可交付产品的完整工作流。适用于代码类产品，也适用于技能、工具、文档等产品形态。

## 总览

```
💡 想法提取 → 🔬 深度调研 → 🎨 产品设计 → 🔥 Grill 评审 → 📋 版本计划 → ⚙️ 执行 → 📦 交付 → 📚 学习反馈
 (extract)     (research)     (design)     (grill)     (plan)      (build)   (ship)    (learn)
```

**核心原则：**
- 调研先于设计 —— 不了解业界实践就设计，大概率是重新发明轮子
- Grill 先于实现 —— 方案没被质疑过，就不值得构建
- 版本化构建 —— 每个版本独立可交付，不追求一次完美
- 每次迭代都要让用户看到可交互的东西
- 学习反馈闭环 —— 每个周期结束后提取学习成果，更新经验和技能

## 自主模式（默认开启）

1. 启动时读取或创建 `docs/workflow_state.yaml`（模板：`assets/workflow_state.template.yaml`）
2. 每步完成更新 checkpoint；下一会话从 `current_phase` 续跑
3. **仅在 G1/G2/G3 停等用户**；其余阶段自动推进
4. 阻塞时：记录 blocker → 2 种备选 → 仍失败才汇报

## 运行模式

| 模式 | 适用 | 行为 |
|------|------|------|
| **greenfield** | 从零新建 | Extract → Research → … → Learn |
| **phase-increment** | 棕地/已有产品 | 读 SSOT + DECISIONS → 定义 target_phase → 只跑该 Phase |

棕地默认：输出 `docs/plans/YYYY-MM-DD-phase-X.md`（模板 `assets/phase-plan.template.md`）。

## 三里程碑门禁

| Gate | 产出 | 停点 |
|------|------|------|
| **G1** | `docs/research.md` 双轴调研（模板 `assets/research-two-axis.template.md`） | awaiting_user |
| **G2** | `docs/design.md` + ASCII 线框 + `docs/DESIGN.md` 草案 | awaiting_user |
| **G3** | `docs/ui-acceptance-report.md` + pre/post 快照 | awaiting_user |

含 UI 改动的 Phase：Ship 前跑 `ui_acceptance.py --full`；每个 Phase 至少跑 `--quick`。

## 分域验收

每个 Phase 使用 `assets/acceptance-matrix.template.md`：**functional / ux / ops** 三域不可省略 UX。

## 什么时候用

- 用户有一个想法，想端到端构建出来
- 用户说"帮我做 X"、"建一个 Y"、"搞一个 Z"
- 功能需求，需要先验证再实现
- 任何需要先调研再设计的产品类任务

---

## Phase 1: 想法提取（Extract）

**目标：** 把模糊的想法变成清晰、可执行的产品概念。

### 交互式提炼

当用户的想法还比较模糊时，通过提问帮助澄清：

**必须回答的核心问题：**
1. 解决什么问题？（用户痛点）
2. 目标用户是谁？
3. 最小可用版本长什么样？
4. 有什么约束条件？（时间、技术、资源）

### 想法分类

根据用户输入判断任务类型：

| 类型 | 特征 | 后续路径 |
|------|------|----------|
| 🟢 绿野项目 | 从零开始，没有现有代码/基础设施 | 完整流程 |
| 🟡 棕地项目 | 在现有系统/代码库上添加功能 | 先做技术审计，再设计 |
| 🔴 轻量修复 | 小 bug 或小改动 | 走 Patches 路径，跳过完整周期 |

### 输出

保存到 `docs/discovery.md`：

```markdown
# 发现文档

## 原始想法
[用户的原始描述]

## 提炼后的概念
[1-2 段清晰描述]

## 核心问题
- 解决: ...
- 用户: ...
- 约束: ...

## 项目类型
- 绿野 / 棕地 / 轻量修复

## 最小可用版本
[描述 MVP 应该包含什么]
```

### 转入 Phase 2

**自动进入 Research**（棕地项目若 SSOT 已清晰可跳过至 plan，须在 workflow_state 记录理由）。

---

## Phase 2: 深度调研（Research）

**目标：** 在动手设计之前，充分调研业界最佳实践。

### 什么时候必须做

- 你不完全了解这个领域
- 用户说"调研一下"、"看看业界怎么做"
- 涉及开源工具选型、工作流设计、产品方案
- 初稿被用户否定（说明理解不够深入）

### 调研方法

**1. 多源搜索：**
```
GitHub 搜索 → 相关项目，stars、更新、issue 活跃度
npm/pip/crates → 相关包，版本历史、依赖
技术博客/论坛 → 实践经验总结
```

**2. 不只读 README，读关键实现：**
```
README.md → 项目定位和核心能力
源码核心文件 → 实际怎么做
测试/示例 → 真实使用场景
```

**3. 提炼可复用模式，不只罗列项目：**
```
❌ 坏输出：A 做了 X，B 做了 Y，C 做了 Z
✅ 好输出：业界有三种模式：模式 A（场景 1）、模式 B（场景 2）...
```

### 输出

保存到 `docs/research.md`：

```markdown
## 🔍 调研发现

### 业界模式
| 模式 | 代表项目 | 适用场景 | 优点 | 缺点 |
|------|---------|---------|------|------|
| ... | ... | ... | ... | ... |

### 核心洞察
1. ...（关键结论）

### 对我们的启示
- 应该采用 XX 模式，因为...
- 应该避免 YY，因为...
```

### 转入 Phase 3

展示调研结果，写入 research.md，**设置 G1 → awaiting_user**，等待用户确认后继续 Design。

---

## Phase 3: 产品设计（Design）

**目标：** 基于调研和用户需求，设计可落地的方案。

### 产品输出件

根据任务性质选择：

| 输出件 | 说明 |
|--------|------|
| **PRD** | 产品需求文档：目标、用户、功能、验收标准 |
| **竞品分析** | 对比 2-3 个方案的优劣势 |
| **架构设计** | 系统结构、模块划分、数据流 |
| **用户故事** | "作为 XX，我希望 XX，以便 XX" |
| **决策记录** | 为什么选 A 不选 B |
| **技能文档** | 如果是 Hermes skill，包含触发条件、操作流程、陷阱、示例 |
| **模板/脚本** | 可复用的模板和自动化工具 |

### 设计要求

- **具体可执行**：不说"做一个待办管理"，而是"用 patch 操作 TODO.md 的 P0/P1/P2 分区"
- **有自动化能力**：不只是定义格式，而是能自动干活
- **中文输出**：除非用户特别要求，否则面向用户的文档用简体中文
- **版本化**：定义清晰的版本边界，每个版本独立可交付

### 输出

保存到 `docs/design.md`：

```markdown
# [产品名] 设计方案

## 背景
- 要解决的问题
- 目标用户

## 业界调研结论
- 最佳实践模式
- 我们的选择及理由

## 产品架构
- 模块划分
- 数据流

## 版本规划
| 版本 | 范围 | 交付物 | 预估 |
|------|------|--------|------|
| v0.1 | MVP 核心功能 | ... | ... |
| v0.2 | 增强功能 | ... | ... |

## 核心能力
| 能力 | 用户触发 | 系统行为 |
|------|---------|---------|

## 输出件清单
- [ ] SKILL.md
- [ ] 模板文件
- [ ] 脚本/工具

## 文件结构
```
path/to/output/
├── ...
```
```

### 转入 Phase 4

**不要直接进入实现。先过 Grill 评审。**

---

## Phase 4: Grill 评审（Challenge）

**目标：** 对设计方案进行批判性质疑，找出漏洞。

### Grill 问题清单

**1. 必要性拷问**
- 这个能力用户真的需要吗？
- 有没有更简单的方式达到同样效果？
- 如果不做，用户会损失什么？

**2. 可行性拷问**
- 技术上有什么坑？调研到的项目踩过什么坑？
- 依赖的工具有没有不稳定/已废弃的风险？
- 用户的实际环境能不能跑起来？

**3. 完整性拷问**
- 用户说了一句话，我们覆盖了所有隐含场景吗？
- 异常/边界情况处理了吗？
- 如果数据格式和预期不一样怎么办？

**4. 体验拷问**
- 用户用起来需要几步？能不能更少？
- 输出对用户有意义吗？还是"格式对了但没用"？
- 初稿被用户否定的风险在哪里？

### 输出

```markdown
## 🔥 Grill 结果

### 通过的项
- ...（设计合理）

### 需要修改的项
- [ ] ... → 修改方案：...

### 风险项
- ⚠️ ...（需要用户确认）
```

### Grill 结果处理

- **全部通过** → 转入 Phase 5
- **有修改项** → 修改方案 → 重新 Grill（最多 2 轮）
- **有重大风险** → 向用户汇报：继续 / 调整 / 放弃

---

## Phase 5: 版本计划（Plan）

**目标：** 将设计方案拆解为版本化的可执行任务。

### 版本规划

每个版本应该：
- 独立可交付
- 范围清晰
- 预估合理
- 有明确的验收标准

### 任务拆解

加载 `writing-plans` skill，将每个版本拆解为 bite-sized 任务。

每个任务 = 2-5 分钟 focused work。

### 输出

保存到 `docs/plans/YYYY-MM-DD-产品名.md`

### 转入 Phase 6

计划写入 `docs/plans/` 后 **自动进入 Build**（加载 subagent-driven-development）。

---

## Phase 6: 执行（Build）

**目标：** 按计划执行，每个任务有审查。

### 执行循环

```
实现 → 规格审查 → (fix if needed) → 质量审查 → (fix if needed) → 下一任务
```

### 版本完成

当一个版本的所有任务完成后：
1. 运行完整测试
2. 安全扫描
3. 生成版本说明
4. 提交代码

### 转入 Phase 7

一个版本完成 → 交付 或 继续下一版本

---

## Phase 7: 交付（Ship）

**目标：** 将可工作的产品交付给用户。

### 交付检查清单

- [ ] 所有测试通过
- [ ] 安全扫描通过
- [ ] 文档已更新
- [ ] 用户已确认功能
- [ ] 代码已提交/推送

### 交付方式

- 代码类产品：PR → Review → Merge
- 技能类：安装到 Hermes skills 目录
- 文档类：保存到指定位置

---

## Phase 8: 学习反馈（Learn）

**目标：** 提取学习成果，更新经验和技能。

### 学习提取

每个版本或周期结束后：

**1. 做得好的（继续保持）：**
- 哪些做法效果特别好？
- 哪些调研结果被验证是正确的？

**2. 需要改进的：**
- 哪些地方花了比预期更多的时间？
- 哪些假设被证明是错的？
- 用户否定了什么？为什么？

**3. 新的认知：**
- 发现了什么之前不知道的？
- 业界有什么新的最佳实践？

**4. 可复用的资产：**
- 有没有可以保存为 skill 的？
- 有没有可以更新的 skill？

### 自进化动作

根据学习结果自动执行：

```python
# 如果发现新的工作流模式
skill_manage(action='create', name='new-workflow', ...)

# 如果发现已有 skill 的陷阱
skill_manage(action='patch', name='existing-skill', 
             old_string='...', new_string='...')

# 如果某个 skill 不再适用
skill_manage(action='delete', name='obsolete-skill')

# 更新记忆中的经验
memory(action='add', target='memory', content='新发现的最佳实践...')
```

### 输出

保存到 `docs/retro/YYYY-MM-DD-产品名.md`：

```markdown
# 回顾：[产品名]

## 做得好的
- ...

## 需要改进的
- ...

## 新的认知
- ...

## 自进化动作
- [ ] 创建/更新/删除 skill: ...
- [ ] 更新记忆: ...
```

---

## 路径选择

根据任务性质，选择不同路径：

### 路径 A: 完整周期（绿野项目）

```
想法提取 → 深度调研 → 产品设计 → Grill → 计划 → 执行 → 交付 → 学习
```

### 路径 B: 棕地项目

```
想法提取 → 技术审计 → 设计 → Grill → 计划 → 执行 → 交付 → 学习
```

技术审计替代深度调研：分析现有代码库/系统，了解现状后再设计。

### 路径 C: 轻量修复（Patches）

```
想法提取 → 直接修复 → 验证 → 交付
```

跳过调研、设计、Grill，快速修复。但仍然需要验证和记录。

### 路径 D: 只做设计

```
想法提取 → 深度调研 → 产品设计 → Grill → 交付设计方案
```

不执行实现，只输出设计方案。

---

## 快速开始

优先加载 **product-orchestrator**。用户说"做 X"时：

1. 判断类型（绿野/棕地/轻量修复）
2. 棕地 → phase-increment；绿野 → greenfield
3. 初始化 workflow_state.yaml
4. 跑 docs-hygiene
5. 按 current_phase 推进，仅在 G1/G2/G3 停

## 跳过阶段指南

| 阶段 | 可以跳过的情况 |
|------|---------------|
| 想法提取 | 用户已有清晰的需求文档 |
| 深度调研 | 技术成熟、方案明确、用户有清晰方向 |
| Grill | 任务极简单（< 15 分钟）且无设计取舍 |
| Spike | 技术风险低，不需要原型验证 |
| 详细计划 | 任务极简单 |

但 **永远不要跳过验证**—— 交付的东西必须经过检查。

## 错误恢复

### 调研后发现此路不通
- 向用户报告发现
- 建议替代方案
- 让用户决定：转向 / 放弃

### Grill 发现方案有根本问题
- 向用户汇报
- 建议重新设计或放弃
- 如果用户坚持继续，记录风险并执行

### 实现中遇到调研没覆盖的坑
- 停下来，补充调研
- 更新设计方案
- 重新 Grill 修改部分

## 整合点

| Phase | 加载 Skill | 关键输出 |
|-------|-----------|----------|
| 1. 想法提取 | product-orchestrator | discovery.md |
| 2. 深度调研 | web/search + 双轴模板 | research.md → **G1** |
| 3. 产品设计 | design-system-md | design.md + DESIGN.md 草案 |
| 4. Grill 评审 | (内置清单) | grill-结果 → **G2** |
| 5. 版本计划 | `writing-plans` | docs/plans/*.md |
| 6. 执行 | `subagent-driven-development` | 可工作的产品 |
| 7. 验证交付 | `ui-acceptance-review` + self_check | ui-acceptance-report → **G3** |
| 8. 学习反馈 | docs-hygiene + obsidian（可选） | retro.md + DECISIONS.md |

### Learn 阶段（Phase 8 补充）

- 保存 `docs/retro/YYYY-MM-DD-<slug>.md`
- **必须**同步架构决策到 `docs/DECISIONS.md`
- stock-copilot 可选写入 `output/evolution/`
- 可选：obsidian-deepen-review 生成周报；obsidian-todo-manager 同步任务

## 记住

```
调研先于设计
Grill 先于实现
版本化构建，每次都可交付
验证先于交付
学习反馈闭环，持续自进化
```
