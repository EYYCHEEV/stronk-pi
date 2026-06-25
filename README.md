# Stronk Pi

`stronkpi-setup` is the setup and validation command for Stronk Pi.
Stronk Pi is the guarded Pi Coding Agent distribution.
`stronkpi` is the portable guarded harness installed by this distribution repo.

This repository provides the public bundle contract: setup and doctor behavior,
manifest verification, the portable harness, public-safe role templates,
default role/config/model files, package pins, generated-agent output paths, and
offline tests. Mutable runtime output is installed under `~/.stronk-pi/`.

## Name Map

| Name | Meaning |
| --- | --- |
| Stronk Pi | Guarded Pi Coding Agent distribution. |
| `stronkpi` | Guarded harness command that launches Pi with Stronk Pi controls. |
| `stronkpi-setup` | Setup, validation, diagnostics, and artifact update command. |
| `stronk-pi` | Public distribution repo and bundle contract. |
| `stronk-pi-plugin` | Plugin source repo and verified artifact consumed by setup manifests. |
| Stronk Pi Mono | Trusted Pi fork runtime lineage used by the guarded harness. |

Guarded means Pi is launched with fail-closed controls for tool permissions,
unsafe shell commands, secret and path handling, trusted runtime drift,
Model Context Protocol (MCP) configuration, and subagent role loading.

## Install

Preview installation without writing to your command directory:

```sh
./install.sh --dry-run
```

Install the command into `~/.local/bin`:

```sh
./install.sh
```

The installer creates `stronkpi-setup` and `stronkpi`. It does not create short
compatibility aliases.

## Validate

