# Stronk Runtime Paths And Subagent Contract Logs

## Progress

- [x] ExecPlan workspace created.
- [x] Initial distribution context gathered.
- [x] Installed intercom package inspected for `~/.pi` behavior.
- [x] Local `stronk-pi-subagents` references inspected.
- [x] Local `pi-mono` searched for `pi-intercom`.
- [x] Session `019f0eb2-302f-7486-bf0d-0e9837189648` inspected for JSON bloat evidence.
- [x] Initial plan drafted.
- [x] Read-only swarm vetting pass completed with five roles.
- [x] Swarm findings folded into the plan.
- [x] Second-pass swarm review completed.
- [x] Decision Gate 0 closed.
- [x] Decision Gate 1 closed.
- [x] Implementation started.
- [x] Local intercom fork implementation verified.
- [x] Local subagents state-root and bridge implementation verified.
- [x] Local plugin compact facade implementation verified.
- [x] Local distribution three-artifact implementation verified with fixture artifacts.
- [x] Stronk-owned repos pushed, reviewed, merged, released, and artifact provenance verified.
- [x] Released artifacts imported into `stronk-pi` distribution `0.2.3`.
- [x] Active live Stronk Pi runtime refreshed from the released distribution.
- [x] Live tmux Stronk Pi proof run completed with `kimi-coding/kimi-for-coding:xhigh`.
- [x] No new real-home `~/.pi` writes observed during temp-root smoke or live proof.
- [x] ExecPlan completed.

## Session History

### 2026-06-29

- Created `docs/exec-plans/active/stronk-runtime-paths-and-subagent-contract/`.
- Gathered local context from distribution files, sibling repos, installed packages, and session artifacts.
- Verified that distribution currently pins `stronk-pi-plugin` and `stronk-pi-subagents` artifacts, while `pi-intercom@0.6.0` is configured as a runtime package outside the immutable artifact identity checks.
- Verified that installed `pi-intercom@0.6.0` has hardcoded `~/.pi/agent/intercom` path defaults.
- Verified that `stronk-pi-subagents` has remaining `.pi` and intercom references.
- Verified that local `pi-mono` did not expose `pi-intercom` in the searched files.
- Inspected session `019f0eb2-302f-7486-bf0d-0e9837189648` and confirmed runtime JSON bloat from lifecycle action payloads, plus prompt-side bloat from embedded skill text.
- Ran a read-only swarm review with critic, architect, security, QA, and technical-research roles.
- Accepted the swarm verdict as `READY-WITH-FIXES`, not final execution-ready, and updated the plan to make Phase 0 executable while blocking implementation phases behind Decision Gates 0 and 1.
- Ran a second-pass read-only swarm review against the revised `PLAN.md` and `LOGS.md`.
- All five reviewers returned `READY-FOR-PHASE-0`.
- The plan is now execution-ready for Phase 0 gate closure work, while implementation remains intentionally blocked until Decision Gate 0 and Decision Gate 1 are closed.
- Closed Decision Gate 0 and Decision Gate 1 from npm registry metadata, GitHub source evidence, local repo inspection, and current facade code inspection.
- Downloaded `pi-intercom@0.6.0` only to `/tmp/stronk-pi-intercom-phase0/` for hashing and inventory.
- Confirmed the downloaded package is older than 14 days relative to 2026-06-29 and did not execute package code.
- Prepared the Phase 0 checkpoint for independent review before starting implementation.
- Act-review-loop checkpoint `phase-0-gates` first review returned `revise`.
- Reviewer accepted the gate evidence but found stale closed-gate items still listed under `PLAN.md` Open Questions and a Phase 3 checklist item that still said to decide post-close output behavior.
- Reconciled `PLAN.md` so closed Phase 0 decisions are no longer open questions and Phase 3 now implements the chosen persistent ledger/output handle behavior.
- Act-review-loop checkpoint `phase-0-gates` re-review returned `accept`.
- Phase 1 implementation is unblocked.
- Prepared local `stronk-pi-intercom` worktree from the approved npm tarball seed and preserved Stronk package identity, state-root path policy, and release metadata.
- Implemented `stronk-pi-subagents` hard cutover to `stronk-pi-intercom` paths under `STRONK_PI_STATE_ROOT || STRONKPI_STATE_ROOT || ~/.stronk-pi`.
- Implemented compact `stronk_subagent` lifecycle JSON and bounded durable `read_output` behavior in `stronk-pi-plugin`, requiring plugin version `0.2.3`.
- Implemented distribution-side first-class `stronk-pi-intercom` artifact identity, provenance checks, required archive/runtime member checks, generic artifact importer, and three-artifact fixtures.
- Act-review-loop checkpoint `CP-SUBAGENTS-PLUGIN-CONTRACT` first review returned `revise` for a lookalike intercom path allowlist issue and a missing `node:os` import; both were fixed.
- Act-review-loop checkpoint `CP-SUBAGENTS-PLUGIN-CONTRACT` re-review returned `accept`.
- Act-review-loop checkpoint `CP-INTERCOM-FORK` returned `accept`.
- Act-review-loop checkpoint `CP-DISTRIBUTION-THREE-ARTIFACT` first review returned `revise` because `AGENTS.md` did not explicitly name `nicobailon/pi-intercom` and `EYYCHEEV/stronk-pi-intercom`.
- Updated `AGENTS.md` upstream boundary policy to block original intercom upstream activity and allow the Stronk-owned intercom repo.
- Act-review-loop checkpoint `CP-DISTRIBUTION-THREE-ARTIFACT` re-review returned `accept`.
- Local package and distribution verification passed for the pre-release implementation.
- Released all changed Stronk-owned repos and verified artifact digests and attestations.
- Imported released plugin, subagents, and intercom artifacts into the distribution and released `stronk-pi-v0.2.3`.
- Refreshed the active live runtime under `~/.stronk-pi` after explicit same-turn operator confirmation.
- Ran a live tmux Stronk Pi proof with the configured Kimi coding model.
- The proof executed `stronk_subagent` `spawn`, `wait_all`, bounded `read_output`, and `close_all`.
- Post-proof diagnose confirmed `subagentRuntime.enabled=true`, adapter `intercom`, bridge path `~/.stronk-pi/agent/extensions/stronk-pi-intercom`, and packages `stronk-pi-subagents@0.22.0-stronk.5` plus `stronk-pi-intercom@0.6.0-stronk.1`.
- Real-home `~/.pi` canary found zero new writes during the live proof.

## Swarm Vetting Summary

FORK_CONTEXT_USED: false.

Reason: the global subagent policy requires context forks off unless explicitly requested.

Roles:

