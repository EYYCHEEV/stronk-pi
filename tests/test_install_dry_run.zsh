#!/usr/bin/env zsh
set -euo pipefail

repo_root="${0:A:h:h}"
tmp="$(mktemp -d)"
export HOME="$tmp/home"
export STRONKPI_STATE_ROOT="$tmp/state"
export XDG_CONFIG_HOME="$tmp/xdg-config"
export XDG_CACHE_HOME="$tmp/xdg-cache"
export STRONKPI_NO_NETWORK=1
mkdir -p "$HOME" "$STRONKPI_STATE_ROOT" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"

"$repo_root/install.sh" --dry-run --prefix "$HOME/.local"
"$repo_root/install.sh" --prefix "$HOME/.local"

[[ -x "$HOME/.local/bin/stronkpi" ]]
[[ ! -e "$HOME/.local/bin/sp" ]]
[[ ! -e "$HOME/.local/bin/pi" ]]

"$HOME/.local/bin/stronkpi" validate

if [[ -e "$tmp/home/.pi" ]]; then
  print -r -- "unexpected .pi directory created" >&2
  exit 1
fi

