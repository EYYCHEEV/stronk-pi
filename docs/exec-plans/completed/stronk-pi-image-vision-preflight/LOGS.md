# Project Log: Stronk Pi Image Vision Preflight
Created: 2026-06-22T20:11:01+0800
Plan: ./PLAN.md
Workspace: docs/exec-plans/completed/stronk-pi-image-vision-preflight/

## Progress

- [x] Confirm the source-of-truth Stronk Pi plugin files, installed artifact path, and current test commands.
- [x] Characterize Pi image input shapes for `event.images`, clipboard-pasted temp paths, and explicit local image paths.
- [x] Define the preflight configuration contract, including default vision model from `~/.stronk-pi/config/`, enablement, limits, timeout, and failure mode.
- [x] Add focused tests for model-capability routing, image discovery, recursion guard, and text-only transform output.
- [x] Implement image normalization with MIME/type checks, byte limits, and safe path handling.
- [x] Implement the Kimi Code vision call path and structured prompt for image summarization.
- [x] Generalize the rich preflight schema from UI-heavy fields to universal image-type-neutral fields.
- [x] Raise and validate the multi-image default and ceiling to 12 images.
- [x] Scope rendered evidence IDs and the image evidence index by stable image label for multi-image traceability.
- [x] Document that prompt-time preflight does not expand folders and that later tool-discovered images are handled by explicit agentic image reading.
- [x] Inject the resulting vision context into text-only prompts while replacing analyzed local image paths with labels and stripping raw images.
- [x] Verify native-vision models still receive images without unnecessary preflight summarization.
- [x] Run source verification, installed-artifact smoke checks, and Stronk Pi launcher validation.
- [x] Refresh the installed Stronk Pi plugin artifact with a backup and document rollback.
- [x] Update relevant docs and this ExecPlan log with final behavior, risks, and verification evidence.
- [x] Lock the follow-up agentic image-reading design in this plan and log.
- [x] Register `image_read` as a Stronk Pi plugin tool with `Image Read` label and text-only-model description.
- [x] Implement explicit path and bounded directory image collection for `image_read`.
- [x] Route `image_read` images through the existing configured vision preflight model path and renderer.
- [x] Add focused plugin tests for `image_read` validation, path handling, directory bounds, provider request shape, evidence output, skipped images, redaction, partial summaries, and failure behavior.
- [x] Update the distribution guard allowlist and tests for `image_read`.
- [x] Update public docs to distinguish prompt-time preflight from explicit agentic image reading.
- [x] Run source, distribution, launcher, smoke, path-scan, and diff validation for the follow-up.
- [x] Record final review, risks, runtime-refresh status, and operator decision in this ExecPlan log.
- [x] Lock the prompt-time preflight extended-analysis artifact design after session truncation feedback.
- [x] Implement session-scoped extended sanitized prompt-time preflight artifacts and the `image_preflight_read` text-artifact tool.
- [x] Scale prompt-time vision request output tokens by prompt image count while preserving the configured per-image budget clamp.
- [x] Add focused tests for artifact handles, redaction, extended-context preservation, registered tool surface, and provider payload budgeting.
- [x] Refine artifact-backed prompt-time inline context into a compact bounded artifact index that tells text-only models to call `image_preflight_read`.
- [x] Split saved prompt-time preflight artifacts into three-image `image_preflight_read` handle groups while preserving one multi-image vision provider request.
- [x] Run full source, distribution, path-scan, and diff validation for the prompt-time artifact follow-up.
- [x] Run read-only Stronk swarm verification for the prompt-time artifact follow-up.
- [x] Record final prompt-time artifact review, risks, runtime-refresh status, and operator decision in this ExecPlan log.

## Session History

[2026-06-22] Created the ExecPlan workspace from current chat context after research found no mature drop-in Stronk Pi solution for image preflight routing.

[2026-06-23] Moved the ExecPlan workspace into `stronk-pi` so the next implementation session starts from the distribution repo while code changes land in `stronk-pi-plugin`.

[2026-06-23] Started implementation session from `stronk-pi`, with runtime/plugin changes scoped to `stronk-pi-plugin` and live `~/.stronk-pi` refresh deferred pending approval.

[2026-06-23] Independent review found two source issues and four documentation/log issues.
Source revisions removed an undeclared Pi dynamic import fallback, added explicit host completion adapter support, and tightened base64 image validation against spoofed MIME payloads.
Documentation revisions now state that source/config changes do not affect live runtime behavior until a matching plugin artifact is released/imported and installed.

[2026-06-23] Second independent review found two source issues and one ExecPlan bookkeeping issue.
Source revisions made the explicit active model authoritative over stale multimodal context metadata, bounded attachment scanning, and rejected oversized base64 payloads by encoded length before decoding.
ExecPlan revisions marked completed verification and recorded full validation evidence while keeping live runtime refresh operator-gated.

[2026-06-23] Final targeted code review accepted the routing fix, including the anonymous stale multimodal context edge case.
Final targeted docs review accepted the public docs and ExecPlan state after operator-local wording and checkpoint status were corrected.
No live `~/.stronk-pi` runtime refresh or artifact overwrite was performed.

[2026-06-24] Operator approved refreshing live Stronk Pi runtime/plugin state.
Created live artifact, config, and agent backups, replaced the installed `stronk-pi-plugin-0.1.0` package from the verified local plugin source, and ran `bin/stronkpi-setup refresh-config --json`.
Post-refresh validation passed for installed artifact smoke, launcher validation, live preflight config, and an installed-artifact functional image preflight transform.

[2026-06-24] Started follow-up diagnosis for live GLM launcher image preflight failure showing `vision preflight requires ctx.visionPreflight or ctx.complete`.
Initial finding: image discovery and prompt injection are active in the installed runtime, but the live Pi harness does not expose a host completion adapter to the plugin, so the plugin needs a direct configured-provider vision fallback.

[2026-06-24] Implemented and validated an interim configured-provider fallback.
The plugin kept host-provided vision adapters first, then fell back to configured OpenAI-compatible vision providers from Stronk Pi `models.json` when the live context did not expose `ctx.complete`.
The interim attempt incorrectly reintroduced `kimi-coding/kimi-for-coding` as a setup-managed OpenAI-compatible provider backed by the Moonshot endpoint; later diagnosis superseded this with Pi's built-in Kimi Code provider contract.

[2026-06-24] Started follow-up diagnosis for Kimi provider HTTP 401 in live GLM launcher image preflight.
Initial finding: both `KIMI_API_KEY` and `KIMI_CODE_API_KEY` are present but different, and the provider fallback selected the configured generic `KIMI_API_KEY` first.
For the `kimi-coding` provider, the coding-specific key should take precedence while keeping generic `KIMI_API_KEY` as a fallback.

[2026-06-24] Source fix for a suspected Kimi credential precedence issue was implemented and verified, pending operator approval for live runtime refresh.
This was later superseded by the finding that live `kimi-coding/kimi-for-coding` should use Pi's built-in provider contract and `KIMI_API_KEY`, not a setup-managed OpenAI-compatible provider entry.

[2026-06-24] Operator approved the Kimi credential precedence runtime refresh.
Refreshed the installed plugin artifact and runtime config after backups.
Installed validation confirmed the live provider config uses `$KIMI_CODE_API_KEY` and the installed plugin selects the coding key even when a different generic Kimi key is also present.

[2026-06-24] Started follow-up diagnosis for the continued Kimi HTTP 401 after the credential-precedence refresh.
Git history showed that commit `86a4a00` intentionally removed the custom `kimi-code` provider block and switched Stronk Pi to Pi's built-in `kimi-coding/kimi-for-coding` provider.
The preflight fallback had accidentally reintroduced `kimi-coding` as a generated OpenAI-compatible provider pointed at the Moonshot endpoint, which does not serve `kimi-for-coding`.
Redacted live provider probes showed `MOONSHOT_API_KEY` authenticates to `https://api.moonshot.ai/v1`, while `KIMI_API_KEY` authenticates to `https://api.kimi.com/coding/v1` and lists `kimi-for-coding`.
The follow-up fix restores the built-in provider contract for distribution config and points the plugin's built-in preflight fallback at the Kimi Code endpoint.

[2026-06-24] Completed source-side correction for the Kimi built-in provider regression.
The plugin now mirrors Pi's generated built-in Kimi Code provider contract by using Anthropic Messages at `https://api.kimi.com/coding/v1/messages`, `x-api-key`, and `User-Agent: KimiCLI/1.5`.
The Kimi-specific setup-managed provider entry remains removed from `models.json`, while `neuralwatt/glm-5.2` remains text-only so GLM image prompts route through preflight.
Real source probing with the operator's clipboard PNG and `neuralwatt/glm-5.2:xhigh` passed after tightening the vision prompt to a compact JSON summary and raising the bounded default timeout to 90 seconds.
Full source validation passed in both repos, temp-HOME `refresh-config` passed, and independent read-only review found no code issues after stale superseded log wording was corrected.

[2026-06-24] Started follow-up multi-image optimization and folder-read design session.
Scope: raise the daily-use multi-image default to 12 where safely bounded, evaluate whether batching is required, inspect a prior image-preflight session, and clarify that agent-initiated folder image reads are outside prompt-time preflight.
The later 2026-06-25 follow-up resolved that boundary with the registered `image_read` plugin tool.

[2026-06-24] Started follow-up image evidence traceability improvement.
Scope: make evidence IDs image-scoped in the injected preflight block so repeated vision-model IDs such as `E1` and `I1` remain unambiguous across multi-image prompts, then run read-only Stronk swarm verification.

[2026-06-24] Completed follow-up image evidence traceability improvement.
The source prompt now requires image-scoped evidence IDs (`<label>.E#`, `<label>.U#`, `<label>.N#`, and `<label>.I#`), and the renderer emits an Image Evidence Index with each image's citation prefix.
Regression coverage verifies duplicate local IDs are scoped per image, already scoped cross-image references are preserved, OCR-like literal text is not rewritten as evidence, skipped paths are redacted, and provider request text is sanitized before vision calls.
This log entry does not assert a live runtime refresh by itself; live behavior still depends on the current operator-approved installed artifact and config refresh recorded below.

[2026-06-24] Operator approved runtime refresh for the image evidence traceability plugin change.
Scope: refresh the installed `stronk-pi-plugin-0.1.0` artifact from verified local source, keep setup-managed config untouched unless validation proves a refresh is required, and record backup plus rollback notes.

[2026-06-25] Started follow-up implementation for agentic image reading.
Locked the design to a neutral registered plugin tool named `image_read` with UI label `Image Read`.
The tool is for text-only model workflows where image files are discovered after the prompt starts, and it must reuse the existing configured image vision preflight model route, limits, renderer, and safe failure handling.
The first implementation path is a plugin tool rather than a new MCP server.

[2026-06-26] Reconciled and closed the image vision preflight ExecPlan after the final static provider-header hardening pass.
All top-level progress items are complete; the workspace moved from active to completed with the remaining live-provider smoke caveat recorded below.

## Decisions

[2026-06-22] Decision: Use a dedicated ExecPlan workspace instead of folding this into `stronk-pi-swarm-parity` because image preflight has separate runtime behavior, provider-routing risk, tests, and rollout concerns.

[2026-06-22] Decision: Use `kimi-coding/kimi-for-coding` as the initial vision preflight target because existing Stronk Pi vision role metadata already points vision work to that model.

[2026-06-22] Decision: Read future vision preflight defaults from the portable Stronk Pi config contract under `~/.stronk-pi/config/` because `stronk-pi-setup` now owns public model defaults and generated role output is runtime state.

