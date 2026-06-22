# Loop Engineering 优化落地计划

**基于 Samuel McDonnell 文章 + 业界最佳实践**  
**日期**: 2026-06-22  
**版本**: v9.2.0

---

## 🎯 核心目标

将 pm-idea-to-mvp 技能从"双循环框架"升级为"4 层循环架构 + 双层验证 + 自进化系统"。

---

## 📋 优化清单（9 项）

### 1. Meta-Verification Gate（验证器的验证）

**问题**: 当前 5 维度质量门没有自我验证机制  
**方案**: 增加第 6 维度"验证器健康度"

**实施**:
```markdown
## 6. 验证器健康度（Meta-Verification）
- 质量门本身是否被测试过？
- 是否有假阳性/假阴性案例？
- 验证器是否随项目演进更新？
- 通过标准：0 未测试的质量门
```

**产物**: `verification-gate-health.md`

---

### 2. 双层验证架构

**问题**: 当前只有确定性验证（lint/build/test），缺少 LLM 验证器  
**方案**: 分离"改进层"和"硬停止层"

**实施**:
```markdown
## 双层验证架构

### Layer 1: LLM 验证器（改进层，概率性）
- 角色：改进草稿，提供语义级反馈
- 工具：`ui-acceptance-review`（LLM 判断）
- 输出：改进建议（非硬停止）

### Layer 2: 确定性验证（硬停止层，确定性）
- 角色：最终发货门
- 工具：lint/build/test/browser-e2e
- 输出：PASS/FAIL（硬停止）

### 工作流
LLM 验证器改进草稿 → 确定性验证决定是否发货
```

**产物**: 更新 `references/agent-behavior-code.md`

---

### 3. 最优停止条件

**问题**: 固定 3 次迭代，缺少成本-质量权衡  
**方案**: 动态迭代 + 成本追踪

**实施**:
```markdown
## 最优停止策略

### 迭代次数决策树
- Iteration 1: 基础功能通过 → 继续
- Iteration 2: 边界情况覆盖 → 继续
- Iteration 3: 性能优化 → 评估
- Iteration 4+: 仍有问题 → 记录到 feedback.jsonl，人工介入

### 成本-质量曲线
- 记录每次迭代的 token 消耗
- 如果 Iteration N 的改进 < 10%，停止
- 如果总 token > 预算阈值，停止

### 产物
- `loop-cost-tracker.jsonl`
```

**产物**: `loop-cost-tracker.jsonl`

---

### 4. 外循环自动化

**问题**: feedback.jsonl 手动记录，缺少模式识别  
**方案**: 每 5 个项目自动分析

**实施**:
```markdown
## 外循环自动化

### 触发条件
- 每完成 5 个项目
- 或 feedback.jsonl 累积 20+ 条记录

### 自动化流程
1. 运行 `consume-feedback.py --pattern-detection`
2. 识别重复失败模式（≥3 次相似失败）
3. 生成新规则建议
4. 写入 `evolution-notes.md` 的 "Auto-Detected Patterns" 章节
5. 人工确认后，更新 `agent-behavior-code.md`

### 产物
- `auto-detected-patterns.md`
```

**产物**: 更新 `scripts/consume-feedback.py`

---

### 5. Token 成本追踪

**问题**: 缺少成本可见性  
**方案**: 记录每次循环的 token 消耗

**实施**:
```markdown
## Token 成本追踪

### 记录格式
```json
{
  "ts": "ISO8601",
  "project": "pm-{slug}",
  "stage": "mvp",
  "iteration": 1,
  "tokens_in": 50000,
  "tokens_out": 10000,
  "cost_usd": 0.15,
  "duration_seconds": 120
}
```

### 产物
- `loop-cost-tracker.jsonl`
- `cost-summary.md`（每项目汇总）
```

**产物**: `loop-cost-tracker.jsonl`

---

### 6. 4 层循环架构

**问题**: 当前只有 Agent Loop + Verification Loop（部分）  
**方案**: 明确区分 4 种循环类型

**实施**:
```markdown
## 4 层循环架构

### Loop 1: Agent Loop（自动化工作）
- 功能：模型重复调用工具直到任务完成
- 实现：MVP Inner Loop（Plan→Code→Test→Observe→Adjust）
- 产物：代码、测试、文档

### Loop 2: Verification Loop（确保质量）
- 功能：包装 Agent Loop，评分输出 vs 标准
- 实现：5 维度质量门 + Meta-Verification
- 产物：验证报告、改进建议

### Loop 3: Event-Driven Loop（规模化集成）
- 功能：事件触发代理运行（webhook、cron、新数据）
- 实现：`/goal` 命令 + cron jobs
- 产物：自动化工作流

### Loop 4: Hill Climbing Loop（自动化改进）
- 功能：分析生产 traces，自动重写 harness 配置
- 实现：外循环自动化（consume-feedback.py）
- 产物：更新的技能、规则、模板
```

**产物**: 更新 SKILL.md 的"设计哲学"章节

---

### 7. 验证器分类

**问题**: 不清楚哪些验证是概率性，哪些是确定性  
**方案**: 明确分类

**实施**:
```markdown
## 验证器分类

### 概率性验证（LLM 判断，可变）
- `ui-acceptance-review`（视觉规范）
- `prd-red-team-panel`（需求审查）
- `dogfood`（探索性测试）

### 确定性验证（硬停止，可重现）
- lint（代码质量）
- build（构建成功）
- test（测试通过）
- browser-e2e（端到端测试）
- security-audit（安全扫描）

### 原则
- 概率性验证用于改进
- 确定性验证用于发货
- 两者结合：LLM 改进 → 确定性决定
```

**产物**: 更新 `references/agent-behavior-code.md`

---

### 8. 深度交互测试（已实现 ✅）

**当前状态**: 已实现，无需改进

---

### 9. 自进化机制（已实现 ✅，可增强）

**当前状态**: feedback.jsonl + evolution-notes.md  
**增强方案**: 自动模式识别（见第 4 项）

---

## 🚀 实施顺序

### Phase 1: 核心增强（优先级 P0）
1. ✅ Meta-Verification Gate
2. ✅ 双层验证架构
3. ✅ 验证器分类

### Phase 2: 成本优化（优先级 P1）
4. ✅ 最优停止条件
5. ✅ Token 成本追踪

### Phase 3: 自动化（优先级 P2）
6. ✅ 外循环自动化
7. ✅ 4 层循环架构文档化

---

## 📦 产物清单

### 新增文件
- `verification-gate-health.md`
- `loop-cost-tracker.jsonl`
- `cost-summary.md`
- `auto-detected-patterns.md`

### 更新文件
- `SKILL.md`（v9.1.0 → v9.2.0）
- `references/agent-behavior-code.md`
- `scripts/consume-feedback.py`

---

## 📊 成功标准

| 指标 | 当前 | 目标 |
|------|------|------|
| 验证器覆盖率 | 5 维度 | 6 维度（+Meta） |
| 停止策略 | 固定 3 次 | 动态 + 成本追踪 |
| 外循环自动化 | 手动 | 每 5 项目自动分析 |
| 成本可见性 | 无 | 每次循环追踪 |
| 循环架构 | 2 层 | 4 层 |

---

## 🔄 回滚计划

如果优化引入问题：
1. 保留 v9.1.0 的 SKILL.md 备份
2. 新增文件可删除
3. 更新文件可 git revert

---

**下一步**: 开始实施 Phase 1（Meta-Verification + 双层验证 + 验证器分类）
