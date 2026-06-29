# Stronk Runtime Paths And Subagent Contract ExecPlan

## Objective

Move the Stronk Pi subagent runtime fully onto Stronk-owned packages, Stronk-managed state paths, and a compact subagent facade contract.

The end state is:

- `pi-intercom` is forked into a Stronk-owned `stronk-pi-intercom` package and release stream.
- `stronk-pi-subagents` consumes `stronk-pi-intercom` and no longer writes to or depends on real-home `~/.pi` state for Stronk-managed runtime behavior.
- The Stronk Pi distribution imports and verifies the intercom package as a first-class immutable artifact, alongside `stronk-pi-plugin` and `stronk-pi-subagents`.
- The `stronk_subagent` facade returns compact lifecycle results by default, while detailed child output is stored in a separate ledger/artifact path and read through a bounded explicit read path.
- `stronkpi-agents` instructions align with the compact contract so agents stop carrying large action JSON through normal lifecycle calls.

## Completion Status

Status: completed on 2026-06-29.

The completed release set is:

- `stronk-pi-intercom-v0.6.0-stronk.1`.
- `stronk-pi-subagents-v0.22.0-stronk.5`.
- `stronk-pi-plugin-v0.2.3`.
- `stronk-pi-v0.2.3`.

The live runtime was refreshed under `~/.stronk-pi`, validated, diagnosed, and proven through a tmux-launched Stronk Pi run using `kimi-coding/kimi-for-coding:xhigh`.
The live proof exercised `stronk_subagent` `spawn`, `wait_all`, bounded `read_output`, and `close_all`; compact lifecycle payloads stayed below the 2048-byte default budget and no new real-home `~/.pi` writes were observed.

## Scope

In scope:

- Create or adopt the Stronk-owned `EYYCHEEV/stronk-pi-intercom` repository from verified upstream source provenance.
- Update `EYYCHEEV/stronk-pi-subagents` so intercom state, config, logs, locks, sockets, and artifacts use the Stronk Pi state root contract.
- Update `EYYCHEEV/stronk-pi-plugin` if the compact facade requires ledger, schema, Model Context Protocol (MCP) tool, or public JSON behavior changes.
- If `stronk-pi-plugin` changes, build, verify, and import a new immutable plugin artifact before the distribution can be considered complete.
- Update this distribution repo so manifests, defaults, guard verification, release candidate validation, and setup/update flows understand the intercom artifact.
- Update `stronkpi-agents` skill guidance to prefer compact lifecycle actions and bounded explicit output reads.
- Add tests and release gates that prove no Stronk-managed runtime flow writes to real-home `~/.pi`.

Out of scope:

- Public activity in original upstream repositories.
- Non-dry-run writes to the user's live `~/.stronk-pi` state root without separate same-turn operator confirmation.
- Deleting or pruning legacy artifacts from the user's live runtime state.
- Migrating arbitrary unrelated user files under `~/.pi`.
- Seeding the intercom fork from the live installed `~/.stronk-pi` package copy. The live installed package is evidence only, not source provenance.

## Hard Constraints

- Do not create pull requests, issues, comments, branches, tags, or commits in original upstream Pi, Pi subagent, or intercom repositories.
- Blocked upstream targets include `earendil-works/pi`, `badlogic/pi-mono`, `nicobailon/pi-subagents`, and the original upstream intercom repository once identified.
- Use Stronk-owned targets only, such as `EYYCHEEV/pi-mono`, `EYYCHEEV/stronk-pi-subagents`, `EYYCHEEV/stronk-pi-plugin`, `EYYCHEEV/stronk-pi-intercom`, and `EYYCHEEV/stronk-pi`.
- Before any sibling repository push, tag, release, or pull request, perform a same-turn remote ownership preflight after operator confirmation for git operations. Confirm every push/release target is Stronk-owned and record the evidence in `LOGS.md`.
- Do not begin Phase 1, Phase 2, or Phase 3 until Decision Gate 0 and Decision Gate 1 are closed in `LOGS.md` with no blockers.
- Do not run non-dry-run setup/update commands against live `~/.stronk-pi` until the final live-update gate is explicitly confirmed.
- Public package installs or executions remain subject to the 14-day supply-chain rule unless the operator explicitly accepts a one-time exception. Stronk-owned release artifacts may be treated as internal trusted artifacts only after provenance, attestation, source, and manifest checks pass.

