Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this revive smoke through real child runs.
If any tool result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.

1. Spawn role `executor` with this task exactly:

```text
Do not modify files.
Return exactly:
REVIVE_SOURCE_DONE=true
```

2. Wait for the source child with `timeoutMs=3600000`.
3. Revive the terminal source child with this task:

```text
Do not modify files.
Return exactly these lines:
STATUS_TOKEN=STRONK_PI_REVIVE_OK
PREVIOUS_CHILD_LINKED=true
MODEL_INHERITED=true
```

4. Verify the revive result includes `previousChildId` equal to the source `childId`, a new child id, role metadata, and a running or completed revived child.
5. Wait for the revived child with `timeoutMs=3600000`.
6. Confirm the parent-visible preview contains all three required lines.
7. Close any terminal children after synthesis.
8. Final answer must include:

```text
STATUS_TOKEN=STRONK_PI_REVIVE_OK
PREVIOUS_CHILD_LINKED=true
MODEL_INHERITED=true
```
