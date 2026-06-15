# 外部技能框架分析（供未来融合参考）

> 记录已分析的外部技能框架、融合决策、未采纳项。未来版本升级时先读此文件。

## 已分析框架

### 1. addyosmani/agent-skills（v7.0 已融合）

- **仓库**: github.com/addyosmani/agent-skills
- **Stars**: 56.3K | **作者**: Addy Osmani（前 Google Chrome DevRel，现 Anthropic）
- **分析日期**: 2026-06-15
- **核心模式**: 6 条行为准则 + 反合理化表格 + 5 轴 Code Review + 路由器决策树
- **融合状态**: ✅ v7.0 已融合以下模式：
  - 6 条不可协商准则 → `references/agent-behavior-code.md`
  - 反合理化表格 → 每个 stage card v7.0
  - 失败模式清单 → 每个 stage card v7.0
  - 5 轴 Code Review → `requesting-code-review` v3.0
  - 变更规模约束 → `agent-behavior-code.md` + code review
  - 路由器决策树 → `orchestrator.md` v7.0
- **未采纳项**:
  - `interview-me` / `idea-refine` — 与现有 `grill-me` 功能重叠
  - `context-engineering` — 与 Hermes 自带上下文管理重叠
  - `browser-testing-with-devtools` — 与 `dogfood` + `ui-acceptance-review` 重叠
  - Agent Personas（code-reviewer/test-engineer/security-auditor）— 与 Hermes kanban profiles 重叠

### 2. obra/superpowers（架构参考，未直接融合）

- **仓库**: github.com/obra/superpowers
- **Stars**: 224.7K | **作者**: Jesse Vincent (obra)
- **分析日期**: 2026-06-15
- **核心模式**: Subagent 分发架构 + 7 阶段强制流程 + 两阶段 Code Review
- **融合状态**: ⚠️ 架构层面已被 pm-idea-to-mvp v6.0 的 Inner Loop 吸收
- **差异点**: superpowers 是"执行框架"（解决"怎么执行"），agent-skills 是"工程标准"（解决"执行什么标准"）
- **未采纳项**:
  - Subagent per task — 与 Hermes kanban profile dispatch 重叠
  - 7 阶段强制 — 与现有 10 阶段流水线重叠（粒度更粗）
  - 视觉化脑图 — 非必需

### 3. mvanhorn/last30days-skill（信息源参考，未融合）

- **仓库**: github.com/mvanhorn/last30days-skill
- **Stars**: 未公开 | **定位**: 社交情报研究（Reddit/X/YouTube/HN/Polymarket）
- **分析日期**: 2026-06-15
- **融合状态**: ❌ 不融合（领域不同：社交情报 vs 开发流水线）
- **潜在集成点**: research 阶段可调用 last30days 做社交声量分析（需用户决定）

## 融合方法论（可复用）

```
1. web_search 定位仓库 + 获取 README/SKILL.md
2. web_extract 读取 raw SKILL.md（完整内容）
3. skill_view 加载现有技能，理解当前结构
4. 结构化对比（架构/哲学/功能/适用场景表格）
5. 差距分析（现有流水线缺什么？外部框架补什么？）
6. 优先级排序（P0 必融 / P1 应融 / P2 可选）
7. 批量执行（execute_code 批量写文件）
8. 自验证（文件存在性 + 内容一致性 + git 状态）
```

## 待分析框架（未来版本）

| 框架 | 方向 | 潜在价值 |
|------|------|---------|
| anthropics/skills (官方) | Claude Code 官方技能集 | 可能与 Hermes 技能格式对齐 |
| vercel/skills.sh | 技能市场（669K+ skills） | 质量参差不齐，需筛选 |
| aws/aws-agent-skills | AWS 部署专用 | 仅在 AWS 项目中有用 |
| jetpack-compose-skills | Android UI 专用 | 仅在 Android 项目中有用 |
