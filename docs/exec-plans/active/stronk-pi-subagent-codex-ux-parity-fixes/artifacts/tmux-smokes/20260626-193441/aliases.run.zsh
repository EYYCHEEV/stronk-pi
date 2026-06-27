#!/usr/bin/env zsh
set -o pipefail
cd "/Users/eyy/Documents/Work/Dev/repos/stronk-pi"
stronkpi --model "deepseek/deepseek-v4-pro:high" --no-session -p "@/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/tmux-alias-resolution-smoke.prompt.md" "Automated validation final-output guard: after completing the prompt, your final answer must include every literal STATUS_TOKEN, DIAG_TOKEN, boolean proof line, alias metadata line, and recommendedNextAction line requested by the prompt. Do not replace required tokens with a prose summary." 2>&1 | tee "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-smokes/20260626-193441/aliases.log"
exit_code=${pipestatus[1]}
print -r -- "STRONK_PI_SMOKE_EXIT=${exit_code}" | tee -a "/Users/eyy/Documents/Work/Dev/repos/stronk-pi/docs/exec-plans/active/stronk-pi-subagent-codex-ux-parity-fixes/artifacts/tmux-smokes/20260626-193441/aliases.log"
exit "${exit_code}"
