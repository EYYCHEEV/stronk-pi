#!/bin/sh
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd -P)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home"
export STRONKPI_STATE_ROOT="$tmp/state"
export XDG_CONFIG_HOME="$tmp/xdg-config"
export XDG_CACHE_HOME="$tmp/xdg-cache"
export STRONKPI_NO_NETWORK=1
mkdir -p "$HOME" "$STRONKPI_STATE_ROOT" "$XDG_CONFIG_HOME/mcp" "$XDG_CACHE_HOME"

"$repo_root/install.sh" --dry-run --prefix "$HOME/.local"
"$repo_root/install.sh" --prefix "$HOME/.local"

test -x "$HOME/.local/bin/stronkpi-setup"
test ! -e "$HOME/.local/bin/stronkpi"
test ! -e "$HOME/.local/bin/stronk-pi-setup"
test ! -e "$HOME/.local/bin/sp"
test ! -e "$HOME/.local/bin/pi"

cat > "$XDG_CONFIG_HOME/mcp/registry.toml" <<'EOF'
version = 1

[servers.example]
command = "python3"
args = ["-c", "print('ok')"]
EOF

"$HOME/.local/bin/stronkpi-setup" validate
"$HOME/.local/bin/stronkpi-setup" doctor --json --mcp-registry "$XDG_CONFIG_HOME/mcp/registry.toml" >/dev/null

if [ -e "$tmp/home/.pi" ]; then
  printf '%s\n' "unexpected .pi directory created" >&2
  exit 1
fi
