# Project Log: Stronk Pi Subagent Codex Parity Audit
Created: 2026-06-26T15:10:00+08:00
Plan: ./PLAN.md
Workspace: docs/exec-plans/active/stronk-pi-subagent-codex-parity-audit/

## Progress
- [x] Create the active exec-plan workspace for this audit.
- [x] Locate relevant historical exec-plans and commits.
- [x] Run a read-only subagent swarm to audit architecture, runtime behavior, and parity expectations.
- [x] Cross-validate findings against local files and live diagnostics.
- [x] Record audit findings in `LOGS.md`.
- [x] Report final verdict and next recommended fixes.

## Session History
- [2026-06-26] Created the active audit workspace and began the parity investigation.
- [2026-06-26 15:10 +08] Spawned four read-only Codex audit agents with `fork_context=false`: history audit, architecture contract audit, code scan, and live runtime QA.
- [2026-06-26 15:27 +08] Reproduced the failing live path in tmux.
  Parent used DeepSeek, but the child session used Kimi and failed with an account error.
  The same child prompt still contained the `$repos` skill block, proving skill injection was not the failing component.
- [2026-06-26 15:35 +08] Applied the parent-model propagation fix to the Stronk Pi plugin source and synced the installed artifact after backing it up.
- [2026-06-26 15:35 +08] Reran the tmux smoke.
  The child completed, returned the `$repos` values, and was closed by the parent.
- [2026-06-26 15:39 +08] Fixed Stronk Pi diagnose so the private `pi-intercom` symlink is inspected instead of reported as hard-coded false.
- [2026-06-26] Ran a second read-only Stronk Agents swarm focused on full Codex-vs-Stronk-Pi UX parity.
  Roles: `architect`, `technical-researcher`, `qa-tester`, and `critic`.
  All four used `fork_context=false`, completed, and were closed.

## Decisions
- [2026-06-26] Decision: keep this workspace minimal because the repo already has `docs/exec-plans/` directories and the user asked for a new plan for this audit, not repo-wide ExecPlan governance edits.
- [2026-06-26] Decision: propagate the active parent model as a private runtime hint from the registered `stronk_subagent` tool execution context.
  Keep user-supplied `model` denied by the public schema.
- [2026-06-26] Decision: do not change upstream `pi-subagents`.
  Its public schema already supports `model`, and the gap was in the Stronk facade bridge request.
- [2026-06-26] Decision: treat `docs/exec-plans/active/` as an internal workspace for the public-surface test.
  Active plans can contain local evidence and should not be scanned as distribution-facing docs.
- [2026-06-26] Decision: do not claim full Codex parity yet.
  The `$repos` smoke path is green, but the full user experience still differs materially in result visibility, tool ergonomics, alias transparency, recovery metadata, cleanup proof, and untested intercom/revive flows.

## Blockers
- None remaining for the audited `$repos` smoke path.
- Full Codex-like UX parity is blocked on the backlog below.

## Open Questions
- [x] Should role aliases like `docs-scout` remain silent aliases, or should Stronk Pi expose alias resolution explicitly to match Codex ergonomics?
  Answer: silent aliasing is acceptable for now because it fixes the observed denied-role failure without exposing more public surface.
- [x] Should Stronk Pi eventually support Codex-style native `$skill` injection inside child agents beyond role frontmatter and `STRONK_PI_SKILL_ROOTS`?
  Answer: the live smoke proves child skill injection works for `$repos` through the current Stronk plugin prompt path.
  No immediate child-skill architectural change is required for this failure.

## Field Notes
- Read-only swarm summary:
  - Role routing and generated role files are present.
  - `pi-subagents@0.22.0` and `pi-intercom@0.6.0` are installed.
  - Parent `$repos` skill discovery and prompt injection work.
  - The failing session was caused by child model fallback, not missing intercom or missing skill injection.
  - All audit subagents were closed after synthesis.
  - `FORK_CONTEXT_USED=false` for every audit subagent.
- Source changes in `stronk-pi-plugin`:
  - `src/subagents/facade.mjs` accepts a private `parentModelProvider` and passes runtime hints to adapter spawn and revive paths.
  - `src/subagents/adapters/pi-subagents-bridge.mjs` includes `model` in upstream `pi-subagents` spawn params when the parent model is known.
  - `src/index.mjs` wires the registered `stronk_subagent` tool execution context into the facade through `activeModelRef`.
  - Tests assert user-supplied `model` is still denied.
  - Tests assert registered intercom facade forwards active model context to the child spawn request.
- Source changes in `stronk-pi`:
  - `lib/stronk-pi-guard.py` now inspects whether the private `pi-intercom` bridge symlink points at the installed package.
  - `tests/test_mcp_doctor.py` covers linked bridge reporting.
  - `tests/test_public_surface.py` excludes active exec-plan workspaces from public distribution surface scanning.
- Installed artifact sync:
  - Synced `src/index.mjs`, `src/subagents/facade.mjs`, and `src/subagents/adapters/pi-subagents-bridge.mjs` into the installed Stronk Pi plugin artifact.
  - Backup directory: `/Users/eyy/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/backups/2026-06-26/153523-subagent-model-propagation`.
- Live tmux smoke:
  - tmux session: `sp-repos-parity-153539`.
  - Parent session: `/Users/eyy/.stronk-pi/agent/sessions/2026-06-26T07-35-39-586Z_019f02db-1342-7e9b-bab7-f7b529d9694f.jsonl`.
  - Child session: `/Users/eyy/.stronk-pi/agent/sessions/2026-06-26T07-35-39-586Z_019f02db-1342-7e9b-bab7-f7b529d9694f/dbba2ca6/run-0/session.jsonl`.
  - Child model: `deepseek/deepseek-v4-pro`.
  - Child status: `completed`.
  - Child exit code: `0`.
  - Child output:
    ```text
    STATUS_TOKEN=STRONK_PI_REPOS_SKILL_OK
    REPOS_DIR=/Users/eyy/Documents/Work/Dev/repos
    QUICK_COMMAND=bash ~/.agents/skills/repos/scripts/list_repos.sh --name-only
    ```
