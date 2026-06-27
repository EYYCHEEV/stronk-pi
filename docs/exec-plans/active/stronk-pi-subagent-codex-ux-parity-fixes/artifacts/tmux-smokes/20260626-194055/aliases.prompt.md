Use only the `stronk_subagent` tool.
Do not call the raw upstream subagent tool.

Run this alias smoke through real child runs.
If any child result indicates a mocked worker, skipped child execution, or no launched worker, stop and report failure.
This is an automated validation prompt.
The final answer must contain the literal token line `STATUS_TOKEN=STRONK_PI_ALIAS_OK`.
If that exact token line is missing, the smoke fails.

For each requested role, spawn a separate child with the listed task, wait with `timeoutMs=3600000`, then close it after it is terminal:

- Requested role `docs-scout`.
  Task: `Do not modify files. Report STATUS_TOKEN=STRONK_PI_ALIAS_OK and ALIAS_CASE=docs-scout.`
- Requested role `structure-scout`.
  Task: `Do not modify files. Report STATUS_TOKEN=STRONK_PI_ALIAS_OK and ALIAS_CASE=structure-scout.`
- Requested role `source-scout`.
  Task: `Do not modify files. Report STATUS_TOKEN=STRONK_PI_ALIAS_OK and ALIAS_CASE=source-scout.`

For every spawn result, verify that `roleRequested` equals the requested alias, `roleUsed` is the effective manifest role, and `aliasResolved=true`.

Final answer must be only these validation lines, with each observed `roleUsed` copied from the corresponding spawn result:

```text
STATUS_TOKEN=STRONK_PI_ALIAS_OK
ALIAS_CASE=docs-scout roleRequested=docs-scout roleUsed=<observed roleUsed> aliasResolved=true
ALIAS_CASE=structure-scout roleRequested=structure-scout roleUsed=<observed roleUsed> aliasResolved=true
ALIAS_CASE=source-scout roleRequested=source-scout roleUsed=<observed roleUsed> aliasResolved=true
```

Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN, DIAG_TOKEN, boolean proof line, alias metadata line, and recommendedNextAction line requested by the prompt. Do not replace required tokens with a prose summary.
