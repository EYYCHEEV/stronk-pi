# Stronk Pi Release SOP

This repo is the public distribution and setup contract.
It consumes immutable `stronk-pi-plugin` releases after the plugin repo publishes them.
It also pins the Stronk-owned `stronk-pi-subagents` fork artifact that the guarded subagent runtime uses.

## Bump Setup Version

Use this when the setup/distribution package version changes:

```zsh
python3 scripts/bump-version.py 0.2.0
STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh
```

This updates setup version surfaces only.
It does not change the expected plugin artifact version.

## Import Plugin Release

First publish the matching plugin artifact from `stronk-pi-plugin`.
Then download that release's `BUILD-MANIFEST.json` and import it:

```zsh
python3 scripts/import-plugin-release.py /tmp/stronk-pi-plugin-v0.2.0/BUILD-MANIFEST.json
STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh
```

The import command updates:

- `manifests/current.json`
- `lib/stronk-pi-guard.py` plugin artifact default
- `roles/stronk/roles.toml` extension path
- deterministic manifest fixtures

Do not import a plugin version before its release artifact and attestation exist.

## Import Subagents Fork Release

The `stronk-pi-subagents` fork is maintained in `EYYCHEEV/stronk-pi-subagents` on branch `stronk-pi-subagents`.
The first artifact is `stronk-pi-subagents@0.22.0-stronk.3`, based on `nicobailon/pi-subagents@0.22.0` commit `1fd371d2a068458741a15507edc6cd49a9807486`.

The setup manifest entry must include:

- `name`: `stronk-pi-subagents`
- `version`: `0.22.0-stronk.3`
- `sourceRepo`: `EYYCHEEV/stronk-pi-subagents`
- `sourceCommit`: `afe08d9a0c84a5c1de4a8de1dda82868c96a6ce0`
- `immutableTag`: `stronk-pi-subagents-v0.22.0-stronk.3`
- `artifactUrl`: `https://github.com/EYYCHEEV/stronk-pi-subagents/releases/download/stronk-pi-subagents-v0.22.0-stronk.3/stronk-pi-subagents-0.22.0-stronk.3.tgz`
- `sha256`: `23aa7beac6ecca0f8d20824cb33f93cfac7fbe00488cb5fea85878a7876f18e4`
- `workflowRunId`: `28301945900`
- `upstreamRepo`: `nicobailon/pi-subagents`
- `upstreamVersion`: `0.22.0`
- `upstreamCommit`: `1fd371d2a068458741a15507edc6cd49a9807486`

The guard requires the tarball to contain the expected package source, bundled agents, and `skills/pi-subagents/SKILL.md`.
A `package.json`-only tarball or runtime package root must fail validation.

After updating the fork entry, regenerate deterministic fixtures and run:

```zsh
python3 tests/make_fixtures.py
STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh
```

## Online Gate

After importing a plugin or subagents fork release, verify the public artifact URL:

```zsh
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
```

Run this without `STRONKPI_NO_NETWORK=1`.

## Live Update

After the distribution PR is merged:

```zsh
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
bin/stronkpi-setup update --manifest manifests/current.json
bin/stronkpi --validate-only
bin/stronkpi --diagnose --json
```

Back up live `~/.stronk-pi` managed files before the non-dry-run update when
operator state may matter.

## Runtime State Validation

Before manual testing from a new shell, refresh active installed artifacts and
managed runtime config:

```zsh
STRONKPI_NO_NETWORK=1 ./install.sh --prefix "$HOME/.local"
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup refresh-config --json
```

Then verify the installed wrapper and state-root split:

```zsh
command -v stronkpi
STRONKPI_NO_NETWORK=1 stronkpi --validate-only
STRONKPI_NO_NETWORK=1 stronkpi --diagnose --json >/tmp/stronkpi-diagnose.json
STRONKPI_NO_NETWORK=1 stronkpi-setup cleanup-private-home --dry-run --json >/tmp/stronkpi-cleanup.json
python3 -m unittest tests/test_public_surface.py tests/test_plugin_state_root.py
```

The diagnose output should show the operator's real `effectiveHome` and
Stronk-owned paths under `~/.stronk-pi`.
When `.mcp-tools` selects servers, launch should refresh project `.mcp.json`
and pass that file through `--mcp-config`.
Do not run cleanup with `--apply` unless the dry-run has been reviewed.

## Rollback

Before plugin import, close or revert the setup version PR.
After plugin import but before live update, revert the distribution PR.
After subagents fork import but before live update, revert the manifest package pin and remove the `stronk-pi-subagents` artifact entry in a new PR.
After live update, restore the previous manifest, package pins, and plugin default version in a new PR, merge it, and rerun `bin/stronkpi-setup update --manifest manifests/current.json`.
Remove or ignore `~/.stronk-pi/artifacts/stronk-pi-subagents-0.22.0-stronk.3/package` after rollback if the fork artifact is no longer selected.
