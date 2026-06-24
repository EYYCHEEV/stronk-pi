#!/bin/sh
set -eu

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
repo_root=$(CDPATH= cd "$script_dir/.." && pwd -P)
cd "$repo_root"

export STRONKPI_NO_NETWORK="${STRONKPI_NO_NETWORK:-1}"
python3 tests/make_fixtures.py

command -v python3 >/dev/null

sh -n install.sh
python3 -m py_compile bin/stronkpi-setup bin/stronkpi
test ! -e bin/stronk-pi-setup
find tests -maxdepth 1 -name "*.sh" -exec sh -n {} \;

python3 -m py_compile \
  lib/stronk-pi-guard.py \
  scripts/bump-version.py \
  scripts/import-plugin-release.py \
  tests/make_fixtures.py \
  tests/test_manifest_verifier.py \
  tests/test_release_scripts.py \
  tests/test_guard_matrix.py \
  tests/test_mcp_doctor.py \
  tests/test_public_surface.py
python3 -m json.tool config/pi/agent/models.json >/dev/null
python3 -m json.tool config/pi/agent/settings.base.json >/dev/null
python3 -m json.tool config/pi/web-search.json >/dev/null
python3 -m json.tool manifests/current.json >/dev/null

python3 -m unittest \
  tests/test_manifest_verifier.py \
  tests/test_release_scripts.py \
  tests/test_guard_matrix.py \
  tests/test_mcp_doctor.py \
  tests/test_public_surface.py
sh tests/test_install_dry_run.sh

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
export HOME="$tmp/home"
export XDG_CONFIG_HOME="$tmp/xdg-config"
export XDG_CACHE_HOME="$tmp/xdg-cache"
mkdir -p "$HOME" "$XDG_CONFIG_HOME/mcp" "$XDG_CACHE_HOME"
cat > "$XDG_CONFIG_HOME/mcp/registry.toml" <<'EOF'
version = 1

[servers.example]
command = "python3"
args = ["-c", "print('ok')"]
EOF
touch "$XDG_CONFIG_HOME/mcp/tools.empty"

bin/stronkpi-setup validate
bin/stronkpi-setup doctor --json --mcp-registry "$XDG_CONFIG_HOME/mcp/registry.toml" --mcp-tools "$XDG_CONFIG_HOME/mcp/tools.empty" >/dev/null
bin/stronkpi-setup refresh-config --dry-run --json >/dev/null
bin/stronkpi-setup refresh-config --json >/dev/null
mkdir -p "$tmp/codex-roles"
cat > "$tmp/codex-roles/import-smoke.toml" <<'EOF'
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
developer_instructions = """
Role: import smoke role.

Verify that Codex role TOML can be imported into Stronk Pi runtime templates.
"""
EOF
bin/stronkpi-setup import-codex-roles --source "$tmp/codex-roles" --dry-run --json >/dev/null
bin/stronkpi-setup import-codex-roles --source "$tmp/codex-roles" --json >/dev/null
test -f "$HOME/.stronk-pi/config/role-templates/import-smoke.toml"
test -f "$HOME/.stronk-pi/agent/agents/import-smoke.md"
bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
bin/stronkpi-setup update --manifest tests/fixtures/manifests/good-local.json
bin/stronkpi-setup run --dry-run
bin/stronkpi --validate-only >/dev/null
bin/stronkpi --diagnose --json >/dev/null

prefix="$tmp/prefix"
bin/stronkpi-setup install --prefix "$prefix"
"$prefix/bin/stronkpi-setup" validate
"$prefix/bin/stronkpi" --validate-only >/dev/null
