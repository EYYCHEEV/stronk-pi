# Architecture

`stronkpi` is a setup surface around four boundaries:

- command entrypoint: `bin/stronkpi`
- guard and manifest verifier: `lib/stronk-pi-guard.py`
- public-safe Pi config templates: `config/pi/`
- release manifest inputs: `manifests/`

The setup repo does not own provider credentials or mutable runtime sessions.
It prepares and validates a state root owned by the current user and verifies
release artifacts before they can be installed.

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

