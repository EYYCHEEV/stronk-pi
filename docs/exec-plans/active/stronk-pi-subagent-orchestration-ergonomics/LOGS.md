# Project Log: Stronk Pi Subagent Orchestration Ergonomics
Created: 2026-06-26T21:10:00+08:00
Plan: ./PLAN.md
Workspace: docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/

## Progress
- [x] Record the swarm-vetted design direction and public action naming decisions.
- [x] Add failing source tests proving existing and new public results expose no `cwd`, local paths, upstream temp paths, durable artifact paths, or debug artifact paths.
- [x] Remove or redact `cwd` and debug artifact paths from public child projections while preserving non-path diagnostics.
- [x] Add failing source tests for `wait_all` schema, duplicate IDs, over-limit IDs, unknown or foreign IDs, timeout metadata, mixed terminal states, and per-child failure visibility.
- [x] Add failing source tests for output handles, redaction before durable write, chunk bounds, invalid handles, wrong-run handles, UTF-8 boundaries, quota truncation, and sanitized-only hashes.
- [x] Add failing source tests for `close_all` per-child cleanup proof and partial close failure visibility.
- [x] Add failing schema and guard tests for recursive denied overrides in new actions.
- [x] Implement schema additions for `wait_all`, `read_output`, and `close_all`.
- [x] Implement facade-level `wait_all` aggregation over existing child wait/status behavior.
- [x] Implement a shared child-output sanitizer used before preview projection and before any durable output write.
- [x] Implement ledger-owned sanitized output artifact storage, the 1 MiB cap, and opaque handle projection.
- [x] Implement bounded `read_output` chunk reads.
- [x] Implement explicit `close_all` with per-child cleanup proof.
- [x] Record `promptHints` as deferred P2 and keep it out of P1 smoke gates.
- [x] Update README and tool guidance for batch waits, output handles, batch close, citation hygiene, long waits, and cleanup.
- [x] Extend fake-intercom coverage for mixed terminal/running/failed children, close partial failure, invalid or wrong-run handles, duplicate or foreign child denial, and dry-run rejection.
- [x] Extend `scripts/installed-artifact-smoke.mjs` for real agent-run `wait_all`, `read_output`, `close_all`, and public path hygiene proof.
- [x] Add tmux smoke prompt and runner coverage for `wait_all`, durable output read, and batch close.
- [x] Run `npm run check` in `<stronk-pi-plugin>`.
- [x] Run targeted fake-intercom tests in `<stronk-pi-plugin>`.
- [x] Run `python3 -m unittest discover -s tests` in `<stronk-pi>`.
- [x] Run offline/public-surface checks such as `tests/run_offline.sh` before installed artifact sync when the script is available.
- [x] Ask for explicit operator approval before installed artifact sync.
- [x] After approval, create dated backup, sync installed artifact, run installed smoke through the real agent-run path, run diagnose, run tmux smokes, and record rollback details.
- [x] Run final cleanup audit proving no child handles, durable output artifacts, tmux sessions, or spawned subagents were left open.
- [x] Add failing fake-intercom tests for provider-neutral capacity classification, no raw capacity output, batch aggregate retry metadata, and same-model capacity revive.
- [x] Implement provider capacity classification in the Pi bridge before generic failure handling and before durable output storage.
- [x] Project capacity retry metadata through the public ledger child result without exposing raw provider text or paths.
- [x] Extend `wait_all` aggregation with retryable capacity child IDs and drain-aware recommended next action.
- [x] Implement same-model capacity revive from in-memory retry payloads without persisting raw task text.
- [x] Update README/tool guidance for capacity failures, no fallback, drain-first retry, and output hygiene.
- [x] Run targeted fake-intercom tests for the capacity retry slice.
- [x] Run `npm run check` in `<stronk-pi-plugin>` after the capacity retry slice is green.

