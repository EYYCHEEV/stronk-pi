# Stronk Pi Host Home State Root Migration

## Objective
Make Stronk Pi launch with the operator's real home directory by default, so user tools behave like they do under Codex.
All Stronk Pi-owned state, sessions, logs, generated config, runtime artifacts, plugin artifacts, role artifacts, and Stronk-owned caches must live under `~/.stronk-pi`, mirroring Codex's `~/.codex` state-root model.

## Scope
- Change the launcher environment so `HOME` resolves to the real operator home, not `~/.stronk-pi/home`.
- Keep Stronk Pi state rooted at `~/.stronk-pi`.
- Make session, log, cache, runtime, role, plugin, web-search config, and subagent bridge paths explicit rather than inferred from `HOME`.
- Keep the Model Context Protocol (MCP) source of truth in the operator registry plus project `.mcp-tools`, and materialize project `.mcp.json` as the generated Claude Code-compatible artifact.
- Remove the private-home runtime model from the default launch path.
- Remove `~/.stronk-pi/home` after inventory proves no first-class Stronk-owned state still depends on it.
- Add tests and diagnostics that prove real-home tool credentials work while Stronk Pi state remains contained.
- Update operator-facing docs to describe the new split: real `HOME`, managed Stronk Pi state under `~/.stronk-pi`.

## Non-Goals
- Do not rename the state root from `~/.stronk-pi` to `~/.stronkpi`.
- Do not copy private-home contents into `/Users/eyy` or any operator home.
- Do not preserve a compatibility fallback solely for pre-release users.
- Do not globally redirect arbitrary user-tool caches into `~/.stronk-pi`.
- Do not print or persist secrets while validating `gh`, `git`, `aws`, `aliyun`, SSH, or provider credential discovery.
- Do not change public package versions or perform network installs as part of this migration.

## Constraints
- This project is still in development, so the plan should favor a clean state model over backward compatibility.
- `~/.stronk-pi` remains the canonical Stronk Pi state root.
- `HOME` must remain the operator's real home during normal `stronkpi` launches.
- Operator-set `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` may be inherited, but Stronk Pi must not synthesize either variable to point at `~/.stronk-pi/home`.
- Stronk Pi must not create normal-launch state in real-home paths such as `~/.pi`, `~/.config/pi`, `~/.local/share/pi`, or `~/.cache/pi`.
- Any upstream Pi direct `homedir()` write that would create Stronk state outside `~/.stronk-pi` must be eliminated, patched, redirected, or treated as a blocker.
- Real `HOME` is a trust-boundary choice: Pi runtime, selected MCP servers, selected skills, plugins, hooks, and subprocesses can access operator credential files and inherited credential environment during trusted launches.
- Verification must avoid printing secret values, account IDs, tokens, private key paths, credential file contents, or raw CLI auth output.
- The plan must be execution-ready before implementation starts.

## Installed Artifact Refresh Rule
Every time a Stronk Pi code mutation reaches a coherent testable checkpoint, all active installed artifacts must be refreshed so the operator can manually test from a new shell.
The exact refresh command or commands, verification evidence, installed `stronkpi` path, minimal installed-wrapper smoke result, and new-shell manual test command must be recorded in `LOGS.md`.
If the correct refresh command is unclear, discover it from repo scripts or docs before continuing implementation.

## Target State Contract
```text
~/.stronk-pi/
  config/
    defaults.toml
    roles.toml
    roles.local.toml
    role-templates/
    pi/web-search.json
  agent/
    AGENTS.md
    settings.json
    models.json
    agents/
    sessions/
    extensions/pi-intercom
    npm/node_modules/
  artifacts/
    stronk-pi-plugin-<version>/package/
  pi-fork-runtime/
  projects/<project-hash>/facade-runs/<run-id>/
  logs/
  cache/
  tmp/
```

- `HOME`: inherited operator home, for example `/Users/eyy`.
- `STRONK_PI_STATE_ROOT`: `~/.stronk-pi`.
- `PI_CODING_AGENT_DIR`: `~/.stronk-pi/agent`.
- `PI_CODING_AGENT_SESSION_DIR`: `~/.stronk-pi/agent/sessions`.
- `STRONK_PI_LOG_ROOT`: `~/.stronk-pi/logs`.
- `STRONK_PI_CACHE_ROOT`: `~/.stronk-pi/cache`.
- `STRONK_PI_TMP_ROOT`: `~/.stronk-pi/tmp`.
- Stronk Pi runtime packages: `~/.stronk-pi/pi-fork-runtime`.
- Generated MCP config: project `.mcp.json`, mode `0600`, refreshed from the operator MCP registry and project `.mcp-tools`, passed explicitly through `--mcp-config`.
- MCP registry discovery may continue to use the operator's normal MCP registry through inherited `HOME` or operator-set `XDG_CONFIG_HOME`.
- `.mcp-tools` remains a workspace selection file, not Stronk Pi state.
- `XDG_CONFIG_HOME`: inherit from the operator environment if already set; otherwise leave unset for the launched Pi process.
- `XDG_CACHE_HOME`: inherit from the operator environment if already set; otherwise leave unset for the launched Pi process.
- Stronk-owned setup/runtime package operations must use explicit state-root cache paths instead of relying on global `XDG_CACHE_HOME`.
- No required runtime path may depend on `~/.stronk-pi/home`.