- Critic: found that plugin facade changes need a first-class release/import gate, and that implementation phases must be blocked until the decision gates are recorded.
- Architect: found that fork provenance, third-artifact distribution support, and bridge compatibility mode needed concrete decisions before implementation.
- Security reviewer: found that remote-name indirection and source provenance need explicit guards before sibling repo public activity.
- QA tester: found missing three-artifact manifest tests, missing intercom importer details, and underspecified temp-root runtime smoke coverage.
- Technical researcher: confirmed most gathered facts and corrected two interpretations:
  - the final `children.json` snapshot is post-cleanup evidence, not proof that async refresh alone stripped output handles.
  - current `stronk-agents` guidance already treats `wait_all` as a barrier and bounded `read_output` as fallback; the bloat comes from full skill text plus oversized facade responses.

Second-pass result:

- Critic: `READY-FOR-PHASE-0`.
- Architect: `READY-FOR-PHASE-0`.
- Security reviewer: `READY-FOR-PHASE-0`.
- QA tester: `READY-FOR-PHASE-0`.
- Technical researcher: `READY-FOR-PHASE-0`.

## Decisions

- The active plan was execution-ready for Phase 0 only until Decision Gate 0 and Decision Gate 1 were closed.
- The live installed `~/.stronk-pi` copy of `pi-intercom` is evidence only and must not be used as fork seed.
- Intercom must become a first-class artifact in the distribution trust model, not only a package string in defaults.
- Plugin changes are conditional, but if the facade implementation changes plugin code, a new immutable `stronk-pi-plugin` artifact is required.
- Public sibling-repo activity requires a same-turn operator confirmation and a remote ownership preflight proving targets are Stronk-owned.
- Active plan text should prefer `~/.stronk-pi` aliases over full real-home paths where possible.
- Decision Gate 0 is closed with `pi-intercom@0.6.0` npm tarball as the approved fork seed and `nicobailon/pi-intercom` commit `5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457` as the authoritative upstream source.
- The Stronk fork must not be seeded from the live installed `~/.stronk-pi` package copy.
- The transition mode is hard cutover to `stronk-pi-intercom`.
- A one-release `pi-intercom` alias is rejected because it preserves the legacy package identity in the new first-class artifact trust model and would weaken guard tests that must reject legacy-only manifests.
- Older sessions or configs that require `pi-intercom` should fail closed with recovery guidance to refresh the Stronk Pi runtime.
- Decision Gate 1 is closed with compact lifecycle results by default, bounded explicit output reads, persistent post-close ledger pointers, and a required `stronk-pi-plugin` version bump.
- `read_output` remains the explicit detailed-read API.
- No new `read_artifact` action is required for this release.
- Post-close output access must survive through an opaque ledger handle or child ledger pointer; `close` and `close_all` must not destroy the only supported detailed-read path.
- Compact lifecycle responses must be redacted before truncation and must avoid absolute local paths unless debug mode is explicitly enabled.

## Field Notes

### Decision Gate 0: Intercom Fork And Path Policy

Status: closed on 2026-06-29.

Authoritative upstream:

- Original upstream repository: `https://github.com/nicobailon/pi-intercom`.
- Upstream tag: `v0.6.0`.
- Upstream commit: `5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457`.
- `git ls-remote` confirmed `refs/heads/main` and `refs/tags/v0.6.0` both point at `5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457`.
- Pi package catalog URL: `https://pi.dev/packages/pi-intercom`.
- GitHub source URL: `https://github.com/nicobailon/pi-intercom/tree/5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457`.

Approved fork seed:

- Seed type: npm tarball.
- Package: `pi-intercom@0.6.0`.
- Published: `2026-05-03T07:05:18.221Z`.
- Registry tarball: `https://registry.npmjs.org/pi-intercom/-/pi-intercom-0.6.0.tgz`.
- Registry integrity: `sha512-OFPh/DXfPhUUSDLTRJiFPEvw00fOA/spjsxUcXiuCHvb2ZkRL02G8Q91mTd+3d42A9AK8BSmbD0+8imFPuHGoQ==`.
- Registry shasum: `7c19f6acd53a5c7a3e5a04f3dc1f7156d2376dd5`.
- Computed tarball SHA256: `76c0d5284661aac437248bb6c7a32879fe863296bd15cb533751b27cafc44818`.
- GitHub codeload source archive: `https://codeload.github.com/nicobailon/pi-intercom/tar.gz/5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457`.
- Computed source archive SHA256: `3ce238f4a75ce9c66ad76766ee878ef19dd83eef620739b73fe08e35c84311c6`.
- Package code was not executed.
- Live installed `~/.stronk-pi` package files were inspected only as behavior evidence and were not used as the fork seed.

Npm package file list:

- `package/LICENSE`
- `package/package.json`
- `package/README.md`
- `package/skills/pi-intercom/SKILL.md`
- `package/broker/broker.ts`
- `package/broker/client.ts`
- `package/ui/compose.ts`
- `package/config.ts`
- `package/broker/framing.ts`
- `package/index.ts`
- `package/ui/inline-message.ts`
- `package/broker/paths.test.ts`
- `package/broker/paths.ts`
- `package/reply-tracker.ts`
- `package/ui/session-list.ts`
- `package/broker/spawn.test.ts`
- `package/broker/spawn.ts`
- `package/types.ts`

Required Stronk intercom archive/runtime members:

- `package/package.json`
- `package/index.ts`
- `package/config.ts`
- `package/types.ts`
- `package/reply-tracker.ts`
- `package/broker/broker.ts`
- `package/broker/client.ts`
- `package/broker/framing.ts`
- `package/broker/paths.ts`
- `package/broker/spawn.ts`
- `package/ui/compose.ts`
- `package/ui/inline-message.ts`
- `package/ui/session-list.ts`
- `package/skills/stronk-pi-intercom/SKILL.md`

Package identity and bridge mode:

- Target package name: `stronk-pi-intercom`.
- Target repository: `EYYCHEEV/stronk-pi-intercom`.
- Target version convention: `0.6.0-stronk.1` for the first Stronk-owned fork artifact.
- Transition mode: hard cutover.
- Distribution bridge path: `~/.stronk-pi/agent/extensions/stronk-pi-intercom`.
- Runtime environment bridge variable: `STRONK_PI_INTERCOM_BRIDGE`.
- The guard must reject manifests that provide only legacy `pi-intercom` for Stronk-managed intercom runtime.
- The guard must reject intercom artifacts whose `name`, `sourceRepo`, `immutableTag`, `attestation`, digest, source commit, seed metadata, or required members do not match the Stronk-owned contract.
- `nicobailon/pi-intercom` is added to the blocked-upstream design together with `earendil-works/pi`, `badlogic/pi-mono`, and `nicobailon/pi-subagents`.

State-root policy:

- `STRONKPI_STATE_ROOT` and `STRONK_PI_STATE_ROOT` select the Stronk state root.
- `STRONK_PI_STATE_ROOT` remains the canonical environment variable for child runtime code when both are present.
- Intercom config, sockets, locks, logs, broker PID files, and Windows launcher helpers must live under `<state-root>/agent/intercom`.
- The default state root is `~/.stronk-pi`.
- No Stronk-managed runtime path may fall back to real-home `~/.pi` when either Stronk state-root variable is present.
- Project-local `.pi` directories are allowed only for project config, fixture, skill, agent, MCP, or settings discovery and must be resolved from the project root or a temp test root.
- Real-home `~/.pi` access is allowed only for explicit dry-run or migration/cleanup diagnostics and must not create files without a separate apply gate.

