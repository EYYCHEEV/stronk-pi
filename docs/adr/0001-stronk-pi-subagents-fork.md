# ADR 0001: Stronk Pi Subagents Fork Distribution

## Status

Accepted on 2026-06-28.

## Context

Stronk Pi generates guarded Pi role files under `~/.stronk-pi/agent/agents` and exports `PI_CODING_AGENT_DIR` to child Pi processes.
Upstream `pi-subagents@0.22.0` discovers user agents and user settings under legacy `~/.pi/agent` paths.
That mismatch can make live guarded subagent roles unavailable unless legacy paths are present.

The current safe upstream base is `nicobailon/pi-subagents@0.22.0`, commit `1fd371d2a068458741a15507edc6cd49a9807486`.
The newer upstream `pi-subagents@0.31.0` was published on 2026-06-24 and is inside the 14-day supply-chain window for this rollout.
`stronk-pi-subagents` is not published to npm, so a first npm rollout would not satisfy the age gate.

## Decision

Stronk Pi will distribute a Stronk-owned fork package named `stronk-pi-subagents`.
The first version is `0.22.0-stronk.3` on branch `stronk-pi-subagents` in `EYYCHEEV/stronk-pi-subagents`.
The first rollout uses an immutable GitHub release asset:

- Tag: `stronk-pi-subagents-v0.22.0-stronk.3`
- Asset: `stronk-pi-subagents-0.22.0-stronk.3.tgz`
- Source commit: `afe08d9a0c84a5c1de4a8de1dda82868c96a6ce0`
- SHA-256: `23aa7beac6ecca0f8d20824cb33f93cfac7fbe00488cb5fea85878a7876f18e4`
- Workflow run id: `28301945900`
- Runtime root: `~/.stronk-pi/artifacts/stronk-pi-subagents-0.22.0-stronk.3/package`

The fork must resolve user agent state in this order:

1. `PI_CODING_AGENT_DIR`
2. `TAU_CODING_AGENT_DIR`
3. `~/.pi/agent`

The Stronk Pi manifest must carry the fork source repo, fork commit, release tag, artifact checksum, verified GitHub artifact attestation, and upstream base metadata.
The setup guard must reject package roots and archives that only contain `package.json`; the fork package must include the expected source, bundled agents, and skill files.

## Consequences

`stronkpi-setup update` materializes the fork artifact under the Stronk state root instead of relying on global npm state.
Live subagent runtime still requires `pi-intercom@0.6.0`; that package identity and bridge contract are unchanged.
Rollback reverts Stronk Pi pins and manifest artifacts to the previous upstream package pin and removes or ignores the installed fork artifact root.

Public npm distribution remains deferred until a published fork version has aged 14 full days or the operator explicitly accepts a one-off exception.
