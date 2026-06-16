# 跨平台工作流 Prompt（非 Slash Command）

Cursor、Hermes、OpenCode 均不支持 phuryn 的 `/discover` 等斜杠命令。将下列 prompt 粘贴到对话，或写入 Kanban task body。

## /discover 等效

```
对产品想法「{IDEA}」执行完整发现周期：
1. 加载 pm-opportunity-solution-tree：产出 OST（outcome → opportunities → solutions → experiments）
2. 加载 pm-identify-assumptions-new：列出 8 类风险假设
3. 按 Impact×Risk 排序，标出 Top 3  risky assumptions
4. 为 Top 3 各设计一个 lean experiment
每步完成后暂停，等我确认再继续。
产出写入 01-research.md 附录或单独 assumptions.md。
```

## /write-prd 等效

```
加载 pm-create-prd，基于 CONTEXT.md 和 02-analysis.md 撰写 8 段 PRD。
输出路径：03-prd.md（简体中文）。
同时加载 pm-user-stories 补充 INVEST 用户故事。
```

## /strategy 等效

```
加载 pm-product-strategy，产出 9 段 Product Strategy Canvas。
写入 02-analysis.md 的「战略」章节或 strategy.md。
```

## /ship-check 等效

```
加载 pm-shipping-artifacts、pm-intended-vs-implemented、kw-deploy-checklist、pm-security-audit-static：
1. 文档化架构、权限流、secrets、测试覆盖图
2. 审计「文档意图 vs 代码实现」差距（附证据）
3. 产出 deploy checklist 与 RUNBOOK.md
```

## /plan-launch 等效

```
加载 pm-gtm-strategy、pm-north-star-metric：
产出 06-growth.md（NSM、输入指标、GTM 摘要）。
```

## /red-team-prd 等效

```
加载 pm-strategy-red-team，对抗性审查 03-prd.md 与 02-analysis.md：
列出 load-bearing assumptions、失败条件、最便宜验证实验，按优先级排序。
```
