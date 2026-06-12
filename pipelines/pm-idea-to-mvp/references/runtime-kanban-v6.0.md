# Runtime Kanban v6.0 — 运行时详解

> pm-idea-to-mvp v6.0 的 Kanban 系统、Harness Rules、Goal Verification 和 Progress Tracking 集成指南

## 1. v6.0 Kanban 阶段图（含 Inner Loop）

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Why Loop (战略循环)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [Brief] ──→ [Align] ──→ [Research] ──→ [Analysis] ──→ [Spec]    │
│     │           │ G1          │              │            │ G2      │
│     │           │             │              │            │         │
│     │           │             └──────────────┘            │         │
│     │           │           [backtrack if gap]            │         │
│     │           │                                         │         │
│     │           └─────────────────────────────────────────┘         │
│     │                                                             │
│     └─────────────────────────────────────────────────────────────┘
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                         How Loop (战术循环)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  [Spec] ──→ [MVP] ──→ [Ship] ──→ [Operate] ──→ [Grow] ──→ [Retro]│
│     │         │ G3       │ human      │           │          │     │
│     │         │          │            │           │          │     │
│     │         │          │            │           │          │     │
│     │         └──┐       │            │           │          │     │
│     │            │       │            │           │          │     │
│     │     ┌──────▼──────┐│            │           │          │     │
│     │     │ Inner Loop  ││            │           │          │     │
│     │     │ test→fix→   ││            │           │          │     │
│     │     │ rebuild     ││            │           │          │     │
│     │     │ (max 3x)    ││            │           │          │     │
│     │     └──────┬──────┘│            │           │          │     │
│     │            │       │            │           │          │     │
│     │     [backtrack to Spec         │           │          │     │
│     │      if design flaw]           │           │          │     │
│     │                                │           │          │     │
│     └────────────────────────────────┘           │          │     │
│                                                  │          │     │
│                                                  └──────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.1 阶段状态机

每个阶段有 4 种状态：
- `pending`：未开始
- `running`：执行中
- `passed`：目标验证通过
- `blocked`：等待人工或 backtrack

### 1.2 Inner Loop 状态机

```
idle → running → [pass] → idle (exit to Ship)
                → [fail, iter < 3] → running (retry)
                → [fail, iter = 3, design_flaw] → backtracked (→ Spec)
                → [fail, iter = 3, no_design_flaw] → blocked (→ human)
```

## 2. Profiles 表（v6.0 更新）

| Profile | 职责 | 绑定的 Skills | 触发条件 |
|---------|------|---------------|----------|
| **orchestrator** | 阶段流转、gate 检查、harness 执行 | kanban-skill, goal-check, progress-tracker | 用户说"继续 pm-{slug}" |
| **pm-aligner** | Align 阶段：问题域、成功标准、术语表 | pm-aligner, context-builder | current_phase = align |
| **pm-researcher** | Research 阶段：竞品、技术调研、URL 收集 | pm-researcher, web-search | current_phase = research |
| **pm-analyst** | Analysis 阶段：方案对比、C4 架构 | pm-analyst, c4-modeler | current_phase = analysis |
| **pm-spec-writer** | Spec 阶段：PRD、用户故事、OpenSpec | pm-spec-writer, openspec | current_phase = spec |
| **pm-builder** | MVP 阶段：代码实现、测试、inner loop | pm-builder, pytest-runner | current_phase = mvp |
| **pm-shipper** | Ship 阶段：部署、RUNBOOK、UI 验收 | pm-shipper, deploy-helper | current_phase = ship |
| **pm-operator** | Operate 阶段：监控、告警、健康检查 | pm-operator, health-monitor | current_phase = operate |
| **pm-grower** | Grow 阶段：功能扩展、用户反馈 | pm-grower, feedback-analyzer | current_phase = grow |
| **pm-retrospector** | Retro 阶段：反思、evolution、skill_patch | pm-retrospector, skill-patcher | current_phase = retro |

### 2.1 Profile 切换协议