## Session History
- [2026-06-26] Created this follow-up ExecPlan from manual real-swarm feedback and the completed `stronk-pi-subagent-codex-ux-parity-fixes` backlog.
- [2026-06-26] Started implementation session for P1 path hygiene, `wait_all`, `read_output`, `close_all`, docs, smokes, and validation.
- [2026-06-26] Verified source TDD slices for path-clean public results, `wait_all`, durable sanitized `read_output`, `close_all`, and recursive override denial with `node --test test/subagent-facade.test.mjs`.
- [2026-06-26] Added diagnose JSON coverage for linked `pi-intercom` runtime and prepared plan-owned tmux smoke artifacts: `tmux-orchestration-smoke.prompt.md` and `tmux-orchestration-smoke.zsh`.
- [2026-06-26] Pre-sync validation passed with `npm run check`, targeted fake-intercom tests, `python3 -m unittest discover -s tests`, and `tests/run_offline.sh`.
- [2026-06-26] Issued the installed artifact sync approval request with exact target, backup path, rollback command, and validation commands.
- [2026-06-26] Hardened durable output cleanup so corrupted child records cannot make ledger cleanup remove paths outside the ledger-owned `outputs/` directory.
- [2026-06-26] Refreshed plugin validation after containment hardening; installed artifact approval remains pending.
- [2026-06-26] Operator approved the installed artifact sync for the whole plan and goal.
- [2026-06-26] Created installed artifact backup `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/backups/2026-06-26/package.bak.20260626-232520`.
- [2026-06-26] Synced `<stronk-pi-plugin>` into `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package` with package-scoped `rsync --delete`.
- [2026-06-26] Ran installed smoke through the real agent-run path and it passed.
- [2026-06-26] Ran post-sync diagnose JSON validation and it passed.
- [2026-06-26] Ran tmux orchestration smoke through a real Stronk Pi agent run and it passed.
- [2026-06-26] Completed final cleanup audit for the post-sync plan-owned runs.
- [2026-06-26] Ran a read-only Stronk Agents swarm with architect, product-designer, security-reviewer, and qa-tester roles using `fork_context=false`.
- [2026-06-26] The swarm agreed the direction is useful but required tighter public contracts, security acceptance criteria, and validation gates before implementation.
- [2026-06-26] Drafted `PLAN.md` with the accepted refinements: `wait_all`, `read_output`, `close_all`, terminal-only sanitized output handles, and optional later `promptHints`.
- [2026-06-26] Ran a final read-only execution-readiness swarm with requirements-analyst, architect, security-reviewer, and qa-tester roles using `fork_context=false`.
- [2026-06-26] Final readiness swarm returned `EXECUTION_READY=no` before hardening because open questions and path leaks would block stable TDD.
- [2026-06-26] Hardened `PLAN.md` by resolving the artifact cap, retention policy, `read_output` shape, `promptHints` scope, path hygiene preflight, `close_all` result schema, and validation gates.
- [2026-06-26] Ran a post-hardening read-only ratification swarm with requirements-analyst, security-reviewer, and qa-tester roles using `fork_context=false`.
- [2026-06-26] Post-hardening ratification returned `EXECUTION_READY=yes` from all three reviewers with no remaining blockers and no minor follow-ups.
- [2026-06-27] Started provider-capacity retry follow-up after a real Stronk Pi swarm hit upstream concurrency limits and produced unusable facade output for capacity-blocked children.
- [2026-06-27] Ran read-only Stronk Agents review with architect, qa-tester, and code-reviewer roles using `fork_context=false`.
  All three agents were closed after synthesis.
- [2026-06-27] Verified red tests for provider-capacity retry with `node --test --test-name-pattern 'capacity|revive retries capacity' test/subagent-facade.test.mjs`.
  The tests failed on the intended gaps: generic capacity failure classification, missing public retry metadata, missing `wait_all` retry aggregate fields, and no same-task capacity revive path.
- [2026-06-27] Implemented the capacity retry slice and verified `node --test test/subagent-facade.test.mjs` passed 49/49.
  Capacity failures now project structured retry metadata, avoid durable output handles, aggregate through `wait_all`, and can be retried through same-model guarded `revive` while the bridge holds the in-memory retry payload.
- [2026-06-27] Pre-refresh validation passed for the capacity retry slice:
  `node --test test/subagent-facade.test.mjs test/extension.test.mjs` reported 228/228 passing, source-mode installed smoke reported ok, `npm run check` reported 240/240 plus `security-check: ok`, `python3 -m unittest discover -s tests` reported 70/70, and `tests/run_offline.sh` passed.