[2026-06-23] Decision: Run image preflight after `UserPromptSubmit` guard approval and before final input transform because unsafe prompts should fail before expensive image work and text-only image payloads must be stripped before model forwarding.

[2026-06-23] Decision: Default vision failure to fail-soft because a bounded explicit failure note is less surprising for pasted-image turns than silently dropping images; operators can set block mode for stricter behavior.

[2026-06-23] Decision: Enable image preflight for all text-only models by default and bypass native multimodal models using runtime model input metadata where available.

[2026-06-23] Decision: Initial image preflight bounds were 4 images and 5 MiB per image, with an internal image ceiling of 8 and a 20 MiB byte ceiling.
This was superseded on 2026-06-24 by the 12-image default and ceiling.

[2026-06-23] Decision: Preserve traceability by replacing successfully analyzed local image paths with stable image labels and appending labeled vision context.
Raw image payloads are stripped for text-only model forwarding after preflight.

[2026-06-24] Decision: Revise the image preflight public default and internal ceiling to 12 images because daily multi-image CLI workflows need more headroom, while keeping the per-image byte cap unchanged.

[2026-06-24] Decision: Defer batching for 12-image preflight because one request preserves cross-image comparison and the current Kimi path is already proven for multi-image request shape; add batching later only if real provider limits, timeouts, or quality failures appear.

[2026-06-24] Decision: Treat folder-discovered image reading as a separate explicit vision capability because prompt-time preflight only receives images attached to or pasted into the current turn.
Superseded on 2026-06-25 by the registered `image_read` plugin tool path rather than a new MCP server.

[2026-06-24] Decision: Scope rendered vision evidence IDs with image labels and add an Image Evidence Index because vision models can reuse local IDs per image and text-only models need unambiguous citations in multi-image prompts.

[2026-06-25] Decision: Implement agentic image reading as a registered Stronk Pi plugin tool, not a new MCP server, because the plugin already owns the image preflight config, provider fallback, limits, evidence renderer, and guard integration.

[2026-06-25] Decision: Name the explicit tool `image_read` with label `Image Read` because the model-facing surface should be neutral while the description explains it is intended for text-only model image inspection.

[2026-06-25] Decision: Route `image_read` through the same configured vision preflight model path as prompt-time preflight because this avoids a second vision stack and preserves the universal Image Evidence Index contract.

[2026-06-26] Decision: Close the image vision preflight ExecPlan because prompt-time preflight, `image_read`, artifact readback, provider-substitution static hardening, runtime-refresh records, and validation evidence are complete.
Future replacement vision providers still require API-keyed smoke tests as separate rollout work.

## Blockers

<!-- Format: [YYYY-MM-DD HH:MM] Description -->

None.

## Open Questions

- [x] Should vision failure fail soft by injecting an explicit failure note, or block the GLM turn because the user expected image understanding?
  Decision: Default to fail-soft; operators can set `failure_mode = "block"` for strict behavior.
- [x] Should preflight be enabled for every text-only model by default, or initially limited to NeuralWatt GLM-5.2 routes?
  Decision: Enable for text-only models by default and bypass native multimodal models.
- [x] What should the default max image count and per-image byte limit be for pasted CLI workflows?
  Decision: Revised follow-up default is 12 images and 5 MiB per image, capped internally at 12 images.
- [x] How should explicit image paths in normal text preserve traceability after summarization?
  Decision: Replace successfully analyzed local image paths with stable image labels while preserving traceability through the labels and appended vision context.

## Field Notes

- Research found OpenClaw media understanding as the strongest prior-art architecture, but not a drop-in dependency for Stronk Pi.
- Research found an OpenWebUI community multimodal reasoning pipe with the same concept, but not enough maturity evidence to adopt directly.
- Pi's input transform surface can modify submitted text and images, making a Pi-native implementation the lowest-blast-radius path.
- Portable Stronk Pi config now makes setup-owned `~/.stronk-pi/config/defaults.toml` and `~/.stronk-pi/config/roles.toml` the source for the default vision preflight model.
- Plugin discovery confirmed `stronk-pi-plugin/src/index.mjs` owns the Pi `input` transform, `package.json` owns `npm test` / `npm run lint:security`, and the installed artifact path is `~/.stronk-pi/artifacts/stronk-pi-plugin-<version>/package/src/index.mjs`.
- Implemented plugin-side image preflight helpers for `event.images`, local image paths in `event.text`, native multimodal bypass, recursion guard, image limits, MIME checks, timeout, fail-soft/block handling, structured context injection, and raw-image stripping for text-only models.
- Targeted plugin verification passed with `npm test -- test/extension.test.mjs` on 2026-06-23 after the final review revision: 115 tests passed, including explicit completion-adapter, stale multimodal context, oversized-base64, attachment-scan-limit, and spoofed-base64 rejection cases.
- Plugin repo verification passed with `npm run check` on 2026-06-23: 144 tests passed and `security-check: ok`.
- Distribution unittest verification passed with `python3 -m unittest tests/test_manifest_verifier.py` and `python3 -m unittest tests/test_mcp_doctor.py` on 2026-06-23: 28 manifest tests and 9 MCP doctor tests passed.
- Distribution offline verification passed with `STRONKPI_NO_NETWORK=1 sh tests/run_offline.sh` on 2026-06-23: 50 tests passed plus offline install/update/validate smoke output.
- Config/schema smoke passed with `python3 -m py_compile lib/stronk-pi-guard.py tests/test_manifest_verifier.py` plus a `load_toml_document(config/defaults.toml)` check for `[image_preflight]`.
- Launcher validation passed for `bin/stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, installed `stronkpi --validate-only`, and interactive-shell validation.
- Installed artifact smoke passed with `npm run smoke:installed`; this validated the currently installed artifact path but did not refresh or overwrite live runtime state.
- Public-surface path scans for operator-local planning and absolute local-repo path strings returned no matches in the scanned public files of both repos.
- `git diff --check` passed in both `stronk-pi` and `stronk-pi-plugin`.
- Runtime refresh backups created on 2026-06-24:
  artifact backup `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-005630.tgz`;
  config backup `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-005630.tgz`;
  agent backup `~/.stronk-pi/agent/backups/2026-06-24/agent.bak.20260624-005630.tgz`;
  socket-excluding agent backup `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-005650.tgz`.
- Runtime refresh command passed: local `npm pack` from `stronk-pi-plugin`, replace `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`, then `bin/stronkpi-setup refresh-config --json`.
- Post-refresh validation passed with `npm run smoke:installed`, `bin/stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, installed `stronkpi --validate-only`, interactive-shell launcher validation, live `[image_preflight]` config assertions, installed artifact source scan, and installed image preflight functional smoke.
- Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, restore the config and agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent`, then rerun `stronkpi --validate-only` and `stronkpi --diagnose --json`.
- Follow-up screenshot evidence showed the GLM launcher now discovers pasted image paths and injects a vision preflight block, but the preflight fails before model invocation because the live context lacks `ctx.visionPreflight` and `ctx.complete`.
- Follow-up implementation added direct OpenAI-compatible provider invocation for configured non-built-in vision preflight providers, including provider/model lookup from runtime `models.json`, `image_url` data URL conversion, bounded response tokens, timeout reuse, and redacted provider error handling.
  The Kimi-specific OpenAI-compatible provider path from that iteration was later superseded by the built-in Kimi Code Anthropic Messages contract.
- Source validation passed on 2026-06-24 with `node --test --test-name-pattern 'image preflight' test/extension.test.mjs` (14 tests), plugin `npm run check` (145 tests plus `security-check: ok`), `node --check src/index.mjs`, source JSON validation for `models.json` and `settings.base.json`, `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`, `STRONKPI_NO_NETWORK=1 sh tests/run_offline.sh` (52 tests), targeted distribution unittest suites, py_compile, public-surface path scan, and `git diff --check` in both touched repos.
- Independent code review accepted the provider fallback with no findings.
Reviewer noted only that live behavior depends on refreshing the installed plugin artifact and runtime model config.
- Runtime refresh on 2026-06-24 replaced the installed `stronk-pi-plugin-0.1.0` artifact from the verified source package and ran `bin/stronkpi-setup refresh-config --json` so live `~/.stronk-pi/agent/models.json` includes `kimi-coding/kimi-for-coding`.
Refresh backups:
  artifact `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-031326.tgz`;
  config `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-031326.tgz`;
  agent `~/.stronk-pi/agent/backups/2026-06-24/agent.bak.20260624-031326.tgz`;
  socket-excluding agent `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-031326.tgz`.
- Post-refresh validation passed with archive integrity checks, `npm run smoke:installed`, `bin/stronkpi --validate-only`, installed `stronkpi --validate-only`, interactive default launcher validation, interactive GLM launcher validation, `bin/stronkpi --diagnose --json`, live agent config assertions, installed artifact source scan, and an installed-artifact mocked provider-fallback smoke confirming GLM text-only flow stripped raw images.
  The mocked Kimi call target from that iteration used the wrong Moonshot/OpenAI-compatible contract and was later superseded.
- Rollback path for the follow-up provider fallback: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, restore config/agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent`, then rerun `stronkpi --validate-only`, GLM launcher validation, and `npm run smoke:installed`.
- Kimi HTTP 401 follow-up source validation passed on 2026-06-24 with focused credential regression tests, plugin `npm run check` (146 tests plus `security-check: ok`), `node --check src/index.mjs`, source JSON validation, `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`, `STRONKPI_NO_NETWORK=1 sh tests/run_offline.sh` (52 tests), temp-HOME `refresh-config` assertion for `$KIMI_CODE_API_KEY`, launcher validation, and `git diff --check` in both touched repos.
- Independent re-review accepted the credential precedence and missing-key fix with no findings.
- Kimi credential precedence runtime refresh backups created on 2026-06-24:
  artifact `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-034157.tgz`;
  config `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-034157.tgz`;
  socket-excluding agent `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-034157.tgz`.
- Kimi credential precedence post-refresh validation passed with archive integrity checks, `npm run smoke:installed`, `bin/stronkpi --validate-only`, installed `stronkpi --validate-only`, interactive default launcher validation, interactive GLM launcher validation, `bin/stronkpi --diagnose --json`, live Kimi config assertions, and installed key-precedence smoke.
- Rollback path for the Kimi credential precedence refresh: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, restore config and agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent`, then rerun `stronkpi --validate-only`, GLM launcher validation, and `npm run smoke:installed`.
- Follow-up git-history diagnosis found that `kimi-coding/kimi-for-coding` previously worked through Pi's built-in provider, not through a setup-managed custom provider in `models.json`.
- Redacted live endpoint probes returned HTTP 200 and listed `kimi-for-coding` for `https://api.kimi.com/coding/v1/models` with `KIMI_API_KEY`, while `https://api.moonshot.ai/v1/models` only accepted `MOONSHOT_API_KEY` and did not list `kimi-for-coding`.
- The source fix removes the setup-managed `kimi-coding` provider block, updates the plugin built-in fallback to the Kimi Anthropic Messages base URL `https://api.kimi.com/coding`, makes configured API-key references win before Kimi fallbacks, and preserves native multimodal bypass for the built-in Kimi model.
- Further live source probing found that `kimi-for-coding` rejects OpenAI-compatible chat calls with HTTP 403 unless the request uses the same built-in provider contract as Pi.
  The generated Pi model metadata declares `api: "anthropic-messages"`, base URL `https://api.kimi.com/coding`, and `User-Agent: KimiCLI/1.5`.
  The plugin fallback now mirrors that contract by calling `POST /v1/messages` with `x-api-key` and the Kimi CLI user-agent.
  A source-level real clipboard PNG preflight against `neuralwatt/glm-5.2:xhigh` passed with one image analyzed and no raw image payload forwarded.
