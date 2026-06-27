# ExecPlan Guidelines

Use ExecPlans for complex features, risky fixes, and cross-repo or runtime changes that need a durable record.

Active workspaces live under `docs/exec-plans/active/<slug>/`.
Completed workspaces live under `docs/exec-plans/completed/<slug>/`.
Each workspace must contain `PLAN.md` and `LOGS.md`.

Plans are living documents.
Update `LOGS.md` as the operational source of truth while executing, and reconcile checklist state back into `PLAN.md`.

Every plan should define:
- Objective and user-visible outcome.
- Scope and explicit non-goals.
- Constraints and safety boundaries.
- Task checklist with verifiable completion criteria.
- Open questions and blockers.
- Validation steps with observable evidence.

Keep plans concise enough for maintainers to edit.
Prefer concrete commands, file paths, runtime checks, and rollback notes over broad intent.
