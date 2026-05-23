---
name: obsidian-todo-manager
description: "管理 Obsidian 仓库中的待办事项：创建、更新、筛选、完成任务，支持优先级、状态、标签和截止日期"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [obsidian, todo, task-management, productivity, notes]
    related_skills: [obsidian]
---

# Obsidian 待办管理

基于文件系统的 Obsidian 待办事项管理。

## 什么时候触发

| 用户说的话 | 触发操作 |
|-----------|----------|
| 「记个待办」「加个任务」 | 创建新待办 |
| 「看下待办」「我有啥没做完」 | 汇总待办 |
| 「XX 搞完了」「标记完成」 | 完成任务 |
| 「汇总待办」「待办总结」 | 生成汇总报告 |
| 「新建 XX 项目的待办」 | 创建项目级待办列表 |

## Vault 路径

先加载 `obsidian` skill 获取 vault 路径约定。

路径来自 `OBSIDIAN_VAULT_PATH` 环境变量，或者默认 `~/Documents/Obsidian Vault`。

**文件工具不展开 shell 变量**。调用 `read_file`、`write_file`、`patch` 前必须先解析为绝对路径。

## 待办文件结构

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

每条待办遵循以下格式：

```
- [ ] YYYY-MM-DD | 任务描述 | #标签1 #标签2 | 额外信息
```

- **日期**: 创建日期 (YYYY-MM-DD)
- **描述**: 简洁的任务描述
- **标签**: 以 # 开头的标签，用于筛选
- **额外信息**: 可选 — 负责人、截止日期、链接等

## 核心操作

### 1. 创建待办

**步骤：**

1. 解析 vault 路径
2. 用 `read_file` 读取目标 TODO.md
3. 确定优先级分区（P0/P1/P2）
4. 用 `patch` 在对应分区标题下插入新条目
5. 更新 frontmatter 中的 `updated:` 日期

**示例 — 添加 P1 任务：**

```python
patch(path="/path/to/TODO.md",
      old_string="## 🟡 P1 - 重要\n",
      new_string="## 🟡 P1 - 重要\n- [ ] 2026-05-23 | 完成API设计文档 | #api #设计\n")
```

### 2. 创建项目待办列表

**步骤：**

1. 检查项目文件夹是否存在
2. 创建 `Vault/10-Projects/<项目名>/TODO.md`
3. 使用 `templates/project-todo.md` 模板

### 3. 完成任务

**步骤：**

1. 读取 TODO.md 找到目标条目
2. 用 `patch`：
   - 将 `- [ ]` 改为 `- [x]`
   - 追加 `| ✅ YYYY-MM-DD`（完成日期）
3. 将条目从优先级分区移到 `## ✅ 已完成`

**示例：**

```python
patch(path="/path/to/TODO.md",
      old_string="- [ ] 2026-05-20 | 需求评审会议 | #meeting",
      new_string="- [x] 2026-05-20 | 需求评审会议 | #meeting | ✅ 2026-05-23")
```

### 4. 筛选待办

**步骤：**

1. 读取 TODO.md
2. 使用 `scripts/parse-todos.py` 进行筛选

```bash
python3 scripts/parse-todos.py /path/to/TODO.md --tag "#prd"        # 按标签
python3 scripts/parse-todos.py /path/to/TODO.md --status pending    # 按状态
python3 scripts/parse-todos.py /path/to/TODO.md --summary           # 汇总统计
python3 scripts/parse-todos.py /path/to/TODO.md --json              # JSON 输出
```

### 5. 汇总待办

生成文本报告：

```
📋 待办汇总 (2026-05-23)

🔴 P0 紧急 (1项):
  - 修复线上支付bug #bug #支付

🟡 P1 重要 (2项):
  - 完成PRD v2.0评审 #prd #评审
  - 完成API设计文档 #api #设计

🟢 P2 常规 (1项):
  - 用户调研报告 #research

✅ 已完成 (1项):
  - 需求评审会议 #meeting
```

### 6. 归档已完成待办

定期将已完成条目移至归档：

1. 读取主 TODO.md
2. 提取 `## ✅ 已完成` 中所有 `[x]` 条目
3. 追加到 `90-Archive/TODO.md`
4. 从主 TODO.md 中移除
5. 更新 frontmatter 日期

## 模板

使用 `templates/` 目录下的文件：

- `templates/daily-todo.md` — 每日笔记模板（含待办分区）
- `templates/project-todo.md` — 项目待办模板

## 脚本

- `scripts/parse-todos.py` — 解析和筛选 TODO.md 条目

## 与 Obsidian 的集成

### 每日笔记

在每日笔记中嵌入待办状态：

```markdown
## 今日待办
![[TODO#🟡 P1 - 重要]]
```

### Dataview 插件（可选）

如果用户安装了 Dataview 插件：

```dataview
TASK FROM "00-Inbox"
WHERE !completed
SORT file.name DESC
```

### Local REST API 插件（可选）

如果用户安装了 **Obsidian Local REST API** 插件：

```bash
# 读取笔记
curl -X GET "http://localhost:27124/vault/00-Inbox/TODO.md" \
  -H "Authorization: Bearer <token>"

# 更新笔记
curl -X PUT "http://localhost:27124/vault/00-Inbox/TODO.md" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: text/markdown" \
  --data-binary "@updated-todo.md"
```

**但优先使用文件工具** — 更简单，不需要 Obsidian 运行，离线可用。

## 陷阱和注意事项

1. **Shell 变量展开**：文件工具不展开 `$OBSIDIAN_VAULT_PATH`。必须先解析为绝对路径。
2. **路径中的空格**：Vault 路径可能包含空格。使用文件工具而非 shell 命令，避免引号问题。
3. **并发编辑**：如果 Obsidian 正在编辑同一个文件，文件系统写入可能冲突。优先快速 read→patch→write 循环。
4. **patch 唯一性**：使用 `patch` 时，确保 `old_string` 唯一。包含足够的上下文行。
5. **Frontmatter 日期**：修改 TODO.md 时始终更新 `updated:` 字段。

## 使用示例

### 示例 1: 快速添加待办

用户："帮我记一下，明天要和产品团队过一下需求评审"

→ 在 TODO.md 的 P1 区添加：
```
- [ ] 2026-05-24 | 和产品团队过需求评审 | #prd #评审 #会议
```

### 示例 2: 查看待办

用户："我现在有哪些待办？"

→ 读取 TODO.md，按优先级汇总未完成项。

### 示例 3: 完成任务

用户："需求评审搞完了"

→ 找到对应条目，改为 `[x]`，记录完成日期。

### 示例 4: 创建项目待办

用户："新建一个支付重构项目的待办列表"

→ 用项目模板创建 `10-Projects/支付重构/TODO.md`。