## Execution Readiness Boundary

This plan was execution-ready for Phase 0 only until Decision Gate 0 and Decision Gate 1 were closed.

Implementation phases were intentionally blocked until these two gates were closed:

- Decision Gate 0: intercom fork provenance, seed, package identity, bridge mode, and no-real-home-`.pi` policy.
- Decision Gate 1: compact facade contract, plugin release requirement, byte budgets, redaction policy, and output-ledger behavior.

Both gates are recorded in `LOGS.md`, and the plan proceeded through fork, package, plugin, distribution, release, runtime refresh, and live tmux proof.

## Initial Findings

These findings captured the pre-implementation state before the gates were closed and the release set was built.

Distribution state:

- `manifests/current.json` currently pins two artifacts:
  - `stronk-pi-plugin` version `0.2.2`.
  - `stronk-pi-subagents` version `0.22.0-stronk.4`.
- `config/defaults.toml` currently lists the runtime packages:
  - `stronk-pi-subagents@0.22.0-stronk.4`.
  - `pi-intercom@0.6.0`.
- `roles/stronk/roles.toml` currently includes `"pi-intercom"` in `packages`.
- `lib/stronk-pi-guard.py` currently has artifact identity and required-member checks for `stronk-pi-plugin` and `stronk-pi-subagents`, but not for an intercom artifact.
- `lib/stronk-pi-guard.py` currently launches the subagent runtime with an explicit `STRONK_PI_INTERCOM_BRIDGE` path and reports status fields named `intercomBridgePath`, `intercomBridgeTarget`, and `intercomBridgeLinked`.
- `tests/test_manifest_verifier.py` currently asserts that `STRONK_PI_INTERCOM_BRIDGE` points at the installed `pi-intercom` bridge path.
- `scripts/import-plugin-release.py` is plugin-specific. It cannot import intercom or subagent artifacts without a new generic importer or dedicated importer.

Installed package evidence:

- The installed `pi-intercom@0.6.0` package under `~/.stronk-pi` contains multiple hardcoded `~/.pi/agent/intercom` defaults.
- Relevant installed files include `package/index.ts`, `package/config.ts`, `package/broker/paths.ts`, `package/broker/spawn.ts`, and `package/broker/broker.ts`.
- This installed package is useful for behavior inspection but must not be the fork seed.

Sibling repo evidence:

- The local `stronk-pi-subagents` worktree has remaining `~/.pi` references in run history, config, intercom bridge integration, artifacts, and user-agent-dir handling.
- The local `pi-mono` worktree was searched for `pi-intercom` and did not appear to contain the package source.
- The local `stronk-pi-intercom` worktree does not exist yet.

Subagent facade evidence:

- The plugin bridge currently caps terminal result text at `8192` bytes and caps public child lists at `6` records.
- `read_output` defaults to `12000` characters.
- Several facade actions return full public child records today, not only `wait_all` and `close_all`.
- Actions needing compact-contract review include `spawn`, `list`, `status`, `wait`, `wait_all`, `send_input`, `revive`, `interrupt`, `close`, and `close_all`.
- `read_output` currently lacks an explicit `artifactKind` or equivalent field.
- `clearChildOutput` clears output handles while preview fields can remain, so a final cleaned-up ledger snapshot with null handles is not standalone proof of async terminal refresh behavior.

Session evidence:

- Investigated session: `019f0eb2-302f-7486-bf0d-0e9837189648`.
- The session file under `~/.stronk-pi/artifacts/runs/` embeds the entire `stronk-agents` skill text in the user prompt.
- The session also shows `stronk_subagent.wait_all` and `stronk_subagent.close_all` lifecycle actions returning large JSON payloads with child records and output previews.
- The final `children.json` snapshot was inspected after `close_all`; missing output handles there are consistent with cleanup clearing handles, while preview fields remained.
- Therefore the bloat problem has two sources:
  - Prompt-side bloat from embedding large skill instructions into a session.
  - Runtime-side bloat from oversized lifecycle action responses.
- The current `stronk-agents` skill already treats `wait_all` as a barrier and recommends bounded `read_output` as fallback. The required improvement is to align instructions with a leaner runtime contract, not to imply the current skill intentionally tells agents to request full payloads.

