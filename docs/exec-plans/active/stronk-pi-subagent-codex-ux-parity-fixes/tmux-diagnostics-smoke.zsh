#!/usr/bin/env zsh
set -euo pipefail

repo_root="/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
workspace="${repo_root}/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes"
stamp="$(date +%Y%m%d-%H%M%S)"
log_dir="${workspace}/artifacts/tmux-diagnostics/${stamp}"
mkdir -p "${log_dir}"

run_diag() {
  local name="$1"
  local token="$2"
  local body="$3"
  local session="sp-ux-diag-${name}-${stamp}"
  local log_file="${log_dir}/${name}.log"
  local run_script="${log_dir}/${name}.run.zsh"
  cat > "${run_script}" <<EOF
#!/usr/bin/env zsh
set -uo pipefail
cd "${repo_root}"
{
${body}
} 2>&1 | tee "${log_file}"
exit_code=\${pipestatus[1]}
exit "\${exit_code}"
EOF
  chmod +x "${run_script}"

  print -r -- "starting diagnostics ${name}: tmux session ${session}"
  tmux new-session -d -s "${session}" -c "${repo_root}" "${run_script}"
  while tmux has-session -t "${session}" 2>/dev/null; do
    sleep 2
  done

  if ! rg -F -- "${token}" "${log_file}" >/dev/null; then
    print -ru2 -- "diagnostics ${name} missing token ${token}; log: ${log_file}"
    return 1
  fi
  print -r -- "diagnostics ${name}: ok (${log_file})"
}

if ! command -v tmux >/dev/null 2>&1; then
  print -ru2 -- "tmux is required for diagnostics smoke"
  exit 2
fi

linked_body='json="$(bin/stronkpi --diagnose --json)"
print -r -- "${json}"
DIAG_JSON="${json}" python3 - <<'"'"'PY'"'"'
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
PY'

missing_body='tmp="$(mktemp -d "${TMPDIR:-/tmp}/stronk-pi-missing-intercom.XXXXXX")"
trap '"'"'rm -rf "${tmp}"'"'"' EXIT
json="$(STRONK_PI_DEV_OVERRIDES=1 STRONK_PI_STATE_ROOT="${tmp}" bin/stronkpi --diagnose --json)"
print -r -- "${json}"
DIAG_JSON="${json}" python3 - <<'"'"'PY'"'"'
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
PY'

run_diag linked "DIAG_TOKEN=STRONK_PI_DIAG_LINKED_OK" "${linked_body}"
run_diag missing-intercom "DIAG_TOKEN=STRONK_PI_DIAG_MISSING_INTERCOM_OK" "${missing_body}"

print -r -- "tmux diagnostics logs: ${log_dir}"