Remote ownership preflight checklist:

- Run `git remote -v` from the target repo immediately before any push, tag, release, or PR command.
- Verify every push target is under `https://github.com/EYYCHEEV/`.
- Verify any upstream remote is fetch-only or has push disabled.
- Run `gh repo view EYYCHEEV/<repo> --json owner,name,isPrivate,url` before GitHub release or workflow dispatch.
- Record the command output summary in this log before the public action.
- Stop before any target matching `earendil-works/pi`, `badlogic/pi-mono`, `nicobailon/pi-subagents`, `nicobailon/pi-intercom`, or another non-Stronk upstream unless the user gives an exact same-turn override naming the upstream repo, action, and command.

### `.pi` Reference Classification

Distribution repo:

| Area | References | Classification | Required action |
| --- | --- | --- | --- |
| `config/defaults.toml` | `intercom_bridge`, `package_pins.intercom` | Stronk runtime config currently naming legacy package | Rename to `stronk-pi-intercom` and Stronk bridge path |
| `roles/stronk/roles.toml` | `"pi-intercom"` extension | Stronk runtime role package currently naming legacy package | Rename to `stronk-pi-intercom` |
| `lib/stronk-pi-guard.py` | package pins, `state_intercom_bridge_path`, bridge env, status fields | Stronk runtime code | Convert to first-class intercom artifact and Stronk package identity |
| `lib/stronk-pi-guard.py` | `.pi/mcp.json`, `.pi/web-search.json`, `.pi/cache`, `.pi/logs`, `.pi/tmp` | Project-local Pi compatibility paths | Preserve as project-local/bypass policy, not real-home writes |
| `tests/run_offline.sh`, `tests/test_install_dry_run.sh` | no `$HOME/.pi` assertions | Real-home write regression checks | Preserve and extend |
| `tests/test_manifest_verifier.py` | legacy `pi-intercom` bridge assertions and legacy `.pi/web-search.json` cleanup tests | Mixed runtime and migration tests | Update bridge assertions, preserve cleanup tests |
| `tests/test_mcp_doctor.py` | runtime package fixtures and `.pi` project fixtures | Mixed runtime and project-local fixtures | Update runtime package identity, preserve project-local fixtures |
| `tests/test_public_surface.py`, `tests/test_plugin_state_root.py` | forbidden real-home path canaries | Security regression checks | Preserve and extend to intercom |
| `tests/fixtures/manifests/*.json` | `packagePins.intercom.name = "pi-intercom"` | Deterministic manifest fixtures | Regenerate for three-artifact Stronk intercom contract |

Subagents repo:

| Area | References | Classification | Required action |
| --- | --- | --- | --- |
| `src/intercom/intercom-bridge.ts` | default extension dir, config path, subagent config dir, availability checks | Stronk runtime code with legacy defaults | Resolve through Stronk state root and `stronk-pi-intercom`; reject or diagnose legacy-only runtime |
| `install.mjs` | install target under `~/.pi/agent/extensions/subagent` | Upstream standalone install behavior | Keep only if explicitly documented as non-Stronk standalone; Stronk runtime must not use it |
| `src/runs/shared/run-history.ts` | run history under `~/.pi/agent/run-history.jsonl` | Runtime state path | Move to Stronk state root |
| `src/extension/index.ts` | config path and session examples under `~/.pi` | Runtime config and docs comments | Move runtime code to Stronk state root; update comments |
| `src/shared/artifacts.ts` | sessions base under `~/.pi/agent/sessions` | Runtime artifact path | Move to Stronk state root or parent session root |
| `src/agents/user-agent-dir.ts` | user agent dir under `~/.pi/agent` | Runtime agent discovery fallback | Prefer `PI_CODING_AGENT_DIR`, `TAU_CODING_AGENT_DIR`, then Stronk state root; legacy fallback only outside Stronk |
| `README.md`, `CHANGELOG.md` | `~/.pi` and `.pi` references | Documentation/history | Update current Stronk sections and preserve historical changelog entries |
| `test/unit/*`, `test/integration/*` | temp-home `.pi`, project `.pi`, and fixture paths | Test fixtures | Preserve project/temp fixtures; add real-home no-write checks |
| `test/integration/intercom-result-delivery.test.ts` | writes under `os.homedir()/.pi` | Test fixture that can hide real-home behavior | Convert to isolated Stronk state-root fixture |
| `src/agents/*`, manager UI, skills fallback | project `.pi` settings, agents, skills | Project-local compatibility paths | Preserve project-local `.pi` discovery and collision rules |

Plugin repo:

| Area | References | Classification | Required action |
| --- | --- | --- | --- |
| `src/subagents/ledger.mjs` | `~/.stronk-pi` state root | Correct Stronk state path | Preserve; add `STRONKPI_STATE_ROOT` parity if missing |
| `src/index.mjs` | `~/.stronk-pi` state root | Correct Stronk state path | Preserve |
| `src/subagents/facade.mjs`, `schema.mjs`, tests | `stronk_subagent` lifecycle and read behavior | Compact facade implementation surface | Change lifecycle payloads to compact summaries |
| `src/subagents/adapters/pi-subagents-bridge.mjs` | 8192-byte terminal preview | Lifecycle bloat source | Reduce lifecycle inline preview budget and push detail to ledger |
| `scripts/security-check.mjs` | forbidden `pi-core dot-pi agent` regex | Security canary | Preserve and extend as needed |
| `README.md` | current `stronk_subagent` guidance | Agent-facing contract docs | Update for compact lifecycle and durable bounded reads |
| `test/*.mjs`, `scripts/installed-artifact-smoke.mjs` | temp `STRONK_PI_STATE_ROOT` paths | Test fixtures | Preserve and extend with byte budgets, bounded reads, and redaction canaries |

Intercom seed:

| Area | References | Classification | Required action |
| --- | --- | --- | --- |
| `package/config.ts` | `~/.pi/agent/intercom/config.json` | Runtime config path | Move to Stronk state root |
| `package/broker/paths.ts` | Unix socket under `~/.pi/agent/intercom/broker.sock` | Runtime socket path | Move to Stronk state root |
| `package/broker/spawn.ts` | broker PID, lock, launcher helper under `~/.pi/agent/intercom` | Runtime state paths | Move to Stronk state root |
| `package/broker/broker.ts` | broker PID and directory under `~/.pi/agent/intercom` | Runtime state paths | Move to Stronk state root |
| `package/README.md` | install and runtime file docs under `~/.pi` | Documentation | Rewrite for Stronk package identity and state root |
| `package/skills/pi-intercom/SKILL.md` | skill identity and guidance | Agent guidance | Rename to `stronk-pi-intercom` or update text to Stronk identity |
| `package/broker/*.test.ts` | temp dirs named `pi-intercom-*` and pipe prefix | Test fixture / IPC naming | Keep temp naming if harmless; update package-facing assertions if needed |

