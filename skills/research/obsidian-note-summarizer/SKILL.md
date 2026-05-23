---
name: obsidian-note-summarizer
description: "Summarize articles, meeting notes, and aggregate Obsidian notes into structured summaries — from single-article digests to weekly/monthly reviews and deep topic analysis."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [obsidian, summarization, notes, review, weekly-report, article-summary]
    related_skills: [obsidian]
---

# Obsidian Note Summarizer

Transform content into structured Obsidian notes and generate periodic or thematic summaries.

## When to Use

### Light Summaries (single source → single note)
- User sends a URL and says "总结一下" / "summarize this"
- User says "帮我记一下这篇文章" / "save this article"
- User provides meeting notes and says "整理成会议记录"
- User says "把这个文档存到 Obsidian"

### Heavy Summaries (multiple sources → aggregated report)
- User says "总结一下这个月的笔记" / "monthly review"
- User says "生成周报" / "weekly report"
- User says "复盘一下支付项目" / "topic review"
- User says "把最近关于 AI 的笔记汇总一下" / "aggregate notes by tag"

## Vault Path

Load the `obsidian` skill first to understand vault path conventions.

The vault path follows the `OBSIDIAN_VAULT_PATH` env var, or falls back to `~/Documents/Obsidian Vault`.

**File tools do NOT expand shell variables.** Always resolve to an absolute path before using `read_file`, `write_file`, or `patch`.

## Note Structure

```
Vault/
├── 00-Inbox/
│   └── articles/                    ← Article summaries
│       └── 2026-05-23-文章标题.md
│   └── meetings/                    ← Meeting notes
│       └── 2026-05-23-会议名称.md
├── 20-Areas/
│   └── reviews/                     ← Periodic reviews
│       ├── weekly/
│       │   └── 2026-W21-review.md
│       └── monthly/
│           └── 2026-05-review.md
└── 30-Topics/
    └── <topic-name>/
        └── review.md                ← Topic deep reviews
```

## Operations

### 1. Article Summary (URL → Note)

**Steps:**

1. Fetch the article content (web tools or user-provided text)
2. Extract: title, author, source URL, key points, data, quotes
3. Create a note using `templates/article-summary.md`
4. Save to `00-Inbox/articles/YYYY-MM-DD-标题.md`
5. Add wikilinks to related existing notes (search vault for related topics)

**Output template (from `templates/article-summary.md`):**

```markdown
---
title: "文章标题"
source: "URL"
author: "作者"
date: 2026-05-23
tags: [summary, 分类]
status: raw
---

# 文章标题

> 一句话总结：...

## 📋 核心观点
1. ...

## 💡 关键洞察
- ...

## 📊 数据/事实
- ...

## 🎯 对我的启发/行动项
- [ ] ...

## 🔗 关联笔记
- [[相关主题]]
```

### 2. Meeting Notes

**Steps:**

1. Parse the meeting input (raw text, transcript, or user dictation)
2. Extract: attendees, decisions, action items, open questions
3. Create a note using `templates/meeting-notes.md`
4. Save to `00-Inbox/meetings/YYYY-MM-DD-会议名.md`
5. Cross-reference any mentioned projects with `[[wikilinks]]`

**Output template (from `templates/meeting-notes.md`):**

```markdown
---
title: "会议名称"
date: 2026-05-23
attendees: [张三, 李四]
type: meeting
tags: [meeting, #项目名]
---

# 会议名称

## 📋 议程
1. ...

## 🎯 决策
- [决策内容] — 决策人 @xxx

## ✅ 行动项
- [ ] 任务描述 | 负责人 @xxx | 截止: YYYY-MM-DD

## ❓ 待确认
- ...

## 📝 备注
- ...

## 🔗 相关
- [[相关项目]]
- [[相关PRD]]
```

### 3. Weekly Review

**Steps:**

1. Determine the week range (current week or specified)
2. Search the vault for all notes created in that range
3. Aggregate by category: articles read, meetings held, decisions made, todos completed
4. Generate summary using `templates/weekly-review.md`
5. Save to `20-Areas/reviews/weekly/YYYY-WNN-review.md`

**Use `scripts/aggregate-notes.py` to automate the search:**

