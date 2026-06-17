# Brownfield Pipeline Audit & Align (v7.1 强化版)

How to bring an existing pm-{slug} project into compliance with the current pipeline version. Discovered during pm-knowledge-platform v6.2 alignment (2026-06-13), enhanced with v7.1 forced audit protocol.

## When to Use

- Resuming work on a project started with an older pipeline version
- After a pipeline upgrade (e.g., v6.0 → v6.2 → v7.1)
- When `check_docs_ssot.py` reports governance warnings
- User asks to "review" or "audit" a project against the pipeline
- **v7.1 新增**：用户说"优化"、"重构"、"E2E"、"深入分析"时，**必须**先执行棕地审计

## v7.2 新增：外部仓库 Clone 意图

当 `00-brief.md` 或用户消息同时包含 **GitHub URL / `[owner/repo]`** 与 **clone / 导入 / 新开项目** 时：

| 禁止 | 必须 |
|------|------|
| ADR 写「align 阶段不 clone」 | align 只定范围；**clone 在 import/mvp 任务执行** |
| `00-brief.md` 非目标写「不实际 clone」 | brief 非目标可写「不在 align 阶段改代码」，但 **不能否定后续 clone** |
| 跳过 `04-mvp/` 代码分析 | clone 完成后 research/analysis 必须基于真实代码 |

**反合理化**：「align 只做文档」≠「永远不碰代码」。用户明确要求 clone 时，MVP/import worker 负责 `git clone` 到 `{PROJECT_ROOT}/04-mvp/`。

## v7.1 新增：强制审计协议

**触发条件**：用户消息包含以下关键词时，**必须**先执行棕地审计，再开始优化工作：
- 优化、重构、E2E、端到端、深入分析、改进、审查、审计

**审计流程**（不可跳过）：

### Step 0: 构建验证（阻塞性检查）

```bash
# 1. 检查 GitHub 版本是否能构建成功
cd {PROJECT_ROOT}
pnpm install
pnpm build

# 2. 如果构建失败，记录错误到 feedback.jsonl
# 3. 修复构建错误（优先级最高）
# 4. 重新构建验证
```

**反合理化表格**：

| 常见借口 | 反驳 |
|---------|------|
| "先优化再修复构建" | ❌ 构建失败是阻塞性问题。无法构建 = 无法部署 = 无法验证。 |
| "构建错误不重要" | ❌ 构建错误会导致后续所有工作白费。先确保基础可用。 |
| "用户不关心构建" | ❌ 用户关心最终可用性。无法构建 = 无法交付。 |

### Step 0.5: 浏览器现状记录

```bash
# 1. 浏览器访问当前部署（如果有）
browser_navigate {DEPLOY_URL}

# 2. 截图记录现状
browser_vision "记录当前页面状态"

# 3. 检查浏览器控制台错误
browser_console "检查 JS 错误"

# 4. 记录问题到 feedback.jsonl
```

**目的**：建立基线，用于后续对比优化效果。

## Step 1: Run Full Diagnostics

Run all three checks in parallel to get the gap picture:

```bash
# 1. Cross-document consistency
python {SKILLS_ROOT}/scripts/check_docs_ssot.py --project-root {PROJECT_ROOT} --json

# 2. Per-stage gate validation (loop all stages)
for stage in brief align research analysis spec mvp ship operate grow retro; do
  python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/validate-gates.py \
    --stage $stage --run {PROJECT_ROOT}
done

# 3. Governance artifact inventory
for f in goals/mvp.yaml goals/ship.yaml goals/retro.yaml \
         PROGRESS.md harness-rules.yaml feedback.jsonl \
         debates/ RUNBOOK.md 07-ops-notes.md 06-growth.md \
         evolution-notes.md harness-improvements.md; do
  [ -e "{PROJECT_ROOT}/$f" ] && echo "✅ $f" || echo "❌ $f"
done
```

## Step 2: Classify Gaps