### Decision Gate 1: Compact Facade Contract

Status: closed on 2026-06-29.

Lifecycle response envelope:

- Every lifecycle action returns `{ ok, action, requestId, schemaVersion, facadeRunId, status, counts, childIds, ledger, warnings, errors }`.
- `requestId` is generated per call unless supplied internally by the runtime.
- `schemaVersion` starts at `2` for the compact facade contract.
- `ledger` is an object with opaque identifiers, not absolute file paths.
- `ledger` includes `facadeRunId`, `projectRef`, and optional `childOutputHandle` or `childOutputHandles` when detailed output exists.
- `counts` includes only numeric status counts and aggregate failure/retry counts.
- Default lifecycle responses do not include full child records.
- Default lifecycle responses do not include `cwd`, upstream temp paths, durable output paths, raw prompts, full child output, or multi-kilobyte previews.
- A lifecycle call may include `preview` only when explicitly supported and must keep the entire JSON response within the lifecycle byte budget.

Action schemas:

- `spawn`: returns `childId`, `roleRequested`, `roleUsed`, `aliasResolved`, `status`, `isTerminal`, `recommendedNextAction`, `ledger`, and compact warnings.
- `list`: returns `childIds`, `counts`, `statusByChildId`, `ledger`, and no child records by default.
- `status`: returns `childId`, `status`, `isTerminal`, `failureClass`, `retryable`, `recommendedNextAction`, `ledger`, and output handle metadata if present.
- `wait`: returns the same compact child summary as `status`, plus `timedOut`, `elapsedMs`, and `timeoutMs`.
- `wait_all`: returns `childIds`, `terminalChildIds`, `nonTerminalChildIds`, `failedChildIds`, `retryableCapacityChildIds`, `counts`, `timedOut`, `elapsedMs`, `timeoutMs`, `retryPolicy`, `nextRetryAfterMs`, `recommendedNextAction`, and `ledger`.
- `send_input`: returns `childId`, `status`, `inputAccepted`, `inputLinkedChildId`, `recommendedNextAction`, and `ledger`.
- `revive`: returns `previousChildId`, `childId`, `roleRequested`, `roleUsed`, `status`, `recommendedNextAction`, and `ledger`.
- `interrupt`: returns `childId`, `status`, `isTerminal`, `processLive`, `recommendedNextAction`, and `ledger`.
- `close`: returns `childId`, `status`, `cleanupState`, `cleanupVerified`, `processLive`, `closeError` if redacted, and `ledger`.
- `close_all`: returns `childIds`, `closedChildIds`, `failedCloseChildIds`, `cleanupVerifiedChildIds`, `cleanupFailedChildIds`, `counts`, `timedOut`, `elapsedMs`, `timeoutMs`, `recommendedNextAction`, and `ledger`.

Byte budgets:

- Default lifecycle response budget: 2048 UTF-8 bytes per tool result.
- Hard lifecycle response ceiling: 4096 UTF-8 bytes per tool result.
- Inline lifecycle preview default: 0 bytes.
- Inline lifecycle preview maximum when explicitly enabled by runtime code: 512 UTF-8 bytes total per tool result.
- `read_output` default `maxChars`: 6000.
- `read_output` maximum `maxChars`: 24000.
- Stored sanitized output artifact cap: 1 MiB.
- Tests must fail if compact lifecycle JSON exceeds the default budget for representative `spawn`, `list`, `status`, `wait`, `wait_all`, `close`, and `close_all` flows.

Explicit read behavior:

- `read_output` remains the detailed read API.
- `read_output` returns `{ ok, action: "read_output", requestId, schemaVersion, output }`.
- `output` includes `handle`, `childId`, `artifactKind`, `chunk`, `offset`, `nextOffset`, `totalChars`, `eof`, `artifactTruncated`, `redacted`, `bytes`, and `hash`.
- `artifactKind` values are `findings`, `failure-summary`, `terminal-summary`, `diagnostic`, or `none`.
- `read_output` chunks are sanitized, bounded, and UTF-8 safe.
- `read_output` must never reveal durable output file paths.
- Output handles remain opaque and must be validated against the current facade ledger.
- Post-close reads are supported through durable ledger/output handles.
- `close` and `close_all` may mark cleanup state but must not delete the only readable detailed-output artifact for terminal children.

Redaction canaries:

- Secret-like values: OpenAI-style `sk-...`, GitHub `ghp_...`, AWS `AKIA...`, Slack `xox...`, Bearer tokens, private keys, and key/password/token/secret assignments.
- Environment values: strings with key names containing `KEY`, `TOKEN`, `SECRET`, or `PASSWORD`.
- Absolute paths: `<macos-home>/...`, `/home/...`, `/tmp/...`, `/private/tmp/...`, `/var/folders/...`, `/root/...`, `/etc/...`, `file:///...`, and `.ssh` paths.
- Prompt text: raw task prompts and inherited prompt bodies must not appear in lifecycle summaries.
- Ledger reads may include sanitized findings chunks, but not raw secret values or private filesystem paths.

Compatibility behavior:

- Older callers that expected full child records receive compact summaries only.
- The supported migration path is to call `read_output` with the returned opaque handle when detailed findings are needed.
- Raw upstream `subagent` and unbounded output options remain denied.
- Provider-capacity and failure-summary artifacts are not synthesis material unless explicitly inspected and accepted by the caller.
- A plugin change is required because current code returns `ledger.publicChild(child)` records and 8192-byte previews from lifecycle actions.
- The next plugin version target is `0.2.3`.

Distribution files inspected:

- `manifests/current.json`
- `config/defaults.toml`
- `roles/stronk/roles.toml`
- `lib/stronk-pi-guard.py`
- `scripts/import-plugin-release.py`
- `tests/test_manifest_verifier.py`

Installed package evidence:

- `~/.stronk-pi/artifacts/packages/pi-intercom@0.6.0/package/index.ts`
- `~/.stronk-pi/artifacts/packages/pi-intercom@0.6.0/package/config.ts`
- `~/.stronk-pi/artifacts/packages/pi-intercom@0.6.0/package/broker/paths.ts`
- `~/.stronk-pi/artifacts/packages/pi-intercom@0.6.0/package/broker/spawn.ts`
- `~/.stronk-pi/artifacts/packages/pi-intercom@0.6.0/package/broker/broker.ts`

Subagents evidence:

- Local `stronk-pi-subagents` contains `.pi`, `pi-intercom`, and intercom bridge references that need classification.

Plugin/facade evidence:

