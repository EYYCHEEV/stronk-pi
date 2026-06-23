# Architecture

Stronk Pi is a guarded Pi Coding Agent distribution built on Pi. The
distribution includes setup manifests, a guarded launch harness, a plugin
artifact, a trusted Pi runtime, and user-owned state.

`stronkpi-setup` is the setup command in the `stronk-pi` distribution repo. It owns
four boundaries:

- setup entrypoint: `bin/stronkpi-setup`
- portable guarded harness: `bin/stronkpi`
- guard, config generator, and manifest verifier: `lib/stronk-pi-guard.py`
- public-safe Pi config templates: `config/pi/`
- public role templates and role manifest: `roles/stronk/`
- release manifest inputs: `manifests/`

`stronkpi` is the guarded harness name and is shipped by this distribution repo.
Setup, config refresh, update, and diagnostics remain available through
`stronkpi-setup`.

The guarded harness protects normal Pi execution with fail-closed controls for
tool permissions, unsafe shell commands, secret and path handling, trusted
runtime drift, Model Context Protocol (MCP) configuration, and subagent role
loading.

`stronkpi-setup` uses a Python entrypoint and a POSIX `sh` installer so public
setup does not require a specific login shell. Shell aliases such as short
local commands remain outside this repo.

The distribution repo does not own provider credentials or mutable runtime sessions.
It prepares and validates a state root owned by the current user and verifies
release artifacts before they can be installed.

## Config Precedence

Runtime config resolves in this order:

1. distribution-owned defaults in this repo;
2. installed defaults under `~/.stronk-pi/config/defaults.toml`;
3. installed default role manifest under `~/.stronk-pi/config/roles.toml`;
4. optional local overlay under `~/.stronk-pi/config/roles.local.toml`;
5. explicit allowlisted environment variables.

Generated Pi agent Markdown is rendered under `~/.stronk-pi/agent/agents/`.
It is runtime output and must not be tracked as public source.
`stronkpi-setup refresh-config` is the explicit operator command for writing
the setup-managed defaults, Pi agent settings, model config, role templates,
and generated role Markdown into `~/.stronk-pi/` without launching Pi.

## MCP Registry Doctor

`stronkpi-setup doctor` validates the user-local MCP registry at
`~/.config/mcp/registry.toml` or the path passed with `--mcp-registry`. It
checks registry TOML, server command availability, selected `.mcp-tools`
entries, selected server environment variables, unsafe URLs, floating package
refs, and accidental personal paths.

`stronkpi` does not currently load a runtime MCP adapter. The setup repo owns
the registry and `.mcp-tools` validation boundary; runtime MCP loading remains
deferred until a verified MCP adapter artifact is included in the launch
extension set.

## Manifest Flow

1. Parse the manifest schema.
2. Reject mutable versions, local absolute paths, and local file URLs.
3. Resolve only approved local fixtures in offline tests, or public HTTPS
   artifacts when network access is allowed.
4. Verify byte size and SHA-256 before archive inspection.
5. Reject archive traversal, symlinks, hardlinks, and special files.
6. Install atomically only after verification passes.

## Offline Mode

`STRONKPI_NO_NETWORK=1` makes network artifact access fail closed. Offline tests
use fixture artifacts under `tests/fixtures/`.