- Diagnostics:
  - `stronkpi --diagnose --json` returns `ok: true`.
  - `subagentRuntime.enabled` is `true`.
  - `subagentRuntime.intercomBridgeLinked` is `true`.
- Full parity swarm verdict:
  - `architect` accepted the baseline: Codex uses native lifecycle primitives, exact semantic roles, 60-minute waits, close-after-synthesis cleanup, model-configured roles, all-complete barriers, and explicit vetting.
  - `technical-researcher` mapped Stronk Pi current behavior: guarded `stronk_subagent` schema, manifest-backed silent aliases, generated Pi roles, pinned `pi-subagents` and `pi-intercom`, active parent model propagation, prompt-time skill injection, ledger-backed lifecycle, and six-child active cap.
  - `qa-tester` marked `$repos` injection, model inheritance, wait/close lifecycle, and diagnose as pass.
    It marked role alias, `send_input`, and `revive` live parity as unknown, and error handling as fail because an earlier provider failure was visible in the child log while parent-facing status still became `completed`.
  - `critic` rejected full UX parity today.
    It identified parent-visible child output and lifecycle ergonomics as P0 issues.
- Codex-vs-Stronk-Pi parity matrix:
  - Lifecycle primitives:
    Codex exposes native `spawn_agent`, `wait`, `send_input`, and `close_agent`.
    Stronk Pi exposes a single guarded `stronk_subagent` JSON action tool.
    Parity target: either add Codex-shaped wrapper tools or strengthen tool guidance and output shape so use feels native.
  - Role routing:
    Codex uses exact semantic role names as `agent_type`.
    Stronk Pi allows canonical generated roles plus silent aliases.
    Parity target: return `roleRequested`, `roleUsed`, and `aliasResolved`.
  - Child output:
    Codex subagent completion returns usable final text to the orchestrator.
    Stronk Pi public child output currently exposes `terminalResult`, hash, and bytes, but not bounded text.
    Parity target: return bounded redacted `terminalOutput` or `summary` in `publicChild`.
  - Context and skills:
    Codex skill loading is first-class in the parent thread.
    Stronk Pi uses prompt-time skill injection and child fresh context.
    Parity target: keep fresh context for safety, but make skill propagation behavior explicit and smoke-tested.
  - Model inheritance:
    Codex role/model behavior is configured by role and inherited runtime.
    Stronk Pi now forwards active parent model privately to live child spawn.
    Parity status: pass for the `$repos` smoke.
  - Wait and close:
    Codex expects long waits, non-terminal timeouts, and immediate cleanup of completed children.
    Stronk Pi polls until terminal or timeout and records ledger cleanup state.
    Parity target: add `timedOut`, `elapsedMs`, recovery hint, `processLive`, and verified cleanup metadata.
  - Error handling:
    Codex-like behavior should surface child failure clearly to the parent.
    Stronk Pi needs a negative smoke and likely bridge logic changes so upstream child errors do not present as successful completion with empty output.
  - Diagnostics:
    Stronk Pi has better explicit runtime package diagnostics than Codex, and diagnose is now accurate for the intercom bridge link.
- Prioritized parity backlog:
  - P0: Add bounded redacted child output to parent-facing `child` results.
  - P0: Provide Codex-shaped lifecycle ergonomics through wrapper tools or stronger prompt/tool guidance.
  - P1: Expose alias resolution metadata on spawn and optionally a roles/aliases discovery action.
  - P1: Add explicit timeout metadata and recovery hints to wait/spawn bridge failures.
  - P1: Verify cleanup after close and report process/upstream state.
  - P1: Add live tmux smokes for role aliases, `send_input`, `revive`, and negative child failure/error surfacing.
  - P2: Expose progress/current tool information through status for long-running children.
  - P2: Decide output preview size: 8 KiB, 16 KiB, or artifact handle plus preview.
- Vetting record:
  - Claims accepted:
    `$repos` smoke path passes; parent model inheritance is fixed; diagnose reports the intercom bridge accurately; the public schema denies unsafe user overrides.
  - Claims rejected for full parity:
    current UX is not identical enough to Codex because child result text is not parent-visible, role aliasing is silent, timeout metadata is thin, cleanup proof is limited, and live `send_input` or `revive` parity is unproven.
  - Cross-validation:
    all four subagents agree on the model-inheritance fix and `$repos` pass.
    `critic` and `qa-tester` agree that full parity remains incomplete.
    `architect` and `technical-researcher` agree that a constrained facade is the safety boundary and should not become a raw upstream pass-through.
  - Independent checks:
    `src/subagents/ledger.mjs` `publicChild` exposes result status/hash/bytes but no output text.
    `src/subagents/facade.mjs` maps aliases silently.
    `src/subagents/adapters/pi-subagents-bridge.mjs` wait returns the child without explicit timeout metadata.
    `src/subagents/schema.mjs` denies user override fields including `model`, `tools`, and `skills`.
  - Decision: accept narrow smoke fix, reject full parity claim, proceed with parity backlog.
  - Cleanup: all four subagents were closed after synthesis.

## Artifacts
- `tmux-repos-skill-smoke.prompt.md`
- `tmux-repos-skill-smoke.zsh`

## Client Feedback
