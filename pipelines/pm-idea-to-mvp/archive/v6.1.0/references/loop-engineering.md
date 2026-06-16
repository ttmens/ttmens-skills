# Loop Engineering — pm-idea-to-mvp v6.0 核心理念

> "The best systems are not the ones that do the most work upfront, but the ones that learn the fastest."  
> — 改编自 Addy Osmani, Boris Cherny, Peter Steinberger 关于 Loop Engineering 的论述

## 1. 什么是 Loop Engineering？

Loop Engineering 是一种将**反馈循环**置于工程实践核心的范式。传统瀑布或线性流水线假设"规划→执行→交付"是一次性过程；而 Loop Engineering 承认：

- **不确定性是常态**：需求会变化，技术选型会暴露问题，用户反馈会推翻假设
- **快速验证优于完美规划**：与其花 3 天写完美设计文档，不如 3 小时出原型并获取反馈
- **自动化决策分级**：低风险决策自动执行，中风险记录决策（ADR），高风险才需要人工介入

### 三位先驱的观点

| 人物 | 核心观点 | 对 pm-idea-to-mvp 的影响 |
|------|----------|--------------------------|
| **Addy Osmani** (Google) | "Automate the boring stuff, let humans focus on creative decisions" | Harness Rules 的 risk-based 分级 |
| **Boris Cherny** (Meta) | "Worktrees let you explore without fear — every branch is disposable" | Inner loop 的 retry/backtrack 机制 |
| **Peter Steinberger** ( PSPDFKit) | "Sub-agents should be specialists; the orchestrator should be dumb" | Profile 分离：orchestrator vs specialist |

## 2. 六大原语（6 Primitives）

Loop Engineering 定义了 6 个构建块：

### 2.1 Automations（自动化）
**定义**：无需人工触发的规则→动作链。  
**在 v6.0 中的实现**：
- `harness-rules.yaml` 定义了 7 类决策的自动处理
- `goal-check.py` 自动验证阶段目标
- `progress-tracker.py` 自动更新 PROGRESS.md
- Kanban 系统的 auto-checkpoint 模式

### 2.2 Worktrees（工作树）
**定义**：隔离的、可丢弃的执行环境，失败不影响主分支。  
**在 v6.0 中的实现**：
- MVP inner loop：每次迭代在 `04-mvp/` 内独立执行
- Backtrack 机制：从 mvp 回退到 spec 时，保留迭代日志但不污染上游产物
- Git worktree 可选：`git worktree add ../mvp-iter-N` 用于并行探索

### 2.3 Skills（技能）
**定义**：可组合、可版本化的能力单元。  
**在 v6.0 中的实现**：
- 每个阶段绑定特定 skill（pm-aligner, pm-researcher, pm-builder 等）
- Skills 可独立升级，不影响流水线结构
- Retro 阶段可产出 `skill_patch` 建议

### 2.4 Connectors（连接器）
**定义**：与外部系统交互的标准化接口。  
**在 v6.0 中的实现**：
- `runtime.test_cmd` / `build_cmd` / `lint_cmd`：连接 CI/测试系统
- `health_url`：连接部署后的服务
- 未来可扩展：Jira connector, Slack connector, GitHub PR connector

### 2.5 Sub-agents（子代理）
**定义**：专注于特定任务的 AI 代理，由 orchestrator 调度。  
**在 v6.0 中的实现**：
- Orchestrator profile：只负责阶段流转和 gate 检查
- Specialist profiles：pm-aligner, pm-researcher, pm-builder, pm-shipper
- 每个 sub-agent 有自己的 skills/ 和 memories/

### 2.6 Memory（记忆）
**定义**：跨会话、跨项目的知识持久化。  
**在 v6.0 中的实现**：
- `PROGRESS.md`：项目级进度记忆
- `DECISIONS.md`：架构决策记录（ADR）
- `harness-rules.yaml`：项目级决策策略记忆
- Retro 阶段的 `evolution` 输出写入全局 memories/

## 3. 双循环框架（Dual-Loop Framework）

灵感来自 Martin Fowler 的 "On the Loop" 模式：

### 3.1 Why Loop（战略循环）
**问题**：我们为什么要做这个项目？目标是否仍然正确？  
**在 v6.0 中的触发点**：
- G1 (Align)：确认问题域和成功标准
- G2 (Spec)：确认 PRD 和用户故事
- Retro：反思目标达成度，产出 evolution 建议

### 3.2 How Loop（战术循环）
**问题**：我们如何以最小代价验证假设？  
**在 v6.0 中的触发点**：
- MVP inner loop：test → fix → rebuild → retest（最多 3 次）
- Research 阶段：发现信息不足 → 补充搜索 → 更新竞品表
- Analysis 阶段：方案不可行 → 回退到 research 补充技术调研

### 3.3 循环嵌套关系
```
Why Loop (战略)
├── Brief → Align (G1) → Research → Analysis → Spec (G2)
│   └── [backtrack to Research if analysis reveals knowledge gap]
└── MVP (G3, How Loop) → Ship → Operate → Grow → Retro
    └── [inner loop: test → fix → rebuild, max 3 iterations]
        └── [backtrack to Spec if design flaw detected]
```

## 4. v6.0 如何实现 Loop Engineering

