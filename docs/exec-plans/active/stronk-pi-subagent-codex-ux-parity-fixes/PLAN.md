# Stronk Pi Subagent Codex UX Parity Fixes

## Objective
Make Stronk Pi subagents feel as close as practical to Codex subagents for users working inside repos.

The target experience is that a Stronk Pi user can ask for subagents, route through roles, use `$skills`, wait, follow up, close children, and synthesize child findings with minimal mental translation from Codex.

## Scope
- Improve the Stronk Pi public `stronk_subagent` facade and parent-facing result shape.
- Preserve the guarded safety boundary that denies unsafe user overrides such as `model`, `tools`, `skills`, worktrees, chains, and raw upstream controls.
- Add parent-visible bounded child output so completed children can be used for synthesis.
- Surface role alias resolution so the user can see what actually ran.
- Improve timeout, recovery, and cleanup metadata.
- Add focused unit coverage in `stronk-pi-plugin`.
- Add Stronk Pi runtime and tmux smoke coverage for alias, `$skill`, model inheritance, wait, close, `send_input`, `revive`, diagnostics, and negative failure handling.
- Keep the earlier audit workspace as evidence, not as the execution plan.

## Non-Goals
- Do not expose raw upstream `subagent` controls directly to the model.
- Do not allow user-supplied model, tool, worktree, chain, background, or skill override fields through `stronk_subagent`.
- Do not make child context forked by default.
- Do not change upstream `pi-subagents` unless the facade cannot solve the UX gap.
- Do not publish or commit from this plan without a separate explicit request.

## Constraints
- Use test-driven changes for behavior gaps.
- Use tmux for live Stronk Pi smokes that prove user-facing behavior.
- Use zsh for shell commands.
- Keep active ExecPlan files under `docs/exec-plans/active/`.
- Keep `docs/exec-plans/active/` excluded from public-surface distribution scanning.
- Before any live installed artifact refresh, get explicit operator confirmation for the exact command and path.
- Sync the installed Stronk Pi plugin artifact before live Stronk Pi verification only after source tests pass.
  Record the installed package target, backup artifact path, rollback command/path, and post-refresh validation commands.
  Use a dated backup under `~/.stronk-pi/artifacts/backups/YYYY-MM-DD/`.
- Runtime parity validation must not use dry-run paths.
  Installed artifact smoke and tmux smokes must exercise the real Stronk Pi agent-run path.
- Do not revert unrelated dirty worktree changes.

## Current Findings
- Source implementation now exposes bounded redacted child previews, role alias metadata, timeout/recovery metadata, conservative cleanup proof, and revive model forwarding.
- Source tests now classify failed upstream result rows, nonzero exit codes, top-level errors, status errors, and failed steps before exposing previews.
- Public `stronk_subagent` payloads now deny `cwd` in both the plugin facade schema and the distribution guard.
- `send_input` now fails closed when upstream resume starts or revives a run instead of confirming live delivery, then uses a same-public-child continuation fallback because non-interactive child runs acknowledge intercom delivery without receiving a model turn.
- The final installed artifact was synced under `~/.stronk-pi` with dated backups and passed the real agent-run installed smoke.
- Final live parity smokes for lifecycle/output preview, `$repos`, aliases, `send_input`, `revive`, negative failure, timeout recovery, diagnostics, and read-only/write-swarm UX passed against the refreshed installed runtime.
- Final cleanup evidence found no stale `sp-ux-*` tmux sessions and no non-terminal or unclean recent child handles.

## Proposed Fix Strategy
1. Keep the single guarded `stronk_subagent` facade for this release.
   This preserves the existing safety boundary and avoids exposing raw upstream controls.
   Separate Codex-shaped wrapper tools can be evaluated later only as thin adapters over the same normalizer and denied-field checks.
2. Fix failure classification before exposing output.
   Treat upstream `success: false`, nonzero `exitCode`, failed result rows, error fields, and failed steps as parent-visible failure even when upstream state says `complete`.
3. Make the parent-facing result useful for synthesis.
   Add bounded, redacted `childOutputPreview`, `childOutputTruncated`, `childOutputBytes`, and `childOutputHash` without changing the existing `terminalResult` status field.
   If any lower-level compatibility alias such as `terminalOutputPreview` remains, it must contain the same redacted bounded value.
   Default the preview cap to 8 KiB because the bridge already uses that internal cap.
4. Make role routing transparent.
   Always return `roleRequested`, `roleUsed`, `aliasResolved`, and an optional `aliasMessage` while keeping `child.role` as the effective role for compatibility.
5. Make recovery paths explicit.
   Return action-level `timedOut`, `elapsedMs`, `timeoutMs`, and `recommendedNextAction` where appropriate.
   `recommendedNextAction` must be one of `wait_again`, `check_status`, `send_input`, `close_child`, `inspect_error`, or `run_diagnose`.
6. Make cleanup proof visible but conservative.
   Report `cleanupState`, `upstreamState`, `closeRequested`, `cleanupVerified`, and tri-state process liveness such as `processLive: true|false|null`.
   Do not claim verified cleanup when the process identifier is unknown.
