# Post-MVP 审计检查清单

> 在 MVP 阶段完成后、进入 Ship 阶段前，执行此检查清单确保 MVP 质量达标

## 1. 代码质量

- [ ] 所有 Python 文件通过 `py_compile` 编译
- [ ] `flake8` 检查无严重错误（max-line-length=120）
- [ ] 无硬编码密钥或敏感信息
- [ ] 依赖列表完整（requirements.txt / package.json）
- [ ] README.md 包含安装和运行说明

## 2. 测试覆盖

- [ ] 核心功能有单元测试
- [ ] 测试通过率 ≥ 90%
- [ ] 测试可重复执行（无随机失败）
- [ ] 测试运行时间 < 60 秒

## 3. 运行时验证（v6.0 新增）

- [ ] `pytest -q --tb=short` 全部通过
- [ ] `python -m py_compile **/*.py` 无错误
- [ ] `python -m flake8 --max-line-length=120` 无错误
- [ ] 所有 runtime 命令在 `04-mvp/` 目录下执行成功

### 3.1 Runtime 验证命令

```bash
cd 04-mvp

# 测试
pytest -q --tb=short
# 期望：全部通过，退出码 0

# 编译检查
python -m py_compile **/*.py
# 期望：无输出，退出码 0

# Lint 检查
python -m flake8 --max-line-length=120
# 期望：无输出，退出码 0
```

## 4. Inner Loop 检查（v6.0 新增）

- [ ] Inner loop 迭代次数 ≤ 3
- [ ] 每次迭代都有记录在 `PROGRESS.md` 的内循环日志中
- [ ] 最后一次迭代所有 feedback_signals 通过
- [ ] 无 backtrack 记录（如果有，检查 backtrack 原因是否合理）

### 4.1 Inner Loop 日志检查

```bash
# 查看迭代次数
grep '内循环迭代' PROGRESS.md
# 期望：内循环迭代 | N/3，其中 N ≤ 3

# 查看迭代详情
grep -A 20 '内循环日志' PROGRESS.md
# 期望：每次迭代都有 时间、触发信号、结果、决策
```

## 5. PROGRESS.md 完整性（v6.0 新增）

- [ ] `PROGRESS.md` 存在且非空
- [ ] 元信息表完整（Slug, 创建时间, 最后更新, 当前阶段, 内循环迭代）
- [ ] 阶段进度 checkbox 正确（已完成阶段标记为 [x]）
- [ ] 当前阶段标记为 `← current`
- [ ] MVP 任务明细表已填充
- [ ] 内循环日志至少有 1 条记录

### 5.1 PROGRESS.md 验证

```bash
# 检查文件存在
test -f PROGRESS.md && echo "✓ PROGRESS.md exists"

# 检查元信息
grep -E 'Slug|创建时间|最后更新|当前阶段|内循环迭代' PROGRESS.md

# 检查阶段进度
grep -E '^\- \[[ x]\] Stage' PROGRESS.md

# 检查内循环日志
grep -A 5 '内循环日志' PROGRESS.md
```

## 6. 架构一致性

- [ ] 代码结构符合 C4 Context 图
- [ ] 无未记录的架构决策（检查 DECISIONS.md）
- [ ] 技术栈符合 `harness-rules.yaml` 中的 `tech_stack` 定义
- [ ] 目录结构符合约定（04-mvp/src, 04-mvp/tests 等）

## 7. UX 验收

- [ ] UX-REVIEW.md 存在
- [ ] P0 问题数量 = 0
- [ ] P1 问题数量 ≤ 3
- [ ] 所有 P0/P1 问题有修复计划或已修复
- [ ] UI 截图或录屏已保存（如适用）

## 8. 文档完整性

- [ ] README.md 包含：项目简介、安装步骤、运行方法、技术栈
- [ ] API 文档（如有 API）
- [ ] 用户手册（如有 UI）
- [ ] 部署文档草稿（为 Ship 阶段准备）

## 9. 安全与合规

- [ ] 无已知安全漏洞（`safety check` / `npm audit`）
- [ ] 用户输入已验证和清理
- [ ] 敏感数据已加密或脱敏
- [ ] 符合隐私政策（如适用）

## 10. 性能基线

- [ ] 核心功能响应时间 < 2 秒
- [ ] 内存占用合理（无内存泄漏）
- [ ] 数据库查询有索引（如适用）
- [ ] 并发处理能力已测试（如适用）

## 11. Goal Check 验证（v6.0 新增）

运行 `goal-check.py mvp` 确保所有目标通过：

```bash
goal-check.py mvp
```

期望输出：
```
Checking goals for phase: mvp
────────────────────────────────────────
✓ M1: MVP directory and README exist
✓ M2: Tests pass (pytest -q --tb=short)
✓ M3: UX review with P0=0

Result: PASSED (3/3 goals met)
Action: Proceed to Ship stage
```

## 12. 审计结果

### 12.1 审计摘要

| 检查项 | 通过 | 失败 | 警告 |
|--------|------|------|------|
| 代码质量 | /5 | /5 | /5 |
| 测试覆盖 | /4 | /4 | /4 |
| 运行时验证 | /4 | /4 | /4 |
| Inner Loop | /4 | /4 | /4 |
| PROGRESS.md | /6 | /6 | /6 |
| 架构一致性 | /4 | /4 | /4 |
| UX 验收 | /5 | /5 | /5 |
| 文档完整性 | /4 | /4 | /4 |
| 安全与合规 | /4 | /4 | /4 |
| 性能基线 | /4 | /4 | /4 |
| Goal Check | /1 | /1 | /1 |
| **总计** | **/45** | **/45** | **/45** |

### 12.2 审计结论

- [ ] ✅ **通过**：所有检查项通过，可以进入 Ship 阶段
- [ ] ⚠️ **条件通过**：有警告但不阻塞，记录到 DECISIONS.md 后进入 Ship
- [ ] ❌ **失败**：有失败项，必须修复后重新审计

### 12.3 审计签名

| 角色 | 姓名 | 日期 | 签名 |
|------|------|------|------|
| 审计员 | | | |
| 项目负责人 | | | |
| 技术负责人 | | | |

## 13. 审计后行动

### 13.1 如果通过

1. 更新 `workflow_state.yaml`：`gates.g3_ship = 'passed'`
2. 更新 `PROGRESS.md`：标记 MVP 阶段为 `[x]`
3. 进入 Ship 阶段：`hermes "继续 pm-{slug}"`

### 13.2 如果失败

1. 记录失败原因到 `DECISIONS.md`
2. 修复失败项
3. 重新运行 `goal-check.py mvp`
4. 重新执行本检查清单

### 13.3 如果触发 Backtrack

如果审计发现设计缺陷（非代码缺陷），触发 backtrack 到 Spec 阶段：

1. 记录 backtrack 原因到 `DECISIONS.md`
2. 更新 `PROGRESS.md` 的 backtracking_log
3. 回退到 Spec 阶段：修改 `workflow_state.yaml` 的 `current_phase = 'spec'`
4. 保留 MVP 代码作为参考，但标记为 `deprecated`

## 14. 参考资源

- [runtime-kanban-v6.0.md](./runtime-kanban-v6.0.md) — Goal Check 详解
- [loop-engineering.md](./loop-engineering.md) — Inner Loop 协议
- [v6.0-upgrade.md](./v6.0-upgrade.md) — PROGRESS.md 格式说明
- [../assets/goal.template.yaml](../assets/goal.template.yaml) — Goal 定义模板
