#!/usr/bin/env zsh
set -euo pipefail

repo_root="/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
workspace="${repo_root}/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes"
model="${STRONK_PI_SMOKE_MODEL:-deepseek/deepseek-v4-pro:high}"
stamp="$(date +%Y%m%d-%H%M%S)"
log_dir="${workspace}/artifacts/tmux-smokes/${stamp}"
mkdir -p "${log_dir}"

typeset -A prompts
typeset -A tokens
prompts[lifecycle]="${workspace}/tmux-lifecycle-output-smoke.prompt.md"
tokens[lifecycle]="STATUS_TOKEN=STRONK_PI_LIFECYCLE_OK|TERMINAL_OUTPUT_PREVIEW_SEEN=true|CLOSED=true"
prompts[repos]="${workspace}/tmux-repos-skill-smoke.prompt.md"
tokens[repos]="STATUS_TOKEN=STRONK_PI_REPOS_SKILL_OK"
prompts[aliases]="${workspace}/tmux-alias-resolution-smoke.prompt.md"
tokens[aliases]="STATUS_TOKEN=STRONK_PI_ALIAS_OK|ALIAS_CASE=docs-scout|ALIAS_CASE=structure-scout|ALIAS_CASE=source-scout|roleRequested=docs-scout|roleRequested=structure-scout|roleRequested=source-scout|aliasResolved=true"
prompts[send-input]="${workspace}/tmux-send-input-smoke.prompt.md"
tokens[send-input]="STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK|FOLLOWUP_CONSUMED=true"
prompts[revive]="${workspace}/tmux-revive-smoke.prompt.md"
tokens[revive]="STATUS_TOKEN=STRONK_PI_REVIVE_OK|PREVIOUS_CHILD_LINKED=true|MODEL_INHERITED=true"
prompts[negative]="${workspace}/tmux-negative-child-failure-smoke.prompt.md"
tokens[negative]="STATUS_TOKEN=STRONK_PI_NEGATIVE_FAILURE_OK|PARENT_VISIBLE_FAILURE=true"
prompts[timeout]="${workspace}/tmux-wait-timeout-recovery-smoke.prompt.md"
tokens[timeout]="STATUS_TOKEN=STRONK_PI_TIMEOUT_RECOVERY_OK|timedOut=true|recommendedNextAction="
prompts[swarm-ux]="${workspace}/tmux-readonly-write-swarm-ux-smoke.prompt.md"
tokens[swarm-ux]="STATUS_TOKEN=STRONK_PI_SWARM_UX_OK|READ_ONLY_DENIED_MUTATION=true|WRITE_SWARM_REPORTS_ROLE_ROUTING=true|ROLE_ROUTING_REPORT_SOURCE=parent_tool_result|CLEANUP_REPORTED=true"