## Target Runtime Contract

### State Roots

Canonical Stronk-managed runtime state:

- `STRONKPI_STATE_ROOT` or `STRONK_PI_STATE_ROOT` selects the state root.
- Default state root remains `~/.stronk-pi`.
- Intercom state must live under the selected Stronk Pi state root, for example:
  - `~/.stronk-pi/agent/intercom`
  - `~/.stronk-pi/agent/intercom/logs`
  - `~/.stronk-pi/agent/intercom/sockets`
  - `~/.stronk-pi/agent/intercom/locks`

Forbidden for Stronk-managed runtime behavior:

- New writes to real-home `~/.pi`.
- Hidden fallback to `~/.pi` when Stronk state-root environment variables are present.
- Test fixtures that pass because `HOME` happens to point at a temporary directory while the runtime still uses `~/.pi`-relative defaults.

Allowed with explicit classification:

- Test fixtures containing `.pi` inside temporary directories.
- Documentation that references old upstream behavior as history.
- Migration or cleanup tooling that inspects real-home `~/.pi` only under an explicit dry-run or apply gate.
- One-release compatibility alias if Decision Gate 0 chooses that bridge mode and the alias is under Stronk-managed control.

### Intercom Package

Target package:

- Name: `stronk-pi-intercom`.
- Owner: Stronk-owned GitHub repository, expected `EYYCHEEV/stronk-pi-intercom`.
- Runtime path behavior: Stronk state-root aware.
- Artifact status: first-class distribution artifact with manifest identity, source, digest, attestation, required-member checks, and release provenance.

Required archive/runtime-member candidates:

- `package/index.ts`
- `package/config.ts`
- `package/broker/paths.ts`
- `package/broker/spawn.ts`
- `package/broker/broker.ts`
- package metadata files needed by the installer and runtime bridge

The exact required-member list must be finalized in Decision Gate 0 after source provenance is confirmed.

### Subagents Package

Target package:

- Name remains `stronk-pi-subagents`.
- It must depend on `stronk-pi-intercom` instead of upstream `pi-intercom`, unless Decision Gate 0 explicitly chooses a short dual-bridge transition.
- It must honor Stronk state roots consistently across launch, config, artifacts, run history, intercom bridge, and generated agent paths.

### Facade JSON Contract

Lifecycle actions should return compact, stable summaries:

- action name
- request id
- aggregate status
- counts by status
- child ids
- short error summary, if any
- artifact or ledger pointer for details
- bounded preview only when explicitly requested and under a strict byte budget

Lifecycle actions should not return full child records or multi-kilobyte previews by default.

Detailed output should be retrieved through explicit bounded reads:

- `read_output`
- `read_artifact`, if added
- ledger/artifact path returned as a pointer, not inline content

`read_output` or its successor must include enough metadata to let agents know what was read, including an `artifactKind` or equivalent field.

Redaction requirements:

- Compact lifecycle responses must not leak secrets.
- Compact lifecycle responses must avoid unnecessary absolute local paths.
- Ledger/read APIs must preserve bounded access and should redact known secret-like values in public summaries.

## Decision Gates

### Decision Gate 0: Intercom Fork And Path Policy

Before implementation, record in `LOGS.md`:

- Exact original upstream repository for `pi-intercom`.
- Exact seed source type:
  - npm tarball
  - upstream source commit
  - Stronk-owned mirror
  - other explicitly approved source
- Npm package name and version used as seed, if applicable.
- Npm tarball URL, registry integrity/SRI, and computed tarball SHA256, if applicable.
- Source URL, upstream repository, commit SHA, and package file list used as fork seed.
- Confirmation that live installed `~/.stronk-pi` files were not used as fork seed.
- Required intercom archive/runtime members.
- Whether the transition is:
  - hard cutover to `stronk-pi-intercom`, or
  - one-release dual alias with a clear managed alias path and removal plan.
- How the original intercom upstream is added to blocked-upstream policy.
- How manifest seed/provenance metadata is enforced by guard/tests, not only written in logs.
- How project-local `.pi` fixtures are distinguished from real-home `~/.pi` writes.

### Decision Gate 1: Compact Facade Contract

Before implementation, record in `LOGS.md`:

