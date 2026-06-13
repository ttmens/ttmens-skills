# Agent 自助：安装与使用

> **运行时规则**（阶段边界、G1/G2/G3）：[AGENTS.md](../AGENTS.md)  
> **能力全景与设计思想**：[README.md](../README.md)

本文档面向 **Cursor / Hermes / OpenCode** 上的 Agent：如何解析路径、安装技能、自检、跑流水线。

---

## 1. 判断当前平台

按优先级检测（命中即停）：

| 信号 | 平台 | 技能安装目录 |
|------|------|--------------|
| 项目存在 `.cursor/skills/` 或 `.cursor/hooks.json` | **Cursor（项目）** | `{PROJECT_ROOT}/.cursor/skills/` |
| 用户全局 Cursor，无项目 skills | **Cursor（全局）** | `~/.cursor/skills/` |
| 环境变量 / 上下文含 Hermes、Kanban、`pm-aligner` | **Hermes** | `~/.hermes/skills/` |
| 项目存在 `.opencode/skills/` | **OpenCode（项目）** | `{PROJECT_ROOT}/.opencode/skills/` |
| 否则 OpenCode 全局 | **OpenCode（全局）** | `~/.config/opencode/skills/` |
| 当前工作区根有 `marketplace.yaml` + `pipelines/pm-idea-to-mvp/` | **源码模式** | 工作区根 = `{SKILLS_ROOT}` |

配置 SSOT：[platforms.yaml](../platforms.yaml)

---

## 2. 解析 `{SKILLS_ROOT}`

**禁止硬编码** `D:\...` 或固定 clone 路径。按序尝试：

```text
1. 源码模式：cwd 或上级目录含 marketplace.yaml → 该目录
2. 项目内：{PROJECT_ROOT}/.cursor/skills/ 且含 pm-idea-to-mvp/ → 该目录
3. 项目内：{PROJECT_ROOT}/.opencode/skills/ 且含 pm-idea-to-mvp/ → 该目录
4. 全局 Cursor：~/.cursor/skills/ 且含 pm-idea-to-mvp/
5. 全局 Hermes：~/.hermes/skills/ 且含 pm-idea-to-mvp/
6. 全局 OpenCode：~/.config/opencode/skills/ 且含 pm-idea-to-mvp/
```

**检测命令**（任选其一存在即可）：

```bash
# 应返回 0
test -f "{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/SKILL.md"
test -f "{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py"
```

**`{PROJECT_ROOT}`**：当前 pm-{slug} 产品仓库根（含 `00-brief.md` 或 `gates.json` 或 `docs/workflow_state.yaml`）。  
若用户只在 ttmens-skills 仓库里对话，则 `{PROJECT_ROOT}` ≠ `{SKILLS_ROOT}`。

---

## 3. 安装（技能缺失时）

### 3.1 前置条件

在 **ttmens-skills 仓库根**执行（需用户授权 shell）：

```bash
git submodule update --init --recursive   # borrowed 技能依赖 vendor/
pip install pyyaml                        # install 脚本需要
```

### 3.2 推荐命令（完整流水线）

```bash
cd {SKILLS_ROOT}   # ttmens-skills 克隆根
./install.sh --core --profile debate --all
```

- `--core`：37 个技能（17 native + 20 borrowed）
- `--profile debate`：**G2 红队**依赖（`pm-strategy-red-team`、`pm-pre-mortem`），spec 阶段必需

Windows：

```powershell
.\install.ps1 -Target All
# 或显式：python scripts/install_skills.py --core --profile debate --all
```

### 3.3 分平台安装

| 平台 | 命令 |
|------|------|
| **Cursor**（+ 项目 AGENTS/hooks） | `./install.sh --core --profile debate --platform cursor --project {PROJECT_ROOT}` |
| **Hermes**（+ Kanban profiles） | `./install.sh --core --profile debate --platform hermes --profile hermes-kanban` |
| **OpenCode**（+ 项目 AGENTS） | `./install.sh --core --profile debate --platform opencode --project {PROJECT_ROOT}` |

### 3.4 减载安装（单阶段）

```bash
./install.sh --lite --stage mvp --all --profile debate
```

仅安装该 stage 相关技能 + `pm-idea-to-mvp`，降低 context。

### 3.5 场景

| 场景 | 安装 |
|------|------|
| 新建 0→1 | 默认即可 |
| 优化现有产品 | 加 `--scenario brownfield`（会自动加 `debate` profile） |
| Refine 深化 | `--scenario refine --profile deep-research` |

Agent **若无 shell 权限**：向用户说明缺少的技能 ID，并给出上表对应 `install.sh` 命令，请用户执行后再继续。

---

## 4. 自检（安装后必做）

