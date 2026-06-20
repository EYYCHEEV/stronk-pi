# Stronk Pi Agent Defaults

This directory contains public-safe baseline configuration for Stronk Pi.

Use the `stronkpi-setup` command for setup, validation, update checks, and
redacted diagnostics. Use `stronkpi` for the guarded harness. Provider
credentials must come from environment variables and must not be written into
settings, sessions, generated files, or logs.

Default posture:

- Prefer read-only inspection unless a guarded write flow explicitly grants
  ownership for a bounded task.
- Keep mutable runtime state under the user-owned Stronk Pi state root.
- Use selected Model Context Protocol (MCP) servers only; MCP tool calls must
  name an explicit selected server.
- Treat private, loopback, link-local, metadata, and local file URLs as denied.
- Redact secret-like keys and values in diagnostics.
- Consume pinned manifest artifacts instead of developer checkouts.

Verification for setup-facing config changes:

- Run `python3 -m json.tool config/pi/agent/models.json`.
- Run `python3 -m json.tool config/pi/agent/settings.base.json`.
- Run `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`.