- Exact compact response schema for:
  - `spawn`
  - `list`
  - `status`
  - `wait`
  - `wait_all`
  - `send_input`
  - `revive`
  - `interrupt`
  - `close`
  - `close_all`
- Exact default response byte budget for lifecycle calls.
- Exact default and maximum byte budget for explicit output reads.
- Whether `read_output` is enough or a new `read_artifact` action is needed.
- How artifact pointers are represented.
- Whether output handles survive `close`/`close_all`, or whether a post-close ledger pointer is the supported read path.
- Whether the plugin facade changes require a new `stronk-pi-plugin` version and immutable artifact import.
- Redaction canary cases for secrets, tokens, environment values, absolute paths, and prompt text.
- Compatibility behavior for older agents or sessions that expect full public child records.

## Task Checklist

### Phase 0: Evidence And Gate Closure

- [x] Create the ExecPlan workspace.
- [x] Inspect current distribution manifest, defaults, guard, and runtime launch behavior.
- [x] Inspect installed intercom behavior under `~/.stronk-pi`.
- [x] Inspect local `stronk-pi-subagents` for `.pi` and intercom references.
- [x] Inspect session `019f0eb2-302f-7486-bf0d-0e9837189648` for JSON bloat evidence without running `stronkpi --session`.
- [x] Run read-only swarm review of the plan.
- [x] Fold swarm findings into the plan.
- [x] Locate the authoritative upstream source for `pi-intercom` without creating upstream public activity.
- [x] Record a source/provenance package inventory for intercom in `LOGS.md`.
- [x] Define the remote ownership preflight checklist for all sibling repos.
- [x] Add the discovered original intercom upstream to the blocked-upstream list design.
- [x] Build a classification table for every `.pi` reference found in distribution, subagents, plugin, and intercom source.
- [x] Close Decision Gate 0 in `LOGS.md`.
- [x] Close Decision Gate 1 in `LOGS.md`.
- [x] Confirm no Phase 1, Phase 2, or Phase 3 work starts before both gates are closed.

### Phase 1: Fork `stronk-pi-intercom`

- [x] Create or prepare the Stronk-owned `EYYCHEEV/stronk-pi-intercom` repository only after same-turn operator confirmation for repo creation or git activity.
- [x] Seed the fork from the approved source recorded in Decision Gate 0.
- [x] Confirm the fork seed is not the live installed `~/.stronk-pi` package copy.
- [x] Rename package identity from `pi-intercom` to `stronk-pi-intercom`.
- [x] Replace hardcoded `~/.pi/agent/intercom` defaults with Stronk state-root aware path resolution.
- [x] Add tests proving default paths land under a temp Stronk state root.
- [x] Add tests proving explicit state root environment variables override default paths.
- [x] Add tests proving real-home `~/.pi` is not written during normal runtime operations.
- [x] Add required package metadata for Stronk-owned release and artifact provenance.
- [x] Add release/build script or document existing package manager release flow.
- [x] Record package file list, required archive members, source commit, tag, and artifact digest in `LOGS.md`.

### Phase 2: Update `stronk-pi-subagents`

