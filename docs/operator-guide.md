# Operator Guide

## Which Command Do I Run?

| Task | Command | Notes |
| --- | --- | --- |
| Validate setup files and host assumptions | `stronkpi-setup validate` | Setup-only; does not launch Pi. |
| Diagnose setup and MCP registry state | `stronkpi-setup doctor` | Redacts secret-like values. |
| Verify/update pinned artifacts | `stronkpi-setup update` | Uses manifests; respects `STRONKPI_NO_NETWORK=1`. |
| Launch the guarded Pi experience | `stronkpi` | Harness command owned outside this setup repo. |

Stronk Pi is the guarded Pi Coding Agent distribution. This repo owns setup and
manifest validation; the `stronkpi` harness owns runtime launch behavior.

## Routine Checks

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --json --allow-missing-mcp
STRONKPI_NO_NETWORK=1 sh tests/run_offline.sh
```

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
floating package refs, and accidental personal absolute paths. It does not
generate the runtime MCP overlay; overlay generation belongs to the `stronkpi`
harness at launch time.

## Release Readiness

Before any public release, verify:

- gitleaks worktree and history scans pass with redaction;
- public-surface scans pass;
- manifest fixture tests cover good and bad artifacts;
- guard matrix tests pass;
- GitHub repository settings and branch protection are recorded;
- third-party workflow Actions are pinned to full commit SHAs.
