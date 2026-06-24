#!/bin/sh
set -eu

export STRONKPI_NO_NETWORK="${STRONKPI_NO_NETWORK:-1}"
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

python3 -m py_compile scripts/bump-version.py scripts/import-plugin-release.py
python3 tests/make_fixtures.py
sh tests/run_offline.sh
HOME="$tmp_dir/home" XDG_CONFIG_HOME="$tmp_dir/config" \
  bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
git diff --check