- [x] Apply the bridge mode chosen in Decision Gate 0.
- [x] Replace `pi-intercom` dependency with `stronk-pi-intercom`, unless a one-release dual alias is explicitly chosen.
- [x] Update intercom bridge resolution to prefer Stronk package identity and Stronk state root.
- [x] Replace real-home `~/.pi` defaults in run history, config, artifacts, and user-agent-dir handling.
- [x] Preserve explicitly classified project-local `.pi` fixtures where they are legitimate.
- [x] Add unit tests for state-root resolution.
- [x] Add integration tests launching through isolated `HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `STRONKPI_STATE_ROOT`, and `STRONK_PI_STATE_ROOT`.
- [x] Add tests for a legacy `pi-intercom`-only runtime, with explicit accept or reject behavior documented.
- [x] Add tests proving no writes occur under real-home `~/.pi`.
- [x] Update package version according to the Stronk package versioning convention.
- [x] Record release and rollback steps in `LOGS.md`.

### Phase 3: Compact Subagent Facade And Agent Instructions

- [x] Implement or update compact lifecycle response schemas for all actions listed in Decision Gate 1.
- [x] Ensure lifecycle calls return only summary fields and pointers by default.
- [x] Ensure bounded detailed reads are available through `read_output` or the chosen successor.
- [x] Add `artifactKind` or equivalent metadata to explicit read results.
- [x] Implement post-close output access through persistent opaque ledger/output handles.
- [x] Add byte-budget tests for `spawn`, `list`, `status`, `wait`, `wait_all`, `close`, and `close_all`.
- [x] Add tests proving `read_output` stays bounded by requested and maximum limits.
- [x] Add redaction canary tests for compact lifecycle results and explicit read summaries.
- [x] Add tests using session-shaped payloads similar to `019f0eb2-302f-7486-bf0d-0e9837189648`.
- [x] Update `stronkpi-agents` guidance so lifecycle calls are treated as barriers/status summaries and output is fetched only through bounded explicit reads when necessary.
- [x] If plugin code changes, bump plugin version, produce immutable plugin artifact, and import it into the distribution in Phase 5.

### Phase 4: Artifact Releases And Provenance

- [x] After operator confirmation for git/release activity, run remote ownership preflight for each target repo.
- [x] Build and test `stronk-pi-intercom`.
- [x] Publish or otherwise prepare the Stronk-owned `stronk-pi-intercom` artifact according to the approved release flow.
- [x] Build and test the updated `stronk-pi-subagents`.
- [x] Publish or otherwise prepare the Stronk-owned `stronk-pi-subagents` artifact.
- [x] If plugin code changed, build, test, publish, and produce an immutable `stronk-pi-plugin` artifact.
- [x] Verify source, tag, digest, attestation, and required archive members for every artifact.
- [x] Record artifact provenance in `LOGS.md`.

### Phase 5: Distribution Import

- [x] Add first-class intercom artifact identity to `lib/stronk-pi-guard.py`.
- [x] Add package archive required-member checks for `stronk-pi-intercom`.
- [x] Add runtime package required-path checks for `stronk-pi-intercom`.
- [x] Add manifest seed/provenance metadata checks for intercom.
- [x] Add or generalize artifact import tooling:
  - either `scripts/import-artifact-release.py`, or
  - dedicated `scripts/import-intercom-release.py` and `scripts/import-subagents-release.py`.
- [x] Keep `scripts/import-plugin-release.py` for plugin artifacts, or fold it into the generic importer with tests.
- [x] Update `manifests/current.json` with the new intercom artifact and updated subagents artifact.
- [x] Update `config/defaults.toml` and `roles/stronk/roles.toml` to use `stronk-pi-intercom`.
- [x] Update tests and fixtures for a three-artifact manifest.
- [x] Add tests rejecting wrong intercom identity, wrong source owner, wrong seed metadata, missing attestation, bad digest, and missing required members.
- [x] Add tests rejecting or explicitly handling manifests that only provide legacy `pi-intercom`.
- [x] If plugin changed, import the new plugin artifact with the approved plugin import flow and update manifest/plugin pins.
- [x] Update release candidate verification to cover all three runtime artifacts.

### Phase 6: Validation

- [x] Run Python syntax and shell syntax checks for modified distribution scripts.
- [x] Run distribution unit tests under polluted ambient environment.
- [x] Run distribution unit tests under scrubbed environment.
- [x] Run `stronk-pi-intercom` unit tests after the worktree exists.
- [x] Run `stronk-pi-subagents` unit and integration tests.
- [x] Run `stronk-pi-plugin` tests if plugin code changed.
- [x] Run a temp-root install/update smoke with isolated:
  - `HOME`
  - `XDG_CONFIG_HOME`
  - `XDG_CACHE_HOME`
  - `STRONKPI_STATE_ROOT`
  - `STRONK_PI_STATE_ROOT`
- [x] In the temp-root smoke, materialize artifacts through setup/update rather than relying only on local worktree paths.
- [x] In the temp-root smoke, run diagnose/status checks and assert intercom bridge path points to `stronk-pi-intercom`.
- [x] In the live tmux proof, run compact `spawn`, `wait_all`, bounded `read_output`, and `close_all` flows from the refreshed runtime.
- [x] Assert no files are created under real-home `~/.pi`.
- [x] Run a session-size regression using either an inline one-off script recorded in `LOGS.md` or a committed helper added during implementation.
- [x] Run release candidate verification only after exact operator confirmation, because the release script includes git checks.

### Phase 7: Release And Live Update Gates

- [x] Prepare release notes for every changed Stronk-owned repo.
- [x] Confirm exact git, tag, pull request, and release commands before running them.
- [x] Merge/publish only Stronk-owned repos.
- [x] Confirm the distribution release candidate after all artifacts are imported.
- [x] Stop before non-dry-run live update.
- [x] On explicit same-turn confirmation, run:

```sh
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
bin/stronkpi-setup update --manifest manifests/current.json
bin/stronkpi --validate-only
bin/stronkpi --diagnose --json
```

- [x] Run the live tmux Stronk Pi proof with `kimi-coding/kimi-for-coding:xhigh`.
- [x] Record proof commands, logs, release URLs, artifact hashes, and rollback instructions in `LOGS.md`.

## Validation Plan

Distribution checks:

```sh
python3 -m py_compile lib/stronk-pi-guard.py scripts/*.py tests/*.py bin/*
zsh -f -n scripts/verify-release-candidate.sh
zsh -f -n tests/run_offline.sh
STRONKPI_NO_NETWORK=1 python3 -m unittest discover -s tests -p "test_*.py"
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate
```

Intercom checks, after `stronk-pi-intercom` exists:

```sh
cd ../stronk-pi-intercom
npm test
npm run lint
```

Subagents checks, exact commands to be confirmed from that repo:

```sh
cd ../stronk-pi-subagents
rg -n '\.pi|pi-intercom|stronk-pi-intercom|STRONKPI_STATE_ROOT|STRONK_PI_STATE_ROOT'
```

Plugin checks, if plugin code changes:

```sh
cd ../stronk-pi-plugin
node --test
npm run lint:security
```

Temp-root smoke shape:

```sh
tmp="$(mktemp -d)"
HOME="$tmp/home" \
XDG_CONFIG_HOME="$tmp/xdg-config" \
XDG_CACHE_HOME="$tmp/xdg-cache" \
STRONKPI_STATE_ROOT="$tmp/state" \
STRONK_PI_STATE_ROOT="$tmp/state" \
bin/stronkpi-setup update --manifest manifests/current.json
```

The smoke must assert:

- installed packages include `stronk-pi-intercom`.
- installed packages do not require upstream `pi-intercom` unless explicitly selected by Decision Gate 0 compatibility mode.
- intercom bridge path resolves under `$tmp/state`.
- lifecycle facade responses stay within the selected byte budget.
- detailed output remains accessible through bounded explicit read.
- no files are created under real-home `~/.pi`.

## Rollback Plan

Before live update:

- Revert distribution manifest/default/guard changes through git.
- Revert sibling repo pull requests through Stronk-owned repositories only.
- Delete or supersede Stronk-owned tags/releases if needed.
- If plugin artifact was imported, revert plugin manifest pins and distribution import commit.
- No live user state rollback is needed if non-dry-run update was not executed.

After live update:

- Restore the previous `manifests/current.json` artifact pins.
- Run the setup/update rollback command approved by the operator.
- Restore the retained pre-update backup under `~/.stronk-pi/backups/2026-06-29/pre-stronkpi-0.2.3-20260629-100159.tgz` if needed.
- Keep old artifacts in `~/.stronk-pi/artifacts` unless a separate prune operation is explicitly confirmed.

## Risks

- The upstream source for `pi-intercom` may not be in the local `pi-mono` worktree and must be identified without upstream public activity.
- Adding a third artifact changes the distribution trust model and installer verification surface.
- Compacting lifecycle JSON can break callers that depended on full child records.
- Keeping a dual alias for compatibility can prolong old naming and path confusion.
- Hard cutover can break older installed state that expects `pi-intercom`.
- Redaction and path minimization must not hide information needed for debugging.
- GitHub release or npm provenance behavior may differ between Stronk-owned repos and public upstream packages.

## Open Questions

None.

Resolved during execution:

- The distribution uses the generic `scripts/import-artifact-release.py` importer while preserving `scripts/import-plugin-release.py`.
- The completed distribution setup version is `0.2.3`.
- Protected repos used the Stronk-owned pull request workflow; direct pushes to protected `main` were rejected and not forced.