### 4.1 Harness Rules = Automations + Risk Grading
```yaml
decisions:
  refactor:
    risk: low
    action: auto_verify  # 自动执行，不阻塞
  tech_choice:
    risk: medium
    action: write_adr_and_notify  # 记录决策，通知人类
  deploy:
    risk: high
    action: human_checkpoint  # 必须人工批准
```

### 4.2 Inner Loop = Worktrees + Feedback Signals
```yaml
inner_loop:
  max_iterations: 3
  feedback_signals:
    - test_results  # pytest exit code
    - build_status  # py_compile success
    - lint_clean    # flake8 clean
  backtracking:
    - from: mvp
      to: spec
      condition: 'design_flaw_detected'
```

### 4.3 Goal Verification = Automations + Memory
每个阶段有明确的 goal 定义（`goal.template.yaml`），由 `goal-check.py` 自动验证：
- 文件存在性（file_exists）
- 内容匹配（content_match, regex）
- 命令通过（command_pass）
- URL 计数（url_count）

### 4.4 Progress Tracking = Memory + Connectors
`PROGRESS.md` 是项目级记忆的载体：
- 自动记录阶段切换时间
- 记录 inner loop 迭代历史
- 可被外部工具（Dashboard, Slack bot）读取

## 5. Inner Loop 协议（MVP 阶段）

### 5.1 触发条件
进入 MVP 阶段后，自动启动 inner loop：
1. 执行 `runtime.test_cmd`
2. 执行 `runtime.build_cmd`
3. 执行 `runtime.lint_cmd`
4. 收集反馈信号

### 5.2 迭代决策树
```
if all_signals_pass:
    → exit inner loop, proceed to Ship
elif iteration < max_iterations:
    → analyze failure, fix code, retry
    → log iteration to PROGRESS.md
else:
    → check backtrack conditions
    → if design_flaw: backtrack to Spec
    → else: escalate to human (high risk)
```

### 5.3 Backtrack 协议
当 inner loop 检测到设计缺陷（非代码缺陷）时：
1. 记录 backtrack 原因到 `DECISIONS.md`
2. 更新 `PROGRESS.md` 的 backtracking_log
3. 回退到 Spec 阶段，保留 MVP 代码作为参考
4. 重新执行 Spec → MVP 流程

### 5.4 迭代日志格式
```markdown
## 内循环日志
| 迭代 | 时间 | 触发信号 | 结果 | 决策 |
|------|------|----------|------|------|
| 1 | 2026-06-12 14:30 | test_failure | 3 tests failed | 修复 test_auth.py |
| 2 | 2026-06-12 14:45 | lint_clean | all pass | 进入 Ship |
```

## 6. 对比表：v5.1 (线性) vs v6.0 (递归)

| 维度 | v5.1 (线性) | v6.0 (递归) |
|------|-------------|-------------|
| **阶段流转** | 单向：brief → align → ... → retro | 可回溯：mvp → spec → mvp |
| **人工卡点** | G1, G2, G3 全部人工 | 仅 Ship 人工（默认） |
| **决策处理** | 所有决策等权，全部人工 | Risk-based 分级（low/medium/high） |
| **失败处理** | 阶段失败 → 阻塞，等人工 | 阶段失败 → inner loop retry / backtrack |
| **进度追踪** | 手动更新 gates.template.json | 自动更新 PROGRESS.md |
| **目标验证** | 人工检查产物 | goal-check.py 自动验证 |
| **自我改进** | Retro 产出文档，手动应用 | Retro 产出 skill_patch，低风险自动应用 |
| **记忆系统** | 分散在各阶段文档 | 集中：PROGRESS.md + DECISIONS.md + harness-rules |
| **子代理** | 单 agent 全栈执行 | Orchestrator + Specialist profiles |
| **外部集成** | 硬编码命令 | runtime.* 可配置，支持 health_url |
| **迭代上限** | 无（无限阻塞） | inner loop max 3 次，然后 backtrack/escalate |
| **适用场景** | 需求明确、技术成熟 | 探索性强、需求模糊、技术选型多 |

## 7. 实践建议

### 7.1 何时使用 v6.0？
- ✅ 探索性项目（0→1，无现有代码）
- ✅ 技术选型不确定（需要对比 3+ 方案）
- ✅ 需求模糊（需要用户故事迭代）
- ✅ 快速验证（MVP 优先，完美主义后移）

### 7.2 何时回退到 v5.1？
- ❌ 需求完全明确（已有详细 PRD）
- ❌ 技术栈固定（公司标准栈）
- ❌ 合规要求（每步必须人工审批）
- ❌ 团队不熟悉 Loop Engineering

### 7.3 迁移成本
- **新项目**：直接使用 v6.0，零成本
- **现有 v5.1 项目**：参考 `v6.0-upgrade.md`，约 30 分钟迁移
- **混合模式**：可在 `harness-rules.yaml` 中将所有 decisions.risk 设为 high，退化为 v5.1 行为

## 8. 参考资源

- Martin Fowler, "On the Loop" (2024)
- Addy Osmani, "AI-Assisted Engineering at Google" (2025)
- Boris Cherny, "Worktrees: The Missing Primitive" (2025)
- Peter Steinberger, "Sub-agent Orchestration Patterns" (2025)
- pm-idea-to-mvp v6.0 SKILL.md（本仓库）
- references/runtime-kanban-v6.0.md（运行时详解）
- references/v6.0-upgrade.md（迁移指南）