- Real clipboard PNG probes also showed Kimi image analysis can run longer than the original 20 second preflight default and can approach the previous 60 second hard cap.
  The source default and public config default are now 90 seconds, with the internal cap raised to 120 seconds so operators can extend the bound for slower screenshots without disabling failure handling.
  The response normalizer now parses JSON wrapped in Markdown code fences so Kimi responses still populate `Observed Facts` and `Inferences And Uncertainty` instead of falling back to an unstructured blob.
- Source validation for the final Kimi correction passed on 2026-06-24 with plugin `npm run check` (149 tests plus `security-check: ok`), plugin syntax checks, plugin `git diff --check`, distribution JSON validation, `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`, distribution offline suite (52 tests), targeted distribution unittests (46 tests), py_compile, distribution `git diff --check`, temp-HOME config refresh assertions, and a real Kimi source preflight against the operator clipboard PNG.
- Independent read-only review used `code-reviewer`, `fork_context=false`, and accepted the code/config changes with no source findings.
  The only finding was stale ExecPlan wording from the superseded Moonshot/OpenAI-compatible and credential-precedence attempts; the log now marks those as superseded and records the current built-in Kimi Anthropic Messages behavior.
- A follow-up persisted session confirmed the universal schema worked on a non-UI diner breakfast photo: the text-only model answered from preflight context, did not call image read tools, and refused to invent a source website when no visible evidence supported it.
- Read-only multi-image swarm used architect, explorer, and qa-tester roles with `fork_context=false`.
  All agents agreed the 12-image bump is not config-only because the plugin hard cap was 8, prompt-time preflight does not scan folders, and batching should be deferred unless provider limits or quality issues are observed.
- Source plugin now defaults and clamps image preflight to 12 images, scans up to 24 candidate paths or attachments, keeps one vision request for up to 12 images, and adds regressions for 12-image request shape, 13th-image skip behavior, and folder non-expansion.
- Setup defaults and public docs now state `max_images = 12` and clarify that prompt-time preflight does not expand folders; the later `image_read` follow-up now handles tool-discovered local images.
- Validation passed on 2026-06-24 with focused image preflight tests (34 passed), full plugin `npm run check` (166 tests plus `security-check: ok`), plugin syntax check, source installed-artifact smoke, setup JSON validation, `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`, manifest verifier unittest suite, offline setup suite, temp-HOME `refresh-config` assertion for `max_images = 12`, public-surface tests, launcher validation for the default alias and GLM alias, `bin/stronkpi --diagnose --json`, public path scans, and `git diff --check` in both repos.
- No live `~/.stronk-pi` runtime/plugin artifact refresh was performed for the 12-image change.
- Follow-up evidence traceability now emits an Image Evidence Index, scopes rendered IDs by stable image label, preserves already scoped cross-image references, and keeps literal OCR-like text such as `E2` or `N1` from being rewritten into false citations.
- Initial read-only Stronk swarm review returned `revise`.
  Code review found overly broad evidence rewriting, skipped-path leaks, and raw local paths in vision request prompt text.
  QA review asked for skipped-path, path-attachment, partial-summary, and mixed citation tests.
  Docs review asked for checklist/log reconciliation.
- The revised source sanitizes analyzed, skipped, and failed image path aliases; sanitizes vision-provider request text and request metadata before calls; avoids assigning mismatched provider summary labels to another image section; and marks partial summary counts explicitly.
- Re-review accepted from code-reviewer, qa-tester, and technical-writer roles with `fork_context=false`; all subagents were closed and closure was confirmed.
- Validation passed on 2026-06-24 with focused image preflight tests (40 passed), plugin `npm run check` (172 tests plus `security-check: ok`), plugin syntax check, source installed-artifact smoke, setup validation, public-surface tests, manifest verifier tests, offline setup suite, launcher validation for `stronkpi`, the default alias, and the GLM alias, and diff whitespace checks in both repos.
- No live `~/.stronk-pi` runtime/plugin artifact refresh was performed for the evidence-traceability change.
- Operator-approved artifact-only runtime refresh on 2026-06-24 replaced `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package` from the verified local source package and left setup-managed config untouched because no config change was required.
  Artifact backup: `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-232723.tgz`.
  Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260624-232723`.
  Validation passed with installed artifact smoke, installed source scan for Image Evidence Index and metadata path stripping, source and installed `stronkpi --validate-only`, default alias validation, GLM alias validation, `bin/stronkpi --diagnose --json`, and a direct installed plugin probe showing request text and request metadata no longer contain the temporary image path.
  Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260624-232723` back to `package`, then rerun `stronkpi --validate-only`, default alias validation, GLM alias validation, and installed artifact smoke.

- Static provider-substitution hardening on 2026-06-26 now forwards provider/model static headers for OpenAI-compatible vision providers.
  Validation passed with plugin syntax checks, focused configured-provider tests, the full image-related test slice, full `npm run check`, and `git diff --check`; no live replacement-provider smoke ran because no replacement vision API key was available.

## Review Checkpoints

