# Changelog

All notable changes to ttmens-skills are documented in this file.

## [v9.2.0] - 2026-06-23

### Added

- **4 层循环架构**：Agent Loop → Verification Loop → Event-Driven Loop → Hill Climbing Loop
- **最优停止策略**：动态迭代 + 质量收敛判断（替代固定 3 次迭代）
- **双层验证**：LLM 改进 + 确定性硬停止
- **核心洞察**：验证器才是产品，其他都是管道

### Changed

- **pm-idea-to-mvp**：v9.1.0 → v9.2.0
- **README.md**：全面升级设计思想章节，新增 DevOps 运维技能分类，更新架构图
- **docs/SKILLS_CATALOG.md**：修正 native 计数 17 → 18，补充 `remote-server-deployment`

### Architecture

- 从「双循环方法论」升级为「4 层循环架构」——方法论不变，执行层有了明确分层
- MVP 内循环支持动态迭代次数（质量收敛判断）

---

## [v9.1.0] - 2026-06-19

### Added

- **Ship 5 维度质量门**：视觉规范、组件结构、交互体验、移动端适配、上线把关
- **Stage 表格验收标准列**：每个 stage 增加明确的验收标准
- **DESIGN.md 输出**：Spec 阶段新增设计系统文档产出（Google Stitch 格式）
- **DESIGN.md 模板**：`references/design-md-template.md`，含颜色/字体/布局/组件/动效/响应式
- **Agent 编排原则**：默认单 Agent，仅两种情况拆子 Agent（独立审查、可并行）
- **第 7 条行为准则**：规则来自失败（Rules from Failures）
- **自进化机制增强**：信号收集 → 规则转化流程（5 步）→ 规则来源原则

### Changed

- **pm-idea-to-mvp**：v9.0.0 → v9.1.0
- **related_skills**：新增 `web-design-guidelines`（Vercel 100+ 规则审计）
- **Project directory**：DESIGN.md 从 `04-mvp/` 移至项目根目录（Spec 阶段产出）
- **Inner Loop 入口检查**：`DESIGN.md` 路径更新为项目根目录

### Architecture

- **Ship 质量门**：借鉴 web-design-guidelines（28K stars）+ impeccable（36.8K stars）
- **Goal 结构**：借鉴 PM 5.0 方法论（目标 + 完成标准 + 验收方式）
- **DESIGN.md**：借鉴 awesome-design-md（90K stars）Google Stitch 格式
- **自进化**：借鉴 PM 5.0 完整链路（Signal → 规则建议 → 人工确认 → 更新规则库）

---

## [v9.0.0] - 2026-06-19

### Removed

- **Kanban 编排系统**：删除 ~100 个编排脚本和配置文件
  - `# v9 removed: use init-project.py + SKILL.md stages`（任务分解）
  - `stage-complete.py`（阶段完成）
  - `validate-gates.py`（门禁验证）
  - `pipeline_notify.py`（通知系统）
  - `pm-e2e-smoke.py`（端到端自检）
  - `pipeline_observability.py`（可观测性）
  - 所有 `goals/*.yaml` 模板
  - 所有 `runtime-kanban-v*.md` 参考文档
  - `stage-skills.yaml` 配置
  - `command-recipes.md` 命令配方

- **Gateway 专用代码**（hermes-agent 侧）
  - `pm_pipeline.py`（PM 流水线编排）
  - `feishu_pipeline_cards.py`（飞书卡片）
  - `pm_kanban_guard.py`（看板守卫）

### Changed

- **pm-idea-to-mvp SKILL.md**：1,401 → 244 行
  - 聚焦双循环方法论（Why Loop + How Loop）
  - 移除脚本命令引用，改为产物路径验证
  - 保留 3 个核心脚本：`inner-loop-driver.py`, `init-project.py`, `consume-feedback.py`
  - 保留 13 个阶段卡片（hermes-stage-cards/*.md）
  - 保留 11 个模板文件（assets/*.template.yaml）

- **remote-server-deployment SKILL.md**：2,113 → 130 行
  - 拆分为核心技能 + 参考文档架构
  - 核心：部署概览、SSH 检查、Node.js 安装、PM2 基础
  - 参考文档：deployment-pitfalls.md, platform-specific.md, database-fallback.md 等

- **架构文档**
  - ARCHITECTURE.md：移除编排层引用，更新为技能驱动架构
  - AGENTS.md：移除 stage-complete.py 命令，改为产物路径验证
  - README.md：更新脚本列表为 4 个核心脚本

### Added

- **新参考文档**
  - `pm-idea-to-mvp/references/deployment-pitfalls.md`
  - `pm-idea-to-mvp/references/browser-e2e-verification.md`
  - `remote-server-deployment/references/no-sudo-stack.md`
  - `remote-server-deployment/references/flutter-android-sdk-setup.md`

### Architecture

- **从编排驱动 → 技能驱动**
  - 移除 Kanban 任务分解和阶段转换逻辑
  - 流水线由 SKILL.md 方法论驱动，Agent 自主执行
  - 保留通用 Kanban 基础设施（kanban.py, kanban_db.py）用于任务管理
  - Gateway 简化为通用消息路由，无 PM 专用代码

- **双循环保留**
  - Why Loop：brief → align → research → analysis → spec
  - How Loop：mvp → ship → operate → grow → retro
  - 三卡点：align（方向）、spec（规格）、ship（上线）

---

## [v7.2.0] - 2026-06-17

### Features

- 双卡点系统（align + ship）
- pipeline_notify.py 统一通知
- deploy 解耦（deploy_servers.py + ssh_preflight.py）
- 产物 SSOT（artifacts.manifest.template.yaml）
- E2E 自检（pm-e2e-smoke.py）
- 可观测性（pipeline_observability.py）

---

## Versioning

ttmens-skills follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes to pipeline architecture or skill structure
- **MINOR**: New features or skills (backward compatible)
- **PATCH**: Bug fixes or documentation updates
