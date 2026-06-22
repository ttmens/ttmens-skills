#!/usr/bin/env python3
"""Purge all Hermes Kanban tasks and related data.

Usage:
    python kanban-purge.py              # Dry run (show counts only)
    python kanban-purge.py --confirm    # Actually delete everything
"""
import sqlite3
import sys
import os

DB_PATH = os.path.expandvars("D:/hermes-data/kanban.db")
WORKSPACE_DIR = os.path.expandvars("D:/hermes-data/kanban/workspaces")

TABLES_ORDER = [
    'task_events', 'task_runs', 'task_comments', 'task_links',
    'task_attachments', 'kanban_notify_subs', 'tasks'
]

def main():
    confirm = '--confirm' in sys.argv

    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
        sys.exit(1)

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()

    # Show current state
    print("=== Current state ===")
    for table in TABLES_ORDER + ['sqlite_sequence']:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {cursor.fetchone()[0]} rows")
        except Exception as e:
            print(f"  {table}: ERROR ({e})")

    cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
    rows = cursor.fetchall()
    if rows:
        print("\n=== Status distribution ===")
        for status, count in rows:
            print(f"  {status}: {count}")

    if not confirm:
        print("\n[DRY RUN] Add --confirm to delete everything.")
        db.close()
        return

    # Delete in order
    print("\n=== Deleting ===")
    for table in TABLES_ORDER:
        cursor.execute(f"DELETE FROM {table}")
        print(f"  {table}: {cursor.rowcount} rows deleted")
    cursor.execute("DELETE FROM sqlite_sequence")
    print(f"  sqlite_sequence: reset")

    db.commit()
    db.close()

    # Clean workspaces
    if os.path.exists(WORKSPACE_DIR):
        import shutil
        count = 0
        for entry in os.listdir(WORKSPACE_DIR):
            path = os.path.join(WORKSPACE_DIR, entry)
            if entry.startswith("t_") and os.path.isdir(path):
                shutil.rmtree(path)
                count += 1
        print(f"\n  Workspaces: {count} directories removed")

    print("\n✅ Kanban purged successfully.")

if __name__ == '__main__':
    main()
