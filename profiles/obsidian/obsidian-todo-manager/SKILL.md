---
name: obsidian-todo-manager
description: "Manage TODO items in Obsidian vault: create, update, filter, complete, and summarize tasks with priority, status, tags, and due dates."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [obsidian, todo, task-management, productivity, notes]
    related_skills: [obsidian]
---

# Obsidian TODO Manager

Manage task tracking in your Obsidian vault using filesystem-first operations.

## When to Use

- User says "add a todo", "create a task", "记个待办"
- User says "show my todos", "what's pending", "看下待办"
- User says "mark done", "完成任务", "完结"
- User says "summarize my todos", "汇总待办", "todo summary"
- User wants to create a new project task list

## Vault Path

Load the `obsidian` skill first to understand vault path conventions.

The vault path follows the `OBSIDIAN_VAULT_PATH` env var, or falls back to `~/Documents/Obsidian Vault`.

**File tools do NOT expand shell variables.** Always resolve to an absolute path before using `read_file`, `write_file`, or `patch`.

## TODO File Structure

### Standard TODO.md Location

```
Vault/
├── 00-Inbox/
│   └── TODO.md              ← Master todo list
├── 10-Projects/
│   └── <project-name>/
│       └── TODO.md           ← Project-specific todos
└── 90-Archive/
    └── TODO.md               ← Completed/archived todos
```

### TODO.md Format

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

### Entry Format

Each todo entry follows this pattern:

```
- [ ] YYYY-MM-DD | 任务描述 | #标签1 #标签2 | 额外信息
```

- **Date**: Creation date (YYYY-MM-DD)
- **Description**: Concise task description
- **Tags**: Hash-prefixed labels for filtering
- **Extra info**: Optional — assignee, due date, links, etc.

## Operations

### 1. Create a New Todo

**Steps:**

1. Resolve vault path (from `obsidian` skill conventions)
2. Read the target TODO.md with `read_file`
3. Determine the priority section (P0/P1/P2)
4. Use `patch` to insert the new entry under the correct section header
5. Update the `updated:` date in frontmatter

**Example — adding a P1 task:**

```python
# Using patch with the section header as anchor
patch(path="/path/to/TODO.md",
      old_string="## 🟡 P1 - 重要\n",
      new_string="## 🟡 P1 - 重要\n- [ ] 2026-05-23 | 完成API设计文档 | #api #设计\n")
```

### 2. Create a New Project TODO List

**Steps:**

1. Check if the project folder exists
2. Create `Vault/10-Projects/<project-name>/TODO.md` with the template
3. Use the template from `templates/project-todo.md`

### 3. Mark a Todo as Complete

**Steps:**

1. Read the TODO.md to find the target entry
2. Use `patch` to:
   - Change `- [ ]` to `- [x]`
   - Append `| ✅ YYYY-MM-DD` (completion date)
3. Move the entry from its priority section to `## ✅ 已完成`

**Example:**

```python
patch(path="/path/to/TODO.md",
      old_string="- [ ] 2026-05-20 | 需求评审会议 | #meeting",
      new_string="- [x] 2026-05-20 | 需求评审会议 | #meeting | ✅ 2026-05-23")
```

### 4. List / Filter Todos

**Steps:**

1. Read the TODO.md
2. Parse entries by section
3. Optional: use `scripts/parse-todos.py` for programmatic filtering

**Filter by tag:**
```bash
python3 scripts/parse-todos.py /path/to/TODO.md --tag "#prd"
```

**Filter by status:**
```bash
python3 scripts/parse-todos.py /path/to/TODO.md --status pending
python3 scripts/parse-todos.py /path/to/TODO.md --status done
```

**Show all:**
```bash
python3 scripts/parse-todos.py /path/to/TODO.md --summary
```

### 5. Summarize Todos

Generate a text summary for reporting:

```
📋 待办汇总 (2026-05-23)

🔴 P0 紧急 (1项):
  - 修复线上支付bug #bug #支付

🟡 P1 重要 (2项):
  - 完成PRD v2.0评审 #prd #评审
  - 完成API设计文档 #api #设计

🟢 P2 常规 (1项):
  - 用户调研报告 #research

✅ 已完成本周 (3项):
  - 需求评审会议 #meeting
  - ...
```

### 6. Archive Completed Todos

Periodically move completed items to archive:

1. Read the main TODO.md
2. Extract all `[x]` entries from `## ✅ 已完成`
3. Append them to `90-Archive/TODO.md`
4. Remove them from the main TODO.md
5. Update frontmatter dates

## Templates

Use files in `templates/` directory:

- `templates/daily-todo.md` — Daily note with embedded todo section
- `templates/project-todo.md` — New project todo list

## Scripts

- `scripts/parse-todos.py` — Parse and filter TODO.md entries

Usage:
```bash
python3 scripts/parse-todos.py <path-to-todo.md> [options]

Options:
  --tag <tag>       Filter by tag (e.g., "#prd")
  --status <status> Filter by status: pending, done, all
  --priority <p>    Filter by priority: P0, P1, P2
  --summary         Show summary counts
  --json            Output as JSON
```

## Integration with Obsidian

### Daily Notes

Embed todo status in daily notes using Obsidian's embed syntax:

```markdown
## 今日待办
![[TODO#🟡 P1 - 重要]]
```

### Dataview Plugin (Optional)

If the user has the Dataview plugin installed, todos can be queried:

```dataview
TASK FROM "00-Inbox"
WHERE !completed
SORT file.name DESC
```

### Local REST API (Optional)

If the user has the **Obsidian Local REST API** plugin installed, you can also:

```bash
# Read a note
curl -X GET "http://localhost:27124/vault/00-Inbox/TODO.md" \
  -H "Authorization: Bearer <token>"

# Update a note
curl -X PUT "http://localhost:27124/vault/00-Inbox/TODO.md" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: text/markdown" \
  --data-binary "@updated-todo.md"
```

**However, filesystem operations via Hermes file tools are preferred** — they're simpler, don't require Obsidian to be running, and work offline.

## Pitfalls

1. **Shell variable expansion**: File tools don't expand `$OBSIDIAN_VAULT_PATH`. Always resolve to absolute path first.
2. **Spaces in paths**: Vault paths may contain spaces. Use file tools (not shell commands) to avoid quoting issues.
3. **Concurrent edits**: If Obsidian is open and editing the same file, filesystem writes may conflict. Prefer quick read→patch→write cycles.
4. **Uniqueness in patch**: When using `patch`, ensure `old_string` is unique. Include surrounding context lines.
5. **Frontmatter dates**: Always update the `updated:` frontmatter field when modifying a TODO.md.

## Examples

### Example 1: Quick todo add

User: "帮我记一下，明天要和产品团队过一下需求评审"

→ Add to P1 section of TODO.md:
```
- [ ] 2026-05-24 | 和产品团队过需求评审 | #prd #评审 #会议
```

### Example 2: Check pending todos

User: "我现在有哪些待办？"

→ Read TODO.md, summarize pending items by priority.

### Example 3: Complete a task

User: "需求评审搞完了"

→ Find matching entry, change to `[x]`, add completion date.

### Example 4: Create project todo

User: "新建一个支付重构项目的待办列表"

→ Create `10-Projects/支付重构/TODO.md` with project template.
