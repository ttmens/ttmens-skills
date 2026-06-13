#!/usr/bin/env bash
# Install ttmens-skills — default: --core --all (37 skills)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: ./install.sh [OPTIONS]

Options:
  --core            Install 17 native + 20 borrowed (default)
  --lite --stage S  Install only skills for pipeline stage S
  --cursor --hermes --opencode --all
  --platform NAME   cursor | hermes | opencode (templates + profiles)
  --profile NAME    obsidian | deep-research | hermes | hermes-kanban | debate
  --scenario NAME   greenfield | brownfield | refine | optimize
  --project PATH    Project .cursor/skills or .opencode/skills
  --dry-run
  -h, --help

Agent install guide: docs/AGENT_ONBOARDING.md
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