7. Preserve fresh child context and private model inheritance.
   Continue denying public `context`, `model`, `tools`, and `skills` overrides.
   Forward the active parent model privately for both spawn and revive paths when supported.
   Before claiming revive model inheritance, prove the installed upstream `pi-subagents` resume path honors a model override or add a facade/upstream fallback task.
8. Add missing live smokes after source tests and fake-intercom tests pass.
   Run tokenized tmux tests for alias, follow-up, revive, wait-timeout recovery, failure UX, read-only/write-swarm UX, diagnostics, and the existing `$repos` path.

## UX Acceptance Criteria
- Spawn returns `childId`, `roleRequested`, `roleUsed`, `aliasResolved`, optional `aliasMessage`, status, `isTerminal`, and `recommendedNextAction`.
- Completed wait and status results include enough bounded child findings in `childOutputPreview` for the parent to synthesize without inspecting hidden logs.
- Preview text is capped at 8 KiB after redaction.
  Results include `childOutputTruncated`, `childOutputBytes`, and `childOutputHash`.
- Preview persistence policy: `children.json` may persist only the redacted bounded preview and metadata.
  Raw child output must never be persisted.
- Failed children expose `status: "failed"`, `failureReason`, `errorSummary`, and a safe redacted preview when available.
- Failure classification happens before preview exposure.
  `success: false`, nonzero `exitCode`, failed result rows, top-level `error` fields, failed steps, or step errors must override upstream `state: "complete"`.
- Timeout results are non-terminal and include `timedOut`, `elapsedMs`, `timeoutMs`, and `recommendedNextAction`.
- `send_input` requires a non-terminal child, returns accepted/linked proof for the same child, and returns actionable errors for terminal or missing children.
- `close` is idempotent for terminal children, handles live children conservatively, and reports `closeRequested`, `cleanupState`, `upstreamState`, `processLive`, and `cleanupVerified`.
- `revive` reports `previousChildId`, uses fresh child context, preserves private active-parent model inheritance when upstream supports it, and returns actionable errors for missing or non-terminal children.
- Diagnostics report enabled runtime, linked intercom bridge, and exact pinned package versions for `pi-subagents` and `pi-intercom`.
- Live smokes assert parent-visible tool-result and transcript behavior, not only child session logs.

## Security Acceptance Criteria
- Child preview redaction must remove common secret patterns, `key/password/token/secret = value` assignments, local paths such as `/Users/...`, `/home/...`, `/tmp/...`, and `file:` URLs.
- Redaction must happen before truncation so the 8 KiB preview cap applies to public text, not raw child output.
- Store or return only redacted bounded previews and metadata.
  Never store or return raw child output in public parent context.
- No new public schema field may pass `model`, `provider`, `tools`, `skills`, non-fresh `context`, worktree, chain, output hints, or background controls.
  Any future wrapper tool must call the same normalizer and denied-field checks.
- Add an end-to-end guard test proving raw upstream `subagent` remains denied while `stronk_subagent` remains allowed.
- Alias metadata may expose only `roleRequested`, `roleUsed`, and `aliasResolved`.
  Do not expose manifest paths, role directory paths, extension paths, full allowed-role lists, or extra runtime paths in alias metadata.
- Cleanup proof must split "close requested" from "cleanup verified".
  `processLive` must be `null` when PID/PGID is unknown, and Stronk Pi must not infer verified cleanup without independent evidence.
- Installed artifact refresh must create and log a dated backup, include rollback instructions, and pass installed smoke plus diagnose before live tmux smokes.
- Dry-run output is not acceptable parity evidence.
  Runtime smokes must invoke actual agent runs and fail if they detect a dry-run flag, dry-run-only warning path, or skipped child execution.

## Task Checklist
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

## Validation Plan
- Source plugin tests first:
  `npm run check` in `<stronk-pi-plugin>`.
- Source Stronk Pi tests:
  `python3 -m unittest discover -s tests` in `<stronk-pi>`.
- Targeted fake-intercom tests:
  cover failure classification, redacted preview, timeout metadata, cleanup proof, and revive model behavior before any installed artifact sync.
- Operator-approved installed artifact refresh:
  record target, backup, rollback path, and validation commands before replacing the live artifact.
- Installed artifact smoke:
  run `npm run smoke:installed` from `<stronk-pi-plugin>`.
  Pass criteria: `stronk_subagent` is registered, raw `subagent` is absent from the public guarded surface, the smoke executes an actual agent run, no dry-run flag/path is used, a child reaches terminal state, close cleanup is reported, and new public fields are present.
- Diagnose linked path:
  `stronkpi --diagnose --json` must return `ok: true`, `subagentRuntime.enabled: true`, `subagentRuntime.intercomBridgeLinked: true`, and exact pinned package versions for `pi-subagents` and `pi-intercom`.
- Diagnose negative path:
  simulate missing or unlinked intercom/package state and prove the message is actionable without leaking secrets or local paths.