check_alias_metadata() {
  local marker_file="$1"
  local log_file="$2"
  local state_root="${STRONK_PI_STATE_ROOT:-${HOME}/.stronk-pi}"
  local children_root="${state_root}/projects"
  local candidates=()

  if [[ ! -d "${children_root}" ]]; then
    print -ru2 -- "alias metadata state root missing: ${children_root}"
    return 1
  fi

  candidates=(${(f)"$(find "${children_root}" -maxdepth 5 -name children.json -newer "${marker_file}" -print 2>/dev/null)"})
  if (( ${#candidates[@]} == 0 )); then
    print -ru2 -- "alias metadata check found no fresh children.json files under ${children_root}"
    return 1
  fi

  node - "${candidates[@]}" <<'NODE' 2>&1 | tee -a "${log_file}"
const fs = require('node:fs');
const required = ['docs-scout', 'structure-scout', 'source-scout'];
const terminalStatuses = new Set(['completed', 'closed', 'failed', 'interrupted', 'stale', 'dry-run']);

let best = null;
for (const path of process.argv.slice(2)) {
  let data;
  try {
    data = JSON.parse(fs.readFileSync(path, 'utf8'));
  } catch {
    continue;
  }
  const children = Array.isArray(data.children) ? data.children : [];
  const rows = new Map();
  for (const child of children) {
    if (!required.includes(child.roleRequested)) continue;
    if (child.aliasResolved !== true) continue;
    if (typeof child.roleUsed !== 'string' || child.roleUsed.length === 0) continue;
    if (child.roleUsed === child.roleRequested) continue;
    if (!terminalStatuses.has(child.status)) continue;
    rows.set(child.roleRequested, child);
  }
  if (!required.every((role) => rows.has(role))) continue;
  const newest = Math.max(...children.map((child) => Date.parse(child.updatedAt || child.createdAt || 0) || 0));
  if (!best || newest > best.newest) best = { path, rows, newest };
}

if (!best) {
  console.error('alias metadata check did not find one fresh facade run with all required aliases');
  process.exit(1);
}

console.log('STATUS_TOKEN=STRONK_PI_ALIAS_OK');
console.log(`ALIAS_LEDGER=${best.path}`);
for (const role of required) {
  const child = best.rows.get(role);
  console.log(`ALIAS_CASE=${role} roleRequested=${child.roleRequested} roleUsed=${child.roleUsed} aliasResolved=${child.aliasResolved}`);
}
NODE
  return ${pipestatus[1]}
}

check_send_input_metadata() {
  local marker_file="$1"
  local log_file="$2"
  local state_root="${STRONK_PI_STATE_ROOT:-${HOME}/.stronk-pi}"
  local children_root="${state_root}/projects"
  local candidates=()

  if [[ ! -d "${children_root}" ]]; then
    print -ru2 -- "send_input metadata state root missing: ${children_root}"
    return 1
  fi

  candidates=(${(f)"$(find "${children_root}" -maxdepth 5 -name children.json -newer "${marker_file}" -print 2>/dev/null)"})
  if (( ${#candidates[@]} == 0 )); then
    print -ru2 -- "send_input metadata check found no fresh children.json files under ${children_root}"
    return 1
  fi

  node - "${candidates[@]}" <<'NODE' 2>&1 | tee -a "${log_file}"
const fs = require('node:fs');
const path = require('node:path');
const terminalStatuses = new Set(['completed', 'closed']);

let best = null;
for (const file of process.argv.slice(2)) {
  let data;
  try {
    data = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    continue;
  }
  const eventsPath = path.join(path.dirname(file), 'events.ndjson');
  let events = '';
  try {
    events = fs.readFileSync(eventsPath, 'utf8');
  } catch {
    continue;
  }
  for (const child of Array.isArray(data.children) ? data.children : []) {
    const preview = String(child.childOutputPreview || '');
    if (!terminalStatuses.has(child.status)) continue;
    if (child.inputAccepted !== true) continue;
    if (child.inputLinkedChildId !== child.childId) continue;
    if (child.cleanupVerified !== true) continue;
    if (!preview.includes('FOLLOWUP_CONSUMED=true')) continue;
    if (!preview.includes('STATUS_TOKEN=<redacted>') && !preview.includes('STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK')) continue;
    if (!events.includes('bridge_send_input_continuation_started')) continue;
    const newest = Date.parse(child.updatedAt || child.createdAt || 0) || 0;
    if (!best || newest > best.newest) best = { file, child, newest };
  }
}

if (!best) {
  console.error('send_input metadata check did not find a fresh completed continuation with accepted linked input and cleanup proof');
  process.exit(1);
}

console.log(`SEND_INPUT_LEDGER=${best.file}`);
console.log(`SEND_INPUT_CHILD=${best.child.childId} inputAccepted=true inputLinkedChildId=${best.child.inputLinkedChildId} cleanupVerified=true`);
console.log('STATUS_TOKEN=STRONK_PI_SEND_INPUT_OK');
console.log('FOLLOWUP_CONSUMED=true');
NODE
  return ${pipestatus[1]}
}

run_one() {
  local name="$1"
  local prompt="${prompts[$name]:-}"
  local required="${tokens[$name]:-}"
  if [[ -z "${prompt}" || -z "${required}" ]]; then
    print -ru2 -- "unknown smoke: ${name}"
    return 2
  fi
  if [[ ! -f "${prompt}" ]]; then
    print -ru2 -- "missing prompt: ${prompt}"
    return 2
  fi

  local session="sp-ux-${name}-${stamp}"
  local log_file="${log_dir}/${name}.log"
  local run_script="${log_dir}/${name}.run.zsh"
  local marker_file="${log_dir}/${name}.marker"
  local combined_prompt="${log_dir}/${name}.prompt.md"
  local final_guard="Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN, DIAG_TOKEN, boolean proof line, alias metadata line, and recommendedNextAction line requested by the prompt. Do not replace required tokens with a prose summary."
  {
    cat "${prompt}"
    print -r -- ""
    print -r -- "${final_guard}"
  } > "${combined_prompt}"
  cat > "${run_script}" <<EOF
#!/usr/bin/env zsh
set -o pipefail
cd "${repo_root}"
stronkpi --model "${model}" --no-session -p "@${combined_prompt}" 2>&1 | tee "${log_file}"
exit_code=\${pipestatus[1]}
print -r -- "STRONK_PI_SMOKE_EXIT=\${exit_code}" | tee -a "${log_file}"
exit "\${exit_code}"
EOF
  chmod +x "${run_script}"

  print -r -- "starting ${name}: tmux session ${session}"
  touch "${marker_file}"
  tmux new-session -d -s "${session}" -c "${repo_root}" "${run_script}"
  while tmux has-session -t "${session}" 2>/dev/null; do
    sleep 5
  done

  if ! rg -F -- "STRONK_PI_SMOKE_EXIT=0" "${log_file}" >/dev/null; then
    print -ru2 -- "${name} failed before token checks; log: ${log_file}"
    return 1
  fi
  if rg -i -- 'dry_run_no_worker|dry-run-completed|dry-run-only warning|skipped child execution detected|reported skipped child execution|no launched worker detected|mocked worker detected' "${log_file}" >/dev/null; then
    print -ru2 -- "${name} reported a mocked or skipped child path; log: ${log_file}"
    return 1
  fi
  if rg -i -- 'PARTIAL FAILURE|DELIVERY FAILURE|SMOKETEST VERDICT:.*FAIL|SMOKE TEST.*FAILED' "${log_file}" >/dev/null; then
    print -ru2 -- "${name} reported an explicit smoke failure verdict; log: ${log_file}"
    return 1
  fi
  if [[ "${name}" == "aliases" ]]; then
    if ! check_alias_metadata "${marker_file}" "${log_file}"; then
      print -ru2 -- "${name} failed alias metadata ledger verification; log: ${log_file}"
      return 1
    fi
  fi
  if [[ "${name}" == "send-input" ]]; then
    if ! check_send_input_metadata "${marker_file}" "${log_file}"; then
      print -ru2 -- "${name} failed send_input metadata ledger verification; log: ${log_file}"
      return 1
    fi
  fi
  local token
  for token in ${(s:|:)required}; do
    if ! rg -F -- "${token}" "${log_file}" >/dev/null; then
      print -ru2 -- "${name} missing required token ${token}; log: ${log_file}"
      return 1
    fi
  done
  if [[ "${name}" == "timeout" ]]; then
    if ! rg -- 'recommendedNextAction=(wait_again|check_status|send_input|close_child|inspect_error|run_diagnose)' "${log_file}" >/dev/null; then
      print -ru2 -- "${name} did not report a constrained recommendedNextAction; log: ${log_file}"
      return 1
    fi
  fi
  print -r -- "${name}: ok (${log_file})"
}

if ! command -v tmux >/dev/null 2>&1; then
  print -ru2 -- "tmux is required for live Stronk Pi smokes"
  exit 2
fi

selected=("$@")
if (( ${#selected[@]} == 0 )); then
  selected=(lifecycle repos aliases send-input revive negative timeout swarm-ux)
fi

for smoke in "${selected[@]}"; do
  run_one "${smoke}"
done

print -r -- "tmux smoke logs: ${log_dir}"
