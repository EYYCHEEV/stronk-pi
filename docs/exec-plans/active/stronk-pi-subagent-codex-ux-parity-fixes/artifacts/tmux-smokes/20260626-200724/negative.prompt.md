Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this negative failure smoke through a real child run.
If the tool result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.

1. Spawn role `executor` with this task exactly:

```text
Do not modify files.
Run a harmless command that exits with status 42.
Treat that command failure as the result of this task.
Include this marker in the final failure summary if the harness lets you summarize:
STATUS_TOKEN=STRONK_PI_NEGATIVE_FAILURE_OK
```

2. Wait for the child with `timeoutMs=3600000`.
3. Confirm the parent-visible result is a failure or actionable error, not a misleading success with empty output.
4. Confirm the result includes at least one of `status=failed`, `failureReason`, `errorSummary`, or a clearly failed tool result.
5. Close the child if the lifecycle result permits closing.
6. Final answer must include:

```text
STATUS_TOKEN=STRONK_PI_NEGATIVE_FAILURE_OK
PARENT_VISIBLE_FAILURE=true
```

Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN, DIAG_TOKEN, boolean proof line, alias metadata line, and recommendedNextAction line requested by the prompt. Do not replace required tokens with a prose summary.
