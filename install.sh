#!/usr/bin/env bash
# Install ttmens-skills to Cursor and/or Hermes skill directories.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="both"
PROJECT=""

usage() {
  cat <<'EOF'
Usage: ./install.sh [OPTIONS]

Options:
  --cursor          Install to ~/.cursor/skills/
  --hermes          Install to ~/.hermes/skills/
  --both            Install to both (default)
  --project PATH    Also symlink into PATH/.cursor/skills/
  -h, --help        Show help

Skills installed:
  workflow/*, design/*, skills/*
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cursor) TARGET="cursor" ;;
    --hermes) TARGET="hermes" ;;
    --both) TARGET="both" ;;
    --project) PROJECT="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
  shift
done

link_tree() {
  local dest_root="$1"
  local rel="$2"
  local src="$ROOT/$rel"
  local dest="$dest_root/$(basename "$rel")"
  if [[ ! -d "$src" ]]; then
    return 0
  fi
  mkdir -p "$(dirname "$dest")"
  ln -sfn "$src" "$dest"
  echo "  linked $rel -> $dest"
}

install_to() {
  local base="$1"
  mkdir -p "$base"
  echo "Installing to $base"
  for dir in workflow/product-orchestrator workflow/idea-to-product workflow/writing-plans \
             workflow/subagent-driven-development workflow/docs-hygiene \
             design/design-system-md design/ui-acceptance-review design/frontend-polish \
             skills/productivity/obsidian-todo-manager skills/research/obsidian-deepen-review \
             skills/research/obsidian-note-summarizer skills/product/prd-template \
             skills/product/competitor-tracker; do
    link_tree "$base" "$dir"
  done
}

case "$TARGET" in
  cursor) install_to "$HOME/.cursor/skills" ;;
  hermes) install_to "$HOME/.hermes/skills" ;;
  both)
    install_to "$HOME/.cursor/skills"
    install_to "$HOME/.hermes/skills"
    ;;
esac

if [[ -n "$PROJECT" ]]; then
  proj_skills="$PROJECT/.cursor/skills"
  mkdir -p "$proj_skills"
  echo "Project skills at $proj_skills"
  for skill in product-orchestrator idea-to-product docs-hygiene design-system-md ui-acceptance-review; do
    for base in workflow design; do
      src="$ROOT/$base/$skill"
      if [[ -d "$src" ]]; then
        ln -sfn "$src" "$proj_skills/$skill"
        echo "  project linked $skill"
      fi
    done
  done
fi

echo "Done."
