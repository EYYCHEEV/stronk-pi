# Stronk Pi Setup

`stronkpi` is the canonical setup and validation command for Stronk Pi.

This repository provides a public-ready installer, manifest verifier, guarded
diagnostics, safe baseline configuration, and offline tests. End users consume
pinned release manifests and verified artifacts. Developer checkouts and
maintainer release tooling are not part of the end-user flow.

## Install

Preview installation without writing to your command directory:

```zsh
./install.sh --dry-run
```

Install the command into `~/.local/bin`:

```zsh
./install.sh
```

The installer creates only `stronkpi`.

## Validate

Run the offline setup checks:

```zsh
STRONKPI_NO_NETWORK=1 bin/stronkpi validate
STRONKPI_NO_NETWORK=1 bin/stronkpi doctor --json
```

Verify an offline fixture manifest:

```zsh
STRONKPI_NO_NETWORK=1 bin/stronkpi update --dry-run --manifest tests/fixtures/manifests/good-local.json
```

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

