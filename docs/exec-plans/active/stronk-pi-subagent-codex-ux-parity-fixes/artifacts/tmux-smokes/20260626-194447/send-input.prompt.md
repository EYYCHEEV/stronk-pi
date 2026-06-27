Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this follow-up smoke through a real child run.
If the tool result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.

1. Spawn role `executor` with this task exactly:

```text
Do not modify files.
Wait for a follow-up message before giving the final answer.
When the follow-up message contains FOLLOWUP_PING, answer exactly:
STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK
FOLLOWUP_CONSUMED=true
```

2. Immediately call `send_input` on the same child with this message:

```text
FOLLOWUP_PING
```

3. Confirm the `send_input` result has `inputAccepted=true` and `inputLinkedChildId` equal to the original `childId`.
4. Wait for the child with `timeoutMs=3600000`.
5. Confirm the parent-visible preview contains `STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK` and `FOLLOWUP_CONSUMED=true`.
6. Close the child after it is terminal.
7. Final answer must include:

```text
STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK
FOLLOWUP_CONSUMED=true
```

Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN, DIAG_TOKEN, boolean proof line, alias metadata line, and recommendedNextAction line requested by the prompt. Do not replace required tokens with a prose summary.
