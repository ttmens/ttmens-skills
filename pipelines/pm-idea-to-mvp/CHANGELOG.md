# pm-idea-to-mvp Changelog

## 6.0.0 — 2026-06-12

### 🚀 核心变化：从线性流水线到 Loop Engineering

**架构升级**：引入 Loop Engineering 范式（灵感来自 Martin Fowler 的 "On the Loop" 模式），将传统的线性流水线升级为递归循环架构。

### ✨ 新增特性

#### 1. 双循环框架（Dual-Loop Framework）
- **Why Loop（战略循环）**：Brief → Align → Research → Analysis → Spec，支持 backtrack
- **How Loop（战术循环）**：MVP inner loop，支持 test → fix → rebuild 迭代（最多 3 次）

#### 2. Harness Rules（风险分级决策自动化）
- 新增 `harness-rules.yaml`，定义 7 类决策的风险等级和处理方式
- **Low risk**：自动执行（refactor, research_supplement）
- **Medium risk**：写 ADR 并通知（tech_choice, architecture_change, scope_change）
- **High risk**：人工卡点（deploy, data_migration）

#### 3. Inner Loop（MVP 阶段内循环）
- MVP 阶段支持最多 3 次迭代，基于 runtime 反馈信号（test, build, lint）
- 自动 backtrack 机制：检测到设计缺陷时回退到 Spec 阶段
- 迭代日志自动记录到 PROGRESS.md

#### 4. Goal Verification（目标自动验证）
- 新增 `goal.template.yaml`，定义各阶段的目标检查规则
- 支持 5 种验证类型：file_exists, content_match, command_pass, url_count, forbidden
- `goal-check.py` 自动验证，替代人工检查

#### 5. Progress Tracking（进度自动追踪）
- 新增 `PROGRESS.md`，自动记录阶段切换、inner loop 迭代、backtrack 历史
- `progress-tracker.py` 自动更新，替代手动维护 gates.json

#### 6. 人工卡点优化
- **v5.1**：G1 (Align), G2 (Spec), G3 (Ship) 全部人工审批
- **v6.0**：仅 Ship 阶段人工审批（默认），其他阶段自动流转
- 可通过 `harness-rules.yaml` 自定义卡点策略

### 📝 新增文件

| 文件 | 用途 |
|------|------|
| `assets/harness-rules.template.yaml` | 决策风险分级模板 |
| `assets/progress.template.md` | 进度追踪模板 |
| `assets/goal.template.yaml` | 目标定义模板 |
| `references/loop-engineering.md` | Loop Engineering 核心理念 |
| `references/runtime-kanban-v6.0.md` | v6.0 运行时详解 |
| `references/v6.0-upgrade.md` | v5.1 → v6.0 迁移指南 |
| `references/post-mvp-audit-checklist.md` | Post-MVP 审计清单（含 v6.0 检查项） |

### 🔄 修改文件

| 文件 | 变化 |
|------|------|
| `assets/gates.template.json` | 新增 `version`, `mode`, `checkpoint` 字段，支持 inner_loop 配置 |
| `assets/workflow_state.template.yaml` | 新增 `inner_loop_state` 块，支持迭代状态追踪 |

### 🎯 适用场景

- ✅ 探索性项目（0→1，需求模糊）
- ✅ 技术选型不确定（需要对比 3+ 方案）
- ✅ 快速验证（MVP 优先，完美主义后移）
- ✅ 需要自动化决策分级（减少人工干预）

### ⚠️ 向后兼容性

- 完全兼容 v5.1 的所有文件
- 可通过 `harness-rules.yaml` 退化为 v5.1 行为（所有决策设为 high risk）
- 现有项目可平滑迁移，参考 `references/v6.0-upgrade.md`

### 📚 参考资源

- Martin Fowler, "On the Loop" (2024)
- Addy Osmani, "AI-Assisted Engineering at Google" (2025)
- Boris Cherny, "Worktrees: The Missing Primitive" (2025)
- Peter Steinberger, "Sub-agent Orchestration Patterns" (2025)

---

## 5.0.0 — 2026-06-11

- Super Developer pipeline: add ship, operate, grow stages
- Merge product-orchestrator G1/G2/G3 gates into stage table
- Cross-platform: Cursor, Hermes, OpenCode (Platform notes)
- Borrowed skills: phuryn PM frameworks + knowledge-work eng/ops/data
- Replace hardcoded paths with `{PROJECT_ROOT}` / `{SKILLS_ROOT}`
- command-recipes.md for non-Claude slash workflows
- gates.template.json v5 schema

## 3.0.0 — 2026-06-07

- Merge V2 (7 stages, industry skills, self-evolution) with v2.1 (GitHub Pages per idea)
- Add `pm-aligner` stage with grill-me / grill-with-docs
- Add openspec, open-design, ui-ux-pro-max skill bindings
- Add superpowers chain for pm-builder
- Extend validate-gates.py: align, prototype, evolution retro gates
- Add pipeline-knowledge/ and feedback.jsonl schema

## 2.1.0 — 2026-06-07

- GitHub repo + Pages per idea at `D:/workspace/projects/pm-{slug}/`
- pm-git-publish skill integration

## 2.0.0 — (planned, superseded by 3.0.0)

- Original V2 design document; implemented as 3.0.0
