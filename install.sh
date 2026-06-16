#!/usr/bin/env zsh
set -euo pipefail

self_path="${0:A}"
repo_root="${self_path:h}"

usage() {
  cat <<'EOF'
usage: ./install.sh [--dry-run] [--prefix PATH]

Installs the canonical stronkpi command. The installer never creates short
aliases and never starts provider sessions.
EOF
}

args=()
while (( $# > 0 )); do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

exec "$repo_root/bin/stronkpi" install "${args[@]}"

