# Hermes Agent 系统架构文档

> 版本：v1.0
> 最后更新：2026-06-19
> 验证状态：✅ 系统健康（HEALTHY）

---

## 目录

1. [系统概览](#系统概览)
2. [核心架构](#核心架构)
3. [Gateway 消息平台集成](#gateway-消息平台集成)
4. [Kanban 多 Profile 协作系统](#kanban-多-profile-协作系统)
5. [工具链与环境系统](#工具链与环境系统)
6. [技能体系](#技能体系)
7. [关键设计模式](#关键设计模式)
8. [验证报告](#验证报告)

---

## 系统概览

Hermes Agent 是一个基于 LLM 的自主代理系统，采用**双循环架构**：

- **Why Loop（战略循环）**：持续验证方向（align → research → analysis → retro）
- **How Loop（执行循环）**：快速迭代实现（spec → MVP inner-loop → ship → operate）

两个循环通过 `feedback.jsonl` 与 `evolution-notes.md` 互相驱动，形成自进化闭环。

### 核心特性

- ✅ 147 个技能（17 个原生 + 130 个借用）
- ✅ 9 个 Kanban Profile 并行协作
- ✅ 20+ 消息平台集成（Telegram、Discord、飞书、钉钉等）
- ✅ 6 种执行环境（Local、Docker、SSH、Modal、Daytona、Singularity）
- ✅ SQLite WAL + CAS 并发控制
- ✅ 多凭据池和自动 failover

### 系统验证结果

```
技能系统:     147/147 ✅ (100%)
流水线资产:    19/19  ✅ (100%)
核心模块:     15/17  ✅ (88%)
整体状态:     HEALTHY ✅
```

---

## 核心架构

### 入口点

```
cli.py / gateway/run.py
  ↓
hermes_cli/config.py (load_config)
  ↓
run_agent.py (AIAgent 类)
  ↓
agent/conversation_loop.py (run_conversation)
```

### AIAgent 核心组件

**位置**: `run_agent.py` (根目录，非 `agent/` 子目录)

```python
class AIAgent:
    def __init__(self, config, tools, memory):
        self.model = config["model"]
        self.context_engine = ContextEngine(config)
        self.memory_manager = MemoryManager(config)
        self.credential_pool = CredentialPool(config)

    def run_conversation(self, messages):
        # 1. 上下文压缩检查
        if self.context_engine.should_compress(messages):
            messages = self.context_engine.compress(messages)

        # 2. 工具调用循环
        while True:
            response = self.llm.chat(messages)
            if response.has_tool_calls():
                results = self.execute_tools(response.tool_calls)
                messages.append(results)
            else:
                return response.content
```

### 模块依赖关系

```
cli.py / gateway/run.py
  ├── hermes_cli/config.py (配置加载)
  ├── hermes_cli/kanban.py (看板 CLI)
  ├── hermes_cli/kanban_db.py (SQLite 数据层)
  ├── hermes_cli/profiles.py (Profile 管理)
  │
  ├── run_agent.py (AIAgent)
  │   ├── agent/conversation_loop.py (对话循环)
  │   ├── agent/system_prompt.py (系统提示词)
  │   ├── agent/context_engine.py (上下文压缩)
  │   ├── agent/memory_manager.py (记忆管理)
  │   ├── agent/credential_pool.py (凭据池)
  │   └── agent/tool_executor.py (工具执行)
  │
  ├── tools/registry.py (工具注册中心)
  │   ├── tools/terminal_tool.py (命令执行)
  │   ├── tools/file_operations.py (文件操作)
  │   ├── tools/code_execution_tool.py (代码执行)
  │   ├── tools/mcp_tool.py (MCP 协议)
  │   └── tools/environments/ (6 种环境)
  │
  └── gateway/run.py (GatewayRunner)
      ├── gateway/platforms/ (20+ 平台适配器)
      ├── gateway/session.py (会话管理)
      └── gateway/stream_consumer.py (流式处理)
```

### 配置层次结构

```
优先级从高到低:
1. 命令行参数 (--model, --toolsets, ...)
2. 环境变量 (OPENAI_API_KEY, HERMES_*, ...)
3. ~/.hermes/.env (API 密钥和 secrets)
4. ~/.hermes/config.yaml (用户配置)
5. DEFAULT_CONFIG (代码内默认值)
```

**config.yaml 主要分区**:

```yaml
model:           # 模型配置
  provider: alibaba-coding-plan
  default: qwen3.7-plus
  context_length: 1000000

auxiliary:       # 辅助 LLM
  compression: qwen3-coder-plus
  background_review: qwen3-coder-plus

terminal:        # 终端配置
  backend: local  # local/docker/ssh/modal/daytona/singularity
  ssh_host: 113.98.62.224
  ssh_port: 55084
  ssh_user: test
  ssh_key: ~/.ssh/id_ed25519_deploy

toolsets:        # 工具集
  enabled:
    - terminal
    - file_operations
    - code_execution
    - mcp

context:         # 上下文管理
  compression_threshold: 0.75
  engine: default

credential_pool: # 凭据池策略
  strategy: round_robin  # fill_first/round_robin/random/least_used

plugins:         # 插件
  enabled:
    - memory
    - kanban

custom_providers: # 自定义 OpenAI 兼容端点
  - name: alibaba-coding-plan
    base_url: https://coding.dashscope.aliyuncs.com/v1

delegation:      # 子 agent 配置
  max_concurrent: 5
  max_depth: 3

skills:          # 技能配置
  auto_load: true
  trigger_conditions:
    - 优化
    - 重构
    - 部署

memory:          # 记忆提供者
  provider: file
  path: ~/.hermes/memories/
```

---

## Gateway 消息平台集成

### 架构概览

```
消息平台 (Telegram/Discord/飞书/钉钉/...)
  ↓
BasePlatformAdapter (适配器基类)
  ↓
GatewayRunner (核心控制器)
  ↓
SessionStore (会话管理)
  ↓
AIAgent (对话处理)
  ↓
响应流式返回
```

### 支持的平台 (20+)

| 平台 | 适配器文件 | 连接方式 |
|------|-----------|---------|
| Telegram | `platforms/telegram.py` | Bot Token + python-telegram-bot |
| Discord | `platforms/discord.py` | Bot Token + discord.py |
| 飞书 | `platforms/feishu.py` | WebSocket + lark-oapi |
| 钉钉 | `platforms/dingtalk.py` | dingtalk-stream SDK |
| Slack | `platforms/slack.py` | Bot Token + slack-bolt |
| WhatsApp | `platforms/whatsapp.py` | Node.js bridge |
| Signal | `platforms/signal.py` | HTTP API (signal-cli) |
| Matrix | `platforms/matrix.py` | mautrix SDK |
| Email | `platforms/email.py` | IMAP + SMTP |
| SMS | `platforms/sms.py` | Twilio API |
| WeCom | `platforms/wecom.py` | aiohttp + WebSocket |
| Weixin | `platforms/weixin.py` | iLink Bot API |
| BlueBubbles | `platforms/bluebubbles.py` | iMessage via BlueBubbles |
| QQBot | `platforms/qqbot/` | QQ 官方 Bot API v2 |
| Yuanbao | `platforms/yuanbao.py` | WebSocket |
| HomeAssistant | `platforms/homeassistant.py` | REST API |
| API Server | `platforms/api_server.py` | HTTP REST |
| Webhook | `platforms/webhook.py` | HTTP webhook |

### 会话管理

**Session Key 生成**:

```
格式: agent:main:{platform}:{chat_type}:{chat_id}[:{thread_id}][:{user_id}]

示例:
- DM:      agent:main:telegram:dm:123456789
- 群组:    agent:main:telegram:group:987654321:111222333
- 线程:    agent:main:discord:channel:555666777:999000111
```

**SessionStore 特性**:

- 主存储: SQLite (`SessionDB`)
- 索引: `sessions.json` (session_key → SessionEntry)
- 过期策略: daily/idle/both/none (可配置)
- 自动清理: `prune_old_entries(max_age_days=90)`
- 崩溃恢复: `suspend_recently_active()` 标记中断的会话

### 流式处理

```
Agent (sync worker thread)
  → stream_delta_callback(text)
  → queue.Queue.put()
  → GatewayStreamConsumer.run() (async task)
  → 缓冲 + 限速 (edit_interval=0.8s)
  → adapter.edit_message() 或 adapter.send_draft()
```

### 错误恢复

- **平台重连**: 指数退避，初始 30 秒，最多 5 次重试
- **会话恢复**: `resume_pending` 标记中断的会话，重启后自动恢复
- **优雅关闭**: drain 机制等待 agent 完成，超时则中断

---

## Kanban 多 Profile 协作系统

### 架构概览

```
用户/Chat
  ↓
hermes kanban create --triage
  ↓
[triage 列] ← Dispatcher (60s tick)
  ↓
auto_decompose?
  ├─ Yes → LLM decomposer → fan-out graph
  └─ No  → LLM specifier → single task
  ↓
[ready 列] ← claim_task() [CAS 原子操作]
  ↓
[running 列] ← _default_spawn() → Popen(hermes -p <profile>)
  ↓
Worker Process (独立 HERMES_HOME)
  ↓
kanban_complete → [done 列]
```

### 9 个 Profile

| Profile | 职责 | 阶段 |
|---------|------|------|
| pm-aligner | 对齐需求，消除歧义 | align |
| pm-researcher | 竞品调研，市场分析 | research |
| pm-analyst | 技术分析，架构设计 | analysis |
| pm-planner | 规格定义，任务拆解 | spec |
| pm-builder | MVP 实现，代码编写 | mvp |
| pm-shipper | 部署上线，文档整理 | ship |
| pm-operator | 运维监控，故障处理 | operate |
| pm-growth | 增长策略，数据分析 | grow |
| pm-orchestrator | 任务编排，依赖管理 | 全局 |

### 数据库 Schema

```sql
-- 任务表
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,           -- t_<hex> 格式
  title TEXT NOT NULL,
  body TEXT,                     -- 任务详细 spec
  assignee TEXT,                 -- profile name
  status TEXT NOT NULL,          -- triage/todo/ready/running/done/blocked/archived
  priority INTEGER DEFAULT 0,
  created_by TEXT,
  created_at INTEGER NOT NULL,
  started_at INTEGER,
  completed_at INTEGER,
  workspace_kind TEXT,           -- scratch/worktree/dir
  workspace_path TEXT,
  branch_name TEXT,
  claim_lock TEXT,               -- CAS 并发控制令牌
  claim_expires INTEGER,
  tenant TEXT,
  result TEXT,
  idempotency_key TEXT,
  consecutive_failures INTEGER,
  worker_pid INTEGER,
  last_failure_error TEXT,
  max_runtime_seconds INTEGER,
  last_heartbeat_at INTEGER,
  current_run_id INTEGER,
  skills TEXT,                   -- JSON 数组
  model_override TEXT,
  max_retries INTEGER,
  meta TEXT,                     -- 扩展元数据 JSON
  goal_mode INTEGER,
  goal_max_turns INTEGER,
  session_id TEXT
);

-- 任务链接表（依赖关系）
CREATE TABLE task_links (
  parent_id TEXT,
  child_id TEXT,
  PRIMARY KEY (parent_id, child_id)
);

-- 任务运行历史表
CREATE TABLE task_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT,
  profile TEXT,
  status TEXT,
  outcome TEXT,
  summary TEXT,
  metadata TEXT,
  error TEXT
);

-- 任务评论表
CREATE TABLE task_comments (
  id INTEGER PRIMARY KEY,
  task_id TEXT,
  author TEXT,
  body TEXT,
  created_at INTEGER
);

-- 任务事件表
CREATE TABLE task_events (
  id INTEGER PRIMARY KEY,
  task_id TEXT,
  run_id INTEGER,
  kind TEXT,
  payload TEXT,
  created_at INTEGER
);
```

### 并发控制：CAS (Compare-And-Swap)

```python
# claim_task() 的核心 SQL — 原子 CAS
UPDATE tasks
   SET status        = 'running',
       claim_lock    = ?,        # 唯一 claimer ID (host:pid:random)
       claim_expires = ?,        # now + TTL
       started_at    = COALESCE(started_at, ?)
 WHERE id = ?
   AND status = 'ready'
   AND claim_lock IS NULL        # CAS 条件
```

**关键设计**:

- WAL 模式 + `BEGIN IMMEDIATE` 写事务
- SQLite WAL 锁序列化所有写者，最多一个 claimer 赢得任务
- 失败者观察到 `rowcount == 0`，直接退出，无重试循环
- Claim TTL 默认 15 分钟
- 心跳机制：worker 调用 `heartbeat_claim()` 续期

### 任务状态机

```
[创建] → triage → todo → ready → running → done → archived
                         ↓        ↓
                      blocked  review → running (review agent)
                         ↓        ↓
                       ready    done
```

### 多 Board 支持

每个 Board 是独立的 SQLite 数据库，实现项目级隔离：

```
<root>/kanban.db                          # default board (向后兼容)
<root>/kanban/boards/<slug>/kanban.db     # 命名 boards
<root>/kanban/boards/<slug>/workspaces/   # 每 board 独立工作区
<root>/kanban/boards/<slug>/logs/         # 每 board 独立日志
<root>/kanban/current                     # 当前选中 board
```

---

## 工具链与环境系统

### 工具注册机制

**位置**: `tools/registry.py`

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.discover_builtin_tools()

    def discover_builtin_tools(self):
        # 扫描 tools/*.py → AST 分析 registry.register() 调用
        for py_file in Path("tools").glob("*.py"):
            module = importlib.import_module(f"tools.{py_file.stem}")

    def register(self, name, schema, handler, check_fn=None):
        self.tools[name] = {
            "schema": schema,
            "handler": handler,
            "check_fn": check_fn,
        }

    def dispatch(self, name, args):
        tool = self.tools[name]
        if tool["check_fn"] and not tool["check_fn"]():
            raise ToolUnavailableError(f"Tool {name} is not available")
        return tool["handler"](args)
```

### 核心工具

#### 1. terminal_tool.py (命令执行)

**职责**: 统一入口，将 shell 命令分发到 6 种后端环境

**关键特性**:

- 环境工厂模式: `_create_environment()` 根据配置选择后端
- 全局环境缓存: `_active_environments` 字典 + `_env_lock` 读写锁
- 危险命令审批系统: `DANGEROUS_PATTERNS` 正则匹配 + 三级审批
- 后台任务支持: `background=True` 时通过 `process_registry` 跟踪
- sudo 处理: `_transform_sudo_command()` 自动输入密码
- 环境变量净化: `_HERMES_PROVIDER_ENV_BLOCKLIST` 阻止 80+ 个敏感变量泄漏

#### 2. file_operations.py (文件操作)

**核心设计**: 所有文件操作都表达为 shell 命令，通过 `terminal_env.execute()` 统一执行

```python
class ShellFileOperations:
    def read_file(self, path) -> ReadResult: ...
    def write_file(self, path, content) -> WriteResult: ...
    def patch(self, path, old, new) -> PatchResult: ...
    def search(self, pattern, target, path) -> SearchResult: ...
```

**安全机制**:

- `WRITE_DENIED_PATHS`: 阻止写入敏感路径
- `path_security.py`: `validate_within_dir()` 防止路径穿越
- `binary_extensions.py`: 自动检测二进制文件避免损坏

#### 3. code_execution_tool.py (PTC 沙箱执行)

**架构**: 让 LLM 编写 Python 脚本，通过 RPC 调用 Hermes 工具

**两种传输模式**:

| 特性 | Local (UDS/TCP) | Remote (File-based RPC) |
|------|-----------------|------------------------|
| 传输 | Unix domain socket | 请求/响应文件轮询 |
| 适用 | `env_type == "local"` | Docker/SSH/Modal/Daytona |
| 沙箱位置 | 子进程 (scrubbed env) | 远程环境内 |

**工具白名单**: `web_search`, `web_extract`, `read_file`, `write_file`, `search_files`, `patch`, `terminal`

#### 4. mcp_tool.py (MCP 协议集成)

**支持的传输**: stdio、Streamable HTTP、SSE

**关键特性**:

- 自动重连: 指数退避，最多 5 次重试
- 动态工具发现: 监听 `notifications/tools/list_changed`
- Sampling 支持: MCP 服务器可请求 LLM 补全
- OAuth 2.0: 处理服务器认证流

### 环境系统

**抽象层**: `tools/environments/base.py`

```python
class BaseEnvironment(ABC):
    def execute(self, command, cwd=None, timeout=30, stdin_data=None):
        self._before_execute()           # Hook: 文件同步
        wrapped = self._wrap_command()   # 注入 snapshot + cd + CWD marker
        proc = self._run_bash(wrapped)   # 子类实现
        result = self._wait_for_process(proc, timeout)
        self._update_cwd(result)
        return result

    @abstractmethod
    def _run_bash(self, cmd_string, *, login=False, timeout=30, stdin_data=None): ...
```

### 6 种执行环境对比

| 后端 | 执行方式 | 文件系统 | 持久化 | 安全隔离 | 文件同步 |
|------|---------|---------|--------|---------|---------|
| **Local** | `subprocess.Popen(bash -c)` | host FS | CWD 文件 | 进程组隔离 | 不需要 |
| **Docker** | `docker exec` | bind mount | bind mount | cap-drop ALL | 不需要 |
| **SSH** | `ssh ControlMaster` | 远程 FS | FileSyncManager | SSH 隔离 | FileSyncManager |
| **Modal** | `Sandbox.exec` (async) | 云 sandbox | snapshot | Modal 沙箱 | FileSyncManager |
| **Daytona** | `sandbox.process.exec` | 云 sandbox | stop/start | Daytona 沙箱 | FileSyncManager |
| **Singularity** | `apptainer exec` | overlay | overlay | containall | 不需要 |

### 权限控制层级

```
Layer 1: Tool Availability
  └─ check_fn() → 环境依赖检查 (TTL 30s)

Layer 2: Dangerous Command Detection
  └─ DANGEROUS_PATTERNS (正则) → 匹配危险命令

Layer 3: Approval System
  └─ CLI 交互 / Gateway 异步队列 / Smart Approval (辅助 LLM)

Layer 4: Sandbox Restrictions
  └─ execute_code: 7 工具白名单 + 50 次调用限制

Layer 5: Output Sanitization
  └─ redact_sensitive_text() → 移除泄漏密钥
```

---

## 技能体系

### 技能分类

**总计**: 147 个技能

| 类别 | 数量 | 说明 |
|------|------|------|
| 原生技能 | 17 | 由 Hermes 团队开发，深度集成 |
| 借用技能 | 130 | 从社区借用，适配 Hermes 工作流 |

### 原生技能清单

| 技能名称 | 版本 | 用途 |
|---------|------|------|
| pm-idea-to-mvp | 9.1.0 | 主流水线：从想法到 MVP |
| openspec | 1.0.0 | 规格驱动开发 |
| writing-plans | 1.0.0 | 任务拆解 |
| grill-me | 1.0.0 | 想法对齐 |
| grill-with-docs | 1.0.0 | 文档对齐 |
| dogfood | 1.0.0 | 探索性 QA 测试 |
| docs-hygiene | 1.0.0 | 文档 SSOT 规则 |
| c4-architecture | 1.0.0 | C4 架构模型 |
| open-design | 2.0.0 | 静态 HTML 原型 |
| requesting-code-review | 3.0.0 | 代码审查 |
| subagent-driven-development | 1.1.0 | 子代理开发 |
| test-driven-development | 1.1.0 | TDD |
| ui-acceptance-review | 2.0.0 | UX/UI 验收 |
| ui-ux-pro-max | 1.0.0 | 设计系统 tokens |
| user-journey | 1.0.0 | 用户旅程地图 |
| pm-git-publish | 2.0.0 | Git 发布 |
| prd-red-team-panel | 1.1.0 | PRD 红队审查 |

### 主流水线技能：pm-idea-to-mvp

**版本**: 9.1.0
**核心特性**: Loop Engineering + 强制治理 + Agent 行为准则 + Hermes UX

**10 个阶段**:

| 阶段 | Profile | 产物 | Gate |
|------|---------|------|------|
| 0 brief | User | 00-brief.md | 想法捕获 |
| 1 align | pm-aligner | CONTEXT.md, decisions.md | G1 |
| 2 research | pm-researcher | 01-research.md | ≥5 URLs |
| 3 analysis | pm-analyst | 02-analysis.md, c4-*.md | C4 L1-L3 |
| 4 spec | pm-planner | 03-prd.md, 02b-prototype/ | G2 |
| 5 mvp | pm-builder | 04-mvp/, UX-REVIEW.md | G3 |
| 6 ship | pm-shipper | RUNBOOK.md | 部署就绪 |
| 7 operate | pm-operator | ops notes | - |
| 8 grow | pm-growth | 06-growth.md | - |
| 9 retro | pm-builder | 05-retro.md | 进化提案 |

**场景路由**:

- greenfield: 默认 0→1 流程
- brownfield: 从 analysis 开始
- refine: 从 mvp 开始
- optimize: 从 analysis 开始

### 技能目录结构

```
D:\hermes-data\skills\
├── product-management/          # 产品管理技能 (17 个)
├── software-development/        # 软件开发技能
├── workflow/                    # 工作流技能
├── devops/                      # 运维技能
├── borrowed/                    # 借用技能 (130 个)
└── pipelines/                   # 流水线技能
    └── pm-idea-to-mvp/
        ├── SKILL.md
        ├── CHANGELOG.md
        ├── scripts/             # 自动化脚本
        ├── assets/              # 模板文件
        └── references/          # 参考文档
```

---

## 关键设计模式

| 模式 | 应用位置 | 说明 |
|------|----------|------|
| 注册表模式 | `tools/registry.py` | 工具自注册，AST 静态分析发现 |
| 策略模式 | `credential_pool.py` | 4 种凭据选择策略 |
| 模板方法 | `base.py` (environments) | 抽象基类定义执行接口 |
| 适配器模式 | `BasePlatformAdapter` | 统一接口，20+ 具体实现 |
| 观察者模式 | `HookRegistry` | 生命周期钩子 |
| 工厂模式 | `terminal_tool.py` | 环境创建工厂 |
| 单例模式 | `ToolRegistry` | 全局唯一工具注册表 |
| 命令模式 | `kanban.py` | CLI 命令分发 |
| 责任链模式 | 权限控制 | 5 层安全检查 |
| 状态模式 | `kanban_db.py` | 任务状态机 |
| 延迟导入 | 全局 (`_ra()` 模式) | 打破循环依赖 |
| LRU + TTL | gateway agent cache | 128 上限 + 1 小时空闲 TTL |
| CAS | `kanban_db.py` | WAL + BEGIN IMMEDIATE 原子 claim |
| ContextVar | `session_context.py` | 任务级会话状态隔离 |

---

## 验证报告

### 验证时间

2026-06-19 17:00:00

### 验证结果

#### 技能系统

```
总计: 147 个技能
通过: 147 个 (100%)
失败: 0 个
```

#### 流水线资产

```
总计: 19 个文件
通过: 19 个 (100%)
失败: 0 个
```

#### 核心模块

```
总计: 17 个模块
通过: 15 个 (88%)
警告: 2 个 (12%)
失败: 0 个

通过模块:
✅ hermes_cli.config.load_config
✅ hermes_cli.kanban.kanban_command
✅ hermes_cli.kanban_db.connect
✅ hermes_cli.profiles.list_profiles
✅ gateway.run.GatewayRunner
✅ tools.file_operations.ShellFileOperations
✅ tools.code_execution_tool.execute_code
✅ tools.environments.ssh.SSHEnvironment
✅ tools.environments.local.LocalEnvironment
✅ tools.environments.docker.DockerEnvironment
✅ agent.credential_pool.CredentialPool
✅ agent.context_engine.ContextEngine
✅ agent.system_prompt.build_system_prompt
✅ agent.memory_manager.MemoryManager
✅ agent.conversation_loop.run_conversation

警告模块:
⚠️ agent.prompt_builder.PromptBuilder (属性名变更)
⚠️ AIAgent (位于 run_agent.py 根目录，非 agent/ 子目录)
```

### 整体评估

```
系统状态: HEALTHY ✅

评分:
- 技能完整性: 100% ✅
- 流水线完整性: 100% ✅
- 模块可用性: 88% ✅
- 总体健康度: 96% ✅
```

---

## 附录

### 配置文件位置

```
~/.hermes/
├── config.yaml              # 主配置文件
├── .env                     # 环境变量和 secrets
├── SOUL.md                  # Agent 人格定义
├── memories/                # 记忆存储
├── sessions/                # 会话历史
├── skills/                  # 技能目录
├── kanban.db                # 看板数据库
├── kanban/                  # 看板相关文件
│   ├── boards/              # 多 board 支持
│   ├── workspaces/          # 工作区
│   └── logs/                # 任务日志
└── profiles/                # Profile 目录
    ├── pm-aligner/
    ├── pm-researcher/
    └── ...
```

### 常用命令

```bash
# 启动 Gateway
hermes gateway start

# 启动 CLI
hermes chat

# 看板操作
hermes kanban create --title "New task" --assignee pm-builder
hermes kanban list
hermes kanban update <task_id> --status done

# 配置管理
hermes config set model.default qwen3.7-plus
hermes config get model

# 技能管理
hermes skills list
hermes skills install <skill_name>

# Profile 管理
hermes profile list
hermes profile create pm-custom
```

---

**文档版本**: v1.0
**最后更新**: 2026-06-19
**维护者**: Hermes Team
