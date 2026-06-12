#!/usr/bin/env bash
# Install ttmens-skills — default: --core --all (40 skills)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: ./install.sh [OPTIONS]

Options:
  --core            Install 17 native + 23 borrowed (default)
  --cursor --hermes --opencode --all
  --native-only     Skip borrowed skills
  --borrowed-only   Skip native skills
  --profile NAME    obsidian | deep-research | hermes (repeatable)
  --project PATH    Project .cursor/skills or .opencode/skills
  --dry-run
  -h, --help
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -eq 0 ]]; then
  set -- --core --all
fi

exec python3 "$ROOT/scripts/install_skills.py" "$@"