Run the offline setup checks:

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup validate
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --json --allow-missing-mcp
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup doctor --mcp-registry ~/.config/mcp/registry.toml
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup refresh-config --dry-run
STRONKPI_NO_NETWORK=1 bin/stronkpi --validate-only
```

Verify an offline fixture manifest:

```sh
STRONKPI_NO_NETWORK=1 bin/stronkpi-setup update --dry-run --manifest tests/fixtures/manifests/good-local.json
```

## Release Bump

Setup version bumps are repo-local:

```sh
python3 scripts/bump-version.py 0.2.0
STRONKPI_NO_NETWORK=1 sh scripts/verify-release-candidate.sh
```

Plugin artifact bumps are imported only after `stronk-pi-plugin` publishes an
immutable release:

```sh
python3 scripts/import-plugin-release.py /tmp/stronk-pi-plugin-v0.2.0/BUILD-MANIFEST.json
```

See `docs/release.md` for the full two-repo release SOP.
Agents can also use the project-scope `stronk-pi-release` skill in this repo.

`doctor` validates the distribution host, bundle contract, harness presence, role
manifest status, optional `roles.local.toml` overlay status, plugin artifact
status, trusted runtime status, and MCP registry. It checks Python availability,
state-root safety, registry TOML shape, server commands, selected `.mcp-tools`
names, selected server environment variables, unsafe MCP URLs, floating package
refs, and accidental personal paths. Network checks are opt-in with
`--check-network` and are skipped when `STRONKPI_NO_NETWORK=1`.

## Runtime Config

The canonical runtime state and config root is `~/.stronk-pi/`.

`stronkpi-setup refresh-config` installs or refreshes:

- `~/.stronk-pi/config/defaults.toml`
- `~/.stronk-pi/config/roles.toml`
- `~/.stronk-pi/config/role-templates/*.toml`
- generated runtime role Markdown under `~/.stronk-pi/agent/agents/`

It also refreshes setup-managed Pi runtime config under
`~/.stronk-pi/agent/`, including `settings.json`, `models.json`, and
`AGENTS.md`.
The public default coding model is `kimi-coding/kimi-for-coding` with Pi
`defaultThinkingLevel` set to `xhigh`.
The default `kimi-coding` provider is Pi's built-in Kimi Code provider.
Image preflight falls back to the Kimi Code Anthropic Messages endpoint under
`https://api.kimi.com/coding` when Pi does not expose a host vision adapter.
It reads `KIMI_API_KEY`, falling back to `KIMI_CODE_API_KEY`.
The guarded launcher maps `KIMI_CODE_API_KEY` into `KIMI_API_KEY` only when
`KIMI_API_KEY` is not already set.
Use `--dry-run` to preview changed paths and `--json` for automation.

Image vision preflight is configured in
`~/.stronk-pi/config/defaults.toml` under `[image_preflight]`.
When enabled, text-only active models route attached or pasted local images
through the configured vision model, then receive a bounded
`<stronk-pi-image-vision-preflight>` context block instead of raw image payloads.
The block is evidence-oriented and image-type neutral: it may include image
type, quality, scene/composition, subjects, objects, attributes/state,
relationships/activity, visible text/symbols, structured content such as
documents/charts/code/UI, domain-specific details, uncertainties, scoped
not-visible evidence, and inference guardrails.
Text-only models should treat omitted, unknown, unreadable, cropped, or
not-visible details as unavailable rather than absent.
The image count default is `max_images = 12`; additional supported images are
reported as skipped instead of being sent to the text-only model as raw image
payloads.
The vision response budget defaults to `max_output_tokens = 4096` and is
clamped from 1024 to 8192.
After successful preflight, pasted local image paths are replaced with stable
image labels in the forwarded prompt so text-only models use the summary rather
than trying to read the image file directly.
The context includes an Image Evidence Index that maps each label to its
filename/source/MIME/byte metadata.
Evidence IDs are image-scoped, such as `image-1.E1`, `image-2.U1`, and
`image-3.I1`, so repeated local IDs from multi-image vision output remain
traceable.
The configured `max_output_tokens` value is treated as a per-image vision
budget for prompt-time preflight; multi-image turns get a scaled provider
request budget within Stronk Pi's hard caps.
Prompt-time preflight still sends one multi-image vision request; only the
saved readback artifacts are split into three-image groups.
When a persisted Stronk Pi session is available, the plugin also writes the
extended bounded sanitized prompt-time image analysis to a private session
artifact.
The inline block remains bounded and compact: it carries only image labels,
safe filenames, MIME/size hints, and opaque handles grouped at up to three
images per handle.
Text-only models must call `image_preflight_read` with the relevant handle to
read the extended text artifact in bounded chunks before making visual claims.
Preflight only handles images attached to or explicitly pasted into the current
user turn.
Images discovered later by agent tool use can be inspected through the
registered `image_read` tool.
`image_read` is intended for text-only models that find local image files after
the prompt starts.
It accepts one explicit image path in `paths`, or one bounded `directory` scan
that must resolve exactly one image, with `recursive = false` by default.
It uses the same configured vision preflight model route, limits, timeout,
response token budget, MIME checks, safe failure classification, Image Evidence
Index, and image-scoped evidence IDs as prompt-time preflight.
When the interactive Pi TUI is available, the plugin shows a temporary animated
below-editor image-vision indicator while analysis runs, then clears its own
status/widget and emits bounded status notifications for completion, skipped
images, or failure-note fallback.
Native multimodal models keep Pi's normal image handling and bypass preflight.
This source/config contract does not update a live install by itself.
Live behavior requires a matching `stronk-pi-plugin` artifact that contains the
image preflight implementation, then an operator-approved config refresh or
manifest update.
Use `stronkpi --diagnose --json` to confirm the installed plugin artifact path
before expecting runtime preflight behavior.

`stronkpi-setup import-codex-roles` imports local Codex-style Stronk role TOML
files into the runtime template directory and refreshes generated Pi role
Markdown.
Without `--source`, it checks `~/.codex/roles/stronk`,
`~/.agents/roles/stronk`, then `~/.agents/codex/roles/stronk`.
The import copies role names and instructions into
`~/.stronk-pi/config/role-templates/`; Pi model selection remains controlled by
`~/.stronk-pi/config/roles.toml` and the optional local overlay.
Later config refreshes preserve imported Codex role templates.
Use `--dry-run` before writing runtime state.

`stronkpi-setup update` verifies the release manifest, also refreshes the same
managed runtime config, and installs or refreshes:

- verified plugin artifacts under `~/.stronk-pi/artifacts/`

Private local preferences belong in `~/.stronk-pi/config/roles.local.toml`.
Generated role Markdown is runtime output, not tracked source.

## State And Credentials

Mutable runtime state belongs under the user-owned Stronk Pi state root. Provider
credentials are read from environment variables only. Diagnostics redact
secret-like keys and values.

## Security Posture

- Manifest entries must include immutable source, checksum, byte size,
  provenance, compatibility, and creation metadata.
- Network access is denied when `STRONKPI_NO_NETWORK=1`.
- Local absolute artifact paths and local file URLs are denied.
- Archive extraction rejects traversal, symlinks, hardlinks, and special files.
- Public setup files are scanned for unsafe shell patterns, local paths, and
  command-surface drift.
