# Git 工作流（ttmens-skills）

## SSOT

- **Git 仓库**：`https://github.com/ttmens/ttmens-skills`（本地 `D:/workspace/ttmens-skills`）
- **Hermes 运行时技能**：`D:/hermes-data/skills/`（从 repo install/sync，非 Git SSOT）

## 凭据（一次配置）

Token 存放在 **`D:/hermes-data/.env`**：

```bash
GITHUB_TOKEN=ghp_...   # https://github.com/settings/tokens
```

Agent 与脚本从此读取，**不要**写进 repo 或聊天记录。

## Push（Agent / 人工）

```powershell
cd D:\workspace\ttmens-skills
powershell -NoProfile -File scripts/push_to_github.ps1
```

`origin` 应指向 `https://github.com/ttmens/ttmens-skills.git`（脚本会自动设置）。

## Pull 网络 fallback

若 `git pull` 失败，见 [`domains/qa/ttmens-skills-sync/SKILL.md`](../domains/qa/ttmens-skills-sync/SKILL.md) 的 API zip 流程。

## Cursor 持久规则

- `D:/hermes-data/.cursor/rules/github-ttmens-workflow.mdc`
- `D:/workspace/ttmens-skills/.cursor/rules/github-push.mdc`

Agent 在「同步 git / push」类任务中应自动使用上述脚本，无需用户重复提醒。
