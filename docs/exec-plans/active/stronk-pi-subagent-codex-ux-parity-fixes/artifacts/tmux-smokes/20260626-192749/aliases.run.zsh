#!/usr/bin/env zsh
set -o pipefail
cd "/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
stronkpi --model "deepseek/deepseek-v4-pro:high" -p "@/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/tmux-alias-resolution-smoke.prompt.md" 2>&1 | tee "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-smokes/20260626-192749/aliases.log"
exit_code=${pipestatus[1]}
print -r -- "STRONK_PI_SMOKE_EXIT=${exit_code}" | tee -a "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-smokes/20260626-192749/aliases.log"
exit "${exit_code}"