- [2026-06-27] Installed artifact refresh details recorded before sync.
  Source: `/Users/eyy/Documents/Work/Dev/repos/stronk-pi-plugin/`.
  Target path: `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.
  Backup path: `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/backups/2026-06-27/package.bak.20260627-025041`.
  Sync command: `rsync -a --delete --exclude .git --exclude node_modules --exclude .DS_Store /Users/eyy/Documents/Work/Dev/repos/stronk-pi-plugin/ /Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package/`.
  Rollback command: `rsync -a --delete /Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/backups/2026-06-27/package.bak.20260627-025041/ /Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package/`.
  Validation commands: `npm run smoke:installed`, `bin/stronkpi --diagnose --json`, and targeted source tests if rollback is needed.
- [2026-06-27] Created installed artifact backup and refreshed target `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.
- [2026-06-27] Installed smoke passed after refresh with `npm run smoke:installed`.
  The smoke used `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package/src/index.mjs` and included the new deterministic capacity retry assertions plus the real agent-run path.
- [2026-06-27] Diagnose JSON passed after refresh with `ok=true`, `subagentRuntime.adapter="intercom"`, and `subagentRuntime.intercomBridgeLinked=true`.
- [2026-06-27] Tmux orchestration smoke passed through real `stronkpi --model ... --no-session -p @prompt`.
  Session: `sp-orchestration-20260627-025256`.
  Artifact: `docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/artifacts/tmux-orchestration/20260627-025256/orchestration.log`.
- [2026-06-27] Final cleanup audit after capacity retry refresh found no plan-owned tmux session, no matching runner/smoke process, and in the five most recent facade runs: 6 children, 0 open children, 0 output handles, and 0 existing durable output artifacts.

## Decisions
- [2026-06-26] Decision: keep one guarded `stronk_subagent` facade and deepen it rather than adding wrapper tools.
- [2026-06-26] Decision: use `wait_all` as the public batch wait action for this plan.
  The product-design review preferred `collect`, but architecture preferred `wait_all`; the final choice favors explicit lifecycle naming and avoids exposing both.
- [2026-06-26] Decision: `wait_all` must accept explicit current-run `childIds` only and reject duplicate, invalid, over-limit, unknown, or foreign-run IDs before waiting.
- [2026-06-26] Decision: durable full-output access must use opaque sanitized handles plus bounded `read_output`.
  Upstream temp paths must never become parent-visible contract.
- [2026-06-26] Decision: `close_all` is explicit and separate from `wait_all`.
  No implicit collect-and-close behavior is accepted for the first implementation because cleanup failures must stay visible per child.
- [2026-06-26] Decision: `promptHints` is lower priority than lifecycle and output contracts.
  If implemented, hints must be enum or length-bounded prompt-shaping fields only and recursively denied for unsafe keys.
- [2026-06-26] Decision: existing public `cwd` exposure is a P1 path hygiene bug.
  Public child results and debug outputs must not expose `cwd`, local paths, upstream temp paths, durable artifact paths, ledger artifact paths, or Stronk state roots.
- [2026-06-26] Decision: `read_output` is handle-only for P1.
  Parent agents should not need to echo `childId` back with an output handle.
- [2026-06-26] Decision: durable sanitized output artifacts use a 1 MiB UTF-8 byte cap for P1.
  If the cap is reached, truncation metadata and hashes describe only the retained sanitized artifact.
- [2026-06-26] Decision: durable sanitized output artifacts are retained only while the child remains tracked in the current facade run.
  `close` and `close_all` invalidate handles and delete the retained artifacts.
- [2026-06-26] Decision: `promptHints` is deferred to P2 and excluded from P1 smoke gates.
- [2026-06-26] Decision: `wait_all` and `close_all` return child results in requested child ID order.
  `wait_all` uses one shared deadline, not one full timeout per child.
- [2026-06-26] Decision: valid `close_all` requests return per-child close failures in the batch result instead of hiding them behind aggregate success or throwing the whole batch for one child.
- [2026-06-26] Decision: debug facade results now expose only non-path diagnostics (`debug.facadeRunId`, `projectRef`, mode, max children) because public artifact paths let parent agents follow private ledger files.
- [2026-06-26] Decision: terminal output handles are ledger-owned and retained only until close because the ledger already owns run identity, project hash, private permissions, and child lifecycle cleanup.
- [2026-06-27] Decision: capacity and concurrency provider failures are retryable lifecycle metadata, not child findings.
  Public results should expose provider-neutral retry fields and must not expose raw provider capacity prose as output.