- `TERMINAL_RESULT_BYTES` currently defaults to `8192`.
- `read_output` currently defaults to `12000` characters.
- Public child record caps currently use `MAX_CHILDREN = 6`.
- `clearChildOutput` can clear handles while retaining preview fields.
- `read_output` does not yet expose `artifactKind`.

Session evidence:

- Session id: `019f0eb2-302f-7486-bf0d-0e9837189648`.
- The session file embeds the full `stronk-agents` skill instructions.
- Lifecycle responses include large public child records and output previews.
- Final cleanup state has null handles, which is consistent with output cleanup and not enough by itself to prove async refresh causality.

## Blockers

- No Phase 0 blocker remains.
- Implementation is allowed to start after the Phase 0 act-review-loop checkpoint returns `accept`.
- Distribution import tooling still handles plugin artifacts only, so Phase 5 must add generic or intercom-specific import support.
- Guard/tests currently know two artifact identities, so Phase 5 must add three-artifact manifest support.
- Sibling repo public activity remains blocked until same-turn remote ownership preflight proves every push, tag, workflow dispatch, or release target is Stronk-owned.

## Verification Notes

### Act-Review-Loop Checkpoints

#### phase-0-gates

- `checkpoint_id`: `phase-0-gates`
- `checkpoint_title`: `Phase 0 gate closure`
- `plan_version`: `PLAN.md` active workspace revision after Phase 0 reconciliation
- `acceptance_criteria`: Decision Gate 0 and Decision Gate 1 closed with provenance, `.pi` classification, bridge mode, compact schema, budgets, redaction, plugin release requirement, and no implementation started.
- `action_taken`: Updated `LOGS.md` with gate evidence and decisions; reconciled `PLAN.md` Phase 0 checklist; after review, removed stale open questions and reworded post-close output access item.
- `gate_mode`: `blocking`
- `independence_mode`: `independent`
- `role_requested`: `critic`
- `role_used`: `critic`
- `fallback_used`: `false`
- `reviewer_role`: `critic`
- `status`: `done`
- `verdict`: `accept`
- `retry_count`: `1`
- `key_findings`: First review found stale closed-gate decisions still listed as open questions and a Phase 3 item that still said to decide post-close behavior.
- `strongest_evidence`: Re-review confirmed `LOGS.md` closes both gates with provenance and compact contract details, `PLAN.md` has no stale gate questions, Phase 3 implements persistent ledger/output handles, and implementation remains unstarted.
- `next_action`: Start Phase 1 intercom fork preparation and implementation.
- `blocker`: ``
- `decision_owner`: ``
- `resume_trigger`: ``

Read-only checks completed:

- Confirmed `scripts/import-plugin-release.py` is plugin-specific.
- Confirmed `lib/stronk-pi-guard.py` has artifact identity checks for plugin and subagents, but not intercom.
- Confirmed `lib/stronk-pi-guard.py` exports `STRONK_PI_INTERCOM_BRIDGE` and reports intercom bridge status fields.
- Confirmed `tests/test_manifest_verifier.py` asserts the current `pi-intercom` bridge path.
- Confirmed local `stronk-pi-intercom` worktree is absent.
- Confirmed no committed `scripts-or-oneoff/session_size_probe.py` helper exists.

No git operations were run for this plan update.

No upstream public activity was created.

At this checkpoint, no live `~/.stronk-pi` update had been run.

#### CP-SUBAGENTS-PLUGIN-CONTRACT

- `checkpoint_id`: `CP-SUBAGENTS-PLUGIN-CONTRACT`
- `checkpoint_title`: `Subagents state-root and plugin compact contract`
- `status`: `done`
- `verdict`: `accept`
- `retry_count`: `1`
- `key_findings`: First review found that the intercom bridge allowlist accepted lookalike paths such as `/tmp/stronk-pi-intercom/index.ts`, and one state-root helper was missing a `node:os` import.
- `action_taken`: Tightened the bridge allowlist to bare `stronk-pi-intercom`, the exact configured extension directory, or subpaths under that exact directory; added the missing import and regression coverage.
- `strongest_evidence`: Re-review accepted the subagents Stronk state-root cutover, legacy bridge rejection, compact lifecycle JSON, bounded read contract, post-close output handles, byte budget tests, and redaction canaries.
- `blocker`: ``

#### CP-INTERCOM-FORK

- `checkpoint_id`: `CP-INTERCOM-FORK`
- `checkpoint_title`: `Stronk-owned intercom fork implementation`
- `status`: `done`
- `verdict`: `accept`
- `retry_count`: `0`
- `key_findings`: No blocking findings.
- `strongest_evidence`: Review accepted package identity `stronk-pi-intercom@0.6.0-stronk.1`, Stronk state-root resolution, socket/config/lock/PID/helper paths under the Stronk state root, release workflow metadata, required package files, and no real-home `.pi` runtime writes.
- `blocker`: ``

#### CP-DISTRIBUTION-THREE-ARTIFACT

- `checkpoint_id`: `CP-DISTRIBUTION-THREE-ARTIFACT`
- `checkpoint_title`: `Distribution three-artifact guard and import support`
- `status`: `done`
- `verdict`: `accept`
- `retry_count`: `1`
- `key_findings`: First review found the repo upstream boundary text did not explicitly include `nicobailon/pi-intercom` or the new `EYYCHEEV/stronk-pi-intercom` target.
- `action_taken`: Updated `AGENTS.md` to block original intercom upstream public activity, add `nicobailon/pi-intercom` to blocked upstream targets, and add `EYYCHEEV/stronk-pi-intercom` to Stronk-owned targets.
- `strongest_evidence`: Re-review accepted guard identity/provenance checks, three-artifact manifest validation, Stronk defaults/roles, generic artifact import tooling, and negative tests for wrong intercom source/metadata/member cases.
- `residual_risk`: `manifests/current.json` still contains old live release data until real released artifacts are imported.
- `blocker`: ``

### Pre-Release Local Verification

All commands used zsh from the named local worktree unless noted.

Intercom worktree `../stronk-pi-intercom`:

- `npm ci --ignore-scripts` passed.
- `npm test` passed 40 tests.
- `npm audit --json` reported zero vulnerabilities.
- `npm pack --dry-run --json` produced `stronk-pi-intercom-0.6.0-stronk.1.tgz`, 19 entries, shasum `287069e742ae4791f2869bb2b57145ed5169caa0`, integrity `sha512-xYLR8TeXNlw+cbRsL5in7gEodRosuOjNbSK0R2gRrhtOPPoSPxtNyhFQ4zenKwCg3lb5+QfSxO7GAOv60uE5Aw==`.
- `git diff --check` passed.

Subagents worktree `../stronk-pi-subagents`:

