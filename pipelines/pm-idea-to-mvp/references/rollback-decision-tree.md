# 回退决策树（v7.1 新增）

> 来源：pm-knowledge-platform 项目实战复盘（2026-06-15）。
> 当修复引入新问题或修复时间过长时，使用此决策树判断是否回退。

## 何时回退？

| 条件 | 动作 | 说明 |
|------|------|------|
| 修复尝试 ≥ 3 次仍未解决 | **回退** | 继续修复的成本 > 回退的成本 |
| 修复引入新的 bug | **回退** | 回归缺陷说明方向错误 |
| 用户明确要求回退 | **立即回退** | 用户信号优先级最高 |
| 修复时间 > 30 分钟 | **暂停** | 通知人类决策，不要继续盲目修复 |
| 修复涉及 > 10 个文件 | **暂停** | 变更规模过大，需要重新评估方案 |

## 回退流程

### Step 1: 确认回退点

```bash
# 查看最近的稳定版本
git log origin/main --oneline -10

# 确认要回退到的 commit
git show <commit_hash>
```

**选择标准**：
- 优先回退到 `origin/main`（GitHub 版本）
- 如果没有稳定的远程版本，回退到上一个本地 commit

### Step 2: 清理本地修改

```bash
# 丢弃所有未提交的修改
git checkout -- .

# 删除未跟踪的文件
git clean -fd

# 确认工作区干净
git status
```

**注意**：如果有一些重要的未提交修改，先 `git stash` 保存。

### Step 3: 重新部署

```bash
# 1. 打包代码
tar -czf /tmp/rollback.tar.gz --exclude='node_modules' --exclude='.next' --exclude='.git' .

# 2. 上传到服务器
scp /tmp/rollback.tar.gz user@server:/path/to/project/

# 3. 服务器端解压
ssh user@server "cd /path/to/project && tar -xzf rollback.tar.gz && rm rollback.tar.gz"

# 4. 重新构建
ssh user@server "cd /path/to/project && pnpm install && pnpm build"

# 5. 重启服务
ssh user@server "pm2 restart all"
```

### Step 4: 浏览器验证

**必须**执行浏览器端到端验证（见 SKILL.md Ship 阶段）：
1. 登录页渲染正常
2. 登录流程成功
3. 首页渲染正常
4. 核心页面无白屏

### Step 5: 记录回退原因

写入 `feedback.jsonl`：

```json
{
  "ts": "2026-06-15T14:30:00+08:00",
  "source": "agent",
  "stage": "ship",
  "signal": "回退到 GitHub 版本",
  "proposed_delta": "修复浏览器渲染问题失败，根因是 standalone 模式 rewrites 不工作",
  "status": "resolved"
}
```

写入 `05-retro.md`（如果是 Retro 阶段）：
- 回退原因
- 修复尝试记录
- 经验教训

## 反合理化表格

| 常见借口 | 反驳 |
|---------|------|
| "再试一次就能修好" | ❌ 已经尝试 3 次了。继续尝试的成本 > 回退的成本。 |
| "回退会丢失进度" | ❌ 回退到稳定版本，然后重新实现。丢失的是错误的实现，不是正确的进度。 |
| "用户会等不及" | ❌ 继续修复可能花更多时间。回退是快速恢复服务的最佳方式。 |
| "我已经投入这么多时间了" | ❌ 沉没成本谬误。未来的时间更宝贵。 |
| "回退显得我很失败" | ❌ 回退是专业决策，不是失败。快速恢复服务比面子重要。 |

## 回退后的恢复流程

### 1. 分析失败原因

```bash
# 查看修复过程中的 git 历史
git reflog

# 查看修改的文件
git diff HEAD@{1} HEAD

# 查看浏览器控制台错误
browser_console "document.body.innerHTML"
```

### 2. 制定新方案

- 重新阅读相关文档（SKILL.md、PRD、设计文档）
- 识别根因（不是表面症状）
- 制定最小化修复方案（改动 < 5 个文件）

### 3. 重新实现

- 使用内循环协议（Plan → Code → Test → Observe）
- 每轮迭代后做浏览器验证
- 最多 3 轮迭代

### 4. 记录经验教训

写入 `evolution-notes.md`：
- 失败模式
- 根因分析
- 预防措施
- 对流水线的改进建议

## 典型场景示例

### 场景 1: 浏览器渲染问题

**症状**：
- curl 200，但浏览器显示 loading spinner
- PM2 状态 online，但页面不可用

**错误做法**：
- 反复重启 PM2
- 修改 AuthProvider 逻辑
- 修改 API 路由

**正确做法**：
1. 浏览器控制台检查 `localStorage.getItem('token')`
2. 检查 `/api/auth/me` 响应格式
3. 如果 3 次尝试未解决 → 回退

### 场景 2: CSS 404

**症状**：
- HTML 200，但页面样式丢失
- 浏览器控制台报 CSS 404

**根因**：
- standalone 模式漏拷静态文件

**正确做法**：
1. 检查 `.next/static` 是否存在
2. 如果不存在 → `cp -r .next/static .next/standalone/.next/`
3. 如果问题持续 → 回退

### 场景 3: API 代理失败

**症状**：
- 前端请求 `/api/*` 返回 404
- 后端 API 正常（curl localhost:3001 正常）

**根因**：
- Next.js rewrites 在 standalone 模式下不工作

**正确做法**：
1. 检查 `next.config.js` 是否有 `output: 'standalone'`
2. 如果有 → 移除 standalone 或使用 middleware 代理
3. 如果修复复杂 → 回退

## 与其他机制的关系

| 机制 | 关系 |
|------|------|
| 内循环协议 | 内循环失败 3 次 → 触发回退决策 |
| 浏览器验证 | 浏览器验证失败 3 次 → 触发回退决策 |
| feedback.jsonl | 回退原因必须记录到 feedback.jsonl |
| evolution-notes.md | 回退经验教训必须记录到 evolution-notes.md |
| harness-improvements.md | 如果是 harness 配置问题 → 写入 harness-improvements.md |
