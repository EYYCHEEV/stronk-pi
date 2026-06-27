# Stronk Pi Subagent Orchestration Ergonomics

## Objective
Make multi-child Stronk Pi subagent orchestration smoother without weakening the guarded `stronk_subagent` safety boundary.

The target experience is that a parent agent can spawn several children, wait once for the set, inspect safe full output when an 8 KiB preview is not enough, close children with visible cleanup proof, and produce citation-grounded synthesis with less manual bookkeeping.

## Scope
- Remove or redact existing public path leaks in current single-child results before adding batch ergonomics.
- Add a guarded batch wait action for known children.
- Add durable redacted full-output handles and bounded chunk reads.
- Add explicit batch close ergonomics with per-child cleanup proof.
- Defer prompt-shaping metadata to a later P2 unless a separate test-backed contract is approved.
- Add citation hygiene guidance for audit and review swarms.
- Extend source tests, fake-intercom coverage, distribution guard tests, installed artifact smoke, diagnose checks, and tmux smokes for the new behavior.

## Non-Goals
- Do not expose raw upstream `subagent`.
- Do not add a second public subagent tool.
- Do not expose raw child output, `cwd`, local paths, upstream temp paths, durable artifact paths, debug artifact paths, or unbounded text.
- Do not add public model, provider, tool, skill, context, worktree, chain, background, or output override controls.
- Do not make advisory metadata look like enforced security policy.
- Do not ship `promptHints` in the P1 implementation wave.
- Do not sync installed artifacts under `~/.stronk-pi` without explicit operator approval.
- Do not commit from this plan without a separate explicit request.

## Constraints
- Use test-driven development for implementation.
- Keep the single guarded `stronk_subagent` facade.
- Keep child context fresh and `fork_context=false`.
- Keep `MAX_CHILDREN` as the batch upper bound unless a later explicit runtime setting lowers it.
- Use zsh for shell commands.
- Use rg for repository search.
- Use tmux for live Stronk Pi smokes.
- Runtime validation must use real agent-run paths, not dry-run paths.
- Before installed artifact sync, ask for explicit approval with target path, backup path, rollback path, and validation commands.
- Do not overwrite unrelated user work.

## Current Findings
- The completed parity pass made single-child lifecycle results useful through `childOutputPreview`, role metadata, timeout metadata, cleanup proof, and revive model inheritance.
- Manual real-swarm feedback found the remaining day-to-day friction is parent orchestration around multiple children.
- The current public schema exposes only single-child lifecycle actions: `spawn`, `wait`, `status`, `send_input`, `interrupt`, `close`, and `revive`.
- Current full child output is available only through upstream temp artifacts such as `${TMPDIR}/pi-subagents-uid-501/artifacts/..._output.md`.
- Those temp paths are not durable enough and must not become public parent context.
- The distribution guard currently allows `stronk_subagent` after nested `cwd` detection, so the plugin schema and facade must carry most new-field safety checks.
- Current public child projection includes `cwd`, and debug mode can return ledger artifact paths.
  Those existing path leaks must be fixed before batch results multiply them.
- Reviewers agreed the direction is sound but required pinned field contracts, path hygiene, output-handle retention policy, and validation gates before implementation.

## Design Decisions
1. First remove path leaks from existing public child projections.
   Public results must not include `cwd`, upstream temp paths, durable artifact paths, ledger artifact paths, or debug artifact paths.
   If a project identifier is needed, use an opaque non-path value such as the existing project hash.
2. Use one public batch wait verb: `wait_all`.
   Do not also expose `collect` in this plan.
   The name is explicit and matches the existing `wait` action.
3. `wait_all` accepts only explicit current-run child IDs.
   It must reject duplicate, over-limit, invalid, unknown, or foreign-run child IDs before waiting.
4. `wait_all` uses a shared batch-level deadline.
   It must not sequentially give every child the full requested timeout.
   It returns aggregate arrays and every child public result, preserving per-child status, failure, timeout, output preview, and cleanup metadata.
   Child results are returned in the same order as requested `childIds`.
5. Durable full-output access uses opaque handles plus `read_output`.
   Handles must never reveal local paths or upstream temp paths.
6. `read_output` is handle-only for P1.
   Do not require parent agents to pass `childId` back with the handle.
7. Durable output artifacts store sanitized text only.
   Redaction happens before durable write, before truncation, and before chunking.
   The first implementation uses a 1 MiB sanitized UTF-8 artifact cap.
8. Durable output artifacts are retained only while the child remains tracked in the current facade run.
   `close` and `close_all` remove the child's durable output handle and sanitized artifact.
