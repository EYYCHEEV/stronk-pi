Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this timeout recovery smoke through a real child run.
If the tool result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.

1. Spawn role `executor` with this task exactly:

```text
Do not modify files.
Run this harmless delay command before answering:
python3 -c 'import time; time.sleep(8); print("STATUS_TOKEN=STRONK_PI_TIMEOUT_RECOVERY_OK")'
Then return the printed token.
```

2. Immediately wait for the child with `timeoutMs=1000`.
3. Confirm this short wait returns a non-terminal child with `timedOut=true`, a numeric `elapsedMs`, `timeoutMs=1000`, and a non-empty `recommendedNextAction`.
4. Wait again with `timeoutMs=3600000`.
5. Confirm the parent-visible preview contains `STATUS_TOKEN=STRONK_PI_TIMEOUT_RECOVERY_OK`.
6. Close the child after it is terminal.
7. Final answer must include:

```text
STATUS_TOKEN=STRONK_PI_TIMEOUT_RECOVERY_OK
timedOut=true
recommendedNextAction=<copy observed recommendedNextAction>
```

Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN, DIAG_TOKEN, boolean proof line, alias metadata line, and recommendedNextAction line requested by the prompt. Do not replace required tokens with a prose summary.
