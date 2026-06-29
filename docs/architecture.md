# Architecture

Stronk Pi is a guarded Pi Coding Agent distribution built on Pi. The
distribution includes setup manifests, a guarded launch harness, a plugin
artifact, a trusted Pi runtime, and user-owned state.

`stronkpi-setup` is the setup command in the `stronk-pi` distribution repo. It owns
four boundaries:

- setup entrypoint: `bin/stronkpi-setup`
- portable guarded harness: `bin/stronkpi`
- guard, config generator, and manifest verifier: `lib/stronk-pi-guard.py`
- public-safe Pi config templates: `config/pi/`
- public role templates and role manifest: `roles/stronk/`
- release manifest inputs: `manifests/`

`stronkpi` is the guarded harness name and is shipped by this distribution repo.
Setup, config refresh, update, and diagnostics remain available through
`stronkpi-setup`.

The guarded harness protects normal Pi execution with fail-closed controls for
tool permissions, unsafe shell commands, secret and path handling, trusted
runtime drift, Model Context Protocol (MCP) configuration, and subagent role
loading.

`stronkpi-setup` uses a Python entrypoint and a POSIX `sh` installer so public
setup does not require a specific login shell. Shell aliases such as short
local commands remain outside this repo.

The distribution repo does not own provider credentials or mutable runtime sessions.
It prepares and validates a state root owned by the current user and verifies
release artifacts before they can be installed.
The guarded harness launches Pi with the operator's real `HOME` and routes
Stronk Pi-owned state through explicit paths under `~/.stronk-pi/`.

## Config Precedence

Runtime config resolves in this order:

1. distribution-owned defaults in this repo;
2. installed defaults under `~/.stronk-pi/config/defaults.toml`;
3. installed default role manifest under `~/.stronk-pi/config/roles.toml`;
4. optional local overlay under `~/.stronk-pi/config/roles.local.toml`;
5. explicit allowlisted environment variables.

Generated Pi agent Markdown is rendered under `~/.stronk-pi/agent/agents/`.
It is runtime output and must not be tracked as public source.
`stronkpi-setup refresh-config` is the explicit operator command for writing
the setup-managed defaults, Pi agent settings, model config, role templates,
and generated role Markdown into `~/.stronk-pi/` without launching Pi.
The shipped coding default is `kimi-coding/kimi-for-coding` with Pi
`defaultThinkingLevel` set to `xhigh`.
Image vision preflight defaults live in `[image_preflight]` in the same
defaults file.
The shipped image count default is 12 for images attached to or explicitly
pasted into the current user turn.
The vision response token budget defaults to 4096 and is clamped from 1024 to
8192 before provider calls.
The default vision model is also mirrored by `[models].vision` and
`[pi].vision_model` in the role manifest.
Environment overrides take final precedence over those public runtime config
files.
When the active model metadata declares image input support, the plugin leaves
images on the native Pi path instead of summarizing them first.
For text-only models, successful preflight replaces pasted local image paths
with stable image labels before the main model sees the prompt.
The injected context is evidence-first rather than caption-only.
It includes an Image Evidence Index and image-scoped evidence IDs such as
`image-1.E1`, `image-2.N1`, and `image-3.I1`, which keeps repeated local IDs
from multi-image vision summaries traceable to the source image.
It preserves image-type neutral evidence such as scene/composition, subjects,
objects, attributes/state, relationships/activity, visible text/symbols,
structured content such as documents/charts/code/UI, domain-specific details,
uncertainties, and scoped negative evidence where the vision model provides
them.
The prompt explicitly tells the downstream model not to treat omitted,
unknown, unreadable, cropped, or not-visible details as absent.
For prompt-time preflight, `[image_preflight].max_output_tokens` is treated as
a per-image response budget; multi-image requests scale the provider budget
within Stronk Pi's hard cap.
The provider call remains one multi-image request; only the saved readback
artifacts are split into three-image groups.
The inline prompt block stays bounded.
When session metadata is available, the plugin saves extended bounded
sanitized analysis text under the state-root session directory.
The model-facing inline block stays compact: image labels, safe filenames,
MIME/size hints, and opaque `image_preflight_read` handles grouped at up to
three images per handle.
Text-only models must read the relevant artifact group before making visual
claims.
That artifact contains text evidence only, not raw image data or base64.
Prompt-time preflight does not recursively inspect folders or tool-discovered
paths after the turn starts.
Agentic image reading is handled by the registered `image_read` plugin tool.
That tool is for text-only models that discover local image files after the
prompt starts.
It accepts one explicit image path in `paths`, or one bounded `directory` scan
that must resolve exactly one image.
It keeps `recursive = false` unless explicitly requested and reuses the same
configured vision preflight model route and evidence renderer as prompt-time
preflight.
The tool output is structured text only; raw image payloads and unnecessary
absolute local paths are not returned to the text-only model.
The input hook uses Pi's extension UI surface for a plugin-owned temporary
animated TUI widget while preflight analyzes images.
It then clears that keyed status/widget and emits bounded notifications for
completion, skips, and failure-note fallback.
These defaults are only the setup/runtime config contract.
Live image preflight behavior requires the installed plugin artifact to contain
the matching implementation.
`manifests/current.json` remains pinned to the last imported plugin release
until a new `stronk-pi-plugin` release manifest is imported and verified.

