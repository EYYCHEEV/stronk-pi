# Stronk Pi

`stronkpi-setup` is the setup and validation command for Stronk Pi.
Stronk Pi is the guarded Pi Coding Agent distribution.
`stronkpi` is the portable guarded harness installed by this distribution repo.

This repository provides the public bundle contract: setup and doctor behavior,
manifest verification, the portable harness, public-safe role templates,
default role/config/model files, package pins, generated-agent output paths, and
offline tests. Mutable runtime output is installed under `~/.stronk-pi/`.

## Name Map

| Name | Meaning |
| --- | --- |
| Stronk Pi | Guarded Pi Coding Agent distribution. |
| `stronkpi` | Guarded harness command that launches Pi with Stronk Pi controls. |
| `stronkpi-setup` | Setup, validation, diagnostics, and artifact update command. |
| `stronk-pi` | Public distribution repo and bundle contract. |
| `stronk-pi-plugin` | Plugin source repo and verified artifact consumed by setup manifests. |
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

The installer creates `stronkpi-setup` and `stronkpi`. It does not create short
compatibility aliases.

## Validate

Run the offline setup checks:

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --json --allow-missing-mcp
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --mcp-registry ~/.config/mcp/registry.toml
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup refresh-config --dry-run
STRONKPI_NO_NETWORK=1 bin/stronkpi --validate-only
```

Verify an offline fixture manifest:

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
```

`doctor` validates the distribution host, bundle contract, harness presence, role
manifest status, optional `roles.local.toml` overlay status, plugin artifact
status, trusted runtime status, and MCP registry. It checks Python availability,
state-root safety, registry TOML shape, server commands, selected `.mcp-tools`
names, selected server environment variables, unsafe MCP URLs, floating package
refs, and accidental personal paths. Network checks are opt-in with
`--check-network` and are skipped when `STRONKPI_NO_NETWORK=1`.

## Runtime Config

The canonical runtime state and config root is `~/.stronk-pi/`.

`stronkpi-setup refresh-config` installs or refreshes:

- `~/.stronk-pi/config/defaults.toml`
- `~/.stronk-pi/config/roles.toml`
- `~/.stronk-pi/config/role-templates/*.toml`
- generated runtime role Markdown under `~/.stronk-pi/agent/agents/`

It also refreshes setup-managed Pi runtime config under
`~/.stronk-pi/agent/`, including `settings.json`, `models.json`, and
`AGENTS.md`.
The public default coding model is `kimi-coding/kimi-for-coding` with Pi
`defaultThinkingLevel` set to `xhigh`.
Use `--dry-run` to preview changed paths and `--json` for automation.

`stronkpi-setup update` verifies the release manifest, also refreshes the same
managed runtime config, and installs or refreshes:

- verified plugin artifacts under `~/.stronk-pi/artifacts/`

Private local preferences belong in `~/.stronk-pi/config/roles.local.toml`.
Generated role Markdown is runtime output, not tracked source.

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
