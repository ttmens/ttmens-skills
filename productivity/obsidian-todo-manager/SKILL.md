---
name: obsidian-todo-manager
description: "管理 Obsidian 仓库中的待办事项：创建、更新、筛选、完成任务，支持优先级、状态、标签和截止日期"
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [obsidian, todo, task-management, productivity, notes, cli]
    related_skills: [obsidian]
---

# Obsidian 待办管理

管理 Obsidian 中的待办事项。**优先使用 Obsidian 官方 CLI**（1.12.4+），CLI 不可用时退回到文件系统操作。

## 什么时候触发

| 用户说的话 | 触发操作 |
|-----------|----------|
| 「记个待办」「加个任务」 | 创建新待办 |
| 「看下待办」「我有啥没做完」 | 汇总待办 |
| 「XX 搞完了」「标记完成」 | 完成任务 |
| 「汇总待办」「待办总结」 | 生成汇总报告 |
| 「新建 XX 项目的待办」 | 创建项目级待办列表 |

## 操作模式选择

**第一步：检测 CLI 是否可用**

```bash
obsidian --version 2>/dev/null && obsidian help 2>/dev/null | head -5
```

- **可用** → 使用 CLI 模式（模式 A）
- **不可用** → 使用文件系统模式（模式 B）

**CLI 前提条件**：
- Obsidian 桌面版 1.12.4 或更新（2026年2月27日发布）
- 设置 → 一般 → 启用 "Command line interface"
- Obsidian 应用正在运行
- 命令必须在 Vault 目录执行，或使用 `--vault <路径>` 指定

---

## 模式 A: Obsidian 官方 CLI（优先）

### CLI 核心命令

```bash
# 基础操作
obsidian --version                 # 查看版本
obsidian help                      # 查看所有命令
obsidian files                     # 列出 vault 文件状态
obsidian files:count               # 统计文件数

# Daily Notes
obsidian daily                     # 打开今日 daily note
obsidian daily:append "内容"        # 追加内容到今日 daily note

# 搜索
obsidian search query="关键词"      # 全文搜索
obsidian search:context "关键词"    # 带上下文的搜索
obsidian search:tag "#标签"         # 按标签搜索

# 文件操作
obsidian create "路径/文件.md"      # 创建文件
obsidian open "路径/文件.md"        # 在 Obsidian 中打开文件
obsidian read "路径/文件.md"        # 读取文件内容
obsidian append "路径/文件.md" "追加内容"  # 追加内容到文件

# 模板
obsidian template "模板名"          # 应用模板

# 重命名（自动维护内部链接）
obsidian rename "旧名" "新名"
obsidian move "旧路径" "新路径"
```

### 使用 CLI 操作待办

#### 1. 读取待办列表

```bash
obsidian read "00-Inbox/TODO.md"
```

#### 2. 创建待办

```bash
# 方式一：追加到 TODO.md
obsidian append "00-Inbox/TODO.md" "- [ ] 2026-05-23 | 新任务 | #标签"

# 方式二：追加到今日 daily note
obsidian daily:append "## 今日待办\n- [ ] 新任务描述"
```

#### 3. 搜索待办

```bash
# 按标签搜索
obsidian search:tag "#prd"

# 按关键词搜索
obsidian search query="待办 未完成"
```

#### 4. 指定 vault 路径

```bash
# 在非 vault 目录执行时指定 vault
obsidian --vault "/path/to/vault" read "00-Inbox/TODO.md"
```

---

## 模式 B: 文件系统操作（CLI 不可用时）

### TODO.md 存放位置

```
Vault/
├── 00-Inbox/
│   └── TODO.md              ← 主待办列表
├── 10-Projects/
│   └── <项目名>/
│       └── TODO.md           ← 项目级待办
└── 90-Archive/
    └── TODO.md               ← 已完成/归档待办
```

### TODO.md 格式

```markdown
---
updated: 2026-05-23
---

# 待办事项

## 🔴 P0 - 紧急
- [ ] 2026-05-23 | 修复线上支付bug | #bug #支付 | 负责人: @张三

## 🟡 P1 - 重要
- [ ] 2026-05-25 | 完成PRD v2.0评审 | #prd #评审

## 🟢 P2 - 常规
- [ ] 2026-06-01 | 用户调研报告 | #research

## ✅ 已完成
- [x] 2026-05-20 | 需求评审会议 | #meeting | ✅ 2026-05-20
```

### 条目格式

```
- [ ] YYYY-MM-DD | 任务描述 | #标签1 #标签2 | 额外信息
```

### 核心操作

#### 1. 创建待办

```python
patch(path="/path/to/TODO.md",
      old_string="## 🟡 P1 - 重要\n",
      new_string="## 🟡 P1 - 重要\n- [ ] 2026-05-23 | 完成API设计文档 | #api #设计\n")
```

#### 2. 完成任务

```python
patch(path="/path/to/TODO.md",
      old_string="- [ ] 2026-05-20 | 需求评审会议 | #meeting",
      new_string="- [x] 2026-05-20 | 需求评审会议 | #meeting | ✅ 2026-05-23")
```

#### 3. 筛选待办

使用 `scripts/parse-todos.py`：

```bash
python3 scripts/parse-todos.py /path/to/TODO.md --tag "#prd"
python3 scripts/parse-todos.py /path/to/TODO.md --status pending
python3 scripts/parse-todos.py /path/to/TODO.md --summary
python3 scripts/parse-todos.py /path/to/TODO.md --json
```

---

## 模板

- `templates/daily-todo.md` — 每日笔记模板
- `templates/project-todo.md` — 项目待办模板

## 脚本

- `scripts/parse-todos.py` — 解析和筛选 TODO.md 条目

## 陷阱和注意事项

1. **CLI 需要 Obsidian 运行**：官方 CLI 需要 Obsidian 桌面应用正在运行且 vault 已打开。
2. **CLI 不可用时自动回退**：检测 `obsidian --version` 失败后，自动切换到文件系统操作模式。
3. **必须在 vault 目录执行**：CLI 命令必须在 Vault 目录执行，或使用 `--vault` 指定路径。
4. **Shell 变量展开**：文件工具不展开 `$OBSIDIAN_VAULT_PATH`。必须先解析为绝对路径。
5. **patch 唯一性**：使用 `patch` 时，确保 `old_string` 唯一。
6. **Frontmatter 日期**：修改 TODO.md 时始终更新 `updated:` 字段。

## 使用示例

### CLI 模式

```bash
# 添加待办
obsidian append "00-Inbox/TODO.md" "- [ ] 2026-05-24 | 和产品团队过需求评审 | #prd #评审"

# 查看待办
obsidian read "00-Inbox/TODO.md"

# 搜索待办
obsidian search:tag "#prd"
```

### 文件系统模式

用户："帮我记一下，明天要和产品团队过一下需求评审"

→ 用 patch 在 TODO.md 的 P1 区添加待办条目。
