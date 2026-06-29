# Stronk Pi Release SOP

This repo is the public distribution and setup contract.
It consumes immutable `stronk-pi-plugin` releases after the plugin repo publishes them.
It also pins the Stronk-owned `stronk-pi-subagents` fork artifact that the guarded subagent runtime uses.

## Bump Setup Version

Use this when the setup/distribution package version changes:

```zsh
python3 scripts/bump-version.py 0.2.1
STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh
```

This updates setup version surfaces only.
It does not change the expected plugin artifact version.

## Import Plugin Release

First publish the matching plugin artifact from `stronk-pi-plugin`.
Then download that release's `BUILD-MANIFEST.json` and import it:

```zsh
python3 scripts/import-artifact-release.py /tmp/stronk-pi-plugin-v0.2.1/BUILD-MANIFEST.json
STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh
```

The import command updates:

- `manifests/current.json`
- `lib/stronk-pi-guard.py` plugin artifact default
- `roles/stronk/roles.toml` extension path
- deterministic manifest fixtures

Do not import a plugin version before its release artifact and attestation exist.

`scripts/import-plugin-release.py` remains as a compatibility wrapper for plugin-only imports.

## Import Subagents Fork Release

The `stronk-pi-subagents` fork is maintained in `EYYCHEEV/stronk-pi-subagents` on branch `stronk-pi-subagents`.
The current artifact is `stronk-pi-subagents@0.22.0-stronk.4`, based on `nicobailon/pi-subagents@0.22.0` commit `1fd371d2a068458741a15507edc6cd49a9807486`.

The setup manifest entry must include:

- `name`: `stronk-pi-subagents`
- `version`: `0.22.0-stronk.4`
- `sourceRepo`: `EYYCHEEV/stronk-pi-subagents`
- `sourceCommit`: `b8e66493987fb3390946049f2c7989428b0f570e`
- `immutableTag`: `stronk-pi-subagents-v0.22.0-stronk.4`
- `artifactUrl`: `https://github.com/EYYCHEEV/stronk-pi-subagents/releases/download/stronk-pi-subagents-v0.22.0-stronk.4/stronk-pi-subagents-0.22.0-stronk.4.tgz`
- `sha256`: `93bc322766b8ffcf811b1fdb3e0ea62538f02dab319d696d0d77689c3d0fbc12`
- `workflowRunId`: `28315836713`
- `upstreamRepo`: `nicobailon/pi-subagents`
- `upstreamVersion`: `0.22.0`
- `upstreamCommit`: `1fd371d2a068458741a15507edc6cd49a9807486`

The guard requires the tarball to contain the expected package source, bundled agents, and the parent orchestration skill.
Release `0.22.0-stronk.4` uses `skills/stronkpi-agents/SKILL.md`; legacy release `0.22.0-stronk.3` used `skills/pi-subagents/SKILL.md`.
A `package.json`-only tarball or runtime package root must fail validation.

After publishing the fork release, download its `BUILD-MANIFEST.json` and import it:

```zsh
python3 scripts/import-artifact-release.py /tmp/stronk-pi-subagents-v0.22.0-stronk.5/BUILD-MANIFEST.json
STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh
```

The importer updates `manifests/current.json`, `config/defaults.toml`, `lib/stronk-pi-guard.py`, and deterministic fixture constants.

## Import Intercom Fork Release

The `stronk-pi-intercom` fork is maintained in `EYYCHEEV/stronk-pi-intercom`.
The first fork artifact is based on `nicobailon/pi-intercom@0.6.0` commit `5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457`.

After publishing the fork release, download its `BUILD-MANIFEST.json` and import it:

```zsh
python3 scripts/import-artifact-release.py /tmp/stronk-pi-intercom-v0.6.0-stronk.1/BUILD-MANIFEST.json
STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh
```

The setup manifest entry must include:

- `name`: `stronk-pi-intercom`
- `sourceRepo`: `EYYCHEEV/stronk-pi-intercom`
- `upstreamRepo`: `nicobailon/pi-intercom`
- `upstreamVersion`: `0.6.0`
- `upstreamCommit`: `5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457`
- `seedType`: `npm-tarball`
- `seedPackage`: `pi-intercom`
- `seedVersion`: `0.6.0`
- `seedTarballSha256`: `76c0d5284661aac437248bb6c7a32879fe863296bd15cb533751b27cafc44818`
- `sourceArchiveSha256`: `3ce238f4a75ce9c66ad76766ee878ef19dd83eef620739b73fe08e35c84311c6`

The guard requires the tarball and installed runtime package to contain the state-root aware intercom bridge, broker, UI helpers, and `skills/stronk-pi-intercom/SKILL.md`.
Legacy `pi-intercom`-only manifests must fail validation.

## Online Gate

After importing a plugin, subagents, or intercom fork release, verify the public artifact URL:

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
After intercom fork import but before live update, revert the manifest package pin and remove the `stronk-pi-intercom` artifact entry in a new PR.
After live update, restore the previous manifest, package pins, and plugin default version in a new PR, merge it, and rerun `bin/stronkpi-setup update --manifest manifests/current.json`.
Remove or ignore `~/.stronk-pi/artifacts/stronk-pi-subagents-0.22.0-stronk.4/package` after rollback if the fork artifact is no longer selected.
Remove or ignore `~/.stronk-pi/artifacts/stronk-pi-intercom-0.6.0-stronk.1/package` after rollback if the fork artifact is no longer selected.