`stronkpi-setup import-codex-roles` is the explicit bridge for local Codex role
definitions.
It imports from an operator-selected Codex role TOML directory, or from the
standard home-owned role directories, into
`~/.stronk-pi/config/role-templates/`.
The command does not mutate this repo's public role templates and does not make
Stronk Pi depend on operator-local source trees.
Imported Codex model metadata is recorded as source metadata; active Pi model
selection remains controlled by the Stronk Pi role manifest and local overlay.

## MCP Registry Doctor

`stronkpi-setup doctor` validates the user-local MCP registry at
`~/.config/mcp/registry.toml` or the path passed with `--mcp-registry`. It
checks registry TOML, server command availability, selected `.mcp-tools`
entries, selected server environment variables, unsafe URLs, floating package
refs, and accidental personal paths.

`stronkpi` loads `pi-mcp-adapter` when `.mcp-tools` selects at least one MCP
server and the pinned adapter package is installed under the Stronk Pi state
root.
Before launch, the harness validates the registry, writes
project `.mcp.json` with only the selected servers, and passes that file
through the adapter-owned `--mcp-config` flag.
The generated config is mode `0600` and uses `${ENV_NAME}` placeholders for
selected secret environment variables instead of persisting their values.
The adapter keeps MCP servers lazy: servers connect when their tools are used,
not when Pi starts.

The generated project `.mcp.json` is refreshed from the registry and
`.mcp-tools` on each launch so Claude Code-compatible repo tooling can discover
the same selected MCP surface.
Symlinked `.mcp.json` and project `.pi/mcp.json` files are rejected because
they would bypass the selected-server boundary or escape the project file.
Operators must keep server definitions in the registry and use `.mcp-tools`
for the selected-server boundary.

## State Root Contract

`~/.stronk-pi` is the only default Stronk Pi state root.
The launcher sets explicit paths for Stronk-owned config, generated files,
runtime artifacts, sessions, logs, caches, and temporary files:

- `~/.stronk-pi/config/`
- `~/.stronk-pi/agent/`
- `~/.stronk-pi/agent/sessions/`
- `~/.stronk-pi/agent/extensions/stronk-pi-intercom`
- `~/.stronk-pi/artifacts/`
- `~/.stronk-pi/pi-fork-runtime/`
- `~/.stronk-pi/logs/`, `~/.stronk-pi/cache/`, and `~/.stronk-pi/tmp/`

Operator-set `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` are inherited when already
present.
The harness does not synthesize either variable to point into a private home.
Normal launch must not create Stronk Pi state in `~/.pi`, `~/.config/pi`, `~/.local/share/pi`, `~/.cache/pi`, or `~/.stronk-pi/home`.

## Manifest Flow

1. Parse the manifest schema.
2. Reject mutable versions, local absolute paths, and local file URLs.
3. Resolve only approved local fixtures in offline tests, or public HTTPS
   artifacts when network access is allowed.
4. Verify byte size and SHA-256 before archive inspection.
5. Reject archive traversal, symlinks, hardlinks, and special files.
6. Install atomically only after verification passes.

## Offline Mode

`STRONKPI_NO_NETWORK=1` makes network artifact access fail closed. Offline tests
use fixture artifacts under `tests/fixtures/`.
