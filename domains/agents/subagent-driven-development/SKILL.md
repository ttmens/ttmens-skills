---
name: subagent-driven-development
description: >-
  Execute implementation plans task-by-task with spec review and quality review
  between tasks. Use during build phase of product-orchestrator or idea-to-product.
version: 1.0.0
author: ttmens
license: MIT
---

# Subagent-Driven Development

按计划 **逐 Task 执行**，每个 Task 完成后做规格审查 + 质量审查，再进入下一 Task。

## When to use

- `docs/plans/*.md` 已存在且 G2 approved
- `workflow_state.yaml` → `current_phase: build`

## Execution loop

```
For each Task in plan:
  1. 实现 Task（仅改 Task Files 列出的路径）
  2. 规格审查：对照 Task Objective 与验收标准
  3. 质量审查：pytest / self_check / ui_acceptance --quick（若涉 UI）
  4. 修复直到通过
  5. commit（若用户在 git 仓库且要求 commit）
  6. 更新 workflow_state checkpoints
  7. 下一 Task
```

## Spec review checklist

- [ ] 实现覆盖 Task Objective 全部要点
- [ ] 未引入 plan 范围外的功能
- [ ] 架构变更已写入 `docs/DECISIONS.md`
- [ ] UI 变更已同步 `docs/DESIGN.md` → `src/site/theme.css`

## Quality review checklist

```bash
# 后端
python -m pytest tests/ -q --tb=short

# 全链路
python {SKILLS_ROOT}/scripts/self_check.py --project-root {PROJECT_ROOT}

# UI 改动
python {SKILLS_ROOT}/scripts/ui_acceptance.py --quick --project-root {PROJECT_ROOT} --profile auto
```

## UI change protocol

1. UI 改动前：保存 `docs/archive/YYYY-MM-DD-pre.html` 或截图
2. 改 `src/site/` → 确认 sync 到 `docs/`
3. 跑 `ui_acceptance.py --quick`
4. 完成后：保存 `-post` 快照

## Parallel tasks

无文件冲突的 Task 可用 Task 工具并行 subagent，但 **同一文件只允许一个 agent 修改**。

## Phase complete

全部 Task 通过后：

1. 跑完整 acceptance matrix（functional + ux + ops）
2. 更新 `workflow_state.yaml` → `current_phase: ship`
3. 若含 UI 变更 → 加载 `ui-acceptance-review` 跑 `--full`，触发 **G3**

## Blocker protocol

- 测试失败 → 修复，不跳过
- 外部 API 不可用 → 降级 + DECISIONS 记录，继续
- 连续 2 次同一 Task 失败 → 记录 blocker，尝试备选方案