- [2026-06-27] Decision: no automatic fallback model for capacity failures.
  Capacity retry preserves the private active parent model path and does not introduce public model, provider, fallback, or concurrency knobs.
- [2026-06-27] Decision: when provider retry timing or concurrency metadata exists, surface it as bounded metadata for next-batch retry.
  When it does not exist, `wait_all` should keep `wait_again` while other children are non-terminal, then recommend retrying capacity-blocked children after the batch drains.
- [2026-06-27] Decision: same-model retry should use guarded `revive` for capacity-blocked children with bridge-held in-memory retry payloads.
  The ledger must continue storing task hashes and byte counts, not raw task text.

## Blockers
- None active after plan hardening.
- Installed artifact sync is intentionally blocked until source implementation and tests pass and the operator explicitly approves the sync command, target path, backup path, rollback path, and validation commands.

## Resolved Questions
- [x] Durable output artifacts use a 1 MiB sanitized UTF-8 byte cap for P1.
- [x] `promptHints` is deferred to P2 and is not part of P1 implementation or smoke gates.
- [x] `read_output` is handle-only in P1.
- [x] Durable sanitized output artifacts are retained only while the child remains tracked in the current facade run and are deleted by `close` or `close_all`.
- [x] Existing public `cwd` exposure is treated as a P1 path hygiene bug, not accepted legacy behavior.

## Open Questions
- None blocking for P1 execution.

## Field Notes
- `wait_all` should aggregate existing child wait/status behavior first rather than changing bridge internals.
- Durable output handles are the highest new leak risk.
  Redaction must happen before durable write, before truncation, and before chunking.
- The current redactor should be expanded for `/var/folders`, `/private/var`, Stronk state roots, `/root`, `/etc`, and sensitive path fragments before durable handles ship.
- Aggregate tool success is not child success.
  Batch results must show failed, running, timed-out, and terminal children separately.
- Citation hygiene should be implemented as guidance first.
  Runtime enforcement can follow only if there is a crisp, testable contract.
- Implement path hygiene before `wait_all` so batch results cannot multiply current `cwd` or debug artifact path leaks.
- Use one shared sanitizer for preview and durable artifacts.
  Ledger owns private writes and should reject attempts to persist unsanitized payloads.
- Diagnose validation must assert JSON fields, not just command success.
- Source TDD verification passed: `node --test test/subagent-facade.test.mjs` in `stronk-pi-plugin` reported 44/44 passing after implementing the public path hygiene, batch wait, durable output, batch close, and guard/schema slices.
- Security reviewer flagged upstream `status.outputFile` arbitrary local file read risk.
  The bridge now only reads output files whose realpath is inside the trusted upstream async/result directories and within the size cap.