```python
# orchestrator 的 phase_transition 逻辑
def transition_to(next_phase):
    # 1. 验证当前阶段 goals
    if not goal_check(current_phase):
        return blocked(f"Goals not met for {current_phase}")
    
    # 2. 检查 checkpoint 类型
    checkpoint = gates.stages[next_phase].checkpoint
    if checkpoint == 'human':
        return blocked(f"Waiting for human approval at {next_phase}")
    
    # 3. 更新 workflow_state
    state.current_phase = next_phase
    state.gates[f"g{n}_{next_phase}"] = 'passed'
    
    # 4. 更新 PROGRESS.md
    progress_tracker.update_stage(next_phase, status='running')
    
    # 5. 加载对应 profile
    load_profile(f"pm-{next_phase}")
```

## 3. Harness Rules 集成

### 3.1 决策分类与处理

当流水线遇到决策点时，orchestrator 查询 `harness-rules.yaml`：

```python
def handle_decision(decision_type, context):
    rule = harness_rules.decisions[decision_type]
    risk = rule.risk
    action = rule.action
    
    if action == 'auto_verify':
        # 低风险：自动执行，记录日志
        execute_decision(context)
        log_decision(decision_type, 'auto', context)
        return 'proceeded'
    
    elif action == 'write_adr_and_notify':
        # 中风险：写 ADR，通知人类，继续执行
        adr = write_adr(decision_type, context)
        notify_human(f"Decision made: {decision_type}. See {adr}")
        log_decision(decision_type, 'adr', context)
        return 'proceeded_with_adr'
    
    elif action == 'human_checkpoint':
        # 高风险：阻塞，等待人工批准
        notify_human(f"Approval needed: {decision_type}")
        log_decision(decision_type, 'blocked', context)
        return 'blocked'
```

### 3.2 决策类型示例

| 决策类型 | 场景 | Risk | Action |
|----------|------|------|--------|
| `research_supplement` | 发现竞品分析缺少 2 个 URL | low | auto_verify |
| `tech_choice` | 选择 FastAPI vs Flask | medium | write_adr_and_notify |
| `architecture_change` | 添加 Redis 缓存层 | medium | write_adr_and_notify |
| `refactor` | 重构 utils.py 结构 | low | auto_verify |
| `deploy` | 生产环境部署 | high | human_checkpoint |
| `data_migration` | 修改数据库 schema | high | human_checkpoint |
| `scope_change` | PRD 增加用户故事 | medium | write_adr_and_notify |

### 3.3 自定义 Harness Rules

用户可在项目的 `harness-rules.yaml` 中覆盖默认规则：

```yaml
# 项目级覆盖：所有决策都需人工批准（退化为 v5.1 行为）
decisions:
  tech_choice:
    risk: high
    action: human_checkpoint
  refactor:
    risk: medium
    action: write_adr_and_notify

# 或者：完全自动化（适合成熟团队）
decisions:
  deploy:
    risk: medium
    action: write_adr_and_notify
  data_migration:
    risk: medium
    action: write_adr_and_notify
```

## 4. Goal Verification 流程

### 4.1 Goal 定义结构

每个阶段的 goal 在 `goals/goals.yaml` 中定义：

```yaml
stages:
  mvp:
    - id: M1
      description: 'MVP directory and README exist'
      type: file_exists
      target: '04-mvp/README.md'
    - id: M2
      description: 'Tests pass'
      type: command_pass
      command: 'pytest -q --tb=short'
      workdir: '04-mvp'
      optional: true  # 无测试文件时不阻塞
    - id: M3
      description: 'UX review with P0=0'
      type: file_exists
      target: '04-mvp/UX-REVIEW.md'
```

### 4.2 Goal Check 执行流程

