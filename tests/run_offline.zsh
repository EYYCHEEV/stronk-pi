#!/usr/bin/env zsh
set -euo pipefail

repo_root="${0:A:h:h}"
cd "$repo_root"

export STRONKPI_NO_NETWORK="${STRONKPI_NO_NETWORK:-1}"
python3 tests/make_fixtures.py

command -v zsh >/dev/null
command -v python3 >/dev/null

zsh -n install.sh
zsh -n bin/stronkpi
for script in tests/*.zsh(N); do
  zsh -n "$script"
done

python3 -m py_compile lib/stronk-pi-guard.py tests/make_fixtures.py tests/test_manifest_verifier.py tests/test_guard_matrix.py tests/test_public_surface.py
python3 -m json.tool config/pi/agent/models.json >/dev/null
python3 -m json.tool config/pi/agent/settings.base.json >/dev/null
python3 -m json.tool config/pi/web-search.json >/dev/null
python3 -m json.tool manifests/current.json >/dev/null

python3 -m unittest tests/test_manifest_verifier.py tests/test_guard_matrix.py tests/test_public_surface.py
zsh tests/test_install_dry_run.zsh

tmp="$(mktemp -d)"
export HOME="$tmp/home"
export STRONKPI_STATE_ROOT="$tmp/state"
export XDG_CONFIG_HOME="$tmp/xdg-config"
export XDG_CACHE_HOME="$tmp/xdg-cache"
mkdir -p "$HOME" "$STRONKPI_STATE_ROOT" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"

bin/stronkpi validate
bin/stronkpi doctor --json >/dev/null
bin/stronkpi update --dry-run --manifest tests/fixtures/manifests/good-local.json
bin/stronkpi run --dry-run