## Starting Evidence
- At plan start, `harness_environment(root)` set `HOME` to `root / "home"` and `XDG_CONFIG_HOME` to `root / "home" / ".config"` in `lib/stronk-pi-guard.py`.
- At plan start, `ensure_private_pi_home_config(...)` wrote `root/home/.pi/web-search.json`.
- At plan start, `private_pi_extension_path(...)` anchored `pi-intercom` under `root/home/.pi/agent/extensions`.
- At plan start, `STRONK_PI_PRIVATE_HOME` was advertised as a control-plane environment name.
- At plan start, `config/defaults.toml` declared `private_home = "~/.stronk-pi/home"`.
- At plan start, generated MCP config was project-local via `PROJECT_GENERATED_MCP_CONFIG_RELATIVE = Path(".mcp.json")`.
- At plan start, `tests/test_mcp_doctor.py` and `tests/test_manifest_verifier.py` encoded private-home and project-local MCP behavior.
- Prior local audit found `~/.stronk-pi/home` is mostly caches, with no important private credential stores discovered.
- Real-home credential locations such as `.config/gh`, `.gitconfig`, `.ssh`, `.aws`, `.aliyun`, `.docker`, and `.kube` exist outside the private home.

## Final Evidence
- `stronkpi` now launches with inherited operator `HOME`.
- Stronk-owned config, web-search config, logs, caches, tmp, sessions, plugin artifacts, runtime artifacts, role artifacts, and intercom bridge paths are explicit under `~/.stronk-pi`.
- Generated MCP config is a project `.mcp.json` artifact for Claude Code compatibility; the source of truth remains the operator registry plus project `.mcp-tools`.
- Default runtime no longer depends on `~/.stronk-pi/home`.
- Cleanup support for obsolete `~/.stronk-pi/home` is dry-run first, fail-closed for unknown non-cache files, and applies only to known migrated Stronk-owned files or cache-like content.
- Operator-requested destructive cleanup was backed up and run against the obsolete live `~/.stronk-pi/home`; post-cleanup validation confirms that path is absent.

## Task Checklist
- [x] Inventory every current use of `root / "home"`, `private_home`, `STRONK_PI_PRIVATE_HOME`, `Path.home()`, `homedir()`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `.pi`, `.config/pi`, `.local/share/pi`, `.cache/pi`, `ensure_private_pi_home_config(...)`, `private_pi_extension_path(...)`, `PROJECT_GENERATED_MCP_CONFIG_RELATIVE`, and `LEGACY_MANAGED_RUNTIME_PATHS` across launcher code, templates, tests, docs, and bundled runtime helpers.
- [x] Classify each `Path.home()` use as acceptable operator-home behavior or migration-sensitive Stronk state behavior, and change only the migration-sensitive call sites.
- [x] Apply the target state contract exactly: logs under `~/.stronk-pi/logs`, caches under `~/.stronk-pi/cache`, runtime packages under `~/.stronk-pi/pi-fork-runtime`, web-search config under `~/.stronk-pi/config/pi`, intercom bridge under `~/.stronk-pi/agent/extensions`, sessions under `~/.stronk-pi/agent/sessions`, and generated MCP config as project `.mcp.json`.
- [x] Add failing unit tests for `harness_environment(root)` that assert launched `HOME` is the inherited operator home, operator-set `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` are not rewritten to private-home paths, and every Stronk-owned path variable resolves under the supplied state root.
- [x] Add a Fake-Pi exec test that captures child environment and argv, proving `HOME` is real home, `--session-dir` is under the state root, `--mcp-config` points under the state root, and no child-observed Stronk path depends on `~/.stronk-pi/home`.
- [x] Add a negative filesystem test that fails if normal launch creates `$HOME/.pi`, `$HOME/.config/pi`, `$HOME/.local/share/pi`, `$HOME/.cache/pi`, or `$STRONK_PI_STATE_ROOT/home`.
- [x] Refactor `harness_environment(root)` so normal launches inherit real `HOME` and explicitly set all Stronk Pi-owned path variables under `~/.stronk-pi`.
- [x] Replace bare hook/control-plane executables such as `python3` with an absolute trusted interpreter path and sanitize inherited `PATH` for hook/control-plane execution.
- [x] Preserve control-plane environment override blocking and extend validation for unapproved `STRONK_PI_*`, `STRONKPI_*`, and `PI_*` launch overrides.
- [x] Delete `private_home` from `config/defaults.toml` and remove `STRONK_PI_PRIVATE_HOME` from the control-plane environment surface once no runtime code reads them.
- [x] Move web-search config from `~/.stronk-pi/home/.pi/web-search.json` to `~/.stronk-pi/config/pi/web-search.json`.
- [x] Move the intercom bridge from `~/.stronk-pi/home/.pi/agent/extensions/pi-intercom` to `~/.stronk-pi/agent/extensions/pi-intercom`.
- [x] Generate project `.mcp.json` from the MCP registry and project `.mcp-tools`, pass it explicitly through `--mcp-config`, write it with mode `0600`, and keep `${ENV_NAME}` placeholders instead of secret values.
- [x] Harden `.mcp-tools` validation so the selection file must be a regular user-owned file, not a symlink, not group-writable, and not world-writable; report selected server names without environment values.
- [x] Add diagnostics that report `effectiveHome`, `stateRoot`, `configRoot`, `cacheRoot`, `logRoot`, `tmpRoot`, `agentDir`, `sessionDir`, `mcpConfigPath`, `intercomBridgePath`, and `blockedRealHomeWriteRisks` without printing secrets.
- [x] Add cleanup dry-run and apply behavior for obsolete `~/.stronk-pi/home`: verify no required runtime paths still point into it, use `lstat`, refuse symlink or hardlink escapes, preserve only inventory-proven first-class Stronk-owned files by moving them to first-class state-root paths, delete cache-like or obsolete contents, and never copy data into real `HOME`.
- [x] Patch or redirect any upstream Pi direct-home writes that would create `~/.pi`, `~/.config/pi`, `~/.local/share/pi`, or `~/.cache/pi` in the real home.
- [x] Add cross-repo plugin-source and installed-artifact verification because subagent ledgers and image preflight artifacts are produced by `stronk-pi-plugin` and must honor `STRONK_PI_STATE_ROOT`.
- [x] Add a post-validation canary secret scan over diagnostics, logs, sessions, generated MCP config, and ExecPlan artifacts.
- [x] Update `config/defaults.toml`, README, operator guide, architecture docs, release docs, and tests to remove private-home language and document the real-home/state-root split.
- [x] Run offline, unit, installed-wrapper, source-scan, diagnose, cleanup, and secret-safe live verification.
- [x] Reconcile this checklist with `LOGS.md` after implementation and validation.

