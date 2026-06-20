#!/bin/sh
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd -P)
cd "$repo_root"

export STRONKPI_NO_NETWORK="${STRONKPI_NO_NETWORK:-1}"
python3 tests/make_fixtures.py

command -v python3 >/dev/null

sh -n install.sh
python3 -m py_compile bin/stronkpi-setup
test ! -e bin/stronkpi
test ! -e bin/stronk-pi-setup
find tests -maxdepth 1 -name "*.sh" -exec sh -n {} \;

python3 -m py_compile \
  lib/stronk-pi-guard.py \
  tests/make_fixtures.py \
  tests/test_manifest_verifier.py \
  tests/test_guard_matrix.py \
  tests/test_mcp_doctor.py \
  tests/test_public_surface.py
python3 -m json.tool config/pi/agent/models.json >/dev/null
python3 -m json.tool config/pi/agent/settings.base.json >/dev/null
python3 -m json.tool config/pi/web-search.json >/dev/null
python3 -m json.tool manifests/current.json >/dev/null

python3 -m unittest \
  tests/test_manifest_verifier.py \
  tests/test_guard_matrix.py \
  tests/test_mcp_doctor.py \
  tests/test_public_surface.py
sh tests/test_install_dry_run.sh

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home"
export STRONKPI_STATE_ROOT="$tmp/state"
export XDG_CONFIG_HOME="$tmp/xdg-config"
export XDG_CACHE_HOME="$tmp/xdg-cache"
mkdir -p "$HOME" "$STRONKPI_STATE_ROOT" "$XDG_CONFIG_HOME/mcp" "$XDG_CACHE_HOME"
cat > "$XDG_CONFIG_HOME/mcp/registry.toml" <<'EOF'
version = 1

[servers.example]
command = "python3"
args = ["-c", "print('ok')"]
EOF

bin/stronkpi-setup validate
bin/stronkpi-setup doctor --json --mcp-registry "$XDG_CONFIG_HOME/mcp/registry.toml" >/dev/null
bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
bin/stronkpi-setup run --dry-run
