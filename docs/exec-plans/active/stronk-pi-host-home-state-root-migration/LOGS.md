# Project Log: Stronk Pi Host Home State Root Migration
Created: 2026-06-27T14:05:25+0800
Plan: ./PLAN.md
Workspace: docs/exec-plans/active/stronk-pi-host-home-state-root-migration/

## Progress
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

## Session History
- [2026-06-27] Created the initial exec-plan from the current chat context and prior read-only swarm findings.
- [2026-06-27] Refined the plan after a five-agent read-only swarm rejected the first draft as not execution-ready.
- [2026-06-27] Ran a second read-only swarm against the refined plan; architecture, security, QA, and critic roles accepted it as execution-ready.
- [2026-06-27] Started end-to-end execution and added the mandatory installed-artifact refresh rule to PLAN.md before implementation.
- [2026-06-27] Completed bounded inventory and `Path.home()` classification before code mutation.
- [2026-06-27] Completed first implementation checkpoint for real-home launcher env, state-root web-search/intercom/MCP paths, `.mcp-tools` hardening, diagnostics, cleanup command, and focused tests.
- [2026-06-27] Completed second implementation checkpoint for cleanup CLI tests, canary diagnostics tests, source-scan gate, plugin source/installed-artifact checks, stale project-MCP helper removal, and operator documentation updates.
- [2026-06-27] Completed third implementation checkpoint for fail-closed cleanup handling of obsolete private-home legacy agent logs and sessions.
- [2026-06-27] Completed full validation and reconciled PLAN.md and LOGS.md.
- [2026-06-27] Operator explicitly requested destructive cleanup; backed up and removed the live obsolete `~/.stronk-pi/home` directory, then verified `stronkpi` still validates and diagnoses cleanly.
- [2026-06-27] User clarified that generated MCP config should materialize as project `.mcp.json` for Claude Code compatibility; updated implementation, tests, docs, and installed artifacts.

## Decisions
- [2026-06-27] Decision: Make real `HOME` the default because Stronk Pi should behave like Codex for user tools and credentials.
- [2026-06-27] Decision: Keep all Stronk Pi-owned state under `~/.stronk-pi` because it mirrors the Codex `~/.codex` state-root model.
- [2026-06-27] Decision: Do not preserve the private-home runtime model for backward compatibility because Stronk Pi is still in development and the user explicitly prefers a clean migration.
- [2026-06-27] Decision: Inherit operator `XDG_CONFIG_HOME` only when already set and otherwise leave it unset for launched Pi because Stronk Pi-owned paths are explicit and user tools should see normal home behavior.
- [2026-06-27] Decision: Inherit operator `XDG_CACHE_HOME` only when already set and otherwise leave it unset for launched Pi because arbitrary user-tool caches should not be globally redirected.
- [2026-06-27] Decision: Scope Stronk-owned setup and runtime package caches to `~/.stronk-pi/cache` because Stronk caches should stay in the state root without changing every user tool's cache behavior.
- [2026-06-27] Superseded decision: Initially moved generated MCP config under `~/.stronk-pi/generated/mcp/<project-hash>.json`.
- [2026-06-27] Decision: Generate project `.mcp.json` and pass it explicitly with `--mcp-config` because the operator wants Claude Code-compatible project discovery; the source of truth remains the MCP registry plus `.mcp-tools`.
- [2026-06-27] Decision: Keep `.mcp-tools` as a workspace selection file because it is project intent, not Stronk Pi runtime state.
- [2026-06-27] Decision: Delete `~/.stronk-pi/home` after verification instead of preserving it for compatibility because the user rejected backward compatibility and rollback for the private-home model.
- [2026-06-27] Decision: Treat real `HOME` as a trusted-workspace boundary because selected MCP servers, skills, plugins, hooks, and subprocesses can access operator credential files unless separately sandboxed.
- [2026-06-27] Decision: Verify `stronk-pi-plugin` source and installed artifacts because plugin-produced subagent and image-preflight artifacts must honor `STRONK_PI_STATE_ROOT`.
- [2026-06-27] Decision: Start implementation from the refined plan because second-pass architecture, security, QA, and critic reviews all accepted the plan with residual implementation risks only.
- [2026-06-27] Decision: Refresh all active installed artifacts after every coherent Stronk Pi code mutation checkpoint because the operator must be able to manually test the current implementation from a new shell.

