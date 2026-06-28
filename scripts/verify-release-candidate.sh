#!/bin/sh
set -eu

# Scrub inherited Stronk Pi control-plane env (STRONK_*/STRONKPI_*/PI_*) so this release
# check runs from a clean temp home and temp state root, never the operator's live
# ~/.stronk-pi. State-root/dev-override vars are removed so they cannot disagree with the
# temp roots set below or redirect stronkpi-setup writes. `eval unset` runs in this shell
# so the unsets persist; var names come from env and match the strict [A-Za-z0-9_] charset
# (grep enforces ^PREFIX[name]=). Portable across sh, bash, and zsh.
_stronk_env_scrub=$(env | grep -E '^(STRONK_|STRONKPI_|PI_)[A-Za-z0-9_]+=' | cut -d= -f1 | tr '\n' ' ')
if [ -n "$_stronk_env_scrub" ]; then
  eval "unset $_stronk_env_scrub"
fi
unset STRONKPI_STATE_ROOT STRONK_PI_STATE_ROOT STRONKPI_DEV_OVERRIDES STRONK_PI_DEV_OVERRIDES STRONKPI_SETUP_ROOT
export STRONKPI_NO_NETWORK=1

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

python3 -m py_compile scripts/bump-version.py scripts/import-plugin-release.py
python3 tests/make_fixtures.py
sh tests/run_offline.sh
HOME="$tmp_dir/home" XDG_CONFIG_HOME="$tmp_dir/config" \
  bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
git diff --check