- `npm ci --ignore-scripts` passed.
- `npm run test:all` passed 386 unit tests and 324 integration tests.
- `npm pack --dry-run --json` produced `stronk-pi-subagents-0.22.0-stronk.5.tgz`, 92 entries, shasum `e25f60c18975a484d59637493ce9c027c879a3ef`, integrity `sha512-cI0X2lkrIHGieZ2GTUUmpDsKAtM4Aj1SHQgY2975lbTsL07k4Yw4+lZ8RmxNMvcfc8+FLzADE8Bdg28cPWeDkg==`.
- `git diff --check` passed.
- `npm audit` still reports existing dev dependency advisories in the inherited lockfile; no dependency versions were changed in this plan.

Plugin worktree `../stronk-pi-plugin`:

- `npm ci --ignore-scripts` passed.
- Initial full `npm run check` hit three image-preflight timeouts; focused reruns passed and a second full `npm run check` passed 250 tests plus `security-check: ok`.
- `npm pack --dry-run --json` produced `stronk-pi-plugin-0.2.3.tgz`, 10 entries, shasum `23561d3e034fb2fe1667fad9aa736dc77dcf7f0c`, integrity `sha512-UN/hT4qKxU9tBpBJ74ML8LWOC+fFR5TlKaFfcCZ6n4V9Q03VSl9zS1XZ71h9bfJOwfNCzQBy1zL2AJ7epnQxsA==`.
- `git diff --check` passed.

Distribution worktree `.`:

- `python3 -m py_compile lib/stronk-pi-guard.py scripts/*.py tests/*.py` passed.
- `python3 tests/make_fixtures.py` passed.
- `python3 -m unittest tests.test_manifest_verifier tests.test_mcp_doctor tests.test_release_scripts` passed 85 tests.
- `STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh` passed 109 tests with 2 skipped and verified three fixture artifacts.
- `env -i PATH="$PATH" HOME="$PWD/.tmp-scrubbed-home" TMPDIR="${TMPDIR:-/tmp}" STRONKPI_NO_NETWORK=1 zsh -f -c 'mkdir -p "$HOME"; python3 -m unittest discover -s tests -p "test_*.py"'` passed 109 tests with 2 skipped.
- Temporary scrubbed home `.tmp-scrubbed-home` was removed after the test.
- `git diff --check` passed.

### Local Package Commits

- `../stronk-pi-intercom`: `d4de2fd feat: add Stronk intercom fork`.
- `../stronk-pi-subagents`: `8bda075 feat: use Stronk state paths and intercom`.
- `../stronk-pi-plugin`: `b4bd8c5 feat: compact Stronk subagent lifecycle output`.
- `.`: `678cd87 feat: verify Stronk intercom artifact`.

### Remote Ownership Preflight

Public actions below were run only after Stronk-owned remote ownership preflight and operator confirmation.
No public activity was created in original upstream Pi, Pi subagent, or intercom repositories.

`../stronk-pi-intercom`:

- `git remote -v` shows `origin https://github.com/EYYCHEEV/stronk-pi-intercom.git` for fetch and push.
- `git status --short --branch` shows local branch `main` with commit `d4de2fd`.
- `gh repo view EYYCHEEV/stronk-pi-intercom --json owner,name,isPrivate,url` failed because the Stronk-owned repository does not exist yet.
- Attempted command `gh repo create EYYCHEEV/stronk-pi-intercom --public --description 'Stronk Pi fork of pi-intercom with Stronk-managed runtime state paths' --clone=false` was blocked by the local safety hook because public repository creation requires explicit confirmation.
- The operator ran the blocked creation command successfully outside Codex and created `https://github.com/EYYCHEEV/stronk-pi-intercom`.
- Fresh preflight after creation confirmed owner `EYYCHEEV`, public repo, URL `https://github.com/EYYCHEEV/stronk-pi-intercom`, default branch `main`.
- `git push -u origin main` pushed `d4de2fd` to `EYYCHEEV/stronk-pi-intercom`.
- Release workflow `release-artifact.yml` run `28343541533` completed successfully.
- Release URL: `https://github.com/EYYCHEEV/stronk-pi-intercom/releases/tag/stronk-pi-intercom-v0.6.0-stronk.1`.
- Release target: `d4de2fd4ffe853260b013e53632bac4175dbad69`.
- Artifact: `stronk-pi-intercom-0.6.0-stronk.1.tgz`.
- Artifact SHA256: `d2b632ae73e4ef56896e72b17074be19653a1cbe44ca231c03764b5526cab4be`.
- Downloaded release asset digest matched `SHA256SUMS.txt`.
- `gh attestation verify` for the downloaded intercom artifact returned success.

`../stronk-pi-subagents`:

- `git remote -v` shows `origin https://github.com/EYYCHEEV/stronk-pi-subagents.git` for fetch and push.
- `git remote -v` shows `upstream https://github.com/nicobailon/pi-subagents.git` for fetch and `upstream DISABLED` for push.
- `gh repo view EYYCHEEV/stronk-pi-subagents --json owner,name,isPrivate,url` returned owner `EYYCHEEV`, repo `stronk-pi-subagents`, public, URL `https://github.com/EYYCHEEV/stronk-pi-subagents`.
- Local branch `stronk-pi-subagents` is ahead of `origin/stronk-pi-subagents` by 1 commit: `8bda075`.
- `git push origin stronk-pi-subagents` pushed `8bda075`.
- Release workflow `release-artifact.yml` run `28343541538` completed successfully.
- Release URL: `https://github.com/EYYCHEEV/stronk-pi-subagents/releases/tag/stronk-pi-subagents-v0.22.0-stronk.5`.
- Release target: `8bda0750b2d67da66dcdb34c3ef9b6d3e6e07365`.
- Artifact: `stronk-pi-subagents-0.22.0-stronk.5.tgz`.
- Artifact SHA256: `a8852e5bb0aaa42d0a93184f53f461b8e852e9829442c913e998ebb73307a550`.
- Downloaded release asset digest matched `SHA256SUMS.txt`.
- `gh attestation verify` for the downloaded subagents artifact returned success.

`../stronk-pi-plugin`:

- `git remote -v` shows `origin https://github.com/EYYCHEEV/stronk-pi-plugin.git` for fetch and push.
- `gh repo view EYYCHEEV/stronk-pi-plugin --json owner,name,isPrivate,url` returned owner `EYYCHEEV`, repo `stronk-pi-plugin`, public, URL `https://github.com/EYYCHEEV/stronk-pi-plugin`.
- Local branch `main` is ahead of `origin/main` by 1 commit: `b4bd8c5`.
- Direct push to protected `main` was rejected by GitHub because required checks are enforced.
- Pushed branch `release/compact-subagent-facade-0.2.3` and opened PR `https://github.com/EYYCHEEV/stronk-pi-plugin/pull/12`.
- PR checks `test` and `gitleaks` passed.
- PR `#12` was squash-merged with merge commit `d8a362ae42802c06153cfb88e6e824d6ef63eca7`.
- Release workflow `release.yml` run `28343587784` completed successfully.
- Release URL: `https://github.com/EYYCHEEV/stronk-pi-plugin/releases/tag/stronk-pi-plugin-v0.2.3`.
- Release target: `d8a362ae42802c06153cfb88e6e824d6ef63eca7`.
- Artifact: `stronk-pi-plugin-0.2.3.tgz`.
- Artifact SHA256: `3ae39a992f72af0d3e05217f50fc5318f127ea8b0aff34a2e8c2636de2a54d4d`.
- Downloaded release asset digest matched `SHA256SUMS.txt`.
- `gh attestation verify` for the downloaded plugin artifact returned success.

