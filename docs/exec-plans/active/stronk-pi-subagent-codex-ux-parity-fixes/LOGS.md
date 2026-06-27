# Project Log: Stronk Pi Subagent Codex UX Parity Fixes
Created: 2026-06-26T16:32:36+08:00
Plan: ./PLAN.md
Workspace: docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/

## Progress
- [x] Record the Codex-vs-Stronk-Pi parity findings in this new workspace.
- [x] Lock the design direction for the public lifecycle surface.
- [x] Add upstream failure classification before exposing child output previews.
- [x] Add parent-visible bounded child output preview fields to `stronk-pi-plugin` facade results.
- [x] Add alias transparency fields to spawn and revive results.
- [x] Add timeout and recovery metadata to wait and bridge-start failure paths.
- [x] Add conservative cleanup verification metadata to close and interrupt paths.
- [x] Propagate the active parent model through the bridge revive path.
- [x] Add or update unit tests for failure classification, child output preview redaction and truncation, alias metadata, timeout metadata, cleanup metadata, revive model inheritance, and schema guardrails.
- [x] Add tests for denied overrides, raw `subagent` denial, unknown child ID, invalid role, terminal `send_input`, bridge start failure, and malformed UTF-8 or multi-byte truncation at the 8 KiB boundary.
- [x] Add guidance/docs for fresh child context, denied overrides, role routing reports, long waits, terminal barriers, and mandatory close cleanup.
- [x] Run `npm run check` in `stronk-pi-plugin`.
- [x] Run `python3 -m unittest discover -s tests` in `stronk-pi`.
- [x] Add fake-intercom targeted tests for failure rows, output preview, timeout, cleanup, and revive model behavior.
- [x] Record the installed artifact target, backup path, rollback path, and post-refresh validation commands.
- [x] Sync the installed plugin artifact with dated backups before live smokes.
- [x] Run installed artifact smoke from `stronk-pi-plugin` through the real agent-run path, with no dry-run mode.
- [x] Add tmux smoke prompts/scripts for lifecycle/output preview, alias resolution, `send_input`, `revive`, wait-timeout recovery, negative child failure, diagnostics, read-only/write-swarm UX, cleanup proof, and the existing `$repos` path.
- [x] Run live tmux smoke suite and inspect parent and child session logs.
- [x] Update `LOGS.md` with evidence, risks, and remaining parity gaps.

## Session History
- [2026-06-26] Started implementation execution session for source TDD, fake-intercom coverage, guarded installed-artifact refresh preparation, and live smoke completion.
- [2026-06-26] Created this execution workspace from the Stronk Agents parity swarm findings.
- [2026-06-26] Set up missing repo ExecPlan infrastructure by adding `.agents/PLANS.md` and the managed root `AGENTS.md` ExecPlans block.
- [2026-06-26] Ran a read-only Stronk Agents swarm with architect, technical-researcher, qa-tester, critic, and code-reviewer roles using `fork_context=false`.
- [2026-06-26] Updated PLAN and LOGS with the swarm-vetted parity matrix, backlog, test plan, and implementation sequence.
- [2026-06-26] Closed all five read-only swarm subagents and confirmed `wait_agent` returned `not_found` for every agent ID.
- [2026-06-26] Ran a second read-only verifier swarm with requirements-analyst, product-designer, architect, security-reviewer, qa-tester, and critic roles using `fork_context=false`.
- [2026-06-26] Second verifier swarm converged on `needs-plan-fix`: keep the strategy, but harden field contracts, redaction, artifact rollback, and tokenized parent-visible smokes before implementation.
- [2026-06-26] Updated PLAN and LOGS with the second-swarm consensus.
- [2026-06-26] Closed all six verifier swarm subagents and confirmed `wait_agent` returned `not_found` for every agent ID.
- [2026-06-26] Updated runtime validation requirements so installed artifact smoke and tmux smokes must use real agent runs, not dry-run paths.
- [2026-06-26] Added source tests for failure classification, bounded redacted previews, alias metadata, timeout metadata, cleanup proof, revive model inheritance, denied overrides, raw `subagent` denial, invalid roles, unknown children, terminal `send_input`, bridge start failure, and UTF-8 truncation.
- [2026-06-26] Implemented parent-facing child preview metadata, failure classification, alias transparency, timeout and recovery metadata, conservative cleanup proof, and bridge revive model propagation in `stronk-pi-plugin`.
- [2026-06-26] Updated Stronk Pi guard and diagnose tests for exact subagent runtime pins, raw upstream `subagent` denial, and missing intercom/package diagnostics.
- [2026-06-26] Updated plugin README and registered tool guidance for fresh child context, denied overrides, role routing reports, long waits, terminal barriers, and close cleanup.
- [2026-06-26] Updated `scripts/installed-artifact-smoke.mjs` so the subagent smoke uses the registered `stronk_subagent` tool with the intercom adapter and rejects mocked or skipped child paths.
- [2026-06-26] Added tmux smoke prompt/script artifacts for lifecycle/output preview, `$repos`, alias resolution, `send_input`, `revive`, negative failure, timeout recovery, diagnostics, and read-only/write-swarm UX.
- [2026-06-26] Source validation passed with `npm run check` in `stronk-pi-plugin`.
  Result: 218 Node tests passed and `security-check: ok`.
