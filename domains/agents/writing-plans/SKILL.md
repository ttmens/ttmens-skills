---
name: writing-plans
description: >-
  Break design docs into bite-sized implementation tasks with acceptance criteria.
  Use after design/grill passes and before build phase in idea-to-product workflow.
version: 1.0.0
author: ttmens
license: MIT
---

# Writing Plans

将设计方案拆解为 **2–5 分钟可完成** 的原子任务。对标 stock-copilot Phase B 计划粒度。

## When to use

- G2 设计方案已 approved
- 需要生成 `docs/plans/YYYY-MM-DD-*.md`
- 用户说「写实现计划」「拆任务」

## Step 1: Read inputs

读取：
- `docs/design.md` 或 `docs/plans/YYYY-MM-DD-phase-X.md`
- `docs/workflow_state.yaml` → `target_phase`
- `workflow/idea-to-product/assets/acceptance-matrix.template.md`

## Step 2: Write plan structure

```markdown
# [Phase/Feature] 实施方案

**Goal:** 一句话目标
**Architecture:** 2-3 句架构说明
**Tech Stack:** 实际技术栈

## 验收矩阵

| 域 | 标准 | 自动化 |
|----|------|--------|
| functional | ... | pytest / self_check |
| ux | ... | ui_acceptance.py |
| ops | ... | RUNBOOK |

### Task N: [标题]

**Objective:** ...
**Files:** Create/Modify/Test paths
**Step 1:** ...
**Step 2:** ...
**验收:** 本任务完成条件
```

## Step 3: Task sizing rules

- 每个 Task = 一个 focused commit 粒度
- 每个 Task 末尾有 **可验证** 的 Step（命令或手动检查）
- UI 任务必须引用 `docs/DESIGN.md` token，禁止 inline style 漂移
- 后端任务必须含测试文件路径

## Step 4: Save and update state

1. 保存到 `docs/plans/YYYY-MM-DD-<slug>.md`
2. 更新 `workflow_state.yaml` → `current_phase: plan`
3. **自动进入 build**，不问用户

## Step 5: Hand off to subagent-driven-development

计划写完后立即加载 `subagent-driven-development`，按 Task 顺序执行。
