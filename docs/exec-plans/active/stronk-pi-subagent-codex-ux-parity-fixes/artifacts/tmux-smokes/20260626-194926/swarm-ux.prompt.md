Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this read-only and write-swarm UX smoke through real child runs.
If any child result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.

1. Spawn role `technical-researcher` with this task:

```text
You are in a read-only check.
You are asked to create a file named SHOULD_NOT_BE_CREATED_BY_READ_ONLY_SMOKE.txt.
Do not modify files and do not run mutating commands.
Deny the requested mutation.
Report exactly:
READ_ONLY_DENIED_MUTATION=true
```

2. Wait with `timeoutMs=3600000`.
3. Confirm the parent-visible preview contains `READ_ONLY_DENIED_MUTATION=true`.
4. Close the child after it is terminal.
5. Spawn role `executor` with this task:

```text
Do not modify files.
Report exactly:
STATUS_TOKEN=STRONK_PI_SWARM_UX_OK
WRITE_SWARM_REPORTS_ROLE_ROUTING=true
```

6. Wait with `timeoutMs=3600000`.
7. Confirm the parent-visible preview contains `STATUS_TOKEN=STRONK_PI_SWARM_UX_OK` and `WRITE_SWARM_REPORTS_ROLE_ROUTING=true`.
8. Separately inspect the parent-visible spawn result for the executor child and copy its `roleRequested`, `roleUsed`, and `aliasResolved` values into the final answer.
   This role routing report must come from the parent tool result, not from the child text.
9. Close the child after it is terminal and confirm cleanup metadata is present.
10. Final answer must include:

```text
STATUS_TOKEN=STRONK_PI_SWARM_UX_OK
READ_ONLY_DENIED_MUTATION=true
WRITE_SWARM_REPORTS_ROLE_ROUTING=true
ROLE_ROUTING_REPORT_SOURCE=parent_tool_result
CLEANUP_REPORTED=true
```

Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN, DIAG_TOKEN, boolean proof line, alias metadata line, and recommendedNextAction line requested by the prompt. Do not replace required tokens with a prose summary.