- `checkpoint_id`: image-vision-preflight-final
  `checkpoint_title`: Source, docs, and rollout readiness review
  `plan_version`: PLAN.md as of 2026-06-23
  `acceptance_criteria`: image preflight source behavior, public docs, verification evidence, and runtime refresh stop condition all match the plan.
  `action_taken`: Implemented plugin image preflight, docs, config defaults, tests, and distribution validation.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer and technical-writer
  `role_used`: code-reviewer and technical-writer
  `fallback_used`: false
  `reviewer_role`: code-reviewer and technical-writer
  `status`: done
  `verdict`: accept
  `retry_count`: 5
  `key_findings`: Removed undeclared dynamic import path, rejected spoofed base64 image payloads, made explicit active model routing authoritative over stale context metadata including anonymous stale metadata, bounded attachment scanning and early oversized-base64 rejection, clarified live artifact activation, resolved stale open questions, recorded full verification state, and replaced operator-local wording in public docs/logs.
  `strongest_evidence`: Targeted code re-review accepted the final routing fix; `npm run check` passes with 144 plugin tests and `security-check: ok`; distribution offline and launcher validations pass.
  `next_action`: none
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: image-vision-preflight-session-close
  `checkpoint_title`: Session-end reconciliation
  `plan_version`: PLAN.md as of 2026-06-23
  `acceptance_criteria`: final code/docs review is accepted, validation evidence is current, and live runtime state is not modified without approval.
  `action_taken`: Closed review findings, reran required verification, and reconciled PLAN/LOGS.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer and technical-writer
  `role_used`: code-reviewer and technical-writer
  `fallback_used`: false
  `reviewer_role`: code-reviewer and technical-writer
  `status`: done
  `verdict`: accept
  `retry_count`: 0
  `key_findings`: Source/docs implementation is accepted and live runtime refresh is complete with backups and rollback notes.
  `strongest_evidence`: Targeted code re-review accepted; final docs re-review accepted; offline, launcher, schema, installed smoke, path scan, diff checks, and post-refresh installed image preflight smoke passed.
  `next_action`: none
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-web-search-subagent-env
  `checkpoint_title`: Web search provider and subagent harness defaults
  `plan_version`: PLAN.md as of 2026-06-23 plus 2026-06-24 follow-up request
  `acceptance_criteria`: launcher exports configured search provider to the plugin harness, preserves explicit provider overrides, keeps subagent facade mode configured, and has validation evidence for launcher and installed plugin behavior.
  `action_taken`: Updated launcher harness env routing, added targeted tests, ran offline and runtime validation, and recorded follow-up evidence.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: qa-tester
  `role_used`: qa-tester
  `fallback_used`: false
  `reviewer_role`: qa-tester
  `status`: done
  `verdict`: accept
  `retry_count`: 0
  `key_findings`: Reviewer found no blocking issues; the launcher now supplies runtime `exa`, `stronk`, and `intercom` defaults without overwriting explicit search provider overrides.
  `strongest_evidence`: Targeted harness tests, full manifest verifier tests, offline setup suite, launcher validation, installed plugin provider and facade registration smoke, public-surface scan, and diff checks passed.
  `next_action`: none
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-image-routing-runtime-refresh
  `checkpoint_title`: Image routing runtime artifact refresh
  `plan_version`: PLAN.md as of 2026-06-23 plus 2026-06-24 screenshot follow-up
  `acceptance_criteria`: live installed artifact runs image preflight for pasted local image paths on text-only GLM, installed smoke covers this case, launchers validate after refresh, and rollback is documented.
  `action_taken`: Diagnosed stale installed artifact, tightened installed-artifact smoke coverage, refreshed the live plugin package with backups, and reran source and installed verification.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: qa-tester
  `role_used`: qa-tester
  `fallback_used`: false
  `reviewer_role`: qa-tester
  `status`: done
  `verdict`: accept
  `retry_count`: 0
  `key_findings`: Reviewer confirmed source and installed artifacts contain the image-preflight path and that a pasted local image path transforms into a bounded preflight context with one vision call.
  `strongest_evidence`: Installed pasted-path probe returned `installed_action=transform`, `installed_vision_calls=1`, and `installed_has_context=true`; installed artifact smoke and full plugin checks passed after refresh.
  `next_action`: none
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-provider-fallback-runtime-refresh
  `checkpoint_title`: Direct configured-provider vision preflight fallback (superseded for Kimi)
  `plan_version`: PLAN.md as of 2026-06-23 plus 2026-06-24 GLM launcher failure screenshot
  `acceptance_criteria`: text-only GLM image preflight no longer requires `ctx.complete`; the plugin can invoke configured OpenAI-compatible non-built-in vision providers directly; source/runtime validation pass; rollback is documented.
  `action_taken`: Added the plugin provider fallback, added interim Kimi provider config/docs, refreshed the installed artifact and runtime model config after validation, and ran source plus installed smoke checks. Later Kimi-specific diagnosis superseded the interim Kimi provider config with Pi's built-in Anthropic Messages provider contract.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer
  `role_used`: code-reviewer
  `fallback_used`: false
  `reviewer_role`: code-reviewer
  `status`: done
  `verdict`: accept
  `retry_count`: 0
  `key_findings`: Reviewer found no issues in the interim state; the old live-host failure path was replaced by a configured OpenAI-compatible provider fallback while preserving host adapters, native multimodal bypass, and text-only raw-image stripping. Later Kimi-specific diagnosis superseded only the Kimi provider shape, not the generic non-built-in fallback.
  `strongest_evidence`: Focused image preflight tests, full plugin check, setup offline suite, launcher validations, installed smoke, live config assertions, and installed provider-fallback smoke all passed.
  `next_action`: operator can retry the original GLM pasted-image prompt.
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-kimi-credential-precedence
  `checkpoint_title`: Kimi coding key precedence for image preflight (superseded)
  `plan_version`: PLAN.md as of 2026-06-23 plus 2026-06-24 HTTP 401 screenshot
  `acceptance_criteria`: interim live `kimi-coding` image preflight preferred `KIMI_CODE_API_KEY`, fell back to `KIMI_API_KEY`, failed before provider fetch when both were missing, source/runtime config and docs aligned, source and installed validation passed, and rollback was documented.
  `action_taken`: Updated interim plugin key resolution, source model config, docs, tests, installed artifact, and generated runtime config. Later diagnosis superseded this with the built-in Kimi Code Anthropic Messages contract, which uses `KIMI_API_KEY` with `KIMI_CODE_API_KEY` fallback.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer
  `role_used`: code-reviewer
  `fallback_used`: false
  `reviewer_role`: code-reviewer
  `status`: done
  `verdict`: accept
  `retry_count`: 1
  `key_findings`: First review found nullish API-key config values could become literal credentials; revision filters non-string refs and adds a missing-key no-fetch regression. Re-review accepted with no findings.
  `strongest_evidence`: Full plugin check passed with 146 tests, offline setup suite passed with 52 tests, installed smoke passed, and installed key-precedence smoke confirmed the interim coding key selection behavior.
  `next_action`: operator can retry the original GLM pasted-image prompt.
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-glm-path-rewrite-runtime
  `checkpoint_title`: GLM text-only prompt-shape runtime correction
  `plan_version`: PLAN.md as of 2026-06-24
  `acceptance_criteria`: successful image preflight for text-only GLM replaces pasted local image paths with image labels, prevents the main model from calling the unusable image-read path, preserves native multimodal bypass, refreshes the installed artifact after source validation, and proves both default and GLM launcher alias live prompts answer from preflight context.
  `action_taken`: Diagnosed the live GLM transcript, added successful-preflight local path rewriting plus an explicit use-preflight instruction, tightened source and installed-artifact tests, refreshed the live artifact with backups, and ran real default and GLM launcher alias GLM-5.2 image prompts.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer
  `role_used`: code-reviewer
  `fallback_used`: false
  `reviewer_role`: code-reviewer
  `status`: done
  `verdict`: accept
  `retry_count`: 0
  `key_findings`: The previous live failure was not Kimi 401 or missing image discovery; preflight succeeded, but GLM saw the raw local path, called `read`, received Pi's text-only image omission message, and answered from that tool result. Replacing analyzed paths with labels kept GLM on the preflight summary. Independent review found one low alias-merge gap for duplicate paths that resolve to the same file; the final source fix preserves all aliases and added a regression test.
  `strongest_evidence`: Direct installed preflight probe returned a prompt prefix beginning `[image-1; codex-clipboard-vNZuzN.png; analyzed by Stronk Pi image vision preflight]`; the installed alias probe rewrote both real and symlink paths; the default launcher alias with `--model neuralwatt/glm-5.2:xhigh -p ...` and the GLM launcher alias with `-p ...` both answered the image question, and their newest session transcripts had `read_tool_call=absent`.
  `next_action`: none
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-image-preflight-cli-status
  `checkpoint_title`: CLI/TUI image preflight status notifications
  `plan_version`: PLAN.md as of 2026-06-24 plus 2026-06-24 UX follow-up
  `acceptance_criteria`: text-only image preflight emits bounded Pi UI notifications for analyzing, completion, skipped images, and failure-note fallback; native multimodal bypass stays quiet; installed artifact smoke covers the status contract; live GLM image prompts still route through preflight without `read`.
  `action_taken`: Ran a read-only Stronk swarm with product-designer, explorer, and qa-tester roles; implemented the minimal `ctx.hasUI && ctx.ui.notify` status seam in the plugin input/preflight path; added status copy, bounded failure reason classification, unit tests, installed-artifact smoke assertions, docs, and a live runtime refresh.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: product-designer, explorer, qa-tester
  `role_used`: product-designer, explorer, qa-tester
  `fallback_used`: false
  `reviewer_role`: product-designer, explorer, qa-tester
  `status`: done
  `verdict`: accept
  `retry_count`: 0
  `key_findings`: The current runtime exposes no input-hook progress renderer or spinner API; the stable visible surface is `ctx.ui.notify(message, kind)`. The implementation therefore emits one bounded analyzing notification and one bounded terminal notification only when image preflight actually runs, skips, or fails.
  `strongest_evidence`: Focused image-preflight tests passed with UI notification capture; plugin `npm run check` passed with 151 tests plus `security-check: ok`; installed artifact smoke passed; direct installed real Kimi status probe passed without path/base64/API-key leakage; default and GLM launcher alias image prompts answered from preflight summaries and newest transcripts had `read_tool_call=absent`.
  `next_action`: none
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-image-preflight-animated-tui-indicator
  `checkpoint_title`: Animated TUI image preflight indicator
  `plan_version`: PLAN.md as of 2026-06-24 plus 2026-06-24 moving-status follow-up
  `acceptance_criteria`: interactive TUI image preflight shows visible movement while Kimi vision analysis is running; old bounded notifications still emit; RPC mode does not receive non-serializable widget factories; cleanup restores status, working message, working indicator, and widget state on completion, skip, or failure.
  `action_taken`: Inspected local Pi Mono extension UI, TUI loader, status, widget, and RPC implementations; added a plugin-side optional UI adapter that starts a plugin-owned below-editor animated widget during the `analyzing` phase and clears the keyed status/widget on terminal phases; added focused unit tests and installed-artifact smoke assertions.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer
  `role_used`: code-reviewer
  `fallback_used`: false
  `reviewer_role`: code-reviewer
  `status`: done
  `verdict`: accept
  `retry_count`: 1
  `key_findings`: Pi Mono exposes `ctx.ui.setWorkingIndicator`, `setWorkingMessage`, `setStatus`, and `setWidget`; the built-in working loader may not be visible before streaming starts and has no getter for prior customization, so the plugin uses only plugin-owned keyed status plus a temporary TUI widget for preflight-time movement and avoids the widget in RPC mode.
  `strongest_evidence`: Re-review accepted the revised adapter with no findings; focused image-preflight tests passed with 23 tests; plugin `npm run check` passed with 155 tests plus `security-check: ok`; source smoke, distribution validate/offline/unit checks, launcher validation, diff checks, installed smoke after refresh, and live GLM screenshot preflight passed.
  `next_action`: none
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-evidence-rich-vision-preflight
  `checkpoint_title`: Evidence-rich image vision preflight prompt and renderer
  `plan_version`: PLAN.md as of 2026-06-24 plus 2026-06-24 evidence-rich vision follow-up
  `acceptance_criteria`: vision prompt asks for evidence-rich structured context; renderer preserves old and new summary fields; text-only model guardrails prevent unsupported identity, absence, count, measurement, condition, layout, relationship, scene, document/chart, and UI claims; fail-soft context does not leak raw image/provider payloads; docs and ExecPlan state are consistent; validation passes.
  `action_taken`: Ran read-only Stronk swarm research, expanded the vision prompt/schema, added rich field rendering with bounded sections, added prompt/rendering/security regressions, updated public docs and ExecPlan wording, fixed raw failure-context leakage, and reran source/distribution verification.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer and technical-writer
  `role_used`: code-reviewer and technical-writer
  `fallback_used`: false
  `reviewer_role`: code-reviewer and technical-writer
  `status`: done
  `verdict`: accept
  `retry_count`: 1
  `key_findings`: First code review found fail-soft context used raw exception text; revision classifies failure context and adds data-URL/base64 leak coverage. First docs review found stale path-preservation wording; PLAN and LOGS now state analyzed local paths become stable labels while traceability is preserved in labels/context. Both re-reviews accepted.
  `strongest_evidence`: Focused image-preflight tests passed with 28 tests; plugin `npm run check` passed with 160 tests plus `security-check: ok`; source installed-artifact smoke, setup validation, offline setup suite, launcher validations, public-surface/path scans, diff checks, and independent re-reviews passed.
  `next_action`: operator approval is required before refreshing the live installed runtime artifact for this evidence-rich prompt change.
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-universal-image-schema
  `checkpoint_title`: Universal image vision preflight schema
  `plan_version`: PLAN.md as of 2026-06-24 plus operator universal-schema intent confirmation
  `acceptance_criteria`: vision prompt and injected context are image-type neutral, renderer preserves prior UI aliases and new universal fields, uncertainty and scoped not-visible evidence stay separate from inference, docs and ExecPlan state name the universal facets, validation passes, and live runtime refresh remains gated by operator approval.
  `action_taken`: Generalized the prompt and renderer around image type, scene/composition, subjects/entities, attributes/state, relationships/activity, visible text/symbols, structured content, domain-specific details, facts, uncertainty, scoped not-visible evidence, inference, and guardrails; added universal rendering tests; fixed singular uncertainty parsing/rendering; updated public docs and PLAN wording.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer and technical-writer
  `role_used`: code-reviewer and technical-writer
  `fallback_used`: false
  `reviewer_role`: code-reviewer and technical-writer
  `status`: done
  `verdict`: accept
  `retry_count`: 1
  `key_findings`: First docs review found PLAN still described only a generic structured summary and did not name the universal facets; PLAN now names those facets and avoids assuming interface/screen-capture input. First code review found singular `uncertainty` and fallback `Uncertainty:` headings could render under inference; the plugin now routes them to `Uncertainties And Limits` and has regression coverage. Both re-reviews accepted.
  `strongest_evidence`: Focused image-preflight tests passed with 30 tests; plugin `npm run check` passed with 162 tests plus `security-check: ok`; source smoke, setup validation, public-surface tests, targeted distribution unittests, offline setup suite, temp-HOME config refresh, launcher validations, stale wording scans, public path scans, diff whitespace checks, and independent re-reviews passed.
  `next_action`: operator approval is required before refreshing the live installed runtime artifact for this universal schema change.
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

- `checkpoint_id`: followup-multi-image-preflight-default
  `checkpoint_title`: 12-image preflight default and folder-read boundary
  `plan_version`: PLAN.md as of 2026-06-24 plus operator multi-image follow-up
  `acceptance_criteria`: source/config default and hard ceiling are 12 images, 12 images are analyzed in one request, the 13th supported image is skipped with bounded reporting, folder paths are not recursively expanded by prompt-time preflight, docs explain the prompt-time boundary, validation passes, and live runtime refresh remains gated by operator approval.
  `action_taken`: Ran read-only Stronk swarm with architect, explorer, and qa-tester roles; raised plugin default and ceiling to 12; widened prompt/attachment scan caps to 24; added focused tests for 12-image request shape, 13th-image skip behavior, and folder non-expansion; updated setup defaults, docs, PLAN, and LOGS.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: architect, explorer, qa-tester
  `role_used`: architect, explorer, qa-tester
  `fallback_used`: false
  `reviewer_role`: architect, explorer, qa-tester
  `fork_context_used`: false
  `status`: done
  `verdict`: accept
  `retry_count`: 0
  `key_findings`: Batching is not required for the 12-image bump because current preflight already sends one multi-image request and one request preserves cross-image comparison. Folder-discovered images are outside prompt-time preflight and were later handled by the `image_read` plugin tool.
  `strongest_evidence`: Focused image-preflight tests passed with 34 tests; plugin `npm run check` passed with 166 tests plus `security-check: ok`; source smoke, setup validation, manifest verifier, offline setup suite, temp-HOME config refresh, launcher validations, public-surface scans, and diff checks passed.
  `next_action`: operator approval is required before refreshing the live installed runtime artifact for this 12-image source/config change.
  `blocker`: none
  `decision_owner`: operator
  `resume_trigger`: approve runtime refresh

