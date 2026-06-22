---
name: task-state-persist
description: "Persist critical task state to survive context compaction. Write checkpoint files for long-running tasks so the agent can resume without re-asking the user."
tags: [state, persistence, context-compaction, checkpoint, resume]
triggers:
  - context compaction
  - 上下文压缩
  - 长任务状态
  - checkpoint
  - resume task
  - 任务恢复
---

# Task State Persist — 关键状态持久化

## When to Use
- Starting any task expected to take 20+ tool calls
- Before context window is likely to compact (long builds, multi-step deploys)
- When task has critical state that's expensive to re-derive
- After user provides information that shouldn't be re-asked

## ⚠️ CRITICAL: Context Compaction Loses Working Memory

**Root cause of "why are you repeating" failures**: after context compaction, the agent loses all intermediate state and re-discovers or re-asks things already known.

**Solution**: Write critical state to a checkpoint file BEFORE compaction happens. After compaction, read the file to resume.

## Checkpoint File Format

Location: `D:/hermes-data/checkpoints/{task-id}.json`

```json
{
  "task_id": "flutter-build-passenger-v2",
  "created_at": "2026-06-22T10:00:00Z",
  "updated_at": "2026-06-22T10:15:00Z",
  "status": "in_progress",
  "phase": "build",
  "completed_steps": [
    "env_setup",
    "jdk_install",
    "android_sdk",
    "plugin_fixes",
    "signing_config"
  ],
  "current_step": "flutter_build_apk",
  "remaining_steps": ["download_apk", "verify"],
  "critical_state": {
    "server": "dc1-priority",
    "project_dir": "~/ridehermes/src/passenger-app",
    "tunnel_url": "https://games-vertex-joy-rider.trycloudflare.com",
    "build_cmd": "flutter build apk --release --android-skip-build-dependency-validation --dart-define=API_BASE_URL=https://games-vertex-joy-rider.trycloudflare.com",
    "known_fixes_applied": ["hashValues", "namespace", "FlutterMain", "Registrar", "compileSdk36", "intl_version"]
  },
  "user_provided_info": {
    "signing_password": "ridehermes",
    "test_phone": "13800138000"
  },
  "errors_encountered": [
    {"step": "build_v9", "error": "hashValues undefined", "fix": "sed replace Object.hash"},
    {"step": "build_v10", "error": "namespace missing", "fix": "inject namespace into build.gradle"}
  ]
}
```

## When to Write Checkpoints

| Trigger | Action |
|---------|--------|
| Task starts | Create checkpoint with plan |
| Each major step completes | Update completed_steps |
| User provides info | Save to user_provided_info |
| Error encountered | Log to errors_encountered |
| Before long operation (build/deploy) | Update current_step |
| Context getting large (>40 tool calls) | Urgent checkpoint flush |

## Implementation Pattern

```python
import json
import os
from datetime import datetime

CHECKPOINT_DIR = "D:/hermes-data/checkpoints"

def save_checkpoint(task_id, state):
    """Save task state to checkpoint file."""
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    state["updated_at"] = datetime.utcnow().isoformat() + "Z"
    path = os.path.join(CHECKPOINT_DIR, f"{task_id}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_checkpoint(task_id):
    """Load task state from checkpoint file."""
    path = os.path.join(CHECKPOINT_DIR, f"{task_id}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def cleanup_checkpoint(task_id):
    """Remove checkpoint after task completes."""
    path = os.path.join(CHECKPOINT_DIR, f"{task_id}.json")
    if os.path.exists(path):
        os.remove(path)
```

## What to Persist (Priority Order)

1. **User-provided info** — passwords, phone numbers, preferences (NEVER re-ask)
2. **Current phase/step** — so we don't repeat completed work
3. **Applied fixes** — so we don't re-diagnose known issues
4. **Server URLs/ports** — so we don't re-discover infrastructure
5. **Error history** — so we don't repeat failed approaches
6. **Remaining plan** — so we know what's left

## What NOT to Persist

- Raw tool output (too large, use session_search instead)
- Intermediate computation results (can be re-derived)
- Verbose logs (save to file, reference path in checkpoint)

## Integration with pm-idea-to-mvp Pipeline

For pipeline tasks, checkpoint at each stage transition:
```
brief → [checkpoint] → align → [checkpoint] → research → ...
```

Checkpoint should include:
- Current stage
- Goal YAML path
- Decisions made in previous stages
- Artifacts produced

## Pitfalls
- **Don't save secrets in plaintext** — use env var references, not values
- **Clean up after completion** — stale checkpoints waste disk and confuse resume
- **Don't checkpoint every tool call** — only at meaningful state transitions
- **Checkpoint BEFORE long operations** — if a build takes 10 min, checkpoint right before it