```python
def goal_check(phase):
    goals = load_goals(phase)
    results = []
    
    for goal in goals:
        if goal.type == 'file_exists':
            passed = file_exists(goal.target)
            if goal.min_chars:
                passed = passed and file_size(goal.target) >= goal.min_chars
        
        elif goal.type == 'content_match':
            content = read_file(goal.target)
            matches = regex_findall(goal.pattern, content)
            passed = len(matches) >= goal.get('min_matches', 1)
        
        elif goal.type == 'command_pass':
            exit_code = run_command(goal.command, workdir=goal.workdir)
            passed = (exit_code == 0)
            if goal.optional and exit_code == 127:  # command not found
                passed = True  # 不阻塞
        
        elif goal.type == 'url_count':
            content = read_file(goal.target)
            urls = regex_findall(r'https?://[^\s]+', content)
            passed = len(urls) >= goal.min
        
        elif goal.type == 'forbidden':
            content = read_file(goal.target)
            passed = not regex_search(goal.pattern, content)
        
        results.append({
            'id': goal.id,
            'description': goal.description,
            'passed': passed
        })
    
    all_passed = all(r['passed'] for r in results)
    return all_passed, results
```

### 4.3 Goal Check 输出示例

```
$ goal-check.py mvp

Checking goals for phase: mvp
────────────────────────────────────────
✓ M1: MVP directory and README exist
✓ M2: Tests pass (pytest -q --tb=short)
✗ M3: UX review with P0=0
  └─ Missing: 04-mvp/UX-REVIEW.md

Result: FAILED (2/3 goals met)
Action: Create UX-REVIEW.md before proceeding to Ship
```

## 5. Progress Tracking 集成

### 5.1 PROGRESS.md 结构

```markdown
# 项目进度追踪

## 元信息
| 项 | 值 |
|----|----|
| Slug | stock-copilot |
| 创建时间 | 2026-06-12 10:00 |
| 最后更新 | 2026-06-12 14:45 |
| 当前阶段 | mvp |
| 内循环迭代 | 2/3 |

## 阶段进度
- [x] Stage 0: Brief
- [x] Stage 1: Align (G1)
- [x] Stage 2: Research
- [x] Stage 3: Analysis + C4
- [x] Stage 4: Spec + 原型 (G2)
- [ ] Stage 5: MVP (G3, inner loop)  ← current
- [ ] Stage 6: Ship
- [ ] Stage 7: Operate
- [ ] Stage 8: Grow
- [ ] Stage 9: Retro

## MVP 任务明细
| 任务 | 状态 | 负责人 |
|------|------|--------|
| 实现 /api/stock/quote | done | pm-builder |
| 实现 /api/stock/history | done | pm-builder |
| 添加单元测试 | in_progress | pm-builder |
| UX review | pending | human |

## 内循环日志
| 迭代 | 时间 | 触发信号 | 结果 | 决策 |
|------|------|----------|------|------|
| 1 | 2026-06-12 14:30 | test_failure | 3 tests failed | 修复 test_auth.py |
| 2 | 2026-06-12 14:45 | lint_clean | all pass | 继续迭代 |
```

### 5.2 Progress Tracker 自动更新

```python
def update_progress(event_type, data):
    progress = read_file('PROGRESS.md')
    
    if event_type == 'phase_transition':
        # 更新当前阶段
        progress = regex_replace(
            r'当前阶段 \| \*\*.+?\*\*',
            f'当前阶段 | **{data["new_phase"]}**',
            progress
        )
        # 更新阶段进度 checkbox
        progress = regex_replace(
            rf'- \[ \] Stage \d+: {data["old_phase"]}',
            f'- [x] Stage {data["stage_num"]}: {data["old_phase"]}',
            progress
        )
        progress = regex_replace(
            rf'- \[ \] Stage \d+: {data["new_phase"]}',
            f'- [ ] Stage {data["stage_num"]}: {data["new_phase"]}  ← current',
            progress
        )
    
    elif event_type == 'inner_loop_iteration':
        # 更新迭代计数
        progress = regex_replace(
            r'内循环迭代 \| \*\*\d+/\d+\*\*',
            f'内循环迭代 | **{data["iteration"]}/{data["max"]}**',
            progress
        )
        # 追加日志行
        log_row = f'| {data["iteration"]} | {data["timestamp"]} | {data["signal"]} | {data["result"]} | {data["decision"]} |'
        progress = append_to_section(progress, '内循环日志', log_row)
    
    write_file('PROGRESS.md', progress)
```

### 5.3 外部集成

PROGRESS.md 可被外部工具读取：