- [2026-06-26] Source validation passed with `python3 -m unittest discover -s tests` in `stronk-pi`.
  Result: 67 tests passed.
- [2026-06-26] Targeted fake-intercom validation passed with `node --test test/subagent-facade.test.mjs test/extension.test.mjs`.
  Result: 206 tests passed.
- [2026-06-26] Source-pointed installed smoke passed with `STRONK_PI_SMOKE_PLUGIN=src/index.mjs node scripts/installed-artifact-smoke.mjs`.
  This is source smoke evidence only and does not replace the required post-sync installed artifact smoke.
- [2026-06-26] Runner syntax validation passed with `zsh -n` for `tmux-live-smoke-runner.zsh` and `tmux-diagnostics-smoke.zsh`.
- [2026-06-26] Diff whitespace validation passed with `git diff --check` in both `stronk-pi` and `stronk-pi-plugin`.
- [2026-06-26] Closed verifier subagents `019f0396-dec3-7b41-b159-cd1c85cd172d` and `019f0396-dfb3-76c0-8099-3687abad4020` after synthesis.
  The earlier QA verifier `019f0396-df34-7833-a9ce-e46c250e7076` was already closed.
- [2026-06-26] Addressed verifier findings by removing public `cwd` from the `stronk_subagent` schema, adding distribution guard denial for `cwd`, strengthening preview redaction for quoted secret assignments and local paths with spaces, refreshing `send_input` before terminal checks, classifying immediate bridge failures, and making installed smoke run the real agent-run phase by default.
- [2026-06-26] Tightened tmux smoke artifacts so alias cases require parent-visible alias metadata, timeout recovery requires a constrained `recommendedNextAction`, and read-only/write-swarm UX reports role routing from the parent tool result.
- [2026-06-26] Targeted fake-intercom validation passed after verifier fixes with `node --test test/subagent-facade.test.mjs test/extension.test.mjs`.
  Result: 211 tests passed.
- [2026-06-26] Source validation passed after verifier fixes with `npm run check` in `stronk-pi-plugin`.
  Result: 223 Node tests passed and `security-check: ok`.
- [2026-06-26] Source validation passed after verifier fixes with `python3 -m unittest discover -s tests` in `stronk-pi`.
  Result: 68 tests passed.
- [2026-06-26] Source-pointed installed smoke passed after verifier fixes with `STRONK_PI_SMOKE_PLUGIN=src/index.mjs STRONK_PI_SMOKE_AGENT_RUN=0 node scripts/installed-artifact-smoke.mjs`.
  This is source smoke evidence only and does not replace the required post-sync installed artifact smoke.
- [2026-06-26] Runner syntax validation passed again with `zsh -n` for `tmux-live-smoke-runner.zsh` and `tmux-diagnostics-smoke.zsh`.
- [2026-06-26] Diff whitespace validation passed again with `git diff --check` in both `stronk-pi` and `stronk-pi-plugin`.
- [2026-06-26] Continuation audit confirmed PLAN and LOGS checklist reconciliation: 20 items in each file, no missing labels, and no state drift.
- [2026-06-26] Fast pre-approval validation passed with `node --test test/subagent-facade.test.mjs`, `python3 -m unittest tests.test_guard_matrix`, and `STRONK_PI_SMOKE_PLUGIN=src/index.mjs STRONK_PI_SMOKE_AGENT_RUN=0 node scripts/installed-artifact-smoke.mjs`.
  Result: 32 subagent facade tests passed, 11 guard matrix tests passed, and source-only smoke passed.
- [2026-06-26] Operator approval was received to sync the installed plugin artifact under `~/.stronk-pi`.
- [2026-06-26] Installed artifact sync completed multiple times while smoke-harness and `send_input` fixes were finalized.
  Final backup path: `/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-200423`.
- [2026-06-26] Final source validation passed with `npm run check` in `stronk-pi-plugin` and `python3 -m unittest discover -s tests` in `stronk-pi`.
  Result: 224 Node tests passed, `security-check: ok`, and 68 Python tests passed.
- [2026-06-26] Final targeted fake-intercom validation passed with `node --test test/subagent-facade.test.mjs test/extension.test.mjs`.
  Result: 212 tests passed.
- [2026-06-26] Final real installed artifact smoke passed with `npm run smoke:installed`.
  Result: real `stronkpi --no-session -p @prompt` agent-run path passed against `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package/src/index.mjs`.
- [2026-06-26] Final diagnose passed with `bin/stronkpi --diagnose --json`.
  Result: `ok: true`, `subagentRuntime.intercomBridgeLinked: true`, `pi-subagents` 0.22.0, and `pi-intercom` 0.6.0.
- [2026-06-26] Final tmux diagnostic smokes passed for linked and missing-intercom paths.
  Logs: `docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-diagnostics/20260626-201159/`.
- [2026-06-26] Final live tmux smoke suite passed through real Stronk Pi agent runs.
  Logs: `docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-smokes/20260626-200724/`.
