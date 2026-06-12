---
name: obsidian-deepen-review
description: "对 Obsidian 笔记进行深度处理：单篇笔记深化提问、多篇笔记聚合分析、自动生成周报/月报/主题复盘、MOC 内容地图导航页"
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [obsidian, deep-review, aggregation, weekly-report, moc, note-deepening, cli]
    related_skills: [obsidian]
---

# Obsidian 笔记深化与聚合

对 Obsidian 知识库进行**深度处理**。**优先使用 Obsidian 官方 CLI**（1.12.4+），CLI 不可用时退回到文件系统操作 + 脚本。

## 什么时候触发

| 用户说的话 | 触发操作 |
|-----------|----------|
| 「深化这篇笔记」「deepen」 | 对指定笔记生成批判性问题 |
| 「总结一下这个月的笔记」「月报」 | 按月聚合所有笔记生成月报 |
| 「生成周报」「weekly」 | 按周聚合所有笔记生成周报 |
| 「把关于 XX 的笔记汇总一下」 | 按标签/关键词聚合，生成主题复盘 |
| 「生成目录」「MOC」「内容地图」 | 自动扫描文件夹生成导航页 |

## 操作模式选择

**第一步：检测 CLI 是否可用**

```bash
obsidian --version 2>/dev/null && obsidian help 2>/dev/null | head -5
```

- **可用** → CLI 模式（优先）
- **不可用** → 文件系统 + 脚本模式

---

## 模式 A: Obsidian 官方 CLI（优先）

### CLI 核心命令

```bash
# 读取笔记
obsidian read "路径/笔记.md"

# 搜索笔记
obsidian search query="关键词"
obsidian search:context "关键词"
obsidian search:tag "#标签"

# 追加内容到笔记
obsidian append "路径/笔记.md" "追加内容"

# 列出文件
obsidian files
obsidian files:count
```

### 使用 CLI 深化笔记

```bash
# 读取目标笔记
obsidian read "路径/笔记.md"

# 搜索相关笔记
obsidian search:tag "#相关标签"
obsidian search query="关键词"
```

### 使用 CLI 聚合笔记

```bash
# 按日期范围搜索（如果 CLI 支持）
obsidian search query="" --after "2026-05-01" --before "2026-05-31"

# 按标签聚合
obsidian search:tag "#支付"
```

---

## 模式 B: 文件系统 + 脚本（CLI 不可用时）

## 核心操作

### 操作 1: 单篇笔记深化（Deepen）

**目标**：对已有笔记生成四类批判性问题，推动思考深化。

**流程**：

1. 读取目标笔记内容
2. 分析笔记的：核心论点、隐含假设、缺失视角、可行动的下一步
3. 在笔记末尾追加一个 `## 🤔 深化提问` 章节
4. 如果发现了相关的已有笔记，自动插入 `[[wikilink]]`

**深化提问模板**（追加到笔记末尾）：

```markdown
---

## 🤔 深化提问（YYYY-MM-DD）

### 🔴 批判性
- 这个观点的隐含假设是什么？如果假设不成立会怎样？
- 有什么反例可以挑战这个结论？

### 🔗 连接性
- [[相关笔记 1]] — 这篇笔记的 XX 观点和那篇的 YY 有什么关联？

### 🎯 行动性
- [ ] 验证 XX 观点在实际场景中的适用性

### 🔭 扩展性
- 进一步了解 ZZ 领域的研究
```

### 操作 2: 周报生成

**流程**：

1. 确定本周日期范围
2. 扫描 vault 中本周创建/修改的所有 `.md` 文件
3. 按类别聚合：完成任务、会议、阅读、决策、想法
4. 生成周报

### 操作 3: 主题复盘

**流程**：

1. 搜索 vault 中所有相关笔记（按标签或关键词）
2. 按时间排序，梳理讨论演进时间线
3. 生成复盘报告

### 操作 4: MOC 内容地图自动生成

**流程**：

1. 扫描 vault 的目录结构
2. 为每个文件夹生成或更新 `_MOC.md`
3. 列出笔记的 `[[wikilink]]`，按标签分组

**MOC 输出示例**：

```markdown
---
type: moc
generated: 2026-05-23
---

# 📂 支付项目 — 内容地图

## 子目录
- [[架构设计/_MOC]]

## 核心文档
- [[支付系统 PRD]]
- [[技术选型报告]]

## 按标签
### #prd
- [[支付系统 PRD]]
```

## 脚本

### scripts/aggregate-notes.py

```bash
python3 scripts/aggregate-notes.py <vault 路径> [选项]

选项：
  --date-from <日期>     起始日期 (YYYY-MM-DD)
  --date-to <日期>       结束日期 (YYYY-MM-DD)
  --tag <标签>           按标签筛选 (如 "#支付")
  --type <类型>          按笔记类型筛选
  --output-format <格式> 输出格式：summary, json, markdown
```

### scripts/generate-mocs.py

```bash
python3 scripts/generate-mocs.py <vault 路径> [选项]

选项：
  --dry-run              预览模式，不实际写入
  --min-notes N          最少笔记数才生成 MOC（默认 3）
```

## 陷阱和注意事项

1. **CLI 需要 Obsidian 运行**：官方 CLI 需要 Obsidian 桌面应用正在运行。
2. **CLI 不可用时自动回退**：检测失败后切换到文件系统 + 脚本模式。
3. **深化不覆盖**：每次深化追加新章节，保留历史深化记录。
4. **Wikilink 准确性**：只在笔记确实存在时才创建 `[[wikilink]]`。
5. **MOC 不要过度生成**：只给包含 3 篇以上笔记的文件夹生成 MOC。

## 使用示例

### CLI 模式

```bash
# 读取笔记并深化
obsidian read "笔记.md"
# → AI 分析内容，追加深化提问

# 搜索相关笔记
obsidian search:tag "#支付"
# → 聚合生成主题复盘
```

### 文件系统模式

```bash
# 笔记聚合
python3 scripts/aggregate-notes.py /path/to/vault --tag "#支付" --summary

# 生成 MOC
python3 scripts/generate-mocs.py /path/to/vault
```