9. `read_output` is bounded by handle, offset, and maximum character count.
   Hashes and byte counts describe sanitized output only.
10. Batch cleanup is explicit through `close_all`.
   It must return per-child cleanup proof and must not hide partial close failures behind aggregate success.
   A valid `close_all` request should return per-child close failures in the result instead of throwing for the whole batch.
11. Prompt-shaping metadata is P2 and excluded from this P1 validation set.
   If a later plan implements `promptHints`, use enum or length-bounded scalar fields only.
   Advisory fields such as read-only intent should be named `readOnlyRequested` unless they are enforced.
12. Citation hygiene belongs in docs and prompt guidance first.
   Final synthesis should regenerate file-line references from current files instead of trusting stale child citations.

## Public Contract Targets

### Public Child Projection Path Hygiene
Before adding new actions, all current and new public child projections must satisfy:

```json
{
  "childId": "sp-child-a",
  "projectRef": "opaque-project-hash-or-null",
  "cwd": null
}
```

Behavior:
- Do not include `cwd` in public tool results.
  If backward compatibility requires the key temporarily, it must be `null` or a redacted sentinel rather than a path.
- Do not include `artifacts`, ledger path maps, upstream temp artifact paths, durable output artifact paths, or Stronk state roots in public tool results, including when `STRONK_PI_FACADE_DEBUG=1`.
- Debug mode may expose non-path diagnostics such as booleans, counts, hashes, and run IDs.
- Existing ledger files need no backfill.
  New public projections must be path-clean.

### `wait_all`
Request shape:

```json
{
  "action": "wait_all",
  "childIds": ["sp-child-a", "sp-child-b"],
  "timeoutMs": 3600000
}
```

Result shape:

```json
{
  "action": "wait_all",
  "children": [],
  "terminalChildIds": [],
  "nonTerminalChildIds": [],
  "failedChildIds": [],
  "timedOut": false,
  "elapsedMs": 0,
  "timeoutMs": 3600000,
  "recommendedNextAction": null
}
```

Behavior:
- `children` contains normal public child projections.
- `children` preserves the order of requested `childIds`.
- Request validation happens before waiting begins.
  Duplicate, over-limit, invalid, unknown, and foreign-run child IDs fail closed.
- The action uses one shared deadline for the whole batch.
  It must not call single-child waits sequentially with the full timeout for each child.
- A timeout is non-terminal.
- `timedOut=true` means at least one requested child remained non-terminal at the batch deadline.
- `recommendedNextAction` is constrained to existing allowed recovery values.
- Aggregate success must not hide failed children.

### Output Handles And `read_output`
Terminal child results may include:

```json
{
  "childOutputPreview": "...",
  "childOutputTruncated": true,
  "childOutputBytes": 8192,
  "childOutputHash": "sha256-of-sanitized-preview",
  "childOutputHandle": "subagent-output-uuid",
  "childOutputFullBytes": 12598,
  "childOutputFullHash": "sha256-of-sanitized-artifact",
  "childOutputArtifactTruncated": false
}
```

Read request:

```json
{
  "action": "read_output",
  "outputHandle": "subagent-output-uuid",
  "offset": 0,
  "maxChars": 12000
}
```

Read result:

```json
{
  "action": "read_output",
  "output": {
    "handle": "subagent-output-uuid",
    "chunk": "...",
    "offset": 0,
    "nextOffset": 12000,
    "totalChars": 38120,
    "eof": false,
    "artifactTruncated": false,
    "redacted": true,
    "hash": "sha256-of-sanitized-artifact"
  }
}
```

Behavior:
- Handles are bound to child ID, facade run ID, project hash, sanitized artifact path, sanitized byte count, and sanitized hash.
- Handles are terminal-only for the first implementation.
- Sanitized artifacts live under private Stronk state with `0700` directories and `0600` files.
- Invalid, guessed, path-like, URL-like, traversal, wrong-run, or wrong-project handles are denied.
- Sanitized artifacts are capped at 1 MiB of UTF-8 bytes.
  If the cap is reached, `childOutputArtifactTruncated=true` and hashes or byte counts describe the retained sanitized artifact only.
- `offset` is a non-negative character offset into the retained sanitized artifact.
- `maxChars` defaults to `12000` and is bounded to `1..65536`.
- `offset == totalChars` returns an empty chunk with `eof=true`.
- `offset > totalChars`, negative offsets, non-integer offsets, and invalid `maxChars` values are denied.
- UTF-8 boundaries must remain valid.
- `close` and `close_all` invalidate the child's output handle and delete the retained sanitized artifact.

### `close_all`
Request shape:

```json
{
  "action": "close_all",
  "childIds": ["sp-child-a", "sp-child-b"],
  "timeoutMs": 3600000
}
```

Result shape:

```json
{
  "action": "close_all",
  "children": [],
  "closedChildIds": [],
  "failedCloseChildIds": [],
  "cleanupVerifiedChildIds": [],
  "cleanupFailedChildIds": [],
  "timedOut": false,
  "elapsedMs": 0,
  "timeoutMs": 3600000,
  "recommendedNextAction": null
}
```

Behavior:
- Close only explicit current-run child IDs.
- Return every child public result in requested `childIds` order.
- Include per-child `closeRequested`, `cleanupState`, `processLive`, and `cleanupVerified`.
- Surface partial cleanup failures clearly.
- Validation errors throw before close begins.
- Per-child upstream close failures do not make the whole batch look successful; they are captured in the child projection and failure arrays.
- A tool-level success means the request was valid and the batch close aggregation completed.
  It does not mean every child closed cleanly.

### `promptHints`
Deferred P2 possible request shape:

```json
{
  "action": "spawn",
  "role": "code-reviewer",
  "task": "...",
  "promptHints": {
    "mode": "audit",
    "ownership": "read_only",
    "expectedOutput": "findings",
    "citationStyle": "file_line",
    "requireFreshReferences": true,
    "readOnlyRequested": true
  }
}
```

Behavior:
- `promptHints` is not part of the P1 implementation or smoke gates in this plan.
- Hints shape the prompt only.
- Hints do not change bridge params for model, tools, skills, cwd, context, worktree, chain, background, or output controls.
- Hints are recursively checked by the denied-field walk.
- Freeform nested objects are denied unless a later test-backed contract proves they are safe.

## Security Acceptance Criteria
- All new actions pass through the same normalizer, denied-key walk, and unknown-key denial.
- New schema paths recursively deny `model`, `provider`, `tools`, `toolChoice`, `allowedTools`, `skills`, `skill`, `cwd`, `workingDirectory`, `context`, `fork_context`, `forkContext`, `worktree`, `chain`, `background`, `async`, `concurrency`, `output`, `outputMode`, `outputPath`, `artifactPath`, `raw`, `includeRaw`, `unredacted`, `extensions`, `packages`, `systemPrompt`, `thinking`, and secret-bearing keys.
- Batch actions accept only explicit current-run child IDs.
- Wildcard all-children behavior is denied unless later scoped strictly to the current facade run with tests.
- Public child projections and debug results expose no local paths.
  This includes existing single-child `spawn`, `wait`, `status`, `send_input`, `interrupt`, `close`, `revive` results and new `wait_all`, `read_output`, and `close_all` results.
- Durable output access returns opaque handles only.
- Redaction removes common secret patterns, key/password/token/secret assignments, local paths, `file:` URLs, `/Users`, `/home`, `/tmp`, `/var/folders`, `/private/var`, Stronk state roots, `/root`, `/etc`, and sensitive path fragments such as `.ssh`.
- No raw child output is persisted in `children.json`, `events.ndjson`, public tool results, or durable output artifacts.
- Exposed hashes and byte counts are for sanitized output only.
- Batch close returns per-child cleanup proof and must not claim verified cleanup without independent evidence.

## Implementation Phases
1. Path hygiene preflight:
   add failing tests for current public path leaks, then remove or redact `cwd` and debug artifact paths from public projections.
2. Batch wait:
   add failing tests and implement `wait_all` with explicit child ID validation, request-order results, and one shared deadline.
3. Durable output handles:
   add failing tests and implement the shared sanitizer, ledger-owned sanitized artifact storage, opaque handles, 1 MiB cap, chunked `read_output`, and handle invalidation on close.
4. Batch close:
   add failing tests and implement `close_all` with per-child cleanup proof, partial-failure visibility, and artifact cleanup.
5. Docs and validation:
   update guidance, installed smoke, diagnose assertions, tmux prompts, and final cleanup audit.

## Provider Capacity Retry Follow-up
- Detect provider capacity and concurrency failures through provider-neutral structured signals first.
  Accepted signals include HTTP status `429`, retry-after metadata, rate-limit or concurrency error codes, and bounded capacity/slot metadata.
- Use provider-neutral message matching only as fallback evidence after an upstream failure has already been observed.
  Accepted fallback phrases include rate limit, too many requests, concurrent limit, concurrency limit, no slots, slots in use, max concurrent, capacity unavailable, and temporarily overloaded.
- Do not hardcode NeuralWatt, GLM, Kimi, DeepSeek, or any provider/model name.
- Do not automatically fallback to another model.
  Retry uses the active parent model path that the bridge already forwards privately.