- [2026-06-26] Final cleanup audit passed.
  Result: no `sp-ux-*` tmux sessions, 8 fresh final ledger files, 12 final children, 0 non-terminal children, and 0 unclean terminal children.

## Decisions
- [2026-06-26] Decision: execute tightly coupled source edits in the orchestrator thread and reserve subagents for read-only verification because the plugin facade, bridge, ledger, and smoke/docs changes have high ownership overlap.
- [2026-06-26] Decision: keep the guarded `stronk_subagent` facade as the safety boundary because full raw upstream pass-through would expose controls Stronk Pi intentionally denies.
- [2026-06-26] Decision: treat the existing `stronk-pi-subagent-codex-parity-audit` workspace as evidence and create this separate execution plan because the audit workspace should not double as the implementation backlog.
- [2026-06-26] Decision: target Codex-like UX through result shape, metadata, guidance, and live smoke coverage before considering larger upstream changes.
- [2026-06-26] Decision: keep one guarded `stronk_subagent` tool for this release because richer result shape is lower-risk than adding multiple wrapper tools before the facade contract is complete.
- [2026-06-26] Decision: default child output preview to 8 KiB because the bridge already computes bounded terminal summaries at that cap.
- [2026-06-26] Decision: always expose `roleRequested`, `roleUsed`, and `aliasResolved` because consistent fields avoid client branching and make silent aliases auditable.
- [2026-06-26] Decision: fix upstream failure classification before exposing output previews because a completed-looking failed child would become more misleading once preview text is visible.
- [2026-06-26] Decision: treat cleanup proof as conservative metadata because Stronk Pi can report process/upstream evidence but cannot always prove process death when no process identifier is available.
- [2026-06-26] Decision: use `childOutputPreview`, `childOutputTruncated`, `childOutputBytes`, and `childOutputHash` as the parent-facing preview contract.
  Any lower-level `terminalOutputPreview` compatibility alias must carry the same redacted bounded value.
- [2026-06-26] Decision: parent-visible child preview is public parent context.
  Only redacted bounded preview and metadata may be stored or returned because child output can contain secrets and local paths.
- [2026-06-26] Decision: allow `children.json` to persist only the redacted bounded preview and metadata.
  Raw child output must never be persisted.
- [2026-06-26] Decision: source tests and fake-intercom tests must pass before installed artifact sync or live tmux smokes.
- [2026-06-26] Decision: installed artifact refresh requires explicit operator confirmation, a dated backup, rollback instructions, installed smoke, and diagnose proof.
- [2026-06-26] Decision: revive model inheritance remains a parity target only after proving the installed upstream resume path honors a model override or adding a facade/upstream fallback.
- [2026-06-26] Decision: dry-run behavior is not acceptable evidence for Codex-like subagent parity because the UX risk lives in the actual parent-to-child agent-run path.
  Runtime smokes must execute real child runs and fail if they detect dry-run flags, dry-run-only warnings, or skipped child execution.
- [2026-06-26] Decision: public `cwd` is a path-boundary override and must be denied through both the plugin facade schema and the Stronk Pi distribution guard.
- [2026-06-26] Decision: `scripts/installed-artifact-smoke.mjs` runs the real `stronkpi -p @prompt` agent-run phase by default.
  Source-only validation must opt out explicitly with `STRONK_PI_SMOKE_AGENT_RUN=0`.
- [2026-06-26] Decision: `send_input` must fail closed unless upstream confirms live delivery, then use a same-public-child continuation fallback because Pi non-interactive child runs acknowledge intercom delivery at the broker layer without receiving a model turn.
- [2026-06-26] Decision: live smoke token checks may append ledger-verified token lines for alias and `send_input` cases because public previews redact `STATUS_TOKEN=...` assignments and model final-answer formatting is nondeterministic.

## Blockers

- None active.
- [2026-06-26 19:22 +0800] Resolved: operator approval was received and installed artifact sync completed with dated backups.

## Installed Artifact Refresh Plan And Evidence

- Target path:
  `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`
- Source path:
  `/Users/eyy/Documents/Work/Dev/repos/stronk-pi-plugin`
- Backup path template:
  `~/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.<YYYYMMDD-HHMMSS>`
- Exact sync command to run after approval:
  `zsh -lc 'set -euo pipefail; src="/Users/eyy/Documents/Work/Dev/repos/stronk-pi-plugin"; target="$HOME/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package"; stamp="$(date +%Y%m%d-%H%M%S)"; backup="$HOME/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.${stamp}"; tmp="$(mktemp -d "${TMPDIR:-/tmp}/stronk-pi-plugin-pack.XXXXXX")"; trap '\''rm -rf "$tmp"'\'' EXIT; mkdir -p "$(dirname "$backup")"; cp -a "$target" "$backup"; tarball="$(cd "$src" && npm pack --pack-destination "$tmp")"; rm -rf "$target"; mkdir -p "$target"; tar -xzf "$tmp/$tarball" -C "$tmp"; cp -a "$tmp/package/." "$target/"; print -r -- "BACKUP=$backup"'`
- Rollback command template:
  `zsh -lc 'set -euo pipefail; backup="<backup path printed by sync>"; rm -rf "$HOME/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package"; cp -a "$backup" "$HOME/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package"'`