- Source package validation passed: `npm run check` in `stronk-pi-plugin` reported 235/235 passing and `security-check: ok`.
- Targeted fake-intercom validation passed: `node --test test/subagent-facade.test.mjs test/extension.test.mjs` reported 223/223 passing.
- Refreshed source package validation passed after durable-output containment hardening: `npm run check` in `stronk-pi-plugin` reported 236/236 passing and `security-check: ok`.
- Refreshed targeted fake-intercom validation passed after durable-output containment hardening: `node --test test/subagent-facade.test.mjs test/extension.test.mjs` reported 224/224 passing.
- Syntax checks passed for `scripts/installed-artifact-smoke.mjs` and `tmux-orchestration-smoke.zsh`.
- Installed artifact sync backup path: `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/backups/2026-06-26/package.bak.20260626-232520`.
- Installed artifact sync target: `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.
- Installed artifact rollback command: `/usr/bin/rsync -a --delete /Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/backups/2026-06-26/package.bak.20260626-232520/ /Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package/`.
- Installed smoke artifact: `docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/artifacts/installed-smoke/20260626-232542/installed-smoke.log`.
- Installed smoke result: `installed artifact smoke: ok (/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package/src/index.mjs)`.
- Diagnose artifact: `docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/artifacts/diagnose/20260626-233113/diagnose.json`.
- Diagnose result: `ok=true`, `pluginArtifact.installed=true`, `subagentRuntime.enabled=true`, and `subagentRuntime.intercomBridgeLinked=true`.
- Tmux smoke session: `sp-orchestration-20260626-233125`.
- Tmux smoke artifact: `docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/artifacts/tmux-orchestration/20260626-233125/orchestration.log`.
- Tmux smoke result: all required live tokens were present and no dry-run, skipped-child, mocked-worker, or no-launched-worker text was present.
- Final distribution unit rerun passed after installed smoke and tmux validation: `python3 -m unittest discover -s tests` reported 70/70 passing.
- Final cleanup audit checked post-sync facade runs `/Users/eyy/.stronk-pi/projects/d452401854ca5df6/facade-runs/facade-1782487543729-0efe3255/children.json` and `/Users/eyy/.stronk-pi/projects/7032ab83a0003dbf/facade-runs/facade-1782487886953-a19db26e/children.json`.
- Final cleanup audit result: 7 post-sync children were terminal and cleanup-verified, with zero open children, zero output handles, zero existing durable output artifacts, zero plan-owned tmux sessions, and zero live `subagent-runner` or installed-smoke processes.
- Final cleanup note: a broad historical ledger scan still shows pre-existing stale `running` or `spawned` statuses from older runs, but those rows predate this plan's approved sync, have no durable output artifacts, and had no live runner processes in the post-sync process audit.
- Distribution validation passed: `python3 -m unittest discover -s tests` in `stronk-pi` reported 70/70 passing.
- Offline/public-surface validation passed: `tests/run_offline.sh` completed unit, install, validate, update dry-run, update installed fixture, and run dry-run checks.
- Source installed-smoke validation passed without a live agent run: `STRONK_PI_SMOKE_PLUGIN=<stronk-pi-plugin>/src/index.mjs STRONK_PI_SMOKE_AGENT_RUN=0 node scripts/installed-artifact-smoke.mjs`.

## Role Routing Report
- DECISION_RECORD:
  `GOAL_CLASS=mixed`
  `PARALLEL_UNITS=4`
  `OWNERSHIP_OVERLAP=high`
  `SHARED_TOUCH=yes`
  `MODE_CHOSEN=read-only-swarm`
  `ROLE_SET=architect, product-designer, security-reviewer, qa-tester`
- `FORK_CONTEXT_USED=false`.
  Reason: user requested Stronk Agents swarm and repository policy requires default context forks off.
- Task `plan-architecture-vet`:
  `ROLE_REQUESTED=architect`
  `ROLE_USED=architect`
  `FALLBACK_USED=false`
  `AGENT_ID=019f042a-bc4e-7d01-987d-b3528d454e7e`
  `MODE=read-only`
  `WRITE_ALLOWED=false`
- Task `plan-ux-vet`:
  `ROLE_REQUESTED=product-designer`
  `ROLE_USED=product-designer`
  `FALLBACK_USED=false`
  `AGENT_ID=019f042a-bd1a-7533-bfaf-5f35f8f8c3ab`
  `MODE=read-only`
  `WRITE_ALLOWED=false`
- Task `plan-security-vet`:
  `ROLE_REQUESTED=security-reviewer`
  `ROLE_USED=security-reviewer`
  `FALLBACK_USED=false`
  `AGENT_ID=019f042a-bd85-75f0-b72c-7b5eb3b2b0fb`
  `MODE=read-only`
  `WRITE_ALLOWED=false`
- Task `plan-validation-vet`:
  `ROLE_REQUESTED=qa-tester`
  `ROLE_USED=qa-tester`
  `FALLBACK_USED=false`
  `AGENT_ID=019f042a-bdfd-7150-9257-748a7c5d4a05`
  `MODE=read-only`
  `WRITE_ALLOWED=false`

## Vetting Record
- CLAIMS:
  The proposed follow-up improvements are meaningful for day-to-day multi-child orchestration.
  The plan must pin action names, field contracts, denial rules, output-handle policy, and validation gates before implementation.
  `wait_all`, durable output handles plus `read_output`, and explicit `close_all` are the correct first wave.
- EVIDENCE:
  `{file_ref: "docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/PLAN.md:182", observation: "Existing follow-up backlog captured batch wait, durable output handles, batch close, structured metadata, and citation hygiene."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/schema.mjs:1", observation: "Current public actions are single-child lifecycle actions only."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/schema.mjs:5", observation: "Current schema recursively denies major override keys."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/ledger.mjs:101", observation: "Current public child projection is the place to add sanitized handle metadata."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/adapters/pi-subagents-bridge.mjs:16", observation: "Current public preview cap is 8192 bytes."}`
  `{file_ref: "<stronk-pi>/lib/stronk-pi-guard.py:591", observation: "Distribution guard broadly allows stronk_subagent after cwd override detection, so plugin schema must guard new fields."}`
- DONE_CRITERIA_MATCH: pass for plan creation after refinements.
- CONFIDENCE: high for plan direction; medium for exact durable artifact cap and retention policy until open questions are answered.
- DECISION: accept after plan hardening.
- NEXT_ACTION: execute this plan with TDD when the operator asks for implementation.
- CROSS_VALIDATION:
  Product-designer and architect disagreed on `collect` versus `wait_all`; the plan resolves to `wait_all` and records the tradeoff.
  Architect, security-reviewer, and qa-tester independently required explicit child ID scoping, per-child proof, and denial tests.
  Security-reviewer and qa-tester independently required redaction before durable write and invalid or foreign handle tests.
  All reviewers agreed durable full-output access must not expose local paths or raw text.

## Final Readiness Role Routing Report
- DECISION_RECORD:
  `GOAL_CLASS=planning-verification`
  `PARALLEL_UNITS=4`
  `OWNERSHIP_OVERLAP=high`
  `SHARED_TOUCH=yes`
  `MODE_CHOSEN=read-only-swarm`
  `ROLE_SET=requirements-analyst, architect, security-reviewer, qa-tester`
- `FORK_CONTEXT_USED=false`.
  Reason: user requested a final Stronk Agents swarm and repository policy requires default context forks off.
- Task `final-requirements-readiness`:
  `ROLE_REQUESTED=requirements-analyst`
  `ROLE_USED=requirements-analyst`
  `FALLBACK_USED=false`
  `AGENT_ID=019f0434-8e0f-7b62-afe9-e36c67835ca2`
  `MODE=read-only`
  `WRITE_ALLOWED=false`
- Task `final-architecture-readiness`:
  `ROLE_REQUESTED=architect`
  `ROLE_USED=architect`
  `FALLBACK_USED=false`
  `AGENT_ID=019f0434-8e81-7793-b740-6a8352200d0a`
  `MODE=read-only`
  `WRITE_ALLOWED=false`
- Task `final-security-readiness`:
  `ROLE_REQUESTED=security-reviewer`
  `ROLE_USED=security-reviewer`
  `FALLBACK_USED=false`
  `AGENT_ID=019f0434-8ef1-7b10-b0a7-15caf27eb3a8`
  `MODE=read-only`
  `WRITE_ALLOWED=false`
- Task `final-qa-readiness`:
  `ROLE_REQUESTED=qa-tester`
  `ROLE_USED=qa-tester`
  `FALLBACK_USED=false`
  `AGENT_ID=019f0434-8f6d-7981-8917-85d5cad00881`
  `MODE=read-only`
  `WRITE_ALLOWED=false`

## Final Readiness Vetting Record
- CLAIMS:
  The draft plan was directionally correct but not execution-ready before hardening.
  Stable TDD required resolving output-handle cap, retention, request shape, `promptHints` scope, `close_all` result semantics, diagnose assertions, and public path hygiene.
- EVIDENCE:
  `{file_ref: "<stronk-pi-plugin>/src/subagents/ledger.mjs:101", observation: "Current public child projection includes cwd."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/facade.mjs:104", observation: "Debug mode can add artifact paths to public results."}`
  `{file_ref: "<stronk-pi-plugin>/scripts/installed-artifact-smoke.mjs:194", observation: "Installed smoke currently enables STRONK_PI_FACADE_DEBUG=1."}`
  `{file_ref: "<stronk-pi-plugin>/src/subagents/adapters/pi-subagents-bridge.mjs:56", observation: "Current redaction is bridge-owned while ledger owns private writes, so ownership must be pinned before durable storage."}`
  `{file_ref: "docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/PLAN.md", observation: "Plan now pins path hygiene preflight, 1 MiB sanitized cap, handle-only read_output, close-time artifact cleanup, close_all result schema, and validation assertions."}`
- DONE_CRITERIA_MATCH: pass for planning readiness after hardening.
- CONFIDENCE: high for execution readiness of the plan; implementation remains unstarted.
- DECISION: accept hardened plan for TDD execution.
- NEXT_ACTION: implement the checklist from top to bottom, starting with failing path hygiene tests.
- CROSS_VALIDATION:
  Requirements and QA independently flagged unresolved output-handle cap, retention, and `read_output` shape as TDD blockers.
  Requirements and QA independently flagged `promptHints` scope ambiguity as a validation blocker.
  Architecture and security independently flagged current `cwd` exposure as incompatible with the no-local-path contract.
  Architecture and QA independently required exact `close_all` and diagnose assertions before execution.
  Security and QA independently required invalid, guessed, wrong-run, and wrong-project handle denial coverage.

## Post-Hardening Ratification Record
- CLAIMS:
  The hardened ExecPlan is execution-ready for TDD implementation.
  No P1-blocking open questions remain.
- EVIDENCE:
  Requirements ratifier found scope, non-goals, design decisions, implementation phases, validation plan, and resolved questions execution-ready.
  Security ratifier found public path hygiene, opaque handles, retention, redaction, denial rules, and installed sync approval gates execution-ready.
  QA ratifier found source tests, fake-intercom coverage, installed smoke assertions, diagnose JSON assertions, tmux smoke tokens, dry-run rejection, and cleanup audit execution-ready.
- DONE_CRITERIA_MATCH: pass for execution-ready planning state.
- CONFIDENCE: high.
- DECISION: proceed to implementation when requested, starting at the first unchecked checklist item.
- NEXT_ACTION: write failing source tests for public path hygiene and remove current `cwd` and debug artifact path leaks before adding `wait_all`.

## Cleanup Report
- Implementation session read-only swarm cleanup:
  closed `019f044d-a0cb-7131-9f4f-510e73bc4f29`, `019f044d-c32d-7c61-8a6b-b72a835ac989`, and `019f044d-e041-7482-aa74-18b1b3d74bc8` after all-complete synthesis.
  No follow-up was required.
- Closed `019f042a-bc4e-7d01-987d-b3528d454e7e` after synthesis.
- Closed `019f042a-bd1a-7533-bfaf-5f35f8f8c3ab` after synthesis.
- Closed `019f042a-bd85-75f0-b72c-7b5eb3b2b0fb` after synthesis.
- Closed `019f042a-bdfd-7150-9257-748a7c5d4a05` after synthesis.
- Confirmation wait returned `not_found` for all four agent IDs, confirming no tracked Codex subagent handles from this read-only plan-vetting swarm remained open.
- Closed `019f0434-8e0f-7b62-afe9-e36c67835ca2` after final readiness synthesis.
- Closed `019f0434-8e81-7793-b740-6a8352200d0a` after final readiness synthesis.
- Closed `019f0434-8ef1-7b10-b0a7-15caf27eb3a8` after final readiness synthesis.
- Closed `019f0434-8f6d-7981-8917-85d5cad00881` after final readiness synthesis.
- Confirmation wait returned `not_found` for all four final readiness agent IDs, confirming no tracked Codex subagent handles from this read-only final swarm remained open.
- Closed `019f043c-eb7a-7590-a80c-c80b4cae3d26` after post-hardening ratification.
- Closed `019f043c-ebe5-7d22-b0a0-2242109db717` after post-hardening ratification.
- Closed `019f043c-ec54-7b10-8bc2-09a439c2e56d` after post-hardening ratification.
- Confirmation wait returned `not_found` for all three post-hardening ratification agent IDs, confirming no tracked Codex subagent handles from this final check remained open.

## Artifacts
- Source backlog: `docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/PLAN.md`
- Source manual feedback log: `docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/LOGS.md`
