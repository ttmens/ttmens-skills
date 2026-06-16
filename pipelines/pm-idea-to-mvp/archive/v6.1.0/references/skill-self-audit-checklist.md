# Skill Self-Audit Checklist

> 用于验证流水线技能自身的文档-脚本一致性。在技能升级后、发布前执行。
> 与 `post-mvp-audit-checklist.md`（检查 MVP 产出质量）不同，本清单检查**流水线本身**的可靠性。

## 触发条件

- 技能版本升级后（如 v5.1 → v6.0）
- 新增/修改脚本后
- SKILL.md 大段重写后
- 用户报告脚本行为与文档不符时

## 审计步骤

### 1. 脚本存在性检查

验证 SKILL.md 中引用的所有脚本实际存在：

```bash
cd {SKILLS_ROOT}/pipelines/pm-idea-to-mvp
grep -oE "scripts/[a-z_-]+\.py" SKILL.md | sort -u | while read script; do
  [ -f "$script" ] && echo "✅ $script" || echo "❌ MISSING: $script"
done
```

**注意区分路径**：
- 流水线脚本：`pipelines/pm-idea-to-mvp/scripts/`
- 通用脚本：`D:/hermes-data/skills/scripts/`（如 check_docs_ssot.py, ui_acceptance.py）
- SKILL.md 中应明确标注哪些脚本不在流水线目录下

### 2. CLI 参数一致性检查

验证 SKILL.md 中的命令示例与实际 `--help` 输出一致：

```bash
cd scripts/
for f in validate-gates.py goal-check.py progress-tracker.py stage-complete.py; do
  echo "=== $f ==="
  python "$f" --help 2>&1 | head -20
done
```

**常见不一致模式**：
- SKILL.md 写 `--update` 但实际是子命令 `update`
- SKILL.md 写 `--runtime-only` 但脚本不支持该参数
- SKILL.md 缺少必填参数如 `--project-root`
- 参数名拼写差异（`--run` vs `--project-root`）

### 3. 模板与参考文档完整性

```bash
# 检查模板
grep -oE "assets/[a-z_.-]+\.template\.(yaml|json|md)" SKILL.md | sort -u | while read tmpl; do
  [ -f "$tmpl" ] && echo "✅ $tmpl" || echo "❌ MISSING: $tmpl"
done

# 检查参考文档
grep -oE "references/[a-z_.-]+\.md" SKILL.md | sort -u | while read ref; do
  [ -f "$ref" ] && echo "✅ $ref" || echo "❌ MISSING: $ref"
done
```

### 4. 端到端集成测试

用临时目录模拟真实项目，验证脚本协同工作：

```bash
TMPDIR=$(mktemp -d)
echo "# Test" > "$TMPDIR/00-brief.md"
mkdir -p "$TMPDIR/goals"
cat > "$TMPDIR/goals/brief.yaml" << 'EOF'
stage: brief
goals:
  - id: B1
    description: "Brief exists"
    type: file_exists
    target: "00-brief.md"
EOF

# 测试各脚本
python scripts/validate-gates.py --run "$TMPDIR" --stage brief --goal
python scripts/goal-check.py --stage brief --project-root "$TMPDIR"
python scripts/progress-tracker.py --project-root "$TMPDIR" init
python scripts/progress-tracker.py --project-root "$TMPDIR" show

rm -rf "$TMPDIR"
```

**期望**：所有脚本退出码 0，JSON 输出中 `all_passed: true` 或 `status: ok`。

### 5. 业界对标检查

验证技能是否覆盖了目标方法论的核心概念：

```bash
# Loop Engineering 6 原语覆盖率
echo "Automations:" && grep -c "validate-gates\|goal-check\|progress-tracker\|stage-complete" SKILL.md
echo "Worktrees:" && grep -c "04-mvp\|worktree" SKILL.md
echo "Skills:" && grep -c "grill-me\|c4-architecture\|user-journey" SKILL.md
echo "Connectors:" && grep -c "Feishu\|GitHub\|Kanban" SKILL.md
echo "Sub-agents:" && grep -c "pm-aligner\|pm-researcher\|pm-builder" SKILL.md
echo "Memory:" && grep -c "CONTEXT.md\|feedback.jsonl\|PROGRESS.md" SKILL.md
```

**期望**：每个原语至少 10 次引用。低于 5 次说明覆盖不足。

### 6. 脚本语法检查

```bash
cd scripts/
for f in *.py; do
  python -m py_compile "$f" 2>&1 && echo "✅ $f" || echo "❌ $f"
done
```

## 审计结果模板

```markdown
## Self-Audit Report — v{VERSION}

日期：{DATE}
审计员：{AGENT}

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 脚本存在性 | ✅/❌ | |
| CLI 参数一致性 | ✅/❌ | |
| 模板完整性 | ✅/❌ | |
| 参考文档完整性 | ✅/❌ | |
| 端到端集成 | ✅/❌ | |
| 业界对标 | ✅/❌ | |
| 语法检查 | ✅/❌ | |

发现问题：
1. ...
2. ...

修复记录：
1. ...
2. ...
```

## 已知陷阱

1. **子命令 vs 参数**：progress-tracker.py 使用子命令（init/update/show/resume），不是 `--update` 参数。SKILL.md 中的命令示例必须匹配。

2. **路径混淆**：check_docs_ssot.py 和 ui_acceptance.py 位于 `SKILLS_ROOT/scripts/`，不在流水线目录下。SKILL.md 应明确标注。

3. **参数别名**：validate-gates.py 同时支持 `--run` 和 `--project-root`，但 stage-complete.py 只支持 `--project-root`。文档应统一。

4. **可选参数缺失**：goal-check.py 的 `--runtime-only` 是后加的，旧版 SKILL.md 可能未提及。升级后需检查。

5. **YAML 解析**：goal-check.py 有内置 YAML 解析 fallback，但复杂 YAML（嵌套列表、多行字符串）可能解析失败。测试时使用简单格式。