| Gap Type | Examples | Priority |
|----------|---------|----------|
| **Governance missing** | No goals/, no harness-rules.yaml, no PROGRESS.md | P0 — blocks all gate checks |
| **Debate missing** | No debates/ directory for align/spec stages | P0 — blocks G1/G2 gates |
| **Stage artifact missing** | No RUNBOOK.md, no 07-ops-notes.md | P1 — blocks specific stage gates |
| **Doc conflict** | decisions.md says PostgreSQL, code uses SQLite | P1 — docs-hygiene error |
| **Content too thin** | CONTEXT.md < 50 lines, retro < 50 lines | P2 — min_lines checks |
| **Status outdated** | PRODUCT-DESIGN.md says "待部署" but already deployed | P2 — accuracy |

## Step 3: Create Governance Artifacts (Batch)

Create all missing governance files in one batch using `execute_code`:

### Required files and their minimum content:

| File | Key Content | Template Source |
|------|-------------|-----------------|
| `goals/{stage}.yaml` | Stage-specific verifiable goals with check types | `assets/goal.template.yaml` |
| `harness-rules.yaml` | Runtime commands, risk levels, inner_loop config | `assets/harness-rules.template.yaml` |
| `PROGRESS.md` | Stage status table, current task, inner loop history | `assets/progress.template.md` |
| `feedback.jsonl` | Initial entry documenting the audit itself | Free-form JSONL |
| `debates/{stage}-synthesis.md` | Debate topics, pros/cons, conclusion, `debate_resolved` marker | Free-form markdown |

### Critical: debates/ files MUST contain `debate_resolved`

The validate-gates.py checks for this exact string (or `辩论已解决`). Without it, G1/G2 gates fail even if the debate files exist.

```markdown
## 结论
[decision and reasoning]

debate_resolved
```

## Step 4: Fix Cross-Document Conflicts

The most common conflict: **database technology**. Projects often have:
- `decisions.md` saying one thing (the SSOT)
- `PRODUCT-DESIGN.md` saying another (often more nuanced)
- `DEPLOYMENT.md` reflecting actual implementation

**Fix strategy**: Make all documents consistent with decisions.md as SSOT. If the actual implementation differs from the original decision (e.g., decided PostgreSQL but using SQLite), update decisions.md to reflect reality AND add the nuance to all other docs.

**check_docs_ssot.py smart detection**: The tech-stack conflict check only flags when documents have genuinely different single-tech claims. If all docs mention both "SQLite + PostgreSQL", that's consistent (not a conflict).

## Step 5: Update PRODUCT-DESIGN.md Status

Common stale status patterns to fix:
- "待部署" → already deployed
- "P0 需立即修复" → already fixed
- "LLM 未配置" → already configured and verified
- Version roadmap showing "⚠️ 待验证" → "✅ 已验证"

## Step 6: Re-verify

Re-run Step 1 diagnostics. Target:
- `check_docs_ssot.py`: `ok: true` (0 errors)
- `validate-gates.py`: all 10 stages `all_passed: true`
- Governance artifacts: all present

## Common Pitfalls

1. **03b-user-journey.md content pattern mismatch**: The spec gate checks `用户故事|user stor|验收标准|acceptance` against ALL spec files including user-journey. If user-journey doesn't contain these terms, add a cross-reference line at the top.

2. **goals/*.yaml format**: Use the simple YAML format that goal-check.py's fallback parser handles. Avoid complex YAML features (anchors, multi-line strings). Each goal needs: `id`, `description`, `type`, and type-specific fields.

3. **RUNBOOK.md required sections**: v6.2 checks for three specific content patterns:
   - Deploy: `部署|deploy|步骤|step`
   - Rollback: `回滚|rollback`
   - Monitor: `监控|monitor|告警|alert`
   All three MUST be present as section headers or content.

4. **Retro quantitative requirements**: v6.2 retro gate checks for:
   - Metrics data: `指标|metric|数据|data|统计|stat`
   - Iteration analysis: `迭代|iteration|循环|loop`
   Include both in 05-retro.md.

5. **operate stage requires 07-ops-notes.md**: This file was not required before v6.2. If missing, create it with monitoring, alerting, SLA, and incident response content.

## Estimated Effort

| Project State | Typical Time | Tool Calls |
|---------------|-------------|------------|
| All governance missing | ~15 min | 20-30 |
| Only debates missing | ~5 min | 5-10 |
| Only doc conflicts | ~5 min | 5-10 |
| Full audit + align | ~20 min | 30-40 |
