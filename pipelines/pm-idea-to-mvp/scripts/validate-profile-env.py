#!/usr/bin/env python3
"""Validate PM profile .env files are valid UTF-8 (prevents kanban-worker skill crash)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from pipeline_paths import resolve_hermes_home  # noqa: E402

DEFAULT_PROFILES_ROOT = resolve_hermes_home() / "profiles"
PM_PROFILES = [
    "pm-aligner",
    "pm-researcher",
    "pm-analyst",
    "pm-planner",
    "pm-builder",
    "pm-orchestrator",
]


def check_env(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return errors
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path}: invalid UTF-8 at byte {exc.start}: {exc}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profiles-root",
        default=os.environ.get("HERMES_PROFILES_ROOT", str(DEFAULT_PROFILES_ROOT)),
    )
    parser.add_argument("--profile", action="append", help="Single profile name (repeatable)")
    parser.add_argument("--fix", action="store_true", help="Replace broken em-dash bytes with --")
    args = parser.parse_args()

    root = Path(args.profiles_root)
    names = args.profile or PM_PROFILES
    all_errors: list[str] = []

    for name in names:
        env_path = root / name / ".env"
        errs = check_env(env_path)
        if errs and args.fix:
            data = env_path.read_bytes()
            fixed = data.replace(b"\xe2\x80?", b"--").replace(b"\xe2\x86?", b"->")
            try:
                fixed.decode("utf-8")
                env_path.write_bytes(fixed)
                print(f"fixed: {env_path}")
                errs = check_env(env_path)
            except UnicodeDecodeError:
                pass
        all_errors.extend(errs)

    if all_errors:
        for e in all_errors:
            print(e, file=sys.stderr)
        raise SystemExit(1)

    print(json_dumps_ok(names))


def json_dumps_ok(names: list[str]) -> str:
    import json

    return json.dumps({"profiles_checked": names, "ok": True}, ensure_ascii=False)


if __name__ == "__main__":
    main()
