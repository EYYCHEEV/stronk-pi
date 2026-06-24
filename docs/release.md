# Stronk Pi Release SOP

This repo is the public distribution and setup contract.
It consumes immutable `stronk-pi-plugin` releases after the plugin repo publishes them.

## Bump Setup Version

Use this when the setup/distribution package version changes:

```bash
python3 scripts/bump-version.py 0.2.0
STRONKPI_NO_NETWORK=1 sh scripts/verify-release-candidate.sh
```

This updates setup version surfaces only.
It does not change the expected plugin artifact version.

## Import Plugin Release

First publish the matching plugin artifact from `stronk-pi-plugin`.
Then download that release's `BUILD-MANIFEST.json` and import it:

```bash
python3 scripts/import-plugin-release.py /tmp/stronk-pi-plugin-v0.2.0/BUILD-MANIFEST.json
STRONKPI_NO_NETWORK=1 sh scripts/verify-release-candidate.sh
```

The import command updates:

- `manifests/current.json`
- `lib/stronk-pi-guard.py` plugin artifact default
- `roles/stronk/roles.toml` extension path
- deterministic manifest fixtures

Do not import a plugin version before its release artifact and attestation exist.

## Online Gate

After importing a plugin release, verify the public artifact URL:

```bash
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
```

Run this without `STRONKPI_NO_NETWORK=1`.

## Live Update

After the distribution PR is merged:

```bash
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
bin/stronkpi-setup update --manifest manifests/current.json
bin/stronkpi --validate-only
bin/stronkpi --diagnose --json
```

Back up live `~/.stronk-pi` managed files before the non-dry-run update when
operator state may matter.

## Rollback

Before plugin import, close or revert the setup version PR.
After plugin import but before live update, revert the distribution PR.
After live update, restore the previous manifest and plugin default version in a
new PR, merge it, and rerun `bin/stronkpi-setup update --manifest manifests/current.json`.
