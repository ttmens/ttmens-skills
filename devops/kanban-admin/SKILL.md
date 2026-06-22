---
name: kanban-admin
version: 1.0.0
description: Manage, troubleshoot, and bulk-operate the Hermes Kanban system — stop stuck tasks, purge history, recover from corruption, inspect DB state.
tags: [kanban, hermes, admin, database, troubleshooting]
trigger_conditions:
  - "kanban stuck/hung/frozen"
  - "delete all kanban tasks"
  - "clear kanban"
  - "reset kanban"
  - "kanban won't stop"
  - "kill kanban task"
  - "kanban database"
  - "purge kanban history"
---

# Kanban Admin

Direct administration of the Hermes Kanban system when CLI commands are insufficient.

## When to Use

- Tasks stuck in `running` state with no active worker
- Need to bulk-delete/archive all tasks (no CLI command for this)
- Kanban DB corruption or inconsistency
- Need to inspect task relationships, events, or run history
- `hermes kanban archive` refuses to work (e.g., already-archived tasks)

## Kanban Database Structure

**Location**: `D:/hermes-data/kanban.db` (SQLite)

### Tables (in dependency order for deletion)

| Table | Purpose |
|-------|---------|
| `task_events` | Event log (created, claimed, heartbeat, etc.) |
| `task_runs` | Worker run records |
| `task_comments` | Task comments |
| `task_links` | Parent-child relationships |
| `task_attachments` | File attachments |
| `kanban_notify_subs` | Notification subscriptions |
| `tasks` | Main task table (FK target) |
| `sqlite_sequence` | Auto-increment counters |

**Important**: Delete from child tables BEFORE `tasks` (foreign key dependencies).

## Procedures

### Stop All Running Tasks + Purge Everything

**Quick way** (preferred):
```bash
python D:/hermes-data/skills/devops/kanban-admin/scripts/kanban-purge.py --confirm
```

**Manual way** (if script unavailable):
```python
import sqlite3

db = sqlite3.connect("D:/hermes-data/kanban.db")
cursor = db.cursor()

# Clear in dependency order
tables = ['task_events', 'task_runs', 'task_comments', 'task_links',
          'task_attachments', 'kanban_notify_subs', 'tasks']
for table in tables:
    cursor.execute(f"DELETE FROM {table}")
    print(f"Cleared {table}: {cursor.rowcount} rows")

cursor.execute("DELETE FROM sqlite_sequence")
db.commit()
db.close()
```

Then clean workspace temp files:
```bash
rm -rf D:/hermes-data/kanban/workspaces/t_*
```

### Inspect Task State (when CLI is insufficient)

```python
import sqlite3

db = sqlite3.connect("D:/hermes-data/kanban.db")
cursor = db.cursor()

# Status distribution
cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Find stuck running tasks
cursor.execute("SELECT id, title, assignee, last_heartbeat_at FROM tasks WHERE status='running'")
for row in cursor.fetchall():
    print(f"  STUCK: {row[0]} — {row[1]} (heartbeat: {row[3]})")

db.close()
```

### Force-Stop a Single Stuck Task

```python
import sqlite3

db = sqlite3.connect("D:/hermes-data/kanban.db")
cursor = db.cursor()
cursor.execute("UPDATE tasks SET status='todo', claim_lock=NULL, claim_expires=NULL, worker_pid=NULL WHERE id=?", (task_id,))
db.commit()
db.close()
```

## Pitfalls

| Pitfall | Explanation |
|---------|-------------|
| **`hermes kanban archive` refuses** | Only works on non-archived tasks. For already-archived tasks, use `--rm` flag or direct DB. |
| **`sqlite3` CLI not on Windows** | Use Python's `sqlite3` module via `execute_code` instead. |
| **Foreign key violations** | Must delete child tables (events, runs, comments, links) BEFORE `tasks`. |
| **Workspace files persist** | DB cleanup doesn't remove `kanban/workspaces/t_*` dirs — delete manually. |
| **Running tasks have worker processes** | DB cleanup alone doesn't kill worker PIDs. Check `process list` and kill if needed. |
| **Profile state DBs** | Each profile has `state.db` under `D:/hermes-data/profiles/<name>/` — separate from kanban.db, usually don't need touching. |

## Auto Health Check (Proactive Stuck Detection)

### Detect Stuck Tasks (run periodically or on-demand)
```python
import sqlite3
from datetime import datetime, timedelta

db = sqlite3.connect("D:/hermes-data/kanban.db")
cursor = db.cursor()

# Find tasks stuck in 'running' with no heartbeat for >10 minutes
cutoff = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
cursor.execute("""
    SELECT id, title, status, last_heartbeat_at, assignee 
    FROM tasks 
    WHERE status='running' 
    AND (last_heartbeat_at IS NULL OR last_heartbeat_at < ?)
""", (cutoff,))

stuck = cursor.fetchall()
if stuck:
    print(f"⚠️ {len(stuck)} stuck tasks detected:")
    for t in stuck:
        print(f"  - {t[0]}: {t[1]} (heartbeat: {t[3]}, assignee: {t[4]})")
else:
    print("✅ No stuck tasks")

db.close()
```

### Auto-Recovery Actions
```python
# For each stuck task:
# 1. Reset to 'todo' (allows re-claim)
cursor.execute("UPDATE tasks SET status='todo', claim_lock=NULL, claim_expires=NULL, worker_pid=NULL WHERE id=?", (task_id,))

# 2. Or: force-complete if it's a zombie
cursor.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))

# 3. Kill orphan worker processes
import subprocess
subprocess.run(["kill", "-9", str(worker_pid)])
```

### Recommended Cron (optional)
Add a periodic health check via Hermes cron:
```
Schedule: every 30m
Prompt: "Check kanban for stuck tasks. Run the stuck detection script. If stuck tasks found, reset them to todo and report."
```

### Stuck Prevention
- **Heartbeat timeout**: Tasks should heartbeat every 60s. If no heartbeat for 10min → stuck.
- **Worker PID check**: If task claims a worker PID but that PID is dead → stuck.
- **Claim expiry**: Set `claim_expires` when claiming. Expired claims auto-release.

## Verification

After any cleanup:
```bash
hermes kanban list  # Should show "(no matching tasks)"
```
