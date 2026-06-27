#!/usr/bin/env zsh
set -euo pipefail

repo_root="/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
prompt_file="${repo_root}/docs/exec-plans/active/stronk-pi-subagent-codex-parity-audit/tmux-repos-skill-smoke.prompt.md"
session="sp-repos-parity-$(date +%H%M%S)"

tmux new-session -d -s "${session}" -c "${repo_root}" \
  "stronkpi --model deepseek/deepseek-v4-pro:high -p @${prompt_file}"

print -r -- "${session}"
