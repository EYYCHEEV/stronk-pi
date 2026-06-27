# Stronk Pi Subagent Orchestration Ergonomics Live Smoke

Use only the `stronk_subagent` tool.
Do not call the raw upstream `subagent` tool.
Do not set `fork_context`, `forkContext`, `cwd`, `model`, `tools`, `skills`, `output`, `outputPath`, `includeRaw`, or `unredacted`.
Do not modify files.
This smoke must exercise real Stronk Pi child agent execution.
If a result indicates a mocked worker, skipped child execution, dry-run-only completion, or no launched worker, stop and report failure.

1. Spawn three role `executor` children.
   Child A must complete with a long output containing `STATUS_TOKEN=STRONK_PI_PUBLIC_PATH_REDACTION_CHILD`, the fake local path `/tmp/stronk-pi-should-redact`, `password=supersecret123`, and enough filler text to require chunked full-output reading.
   Child B must remain non-terminal for at least 30 seconds before returning `STATUS_TOKEN=STRONK_PI_WAIT_ALL_RUNNING_CHILD_DONE`.
   Child C must complete with a clearly visible failed finding, for example `FAILED_CHILD_VISIBLE=true`.
2. Call `wait_all` for the three child IDs with `timeoutMs=1000` before Child B finishes.
   Confirm the batch result has exactly three children in request order, reports a non-terminal timeout for Child B, and makes Child C's failure visible.
   Confirm the public result has no `cwd`, no raw local paths, and no debug artifact paths.
3. Use `read_output` on Child A's `childOutputHandle` with at least two chunks.
   Confirm the handle is opaque, the chunked output is redacted, and no raw output path is visible.
4. Call `close_all` on all three child IDs.
   Confirm per-child cleanup reporting is visible.
   Confirm close failure reporting arrays are visible and would not hide a failure, even if this real run closes all children successfully.
5. Run negative checks through `stronk_subagent`.
   A duplicate child ID in `wait_all` must be denied.
   A foreign child ID in `wait_all` must be denied.
   An invalid `read_output` handle must be denied.
6. If you cite a file or line, re-check it against the current file at synthesis time.
7. Final answer must include exactly these lines:

```text
STATUS_TOKEN=STRONK_PI_PUBLIC_PATH_REDACTION_OK
NO_CWD_IN_PUBLIC_RESULT=true
DEBUG_ARTIFACT_PATHS_NOT_PUBLIC=true
STATUS_TOKEN=STRONK_PI_WAIT_ALL_OK
WAIT_ALL_CHILDREN=3
WAIT_ALL_TIMEOUT_NONTERMINAL=true
WAIT_ALL_FAILURE_VISIBLE=true
STATUS_TOKEN=STRONK_PI_READ_OUTPUT_OK
OUTPUT_HANDLE_OPAQUE=true
READ_OUTPUT_CHUNKED=true
READ_OUTPUT_REDACTED=true
NO_RAW_OUTPUT_PATH=true
STATUS_TOKEN=STRONK_PI_BATCH_CLOSE_OK
CLEANUP_REPORTED_PER_CHILD=true
CLOSE_FAILURE_NOT_HIDDEN=true
STATUS_TOKEN=STRONK_PI_NEGATIVE_BATCH_OK
DUPLICATE_CHILD_DENIED=true
FOREIGN_CHILD_DENIED=true
INVALID_OUTPUT_HANDLE_DENIED=true
STATUS_TOKEN=STRONK_PI_CITATION_OK
FILE_LINE_RECHECKED_AT_SYNTHESIS=true
```