`EYYCHEEV/stronk-pi` distribution:

- Direct push to protected `main` was rejected by GitHub because required checks are enforced.
- Pushed branch `release/runtime-paths-intercom-artifacts` and opened PR `https://github.com/EYYCHEEV/stronk-pi/pull/19`.
- PR checks passed: Test / Offline, Security / Guardrails, Security / Manifest Verification, Security / Installer Dry Run, Compatibility / OS Matrix (Ubuntu), Compatibility / OS Matrix (macOS), Compatibility / WSL Manual Gate, and Security / Gitleaks.
- PR `#19` was squash-merged with merge commit `3ab96ed555b148a2ba1279bf0a427a85fa9fa2ba`.
- Distribution release URL: `https://github.com/EYYCHEEV/stronk-pi/releases/tag/stronk-pi-v0.2.3`.
- Distribution release target: `3ab96ed555b148a2ba1279bf0a427a85fa9fa2ba`.

### Distribution Import And Runtime Smoke

- Imported `stronk-pi-plugin-v0.2.3`, `stronk-pi-subagents-v0.22.0-stronk.5`, and `stronk-pi-intercom-v0.6.0-stronk.1` with `python3 scripts/import-artifact-release.py`.
- Bumped Stronk Pi setup/distribution version from `0.2.2` to `0.2.3` with `python3 scripts/bump-version.py 0.2.3`.
- `python3 -m py_compile lib/stronk-pi-guard.py scripts/*.py tests/*.py` passed after import.
- `python3 -m unittest tests.test_manifest_verifier tests.test_mcp_doctor tests.test_release_scripts` passed 85 tests after import.
- `STRONKPI_NO_NETWORK=1 zsh scripts/verify-release-candidate.sh` passed 109 tests with 2 skipped after import.
- Online gate `bin/stronkpi-setup update --dry-run --manifest manifests/current.json` passed and verified real public artifact hashes:
  - `stronk-pi-plugin 0.2.3 3ae39a992f72af0d3e05217f50fc5318f127ea8b0aff34a2e8c2636de2a54d4d`
  - `stronk-pi-subagents 0.22.0-stronk.5 a8852e5bb0aaa42d0a93184f53f461b8e852e9829442c913e998ebb73307a550`
  - `stronk-pi-intercom 0.6.0-stronk.1 d2b632ae73e4ef56896e72b17074be19653a1cbe44ca231c03764b5526cab4be`
