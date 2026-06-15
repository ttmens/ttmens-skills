# 流水线自检清单（Self-Inspection Checklist）

> 适用于 pm-idea-to-mvp 这类多脚本、多模板、多 reference 的复合型流水线技能。
> 在以下时机运行：大版本升级后、连续 3 次 pipeline 运行后、用户报告"流水线行为与预期不符"时。

## 检查维度（5 层）

### Layer 1: 脚本存在性 & 语法

```bash
# 所有 SKILL.md 中引用的脚本是否都存在
grep -oE "scripts/[a-z_-]+\.py" SKILL.md | sort -u | while read s; do
  [ -f "$s" ] && echo "✅ $s" || echo "❌ MISSING: $s"
done

# 所有脚本语法检查
for f in scripts/*.py; do python -m py_compile "$f" && echo "✅ $f" || echo "❌ $f"; done
```

**常见陷阱**：SKILL.md 引用 `scripts/check_docs_ssot.py` 但该脚本实际在 `SKILLS_ROOT/scripts/`（共享脚本目录）而非 pipeline 自身的 `scripts/` 目录。区分方法：共享脚本服务于多个技能，pipeline 脚本只服务于本流水线。

### Layer 2: 参数一致性

SKILL.md 中描述的命令参数必须与实际脚本的 `--help` 输出一致。

```bash
# 对每个脚本，比对 SKILL.md 描述 vs 实际 --help
for script in validate-gates goal-check progress-tracker stage-complete; do
  echo "=== $script.py ==="
  python scripts/$script.py --help 2>&1
  # 人工比对 SKILL.md 中的命令示例
done
```

**常见陷阱**：
- SKILL.md 写 `--update` 但实际是子命令 `update`（argparse subparser vs flag）
- SKILL.md 写 `--runtime-only` 但脚本未实现该参数
- SKILL.md 省略了 `--project-root` 等必填参数

### Layer 3: 模板 & Reference 完整性

```bash
# 模板文件
grep -oE "assets/[a-z_.-]+\.template\.(yaml|json|md)" SKILL.md | sort -u | while read t; do
  [ -f "$t" ] && echo "✅ $t" || echo "❌ MISSING: $t"
done

# Reference 文档
grep -oE "references/[a-z_.-]+\.md" SKILL.md | sort -u | while read r; do
  [ -f "$r" ] && echo "✅ $r" || echo "❌ MISSING: $r"
done
```

### Layer 4: 端到端集成测试

用临时目录模拟一个最小项目，跑通核心脚本链：

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

# 链式验证
python scripts/validate-gates.py --run "$TMPDIR" --stage brief --goal
python scripts/goal-check.py --stage brief --project-root "$TMPDIR"
python scripts/progress-tracker.py --project-root "$TMPDIR" init
python scripts/progress-tracker.py --project-root "$TMPDIR" show
rm -rf "$TMPDIR"
```

### Layer 5: 业界对标

对 Loop Engineering 6 核心原语逐项检查 SKILL.md 覆盖度：

| 原语 | 检查方式 |
|------|---------|
| Automations | grep 脚本引用次数（应 >10） |
| Worktrees | grep worktree/隔离目录引用 |
| Skills | grep 绑定技能名称 |
| Connectors | grep 外部系统名称（Feishu/GitHub/Kanban） |
| Sub-agents | grep profile 角色名称 |
| Memory | grep 持久化文件名称 |

## 修复优先级

1. **P0 — 脚本不存在或语法错误**：流水线完全无法运行
2. **P0 — 参数不一致**：agent 按 SKILL.md 执行会报错
3. **P1 — 模板/reference 缺失**：decompose 阶段会失败
4. **P2 — 业界对标缺失**：功能可用但方法论不完整

## 修复后的验证循环

```
修复 → py_compile → 端到端测试 → 同步到 ttmens-skills 仓库 → git commit
```

**注意**：修复 SKILL.md 后必须同步修复对应的脚本文件（如添加缺失参数），然后两个文件一起同步到 `D:/workspace/ttmens-skills/pipelines/pm-idea-to-mvp/`。