- Public capacity failures expose only structured metadata:
  `failureClass="provider_capacity"`, `retryable=true`, `retryReason="provider_capacity"`, optional bounded retry/concurrency counts, and `outputUsableForSynthesis=false`.
- Raw provider capacity prose is not child output.
  It must not create a `childOutputHandle`, durable output artifact, terminal output preview, or synthesis-ready text.
- `wait_all` reports retryable capacity children separately.
  If any requested child is still non-terminal, the aggregate action stays `wait_again`.
  Once the batch has drained, capacity-only failures recommend retrying those children in the next batch.
- Same-model retry uses the guarded `revive` action for capacity-blocked children when the bridge still has an in-memory retry payload.
  The ledger must not persist raw task text to enable retry.

## Task Checklist
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

## Validation Plan
- Source tests first:
  `npm run check` in `<stronk-pi-plugin>`.
- Targeted fake-intercom tests:
  `node --test test/subagent-facade.test.mjs test/extension.test.mjs` in `<stronk-pi-plugin>`.
- Distribution tests:
  `python3 -m unittest discover -s tests` in `<stronk-pi>`.
- Optional release-style offline checks:
  `tests/run_offline.sh` in `<stronk-pi>`.
- Installed artifact refresh:
  operator-approved only, with dated backup, rollback command, target path, and validation commands recorded before sync.
- Installed artifact smoke:
  `npm run smoke:installed` in `<stronk-pi-plugin>`, using real `stronkpi --no-session -p @prompt`.
  Assertions must prove real child execution, `wait_all` aggregates three children, `read_output` returns opaque chunked sanitized output, public results contain no local paths, and `close_all` reports per-child cleanup.
- Diagnose:
  `bin/stronkpi --diagnose --json` in `<stronk-pi>`.
  The JSON must parse and satisfy `ok=true`, `subagentRuntime.configured=true`, `subagentRuntime.enabled=true`, `subagentRuntime.adapter="intercom"`, `subagentRuntime.intercomBridgeLinked=true`, and pinned `pi-subagents` or `pi-intercom` package metadata where present.
- Tmux live smoke:
  use real Stronk Pi agent runs and fail on dry-run flags, skipped child execution, or dry-run-only warnings.
  The tmux runner must record session names and cleanup commands in `LOGS.md`.
- Cleanup audit:
  confirm no tracked Stronk subagent handles remain open, no plan-owned tmux sessions remain, and no durable output artifacts remain for closed children.

## Live Smoke Token Targets
- `STATUS_TOKEN=STRONK_PI_PUBLIC_PATH_REDACTION_OK`
- `NO_CWD_IN_PUBLIC_RESULT=true`
- `DEBUG_ARTIFACT_PATHS_NOT_PUBLIC=true`
- `STATUS_TOKEN=STRONK_PI_WAIT_ALL_OK`
- `WAIT_ALL_CHILDREN=3`
- `WAIT_ALL_TIMEOUT_NONTERMINAL=true`
- `WAIT_ALL_FAILURE_VISIBLE=true`
- `STATUS_TOKEN=STRONK_PI_READ_OUTPUT_OK`
- `OUTPUT_HANDLE_OPAQUE=true`
- `READ_OUTPUT_CHUNKED=true`
- `READ_OUTPUT_REDACTED=true`
- `NO_RAW_OUTPUT_PATH=true`
- `STATUS_TOKEN=STRONK_PI_BATCH_CLOSE_OK`
- `CLEANUP_REPORTED_PER_CHILD=true`
- `CLOSE_FAILURE_NOT_HIDDEN=true`
- `STATUS_TOKEN=STRONK_PI_NEGATIVE_BATCH_OK`
- `DUPLICATE_CHILD_DENIED=true`
- `FOREIGN_CHILD_DENIED=true`
- `INVALID_OUTPUT_HANDLE_DENIED=true`
- `STATUS_TOKEN=STRONK_PI_CITATION_OK`
- `FILE_LINE_RECHECKED_AT_SYNTHESIS=true`

## Resolved Questions
- [x] Durable output artifacts use a 1 MiB sanitized UTF-8 byte cap for P1.
- [x] `promptHints` is deferred to P2 and is not part of P1 implementation or smoke gates.
- [x] `read_output` is handle-only in P1.
- [x] Durable sanitized output artifacts are retained only while the child remains tracked in the current facade run and are deleted by `close` or `close_all`.
- [x] Existing public `cwd` exposure is treated as a P1 path hygiene bug, not accepted legacy behavior.

## Open Questions
- None blocking for P1 execution.