- Post-refresh validation commands:
  `zsh -lc 'npm run smoke:installed'` from `/Users/eyy/Documents/Work/Dev/repos/stronk-pi-plugin`.
  `zsh -lc 'bin/stronkpi --diagnose --json'` from `/Users/eyy/Documents/Work/Dev/repos/stronk-pi`.
  `zsh -lc 'docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/tmux-diagnostics-smoke.zsh'` from `/Users/eyy/Documents/Work/Dev/repos/stronk-pi`.
  `zsh -lc 'docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/tmux-live-smoke-runner.zsh'` from `/Users/eyy/Documents/Work/Dev/repos/stronk-pi`.
- Final applied backup:
  `/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-200423`
- Earlier backups from this approved refresh sequence:
  `/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-192505`
  `/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-192604`
  `/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-194157`
  `/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-195756`
- Rollback command for final installed state:
  `zsh -lc 'set -euo pipefail; backup="/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-200423"; rm -rf "$HOME/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package"; cp -a "$backup" "$HOME/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package"'`

## Open Questions
- [x] Should Stronk Pi add separate Codex-shaped wrapper tools, or keep one `stronk_subagent` tool with Codex-like result shape and stronger guidance?
  Answer: keep one guarded `stronk_subagent` tool for this release; consider wrapper tools later only as thin adapters over the same facade.
- [x] What is the default safe child output preview size: 8 KiB, 16 KiB, or artifact handle plus preview?
  Answer: use 8 KiB first because the bridge already uses that terminal summary cap.
- [x] Should alias metadata be returned only when an alias is used, or always as explicit `roleRequested` and `roleUsed`?
  Answer: always return role metadata.
- [x] Should `revive` remain Stronk-specific, or should it be described as a recovery affordance rather than Codex parity behavior?
  Answer: keep `revive` as a Stronk-specific recovery affordance.

## Field Notes
- Evidence workspace: `docs/exec-plans/active/stronk-pi-subagent-codex-parity-audit/`.
- Verified green path from audit:
  parent prompt loads `$repos`, parent uses `stronk_subagent`, child receives `$repos`, child uses the active parent model, parent waits with `timeoutMs=3600000`, parent closes the terminal child, and diagnose reports the intercom bridge as linked.
- Primary remaining P0 gap:
  parent-facing `child` result metadata does not include bounded child output text, so a parent can observe completion without seeing the child findings in the tool result.
- Primary UX mismatch:
  Codex exposes native lifecycle primitives while Stronk Pi exposes a single guarded action tool.
- Safety boundary:
  public schema should continue denying user-supplied `model`, `provider`, `tools`, `skills`, worktrees, chains, background controls, output hints, and non-fresh context.
- Runtime smokes still needed:
  aliases, `send_input`, `revive`, and negative child failure handling.
- Second verifier swarm consensus:
  the architecture is sound and no more broad design pass is needed, but implementation should wait until the plan has explicit UX/security acceptance criteria and tokenized parent-visible verification gates.
- Broader role discovery remains deferred P2.
  It is not required for the first parity pass as long as role routing metadata and diagnostics are explicit.
- Live parity confidence remains medium until installed artifact smoke and all tokenized tmux smokes pass against the refreshed installed runtime.
- Runtime parity evidence must come from actual agent runs.
  Unit and fake-intercom tests still cover source logic, but installed artifact smoke and tmux smokes cannot pass through dry-run behavior.

### 2026-06-26 Read-Only Swarm Synthesis

Subagent routing report:
- architect: `ROLE_REQUESTED=architect`, `ROLE_USED=architect`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- technical-researcher: `ROLE_REQUESTED=technical-researcher`, `ROLE_USED=technical-researcher`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- qa-tester: `ROLE_REQUESTED=qa-tester`, `ROLE_USED=qa-tester`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- critic: `ROLE_REQUESTED=critic`, `ROLE_USED=critic`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- code-reviewer: `ROLE_REQUESTED=code-reviewer`, `ROLE_USED=code-reviewer`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.

Codex-vs-Stronk-Pi parity matrix:
- Lifecycle primitives:
  Codex exposes separate `spawn_agent`, `wait`, `send_input`, and `close_agent` tools.
  Stronk Pi exposes one guarded `stronk_subagent` action tool with `spawn`, `wait`, `status`, `send_input`, `interrupt`, `close`, and `revive`.
  Parity target: keep one guarded tool for this release, but make outputs and guidance Codex-like.
- Parent-visible child output:
  Codex returns usable final child text to the parent.
  Stronk Pi exposes `terminalResult`, hash, and byte count but no bounded output preview.
  Parity target: add redacted `childOutputPreview` plus truncation and byte/hash metadata.
- Role routing, aliases, and discovery:
  Codex uses exact role names in `agent_type`.
  Stronk Pi uses manifest roles and silent aliases such as `docs-scout`, `structure-scout`, and `source-scout`.
  Parity target: always expose requested/effective role metadata and leave broader role discovery as P2.
- Skill injection and `$skill` behavior:
  Codex skill context is first-class in the parent session.
  Stronk Pi injects `$skill` content at prompt time from `STRONK_PI_SKILL_ROOTS`, then child execution uses fresh context.
  Parity target: keep fresh context and smoke-test that parent-loaded skill blocks reach child prompts.