```bash
python3 scripts/aggregate-notes.py /path/to/vault \
  --date-from 2026-05-19 --date-to 2026-05-25 \
  --output-format json
```

**Output template (from `templates/weekly-review.md`):**

```markdown
---
week: 2026-W21
date_from: 2026-05-19
date_to: 2026-05-25
type: weekly-review
---

# 周报 — 2026年第21周

## 📊 概览
- 新建笔记: N篇
- 完成待办: N项
- 会议: N场
- 文章阅读: N篇

## 🎯 本周完成
- ...

## 📝 关键决策
- ...

## 📖 学习 & 阅读
- [[文章1]] — 一句话总结
- [[文章2]] — 一句话总结

## 🔮 下周计划
- ...

## 💡 反思
- ...
```

### 4. Monthly Review

Similar to weekly review but aggregates by calendar month. Uses `templates/monthly-review.md`.

### 5. Topic Deep Review

**Steps:**

1. Search vault for all notes matching a tag or topic keyword
2. Read each note and extract: decisions, insights, timeline of thinking evolution
3. Synthesize into a coherent narrative
4. Save to `30-Topics/<topic>/review.md`

**Use `scripts/aggregate-notes.py` to find related notes:**

```bash
python3 scripts/aggregate-notes.py /path/to/vault \
  --tag "#支付" \
  --output-format json
```

**Output template (from `templates/topic-review.md`):**

```markdown
---
topic: "支付系统"
date: 2026-05-23
type: topic-review
notes_count: 12
---

# 主题复盘: 支付系统

## 📈 演进时间线
- 2026-01: 初始方案讨论
- 2026-03: 技术选型
- 2026-05: 重构启动

## 🎯 核心决策
| 决策 | 时间 | 理由 | 结果 |
|------|------|------|------|
| 选择方案A | 2026-03-15 | 性能最优 | ✅ 验证通过 |

## 💡 关键洞察
- ...

## 🔗 相关笔记
- [[笔记1]]
- [[笔记2]]

## 📝 下一步
- ...
```

## Scripts

### aggregate-notes.py

Search and aggregate notes by date range, tag, or keyword.

```bash
python3 scripts/aggregate-notes.py <vault-path> [options]

Options:
  --date-from <date>   Start date (YYYY-MM-DD)
  --date-to <date>     End date (YYYY-MM-DD)
  --tag <tag>          Filter by tag (e.g., "#支付")
  --type <type>        Filter by note type: article, meeting, review, all
  --keyword <word>     Full-text search keyword
  --output-format <fmt> Output format: summary, json, markdown
  --top-dir <dir>      Search only under this subdirectory
```

## Source Handling

### Web Articles
Use web tools to fetch content, then summarize into structured note.

### PDF Documents
If the user provides a PDF path, extract text first (use OCR tools if needed), then summarize.

### WeChat Articles
WeChat articles may have anti-scraping. Ask the user to copy-paste content if direct fetch fails.

### User Dictation / Voice
Transcribe first, then structure into meeting notes or article summary.

## Pitfalls

1. **Title normalization**: Article titles may contain characters invalid for filenames. Sanitize: replace `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` with `-`.
2. **Duplicate detection**: Before creating a summary note, search the vault for existing notes with the same URL or similar title to avoid duplicates.
3. **Encoding**: Chinese characters in paths and content — always use UTF-8 encoding.
4. **Large vaults**: When aggregating across many notes, use targeted searches (by date range or tag) rather than scanning all files.
5. **Wikilink accuracy**: Only create `[[wikilinks]]` to notes that actually exist. Use `search_files` to verify before linking.

## Examples

### Example 1: Quick article summary

User sends a link: "https://example.com/ai-product-trends"

→ Fetch content, create `00-Inbox/articles/2026-05-23-AI产品趋势.md`

### Example 2: Meeting notes

User: "刚和产品开了个会，决定把支付流程从3步改到2步，张三负责出方案，下周三前完成"

→ Create `00-Inbox/meetings/2026-05-23-支付流程优化会议.md` with action items

### Example 3: Weekly review

User: "帮我生成这周的周报"

→ Aggregate all notes from Mon-Fri, generate weekly review

### Example 4: Topic review

User: "把关于支付的所有笔记汇总一下，做个复盘"

→ Search vault for `#支付` tagged notes, synthesize topic review
