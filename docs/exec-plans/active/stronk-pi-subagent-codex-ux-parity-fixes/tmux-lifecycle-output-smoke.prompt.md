Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this lifecycle smoke through a real child run.
If the tool result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.

1. Spawn role `executor` with this task exactly:

```text
Do not modify files.
Return exactly these lines and no extra prose:
STATUS_TOKEN=STRONK_PI_LIFECYCLE_OK
CHILD_FINDING=parent can synthesize from bounded preview
```

2. Wait for the child with `timeoutMs=3600000`.
3. Inspect the parent-visible tool result.
Confirm that the completed child result includes `childOutputPreview`, `childOutputTruncated`, `childOutputBytes`, `childOutputHash`, `roleRequested`, `roleUsed`, `aliasResolved`, `isTerminal`, and `recommendedNextAction`.
4. Close the child after it is terminal.
Confirm the close result includes `closeRequested`, `cleanupState`, `upstreamState`, `processLive`, and `cleanupVerified`.
5. Final answer must include exactly these lines, plus the observed child status and cleanup state:

```text
STATUS_TOKEN=STRONK_PI_LIFECYCLE_OK
TERMINAL_OUTPUT_PREVIEW_SEEN=true
CLOSED=true
```
