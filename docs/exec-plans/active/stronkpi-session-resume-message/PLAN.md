# Stronk Pi Session Resume Message

## Objective

Update Stronk Pi Mono so session continuation guidance shows only the Stronk Pi wrapper command:

```text
To continue this session, run stronkpi --session <session-id>
```

The raw underlying `pi --session-dir ... --session ...` resume command must no longer be printed or treated as operator-facing guidance, because `stronkpi` owns the session directory wiring.

## Scope

- Implement the runtime message change in `/Users/eyy/Documents/Work/Dev/repos/pi-mono`.
- Keep this ExecPlan workspace in `/Users/eyy/Documents/Work/Dev/repos/stronk-pi`.
- Use the guarded `upgrade-pi` workflow to refresh the active installed Stronk Pi runtime after the code mutation is testable.
- Verify the installed `stronkpi` wrapper from a new-shell operator perspective.
- Commit and push the verified `pi-mono` change using the current branch/upstream defaults unless inspection shows that would be unsafe.

## Constraints

- Use `zsh` for shell commands.
- Use `rg` and `rg --files` for searches.
- Use `apply_patch` for manual edits.
- Do not install Pi globally or run Stow apply.
- Do not fetch, mutate, or push upstream refs except through the approved current-branch Stronk Pi Mono maintenance flow.
- Do not print secrets, tokens, raw auth output, private key paths, or credential file contents.
- If public package installs, public version changes, or unexpected cross-repo edits are needed, stop and get explicit confirmation first.
- Preserve Stronk Pi's repo-local `.mcp.json` behavior for repositories that have `.mcp-tools`; do not reintroduce generated MCP settings under `~/.stronk-pi/<project-hash>`.

## Task Checklist

- [x] Record initial repository state and confirm implementation target in `pi-mono`.
- [x] Locate the code path that emits `To continue this session` and `To resume this session` guidance.
- [x] Add or update focused tests proving only `stronkpi --session <id>` is shown.
- [x] Ensure tests fail or would fail against the old raw `pi --session-dir` guidance.
- [x] Patch the runtime message construction to use `stronkpi --session <id>` only.
- [x] Run the smallest focused test set for the changed message path.
- [x] Run the relevant `pi-mono` check and build commands.
- [x] Refresh active installed Stronk Pi artifacts with the repo-approved `upgrade-pi` command path.
- [x] Verify the installed `stronkpi` path and artifact freshness.
- [x] Run an installed-wrapper smoke check that exercises or validates session continuation guidance.
- [x] Record exact commands, outputs, and manual-test instructions in `LOGS.md`.
- [x] Commit the verified `pi-mono` change with a meaningful message.
- [x] Push the verified `pi-mono` commit to a safe remote branch after branch/upstream inspection.

## Open Questions

- [x] If the current `pi-mono` branch has no configured upstream, which remote and branch should receive the push?
  Answer: `origin` is `https://github.com/EYYCHEEV/pi-mono.git`.
  The existing remote branch `origin/stronk-pi-mono` diverged from the local branch, so the verified commit was pushed to non-overwriting branch `origin/stronk-pi-mono-session-resume-message`.
- [x] If `upgrade-pi` reports that a broader release/import step is required, should this plan expand to include distribution-manifest updates in `stronk-pi`?
  Answer: no `pi-mono` distribution-manifest update was required for the installed runtime refresh.
  The duplicate-print risk was resolved with a `pi-mono` host-owned suppression flag and a matching installed plugin fallback guard.
  A durable plugin release/import remains separate follow-up work if an immutable plugin artifact is required.