- Model inheritance:
  Codex child agents inherit the active parent model unless a role override applies.
  Stronk Pi spawn now forwards the active parent model privately.
  Parity target: extend that same private model propagation to `revive`.
- Context inheritance:
  Codex subagents start as separate agent threads.
  Stronk Pi intentionally forces upstream `context: "fresh"` and denies public context overrides.
  Parity target: keep fresh context for safety and make the behavior explicit in docs and smokes.
- Wait timeout behavior:
  Codex wait can time out without making the child terminal.
  Stronk Pi polls until terminal or timeout, but currently returns a child without explicit timeout metadata.
  Parity target: return `timedOut`, `elapsedMs`, `timeoutMs`, and `recommendedNextAction`.
- Close and cleanup proof:
  Codex closed agents stop counting toward lifecycle limits and can be confirmed absent.
  Stronk Pi records `cleanupState` and can infer some PID/upstream state, but does not strongly prove process cleanup.
  Parity target: expose conservative upstream/process proof and avoid overclaiming.
- Error surfacing and negative failures:
  Codex-like behavior should make child failures obvious to the parent.
  Stronk Pi can map upstream `state: "complete"` to `completed` without checking failed result details.
  Parity target: classify failure from success flags, exit codes, result rows, step errors, and error fields before exposing preview text.
- Diagnostics and setup failures:
  Stronk Pi diagnose already reports subagent runtime package state, extension paths, and `intercomBridgeLinked`.
  Parity target: keep diagnostics as the source of setup truth and add focused missing-package/intercom messages where needed.
- Write-swarm/read-only-swarm UX expectations:
  Codex uses explicit lifecycle tools and close discipline.
  Stronk Pi should keep the guarded facade, explicit role routing reports, long waits, terminal barrier, and mandatory close cleanup.
- Tmux live smoke coverage:
  Existing `$repos` smoke proves skill injection, parent model inheritance for spawn, wait, close, and diagnose.
  Missing live smokes are alias resolution, `send_input`, `revive`, wait-timeout recovery, negative child failure, and cleanup proof.

P0 backlog:
- Fix upstream failure classification before output preview.
- Add bounded redacted child output preview fields.
- Enforce preview redaction before truncation, with no raw child output stored or returned in public parent context.
- Add explicit wait timeout/recovery metadata.
- Add alias transparency fields because role routing is part of the parity goal.
- Add conservative cleanup proof metadata because close must be parent-visible and trustworthy.
- Add parent-transcript/tool-result assertions for output preview and failure visibility.
- Add installed artifact backup, rollback, real agent-run installed smoke, and diagnose gates before live tmux smokes.
- Add tests for failure classification, output preview redaction and truncation, timeout metadata, denied overrides, raw `subagent` denial, and malformed UTF-8 or multi-byte truncation at the 8 KiB boundary.

P1 backlog:
- Propagate active parent model through bridge revive.
- Prove installed upstream revive honors model override or add a facade/upstream fallback.
- Add guidance/docs for fresh context, guarded overrides, role routing reports, long waits, terminal barriers, and mandatory close cleanup.
- Add negative diagnostics tests and smokes for missing package and intercom bridge states.
- Add live tmux smokes for alias, `send_input`, `revive`, wait-timeout recovery, negative failure, and cleanup proof.

P2 backlog:
- Evaluate thin Codex-shaped wrapper tools over the same guarded facade.
- Add role/capability discovery if diagnostics and role metadata are not enough.
- Add richer progress/current-tool metadata for long-running children.
- Consider artifact-handle output for previews larger than 8 KiB.

Exact files likely needing changes:
- `<stronk-pi-plugin>/src/subagents/adapters/pi-subagents-bridge.mjs`
- `<stronk-pi-plugin>/src/subagents/facade.mjs`
- `<stronk-pi-plugin>/src/subagents/ledger.mjs`
- `<stronk-pi-plugin>/src/subagents/schema.mjs`
- `<stronk-pi-plugin>/src/index.mjs`
- `<stronk-pi-plugin>/test/subagent-facade.test.mjs`
- `<stronk-pi-plugin>/test/extension.test.mjs`
- `<stronk-pi-plugin>/scripts/installed-artifact-smoke.mjs`
- `<stronk-pi>/lib/stronk-pi-guard.py`
- `<stronk-pi>/tests/test_mcp_doctor.py`
- `<stronk-pi>/tests/test_public_surface.py`
- `<stronk-pi>/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/`

Tests to add:
- `stronk_subagent maps upstream success false or failed result rows to child failure`.
- `stronk_subagent public child exposes bounded redacted child output preview`.
- `stronk_subagent reports roleRequested roleUsed aliasResolved for canonical roles and aliases`.
- `stronk_subagent wait timeout returns running child plus timedOut metadata`.
- `stronk_subagent close and interrupt return conservative cleanup proof`.
- `stronk_subagent revive forwards active parent model to upstream resume`.
- `stronk_subagent revive proves the installed upstream resume path honors model override, or the facade fallback is exercised`.
- `stronk_subagent denies raw/public overrides for model, provider, tools, skills, context, worktree, chain, output hints, and background controls`.
- `stronk_subagent preview redaction handles local paths, file URLs, secret assignments, malformed UTF-8, and multi-byte truncation at the 8 KiB boundary`.
- Distribution tests that `stronk_subagent` stays allowed, raw `subagent` stays denied, and diagnose keeps `intercomBridgeLinked` evidence.

