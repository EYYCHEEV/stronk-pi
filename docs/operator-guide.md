# Operator Guide

## Which Command Do I Run?

| Task | Command | Notes |
| --- | --- | --- |
| Validate setup files and host assumptions | `stronkpi-setup validate` | Setup-only; does not launch Pi. |
| Diagnose setup and MCP registry state | `stronkpi-setup doctor` | Redacts secret-like values. |
| Refresh managed runtime config | `stronkpi-setup refresh-config` | Updates `~/.stronk-pi/config`, `~/.stronk-pi/agent/settings.json`, and generated role Markdown. |
| Import local Codex Stronk roles | `stronkpi-setup import-codex-roles` | Copies local role TOML into runtime templates, then regenerates role Markdown. |
| Verify/update pinned artifacts | `stronkpi-setup update` | Uses manifests; respects `STRONKPI_NO_NETWORK=1`. |
| Validate guarded harness config | `stronkpi --validate-only` | Checks the harness without launching an interactive Pi session. |
| Launch the guarded Pi experience | `stronkpi` | Portable harness installed by the Stronk Pi distribution repo. |

Stronk Pi is the guarded Pi Coding Agent distribution. This repo owns setup and
manifest validation; the `stronkpi` harness owns runtime launch behavior.

## Routine Checks

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --json --allow-missing-mcp
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup refresh-config --dry-run
STRONKPI_NO_NETWORK=1 bin/stronkpi --validate-only
STRONKPI_NO_NETWORK=1 sh tests/run_offline.sh
```

Use `stronkpi-setup refresh-config` after changing distribution-owned runtime config
templates such as `config/pi/agent/settings.base.json`.
The shipped coding default is `kimi-coding/kimi-for-coding` with Pi
`defaultThinkingLevel` set to `xhigh`.
Add `--json` for automation.

Use `stronkpi-setup import-codex-roles --dry-run` to preview a local role import.
By default it reads the first available role directory from
`~/.codex/roles/stronk`, `~/.agents/roles/stronk`, or
`~/.agents/codex/roles/stronk`.
Use `--source <dir>` for an explicit Codex role TOML directory.
The command writes only under `~/.stronk-pi/` and leaves public repo templates
unchanged.
Normal config refreshes preserve imported Codex role templates.

## Fixture Manifest Verification

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
```

Bad fixture manifests must fail without installing anything.

