---
name: stronk-pi-release
description: >-
  Use inside the stronk-pi distribution repo for Stronk Pi setup and distribution releases: setup version bumps, importing immutable stronk-pi-plugin, stronk-pi-subagents, or stronk-pi-intercom BUILD-MANIFEST artifacts, release-candidate validation, distribution manifest updates, guarded runtime update planning, rollback planning, or questions about the public setup contract.
  Trigger for requests like "bump the Stronk Pi setup version", "import a stronk-pi-intercom release", "import a stronk-pi-plugin release", "verify the distribution release candidate", or "plan the stronk-pi live update".
  Do not use for editing or publishing plugin source; use the plugin release skill in stronk-pi-plugin for that.
---

# Stronk Pi Release

This repo owns the public Stronk Pi distribution contract: setup behavior,
launcher config, role templates, model defaults, package pins, manifest
verification, and generated-agent output paths.
It consumes immutable `stronk-pi-plugin` release artifacts; plugin source changes
belong in the plugin repo.

## First Checks

1. Read `docs/release.md`.
2. Inspect `manifests/current.json`, `lib/stronk-pi-guard.py`, and
   `roles/stronk/roles.toml` when artifact wiring may change.
3. Decide whether the task is a setup version bump, a plugin artifact import, or
   a live runtime update.
4. Do not commit, push, tag, publish, or run non-dry-run live updates without
   explicit operator confirmation for the exact command.

## Setup Version Bump

Use this when the setup/distribution package version changes, independent of the
plugin artifact version:

```sh
python3 scripts/bump-version.py <version>
STRONKPI_NO_NETWORK=1 sh scripts/verify-release-candidate.sh
```

The bump command updates setup version surfaces only.
It intentionally does not update `DEFAULT_PLUGIN_VERSION` or
`manifests/current.json`.

## Plugin Artifact Import

Use this only after the plugin repo has published an immutable artifact,
`BUILD-MANIFEST.json` has been downloaded, and the release attestation has been
verified or explicitly confirmed by the operator:

```sh
python3 scripts/import-artifact-release.py /tmp/stronk-pi-plugin-v<version>/BUILD-MANIFEST.json
STRONKPI_NO_NETWORK=1 sh scripts/verify-release-candidate.sh
```

The import command updates:

- `manifests/current.json`
- `lib/stronk-pi-guard.py` plugin artifact default
- `roles/stronk/roles.toml` extension path
- deterministic manifest fixtures

`scripts/import-plugin-release.py` remains available for plugin-only compatibility imports.

```sh
python3 scripts/import-plugin-release.py /tmp/stronk-pi-plugin-v<version>/BUILD-MANIFEST.json
```

## Runtime Artifact Import

Use this after `stronk-pi-subagents` or `stronk-pi-intercom` has published an immutable artifact, `BUILD-MANIFEST.json` has been downloaded, and the release attestation has been verified or explicitly confirmed by the operator:

```sh
python3 scripts/import-artifact-release.py /tmp/<artifact-tag>/BUILD-MANIFEST.json
STRONKPI_NO_NETWORK=1 sh scripts/verify-release-candidate.sh
```

The import command updates:

- `manifests/current.json`
- `config/defaults.toml`
- `lib/stronk-pi-guard.py` package defaults
- deterministic manifest fixtures

## Online Gate

After importing a plugin, subagents, or intercom release, verify the public artifact URL:

```sh
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
```

Run this without `STRONKPI_NO_NETWORK=1`.

## Live Runtime Update

After the distribution change is merged and the operator confirms the exact
non-dry-run command, use:

```sh
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
bin/stronkpi-setup update --manifest manifests/current.json
bin/stronkpi --validate-only
bin/stronkpi --diagnose --json
```

Back up managed `~/.stronk-pi` files first when operator state may matter.

## Rollback And Recovery

If an import, release-candidate check, or live update fails, read the rollback
section in `docs/release.md` before proposing the next command.
Do not run rollback or live-update commands without explicit operator
confirmation for the exact command.

Include the relevant rollback path in the final report:

- Before plugin import: close or revert the setup version PR.
- After plugin import but before live update: revert the distribution PR.
- After intercom import but before live update: revert the distribution PR.
- After live update: restore the previous manifest and plugin default version in
  a new PR, merge it, then rerun
  `bin/stronkpi-setup update --manifest manifests/current.json`.

## Eval Guidance

Lightweight skill-creator eval prompts live in `evals/evals.json`.
Use them when checking trigger behavior or revising this skill.

## Report

End with the version target, files changed, validation commands and outcomes,
and whether any publish or live-update action still needs operator approval.