Tmux smokes to add:
- `tmux-lifecycle-output-smoke.prompt.md` with `STATUS_TOKEN=STRONK_PI_LIFECYCLE_OK`, `TERMINAL_OUTPUT_PREVIEW_SEEN=true`, and `CLOSED=true`; this must use the real agent-run path and fail on dry-run behavior.
- `tmux-repos-skill-smoke.prompt.md` and runner copied or refreshed from the audit workspace; parent result inspection must prove the preview is sufficient for synthesis.
- `tmux-alias-resolution-smoke.prompt.md` with `STATUS_TOKEN=STRONK_PI_ALIAS_OK` for `docs-scout`, `structure-scout`, and `source-scout`.
- `tmux-send-input-smoke.prompt.md` with `STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK` and `FOLLOWUP_CONSUMED=true`.
- `tmux-revive-smoke.prompt.md` with `STATUS_TOKEN=STRONK_PI_REVIVE_OK`, `PREVIOUS_CHILD_LINKED=true`, and `MODEL_INHERITED=true`.
- `tmux-negative-child-failure-smoke.prompt.md` with `STATUS_TOKEN=STRONK_PI_NEGATIVE_FAILURE_OK` and `PARENT_VISIBLE_FAILURE=true`.
- `tmux-wait-timeout-recovery-smoke.prompt.md` with `STATUS_TOKEN=STRONK_PI_TIMEOUT_RECOVERY_OK`, `timedOut=true`, and a non-empty `recommendedNextAction`.
- `tmux-diagnostics-smoke.zsh` with linked `DIAG_TOKEN=STRONK_PI_DIAG_LINKED_OK` and missing-intercom `DIAG_TOKEN=STRONK_PI_DIAG_MISSING_INTERCOM_OK`.
- `tmux-readonly-write-swarm-ux-smoke.prompt.md` with `STATUS_TOKEN=STRONK_PI_SWARM_UX_OK`, `READ_ONLY_DENIED_MUTATION=true`, `WRITE_SWARM_REPORTS_ROLE_ROUTING=true`, and `CLEANUP_REPORTED=true`.

VETTING_RECORD:
- CLAIMS:
  The five subagents agree that the current architecture should keep the guarded facade and improve result shape before wrapper tools.
  They agree the main remaining UX gap is parent-visible child output.
  They agree alias, timeout, cleanup, revive, and negative failure paths need additional metadata and tests.
- EVIDENCE:
  `{file_ref: "<stronk-pi-plugin>/src/subagents/schema.mjs:1", observation: "Public actions are spawn, wait, status, send_input, interrupt, close, and revive."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/schema.mjs:5", observation: "Denied override keys include model, tools, skills, worktree, chain, and background controls."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/ledger.mjs:91", observation: "publicChild exposes status/hash/bytes but no child output preview."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/adapters/pi-subagents-bridge.mjs:34", observation: "Bridge has bounded terminal summary logic."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/adapters/pi-subagents-bridge.mjs:169", observation: "Status mapping needs failed-result checks before completed classification."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/facade.mjs:61", observation: "Aliases are resolved silently."}`
  `{file_ref: "<stronk-pi>/lib/stronk-pi-guard.py:578", observation: "Guard allows stronk_subagent while denying raw subagent."}`
- DONE_CRITERIA_MATCH: pass for read-only investigation and plan update; implementation remains pending.
- CONFIDENCE: high for source-mapped gaps; medium for live UX gaps until tmux smokes are added and run.
- DECISION: accept.
- NEXT_ACTION: implement with TDD starting from failure classification and output preview tests.
- CROSS_VALIDATION:
  Architect, technical-researcher, critic, and code-reviewer agreed on preserving the guarded facade.
  Architect, technical-researcher, qa-tester, and code-reviewer agreed parent-visible output is P0.
  Code-reviewer added the revive model inheritance gap, and source inspection confirmed bridge `revive()` lacks runtime model handling.
  No material contradictions remained after local source inspection.

Cleanup report:
- Closed `019f0319-cbc1-7632-a18f-16aff8e2913a` after synthesis.
- Closed `019f0319-f625-7130-b058-0b303066e6bf` after synthesis.
- Closed `019f031a-2132-7be0-9e3d-77d5550915da` after synthesis.
- Closed `019f031a-4146-7b12-a583-b80067689617` after synthesis.
- Closed `019f031a-6807-72c3-b35b-970de9447be1` after synthesis.
- Confirmation wait returned `not_found` for all five IDs, confirming no tracked Codex subagent handles from that swarm remained open.

### 2026-06-26 Second Verifier Swarm Synthesis

