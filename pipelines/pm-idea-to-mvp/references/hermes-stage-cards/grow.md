# Grow — Stage Card (v7.0)

**Profile**: `pm-growth` | **Stage**: `grow`

## Outputs

- `06-growth.md` (NSM + GTM)

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 1（假设前置）**：增长策略基于什么假设？用户增长 = 产品好？
- **准则 4（简洁）**：GTM 策略要可执行，不要写 20 页 PPT

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "增长策略随便写写就行" | 最低 30 行。NSM + GTM 是产品方向 |
| "北极星指标不重要" | 没有 NSM = 没有方向 |
| "GTM 是市场的事" | PM 必须定义 GTM 的技术可行性 |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | growth.md 低于 30 行 | 敷衍产物 | 最低行数检查 |
| 2 | 无 NSM 定义 | 增长无方向 | pm-north-star-metric 技能 |
| 3 | GTM 不可执行 | 纸上谈兵 | GTM 含具体渠道 + 预算 |

## Exit (mandatory)

Verify artifact paths from the main pipeline SKILL exist under `{PROJECT_ROOT}`.
Update `PROGRESS.md` stage status.
