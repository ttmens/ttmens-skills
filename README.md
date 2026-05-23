# Obsidian PM Skills

Obsidian skills for IT product managers — built for use with [Hermes Agent](https://hermes-agent.nousresearch.com/docs).

## 📦 Skills

### [obsidian-todo-manager](skills/productivity/obsidian-todo-manager/SKILL.md)
Manage TODO items in your Obsidian vault: create, update, filter, complete, and summarize tasks with priority, status, tags, and due dates.

**Trigger phrases**: "记个待办", "看下待办", "完成任务", "汇总待办"

### [obsidian-note-summarizer](skills/research/obsidian-note-summarizer/SKILL.md)
Summarize articles, meeting notes, and aggregate Obsidian notes into structured summaries — from single-article digests to weekly/monthly reviews and deep topic analysis.

**Trigger phrases**: "总结一下", "生成周报", "复盘一下", "汇总笔记"

## 🚀 Usage

### With Hermes Agent

1. Clone this repo:
   ```bash
   git clone https://github.com/ttmens/obsidian-pm-skills.git
   ```

2. Symlink skills to your Hermes skills directory:
   ```bash
   ln -s $(pwd)/skills/productivity/obsidian-todo-manager ~/.hermes/skills/productivity/obsidian-todo-manager
   ln -s $(pwd)/skills/research/obsidian-note-summarizer ~/.hermes/skills/research/obsidian-note-summarizer
   ```

3. Configure your Obsidian vault path in `~/.hermes/.env`:
   ```
   OBSIDIAN_VAULT_PATH=~/Documents/Obsidian Vault
   ```

### Direct File Operations

Each skill operates on your Obsidian vault via filesystem. No plugins required (though [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) and [Dataview](https://github.com/blacksmithgu/obsidian-dataview) enhance the experience).

## 📁 Structure

```
skills/
├── productivity/
│   └── obsidian-todo-manager/
│       ├── SKILL.md
│       ├── templates/
│       │   ├── daily-todo.md
│       │   └── project-todo.md
│       └── scripts/
│           └── parse-todos.py
└── research/
    └── obsidian-note-summarizer/
        ├── SKILL.md
        ├── templates/
        │   ├── article-summary.md
        │   ├── meeting-notes.md
        │   ├── weekly-review.md
        │   ├── monthly-review.md
        │   └── topic-review.md
        ├── scripts/
        │   └── aggregate-notes.py
        └── references/
            └── source-handlers.md
```

## 🔄 Workflow

```
📥 输入源              📝 Obsidian Vault              📤 输出
─────────────────      ─────────────────────────      ────────────
文章/链接      ──→   [[文章摘要]] + 关键观点    ──→   知识库
会议记录       ──→   [[会议记录]] + 行动项      ──→   任务追踪
待办事项       ──→   [[TODO]] + 状态标签       ──→   进度报告
日常笔记       ──→   按标签/时间聚合          ──→   周报/月报
```

## 📝 TODO

- [ ] Add support for Obsidian Local REST API integration
- [ ] Add skill for project management (PRD templates, decision logs)
- [ ] Add skill for competitive analysis tracking
- [ ] Improve parse-todos.py with date-based filtering
- [ ] Add support for Obsidian canvas diagrams
- [ ] Create skill for user research note management

## License

MIT
