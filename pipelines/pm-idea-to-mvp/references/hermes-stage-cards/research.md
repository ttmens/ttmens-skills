# Research — Stage Card (v7.0)

**Profile**: `pm-researcher` | **Stage**: `research`

## Outputs

- `01-research.md` (≥5 URLs, competitor table)

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 2（管理困惑）**：来源打不开时不要默默跳过，要 fallback
- **准则 6（验证）**：URL 必须验证可访问性

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "这个来源打不开，跳过" | 必须 fallback 到 browser 或替代来源 |
| "竞品已经够多了，5 个够了" | 5 个是底线不是目标。置信度不足时继续搜 |
| "中文来源太难找" | 用 Tavily + browser 双通道。中文市场的产品必须有中文来源 |
| "这个 URL 看起来对，不用验证" | 404 链接进入正式产物 = 信誉损失 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | 只搜英文忽略中文来源 | 竞品分析不完整 | 双语搜索 |
| 2 | URL 不验证 | 404 链接进入产物 | HTTP 200 抽检 |
| 3 | 来源 <5 就结束 | 置信度不足 | 最低 5 URLs |
| 4 | 只搜不读（标题党） | 信息质量低 | 必须 web_extract 读内容 |

## Exit (mandatory)

Verify artifact paths from the main pipeline SKILL exist under `{PROJECT_ROOT}`.
Update `PROGRESS.md` stage status.
