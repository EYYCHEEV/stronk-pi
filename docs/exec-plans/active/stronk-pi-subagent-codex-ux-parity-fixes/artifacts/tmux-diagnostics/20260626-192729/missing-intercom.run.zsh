#!/usr/bin/env zsh
set -uo pipefail
cd "/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
{
tmp="$(mktemp -d "${TMPDIR:-/tmp}/stronk-pi-missing-intercom.XXXXXX")"
trap 'rm -rf "${tmp}"' EXIT
json="$(STRONK_PI_DEV_OVERRIDES=1 STRONK_PI_STATE_ROOT="${tmp}" bin/stronkpi --diagnose --json)"
print -r -- "${json}"
DIAG_JSON="${json}" python3 - <<'PY'
import json
import os
payload = json.loads(os.environ["DIAG_JSON"])
runtime = payload["subagentRuntime"]
missing = {(item["packageName"], item["packageVersion"]) for item in runtime["missingPackages"]}
assert runtime["enabled"] is False
assert runtime["intercomBridgeLinked"] is False
assert ("pi-subagents", "0.22.0") in missing
assert ("pi-intercom", "0.6.0") in missing
print("DIAG_TOKEN=STRONK_PI_DIAG_MISSING_INTERCOM_OK")
PY
} 2>&1 | tee "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-diagnostics/20260626-192729/missing-intercom.log"
exit_code=${pipestatus[1]}
exit "${exit_code}"
