# Stronk Pi Setup

`stronkpi-setup` is the setup and validation command for Stronk Pi.
Stronk Pi is the guarded Pi Coding Agent distribution. `stronkpi` is reserved
for the guarded Stronk Pi harness.

> Status: Public preview / not fully self-contained
>
> `stronkpi-setup` currently validates manifests, artifacts, host safety, and
> MCP configuration for Stronk Pi. The complete end-user `stronkpi` launch path
> is still being separated from the private maintainer workstation
> configuration.
>
> Until that extraction is complete, this repo is useful for development,
> validation, and artifact verification, but external users should not expect a
> one-command standalone Stronk Pi install.

This repository provides a preview installer, manifest verifier, guarded
diagnostics, safe baseline configuration, and offline tests. Maintainers and
early testers can use pinned release manifests and verified artifacts while the
standalone public launch path is being extracted.

## Name Map

| Name | Meaning |
| --- | --- |
| Stronk Pi | Guarded Pi Coding Agent distribution. |
| `stronkpi` | Guarded harness command that launches Pi with Stronk Pi controls. |
| `stronkpi-setup` | Setup, validation, diagnostics, and artifact update command. |
| `stronk-pi` | Plugin source repo and package namespace. |
| `stronk-pi-plugin` | Verified plugin artifact consumed by setup manifests. |
| Stronk Pi Mono | Trusted Pi fork runtime lineage used by the guarded harness. |

Guarded means Pi is launched with fail-closed controls for tool permissions,
unsafe shell commands, secret and path handling, trusted runtime drift,
Model Context Protocol (MCP) configuration, and subagent role loading.

## Install

Preview installation without writing to your command directory:

```sh
./install.sh --dry-run
```

Install the command into `~/.local/bin`:

```sh
./install.sh
```

The installer creates `stronkpi-setup`. It does not create or wrap `stronkpi`,
and it does not create short compatibility commands.

## Validate

Run the offline setup checks:

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --json --allow-missing-mcp
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --mcp-registry ~/.config/mcp/registry.toml
```

Verify an offline fixture manifest:

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
```

`doctor` validates the setup host and MCP registry. It checks Python
availability, state-root safety, registry TOML shape, server commands,
selected `.mcp-tools` names, selected server environment variables, unsafe MCP
URLs, floating package refs, and accidental personal paths. Network checks are
opt-in with `--check-network` and are skipped when `STRONKPI_NO_NETWORK=1`.

## State And Credentials

Mutable runtime state belongs under the user-owned Stronk Pi state root. Provider
credentials are read from environment variables only. Diagnostics redact
secret-like keys and values.

## Security Posture

- Manifest entries must include immutable source, checksum, byte size,
  provenance, compatibility, and creation metadata.
- Network access is denied when `STRONKPI_NO_NETWORK=1`.
- Local absolute artifact paths and local file URLs are denied.
- Archive extraction rejects traversal, symlinks, hardlinks, and special files.
- Public setup files are scanned for unsafe shell patterns, local paths, and
  command-surface drift.
