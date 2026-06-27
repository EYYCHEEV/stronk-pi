#!/usr/bin/env zsh
set -o pipefail
cd "/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
stronkpi --model "deepseek/deepseek-v4-pro:high" --no-session -p "@/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/artifacts/tmux-orchestration/20260627-025256/orchestration.prompt.md" 2>&1 | tee "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/artifacts/tmux-orchestration/20260627-025256/orchestration.log"
exit_code=${pipestatus[1]}
print -r -- "STRONK_PI_TMUX_SMOKE_EXIT=${exit_code}" | tee -a "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-orchestration-ergonomics/artifacts/tmux-orchestration/20260627-025256/orchestration.log"
exit "${exit_code}"
