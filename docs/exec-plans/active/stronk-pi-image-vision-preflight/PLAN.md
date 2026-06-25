# Stronk Pi Image Vision Preflight

## Objective

Add a Stronk Pi image preflight path so text-only daily-driver models, especially NeuralWatt GLM-5.2, can still handle pasted or attached images. When the active model cannot accept images, Stronk Pi should route the images through the configured vision model, initially `kimi-coding/kimi-for-coding`, inject a bounded universal visual-understanding context block into the user prompt, and avoid sending raw images to the text-only provider. The context should preserve image-type-neutral facets such as image type, scene/composition, subjects/objects/entities, attributes/counts/state, relationships/activity, visible text/symbols, structured content/data, domain-specific details, uncertainties, scoped not-visible evidence, and inferences.
Add an explicit agentic `image_read` tool so text-only models can inspect local image files discovered after the prompt starts, such as screenshots found by `ls`, `glob`, or `find`.
The tool should reuse the same configured image vision preflight model route and evidence renderer instead of creating a second vision system.

## Scope

- Implement this in Stronk Pi's managed extension/input-transform path, not as a broad rewrite of the Pi runtime.
- Detect images from both Pi `event.images` attachments and pasted clipboard image file paths in `event.text`.
- Preserve native vision behavior when the active model already supports images.
- Use the vision model from the portable Stronk Pi config contract, defaulting to `kimi-coding/kimi-for-coding` in `~/.stronk-pi/config/defaults.toml` and `~/.stronk-pi/config/roles.toml`.
- Produce a bounded, clearly labeled universal vision context block that separates direct observations, visible text/symbols, scene/composition, subjects/objects, attributes/state, relationships/activity, structured content, domain-specific details, uncertainty/limits, scoped not-visible evidence, and inference.
- Strip raw image payloads before forwarding to a text-only model.
- Add tests for routing, limits, failure behavior, recursion guard, and prompt shape.
- Do not assume every image is an interface or screen capture; first classify the image type and preserve the evidence needed for that type.
- Refresh the installed Stronk Pi plugin artifact only after source tests pass and with the existing backup workflow.
- Add a neutral registered plugin tool named `image_read` with label `Image Read`.
- Use `image_read` for explicit local image reads discovered during tool use by text-only models.
- Keep prompt-time preflight behavior unchanged.
- Implement the first agentic image-reading path as a registered Stronk Pi plugin tool, not a new MCP server.
- Let `image_read` accept one explicit image path in `paths`, or one bounded `directory` scan that resolves exactly one image with `recursive = false` by default.
- Reuse the existing image preflight config, provider invocation, MIME checks, byte limits, timeout, output token budget, evidence renderer, and safe failure classification where practical.
- Return bounded structured text with the same universal evidence style, Image Evidence Index, and image-scoped evidence IDs.

## Constraints

- Do not log image base64 data, OCR payloads beyond test fixtures, API keys, or provider secrets.
- Skip extension-originated input to avoid recursive preflight calls.
- Keep the existing guarded input flow intact, including safety hook behavior before expensive image work.
- Enforce conservative limits for image count, byte size, MIME type, and preflight timeout.
- Keep behavior configurable enough to disable or narrow the preflight if Kimi Code is unavailable.
- Avoid changing `.zshrc`, Codex config, or unrelated model aliases as part of this plan.
- Do not expose raw base64 image data, unnecessary absolute local paths, or raw provider error bodies from `image_read`.
- Directory scanning must be deterministic and bounded.
  Restricted/default permission modes are limited to allowed image roots.
  Full-disk modes such as Codex `danger-full-access` / Pi full-yolo do not reject image paths only because they are outside those roots.
  Hidden and protected directories are skipped, and recursive scanning is opt-in only.

## Task Checklist

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

## Open Questions

- [x] Should vision failure fail soft by injecting an explicit failure note, or block the GLM turn because the user expected image understanding?
  Decision: Default to fail-soft, with `failure_mode = "block"` available for stricter operators.
- [x] Should preflight be enabled for every text-only model by default, or initially limited to NeuralWatt GLM-5.2 routes?
  Decision: Enable for text-only models by default, while bypassing models whose metadata declares image input support.
- [x] What should the default max image count and per-image byte limit be for pasted CLI workflows?
  Decision: Default to 12 images and 5 MiB per image, capped internally at 12 images and 20 MiB per image.
- [x] How should explicit image paths in normal text preserve traceability after summarization?
  Decision: Replace successfully analyzed local image paths with stable image labels before forwarding to text-only models, while keeping filename, MIME type, byte count, observed facts, and uncertainty in the labeled preflight context.
- [x] Should agentic image reading be a new MCP server or a plugin tool?
  Decision: Use a registered Stronk Pi plugin tool first because it can reuse the existing vision preflight route and avoids adding a new runtime boundary.
- [x] What should the agentic image-reading tool be called?
  Decision: Use neutral tool name `image_read` and UI label `Image Read`.
- [x] How should prompt-time preflight preserve extended multi-image analysis when the inline context block is bounded?
  Decision: Keep the model-facing inline block bounded, save extended bounded sanitized text analysis under private session state when session metadata is available, expose only an opaque `image_preflight_read` handle, and let the model read the artifact in bounded chunks when needed.
- [x] Should prompt-time `max_output_tokens` be shared by a multi-image batch or treated per image?
  Decision: Treat `[image_preflight].max_output_tokens` as a per-image budget and scale the provider request budget by prompt image count within Stronk Pi hard caps, while keeping one multi-image provider request to preserve cross-image comparison and avoid new partial-call failure semantics.
- [x] What should the inline prompt-time image context say when extended artifact handles are available?
  Decision: Treat the inline block as a compact bounded artifact index, include only image labels, safe filenames, MIME/size hints, and relevant artifact handles, and instruct text-only models to call `image_preflight_read` before making visual claims.
- [x] Should prompt-time preflight batch vision provider calls or split readback artifacts?
  Decision: Keep one multi-image provider request for cross-image comparison and split only the private `image_preflight_read` artifacts into deterministic groups of up to three images per handle.
