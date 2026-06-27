Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this `$repos` smoke through a real child run.
If the tool result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.

1. Spawn role `technical-researcher` with this task exactly, preserving the dollar mention:

```text
Do not modify files.
Do not run shell commands or inspect files.
Use $repos skill context only.
Report exactly these three lines:
STATUS_TOKEN=STRONK_PI_REPOS_SKILL_OK
REPOS_DIR=<copy the REPOS_DIR value from the repos skill>
QUICK_COMMAND=<copy the exact command under "List repo names only" from the repos skill>
```

2. Wait for that child to complete with `timeoutMs=3600000`.
3. Confirm the parent-visible result includes bounded `childOutputPreview` text containing `STATUS_TOKEN=STRONK_PI_REPOS_SKILL_OK`.
4. Close the child after it is terminal.
5. Final answer must include the child status, terminal result, cleanup state, and this exact token line:

```text
STATUS_TOKEN=STRONK_PI_REPOS_SKILL_OK
```
