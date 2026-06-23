# Operator Guide

## Which Command Do I Run?

| Task | Command | Notes |
| --- | --- | --- |
| Validate setup files and host assumptions | `stronkpi-setup validate` | Setup-only; does not launch Pi. |
| Diagnose setup and MCP registry state | `stronkpi-setup doctor` | Redacts secret-like values. |
| Refresh managed runtime config | `stronkpi-setup refresh-config` | Updates `~/.stronk-pi/config`, `~/.stronk-pi/agent/settings.json`, and generated role Markdown. |
| Verify/update pinned artifacts | `stronkpi-setup update` | Uses manifests; respects `STRONKPI_NO_NETWORK=1`. |
| Validate guarded harness config | `stronkpi --validate-only` | Checks the harness without launching an interactive Pi session. |
| Launch the guarded Pi experience | `stronkpi` | Portable harness installed by the Stronk Pi distribution repo. |

Stronk Pi is the guarded Pi Coding Agent distribution. This repo owns setup and
manifest validation; the `stronkpi` harness owns runtime launch behavior.

## Routine Checks

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --json --allow-missing-mcp
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup refresh-config --dry-run
STRONKPI_NO_NETWORK=1 bin/stronkpi --validate-only
STRONKPI_NO_NETWORK=1 sh tests/run_offline.sh
```

Use `stronkpi-setup refresh-config` after changing distribution-owned runtime config
templates such as `config/pi/agent/settings.base.json`.
The shipped coding default is `kimi-coding/kimi-for-coding` with Pi
`defaultThinkingLevel` set to `xhigh`.
Add `--json` for automation.

## Fixture Manifest Verification

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
```

Bad fixture manifests must fail without installing anything.

## MCP Registry Doctor

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --mcp-registry ~/.config/mcp/registry.toml --mcp-tools .mcp-tools
```

The MCP registry check validates registry TOML, server command availability,
selected tool names, selected server environment variables, unsafe URLs,
floating package refs, and accidental personal absolute paths. Runtime MCP
loading is not enabled until the guarded launcher includes a verified MCP
adapter artifact.

## Local Role Overlay

Public defaults are installed to `~/.stronk-pi/config/roles.toml`.
Private local preferences can be placed in
`~/.stronk-pi/config/roles.local.toml`.
The overlay is optional and is never required for public setup.

## Release Readiness

Before any public release, verify:

- gitleaks worktree and history scans pass with redaction;
- public-surface scans pass;
- manifest fixture tests cover good and bad artifacts;
- guard matrix tests pass;
- GitHub repository settings and branch protection are recorded;
- third-party workflow Actions are pinned to full commit SHAs.