- Temp-root non-dry-run smoke passed with isolated `HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `STRONKPI_STATE_ROOT`, and `STRONK_PI_STATE_ROOT`.
- Temp-root smoke installed and materialized all three released artifacts under the isolated state root, validated `stronkpi`, diagnosed `subagentRuntime.enabled=true`, and resolved `intercomBridgePath` under the isolated Stronk state root.
- Temp-root real-home write canary found no new writes under real-home `~/.pi`.

### Live Runtime Refresh

Live non-dry-run update was run only after the operator sent explicit same-turn confirmation: `CONFIRM and APPROVE`.

Command block:

```sh
backup_dir="$HOME/.stronk-pi/backups/$(date +%Y-%m-%d)"
mkdir -p "$backup_dir"
backup_file="$backup_dir/pre-stronkpi-0.2.3-$(date +%Y%m%d-%H%M%S).tgz"
tar -czf "$backup_file" -C "$HOME/.stronk-pi" config agent 2>/dev/null || true
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
bin/stronkpi-setup update --manifest manifests/current.json
bin/stronkpi --validate-only
bin/stronkpi --diagnose --json
```

Evidence:

- Backup: `~/.stronk-pi/backups/2026-06-29/pre-stronkpi-0.2.3-20260629-100159.tgz`.
- Backup SHA256: `2e20850e9eb62aca52f323077a9a102a8de8267ac3fda0e90a51a9c21207c13e`.
- Active runtime artifacts after update:
  - `~/.stronk-pi/artifacts/stronk-pi-plugin-0.2.3/package`
  - `~/.stronk-pi/artifacts/stronk-pi-subagents-0.22.0-stronk.5/package`
  - `~/.stronk-pi/artifacts/stronk-pi-intercom-0.6.0-stronk.1/package`
- `bin/stronkpi-setup validate` output captured at `/tmp/stronk-pi-live-proof-20260629-100447/setup-validate.txt`; output: `stronkpi-setup validate: ok`.
- `bin/stronkpi --validate-only` output captured at `/tmp/stronk-pi-live-proof-20260629-100447/stronkpi-validate.txt`; output included `stronkpi validate: ok`, `plugin_installed=True`, `runtime_installed=True`, `subagent_runtime_enabled=True`, and `intercom_bridge=~/.stronk-pi/agent/extensions/stronk-pi-intercom`.
- Pre-proof diagnose JSON: `/tmp/stronk-pi-live-proof-20260629-100447/diagnose.json`.
- Post-proof diagnose JSON: `/tmp/stronk-pi-live-proof-20260629-100447/diagnose-after-proof.json`.
- Post-proof diagnose summary:
  - version `0.2.3`.
  - `subagentRuntime.enabled=true`.
  - adapter `intercom`.
  - bridge `~/.stronk-pi/agent/extensions/stronk-pi-intercom`.
  - bridge target `~/.stronk-pi/artifacts/stronk-pi-intercom-0.6.0-stronk.1/package`.
  - packages: `stronk-pi-intercom@0.6.0-stronk.1` and `stronk-pi-subagents@0.22.0-stronk.5`, both installed.

### Live TMUX Proof

Dedicated tmux proof:

- Session: `stronk-pi-proof-20260629-100628`.
- Socket: `/tmp/stronk-pi-live-proof-20260629-100447/stronk-pi-proof-20260629-100628.sock`.
- Prompt: `/tmp/stronk-pi-live-proof-20260629-100447/proof-prompt.txt`.
- Runner script: `/tmp/stronk-pi-live-proof-20260629-100447/proof-run.zsh`.
- JSONL transcript: `/tmp/stronk-pi-live-proof-20260629-100447/pi-proof.jsonl`.
- Stderr: `/tmp/stronk-pi-live-proof-20260629-100447/pi-proof.stderr`.
- Parsed summary: `/tmp/stronk-pi-live-proof-20260629-100447/proof-summary.json`.
- Real-home `~/.pi` canary output: `/tmp/stronk-pi-live-proof-20260629-100447/real-home-pi-newer-than-proof-stamp.txt`.

Launch command inside tmux:

```sh
./bin/stronkpi -- --model kimi-coding/kimi-for-coding:xhigh --mode json -p "$(cat /tmp/stronk-pi-live-proof-20260629-100447/proof-prompt.txt)"
```

Proof summary:

- Provider/model: `kimi-coding` / `kimi-for-coding`.
- JSONL final event: `agent_end`.
- Stderr bytes: `0`.
- Action sequence: `spawn`, `wait_all`, `read_output`, `close_all`.
- Child id: `sp-child-c1408c97-f625-4ebb-9a13-06208f17b079`.
- Output handle: `subagent-output-f19a6183-7f21-4937-aa1b-76828d7d4d2f`.
- Compact facade result sizes:
  - `spawn`: `1504` bytes.
  - `wait_all`: `811` bytes.
  - `close_all`: `783` bytes.
- Compact budget result: pass under default `2048` bytes and hard `4096` bytes.
- Bounded `read_output` result:
  - response bytes: `1979`.
  - artifact bytes: `1186`.
  - `offset=0`, `nextOffset=1186`, `totalChars=1186`.
  - `eof=true`.
  - `artifactTruncated=false`.
  - `redacted=true`.
  - artifact hash `db8fdbdb6e017de913fb19ae82973e34c34054284ef9cc8d335d4c4b731fd7b9`.
- `close_all` cleanup:
  - closed child ids: `sp-child-c1408c97-f625-4ebb-9a13-06208f17b079`.
  - failed close ids: none.
  - cleanup verified ids: `sp-child-c1408c97-f625-4ebb-9a13-06208f17b079`.
  - cleanup failed ids: none.
  - timed out: false.
- Child review result: no findings; inspected `scripts/import-artifact-release.py`, `lib/stronk-pi-guard.py`, and `tests/test_manifest_verifier.py`, and confirmed `stronk-pi-intercom` is treated as a first-class verified runtime artifact.
- Real-home `~/.pi` write canary: `newer_count=0` after the live proof.

The wrapper script did not leave its `pi-proof.exit` marker after the tmux server exited, but the JSONL transcript ended with a normal `agent_end`, contained no stderr output, and included successful `close_all` cleanup for the spawned child.

### Final Rollback Instructions

Distribution rollback:

- Revert the distribution release to the previous manifest pins for `stronk-pi-plugin@0.2.2`, `stronk-pi-subagents@0.22.0-stronk.4`, and legacy intercom package configuration if a rollback is required.
- Publish a superseding Stronk-owned distribution release rather than editing upstream repositories.
- Run `bin/stronkpi-setup update --manifest <rollback-manifest>` only after explicit operator confirmation.

Live runtime rollback:

- Restore `~/.stronk-pi/backups/2026-06-29/pre-stronkpi-0.2.3-20260629-100159.tgz` if the live config/agent tree must be reverted.
- Keep old artifacts in `~/.stronk-pi/artifacts` unless a separate prune/delete operation is explicitly confirmed.
- Do not touch original upstream repositories during rollback.

Local branch note:

- `stronk-pi-plugin` and `stronk-pi` local branches are not fast-forward-synced after protected-branch squash merges.
- Do not reset them destructively without an explicit request.
- Remote released commits are the source of truth for published artifacts.

Phase 0 gate evidence commands completed:

- `npm view pi-intercom@0.6.0 --json`
- `npm pack pi-intercom@0.6.0 --pack-destination /tmp/stronk-pi-intercom-phase0 --ignore-scripts`
- `shasum -a 256 /tmp/stronk-pi-intercom-phase0/pi-intercom-0.6.0.tgz`
- `tar -tzf /tmp/stronk-pi-intercom-phase0/pi-intercom-0.6.0.tgz`
- `git ls-remote --tags --heads https://github.com/nicobailon/pi-intercom.git refs/heads/main refs/tags/v0.6.0 refs/tags/v0.6.0^{}`
- `curl -fsSL -o /tmp/stronk-pi-intercom-phase0/nicobailon-pi-intercom-5caa4aa.tar.gz https://codeload.github.com/nicobailon/pi-intercom/tar.gz/5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457`
- `shasum -a 256 /tmp/stronk-pi-intercom-phase0/nicobailon-pi-intercom-5caa4aa.tar.gz`
- `rg -n "\\.pi|pi-intercom|stronk-pi-intercom|STRONKPI_STATE_ROOT|STRONK_PI_STATE_ROOT|INTERCOM" ../stronk-pi-subagents`
- `rg -n "\\.pi|pi-intercom|stronk-pi-intercom|STRONKPI_STATE_ROOT|STRONK_PI_STATE_ROOT|stronk_subagent|read_output|TERMINAL_RESULT_BYTES|MAX_CHILDREN|clearChildOutput" ../stronk-pi-plugin`
- `sed -n` inspections of `src/subagents/facade.mjs`, `src/subagents/schema.mjs`, `src/subagents/ledger.mjs`, and `src/subagents/adapters/pi-subagents-bridge.mjs` in `stronk-pi-plugin`.

## Completion Summary

Completed on 2026-06-29.

- Decision Gate 0 and Decision Gate 1 are closed.
- `stronk-pi-intercom` exists as Stronk-owned repo `EYYCHEEV/stronk-pi-intercom` and released artifact `stronk-pi-intercom-v0.6.0-stronk.1`.
- `stronk-pi-subagents` uses Stronk state roots and `stronk-pi-intercom`, released as `stronk-pi-subagents-v0.22.0-stronk.5`.
- `stronk-pi-plugin` compact facade behavior was released as `stronk-pi-plugin-v0.2.3`.
- `stronk-pi` distribution imports all three released artifacts and was released as `stronk-pi-v0.2.3`.
- Artifact hashes and attestations were verified before import.
- Active live Stronk Pi runtime was refreshed and verified.
- Live tmux Kimi proof succeeded with compact lifecycle calls, bounded redacted output read, and child cleanup.
- No upstream public activity occurred.
- No new unmanaged real-home `~/.pi` writes were observed.

### Final Review Checkpoint

- `checkpoint_id`: `CP-FINAL-COMPLETION`
- `checkpoint_title`: `Final completion and proof audit`
- `status`: `done`
- `verdict`: `accept`
- `retry_count`: `0`
- `blocking_findings`: none.
- `FORK_CONTEXT_USED`: false.
- `strongest_evidence`: Reviewer verified no unchecked plan items, Stronk-owned release tags for all changed repos, three-artifact manifest pins, live proof summary with `spawn`, `wait_all`, bounded `read_output`, and `close_all`, post-proof diagnose with Stronk intercom bridge under `~/.stronk-pi`, empty real-home `.pi` canary, upstream boundary coverage for `nicobailon/pi-intercom`, and rollback instructions.
- `residual_risk`: Local branches in `stronk-pi` and `stronk-pi-plugin` remain diverged from protected-branch squash merges; do not destructively reset without explicit request.