## Validation
- `python3 -m unittest tests/test_manifest_verifier.py tests/test_mcp_doctor.py tests/test_guard_matrix.py tests/test_public_surface.py`
- `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh tests/run_offline.sh'`
- `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh tests/test_install_dry_run.sh'`
- `STRONKPI_NO_NETWORK=1 bin/stronkpi --validate-only`
- `STRONKPI_NO_NETWORK=1 bin/stronkpi --diagnose --json`
- `STRONKPI_NO_NETWORK=1 <installed-prefix>/bin/stronkpi --validate-only`
- After every coherent code checkpoint, run the discovered installed-artifact refresh command, verify the installed `stronkpi` path is refreshed, and run a minimal installed-wrapper smoke check.
- Fake-Pi launch test asserts `HOME` is the operator home, Stronk paths resolve under the test state root, and generated MCP config resolves to project `.mcp.json`.
- Fake-Pi launch test asserts no `~/.pi`, `~/.config/pi`, `~/.local/share/pi`, `~/.cache/pi`, or `~/.stronk-pi/home` is created during normal launch.
- Diagnose JSON must report real `effectiveHome`, state-root-contained `stateRoot`, `configRoot`, `cacheRoot`, `logRoot`, `tmpRoot`, `agentDir`, `sessionDir`, and `intercomBridgePath`, plus project `.mcp.json` in `mcpConfigPath`.
- Source scan must find no default-runtime references to `~/.stronk-pi/home`, `private_home`, `STRONK_PI_PRIVATE_HOME`, `home/.pi`, or `root / "home"` outside explicit cleanup tests or historical docs marked as legacy.
- Fake PATH injection test proves hook command JSON uses the expected absolute interpreter, not a workspace-provided `python3`.
- MCP tests reject symlinked, group-writable, world-writable, or non-user-owned `.mcp-tools`; generated config is `0600` and contains placeholders only.
- Cleanup command tests cover dry-run, successful removal, fail-closed symlink and hardlink escapes, and fail-closed behavior when obsolete `~/.stronk-pi/home` contains unknown non-cache files.
- Canary secret test seeds fake environment tokens and fake credential files, then verifies no canary appears in diagnostics, sessions, logs, generated configs, or artifacts.
- Plugin checks verify subagent ledger and image-preflight artifacts honor `STRONK_PI_STATE_ROOT` in source and installed-artifact contexts.
- Secret-safe live smoke checks assert `gh auth status`, `git config --global`, `aws configure list`, `aliyun configure list`, and SSH config parsing can discover config from the real home while redirecting stdout/stderr and recording only pass/fail.

## Open Questions
- [x] None for the state model.
