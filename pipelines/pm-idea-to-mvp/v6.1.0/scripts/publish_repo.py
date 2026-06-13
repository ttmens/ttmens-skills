#!/usr/bin/env python3
"""Init git repo, create GitHub remote, push, enable Pages."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from github_helpers import create_repo, enable_pages, load_token, pages_url, repo_url  # noqa: E402


def run(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    import os

    merged = os.environ.copy()
    if env:
        merged.update(env)
    subprocess.run(cmd, cwd=cwd, check=True, env=merged)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--slug", required=True, help="Without pm- prefix")
    parser.add_argument("--description", default="PM pipeline idea-to-MVP artifacts")
    args = parser.parse_args()

    repo_dir = Path(args.dir).resolve()
    repo_name = f"pm-{args.slug}"
    token = load_token()
    remote = f"https://{token}@github.com/ttmens/{repo_name}.git"

    create_repo(repo_name, description=args.description, private=False)

    if not (repo_dir / ".git").exists():
        run(["git", "init", "-b", "main"], repo_dir)
        run(["git", "config", "user.email", "pm-pipeline@hermes.local"], repo_dir)
        run(["git", "config", "user.name", "Hermes PM Pipeline"], repo_dir)

    if _has_remote(repo_dir):
        run(["git", "remote", "remove", "origin"], repo_dir)
    run(["git", "remote", "add", "origin", remote], repo_dir)
    run(["git", "add", "-A"], repo_dir)
    try:
        run(["git", "commit", "-m", "initial: PM pipeline artifacts"], repo_dir)
    except subprocess.CalledProcessError:
        run(["git", "commit", "--allow-empty", "-m", "initial: PM pipeline artifacts"], repo_dir)
    run(["git", "push", "-u", "origin", "main"], repo_dir)
    # Drop token from stored remote URL
    run(["git", "remote", "set-url", "origin", f"https://github.com/ttmens/{repo_name}.git"], repo_dir)

    try:
        enable_pages(repo_name)
    except Exception as exc:
        print(f"Pages enable warning: {exc}")

    print(f"Repo: {repo_url(repo_name)}")
    print(f"Pages: {pages_url(repo_name)}")


def _has_remote(repo_dir: Path) -> bool:
    try:
        subprocess.run(["git", "remote", "get-url", "origin"], cwd=repo_dir, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


if __name__ == "__main__":
    main()
