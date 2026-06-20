# MVP Code+Test — Inner Loop iter 1-3 (v7.0)

**Profile**: `pm-builder` | **Stages**: `mvp-iter1`, `mvp-iter2`, `mvp-iter3`

## Chain

TDD → opencode → ui-acceptance-review (journey) → dogfood

Workdir: `{PROJECT_ROOT}/04-mvp`

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 5（范围纪律）**：只改 plan 中定义的文件，不"顺便"重构
- **准则 6（验证）**：每个 iter 必须以 inner-loop-driver.py observe (harness-rules.yaml) 结束

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "这个 iter 先跳过测试" | 没有测试的 iter 不算 iter |
| "测试通过了，不用跑 lint" | lint 是独立的验证维度 |
| "这个 bug 下个 iter 再修" | 当前 iter 的 bug 当前修。积累 = 雪崩 |
| "改动太多不好 revert，一起提交" | 原子提交。每个逻辑变更独立提交 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | 跳过测试直接写代码 | TDD 纪律崩溃 | test-driven-development 技能强制 |
| 2 | 一次改太多文件 | 无法审查 + revert 困难 | ≤5 文件/iter |
| 3 | 不运行 inner-loop observe | 不知道 iter 是否 PASS | 自动触发 |
| 4 | iter 3 还 FAIL 但不报告 | 问题被隐藏 | harness-improvements.md + 人工升级 |

## Exit (iter1/3 on final pass)

## Exit (mandatory)

Verify artifact paths from the main pipeline SKILL exist under `{PROJECT_ROOT}`.
Update `PROGRESS.md` stage status.