- `checkpoint_id`: followup-image-evidence-traceability
  `checkpoint_title`: Image-scoped evidence traceability and path redaction
  `plan_version`: PLAN.md as of 2026-06-24 plus operator evidence-traceability follow-up
  `acceptance_criteria`: rendered evidence IDs are image-scoped, duplicate local IDs stay unambiguous across multi-image prompts, already scoped cross-image references are preserved, literal OCR-like text is not corrupted into citations, skipped and failed path aliases are redacted from downstream text, vision-provider prompt text is sanitized, docs and ExecPlan state reflect the behavior, validation passes, and live runtime refresh remains operator-gated.
  `action_taken`: Added Image Evidence Index rendering; narrowed evidence scoping to leading IDs and explicit evidence fields by default; kept inference/guardrail sections citation-aware; sanitized analyzed, skipped, and failed image path aliases; sanitized vision request prompt text and request metadata; guarded mismatched summary-label fallback; added focused regression coverage; updated public docs and ExecPlan state.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: code-reviewer, qa-tester, technical-writer
  `role_used`: code-reviewer, qa-tester, technical-writer
  `fallback_used`: false
  `reviewer_role`: code-reviewer, qa-tester, technical-writer
  `fork_context_used`: false
  `status`: done
  `verdict`: accept
  `retry_count`: 1
  `key_findings`: First review found broad evidence rewriting could corrupt OCR, skipped paths could leak, vision request prompt text could include raw local paths, and tests/logs needed more coverage. Revisions fixed those issues and all re-reviews accepted.
  `strongest_evidence`: Focused image-preflight tests passed with 40 tests; plugin `npm run check` passed with 172 tests plus `security-check: ok`; source installed-artifact smoke, setup validation, public-surface tests, manifest verifier tests, offline setup suite, launcher validations, and diff whitespace checks passed.
  `next_action`: operator approval is required before refreshing the live installed runtime artifact for this source change.
  `blocker`: none
  `decision_owner`: operator
  `resume_trigger`: approve runtime refresh

- `checkpoint_id`: followup-agentic-image-read
  `checkpoint_title`: Agentic Image Read tool for text-only models
  `plan_version`: PLAN.md as of 2026-06-25
  `acceptance_criteria`: `image_read` is registered with label `Image Read`; text-only models can request vision analysis of explicit local image paths and one bounded directory scan; the tool reuses configured image preflight routing, limits, MIME checks, timeout, renderer, Image Evidence Index, image-scoped evidence IDs, and safe failures; unsupported, oversized, unsafe, missing, duplicate, excess, hidden, symlink, and provider-failure cases are bounded and redacted; prompt-time preflight and native multimodal behavior remain unchanged; docs and guard policy are updated; validation passes; live runtime refresh remains operator-gated.
  `action_taken`: Added the `image_read` plugin tool and schema; implemented explicit path and bounded deterministic directory collection; hardened directory scans with supported-extension prefiltering, hidden/symlink root rejection, protected-path checks, recursion opt-in, max-image pre-read limiting, skipped-reason bounds, and provider-success summary redaction; routed images through the existing vision preflight path; updated installed-artifact smoke, distribution guard allowlist/tests, public docs, PLAN, and LOGS.
  `gate_mode`: blocking
  `independence_mode`: independent
  `role_requested`: architect, code-reviewer, technical-writer
  `role_used`: architect, code-reviewer, technical-writer
  `fallback_used`: false
  `reviewer_role`: architect, code-reviewer, technical-writer
  `fork_context_used`: false
  `status`: done
  `verdict`: accept
  `retry_count`: 4
  `key_findings`: Initial design review accepted a registered plugin tool rather than a new MCP server. Code review then found directory scans should not enqueue every file, local image reads should be bounded before normalization, hidden/symlink directory roots should be rejected, successful provider summaries needed path/data redaction, and rendered object-key redaction needed direct coverage. Docs review found the operator smoke command needed plugin-repo context and the log needed implementation/validation/runtime-refresh status. All findings were revised and re-reviewed to accept.
  `strongest_evidence`: Focused image/preflight tests passed with 51 tests; full plugin `npm run check` passed with 181 tests plus `security-check: ok`; `node --check src/index.mjs` passed; source installed-artifact smoke passed; distribution guard/public-surface/unit/offline/setup validations passed; launcher/model probes passed for `stronkpi`, installed `stronkpi`, GLM text-only, and Kimi image-capable routes; public/path scans, stale-wording scans, and `git diff --check` passed in both repos.
  `next_action`: none; operator-approved artifact-only refresh completed on 2026-06-25.
  `blocker`: none
  `decision_owner`: none
  `resume_trigger`: none

## Session End

[2026-06-23 23:24 +0800] Source, docs, tests, and ExecPlan state were reconciled before live runtime refresh.

[2026-06-24 00:57 +0800] Live runtime/plugin refresh is complete and validated.
No ExecPlan tasks remain unchecked.

[2026-06-24 01:16 +0800] Follow-up NeuralWatt GLM runtime config restore is complete.
The existing GLM shell launcher function was read for reference only and was not edited.
The durable Stronk Pi source config now includes `neuralwatt/glm-5.2` and `neuralwatt/glm-5.2-short` as text-only OpenAI-compatible models using `$NEURALWATT_API_KEY`.
Live `~/.stronk-pi/agent/settings.json` and `~/.stronk-pi/agent/models.json` were refreshed from source after backups under `~/.stronk-pi/agent/backups/2026-06-24/settings.json.bak.20260624-010920` and `~/.stronk-pi/agent/backups/2026-06-24/models.json.bak.20260624-010920`.
Validation passed with source JSON checks, `bin/stronkpi --validate-only`, `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`, interactive-shell default launcher validation, GLM launcher validation, model-list checks showing `neuralwatt` GLM entries, direct Pi registry resolution for `neuralwatt/glm-5.2:xhigh`, installed plugin GLM image preflight smoke, and `git diff --check` for the touched source config files.

[2026-06-24 01:25 +0800] Follow-up web search and subagent harness defaults fix is complete.
The launcher now reads runtime `[harness]` defaults and exports `STRONK_PI_SEARCH_PROVIDER` from `~/.stronk-pi/config/defaults.toml` unless an explicit shell override is already set.
Subagent facade and adapter values now come from the same runtime defaults, keeping the configured `stronk` and `intercom` mode active for plugin harness runs.
Validation passed with targeted harness env tests, full manifest verifier tests, the offline setup suite, installed web search provider smoke, installed subagent facade smoke, setup validate, launcher validate, interactive GLM launcher validate, py_compile, and diff whitespace checks.
No dotfiles or secret values were edited.

[2026-06-24 02:35 +0800] Follow-up image routing runtime refresh is complete.
Diagnosis confirmed source image preflight worked, but the live installed artifact was stale and its `handleInput` path did not contain `buildImageVisionPreflight`.
The installed-artifact smoke was tightened to assert pasted local image path preflight, then the live artifact was refreshed from the verified source package.
Pre-refresh backup: `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-023249.tgz`.
Post-first-refresh consistency backup: `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.post-first-refresh.bak.20260624-023420.tgz`.
Validation passed with focused source image-preflight tests, direct source pasted-path smoke, full plugin `npm run check`, installed artifact smoke, direct installed pasted-path smoke, launcher validation, interactive default and GLM launcher validation, installed artifact source scan, and diff whitespace checks in both repos.
Rollback path: restore the pre-refresh backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, then rerun launcher validation and installed artifact smoke.

[2026-06-24 03:18 +0800] Follow-up direct provider fallback runtime refresh was completed, then superseded.
The live GLM launcher failure was not image discovery; it was a missing host completion adapter in the Pi context.
That interim installed plugin fell back to a configured OpenAI-compatible `kimi-coding/kimi-for-coding` vision provider when no host adapter existed, and live runtime model config declared that provider.
Later git-history and live endpoint diagnosis showed this was the wrong Kimi contract.
The current fix removes the setup-managed `kimi-coding` provider from generated `models.json` and uses Pi's built-in Kimi Code Anthropic Messages contract instead.
Validation passed with focused source regression tests, full plugin checks, distribution offline/config tests, independent review, archive checks, installed artifact smoke, launcher validation for `stronkpi`, default launcher alias, and GLM launcher alias, live config assertions, and an installed mocked provider-fallback smoke.
Rollback path: restore the timestamped artifact, config, and agent backups from the 2026-06-24 03:13 refresh, then rerun launcher validation and installed smoke.

[2026-06-24 03:47 +0800] Follow-up Kimi credential precedence runtime refresh was completed, then superseded.
At that point the live HTTP 401 path appeared to be credential precedence, so the interim installed plugin and generated runtime model config preferred `KIMI_CODE_API_KEY`.
Later diagnosis showed the durable fix is to use the built-in Kimi Code provider contract.
The current plugin fallback uses `KIMI_API_KEY`, with `KIMI_CODE_API_KEY` as fallback, and calls `https://api.kimi.com/coding/v1/messages` with `x-api-key` and `User-Agent: KimiCLI/1.5`.
Validation passed with focused credential regressions, full plugin checks, offline setup tests, independent re-review, archive checks, installed artifact smoke, launcher validation, live Kimi config assertions, and installed key-precedence smoke.
Rollback path: restore the 2026-06-24 03:41 artifact/config/agent backups, then rerun launcher validation and installed smoke.

[2026-06-24 04:29 +0800] Source-side Kimi built-in provider correction is validated and ready for approved live refresh.
The live refresh target is the installed `stronk-pi-plugin-0.1.0` artifact and setup-managed runtime config under `~/.stronk-pi`.
Rollback will restore the timestamped artifact, config, and socket-excluding agent backups created immediately before refresh.

[2026-06-24 04:56 +0800] Follow-up GLM prompt-shape runtime correction is complete.
The live transcript confirmed image preflight was running and Kimi was returning a summary, but GLM still called the image `read` tool because the original pasted local path remained in the forwarded prompt.
The source plugin now rewrites successfully analyzed local image paths to stable image labels and tells the main model to use the preflight block as the image input for the turn.
The installed-artifact smoke now asserts the same path rewrite.
Independent review found a low-risk alias gap where two textual paths resolving to the same real file could drop the later spelling before prompt rewrite.
The final source fix preserves all path aliases for a normalized image and adds a symlink-alias regression test.
Operator-approved refresh replaced the installed `stronk-pi-plugin-0.1.0` artifact and refreshed setup-managed config after the final alias fix.
Final refresh backups:
  artifact `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-045416.tgz`;
  config `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-045416.tgz`;
  socket-excluding agent `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-045416.tgz`.
Validation passed with focused image preflight tests, plugin `npm run check`, plugin syntax and diff checks, installed artifact smoke, installed alias path rewrite probe, `bin/stronkpi --validate-only`, installed `stronkpi --validate-only`, interactive default launcher alias validation, interactive GLM launcher alias validation, direct installed real Kimi preflight path rewrite probe, default launcher alias GLM image prompt, GLM launcher alias image prompt, distribution setup validation, distribution offline suite, targeted distribution unittests, and diff checks in both repos.
The newest default and GLM launcher alias session transcripts both showed the forwarded prompt starting with the analyzed image label and `read_tool_call=absent`.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, restore config and agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent`, then rerun `stronkpi --validate-only`, GLM launcher alias validation, and `npm run smoke:installed`.

[2026-06-24 16:08 +0800] Follow-up CLI/TUI image preflight status notifications are complete.
Read-only Stronk swarm routing:
  product-designer proposed the bounded status states and copy;
  explorer confirmed the safe implementation seam is `ctx.hasUI` plus `ctx.ui.notify(message, kind)`;
  qa-tester proposed the focused source, installed-smoke, and live validation matrix.
FORK_CONTEXT_USED=false for all swarm agents, and all agents were closed after synthesis.
The plugin now emits UI notifications when a text-only prompt triggers image preflight:
  `Stronk Pi detected N images for a text-only model; analyzing with vision preflight.`;
  `Image vision preflight complete: analyzed N images.`;
  skipped-image and failure-note variants use bounded counts and classified reasons.
Native multimodal image handling remains quiet.
Docs now mention bounded UI notifications when the Pi UI surface is available.
Operator-approved refresh replaced the installed `stronk-pi-plugin-0.1.0` artifact and refreshed setup-managed config.
Final refresh backups:
  artifact `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-160509.tgz`;
  config `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-160509.tgz`;
  socket-excluding agent `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-160509.tgz`.
Validation passed with focused image-preflight status tests, plugin `npm run check`, plugin syntax checks, plugin diff checks, installed artifact smoke, installed real Kimi status probe, launcher validation for `stronkpi` plus default and GLM launcher aliases, live default and GLM launcher alias image prompts, newest transcript checks showing `read_tool_call=absent`, distribution setup validation, distribution offline suite, targeted distribution unittests, public-surface tests, and distribution diff checks.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, restore config and agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent`, then rerun `stronkpi --validate-only`, GLM launcher alias validation, and `npm run smoke:installed`.

