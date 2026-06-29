## Upstream Boundary (HARD POLICY)

Stronk Pi is a personal distribution and must use Stronk-owned forks, local worktrees, and Stronk Pi release/update pipelines for runtime changes.
Agents MUST NOT open, reopen, edit, comment on, review, or otherwise create public activity in original upstream Pi, Pi subagent, or Pi intercom repositories.
This includes pull requests, issues, discussions, review comments, maintainer pings, and follow-up comments.
Agents MUST NOT push branches, tags, or commits to original upstream Pi, Pi subagent, or Pi intercom remotes.
Blocked upstream targets include `earendil-works/pi`, `badlogic/pi-mono`, `nicobailon/pi-subagents`, `nicobailon/pi-intercom`, and any non-Stronk-owned original upstream for Pi runtime, Pi subagent, or Pi intercom work.
Use Stronk-owned targets such as `EYYCHEEV/pi-mono`, `EYYCHEEV/stronk-pi-subagents`, `EYYCHEEV/stronk-pi-intercom`, `EYYCHEEV/stronk-pi-plugin`, and this `EYYCHEEV/stronk-pi` distribution repo instead.
If a runtime, subagent, or intercom change appears to require upstream work, keep it in the Stronk-owned fork/distribution path and report the Stronk-owned next step.
General approval for git operations, release work, or "end to end" execution does not override this policy.
Only an explicit same-turn user instruction naming the exact upstream repo, exact action, and exact text/command can override it.
If that explicit override is absent, stop before any upstream public action and report the blocked command.

<!-- exec-plan:init:start -->
## ExecPlans

When writing complex features or significant refactors, use an ExecPlan aligned with `.agents/PLANS.md`.

For this repo, active exec-plan workspaces live under `docs/exec-plans/active/<slug>/` and completed exec-plan workspaces live under `docs/exec-plans/completed/<slug>/`.
Each workspace must include `PLAN.md` and `LOGS.md`.
<!-- exec-plan:init:end -->
