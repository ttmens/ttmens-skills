# Retro — Stage Card (v7.0)

**Profile**: `pm-builder` | **Stage**: `retro`

## Outputs

- `05-retro.md`, `harness-improvements.md`, `evolution-notes.md`

## 行为准则

加载 `references/agent-behavior-code.md` — 特别是：
- **准则 2（管理困惑）**：retro 中遇到"不知道为什么成功/失败"要深挖
- **准则 6（验证）**：retro 的教训必须有数据支撑，不是感觉

## 反合理化表格

| 常见合理化 | 现实 |
|-----------|------|
| "这次没什么特别的教训" | 没有教训 = 没认真观察。至少 3 条 |
| "retro 随便写写就行" | 最低 50 行。retro 是进化的驱动力 |
| "harness 不需要改进" | 每次运行都有改进空间。至少提 1 个提案 |
| "量化指标太难收集了" | 没有量化的 retro = 空洞的 retro |

## 失败模式

| # | 失败模式 | 后果 | 预防 |
|---|---------|------|------|
| 1 | retro 低于 50 行 | 敷衍产物 | 最低行数检查 |
| 2 | 无量化指标 | 教训不可验证 | 阶段耗时 + 迭代次数 |
| 3 | 无 harness 改进提案 | 流水线不进化 | harness-improvements.md 必需 |
| 4 | 跳过 feedback.jsonl 消费 | 用户反馈丢失 | consume-feedback.py 必须运行 |

## Exit (mandatory)

Verify artifact paths from the main pipeline SKILL exist under `{PROJECT_ROOT}`.
Update `PROGRESS.md` stage status.
