#!/usr/bin/env zsh
set -euo pipefail

repo_root="/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
workspace="${repo_root}/docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics"
prompt="${workspace}/tmux-orchestration-smoke.prompt.md"
model="${STRONK_PI_SMOKE_MODEL:-deepseek/deepseek-v4-pro:high}"
stamp="$(date +%Y%m%d-%H%M%S)"
log_dir="${workspace}/artifacts/tmux-orchestration/${stamp}"
session="sp-orchestration-${stamp}"
log_file="${log_dir}/orchestration.log"
run_script="${log_dir}/orchestration.run.zsh"
combined_prompt="${log_dir}/orchestration.prompt.md"

required_tokens=(
  "STATUS_TOKEN=STRONK_PI_PUBLIC_PATH_REDACTION_OK"
  "NO_CWD_IN_PUBLIC_RESULT=true"
  "DEBUG_ARTIFACT_PATHS_NOT_PUBLIC=true"
  "STATUS_TOKEN=STRONK_PI_WAIT_ALL_OK"
  "WAIT_ALL_CHILDREN=3"
  "WAIT_ALL_TIMEOUT_NONTERMINAL=true"
  "WAIT_ALL_FAILURE_VISIBLE=true"
  "STATUS_TOKEN=STRONK_PI_READ_OUTPUT_OK"
  "OUTPUT_HANDLE_OPAQUE=true"
  "READ_OUTPUT_CHUNKED=true"
  "READ_OUTPUT_REDACTED=true"
  "NO_RAW_OUTPUT_PATH=true"
  "STATUS_TOKEN=STRONK_PI_BATCH_CLOSE_OK"
  "CLEANUP_REPORTED_PER_CHILD=true"
  "CLOSE_FAILURE_NOT_HIDDEN=true"
  "STATUS_TOKEN=STRONK_PI_NEGATIVE_BATCH_OK"
  "DUPLICATE_CHILD_DENIED=true"
  "FOREIGN_CHILD_DENIED=true"
  "INVALID_OUTPUT_HANDLE_DENIED=true"
  "STATUS_TOKEN=STRONK_PI_CITATION_OK"
  "FILE_LINE_RECHECKED_AT_SYNTHESIS=true"
)

cleanup_session() {
  if tmux has-session -t "${session}" 2>/dev/null; then
    tmux kill-session -t "${session}" 2>/dev/null || true
  fi
}

trap cleanup_session EXIT

if ! command -v tmux >/dev/null 2>&1; then
  print -ru2 -- "tmux is required for live Stronk Pi smokes"
  exit 2
fi

if [[ ! -f "${prompt}" ]]; then
  print -ru2 -- "missing smoke prompt: ${prompt}"
  exit 2
fi

mkdir -p "${log_dir}"
{
  cat "${prompt}"
  print -r -- ""
  print -r -- "Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN and boolean proof line requested by the prompt. Do not replace required tokens with a prose summary."
} > "${combined_prompt}"

cat > "${run_script}" <<EOF
#!/usr/bin/env zsh
set -o pipefail
cd "${repo_root}"
stronkpi --model "${model}" --no-session -p "@${combined_prompt}" 2>&1 | tee "${log_file}"
exit_code=\${pipestatus[1]}
print -r -- "STRONK_PI_TMUX_SMOKE_EXIT=\${exit_code}" | tee -a "${log_file}"
exit "\${exit_code}"
EOF
chmod +x "${run_script}"

print -r -- "starting tmux smoke session=${session}"
print -r -- "log_file=${log_file}"
print -r -- "cleanup_command=tmux kill-session -t ${session}"

tmux new-session -d -s "${session}" -c "${repo_root}" "${run_script}"
while tmux has-session -t "${session}" 2>/dev/null; do
  sleep 5
done

if ! rg -F -- "STRONK_PI_TMUX_SMOKE_EXIT=0" "${log_file}" >/dev/null; then
  print -ru2 -- "tmux smoke failed before token checks; log: ${log_file}"
  exit 1
fi

if rg -i -- 'dry[-_ ]run|dry_run_no_worker|dry-run-only warning|skipped child execution|no launched worker|mocked worker' "${log_file}" >/dev/null; then
  print -ru2 -- "tmux smoke reported a dry-run, mocked, or skipped child path; log: ${log_file}"
  exit 1
fi

if rg -i -- 'SMOKE TEST.*FAILED|SMOKETEST VERDICT:.*FAIL|PARTIAL FAILURE|DELIVERY FAILURE' "${log_file}" >/dev/null; then
  print -ru2 -- "tmux smoke reported an explicit failure verdict; log: ${log_file}"
  exit 1
fi

for token in "${required_tokens[@]}"; do
  if ! rg -F -- "${token}" "${log_file}" >/dev/null; then
    print -ru2 -- "tmux smoke missing required token ${token}; log: ${log_file}"
    exit 1
  fi
done

print -r -- "tmux orchestration smoke: ok"
print -r -- "session=${session}"
print -r -- "log_file=${log_file}"