[2026-06-24 16:21 +0800] Follow-up animated TUI image preflight indicator started.
Pi Mono source inspection found the current extension UI can set footer status, working indicator/message, and temporary widgets.
Because input hooks run before normal model streaming, the source plugin now uses a temporary below-editor animated widget during image vision preflight, while also customizing the working indicator for any streaming-visible path.
The widget factory is guarded to TUI mode so RPC mode only receives serializable status and notification events.
Focused source image-preflight tests passed with 22 tests, including animation-frame advancement and cleanup.

[2026-06-24 16:29 +0800] Independent code review returned revise for the first animated TUI adapter.
The reviewer found that mutating Pi's shared working message/indicator could clobber prior global loader customization because the extension API has no getter or scoped restore token.
The source plugin was revised to stop touching shared working loader state and to rely on plugin-owned keyed status plus the temporary below-editor animated widget.
Docs were aligned to say the plugin clears its own status/widget rather than restoring global UI state.

[2026-06-24 16:36 +0800] Follow-up animated TUI image preflight indicator source work is complete and accepted.
Independent re-review accepted the revised plugin-owned status/widget adapter with no findings.
Validation passed with focused image-preflight tests, full plugin checks, source smoke using `STRONK_PI_SMOKE_PLUGIN=src/index.mjs`, distribution setup validation, distribution offline suite, targeted distribution unittests, public-surface scans, launcher validation for `stronkpi`, the default launcher alias, and the GLM launcher alias, and diff whitespace checks in both repos.
No live `~/.stronk-pi` runtime/plugin artifact refresh has been performed for this animated indicator change yet.

[2026-06-24 17:28 +0800] Operator-approved animated TUI indicator runtime refresh is complete.
The first refresh attempt stopped before artifact replacement because the backup tar tried to include its own `config/backups` archive and `npm pack --prefix` resolved from the setup repo.
The successful rerun excluded backup folders from backup archives and packed from inside `stronk-pi-plugin`.
Final refresh backups:
  artifact `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-172621.tgz`;
  config `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-172621.tgz`;
  socket-excluding agent `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-172621.tgz`.
Installed validation passed with `npm run smoke:installed`, source and installed `stronkpi --validate-only`, interactive-shell default alias validation, and interactive-shell GLM alias validation.
Installed artifact scan confirmed production code uses `setWidget` for `stronk-pi-image-vision-preflight` and does not call `setWorkingMessage` or `setWorkingIndicator`.
A live GLM alias prompt against the operator screenshot answered from the image summary; newest transcript had preflight context, one analyzed image, and no `read` tool call.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, restore config and agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent`, then rerun `stronkpi --validate-only`, default alias validation, GLM alias validation, and `npm run smoke:installed`.

[2026-06-24 18:03 +0800] Follow-up image preflight output-token config started.
The previous implementation used an internal 800-token default for direct provider fallbacks and did not expose the response budget in the public `[image_preflight]` config contract.
The source plugin now exposes `max_output_tokens`, defaults it to 4096, clamps it from 1024 to 8192, and passes the clamped numeric value into OpenAI-compatible and Anthropic Messages provider payloads.
Focused image-preflight tests passed with 25 tests, including default/min/max/env config assertions and a direct provider payload assertion proving a 12000 config value clamps to 8192.
Setup config refresh regression passed for `config/defaults.toml` including `max_output_tokens = 4096`.

[2026-06-24 18:03 +0800] Follow-up image preflight output-token config source validation is complete.
Independent read-only code review found no source-level issues and confirmed a live runtime/plugin refresh is still required before the installed launcher uses the new plugin default.
The reviewer noted one residual coverage gap for Anthropic Messages clamp propagation; a focused regression now covers low-clamp propagation to the Anthropic payload while the OpenAI-compatible regression covers high-clamp propagation.
Validation passed with focused image-preflight tests, full plugin `npm run check` with 158 tests and `security-check: ok`, plugin syntax checks, source installed-artifact smoke using the local source plugin, setup validation, temp-HOME `refresh-config` assertion for `max_output_tokens = 4096`, distribution py_compile, targeted distribution unittest suites, offline setup suite, source launcher validation, default launcher alias validation, GLM launcher alias validation, public-surface checks, and diff whitespace checks in both repos.
No live runtime/plugin artifact refresh was performed for this token-budget change.

[2026-06-24 18:06 +0800] Operator-approved image preflight output-token runtime refresh is complete.
The installed `stronk-pi-plugin-0.1.0` artifact was backed up and replaced from the verified local source package, then setup-managed runtime config was refreshed.
Final refresh backups:
  artifact `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-180430.tgz`;
  config `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-180430.tgz`;
  socket-excluding agent `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-180430.tgz`.
Installed validation passed with installed-artifact smoke, source and installed `stronkpi --validate-only`, default launcher alias validation, GLM launcher alias validation, installed artifact source scan showing the 4096 default and 1024 to 8192 clamp constants, runtime config scan showing `max_output_tokens = 4096`, refresh JSON validation, and a direct installed-plugin mocked provider probe proving `STRONK_PI_IMAGE_PREFLIGHT_MAX_OUTPUT_TOKENS=8192` reaches the provider payload as `max_tokens=8192`.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, restore config and agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent`, then rerun `stronkpi --validate-only`, default launcher alias validation, GLM launcher alias validation, and `npm run smoke:installed`.

[2026-06-24 18:34 +0800] Follow-up evidence-rich vision preflight prompt started after a live UI critique session showed the text-only model overclaimed layout details from a short vision summary.
Read-only Stronk swarm routing:
  technical-researcher recommended an evidence-first schema with visible text spans, layout, UI elements, tables/charts, facts, uncertainty, scoped negative evidence, and inference evidence ids;
  product-designer recommended downstream guardrails that require visible evidence for density, layout, and missing-feature claims;
  explorer confirmed the current implementation prompt and renderer live in `stronk-pi-plugin/src/index.mjs`, and that the existing renderer did not enforce item caps or preserve richer schema fields.
FORK_CONTEXT_USED=false for all swarm agents, and all agents were closed after synthesis.
The source plugin now asks the configured vision model for evidence-rich JSON instead of a short caption-like summary.
The injected context can render overview, quality/scope, layout, visible text, screen/data details, counts/density, observed facts, uncertainties, scoped negative evidence, inferences, and guardrails; this was later generalized to universal image-type neutral sections.
The context block now tells text-only models that omitted, unknown, unreadable, cropped, or not-visible details are unavailable, not absent.
Focused image-preflight source tests passed with 28 tests, including prompt-contract coverage and a rich-schema rendering regression that prevents `[object Object]` leaks.
No live `~/.stronk-pi` runtime/plugin artifact refresh has been performed for this evidence-rich prompt change yet.

[2026-06-24 18:45 +0800] Evidence-rich vision preflight prompt source validation and review are complete.
Independent code review first found that fail-soft preflight context could inject raw provider exception text into the downstream prompt even after raw images were stripped.
The plugin now classifies failure context with the same bounded safe failure reason used for status notifications, and a regression throws a data URL plus base64-shaped image payload to prove neither reaches `result.text`.
Independent docs review first found stale ExecPlan wording from the earlier path-preservation decision; PLAN and LOGS now state that successfully analyzed local image paths are replaced with stable labels while labels/context preserve traceability.
Both re-reviews accepted after revision.
Validation passed with focused image-preflight tests, full plugin checks, plugin syntax check, source installed-artifact smoke, setup validation, distribution public-surface tests, targeted distribution unittests, distribution py_compile, offline setup suite, launcher validation for `stronkpi`, the default launcher alias, and the GLM launcher alias, temp-HOME config refresh, public-surface/path scans, and diff whitespace checks in both repos.
No live `~/.stronk-pi` runtime/plugin artifact refresh has been performed for this evidence-rich prompt change yet.

[2026-06-24 20:01 +0800] Follow-up universal image schema revision started after operator feedback that the previous evidence-rich schema still leaned too heavily toward UI screenshots.
The source prompt now uses an image-type neutral shape with image type, scene/composition, subjects/entities, attributes/state, relationships/activity, visible text/symbols, structured content, domain-specific details, facts, uncertainty, scoped negative evidence, and inference guardrails.
The renderer now groups rich fields under universal section headings while still accepting prior UI/screenshot field aliases.
Focused image-preflight source tests passed with 29 tests, including a new photo plus chart/document rendering regression.
Docs now describe the preflight block as universal visual understanding rather than interface-specific evidence.
No live `~/.stronk-pi` runtime/plugin artifact refresh has been performed for this universal schema change yet.

[2026-06-24 20:14 +0800] Universal image schema source validation and review are complete.
Independent docs review first found that PLAN.md still described a generic structured summary; PLAN now names the universal evidence facets and avoids assuming interface/screen-capture input.
Independent code review first found that singular `uncertainty` and fallback `Uncertainty:` headings could be grouped with inference; the plugin now routes them to `Uncertainties And Limits` and includes regression coverage for both structured and fallback response paths.
Both re-reviews accepted with no remaining findings.
FORK_CONTEXT_USED=false for the review agents.
Validation passed with focused image-preflight tests, full plugin checks, plugin syntax check, source installed-artifact smoke, setup validation, distribution public-surface tests, targeted distribution unittests, distribution py_compile, offline setup suite, temp-HOME config refresh, launcher validation for `stronkpi`, the default launcher alias, and the GLM launcher alias, public-surface/path scans, stale wording scans, and diff whitespace checks in both repos.
No live `~/.stronk-pi` runtime/plugin artifact refresh has been performed for this universal schema change yet.

[2026-06-24 21:10 +0800] Operator-approved universal image schema runtime refresh is complete.
The installed `stronk-pi-plugin-0.1.0` artifact was backed up and replaced from the verified local source package, then setup-managed runtime config was refreshed.
Final refresh backups:
  artifact `~/.stronk-pi/artifacts/backups/2026-06-24/stronk-pi-plugin-0.1.0.bak.20260624-210936.tgz`;
  config `~/.stronk-pi/config/backups/2026-06-24/config.bak.20260624-210936.tgz`;
  socket-excluding agent `~/.stronk-pi/agent/backups/2026-06-24/agent.no-sockets.bak.20260624-210936.tgz`.
