# 编码与 Agent 行为约定（Coding Conventions）

> **入口**：本文是编码/阶段协议的**单一索引**。  
> **部署**：见 [DEPLOY_CONVENTIONS.md](DEPLOY_CONVENTIONS.md)  
> **架构**：见 [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 1. 启动检查（Agent 第一件事）

1. 解析 `{SKILLS_ROOT}`：`python {SKILLS_ROOT}/scripts/detect_agent_env.py --json`
2. 若 `install_needed` → 按 [AGENT_ONBOARDING.md](AGENT_ONBOARDING.md) 安装
3. 运行 `python {SKILLS_ROOT}/scripts/validate_skills.py`
4. spec 前确认 `--profile debate`（G2 红队依赖）

详见根目录 [AGENTS.md](../AGENTS.md)。

---

## 2. 流水线协议（v9.1 产物驱动）

| 规则 | 说明 |
|------|------|
| **只写当前 stage** | 不得跳过或预写后续阶段产物 |
| **阶段完成 = 产物存在** | 验证 SKILL.md 目录结构中的路径，不靠自报 |
| **内循环** | MVP 用 `inner-loop-driver.py`，max 3 iter |
| **人工卡点** | **align + ship**（2 个）；spec 仅 G2 技能辩论，不占人工 unblock |

### 质量门

| Gate | 阶段 | 验证 |
|------|------|------|
| G1 | align | `grill-me` 辩论 → `debates/align-synthesis.md` |
| G2 | spec | `prd-red-team-panel` → `debates/spec-synthesis.md` |
| G3 | mvp/ship | `ui-acceptance-review` + 浏览器 E2E（ship 强制） |

**不再使用** `stage-complete.py`、`goal-check.py`、`validate-gates.py`（v9 已删除）。

---

## 3. 七条不可协商行为准则

全文：[agent-behavior-code.md](../pipelines/pm-idea-to-mvp/references/agent-behavior-code.md)

1. **假设前置** — 非平凡工作前显式列出假设
2. **主动管理困惑** — 不确定时 STOP，提问而非猜测
3. **必要时推回** — 反谄媚，量化风险
4. **强制简洁** — 抵抗过度工程
5. **范围纪律** — 只碰被要求的部分
6. **TDD 优先** — 业务逻辑 RED-GREEN-REFACTOR
7. **规则来自失败** — retro 信号 → 行为准则更新

---

## 4. 语言与产物

- 面向用户的文档、PRD、评审 → **简体中文**
- 代码、URL、YAML 键、Git 提交信息 → 英文可

---

## 5. Inner Loop 与 Subagent

| 场景 | 做法 |
|------|------|
| MVP 迭代 | `inner-loop-driver.py --project-root <path>` |
| 多任务实现 | `subagent-driven-development` 逐 Task |
| 计划拆分 | `writing-plans` → openspec tasks |
| 提交前 | `requesting-code-review` |

**Subagent 拆分条件**（v9.1）：默认单 Agent；仅 (1) 独立审查 (2) 可并行任务 时拆子 Agent。

---

## 6. 路径变量

| 变量 | 含义 |
|------|------|
| `{SKILLS_ROOT}` | ttmens-skills 或 `HERMES_HOME/skills` 根 |
| `{PROJECT_ROOT}` | `pm-{slug}` 仓库根 |
| `{HERMES_HOME}` | 如 `D:/hermes-data` |

**禁止**在技能正文中硬编码绝对路径（示例可用占位符）。

---

## 7. 相关文件

| 文件 | 内容 |
|------|------|
| [AGENTS.md](../AGENTS.md) | Agent 入口、Stage→Skill 表 |
| [pipelines/pm-idea-to-mvp/SKILL.md](../pipelines/pm-idea-to-mvp/SKILL.md) | 流水线 SSOT |
| [agent-behavior-code.md](../pipelines/pm-idea-to-mvp/references/agent-behavior-code.md) | 7 条准则 + 失败模式 |
| [hermes-stage-cards/](../pipelines/pm-idea-to-mvp/references/hermes-stage-cards/) | 各阶段卡片 |
| [templates/cursor/AGENTS.md](../templates/cursor/AGENTS.md) | Cursor 项目模板入口 |
