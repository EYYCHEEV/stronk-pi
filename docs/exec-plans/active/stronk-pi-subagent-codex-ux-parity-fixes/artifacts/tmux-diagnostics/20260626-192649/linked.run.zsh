#!/usr/bin/env zsh
set -euo pipefail
cd "/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
json="$(bin/stronkpi --diagnose --json)"
print -r -- "${json}"
DIAG_JSON="${json}" python3 - <<'PY'
import json
import os
payload = json.loads(os.environ["DIAG_JSON"])
runtime = payload["subagentRuntime"]
assert payload["ok"] is True
assert runtime["enabled"] is True
assert runtime["intercomBridgeLinked"] is True
assert runtime["packages"]["subagents"]["packageName"] == "pi-subagents"
assert runtime["packages"]["subagents"]["packageVersion"] == "0.22.0"
assert runtime["packages"]["intercom"]["packageName"] == "pi-intercom"
assert runtime["packages"]["intercom"]["packageVersion"] == "0.6.0"
print("DIAG_TOKEN=STRONK_PI_DIAG_LINKED_OK")
PY 2>&1 | tee "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-diagnostics/20260626-192649/linked.log"