The immediate pre-refresh package directory was also kept at `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260624-210936`.
Installed validation passed with installed-artifact smoke, source and installed `stronkpi --validate-only`, default launcher alias validation, GLM launcher alias validation, `bin/stronkpi --diagnose --json`, runtime config scan for `[image_preflight]`, and installed artifact source scan proving the universal prompt and uncertainty/inference routing are present.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260624-210936` back to `package` for the artifact-only rollback; restore config and agent backups into `~/.stronk-pi/config` and `~/.stronk-pi/agent` if runtime config must be reverted, then rerun `stronkpi --validate-only`, default alias validation, GLM alias validation, and `npm run smoke:installed`.

[2026-06-24 21:59 +0800] Follow-up 12-image source/config change is complete and validated, but not refreshed into live `~/.stronk-pi` runtime state.
The source plugin now accepts up to 12 turn-supplied images in one preflight request and skips the 13th with bounded reporting.
Docs clarify that folder-discovered images are outside prompt-time preflight; the later 2026-06-25 follow-up resolves this with `image_read`.

[2026-06-24 22:52 +0800] Follow-up image evidence traceability source change is complete and validated, but not refreshed into live `~/.stronk-pi` runtime state.
The source plugin now emits an Image Evidence Index, scopes evidence IDs by image label, preserves literal OCR-like evidence-shaped text, sanitizes raw image paths before both vision-provider and text-only prompts, removes local path fields from request metadata, and handles partial/mismatched summaries without assigning evidence to the wrong image.
Read-only Stronk swarm re-review accepted the revised code, tests, and docs.

[2026-06-24 23:27 +0800] Operator-approved artifact-only runtime refresh for image evidence traceability is complete.
The installed plugin package now contains the Image Evidence Index renderer, scoped evidence reference handling, partial-summary traceability, and request metadata path stripping.
Setup-managed config was not refreshed because this follow-up did not change config defaults.

[2026-06-25 01:10 +0800] Follow-up agentic `image_read` source change is complete and validated, but not refreshed into live `~/.stronk-pi` runtime state.
The source plugin now registers `image_read` with label `Image Read` for text-only model workflows that discover local image files after the prompt starts.
The tool accepts one explicit image path in `paths`, or one bounded `directory` scan that resolves exactly one image, keeps recursion opt-in, rejects hidden and symlink directory roots, skips hidden/protected/symlink scan entries, prefilters directory candidates by supported image extension before magic-byte validation, and returns bounded skipped-image reasons.
`image_read` reuses the existing configured vision preflight model route, provider invocation, MIME checks, byte limits, timeout, evidence renderer, Image Evidence Index, image-scoped evidence IDs, and safe failure classification.
The distribution guard now allows `image_read` as a distribution-owned safe tool class.
Focused plugin tests, full plugin check, installed-artifact smoke using the source plugin path, distribution guard and setup validation, offline setup suite, launcher validation, public/path scans, stale-wording scans, and diff whitespace checks passed.
Read-only independent review used `code-reviewer` and `technical-writer` with `fork_context=false`; initial findings hardened directory scan bounds, corrected docs/log reconciliation, and added successful-summary redaction for provider-echoed paths, data URLs, long base64-like payloads, and object keys.
No live runtime refresh was performed.

[2026-06-25 01:16 +0800] Final `image_read` review loop accepted after the object-key redaction regression was strengthened.
All follow-up checklist items are complete.
The next operator decision is whether to approve a live installed artifact refresh for the source plugin change.

[2026-06-25 01:17 +0800] Operator-approved artifact-only runtime refresh for `image_read` is complete.
The installed `stronk-pi-plugin-0.1.0` artifact was backed up and replaced from the verified local source package.
Setup-managed config was not refreshed because this follow-up did not change config defaults.
Artifact backup: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-011707.tgz`.
Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-011707`.
Validation passed with installed artifact smoke, source and installed `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, installed artifact source scan for `image_read` and successful-summary redaction, GLM text-only model-list check, and Kimi image-capable model-list check.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-011707` back to `package`, then rerun `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, and `npm run smoke:installed` from the `stronk-pi-plugin` source repo.

[2026-06-25 02:19 +0800] Operator requested a clean-code/dead-code and architecture alignment pass after the initial `image_read` refresh.
Read-only Stronk swarm used `code-reviewer`, `architect`, and `security-reviewer` roles with `fork_context=false`.
Initial findings removed stale distribution guard allowlist entries for `get_search_content` and `stronk_fetch_content`, removed dead directory-scan queue bookkeeping, corrected runtime config precedence wording, and hardened explicit `image_read` path handling.
Follow-up review found hidden ancestor and realpath directory edge cases plus provider-bound prompt redaction gaps.
The source plugin now evaluates hidden segments relative to the logical and real workspace root, rejects hidden realpath directory roots before enumeration, checks recursive child realpaths before enqueue, redacts raw image data and unrelated local paths in `image_read` questions and provider summaries, and applies the same local-path/image-data redaction to shared prompt-time vision request text before provider calls.
Regression coverage now includes hidden cwd ancestors, hidden realpath directory roots, `/etc/passwd`, `/root/.ssh/id_ed25519`, `.ssh`, and raw data URL redaction in both `image_read` and prompt-time preflight provider requests.
The final architecture and security re-reviews accepted with no remaining findings.
The only accepted residual clean-code note is small duplication between prompt-time image collection and `image_read` collection; reviewers considered it acceptable because it preserves the critical boundary that prompt-time preflight does not scan folders.
Validation passed with focused image/tool tests (54 passed), full plugin `npm run check` (184 tests plus `security-check: ok`), plugin syntax checks, source installed-artifact smoke, distribution guard/public-surface/manifest/MCP tests (51 passed), setup validation, offline setup suite (54 tests plus install/update/run dry-runs), source and installed launcher validation, GLM text-only and Kimi image-capable model-list checks, public/path scans, and diff whitespace checks in both repos.
Operator approval for a new artifact-only refresh is already present in chat; setup-managed config refresh is not required because this cleanup only changes plugin source and distribution docs/tests.

[2026-06-25 02:20 +0800] Operator-approved artifact-only runtime refresh for the clean-code/security cleanup is complete.
The installed `stronk-pi-plugin-0.1.0` artifact was backed up and replaced from the verified local source package.
Setup-managed config was not refreshed because this cleanup did not change setup-managed config defaults.
Artifact backup: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-022009.tgz`.
Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-022009`.
Validation passed with installed artifact smoke, source and installed `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, GLM text-only and Kimi image-capable model-list checks, installed artifact source scan for `image_read`, `imageCandidateHasHiddenSegment`, shared request redaction, and `/root|/etc` local-path redaction, plus a direct installed-plugin probe proving both `image_read` and prompt-time preflight redact `/etc/passwd`, `/root/.ssh/id_ed25519`, `.ssh`, raw data URLs, and local image paths before provider request text or model-facing output.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-022009` back to `package`, then rerun `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, and `npm run smoke:installed` from the `stronk-pi-plugin` source repo.

[2026-06-25 03:05 +0800] Follow-up fix for `image_read` full-yolo path handling is complete in source, but not refreshed into live `~/.stronk-pi` runtime state.
Operator feedback showed `image_read` skipped explicit screenshot paths with `path outside allowed image roots` during a GLM full-yolo session.
Local Codex inspection confirmed Codex full-disk mode maps to unrestricted filesystem access (`danger-full-access` / disabled sandbox), so `image_read` should not impose the allowed-root gate in equivalent Pi full-yolo/full-disk modes.
The source plugin now keeps the allowed-root gate for default/restricted modes, bypasses only that gate for full-disk modes, and still rejects hidden, protected, symlink, unreadable, oversized, unsupported, duplicate, and excess images.
Prompt-time preflight remains root-bounded and unchanged.
Directory scanning remains deterministic and bounded; large directories are read through a capped directory iterator before sorting, and recursive scans still require explicit opt-in and scan-root containment.
Provider request text and model-facing output now redact broader local paths, including quoted paths and image paths with spaces, without corrupting public URLs, MIME tokens, model names, or ratio-like text.
Read-only Stronk swarm used architect, code-reviewer, and security-reviewer roles with `fork_context=false`.
Initial findings corrected mode precedence when default permission metadata and full-disk sandbox metadata coexist, added prompt-time regression coverage, fixed an uncapped `readdirSync().sort()` denial-of-service risk, broadened path redaction, and then narrowed the redactor to avoid over-redacting non-path slash tokens.
Validation passed with full plugin `npm run check` (189 tests plus `security-check: ok`), focused image/preflight coverage inside that suite, plugin syntax check, plugin `git diff --check`, and the amended image feature commit.
No live artifact refresh has been performed for this full-yolo path handling fix.

[2026-06-25 03:10 +0800] Operator-approved artifact-only runtime refresh for the `image_read` full-yolo path handling fix is complete.
Direct pushes to `main` were blocked by GitHub branch protection, so the plugin commits were pushed to `feat/agentic-image-read` and the distribution commits were pushed to `feat/image-read-setup-release`.
The installed `stronk-pi-plugin-0.1.0` package was backed up and replaced from the verified local source package.
Setup-managed config was not refreshed because this fix only changes plugin source behavior.
Artifact backup: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-030855.tgz`.
Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-030855`.
Validation passed with installed artifact smoke, source and installed `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, installed default/Kimi and GLM launcher validation, installed plugin syntax check, and a direct installed-plugin `image_read` probe proving a full-yolo outside-root PNG is analyzed instead of skipped for `path outside allowed image roots`.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-030855` back to `package`, then rerun `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, and `npm run smoke:installed` from the `stronk-pi-plugin` source repo.

[2026-06-25 03:18 +0800] Follow-up fix for the live registered-tool callback shape is complete and refreshed.
The failed external-folder image-read session proved the previous probe was too shallow: the installed registered `image_read` callback did not receive permission metadata, so the code still inferred restricted allowed roots.
The source plugin now enforces allowed image roots only for explicit restricted/default modes.
Full-disk modes bypass the root gate, and missing or unknown permission metadata no longer silently becomes restricted for explicit `image_read`.
Prompt-time image preflight remains unchanged and root-bounded.
Regression coverage now includes the registered-tool execution shape with no permission metadata and an `auto` mode case.
Validation passed with focused image/preflight tests (59 passed), full plugin `npm run check` (191 tests plus `security-check: ok`), plugin syntax check, and plugin diff whitespace check.
The plugin branch `feat/agentic-image-read` now includes `97803a0 fix(image): do not infer restricted roots without mode`.
Operator-approved artifact-only refresh replaced the installed `stronk-pi-plugin-0.1.0` package again.
Artifact backup: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-031824.tgz`.
Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-031824`.
Installed validation passed with installed artifact smoke, source and installed `stronkpi --validate-only`, GLM launcher validation, and a direct installed registered-tool probe against an external Downloads-folder image directory proving 3 images analyze with 0 skipped and no `path outside allowed image roots` result.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-031824` back to `package`, then rerun `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, and `npm run smoke:installed` from the `stronk-pi-plugin` source repo.