- Live tmux lifecycle/output smoke:
  pass tokens `STATUS_TOKEN=STRONK_PI_LIFECYCLE_OK`, `TERMINAL_OUTPUT_PREVIEW_SEEN=true`, `CLOSED=true`.
  Parent-visible result must show `childOutputPreview`, truncation/byte/hash metadata, role metadata, and cleanup metadata.
- Live tmux `$repos` smoke:
  child output must include `STATUS_TOKEN=STRONK_PI_REPOS_SKILL_OK`, and the parent transcript must show a bounded preview that is sufficient for synthesis.
- Live tmux alias smoke:
  pass token `STATUS_TOKEN=STRONK_PI_ALIAS_OK`.
  Spawning `docs-scout`, `structure-scout`, and `source-scout` must not fail role validation and must expose `roleRequested`, `roleUsed`, and `aliasResolved=true`.
- Live tmux `send_input` smoke:
  pass token `STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK` and line `FOLLOWUP_CONSUMED=true`.
  Parent must prove the follow-up is linked to the same child.
- Live tmux `revive` smoke:
  pass token `STATUS_TOKEN=STRONK_PI_REVIVE_OK`, line `PREVIOUS_CHILD_LINKED=true`, and line `MODEL_INHERITED=true`.
  Inspect the revived child session/model, not only the bridge request payload.
- Live tmux negative smoke:
  pass token `STATUS_TOKEN=STRONK_PI_NEGATIVE_FAILURE_OK` and line `PARENT_VISIBLE_FAILURE=true`.
  Safe child failure must surface as parent-visible failure or actionable error, not misleading success with empty output.
- Live tmux wait-timeout recovery smoke:
  pass token `STATUS_TOKEN=STRONK_PI_TIMEOUT_RECOVERY_OK`.
  A short wait must return `timedOut=true` and a non-empty `recommendedNextAction`, then a later status or wait must prove the child can complete or be closed.
- Live tmux diagnostics smoke:
  linked path passes `DIAG_TOKEN=STRONK_PI_DIAG_LINKED_OK`.
  missing intercom path passes `DIAG_TOKEN=STRONK_PI_DIAG_MISSING_INTERCOM_OK`.
- Live tmux read-only/write-swarm UX smoke:
  pass token `STATUS_TOKEN=STRONK_PI_SWARM_UX_OK`, line `READ_ONLY_DENIED_MUTATION=true`, line `WRITE_SWARM_REPORTS_ROLE_ROUTING=true`, and line `CLEANUP_REPORTED=true`.
- Cleanup verification:
  inspect parent transcript, child session logs, and tracked child handles; close any remaining children and record cleanup proof.

## Open Questions
- [x] Should Stronk Pi add separate Codex-shaped wrapper tools, or keep one `stronk_subagent` tool with Codex-like result shape and stronger guidance?
  Answer: keep one guarded `stronk_subagent` tool for this release; consider wrapper tools later only as thin adapters over the same facade.
- [x] What is the default safe child output preview size: 8 KiB, 16 KiB, or artifact handle plus preview?
  Answer: default to 8 KiB for the first implementation because the bridge already uses an 8 KiB terminal summary cap.
- [x] Should alias metadata be returned only when an alias is used, or always as explicit `roleRequested` and `roleUsed`?
  Answer: always return role metadata so callers do not branch on missing fields.
- [x] Should `revive` remain Stronk-specific, or should it be described as a recovery affordance rather than Codex parity behavior?
  Answer: keep `revive` as a Stronk-specific recovery affordance; do not present it as a native Codex lifecycle primitive.

## Follow-Up Backlog From Manual Swarm Feedback
- [ ] Add a guarded batch wait/barrier affordance, likely `action: "wait_all"` or a narrow `collect` action over known child IDs, so parent orchestration does not require one wait call per child.
  It must preserve `MAX_CHILDREN`, timeout metadata, non-terminal timeout semantics, and the existing guarded `stronk_subagent` safety boundary.
- [ ] Add durable full-output access through an opaque handle or chunked read contract.
  The current 8 KiB `childOutputPreview` is correct for parent context, but full child output currently lives in upstream temp artifacts such as `/var/folders/.../pi-subagents-uid-501/artifacts/..._output.md`.
  A follow-up should copy or render a redacted durable artifact under Stronk state and expose only a safe handle plus metadata, not a local absolute path or raw unbounded text.
- [ ] Consider batch close or collect-and-close ergonomics after synthesis.
  This should remain explicit enough that cleanup proof is visible per child and does not hide failures.
- [ ] Consider structured spawn metadata for common orchestration intent such as `mode`, `ownership`, `expectedOutput`, or `readOnly`.
  These fields must be prompt-shaping metadata only and must not become model/tool/skill/context/worktree override channels.
- [ ] Add citation/evidence hygiene guidance for subagent audit tasks.
  Manual feedback found minor line-number drift even when source claims were substantively correct, so future evidence reports should prefer freshly generated file-line references at final synthesis time.