```bash
python {SKILLS_ROOT}/scripts/validate_skills.py
```

通过应看到：`OK: 17 native + 20 borrowed skills; pipeline scripts present`

可选：

```bash
# 确认 G2 红队依赖（spec 阶段）
test -d "{SKILLS_ROOT}/pm-strategy-red-team" || test -d "~/.cursor/skills/pm-strategy-red-team"
# 实际路径取决于 install 目标；或检查 install 日志 debate_borrowed=2
```

---

## 5. 加载与使用顺序

```mermaid
flowchart LR
  A[读取 pm-idea-to-mvp SKILL] --> B[读 stage-skills.yaml]
  B --> C[加载当前 stage 技能]
  C --> D[产出 artifacts]
  D --> E[stage-complete.py]
  E --> F{exit 0?}
  F -->|yes| G[下一阶段]
  F -->|no| D
```

1. **始终先读** [`pipelines/pm-idea-to-mvp/SKILL.md`](../pipelines/pm-idea-to-mvp/SKILL.md)
2. **查当前 stage 技能**：[`stage-skills.yaml`](../pipelines/pm-idea-to-mvp/stage-skills.yaml)
3. **只写当前 stage 产物**，勿越界
4. **阶段结束**：

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py \
  --project-root {PROJECT_ROOT} --stage <stage> --verify-goals
```

5. **MVP 内循环**（stage=mvp）：

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/inner-loop-driver.py \
  --project-root {PROJECT_ROOT}
```

### 触发语

| 用户说 | 动作 |
|--------|------|
| 从想法做到上线 | greenfield，从 brief/align 开始 |
| 继续 pm-{slug} | 读 `gates.json` / `docs/workflow_state.yaml` 续跑 |
| 优化现有产品 | brownfield，`domains/product/brownfield-bootstrap` |
| 进入 spec / mvp 阶段 | 只加载该 stage 技能 |

---

## 6. 分平台要点

### Cursor

- 项目入口：复制 [`templates/cursor/AGENTS.md`](../templates/cursor/AGENTS.md) 到 `{PROJECT_ROOT}/AGENTS.md`
- `stage-complete` 可写 `.cursor/stage-status.json`（若装了 hooks）
- 详见 [platforms/cursor.md](platforms/cursor.md)

### Hermes

- 新想法先 **decompose**，勿依赖 LLM 随意拆任务：

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/decompose-pm-pipeline.py \
  --project-root {PROJECT_ROOT} --scenario greenfield
```

- Kanban profile：`pm-aligner` … `pm-growth` 对应各 stage
- MVP 子任务：T5a Plan → T5b Inner Loop → T5c G3 Verify
- 详见 [platforms/hermes.md](platforms/hermes.md)

### OpenCode

- MVP 实现可委托：

```bash
opencode run "Implement per openspec/tasks.md and 04-mvp/DESIGN.md" --workdir {PROJECT_ROOT}/04-mvp
```

- 每个 phase 结束仍须手动/脚本跑 `stage-complete.py`
- 可选 `--profile hermes` 安装 `opencode` skill
- 详见 [platforms/opencode.md](platforms/opencode.md)

---

## 7. 质量门速查

| Gate | Stage | 关键验证 |
|------|-------|----------|
| G1 | align | `debates/align-synthesis.md` + `goal-check --stage align` |
| G2 | spec | `prd-red-team-panel` + `debates/spec-synthesis.md`（需 debate profile） |
| G3 | mvp/ship | 测试/lint/build + `ui_acceptance.py --full` |

---

## 8. 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| `stage-complete` 找不到脚本 | `{SKILLS_ROOT}` 错误 | 按 §2 重算；或运行 install |
| G2 `debate_resolved` 失败 | 未装 debate profile | `./install.sh --profile debate --all` |
| borrowed 技能缺失 | vendor submodule 未 init | `git submodule update --init --recursive` 后重装 |
| `validate_skills.py` 失败 | marketplace 与 stage-skills 不一致 | 拉最新 main，勿用 `deprecated/` 下技能 |
| Agent 加载了旧路径 | 根目录 `pm-idea-to-mvp/` 等已废弃 | 只用 `pipelines/pm-idea-to-mvp/` |

---

## 9. 索引

| 文档 | 用途 |
|------|------|
| [AGENTS.md](../AGENTS.md) | 运行时强制协议 |
| [SKILLS_CATALOG.md](SKILLS_CATALOG.md) | 全技能表 |
| [REPO_LAYOUT.md](REPO_LAYOUT.md) | 目录与脚本 SSOT |
| [command-recipes.md](../pipelines/pm-idea-to-mvp/references/command-recipes.md) | 无 slash command 时的 prompt 链 |
| [scenarios.yaml](../scenarios.yaml) | greenfield / brownfield / refine |
