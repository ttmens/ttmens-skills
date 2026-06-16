# Agent Entry — ttmens-skills v7.2.0

> 设计思想与能力全景：[README.md](README.md)  
> **系统架构**：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)  
> **首次使用 / 安装 / 分平台自检**：[docs/AGENT_ONBOARDING.md](docs/AGENT_ONBOARDING.md)

## 0. 启动检查（技能未装时先做）

1. 运行 `python {SKILLS_ROOT}/scripts/detect_agent_env.py --json`（或按 [AGENT_ONBOARDING.md §2](docs/AGENT_ONBOARDING.md#2-解析-skills_root) 解析 `{SKILLS_ROOT}`）
2. 若 `install_needed: true` → 请用户执行 [§3 安装](docs/AGENT_ONBOARDING.md#3-安装技能缺失时) 或 Agent 在授权下执行
3. 运行 `python {SKILLS_ROOT}/scripts/validate_skills.py` 确认通过
4. spec 阶段前确认已装 `--profile debate`（G2 红队）

## 1. 默认行为

- **加载流水线**：`pm-idea-to-mvp` v7.2.0（[`pipelines/pm-idea-to-mvp/SKILL.md`](pipelines/pm-idea-to-mvp/SKILL.md)）
- **唯一 live 入口**：`pipelines/pm-idea-to-mvp/`（勿使用 `v6.1.0/` 快照目录）
- **触发语**：从想法做到上线 · 继续 pm-{slug} · 优化现有产品 · 进入 {stage} 阶段
- **路径变量**：`{PROJECT_ROOT}` = pm-{slug} 仓库根；`{SKILLS_ROOT}` = 技能库根（**勿硬编码绝对路径**）

## 2. 阶段协议（强制）

1. 只写**当前 stage** 的产物（见 stage 表）
2. 阶段结束前运行：

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py \
  --project-root {PROJECT_ROOT} --stage <stage> --verify-goals
```

3. exit 非零 → 修复后重试，**不得**标记完成或进入下一阶段
4. MVP 使用 `inner-loop-driver.py` 内循环（max 3 iter）

## 3. 质量门

| Gate | 何时 | 关键技能 / 验证 |
|------|------|-----------------|
| G1 | align 结束 | `grill-me` § Debate Protocol → `debates/align-synthesis.md` |
| G2 | spec 结束 | `prd-red-team-panel` → `debates/spec-synthesis.md` |
| G3 | mvp/ship | `ui-acceptance-review` + `ui_acceptance.py --full` + 浏览器 E2E（ship 强制） |

## 4. Stage → Skill 速查

SSOT：[`pipelines/pm-idea-to-mvp/stage-skills.yaml`](pipelines/pm-idea-to-mvp/stage-skills.yaml)

| Stage | Native | Borrowed |
|-------|--------|----------|
| brief | — | — |
| align | grill-me, grill-with-docs | pm-identify-assumptions-new |
| research | — | pm-opportunity-solution-tree, pm-competitor-analysis, pm-market-sizing |
| analysis | c4-architecture, openspec, docs-hygiene | pm-product-strategy, kw-system-design |
| spec | user-journey, open-design, ui-ux-pro-max, prd-red-team-panel | pm-create-prd, pm-user-stories |
| mvp | writing-plans, subagent-driven-development, test-driven-development, ui-acceptance-review, requesting-code-review, dogfood | kw-testing-strategy |
| ship | ui-acceptance-review, docs-hygiene | pm-shipping-artifacts, pm-intended-vs-implemented, kw-deploy-checklist, pm-security-audit-static |
| operate | — | kw-incident-response, kw-runbook, pm-sql-queries |
| grow | — | pm-north-star-metric, pm-gtm-strategy |
| retro | pm-git-publish | pm-retro, pm-release-notes |

## 5. 语言

面向用户产物 → **简体中文**。代码 / URL / goal YAML 键 → 英文可。

## 6. 索引

- 安装与平台：[docs/AGENT_ONBOARDING.md](docs/AGENT_ONBOARDING.md)
- 技能全表：[docs/SKILLS_CATALOG.md](docs/SKILLS_CATALOG.md)
- 目录布局：[docs/REPO_LAYOUT.md](docs/REPO_LAYOUT.md)
- 行为准则：[agent-behavior-code.md](pipelines/pm-idea-to-mvp/references/agent-behavior-code.md)
- Prompt 链：[command-recipes.md](pipelines/pm-idea-to-mvp/references/command-recipes.md)
- 场景：[scenarios.yaml](scenarios.yaml)
