#!/bin/sh
set -eu

script_path=$0
case "$script_path" in
  */*) ;;
  *) script_path=$(command -v "$script_path") ;;
esac
repo_root=$(CDPATH= cd "$(dirname "$script_path")" && pwd -P)

usage() {
  cat <<'EOF'
usage: ./install.sh [--dry-run] [--prefix PATH]

Installs stronkpi-setup for setup/validation and stronkpi for the guarded
portable harness. Short compatibility aliases are not created.
EOF
}

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "install.sh: python3 is required but was not found on PATH" >&2
  exit 1
fi

for arg do
  case "$arg" in
    -h|--help)
      usage
      exit 0
      ;;
  esac
done

exec "$repo_root/bin/stronkpi-setup" install "$@"