- **Dashboard**：解析 markdown table，渲染为可视化进度条
- **Slack bot**：定期读取 `当前阶段` 和 `内循环迭代`，推送到频道
- **GitHub Action**：在 PR 描述中嵌入 PROGRESS.md 摘要
- **API endpoint**：`GET /api/project/{slug}/progress` 返回 JSON

## 6. 完整运行时流程示例

### 6.1 用户触发

```
用户: 继续 pm-stock-copilot
```

### 6.2 Orchestrator 执行

```python
# 1. 加载 workflow_state
state = load_yaml('workflow_state.yaml')
current_phase = state.current_phase  # 'mvp'

# 2. 检查当前阶段 goals
passed, results = goal_check(current_phase)
if not passed:
    # 3. 进入 inner loop（如果是 MVP 阶段）
    if current_phase == 'mvp':
        iteration = state.inner_loop_state.current_iteration
        if iteration < 3:
            # 执行 inner loop
            run_inner_loop(iteration + 1)
            # 更新 PROGRESS.md
            update_progress('inner_loop_iteration', {...})
            # 重新检查 goals
            passed, results = goal_check('mvp')
        else:
            # 检查 backtrack 条件
            if detect_design_flaw():
                backtrack_to('spec')
            else:
                escalate_to_human()
    
    if not passed:
        return blocked(f"Goals not met: {results}")

# 4. 阶段流转
next_phase = get_next_phase(current_phase)
transition_to(next_phase)

# 5. 加载对应 profile
load_profile(f'pm-{next_phase}')

# 6. 返回给用户
return f"✓ {current_phase} passed. Now in {next_phase}. What's next?"
```

### 6.3 Inner Loop 执行

```python
def run_inner_loop(iteration):
    # 1. 执行 runtime 命令
    test_result = run_command(harness.runtime.test_cmd)
    build_result = run_command(harness.runtime.build_cmd)
    lint_result = run_command(harness.runtime.lint_cmd)
    
    # 2. 收集反馈信号
    signals = {
        'test_results': test_result.exit_code == 0,
        'build_status': build_result.exit_code == 0,
        'lint_clean': lint_result.exit_code == 0
    }
    
    # 3. 分析失败原因
    if not all(signals.values()):
        failure_analysis = analyze_failure(test_result, build_result, lint_result)
        
        # 4. 自动修复（如果是低风险问题）
        if failure_analysis.risk == 'low':
            fix_code(failure_analysis.suggestions)
        
        # 5. 记录迭代
        log_iteration(iteration, signals, failure_analysis)
    
    # 6. 更新 inner_loop_state
    state.inner_loop_state.current_iteration = iteration
    state.inner_loop_state.last_signal = signals
```

## 7. 故障排查

### 7.1 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Goal check 永远失败 | `goals/goals.yaml` 路径错误 | 检查 `target` 字段是否相对于项目根目录 |
| Inner loop 无限循环 | `max_iterations` 未设置 | 在 `harness-rules.yaml` 中设置 `inner_loop.max_iterations: 3` |
| Harness rule 不生效 | `decisions` 字段拼写错误 | 检查 YAML 缩进和键名 |
| PROGRESS.md 不更新 | `progress-tracker.py` 未安装 | 运行 `pip install progress-tracker` 或检查 PATH |
| Profile 加载失败 | Profile 文件不存在 | 检查 `~/.hermes/profiles/pm-{phase}/SKILL.md` |

### 7.2 调试命令

```bash
# 检查当前状态
$ cat workflow_state.yaml

# 手动触发 goal check
$ goal-check.py mvp

# 查看 inner loop 历史
$ grep -A 10 '内循环日志' PROGRESS.md

# 验证 harness-rules 语法
$ python -c "import yaml; yaml.safe_load(open('harness-rules.yaml'))"

# 列出所有 profiles
$ ls ~/.hermes/profiles/ | grep pm-
```

## 8. 参考资源

- [loop-engineering.md](./loop-engineering.md) — 核心理念
- [v6.0-upgrade.md](./v6.0-upgrade.md) — 迁移指南
- [command-recipes.md](./command-recipes.md) — 命令速查
- [quality-rubric.md](./quality-rubric.md) — 质量评分
