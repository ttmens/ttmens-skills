# Obsidian PM Skills

面向 IT 产品经理的 Obsidian 自动化 Skills — 基于 [Hermes Agent](https://hermes-agent.nousresearch.com/docs)。

## 📦 包含 Skills

### [obsidian-todo-manager](skills/productivity/obsidian-todo-manager/SKILL.md) — 待办管理

**能力**：创建/更新/筛选/完成任务，P0/P1/P2 优先级，标签筛选，项目级待办，待办汇总。

**触发**：「记个待办」「看下待办」「完成任务」「汇总待办」

### [obsidian-deepen-review](skills/research/obsidian-deepen-review/SKILL.md) — 笔记深化与聚合

**能力**：
| 能力 | 说明 |
|------|------|
| 🔍 笔记深化 | 对单篇笔记生成四类批判性问题（批判性/连接性/行动性/扩展性），自动链接相关笔记 |
| 📊 周报生成 | 自动聚合本周所有笔记，按类别汇总生成结构化周报 |
| 📈 月报生成 | 月度总结，含趋势对比、决策汇总、月度反思 |
| 🔄 主题复盘 | 按标签/关键词聚合笔记，梳理决策演进时间线 |
| 🗺️ MOC 自动生成 | 扫描文件夹自动生成内容地图导航页，按标签和类型分组 |

**触发**：「深化这篇笔记」「生成周报」「月报」「汇总关于 XX 的笔记」「生成目录/MOC」

## 🚀 安装

### 方式一：Symlink（推荐）

```bash
git clone https://github.com/ttmens/obsidian-pm-skills.git
cd obsidian-pm-skills

# 软链接到 Hermes skills 目录
ln -sf $(pwd)/skills/productivity/obsidian-todo-manager ~/.hermes/skills/productivity/obsidian-todo-manager
ln -sf $(pwd)/skills/research/obsidian-deepen-review ~/.hermes/skills/research/obsidian-deepen-review
```

### 方式二：直接复制到 skills 目录

```bash
cp -r skills/* ~/.hermes/skills/
```

### 配置 Vault 路径

在 `~/.hermes/.env` 中设置：
```
OBSIDIAN_VAULT_PATH=~/Documents/Obsidian Vault
```

## 📁 仓库结构

```
skills/
├── productivity/
│   └── obsidian-todo-manager/
│       ├── SKILL.md
│       ├── templates/
│       │   ├── daily-todo.md          # 每日笔记模板
│       │   └── project-todo.md        # 项目待办模板
│       └── scripts/
│           └── parse-todos.py         # 待办解析/筛选脚本
└── research/
    └── obsidian-deepen-review/
        ├── SKILL.md
        └── scripts/
            ├── aggregate-notes.py     # 笔记聚合扫描脚本
            └── generate-mocs.py       # MOC 内容地图自动生成脚本
```

## 🔄 工作流

```
📥 原始输入           📝 Obsidian Vault              📤 自动化输出
─────────────         ──────────────────              ──────────────
想法/任务     ──→   Inbox 分类路由            ──→   结构化待办列表
文章/链接     ──→   笔记深化提问              ──→   批判性问题 + 关联笔记
会议记录      ──→   决策/行动项提取           ──→   可追踪任务
日常笔记      ──→   按周/月/主题聚合          ──→   周报/月报/复盘
项目文档      ──→   MOC 自动生成              ──→   内容地图导航
```

## 🔧 脚本使用

### parse-todos.py — 待办筛选

```bash
python3 scripts/parse-todos.py /path/to/TODO.md --tag "#prd"
python3 scripts/parse-todos.py /path/to/TODO.md --status pending
python3 scripts/parse-todos.py /path/to/TODO.md --summary
```

### aggregate-notes.py — 笔记聚合

```bash
python3 scripts/aggregate-notes.py /path/to/vault --tag "#支付"
python3 scripts/aggregate-notes.py /path/to/vault --date-from 2026-05-01 --date-to 2026-05-31
python3 scripts/aggregate-notes.py /path/to/vault --type meeting --output-format markdown
```

### generate-mocs.py — MOC 自动生成

```bash
python3 scripts/generate-mocs.py /path/to/vault
python3 scripts/generate-mocs.py /path/to/vault --dry-run     # 预览
python3 scripts/generate-mocs.py /path/to/vault --min-notes 2  # 最少 2 篇笔记
```

## 📝 TODO

- [ ] 支持 Obsidian Local REST API 插件（双向同步）
- [ ] 添加 PRD 模板管理 skill
- [ ] 添加竞品分析追踪 skill
- [ ] 周报/月报自动生成（定时任务）
- [ ] 笔记间关系图谱可视化
- [ ] 支持 Obsidian Canvas 自动生成

## License

MIT