## Blockers
<!-- Format: [YYYY-MM-DD HH:MM] Description -->

## Open Questions
- [x] None for the state model.

## Field Notes
- Installed artifact refresh evidence will be recorded after each coherent code checkpoint, including exact command, installed path, smoke result, and manual new-shell test command.
- Inventory found production private-home anchors in `lib/stronk-pi-guard.py`: `LEGACY_MANAGED_RUNTIME_PATHS`, `CONTROL_PLANE_ENV_NAMES`, `PROJECT_GENERATED_MCP_CONFIG_RELATIVE`, `ensure_private_pi_home_config(...)`, `private_pi_extension_path(...)`, `inspect_mcp_adapter_runtime(...)`, `prepare_mcp_adapter_runtime(...)`, `inspect_subagent_runtime(...)`, `harness_environment(...)`, and related launcher argument assembly.
- Inventory found stale private-home assertions in `tests/test_manifest_verifier.py` and `tests/test_mcp_doctor.py`, plus documentation references in README, operator guide, architecture docs, and release docs.
- `Path.home()` classification: acceptable operator-home behavior includes default state-root resolution, operator MCP registry discovery, Codex role discovery, default dangerous-command hook discovery, personal-path redaction comparison, skill-root discovery, and installer prefix default.
- `Path.home()` classification: migration-sensitive behavior is the launcher-private-home model in `harness_environment(...)`, which must stop rewriting `HOME` and `XDG_CONFIG_HOME`.
- No production `homedir()` call sites were found in the bounded repo scan.
- Focused checkpoint validation passed: `python3 -m unittest tests/test_manifest_verifier.py` ran 36 tests; `python3 -m unittest tests/test_mcp_doctor.py` ran 21 tests.
- Installed artifact refresh checkpoint 1 command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh ./install.sh --prefix "$HOME/.local"'`.
- Runtime config refresh checkpoint 1 command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi-setup refresh-config --json'`.
- Installed path checkpoint 1 evidence: `zsh -lc 'SHELL=zsh command -v stronkpi; test -x "$HOME/.local/bin/stronkpi"; "$HOME/.local/bin/stronkpi" --version'` reported `/Users/eyy/.local/bin/stronkpi` and `stronkpi 0.1.0`.
- Installed-wrapper smoke checkpoint 1 evidence: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh "$HOME/.local/bin/stronkpi" --validate-only >/tmp/stronkpi-installed-validate.log && printf "%s\n" installed-validate-ok'` passed.
- Source-wrapper smoke checkpoint 1 evidence: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi --validate-only >/tmp/stronkpi-source-validate.log && printf "%s\n" source-validate-ok'` passed.
- New-shell manual test command after checkpoint 1: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --validate-only && stronkpi --diagnose --json >/tmp/stronkpi-diagnose.json'`.
- Focused checkpoint 2 validation passed: `python3 -m py_compile lib/stronk-pi-guard.py tests/test_manifest_verifier.py tests/test_mcp_doctor.py tests/test_public_surface.py tests/test_plugin_state_root.py` and `python3 -m unittest tests/test_manifest_verifier.py tests/test_mcp_doctor.py tests/test_public_surface.py tests/test_plugin_state_root.py` ran 67 tests with one expected skip for the minimal fixture tarball.
- Installed artifact refresh checkpoint 2 command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh ./install.sh --prefix "$HOME/.local"'`.
- Runtime config refresh checkpoint 2 command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi-setup refresh-config --json'`.
- Runtime config refresh checkpoint 2 evidence: `changedCount` was `0`, `stateRoot` was `/Users/eyy/.stronk-pi`, and the command reported `ok: true`.
- Installed path checkpoint 2 evidence: `zsh -lc 'SHELL=zsh command -v stronkpi; test -x "$HOME/.local/bin/stronkpi"; "$HOME/.local/bin/stronkpi" --version'` reported `/Users/eyy/.local/bin/stronkpi` and `stronkpi 0.1.0`.
- Installed-wrapper smoke checkpoint 2 evidence: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh "$HOME/.local/bin/stronkpi" --validate-only >/tmp/stronkpi-installed-validate-checkpoint2.log && printf "%s\n" installed-validate-ok'` passed.
- Source-wrapper smoke checkpoint 2 evidence: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi --validate-only >/tmp/stronkpi-source-validate-checkpoint2.log && printf "%s\n" source-validate-ok'` passed.
- New-shell manual test command after checkpoint 2: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --validate-only && stronkpi --diagnose --json >/tmp/stronkpi-diagnose.json'`.
- Focused checkpoint 3 validation passed: `python3 -m unittest tests/test_manifest_verifier.py` ran 38 tests and covered legacy `.agents`, `.claude`, and `.codex` cleanup handling.
- Installed artifact refresh checkpoint 3 command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh ./install.sh --prefix "$HOME/.local"'`.
- Runtime config refresh checkpoint 3 command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi-setup refresh-config --json'`.
- Runtime config refresh checkpoint 3 evidence: `changedCount` was `0`, `stateRoot` was `/Users/eyy/.stronk-pi`, and the command reported `ok: true`.
- Installed path checkpoint 3 evidence: `zsh -lc 'SHELL=zsh command -v stronkpi; test -x "$HOME/.local/bin/stronkpi"; "$HOME/.local/bin/stronkpi" --version'` reported `/Users/eyy/.local/bin/stronkpi` and `stronkpi 0.1.0`.
- Installed-wrapper smoke checkpoint 3 evidence: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh "$HOME/.local/bin/stronkpi" --validate-only >/tmp/stronkpi-installed-validate-checkpoint3.log && printf "%s\n" installed-validate-ok'` passed.
- Source-wrapper smoke checkpoint 3 evidence: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi --validate-only >/tmp/stronkpi-source-validate-checkpoint3.log && printf "%s\n" source-validate-ok'` passed.
- New-shell manual test command after checkpoint 3: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --validate-only && stronkpi --diagnose --json >/tmp/stronkpi-diagnose.json'`.
- Final unit validation passed: `python3 -m unittest tests/test_manifest_verifier.py tests/test_mcp_doctor.py tests/test_guard_matrix.py tests/test_public_surface.py tests/test_release_scripts.py tests/test_plugin_state_root.py` ran 82 tests with one expected skip for the minimal fixture tarball.
- Final offline validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh tests/run_offline.sh'` ran the offline suite, install/update dry-run and apply against temporary homes, `stronkpi --validate-only`, `stronkpi --diagnose --json`, and negative filesystem checks.
- Final install dry-run validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh tests/test_install_dry_run.sh'`.
- Final source validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi --validate-only >/tmp/stronkpi-source-final2-validate.log && printf "%s\n" source-final-validate-ok'`.
- Final source diagnose validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi --diagnose --json >/tmp/stronkpi-source-final2-diagnose.json && printf "%s\n" source-final-diagnose-ok'`.
- Superseded final diagnose invariant check passed before the MCP artifact location reversal: `effectiveHome=/Users/eyy`, `stateRoot=/Users/eyy/.stronk-pi`, and `mcpConfigPath=/Users/eyy/.stronk-pi/generated/mcp/7032ab83a0003dbf.json`.
- Final installed-wrapper validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh "$HOME/.local/bin/stronkpi" --validate-only >/tmp/stronkpi-installed-final2-validate.log && printf "%s\n" installed-final-validate-ok'`.
- Final source-scan gate passed: `python3 -m unittest -v tests.test_public_surface.PublicSurfaceTests.test_no_default_runtime_private_home_markers`.
- Final canary gate passed: `python3 -m unittest -v tests.test_manifest_verifier.ManifestVerifierTests.test_diagnose_does_not_persist_or_print_canary_secrets`.
- Final plugin gate passed: `python3 -m unittest -v tests.test_plugin_state_root`; source and active installed artifact checks passed, and only the minimal manifest fixture artifact test was skipped.
- Secret-safe live discovery probes completed with raw output redirected under `/tmp/stronkpi-live-smoke`: `gh auth status`, `git config --global --list`, `aws configure list`, `aliyun configure list`, and `ssh -G github.com` all exited `0`.
- Initial installed cleanup dry-run verification used `zsh -lc 'SHELL=zsh STRONKPI_NO_NETWORK=1 stronkpi-setup cleanup-private-home --dry-run --json >/tmp/stronkpi-cleanup-final-installed.json 2>/tmp/stronkpi-cleanup-final-installed.err; code=$?; printf "cleanup-dry-run-exit:%s\n" "$code"; if [ "$code" -eq 0 ] || [ "$code" -eq 1 ]; then exit 0; fi; exit "$code"'` and reported `cleanup-dry-run-exit:1`.
- Initial cleanup dry-run exit `1` was fail-closed because the operator's live obsolete private home contained non-Stronk-owned user-tool state.
- Superseded final live-state check confirmed installed wrappers exist, `~/.stronk-pi/config/pi/web-search.json`, `~/.stronk-pi/generated/mcp`, and `~/.stronk-pi/agent/sessions` exist, and real-home negative paths `~/.pi`, `~/.config/pi`, `~/.local/share/pi`, and `~/.cache/pi` are absent.
- Destructive cleanup backup command created `/Users/eyy/.stronk-pi/backups/2026-06-27/home.bak.20260627-154202.tgz`.
- Guarded cleanup apply command `zsh -lc 'SHELL=zsh STRONKPI_NO_NETWORK=1 stronkpi-setup cleanup-private-home --apply --json >/tmp/stronkpi-cleanup-apply.json 2>/tmp/stronkpi-cleanup-apply.err; code=$?; printf "cleanup-apply-exit:%s\n" "$code"; exit 0'` reported `cleanup-apply-exit:1`.
- Because the operator explicitly requested destructive cleanup after backup, direct guarded-path removal command verified the target was exactly `~/.stronk-pi/home`, refused symlinks and non-directories, then removed it with `rm -rf -- "$target"`; result was `obsolete-home-removed`.
- Post-cleanup verification passed: `test ! -e "$HOME/.stronk-pi/home"` reported `obsolete-home-absent`.
- Post-cleanup cleanup dry-run passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi-setup cleanup-private-home --dry-run --json >/tmp/stronkpi-cleanup-after-delete.json && printf "%s\n" cleanup-dry-run-now-ok'`.
- Post-cleanup cleanup JSON check passed with `obsoleteHome=/Users/eyy/.stronk-pi/home` and `exists=false`.
- Post-cleanup installed validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --validate-only >/tmp/stronkpi-after-cleanup-validate.log && printf "%s\n" installed-validate-ok'`.
- Post-cleanup installed diagnose passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --diagnose --json >/tmp/stronkpi-after-cleanup-diagnose.json && printf "%s\n" installed-diagnose-ok'`.
- Superseded post-cleanup diagnose invariant check passed before the MCP artifact location reversal: `effectiveHome=/Users/eyy`, `stateRoot=/Users/eyy/.stronk-pi`, and `mcpConfigPath=/Users/eyy/.stronk-pi/generated/mcp/7032ab83a0003dbf.json`.
- Post-cleanup negative path check passed: `~/.pi`, `~/.config/pi`, `~/.local/share/pi`, `~/.cache/pi`, and `~/.stronk-pi/home` are absent.
- MCP artifact location reversal validation passed: `python3 -m unittest tests/test_manifest_verifier.py tests/test_mcp_doctor.py tests/test_guard_matrix.py tests/test_public_surface.py tests/test_release_scripts.py tests/test_plugin_state_root.py` ran 82 tests with one expected minimal-fixture skip.
- MCP artifact location reversal offline validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh tests/run_offline.sh'`.
- MCP artifact location reversal install dry-run validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh tests/test_install_dry_run.sh'`.
- Source wrapper validation after MCP reversal passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi --validate-only >/tmp/stronkpi-mcp-json-source-validate.log && printf "%s\n" source-validate-ok'`.
- Source wrapper diagnose after MCP reversal passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi --diagnose --json >/tmp/stronkpi-mcp-json-source-diagnose.json && printf "%s\n" source-diagnose-ok'`.
- Source diagnose MCP path check after MCP reversal passed with `mcpConfigPath=/Users/eyy/Documents/Work/Dev/repos/stronk-pi/.mcp.json`.
- Installed artifact refresh after MCP reversal command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh ./install.sh --prefix "$HOME/.local"'`.
- Runtime config refresh after MCP reversal command: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh bin/stronkpi-setup refresh-config --json'`; result was `ok: true`, `changedCount: 0`, and installed defaults already contained `generated_mcp_file = ".mcp.json"`.
- Installed wrapper path after MCP reversal: `zsh -lc 'SHELL=zsh command -v stronkpi; test -x "$HOME/.local/bin/stronkpi"; "$HOME/.local/bin/stronkpi" --version'` reported `/Users/eyy/.local/bin/stronkpi` and `stronkpi 0.1.0`.
- Installed wrapper validation after MCP reversal passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --validate-only >/tmp/stronkpi-mcp-json-installed-validate.log && printf "%s\n" installed-validate-ok'`.
- Installed wrapper diagnose after MCP reversal passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --diagnose --json >/tmp/stronkpi-mcp-json-installed-diagnose.json && printf "%s\n" installed-diagnose-ok'`.
- Installed diagnose MCP path check after MCP reversal passed with `mcpConfigPath=/Users/eyy/Documents/Work/Dev/repos/stronk-pi/.mcp.json`.
- Project `.mcp.json` generation command after MCP reversal: `STRONKPI_NO_NETWORK=1 python3 -c 'import importlib.util, pathlib, sys; root=pathlib.Path.cwd(); spec=importlib.util.spec_from_file_location("guard", root/"lib"/"stronk-pi-guard.py"); mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod); status=mod.prepare_mcp_adapter_runtime(mod.state_root(), cwd=root); print("generated=" + status["configPath"]); print("selectedCount=" + str(len(status.get("selectedTools") or []))); print("configChanged=" + str(status.get("configChanged")).lower())'`.
- Project `.mcp.json` generation evidence: generated `/Users/eyy/Documents/Work/Dev/repos/stronk-pi/.mcp.json`, selected two MCP servers, and `configChanged=true`.
- Project `.mcp.json` safety check passed: JSON parsed, file mode was `0o600`, server count was `2`, and common raw secret token patterns were absent.
- Post-generation installed validation passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --validate-only >/tmp/stronkpi-mcp-json-post-generate-validate.log && printf "%s\n" validate-ok'`.
- Post-generation installed diagnose passed: `STRONKPI_NO_NETWORK=1 zsh -lc 'SHELL=zsh stronkpi --diagnose --json >/tmp/stronkpi-mcp-json-post-generate-diagnose.json && printf "%s\n" diagnose-ok'`.
- Post-generation diagnose MCP path check passed with `mcpConfigPath=/Users/eyy/Documents/Work/Dev/repos/stronk-pi/.mcp.json`.
- Prior audit found `~/.stronk-pi/home` was mostly cache content, including `.npm` and `Library` cache trees, and did not reveal important private credential stores.
- `harness_environment(root)` is the central launcher boundary that currently rewrites `HOME` and `XDG_CONFIG_HOME`.
- Pi already has explicit environment hooks for agent and session directories, so `HOME` should not be the primary state containment mechanism.
- Read-only swarm verified private-home anchors in `harness_environment(...)`, `ensure_private_pi_home_config(...)`, `private_pi_extension_path(...)`, `config/defaults.toml`, `tests/test_manifest_verifier.py`, and `tests/test_mcp_doctor.py`.
- Read-only swarm verified generated MCP config is currently project-local and must move to a state-root generated path to satisfy the new state contract.
- Read-only swarm found no production `homedir()` call sites in the bounded repo search; upstream packaged runtime assumptions still need implementation-time verification.
- Second-pass vetting residual risks: upstream direct-home writes may appear during inventory, real `HOME` expands trusted-launch exposure, cleanup must fail closed, installed-wrapper behavior needs runtime evidence, and cross-repo plugin verification may drift.

## Artifacts
- [PLAN.md](./PLAN.md)

## Client Feedback
- [2026-06-27] User clarified that no backward compatibility or rollback path is needed for `~/.stronk-pi/home`; Stronk Pi state should write under `~/.stronk-pi` like Codex writes under `~/.codex`.
