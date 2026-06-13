#!/usr/bin/env python3
"""Push current branch using GITHUB_TOKEN from HERMES_HOME/.env."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from github_helpers import GITHUB_OWNER, load_token  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Git add, commit, and push project changes")
    parser.add_argument("--dir", default=".", help="Repo directory")
    parser.add_argument("--slug", required=True, help="Without pm- prefix")
    parser.add_argument("--branch", default="main")
    args = parser.parse_args()

    repo_dir = Path(args.dir).resolve()
    token = load_token()
    repo_name = f"pm-{args.slug}"
    remote = f"https://{token}@github.com/{GITHUB_OWNER}/{repo_name}.git"
    subprocess.run(["git", "push", remote, f"HEAD:{args.branch}"], cwd=repo_dir, check=True, timeout=60)
    print(f"Pushed to https://github.com/{GITHUB_OWNER}/{repo_name}")


if __name__ == "__main__":
    main()
