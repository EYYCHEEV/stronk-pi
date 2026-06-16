# Operator Guide

## Routine Checks

```zsh
STRONKPI_NO_NETWORK=1 bin/stronkpi validate
STRONKPI_NO_NETWORK=1 bin/stronkpi doctor --json
zsh tests/run_offline.zsh
```

## Fixture Manifest Verification

```zsh
STRONKPI_NO_NETWORK=1 bin/stronkpi update --dry-run --manifest tests/fixtures/manifests/good-local.json
```

Bad fixture manifests must fail without installing anything.

## Release Readiness

Before any public release, verify:

- gitleaks worktree and history scans pass with redaction;
- public-surface scans pass;
- manifest fixture tests cover good and bad artifacts;
- guard matrix tests pass;
- GitHub repository settings and branch protection are recorded;
- third-party workflow Actions are pinned to full commit SHAs.