[2026-06-25 04:00 +0800] Follow-up prompt-time preflight extended-analysis artifacts started after a persisted three-image session showed a preflight block ending with `[truncated by Stronk Pi]`.
Read-only Stronk design swarm used `explorer` and `architect` roles with `fork_context=false`; both found that prompt-time `renderVisionContext` truncates the injected block at 12000 characters and provider output budgeting was effectively per multi-image request.
The source plugin now keeps the inline prompt-time preflight block bounded, saves extended bounded sanitized prompt-time analysis under private session state when session metadata is available, exposes only an opaque `image_preflight_read` handle, and lets text-only models read that artifact in bounded chunks.
The source plugin also scales prompt-time vision request output tokens by prompt image count while preserving the configured per-image clamp, one multi-image request, and an aggregate hard cap.
The follow-up hardening makes `image_preflight_read` fail closed without a verified session binding, denies cross-session artifact reads, derives transcript-only session directories from transcript filenames, strips path metasegments from artifact directories, and surfaces whether the extended artifact was capped.
The distribution guard validates the `image_preflight_read` handle shape before treating the tool as distribution-safe.
Validation passed with plugin syntax check, focused artifact/session/token/custom-tool tests, full plugin `npm run check` (194 tests plus `security-check: ok`), source installed-artifact smoke, distribution guard matrix, distribution public-surface tests, distribution offline validation (55 tests), setup validation, source and installed `stronkpi --validate-only`, short-wrapper validation, GLM wrapper validation, `bin/stronkpi --diagnose --json`, path/stale-wording scans, and diff whitespace checks in both repos.
Read-only Stronk swarm verification used code-reviewer, security-reviewer, and qa-tester with `fork_context=false`.
Security found no remaining findings after hardening.
QA passed source behavior and confirmed the live installed plugin artifact is still stale for this feature.
Code review found one low stale "full" wording issue in the tool prompt snippet; the final source changed it to "extended" and reran syntax plus focused registration/artifact tests.
No live `~/.stronk-pi` plugin artifact refresh was performed for this prompt-time artifact follow-up.
The installed `stronkpi` wrapper points at this source repo, so the distribution guard change is active through the source-linked wrapper; the next operator decision is whether to approve an artifact-only refresh for `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.

[2026-06-25 04:51 +0800] Operator-approved artifact-only runtime refresh for prompt-time extended image preflight artifacts is complete.
The installed `stronk-pi-plugin-0.1.0` package was backed up and replaced from the verified local plugin source package.
Setup-managed config was not refreshed because this follow-up changes plugin source behavior and distribution guard/docs/tests, not setup-owned config defaults.
Final refresh backup: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-045026.tgz`.
Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-045026`.
Installed validation passed with installed artifact symbol scan for `image_preflight_read`, `writeImagePreflightArtifact`, `Extended Image Analysis Artifact`, and capped-artifact output; `npm run smoke:installed`; source and installed `stronkpi --validate-only`; short-wrapper validation; GLM wrapper validation; `bin/stronkpi-setup validate`; `bin/stronkpi --diagnose --json`; and a direct installed artifact smoke that created a prompt-time image preflight artifact, read it through `image_preflight_read`, confirmed `Artifact capped: no`, and confirmed no-session read denial.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-045026` back to `package`, then rerun `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, GLM wrapper validation, and `npm run smoke:installed` from the `stronk-pi-plugin` source repo.

[2026-06-25 05:02 +0800] Follow-up diagnosis of persisted session `019efb69...6378` found the refreshed code did run and did save an extended image preflight artifact.
The session prompt contained `Extended Image Analysis Artifact` with handle `image-preflight-61256c53-...`, and the artifact existed under private session state with 13,595 characters and `truncated=false`.
The inline prompt block was still capped at 12,000 characters by design, so it ended with `[truncated by Stronk Pi]`; the assistant answered from the bounded inline block instead of calling `image_preflight_read`.
The real bug found in that session was provider evidence-ID drift in the three-image batch response: image-2 and image-3 sections contained leading `image-1.E...` ids even though the Image Evidence Index was correct.
The source plugin renderer now retargets a mismatched leading scoped evidence id to the current image section and retargets citations with that same wrong label inside the item, while preserving deliberate cross-image citations when the item's own id is already correctly scoped.
Validation passed with focused evidence-scoping regressions and full plugin `npm run check` (195 tests plus `security-check: ok`).
No live artifact refresh has been performed for this evidence-ID retargeting source fix yet.
The next operator decision is whether to approve another artifact-only refresh for `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.

[2026-06-25 05:20 +0800] Follow-up source refinement changes artifact-backed prompt-time inline context from "use this as the image input" to an explicit bounded image summary index.
When `writeImagePreflightArtifact` returns an `image_preflight_read` handle, the inline preflight block now tells text-only models to call `image_preflight_read` before answering details omitted from the bounded summaries, details hidden by `[truncated by Stronk Pi]`, or details the user asks for that are not shown inline.
Prompt-time preflight without an artifact handle keeps the previous "do not call file or image read tools" wording.
Focused tests now assert the artifact-backed summary-index wording, the artifact read rule, the artifact handle instruction, and the non-artifact legacy wording.
Validation passed with `node --check src/index.mjs`, focused prompt-time artifact/evidence tests (7 passed), full plugin `npm run check` (195 tests plus `security-check: ok`), and `git diff --check` in both repos.
No live artifact refresh has been performed for this summary-index source refinement yet.
The next operator decision is whether to approve another artifact-only refresh for `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.

[2026-06-25 05:39 +0800] Follow-up compactness refinement removes repeated nonessential provenance from artifact-backed inline prompt-time preflight context and from rewritten prompt image labels.
Analyzed image path replacements now use compact labels like `[image-1; screenshot.png]`; skipped and failed labels use `[...; skipped]` and `[...; failed]`.
When an extended artifact handle is available, the inline context now renders as a compact text block: header, artifact handle, one-line Image Evidence Index, one compact summary line per image, bounded skipped reasons when needed, and no bullet-list provenance such as `source=`, `citation_prefix=`, or repeated `analyzed by Stronk Pi image vision preflight`.
The rich full artifact remains available through `image_preflight_read` for detailed evidence.
Public docs now describe the artifact-backed inline block as a compact image index with minimal summaries and scoped evidence IDs.
Validation passed with `node --check src/index.mjs`, focused image/preflight regression tests (11 passed), full plugin `npm run check` (195 tests plus `security-check: ok`), and docs/source review.
No live artifact refresh has been performed for this compactness refinement yet.
The next operator decision is whether to approve another artifact-only refresh for `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.

[2026-06-25 05:52 +0800] Follow-up refinement removes artifact-backed inline per-image summaries entirely.
The inline prompt-time preflight block is now only an artifact index: model name, analyzed count, artifact handle, artifact character count/capped flag, compact Image Evidence Index, and bounded skipped-image reasons.
It explicitly tells the text-only model not to make visual claims from the inline block alone and to call `image_preflight_read` first, then cite evidence IDs from the artifact.
The now-unused compact summary helper functions were removed from the plugin source.
Public docs and the plan now describe the artifact-backed inline block as an index-only route to the session artifact.
Validation passed with `node --check src/index.mjs`, focused prompt-time artifact tests (7 passed), focused image/preflight regression tests (10 passed), full plugin `npm run check` (195 tests plus `security-check: ok`), stale-source wording scans, a direct 12-image renderer probe, and `git diff --check` in both repos.
No live artifact refresh has been performed for this index-only source refinement yet.
The next operator decision is whether to approve another artifact-only refresh for `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package`.

[2026-06-25 06:09 +0800] Operator-approved artifact-only runtime refresh for the index-only prompt-time preflight context is complete.
The installed `stronk-pi-plugin-0.1.0` package was replaced from the verified local plugin source package.
Setup-managed config was not refreshed because this change only affects plugin source and smoke-test expectations.
The first replacement exposed a stale source smoke assertion that still expected verbose `[... analyzed by Stronk Pi image vision preflight]` prompt labels.
The source smoke assertion was updated to the compact `[image-1; filename.png]` label, verified, and the installed package was replaced a second time so the installed artifact contents match current source.
Pre-refresh backup for rollback to the previous live package: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-060659.tgz`.
Intermediate backup before the final matching-package replacement: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-060807.tgz`.
Previous package directories retained: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-060659` and `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-060807`.
Installed validation passed with installed artifact syntax check, installed source scan for `Artifact index only`, direct installed 12-image renderer probe proving the blank line after the human-readable status line and no inline `Summaries:`, corrected `npm run smoke:installed`, source and installed `stronkpi --validate-only`, interactive-zsh `sp --validate-only` and `sp-glm --validate-only`, `bin/stronkpi-setup validate`, and `bin/stronkpi --diagnose --json`.
Rollback path: to return to the pre-refresh package, restore the `20260625-060659` backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-060659` back to `package`, then rerun `stronkpi --validate-only`, `sp-glm --validate-only`, `bin/stronkpi --diagnose --json`, and `npm run smoke:installed`.

[2026-06-25 06:25 +0800] Follow-up prompt-time preflight artifact grouping started after operator feedback that the saved context should be split by image groups while keeping the vision request batched.
Read-only Stronk swarm used architect, code-reviewer, and qa-tester roles with `fork_context=false`.
The agreed design keeps one multi-image vision provider request so cross-image comparison remains available, then splits only the private `image_preflight_read` artifacts into deterministic groups of up to three images per handle.
The inline artifact index now exposes `Artifact Groups` with ranges such as `image-1..image-3`, while the Image Evidence Index points each image label to its group range.
Each saved group artifact keeps original global labels, adds sibling-handle navigation, and preserves image-scoped evidence IDs without renumbering.
Validation passed with `node --check src/index.mjs`, `node --test test/extension.test.mjs --test-name-pattern "image preflight"`, full plugin `npm run check` (196 tests plus `security-check: ok`), source installed-artifact smoke with `STRONK_PI_SMOKE_PLUGIN=src/index.mjs`, distribution `STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate`, source, short-wrapper, and GLM-wrapper launcher validation, `bin/stronkpi --diagnose --json`, `git diff --check` in both repos, and a direct source 12-image preflight probe proving one provider call with 12 images and four three-image artifact groups.
No live `~/.stronk-pi` plugin artifact refresh has been performed for this grouping source change yet.

[2026-06-25 13:35 +0800] Operator-approved artifact-only runtime refresh for three-image prompt-time preflight artifact groups is complete.
The installed `stronk-pi-plugin-0.1.0` package was backed up and replaced from the verified local plugin source package.
Setup-managed config was not refreshed because this change only affects plugin source.
Final refresh backup: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-133432.tgz`.
Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-133432`.
Installed validation passed with installed package syntax check before and after replacement, installed artifact smoke, installed source scan for the three-image grouping symbols, source, short-wrapper, and GLM-wrapper launcher validation, `bin/stronkpi --diagnose --json`, and a direct installed 12-image grouping probe proving one provider call with 12 images, four artifact handles, and group-scoped readback metadata.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-133432` back to `package`, then rerun `stronkpi --validate-only`, GLM wrapper validation, `bin/stronkpi --diagnose --json`, and `npm run smoke:installed`.

[2026-06-25 18:35 +0800] Operator-approved artifact-only runtime refresh for Kimi streaming image preflight timeout handling is complete.
The installed `stronk-pi-plugin-0.1.0` package was backed up and replaced from the verified local plugin source package.
Setup-managed config was not rewritten because live `~/.stronk-pi/config/defaults.toml` already contains `timeout_ms = 360000` and `stream_idle_timeout_ms = 60000`.
Final refresh backup: `~/.stronk-pi/artifacts/backups/2026-06-25/stronk-pi-plugin-0.1.0.bak.20260625-183427.tgz`.
Previous package directory: `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0/package.previous.20260625-183442`.
Installed validation passed with installed package syntax check, installed source scan for the six-minute timeout constants and Kimi streaming helpers, `npm run smoke:installed`, source and installed `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, and a direct installed-plugin real Kimi probe proving one prompt-time image preflight call used `stream: true`, requested `text/event-stream`, returned no preflight failure, and analyzed one image.
Rollback path: restore the artifact backup into `~/.stronk-pi/artifacts/stronk-pi-plugin-0.1.0`, or swap `package.previous.20260625-183442` back to `package`, then rerun `stronkpi --validate-only`, `bin/stronkpi --diagnose --json`, and `npm run smoke:installed`.

## Artifacts

<!-- Format: - [description](path/or/url) -->

## Client Feedback

[2026-06-22] User approved creating a dedicated plan workspace for routing images through the current Kimi Code vision model before text-only Stronk Pi models.

[2026-06-23] User requested a Codex-target prompt for implementing the moved plan while working from `stronk-pi` and landing plugin changes in `stronk-pi-plugin`.
