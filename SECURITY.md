# Security

Report security issues privately through the repository security advisory
channel once the repository is published.

## Credential Handling

Provider credentials must be supplied through environment variables. Do not put
credential values in config files, manifests, sessions, generated files, issue
reports, or logs.

Diagnostics redact secret-like keys and common token formats. Redaction is a
defense-in-depth measure, not permission to paste secrets into diagnostics.

## Artifact Policy

Setup and update flows consume pinned manifests. Manifests must include source
repository, full source commit, immutable tag, release URL, SHA-256, byte size,
workflow/run provenance, compatibility version, and creation timestamp.

Local absolute artifact paths, local file URLs, floating version references, and
unchecked archives are rejected.

