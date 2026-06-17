# 部署陷阱参考（从 SKILL.md 提取）

> 来源：pm-knowledge-platform、pm-portfolio-hub 等项目实战复盘。
> 部署前必读，避免重复踩坑。

## Next.js standalone + PM2 部署配置

当 `next.config.js` 设置 `output: 'standalone'` 时，PM2 ecosystem.config.js 必须指向 standalone server.js，不能用 `next start`：

```js
// ecosystem.config.js — standalone 模式正确配置
{
  name: 'pm-web',
  script: 'packages/web/.next/standalone/packages/web/server.js',  // ← 关键路径
  cwd: '/path/to/project',  // ← 必须是项目根目录
  env: { NODE_ENV: 'production', PORT: 3000, HOSTNAME: '0.0.0.0' },
}
```

构建后必须手动同步静态文件：`cp -r .next/static .next/standalone/.next/`。否则 CSS/JS 全部 404（HTML 200 但页面白屏）。

常见错误：PM2 日志出现 `⚠ "next start" does not work with "output: standalone"` 说明配置指向了错误的 script。

## AuthProvider 加载卡死诊断

页面一直显示 loading spinner（AppShell 的 `if (isLoading)` 分支），但 API 全部正常时的排查路径：

1. `localStorage.getItem('token')` 是否存在？→ 不存在则登录流程有问题
2. `fetch('/api/auth/me', {headers: {Authorization: ...}})` 是否返回正确格式？→ 检查响应 key 是否匹配前端期望（`res.data.user` vs `res.data` 直接是 user）
3. AuthProvider useEffect 中 `.catch()` 是否静默删除 token？→ 加 `console.error` 看实际错误
4. 浏览器控制台 `document.body.innerHTML` 如果只有 spinner div，说明 React hydration 未完成或 useEffect 卡在 await

关键：`curl` 200 + 浏览器 spinner = 前端 JS 执行问题，不是服务器问题。不要反复重启 PM2。

## API 参数兼容性过渡

前后端并行开发时，前端发送的字段名可能与后端 schema 不一致（如 `query` vs `question`）。后端 zod schema 应同时接受两种名称：

```ts
const schema = z.object({
  question: z.string().min(1).optional(),
  query: z.string().min(1).optional(),
});
// 路由处理中：const q = question || query;
```

避免前端改一个字段名就导致 400 错误。迁移完成后再移除兼容。

## SSE/流式请求 Auth 陷阱

UI 重构时，很容易只关注视觉层而忽略功能层的 API 调用：

- **SSE/流式请求使用原生 `fetch()` 而非 axios**：`fetch()` 不经过 axios 拦截器，不会自动附加 `Authorization` header。重构后这些调用会 401。
- **审计方法**：`grep -rn "fetch(" packages/web/src/` 找出所有原生 fetch 调用，逐一确认是否携带 auth token
- **修复模式**：在 fetch headers 中显式添加 `...(token ? { 'Authorization': \`Bearer ${token}\` } : {})`
- **更深层检查**：重构后必须端到端测试每个页面的核心功能（不只是视觉），特别是：流式聊天、文件上传、WebSocket 连接等不走标准 axios 管线的功能

## Refine 前端大规模升级陷阱

Refine 涉及前端 CSS/JS/HTML 全面升级时（如设计系统 v2→v3），文件通常 >1000 行。此时：

- **禁止**一次性 `write_file` 整个大文件（stream 超时风险极高）
- **禁止**连续多次 `patch` 不做验证（`patch` 在 Windows 上可能报告 `success: true` 但内容未实际写入）
- **正确模式**：`read_file(offset, limit)` 获取精确上下文 → `patch` 单次修改 → `terminal(grep)` 验证关键 token 确实存在 → 下一个 patch
- 每完成一个文件的升级后，用 `terminal(grep -c "keyToken" file)` 做批量验证
- 最终必须运行项目自身的构建/生成命令确认模板语法无误，再跑测试

## Refine 系统性 UI 重构模式（多页面 <500 行场景）

当重构目标是整个应用的交互页面（如 8 个 Next.js 页面），且每个文件 <500 行时：

1. **全量阅读**：先读取所有页面代码，理解当前状态
2. **设计系统先行**：先写 tailwind.config + globals.css（设计 token）
3. **共享组件次之**：重写 sidebar/layout 等影响所有页面的组件
4. **批量写页面**：一次性重写所有页面（比逐个 patch 快 5x）
5. **统一构建验证**：所有页面写完后 `pnpm build`，一次性修复 TypeScript 跨文件错误
6. **部署**：tar 打包上传 → 服务器 build → PM2 restart

关键洞察：对于中等规模文件（200-500 行），`write_file` 比连续 `patch` 更可靠且更快。TypeScript 严格模式会捕获跨文件类型错误，统一构建比逐文件验证更高效。
