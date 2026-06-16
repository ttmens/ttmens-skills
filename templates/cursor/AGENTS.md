# pm-idea-to-mvp v7.2.0 — Cursor Agent

## 技能从哪来

1. 运行 `python {SKILLS_ROOT}/scripts/detect_agent_env.py --json`，或按序尝试：
   - 本项目 `.cursor/skills/`（若含 `pm-idea-to-mvp/`）
   - `~/.cursor/skills/`
   - 本机 ttmens-skills 克隆根（含 `marketplace.yaml`）
2. **若缺失**：请用户在本机 ttmens-skills 仓库执行：

```bash
git submodule update --init --recursive
./install.sh --core --profile debate --platform cursor --project .
```

完整分平台说明：读取 `{SKILLS_ROOT}/docs/AGENT_ONBOARDING.md`（安装后路径）。

## 运行时（强制）

- 默认流水线：`pm-idea-to-mvp` v7.2.0 → 读 `{SKILLS_ROOT}/pipelines/pm-idea-to-mvp/SKILL.md`
- 触发语：**从想法做到上线** · 继续 pm-{slug} · 进入 {stage} 阶段
- 每 stage 结束：

```bash
python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/stage-complete.py \
  --project-root . --stage <stage> --verify-goals
```

- MVP 内循环：`python {SKILLS_ROOT}/pipelines/pm-idea-to-mvp/scripts/inner-loop-driver.py --project-root .`
- 用户可见产物：**简体中文**
- 运行时规则：`{SKILLS_ROOT}/AGENTS.md`