Subagent routing report:
- requirements-analyst: `ROLE_REQUESTED=requirements-analyst`, `ROLE_USED=requirements-analyst`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- product-designer: `ROLE_REQUESTED=product-designer`, `ROLE_USED=product-designer`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- architect: `ROLE_REQUESTED=architect`, `ROLE_USED=architect`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- security-reviewer: `ROLE_REQUESTED=security-reviewer`, `ROLE_USED=security-reviewer`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- qa-tester: `ROLE_REQUESTED=qa-tester`, `ROLE_USED=qa-tester`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.
- critic: `ROLE_REQUESTED=critic`, `ROLE_USED=critic`, `FALLBACK_USED=false`, `FORK_CONTEXT_USED=false`.

Verifier verdict:
- All six verifier agents returned `needs-plan-fix`, not because the architecture was wrong, but because the plan needed sharper acceptance criteria before implementation.
- Consensus: keep the guarded one-tool `stronk_subagent` boundary for this release.
- Consensus: separate Codex-shaped wrapper tools remain P2 until the guarded facade result contract is complete.
- Consensus: implementation can start after the plan hardening edits in this log and `PLAN.md`; another broad design pass is not needed.

Second-swarm plan fixes applied:
- Added UX acceptance criteria for spawn, wait, timeout, `send_input`, close, revive, diagnostics, and live parent-visible transcript behavior.
- Adopted `childOutputPreview`, `childOutputTruncated`, `childOutputBytes`, and `childOutputHash` as the parent-facing preview contract.
- Added preview redaction and persistence policy: redaction before truncation, 8 KiB public cap, no raw child output in parent context, and only redacted bounded preview plus metadata may be persisted.
- Added security criteria for denied override fields, raw upstream `subagent` denial, alias metadata leakage, and conservative cleanup proof.
- Added artifact sync criteria: explicit operator confirmation, dated backup, rollback path, installed smoke, and diagnose proof before live tmux smokes.
- Added no-dry-run runtime validation criteria: installed artifact smoke and tmux smokes must exercise actual agent runs.
- Added revive dependency criteria: prove installed upstream resume honors model override or implement a facade/upstream fallback.
- Reordered validation so source tests and fake-intercom tests run before installed artifact sync and live smokes.
- Replaced absolute local source paths in the active plan/log with `<stronk-pi>` and `<stronk-pi-plugin>` placeholders.

Second-swarm VETTING_RECORD:
- CLAIMS:
  The second verifier swarm agrees the plan is aligned with the ultimate Codex-subagent parity goal after the hardening edits.
  The swarm agrees the next implementation step is source-level TDD, beginning with failure classification and child output preview tests.
  The swarm agrees live confidence remains medium until installed artifact smoke and tokenized tmux smokes pass against the refreshed runtime.
- EVIDENCE:
  `{agent: "requirements-analyst", observation: "Requested explicit acceptance criteria for output semantics, failure precedence, context guidance, close semantics, negative diagnostics, and artifact rollback."}`
  `{agent: "product-designer", observation: "Requested parent mental model criteria, childOutputPreview naming, constrained recommendedNextAction values, and transcript-level smoke assertions."}`
  `{agent: "architect", observation: "Identified ledger preview policy and upstream revive model propagation as plan decisions that could otherwise cause rework."}`
  `{agent: "security-reviewer", observation: "Requested preview redaction-before-truncation, no raw output in public context, raw subagent denial tests, non-leaky alias metadata, and conservative cleanup wording."}`
  `{agent: "qa-tester", observation: "Requested ordered validation, installed artifact smoke, fake-intercom tests, and tokenized tmux smokes with pass/fail evidence."}`
  `{agent: "critic", observation: "Requested parent-visible tool-result assertions, artifact refresh approval, rollback path, and post-refresh validation."}`
- DONE_CRITERIA_MATCH: pass for second read-only verification and ExecPlan hardening; implementation remains pending.
- CONFIDENCE: high for strategy and source-mapped implementation path; medium for live UX until installed artifact and tmux smokes run.
- DECISION: accept with plan hardening complete.
- NEXT_ACTION: implement source P0 with TDD, then run source tests, fake-intercom tests, operator-approved artifact sync, installed smoke, diagnose, and tokenized tmux smokes.
- CROSS_VALIDATION:
  Six agents independently agreed the one-tool guarded facade should stay.
  Six agents independently found the plan needed field-level acceptance criteria before implementation.
  Architect and security-reviewer converged on the preview persistence/redaction policy.
  Product-designer, qa-tester, and critic converged on parent-visible transcript assertions.
  Qa-tester, critic, and security-reviewer converged on installed artifact backup/rollback and installed-smoke requirements.

Second-swarm cleanup report:
- Closed `019f0334-f5ec-7c80-be85-f1102a5125c0` after synthesis.
- Closed `019f0335-1b13-7730-96a0-8e03226c14b6` after synthesis.
- Closed `019f0335-3da9-7df0-b39a-cb1650c6dbcc` after synthesis.
- Closed `019f0335-601a-79a0-9750-8e7cd4e562f4` after synthesis.
- Closed `019f0335-86c3-7d82-8a9e-7ac78c36d391` after synthesis.
- Closed `019f0335-b3ce-7452-aec0-48dc1d1747d5` after synthesis.
- Confirmation wait returned `not_found` for all six IDs, confirming no tracked Codex subagent handles from that verifier swarm remained open.

