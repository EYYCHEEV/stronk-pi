# Stronk Pi Subagent Codex Parity Audit

## Objective
Audit whether the current Stronk Pi subagent setup with `pi-subagents` and `pi-intercom` matches the intended Codex-like subagent experience for repo navigation, skill-triggered `$repos` workflows, role routing, lifecycle behavior, and verification.

## Scope
- Compare current Stronk Pi subagent behavior against the Codex-facing expectations used in `agentic-workstation`.
- Locate relevant prior exec-plans, commits, docs, and implementation notes in `agentic-workstation`, `stronk-pi`, and `stronk-pi-plugin`.
- Inspect live Stronk Pi runtime wiring only as needed for evidence.
- Produce a verdict with gaps, risks, and proposed follow-up fixes.

## Constraints
- Run the audit swarm as read-only.
- Subagents must not edit files or run mutating commands.
- Use `fork_context=false` for subagents.
- Use long waits and close completed subagents.
- Do not modify repo governance files for ExecPlan infrastructure during this audit.
- Avoid broad unbounded scans across `/Users`; scope searches to the named repos.

## Task Checklist
- [x] Create the active exec-plan workspace for this audit.
- [x] Locate relevant historical exec-plans and commits.
- [x] Run a read-only subagent swarm to audit architecture, runtime behavior, and parity expectations.
- [x] Cross-validate findings against local files and live diagnostics.
- [x] Record audit findings in `LOGS.md`.
- [x] Report final verdict and next recommended fixes.

## Open Questions
- [x] Should role aliases like `docs-scout` remain silent aliases, or should Stronk Pi expose alias resolution explicitly to match Codex ergonomics?
- [x] Should Stronk Pi eventually support Codex-style native `$skill` injection inside child agents beyond role frontmatter and `STRONK_PI_SKILL_ROOTS`?

## Final Verdict
Stronk Pi subagents now satisfy the audited `$repos` smoke path, but they are not yet identical enough to Codex across the full subagent user experience.
The verified path is: parent prompt loads `$repos`, parent uses `stronk_subagent`, child receives `$repos` skill context, child runs on the active parent model, parent waits with a long timeout, parent closes the terminal child, and live diagnose reports the intercom bridge as linked.

The main root cause was not intercom delivery or skill injection.
The failing child was launched without a `model` override, so upstream `pi-subagents` used the private Pi default model and hit Kimi account errors.

Full UX parity still needs work.
The highest-priority gaps are parent-visible child output, Codex-like lifecycle ergonomics, explicit role alias reporting, timeout and recovery metadata, verified cleanup reporting, live `send_input` and `revive` smokes, and negative error handling so child failures are not parent-facing `completed` states.

Alias handling is currently silent.
The facade accepts common scout aliases and maps them to allowed generated roles, which helps the failing `docs-scout`, `structure-scout`, and `source-scout` examples, but the tool should expose `roleRequested`, `roleUsed`, and `aliasResolved` for Codex-like clarity.