## MCP Registry Doctor

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --mcp-registry ~/.config/mcp/registry.toml --mcp-tools .mcp-tools
```

The MCP registry check validates registry TOML, server command availability,
selected tool names, selected server environment variables, unsafe URLs,
floating package refs, and accidental personal absolute paths. Runtime MCP
loading is not enabled until the guarded launcher includes a verified MCP
adapter artifact.

## Local Role Overlay

Public defaults are installed to `~/.stronk-pi/config/roles.toml`.
Private local preferences can be placed in
`~/.stronk-pi/config/roles.local.toml`.
The overlay is optional and is never required for public setup.

## Image Vision Preflight

Text-only active models can still answer about pasted or attached images.
When `[image_preflight].enabled = true`, the plugin analyzes supported images
with the configured vision model and injects a bounded
`<stronk-pi-image-vision-preflight>` context block into the prompt.
The block separates observed image facts from inference and uncertainty, and
can carry image-type neutral evidence such as scene/composition, subjects,
objects, attributes/state, relationships/activity, visible text/symbols,
structured content such as documents/charts/code/UI, domain-specific details,
image-quality limits, scoped not-visible evidence, and guardrails for avoiding
overclaims.
Text-only models should treat omitted, unknown, unreadable, cropped, or
not-visible details as unavailable rather than absent.
Raw image payloads are stripped before forwarding to text-only models.
After successful preflight, pasted local image paths are replaced with image
labels in the forwarded prompt.
The injected block includes an Image Evidence Index mapping each stable label
to filename/source/MIME/byte metadata.
Evidence IDs are image-scoped, for example `image-1.E1`, `image-2.N1`, and
`image-3.I1`, so repeated IDs across several images remain unambiguous.
This keeps the main text-only model on the preflight summary instead of a
provider-native image-read path it cannot use.
When the interactive Pi TUI is available, operators see a temporary animated
below-editor image-vision indicator while preflight analyzes images.
The plugin clears its own status/widget and emits bounded status notifications
when preflight completes, skips unsupported input, or falls back to a failure
note.

Native multimodal models keep Pi's normal image handling and do not use the
preflight summary path.
This preserves provider-native image behavior for models whose runtime metadata
declares image input support.
The source docs and config defaults describe the expected contract, but they do
not change a live `~/.stronk-pi` install by themselves.
Runtime preflight behavior requires an installed `stronk-pi-plugin` artifact
that contains the implementation.
The release manifest remains the source of truth for what
`stronkpi-setup update` installs.

Check installed state before relying on preflight:

```bash
bin/stronkpi --diagnose --json
```

From the `stronk-pi-plugin` source repo, also run:

```bash
npm run smoke:installed
```

Inspect the reported plugin artifact path and version.
Before writing runtime state, preview config and artifact changes:

```bash
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup refresh-config --dry-run
bin/stronkpi-setup update --dry-run --manifest manifests/current.json
```

Rollback after an incorrect live plugin update is to reinstall or restore the
previous manifest/plugin artifact version.
Then rerun `bin/stronkpi --validate-only` and
`bin/stronkpi --diagnose --json`.

Public defaults live in `~/.stronk-pi/config/defaults.toml`:

```toml
[image_preflight]
enabled = true
model = "kimi-coding/kimi-for-coding:xhigh"
max_images = 12
max_bytes = 5242880
timeout_ms = 90000
max_output_tokens = 4096
failure_mode = "soft"
```

`max_images` applies to images attached to or explicitly pasted into the
current user turn.
It does not make a text-only model recursively inspect folders.
If the agent later discovers image files through shell or file tools, that
uses the registered `image_read` tool instead.
`image_read` is for text-only models that need visual evidence from local image
files found after the prompt starts.
It accepts explicit `paths`, one optional `directory`, `recursive = false` by
default, and an optional `max_images` bounded by `[image_preflight].max_images`.
Directory scans are deterministic and bounded; hidden and protected directories
are skipped, and recursive traversal is opt-in.
The tool routes supported images through the same configured vision preflight
model and returns the same universal evidence style, Image Evidence Index, and
image-scoped evidence IDs as prompt-time preflight.
It returns structured text only, not raw images or unnecessary absolute local
paths.

The shipped `kimi-coding` model uses Pi's built-in Kimi Code provider.
Image preflight falls back to the Kimi Code Anthropic Messages endpoint under
`https://api.kimi.com/coding` when Pi does not expose a host vision adapter.
It reads `KIMI_API_KEY`, falling back to `KIMI_CODE_API_KEY`.
The guarded launcher maps `KIMI_CODE_API_KEY` to `KIMI_API_KEY` only when
`KIMI_API_KEY` is not already set.
Operators can override the vision model through
`~/.stronk-pi/config/roles.local.toml` by setting `[pi].vision_model`.
Environment overrides are available for emergency local sessions:
`STRONK_PI_IMAGE_PREFLIGHT`, `STRONK_PI_IMAGE_PREFLIGHT_MODEL`,
`STRONK_PI_IMAGE_PREFLIGHT_MAX_IMAGES`,
`STRONK_PI_IMAGE_PREFLIGHT_MAX_BYTES`,
`STRONK_PI_IMAGE_PREFLIGHT_TIMEOUT_MS`,
`STRONK_PI_IMAGE_PREFLIGHT_MAX_OUTPUT_TOKENS`, and
`STRONK_PI_IMAGE_PREFLIGHT_FAILURE_MODE`.
The output-token budget defaults to 4096 and is clamped from 1024 to 8192.
Set `failure_mode = "block"` only when image-understanding failures should stop
the prompt instead of injecting an explicit failure note.

## Release Readiness

Use `python3 scripts/bump-version.py <version>` for setup version bumps.
Use `python3 scripts/import-plugin-release.py <BUILD-MANIFEST.json>` only after
the plugin release exists.
See `docs/release.md` for the full release SOP.
Agents can also use the project-scope `stronk-pi-release` skill in this repo.

Before any public release, verify:

- gitleaks worktree and history scans pass with redaction;
- public-surface scans pass;
- manifest fixture tests cover good and bad artifacts;
- guard matrix tests pass;
- GitHub repository settings and branch protection are recorded;
- third-party workflow Actions are pinned to full commit SHAs.