### 2026-06-26 Final Validation Evidence

Final real-run evidence:
- Installed artifact smoke passed through real `stronkpi --no-session -p @prompt` execution.
- Diagnose passed with linked intercom bridge and pinned package versions: `pi-subagents` 0.22.0 and `pi-intercom` 0.6.0.
- Tmux diagnostics passed both linked and missing-intercom paths.
- Final full live tmux suite passed all required token gates in `artifacts/tmux-smokes/20260626-200724/`.
- Final cleanup audit found 8 fresh final ledger files, 12 final children, 0 non-terminal children, and 0 unclean terminal children.

Send-input runtime finding:
- Upstream `pi-subagents` live resume reports broker-level delivery for non-interactive children, but those children do not receive a model turn from the intercom message.
- The facade now fails closed when upstream resume starts or revives a run instead of confirming live delivery.
- After live-delivery acknowledgement, the facade starts a continuation async run under the same public child handle and records `inputAccepted=true` plus `inputLinkedChildId=<same child>`.
- The smoke runner validates this through fresh `children.json` and `events.ndjson` evidence before emitting `STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK`.

Residual risk:
- The negative failure smoke proves parent-visible failure through the bounded child preview.
  The structured child status can still be `completed` when the child agent intentionally reports a failed shell command in text rather than causing the upstream agent run itself to fail.
  This is acceptable for this plan because the parent-visible preview is non-empty and includes the failure evidence, but a future P2 could classify tool-level failure text more aggressively.

## Artifacts
- Prior audit plan: `docs/exec-plans/active/stronk-pi-subagent-codex-parity-audit/PLAN.md`
- Prior audit log: `docs/exec-plans/active/stronk-pi-subagent-codex-parity-audit/LOGS.md`
- Existing `$repos` tmux prompt: `docs/exec-plans/active/stronk-pi-subagent-codex-parity-audit/tmux-repos-skill-smoke.prompt.md`
- Existing `$repos` tmux runner: `docs/exec-plans/active/stronk-pi-subagent-codex-parity-audit/tmux-repos-skill-smoke.zsh`
- Read-only swarm synthesis recorded in this log on 2026-06-26.
- Final installed artifact backup: `/Users/eyy/.stronk-pi/artifacts/backups/2026-06-26/stronk-pi-plugin-0.1.0.package.bak.20260626-200423`
- Final live tmux smoke logs: `docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-smokes/20260626-200724/`
- Final diagnostics tmux smoke logs: `docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-diagnostics/20260626-201159/`
- Final alias ledger proof: `/Users/eyy/.stronk-pi/projects/7032ab83a0003dbf/facade-runs/facade-1782475685821-f7ec5f8a/children.json`
- Final send-input ledger proof: `/Users/eyy/.stronk-pi/projects/7032ab83a0003dbf/facade-runs/facade-1782475721291-be1f7d69/children.json`

## Client Feedback
- [2026-06-26] User requested a new ExecPlan that records findings in this repo and includes ways to fix Stronk Pi subagent UX so it matches Codex as closely as possible.
- [2026-06-26] User supplied a manual GLM-5.2 vetted report for a real `stronk_subagent` swarm.
  Local re-vetting found the report substantively valid for lifecycle metadata, guard behavior, role policy, manifest pinning, raw `subagent` denial, 8 KiB preview truncation, and cleanup proof.
  Corrections: the technical-researcher upstream artifact/run ID on disk is `16f8b24c-e5c1-44b3-85cc-47de2f61000d`, not `16f8b24d...`; role and manifest line citations drifted but the cited content is correct.
  Evidence checked: `lib/stronk-pi-guard.py` lines for `DENY_BASH_PATTERNS`, `SENSITIVE_PATH_PARTS`, `guarded_tool_decision`, and raw `subagent` denial; `roles/stronk/roles.toml` `[pi.policy]`; `manifests/current.json` plugin pin and attestation; source and installed `stronk-pi-plugin` subagent schema and result fields; `~/.stronk-pi/projects/7032ab83a0003dbf/facade-runs/facade-1782476859571-1f691a15/children.json`; and upstream session files under `~/.stronk-pi/agent/sessions/2026-06-26T12-27-39-559Z_019f03e6-68a7-718b-97d7-ca9ba2b36c10/`.
  Full-output artifacts were present under `${TMPDIR}/pi-subagents-uid-501/artifacts/` with sizes 4904 bytes for `c4ec085d-25c9-48fc-b614-b72a81a68ff4_explorer_output.md` and 12598 bytes for `16f8b24c-e5c1-44b3-85cc-47de2f61000d_technical-researcher_output.md`.
  Caveat: those full-output artifacts are temp-root artifacts, so the report's "artifacts persisted" claim is valid only as "present after the run"; durable full-output access should be a follow-up if Stronk Pi wants day-to-day audit ergonomics beyond the persisted 8 KiB redacted preview.
  Worth implementing later: guarded batch wait/barrier or collect action, durable redacted full-output handles/chunked reads, optional batch close/collect-and-close ergonomics, structured prompt-shaping spawn metadata, and final-synthesis citation hygiene.
