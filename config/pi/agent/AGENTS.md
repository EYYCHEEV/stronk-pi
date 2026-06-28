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

Upstream boundary hard policy:

- Stronk Pi is a personal distribution.
- Use Stronk-owned forks, local worktrees, and Stronk Pi release/update
  pipelines for Pi runtime or Pi subagent changes.
- Do not open, reopen, edit, comment on, review, or otherwise create public
  activity in original upstream Pi or Pi subagent repositories.
- This ban includes pull requests, issues, discussions, review comments,
  maintainer pings, and follow-up comments.
- Do not push branches, tags, or commits to original upstream Pi or Pi subagent
  remotes.
- Blocked upstream targets include `earendil-works/pi`, `badlogic/pi-mono`,
  `nicobailon/pi-subagents`, and any non-Stronk-owned original upstream for Pi
  runtime or Pi subagent work.
- Use Stronk-owned targets such as `EYYCHEEV/pi-mono`,
  `EYYCHEEV/stronk-pi-subagents`, `EYYCHEEV/stronk-pi-plugin`, and
  `EYYCHEEV/stronk-pi` instead.
- General approval for git operations, release work, or end-to-end execution
  does not override this policy.
- Only an explicit same-turn user instruction naming the exact upstream repo,
  exact action, and exact text or command can override it.
- If that explicit override is absent, stop before any upstream public action
  and report the blocked command.

Verification for setup-facing config changes:

- Run `python3 -m json.tool config/pi/agent/models.json`.
- Run `python3 -m json.tool config/pi/agent/settings.base.json`.
- Run `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`.
