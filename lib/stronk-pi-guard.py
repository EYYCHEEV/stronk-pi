#!/usr/bin/env python3
"""Stronk Pi setup guard, validator, and manifest verifier."""

from __future__ import annotations

import argparse
import base64
import hashlib
import ipaddress
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


VERSION = "0.2.3"
CONFIG_SCHEMA_VERSION = 1
BUNDLE_CONTRACT_VERSION = "stronkpi-setup-v1"
MANAGED_MARKER = 'managed_by = "stronk-pi"'
IMPORTED_CODEX_ROLE_MARKER = 'source_of_truth = "codex-role-toml"'
LEGACY_MANAGED_MARKERS = ('managed_by = "stronk-pi-setup"',)
DEFAULT_ROLE_MANIFEST_RELATIVE = Path("roles") / "stronk" / "roles.toml"
ROLE_TEMPLATE_RELATIVE = Path("roles") / "stronk" / "templates"
DEFAULTS_RELATIVE = Path("config") / "defaults.toml"
DEFAULT_CODEX_ROLE_DIR_CANDIDATES = (
    Path(".codex") / "roles" / "stronk",
    Path(".agents") / "roles" / "stronk",
    Path(".agents") / "codex" / "roles" / "stronk",
)
DEFAULT_PLUGIN_VERSION = "0.2.3"
DEFAULT_PLUGIN_RELATIVE = Path("artifacts") / f"stronk-pi-plugin-{DEFAULT_PLUGIN_VERSION}" / "package" / "src" / "index.mjs"
DEFAULT_PACKAGE_PINS = {
    "mcp_adapter": ("pi-mcp-adapter", "2.9.0"),
    "subagents": ("stronk-pi-subagents", "0.22.0-stronk.5"),
    "intercom": ("stronk-pi-intercom", "0.6.0-stronk.1"),
}
SUBAGENT_RUNTIME_PACKAGE_KEYS = ("subagents", "intercom")
SHARED_HOOK_TIMEOUT_SEC = 5.0
LEGACY_MANAGED_RUNTIME_PATHS = (
    Path("agent") / "agents",
    Path("agent") / "AGENTS.md",
    Path("agent") / "models.json",
    Path("agent") / "settings.json",
    Path("config") / "web-search.json",
)
LEGACY_PRIVATE_HOME_AGENT_DIRS = {".agents", ".claude", ".codex"}
CONTROL_PLANE_ENV_NAMES = (
    "STRONKPI_SETUP_ROOT",
    "STRONKPI_STATE_ROOT",
    "STRONK_PI_STATE_ROOT",
    "STRONK_PI_GUARD",
    "STRONK_PI_HOOK_COMMAND_JSON",
    "STRONK_PI_CODEX_HOOK_COMMAND_JSON",
    "STRONK_PI_URL_CHECK_COMMAND_JSON",
    "STRONK_PI_TELEGRAM_COMMAND_JSON",
    "STRONK_PI_EXTENSION",
    "STRONK_PI_AGENT_DIR",
    "STRONK_PI_CODEX_AGENTS",
    "STRONK_PI_SESSION_BASE",
    "STRONK_PI_CONFIG_ROOT",
    "STRONK_PI_LOG_ROOT",
    "STRONK_PI_CACHE_ROOT",
    "STRONK_PI_TMP_ROOT",
    "STRONK_PI_MCP_CONFIG_PATH",
    "STRONK_PI_WEB_SEARCH_CONFIG",
    "STRONK_PI_INTERCOM_BRIDGE",
    "STRONK_PI_MCP_REGISTRY",
    "STRONK_PI_ROLE_MANIFEST",
    "STRONK_PI_ROLE_MANIFEST_LOCAL",
    "STRONK_PI_DANGEROUS_COMMAND_HOOK",
    "STRONK_PI_SUBAGENT_FACADE",
    "STRONK_PI_SUBAGENT_ADAPTER",
    "STRONK_PI_SKILL_ROOTS",
    "PI_CODING_AGENT_DIR",
    "PI_CODING_AGENT_SESSION_DIR",
    "PI_SKIP_VERSION_CHECK",
    "PI_OFFLINE",
)
CONTROL_PLANE_PREFIX_ALLOWLIST_EXACT = {
    "STRONKPI_NO_NETWORK",
    "STRONKPI_DEV_OVERRIDES",
    "STRONK_PI_DEV_OVERRIDES",
    "STRONK_PI_SEARCH_PROVIDER",
    "STRONK_PI_SMOKE_PLUGIN",
    "STRONK_PI_SMOKE_AGENT_RUN",
}
CONTROL_PLANE_PREFIX_ALLOWLIST_PREFIXES = (
    "STRONK_PI_IMAGE_PREFLIGHT",
)
CONTROLLED_PI_FLAGS = {
    "--extension",
    "-e",
    "--no-extensions",
    "-ne",
    "--skill",
    "--no-skills",
    "-ns",
    "--tools",
    "-t",
    "--exclude-tools",
    "-xt",
    "--no-tools",
    "-nt",
    "--no-builtin-tools",
    "-nbt",
    "--session-dir",
    "--provider",
    "--api-key",
    "--offline",
    "--no-context-files",
    "-nc",
    "--system-prompt",
    "--append-system-prompt",
    "--prompt-template",
    "--no-prompt-templates",
    "-np",
    "--theme",
    "--no-themes",
    "--mcp-config",
}
PACKAGE_PIN_KEYS = (
    "mcp_adapter",
    "subagents",
    "intercom",
    "jiti",
    "ask_user",
    "tsx",
    "typebox",
    "esbuild",
)
BLOCKED_WEB_HOSTS = {
    "localhost",
    "ip6-localhost",
    "ip6-loopback",
    "metadata",
    "metadata.google.internal",
    "instance-data.ec2.internal",
}
BLOCKED_WEB_SUFFIXES = (".localhost", ".local", ".internal", ".lan", ".home.arpa")
BLOCKED_METADATA_IP_NETWORKS = (
    ipaddress.ip_network("169.254.169.254/32"),
    ipaddress.ip_network("100.100.100.200/32"),
    ipaddress.ip_network("fd00:ec2::254/128"),
)
DNS_PROXY_IP_NETWORKS = (ipaddress.ip_network("198.18.0.0/15"),)
SECRET_KEY_PATTERN = re.compile(
    r"(^|_)(API_KEY|KEY|TOKEN|SECRET|PASSWORD|PASS|CREDENTIAL|COOKIE)($|_)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{16,}"),
)
FLOATING_VERSION_RE = re.compile(
    r"(^latest$|@latest\b|^[~^*<>]=?|[xX*](?:\.|$)|\bHEAD\b)",
    re.IGNORECASE,
)
MCP_FLOATING_ARG_RE = re.compile(
    (
        r"(^latest$|@latest\b|releases/"
        + "latest"
        + r"|@[~^*<>]|@[0-9]+(?:\.[0-9]+)*\.[xX*]\b|@[xX*](?:\.|$))"
    ),
    re.IGNORECASE,
)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[/\\]")
MCP_SERVER_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# Runtime package pins resolved from defaults.toml or DEFAULT_PACKAGE_PINS must be
# concrete (non-floating) and syntactically constrained so a malicious defaults file
# cannot redirect runtime discovery to an arbitrary package name or moving version.
PACKAGE_PIN_NAME_RE = re.compile(r"^(?:@[A-Za-z0-9][A-Za-z0-9._-]*/)?[A-Za-z0-9][A-Za-z0-9._-]*$")
PACKAGE_PIN_VERSION_RE = re.compile(r"^[A-Za-z0-9.+~-]+$")
# Environment variables that can inject code or rewrite trust roots into a spawned
# Node/Python/Bun Pi runtime. These are stripped from harness_environment() so an
# inherited shell session cannot tamper with the live launch.
HARNESS_ENV_INJECTION_DENY_EXACT = frozenset(
    {
        "NODE_OPTIONS",
        "NODE_PATH",
        "NODE_EXTRA_CA_CERTS",
        "NODE_TLS_REJECT_UNAUTHORIZED",
        "NODE_REPL_EXTERNAL_MODULE",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONHOME",
        "PYTHONINSPECT",
        "ELECTRON_RUN_AS_NODE",
        "ELECTRON_ENABLE_LOGGING",
        "ELECTRON_OVERRIDE_DIST_PATH",
    }
)
HARNESS_ENV_INJECTION_DENY_PREFIXES = (
    "DYLD_",
    "LD_",
    "NPM_CONFIG_",
    "BUN_",
    "NODE_OPTIONS_",
)
PROJECT_GENERATED_MCP_CONFIG_RELATIVE = Path(".mcp.json")
PROJECT_MCP_BYPASS_CONFIG_RELATIVES = (Path(".pi") / "mcp.json",)
DEFAULT_NETWORK_URL = "https://github.com/EYYCHEEV/stronk-pi"
EXPECTED_ARTIFACT_IDENTITIES = {
    "stronk-pi-plugin": {
        "sourceRepo": "EYYCHEEV/stronk-pi-plugin",
        "tagPrefix": "stronk-pi-plugin-v",
        "assetPrefix": "stronk-pi-plugin-",
        "signerWorkflow": "github.com/EYYCHEEV/stronk-pi-plugin/.github/workflows/release.yml",
    },
    "stronk-pi-subagents": {
        "sourceRepo": "EYYCHEEV/stronk-pi-subagents",
        "tagPrefix": "stronk-pi-subagents-v",
        "assetPrefix": "stronk-pi-subagents-",
        "signerWorkflow": "github.com/EYYCHEEV/stronk-pi-subagents/.github/workflows/release-artifact.yml",
        "upstreamRepo": "nicobailon/pi-subagents",
        "upstreamVersion": "0.22.0",
        "upstreamCommit": "1fd371d2a068458741a15507edc6cd49a9807486",
    },
    "stronk-pi-intercom": {
        "sourceRepo": "EYYCHEEV/stronk-pi-intercom",
        "tagPrefix": "stronk-pi-intercom-v",
        "assetPrefix": "stronk-pi-intercom-",
        "signerWorkflow": "github.com/EYYCHEEV/stronk-pi-intercom/.github/workflows/release-artifact.yml",
        "upstreamRepo": "nicobailon/pi-intercom",
        "upstreamVersion": "0.6.0",
        "upstreamCommit": "5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457",
        "seedType": "npm-tarball",
        "seedPackage": "pi-intercom",
        "seedVersion": "0.6.0",
        "seedTarballUrl": "https://registry.npmjs.org/pi-intercom/-/pi-intercom-0.6.0.tgz",
        "seedTarballSha256": "76c0d5284661aac437248bb6c7a32879fe863296bd15cb533751b27cafc44818",
        "sourceArchiveSha256": "3ce238f4a75ce9c66ad76766ee878ef19dd83eef620739b73fe08e35c84311c6",
    },
}
ARTIFACT_PROVENANCE_METADATA_FIELDS = (
    "upstreamRepo",
    "upstreamVersion",
    "upstreamCommit",
    "seedType",
    "seedPackage",
    "seedVersion",
    "seedTarballUrl",
    "seedTarballSha256",
    "sourceArchiveSha256",
)
PACKAGE_ARCHIVE_REQUIRED_MEMBERS = {
    "stronk-pi-plugin": (
        "package/src/index.mjs",
    ),
    "stronk-pi-subagents": (
        "package/src/extension/index.ts",
        "package/src/agents/agents.ts",
        "package/src/agents/skills.ts",
        "package/src/agents/user-agent-dir.ts",
        "package/agents/delegate.md",
        "package/agents/worker.md",
    ),
    "stronk-pi-intercom": (
        "package/index.ts",
        "package/config.ts",
        "package/types.ts",
        "package/state-root.ts",
        "package/reply-tracker.ts",
        "package/broker/broker.ts",
        "package/broker/client.ts",
        "package/broker/framing.ts",
        "package/broker/paths.ts",
        "package/broker/spawn.ts",
        "package/ui/compose.ts",
        "package/ui/inline-message.ts",
        "package/ui/session-list.ts",
        "package/skills/stronk-pi-intercom/SKILL.md",
    ),
}
RUNTIME_PACKAGE_REQUIRED_PATHS = {
    "stronk-pi-subagents": (
        "src/extension/index.ts",
        "src/agents/agents.ts",
        "src/agents/skills.ts",
        "src/agents/user-agent-dir.ts",
        "agents/delegate.md",
        "agents/worker.md",
    ),
    "stronk-pi-intercom": (
        "index.ts",
        "config.ts",
        "types.ts",
        "state-root.ts",
        "reply-tracker.ts",
        "broker/broker.ts",
        "broker/client.ts",
        "broker/framing.ts",
        "broker/paths.ts",
        "broker/spawn.ts",
        "ui/compose.ts",
        "ui/inline-message.ts",
        "ui/session-list.ts",
        "skills/stronk-pi-intercom/SKILL.md",
    ),
}
SUBAGENTS_LEGACY_PARENT_SKILL_VERSION = "0.22.0-stronk.3"
SUBAGENTS_LEGACY_PARENT_SKILL = "pi-subagents"
SUBAGENTS_PARENT_SKILL = "stronkpi-agents"
PERSONAL_PATH_RE = re.compile(r"(?<![A-Za-z0-9_.-])(?:/Users|/home)/[^/\s\"':,;)]+")
IMAGE_PREFLIGHT_HANDLE_RE = re.compile(r"^image-preflight-[0-9A-Fa-f-]{36}$")
ENV_NAMES = (
    "DEEPSEEK_API_KEY",
    "MOONSHOT_API_KEY",
    "KIMI_API_KEY",
    "KIMI_CODE_API_KEY",
    "ALIBABA_CLOUD_CODING_PLAN_API_KEY",
)
REAL_HOME_WRITE_RISK_RELATIVES = (
    Path(".pi"),
    Path(".config") / "pi",
    Path(".local") / "share" / "pi",
    Path(".cache") / "pi",
)
READ_ONLY_TOOLS = {"read", "grep", "find", "ls", "glob", "todoread"}
WEB_TOOLS = {"web_search", "code_search", "fetch_content"}
IMAGE_TOOLS = {"image_read", "image_preflight_read"}
SESSION_TOOLS = {"todowrite", "todoread", "question", "ask_user"}
MUTATING_TOOLS = {"bash", "write", "edit", "patch", "apply_patch", "multi_edit", "user_bash"}
CODEX_HOOK_EVENTS = {
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "Stop",
}
CODEX_HOOK_REQUIRED_FIELDS = {
    "SessionStart": {
        "session_id",
        "transcript_path",
        "cwd",
        "hook_event_name",
        "model",
        "permission_mode",
        "source",
    },
    "UserPromptSubmit": {
        "session_id",
        "turn_id",
        "transcript_path",
        "cwd",
        "hook_event_name",
        "model",
        "permission_mode",
        "prompt",
    },
    "PreToolUse": {
        "session_id",
        "turn_id",
        "transcript_path",
        "cwd",
        "hook_event_name",
        "model",
        "permission_mode",
        "tool_name",
        "tool_input",
        "tool_use_id",
    },
    "PermissionRequest": {
        "session_id",
        "turn_id",
        "transcript_path",
        "cwd",
        "hook_event_name",
        "model",
        "permission_mode",
        "tool_name",
        "tool_input",
    },
    "PostToolUse": {
        "session_id",
        "turn_id",
        "transcript_path",
        "cwd",
        "hook_event_name",
        "model",
        "permission_mode",
        "tool_name",
        "tool_input",
        "tool_response",
        "tool_use_id",
    },
    "Stop": {
        "session_id",
        "turn_id",
        "transcript_path",
        "cwd",
        "hook_event_name",
        "model",
        "permission_mode",
        "stop_hook_active",
        "last_assistant_message",
    },
}
DENY_BASH_PATTERNS = (
    re.compile(r"(^|[;&|]\s*)sudo(\s|$)"),
    re.compile(r"rm\s+-[^\n;|&]*[rf][^\n;|&]*\s+/(?:\s|$)"),
    re.compile(r"curl\b[^\n|;]*\|\s*(?:sh|bash|zsh)\b"),
    re.compile(r"wget\b[^\n|;]*\|\s*(?:sh|bash|zsh)\b"),
    re.compile(r"\bgit\s+reset\s+--hard\b"),
    re.compile(r"\bgit\s+clean\s+-[^\n;|&]*[df][^\n;|&]*\b"),
)
SENSITIVE_PATH_PARTS = {".env", ".ssh", ".gnupg", ".aws", ".config/mcp", ".codex", ".claude"}
# Blocked original upstream Pi/Pi-subagent repositories. The Stronk Pi upstream-boundary
# policy forbids creating any public activity (PRs, issues, comments, reviews, pushes) in
# these repos; the guard safety screen enforces that policy mechanically for direct
# owner/name or github.com references in gh/git commands.
BLOCKED_UPSTREAM_REPOSITORIES = (
    "earendil-works/pi",
    "badlogic/pi-mono",
    "nicobailon/pi-subagents",
    "nicobailon/pi-intercom",
)
BLOCKED_UPSTREAM_REPO_RE = re.compile(
    r"(?:github\.com[:/])?(?:"
    + "|".join(re.escape(repo) for repo in BLOCKED_UPSTREAM_REPOSITORIES)
    + r")",
    re.IGNORECASE,
)
# Git subcommands that perform network/public actions and can target a remote.
BLOCKED_UPSTREAM_GIT_ACTIONS = frozenset(
    {"push", "clone", "remote", "fetch", "pull", "submodule"}
)


class StronkPiError(RuntimeError):
    """Fail-closed setup error."""


@dataclass(frozen=True)
class ArtifactResult:
    name: str
    version: str
    path: Path
    sha256: str
    byte_size: int


def setup_root() -> Path:
    raw = os.environ.get("STRONKPI_SETUP_ROOT")
    if raw:
        if not dev_overrides_enabled():
            raise StronkPiError("STRONKPI_SETUP_ROOT requires STRONK_PI_DEV_OVERRIDES=1")
        return Path(raw).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if SECRET_KEY_PATTERN.search(str(key)):
                redacted[str(key)] = "<redacted>"
            else:
                redacted[str(key)] = redact(item)
        return redacted
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        text = value
        for pattern in SECRET_VALUE_PATTERNS:
            text = pattern.sub("<redacted>", text)
        return text
    return value


def json_out(payload: dict[str, Any]) -> None:
    print(json.dumps(redact(payload), indent=2, sort_keys=True))


def is_plain_object(value: Any) -> bool:
    return isinstance(value, dict)


def nonempty(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def fail_if_floating(label: str, value: str) -> None:
    if FLOATING_VERSION_RE.search(value):
        raise StronkPiError(f"{label} uses a floating or mutable version reference")


def fail_if_floating_mcp_arg(label: str, value: str) -> None:
    if MCP_FLOATING_ARG_RE.search(value.strip()):
        raise StronkPiError(f"{label} uses a floating or mutable version reference")


def parse_ip_literal(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        return None


def is_dns_proxy_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return any(ip in network for network in DNS_PROXY_IP_NETWORKS)


def assert_public_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address, label: str) -> None:
    blocked = ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
    blocked = blocked or ip.is_unspecified or ip.is_reserved
    blocked = blocked or any(ip in network for network in BLOCKED_METADATA_IP_NETWORKS)
    if blocked and not is_dns_proxy_ip(ip):
        raise StronkPiError(f"{label} private/local IP denied: {ip}")


def resolve_public_host(host: str, label: str) -> list[dict[str, Any]]:
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise StronkPiError(f"{label} DNS resolution failed: {host}") from exc
    addresses: list[dict[str, Any]] = []
    seen: set[str] = set()
    for info in infos:
        ip_text = info[4][0]
        if ip_text in seen:
            continue
        seen.add(ip_text)
        ip = ipaddress.ip_address(ip_text)
        assert_public_ip(ip, label)
        addresses.append({"address": ip_text, "family": ip.version})
    if not addresses:
        raise StronkPiError(f"{label} DNS resolution returned no addresses")
    return addresses


def check_public_http_url(value: str, label: str) -> dict[str, Any]:
    stripped = value.strip()
    parsed = urlparse(stripped)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise StronkPiError(f"{label} must be an http(s) URL")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise StronkPiError(f"{label} URL has no host")
    if host in BLOCKED_WEB_HOSTS or any(host.endswith(suffix) for suffix in BLOCKED_WEB_SUFFIXES):
        raise StronkPiError(f"{label} private/local host denied: {host}")
    literal = parse_ip_literal(host)
    if literal is not None:
        assert_public_ip(literal, label)
        addresses = [{"address": str(literal), "family": literal.version}]
    else:
        addresses = resolve_public_host(host, label)
    return {"url": stripped, "hostname": host, "addresses": addresses}


def default_dangerous_command_hook_path() -> Path:
    return Path.home() / ".agents" / "hooks" / "block-dangerous-commands.py"


def hook_context(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("hookContext") or event.get("hook_context") or {}
    return raw if is_plain_object(raw) else {}


def context_string(context: dict[str, Any], key: str, *env_names: str, default: str | None = None) -> str | None:
    value = context.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    for env_name in env_names:
        env_value = os.environ.get(env_name)
        if env_value and env_value.strip():
            return env_value.strip()
    return default


def codex_transcript_path(context: dict[str, Any]) -> str | None:
    value = context_string(context, "transcript_path", "PI_TRANSCRIPT_PATH", "STRONK_PI_TRANSCRIPT_PATH")
    return value if value else None


def shared_hook_pre_tool_use_input(
    tool_name: str,
    tool_input: dict[str, Any],
    cwd: Path,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    return {
        "session_id": context_string(context, "session_id", "PI_SESSION_ID", default="stronk-pi"),
        "turn_id": context_string(context, "turn_id", "PI_TURN_ID", default=f"stronk-pi-{os.getpid()}"),
        "transcript_path": codex_transcript_path(context),
        "cwd": str(cwd.resolve()),
        "hook_event_name": "PreToolUse",
        "model": context_string(context, "model", "PI_MODEL", default="stronk-pi"),
        "permission_mode": context_string(context, "permission_mode", "PI_PERMISSION_MODE", default="default"),
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": context_string(context, "tool_use_id", "PI_TOOL_USE_ID", default=f"stronk-pi-{os.getpid()}"),
    }


def shared_hook_reason(payload: dict[str, Any], fallback: str) -> str:
    hook_specific = payload.get("hookSpecificOutput")
    if is_plain_object(hook_specific):
        for key in ("permissionDecisionReason", "reason", "message", "additionalContext"):
            reason = nonempty(hook_specific.get(key))
            if reason:
                return reason
    for key in ("reason", "message", "stopReason", "systemMessage"):
        reason = nonempty(payload.get(key))
        if reason:
            return reason
    return fallback


def interpret_shared_hook_payload(payload: dict[str, Any] | None) -> tuple[bool, str]:
    if payload is None:
        return True, "allowed by shared dangerous-command hook"
    if payload.get("continue") is False:
        return False, shared_hook_reason(payload, "shared dangerous-command hook stopped processing")
    hook_specific = payload.get("hookSpecificOutput")
    if is_plain_object(hook_specific):
        if hook_specific.get("updatedInput") is not None:
            return False, "shared dangerous-command hook attempted to mutate tool input"
        decision = str(hook_specific.get("permissionDecision") or "").strip().lower()
        if decision in {"deny", "block", "ask"}:
            return False, shared_hook_reason(payload, "blocked by shared dangerous-command hook")
        if decision == "allow":
            return True, "allowed by shared dangerous-command hook"
    decision = str(payload.get("decision") or "").strip().lower()
    if decision in {"block", "deny", "ask"}:
        return False, shared_hook_reason(payload, "blocked by shared dangerous-command hook")
    if decision in {"approve", "allow"}:
        return True, "allowed by shared dangerous-command hook"
    return True, "allowed by shared dangerous-command hook"


def run_shared_pre_tool_use_hook(
    tool_name: str,
    tool_input: dict[str, Any],
    cwd: Path,
    context: dict[str, Any] | None = None,
) -> tuple[bool, str] | None:
    raw = os.environ.get("STRONK_PI_DANGEROUS_COMMAND_HOOK")
    if not raw:
        return None
    hook_path = Path(raw).expanduser()
    if not hook_path.is_file():
        raise StronkPiError(f"shared dangerous-command hook missing: {hook_path}")
    event = shared_hook_pre_tool_use_input(tool_name, tool_input, cwd, context)
    try:
        proc = subprocess.run(
            [sys.executable or "python3", str(hook_path)],
            input=json.dumps(event, separators=(",", ":")),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=SHARED_HOOK_TIMEOUT_SEC,
            check=False,
            text=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise StronkPiError("shared dangerous-command hook timed out") from exc
    except Exception as exc:
        raise StronkPiError(f"shared dangerous-command hook failed to run: {exc}") from exc
    if proc.returncode == 2:
        reason = nonempty(proc.stderr) or nonempty(proc.stdout) or "blocked by shared dangerous-command hook"
        return False, reason
    if proc.returncode != 0:
        detail = nonempty(proc.stderr) or nonempty(proc.stdout) or "no output"
        raise StronkPiError(f"shared dangerous-command hook failed closed with exit {proc.returncode}: {detail}")
    stdout = proc.stdout.strip()
    if not stdout:
        return True, "allowed by shared dangerous-command hook"
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise StronkPiError(f"shared dangerous-command hook returned malformed stdout: {exc}") from exc
    if not is_plain_object(parsed):
        raise StronkPiError("shared dangerous-command hook returned non-object JSON")
    return interpret_shared_hook_payload(parsed)


def command_targets_blocked_upstream(command: str) -> bool:
    """Return True when a shell command performs a public git/gh action against a blocked upstream repo.

    Detects blocked repositories named directly as ``owner/name`` or via a github.com URL
    inside a ``gh`` invocation or a state-changing ``git`` subcommand (push/clone/remote/
    fetch/pull/submodule). Remote-name indirection cannot be resolved statically and is
    intentionally out of scope; the textual upstream-boundary policy still applies.
    """
    stripped = command.strip()
    if not stripped or not BLOCKED_UPSTREAM_REPO_RE.search(stripped):
        return False
    # Split on shell/line separators so compound commands are inspected segment by segment.
    for segment in re.split(r"[;\n&|]+", stripped):
        tokens = segment.split()
        if len(tokens) < 2:
            continue
        program = tokens[0]
        if program == "gh":
            if BLOCKED_UPSTREAM_REPO_RE.search(segment):
                return True
        elif program == "git":
            if (
                tokens[1] in BLOCKED_UPSTREAM_GIT_ACTIONS
                and BLOCKED_UPSTREAM_REPO_RE.search(segment)
            ):
                return True
    return False


def internally_screen_bash(command: str) -> tuple[bool, str]:
    if command_targets_blocked_upstream(command):
        return False, "blocked upstream git/gh action denied by distribution boundary"
    for pattern in DENY_BASH_PATTERNS:
        if pattern.search(command):
            return False, "blocked by distribution-owned shell safety screen"
    if string_has_secret(command):
        return False, "shell command contains a secret-like value"
    return True, "allowed by distribution-owned shell safety screen"


def target_path_from_payload(tool: str, payload: dict[str, Any], cwd: Path) -> Path:
    for key in ("path", "file_path", "filepath", "target", "filename"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            raw = Path(value).expanduser()
            return raw if raw.is_absolute() else cwd / raw
    raise StronkPiError(f"{tool} payload missing target path")


def validate_mutation_target(tool: str, payload: dict[str, Any], cwd: Path) -> tuple[Path, str]:
    target = target_path_from_payload(tool, payload, cwd).resolve(strict=False)
    cwd_resolved = cwd.resolve(strict=False)
    if not is_relative_to(target, cwd_resolved):
        raise StronkPiError(f"{tool} target escapes cwd: {target}")
    text = str(target)
    if any(part in text for part in SENSITIVE_PATH_PARTS):
        raise StronkPiError(f"{tool} target touches sensitive path: {target}")
    return target, f"{tool} target stays under cwd"


def validate_image_tool(tool: str, payload: dict[str, Any]) -> tuple[bool, str]:
    if tool == "image_preflight_read":
        handle = payload.get("handle")
        if not isinstance(handle, str) or not IMAGE_PREFLIGHT_HANDLE_RE.fullmatch(handle.strip()):
            raise StronkPiError("image_preflight_read requires a valid image preflight handle")
    return True, "distribution-owned safe tool class"


STRONK_SUBAGENT_DENIED_OVERRIDE_KEYS = {
    "allowedTools",
    "apiKey",
    "artifactPath",
    "async",
    "background",
    "chain",
    "concurrency",
    "context",
    "cwd",
    "extensions",
    "forkContext",
    "fork_context",
    "includeRaw",
    "maxConcurrency",
    "model",
    "output",
    "outputMode",
    "outputPath",
    "packages",
    "provider",
    "raw",
    "skill",
    "skills",
    "systemPrompt",
    "thinking",
    "toolChoice",
    "tools",
    "unredacted",
    "worktree",
    "workingDirectory",
}


def find_stronk_subagent_override(value: Any, path: tuple[str, ...] = ()) -> tuple[str, str] | None:
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = (*path, str(key))
            if key in STRONK_SUBAGENT_DENIED_OVERRIDE_KEYS:
                return key, ".".join(next_path)
            found = find_stronk_subagent_override(item, next_path)
            if found:
                return found
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found = find_stronk_subagent_override(item, (*path, str(index)))
            if found:
                return found
    return None


def guarded_tool_decision(tool: str, payload: dict[str, Any], cwd: Path, context: dict[str, Any]) -> dict[str, Any]:
    if tool in IMAGE_TOOLS:
        allowed, reason = validate_image_tool(tool, payload)
        return {"allow": allowed, "reason": reason, "input": payload}
    if tool == "stronk_subagent":
        override = find_stronk_subagent_override(payload)
        if override:
            key, override_path = override
            if key == "cwd":
                reason = f"stronk_subagent cwd override denied: {override_path}"
            else:
                reason = f"stronk_subagent override denied: {key} at {override_path}"
            return {
                "allow": False,
                "reason": reason,
                "input": payload,
            }
        return {"allow": True, "reason": "distribution-owned safe tool class", "input": payload}
    if tool in {"mcp"} | WEB_TOOLS | SESSION_TOOLS | READ_ONLY_TOOLS:
        return {"allow": True, "reason": "distribution-owned safe tool class", "input": payload}
    if tool == "subagent":
        return {"allow": False, "reason": "raw subagent tool denied; use stronk_subagent", "input": payload}
    if tool == "bash":
        command = payload.get("command")
        if not isinstance(command, str) or not command.strip():
            raise StronkPiError("bash payload missing command")
        # The distribution-owned screen always runs first and its deny is final, even
        # when a shared dangerous-command hook is configured, so upstream-boundary and
        # secret-laden commands can never be allowed by an external hook.
        allowed, reason = internally_screen_bash(command)
        if not allowed:
            return {"allow": allowed, "reason": reason, "input": payload}
        shared = run_shared_pre_tool_use_hook("shell_command", {"command": command}, cwd, context)
        if shared is not None:
            allowed, shared_reason = shared
            reason = f"{reason}; {shared_reason}"
        return {"allow": allowed, "reason": reason, "input": payload}
    if tool in {"write", "edit"}:
        _target, reason = validate_mutation_target(tool, payload, cwd)
        shared = run_shared_pre_tool_use_hook(tool, payload, cwd, context)
        if shared is not None:
            allowed, shared_reason = shared
            reason = f"{reason}; {shared_reason}"
        else:
            allowed = True
        return {"allow": allowed, "reason": reason, "input": payload}
    if tool in MUTATING_TOOLS:
        return {"allow": False, "reason": f"unsupported mutating tool denied: {tool}", "input": payload}
    return {"allow": False, "reason": f"unknown tool denied by default: {tool}", "input": payload}


def hook_decision(event: dict[str, Any]) -> dict[str, Any]:
    event_type = event.get("event") or event.get("type")
    cwd = Path(str(event.get("cwd") or os.getcwd())).expanduser()
    context = hook_context(event)
    if event_type == "tool_call":
        tool = str(event.get("toolName") or event.get("tool_name") or "")
        payload = event.get("input")
        if not tool or not is_plain_object(payload):
            raise StronkPiError("tool_call payload requires toolName and object input")
        return guarded_tool_decision(tool, payload, cwd, context)
    if event_type == "user_bash":
        command = event.get("command")
        if not isinstance(command, str) or not command.strip():
            raise StronkPiError("user_bash payload missing command")
        allowed, reason = internally_screen_bash(command)
        if not allowed:
            return {
                "allow": allowed,
                "reason": reason,
                "command": command,
                "excludeFromContext": bool(event.get("excludeFromContext")),
            }
        shared = run_shared_pre_tool_use_hook("shell_command", {"command": command}, cwd, context)
        if shared is not None:
            allowed, shared_reason = shared
            reason = f"{reason}; {shared_reason}"
        return {
            "allow": allowed,
            "reason": reason,
            "command": command,
            "excludeFromContext": bool(event.get("excludeFromContext")),
        }
    raise StronkPiError(f"unsupported Pi hook event: {event_type!r}")


def cmd_hook(_args: argparse.Namespace) -> int:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw)
        if not is_plain_object(event):
            raise StronkPiError("hook input must be a JSON object")
        json_out(hook_decision(event))
        return 0
    except StronkPiError as exc:
        json_out({"allow": False, "reason": str(redact(str(exc)))})
        return 1
    except Exception as exc:
        json_out({"allow": False, "reason": f"unexpected hook failure: {redact(str(exc))}"})
        return 2


def validate_codex_hook_payload(payload: dict[str, Any]) -> str:
    event_name = payload.get("hook_event_name") or payload.get("hookEventName")
    if not isinstance(event_name, str) or event_name not in CODEX_HOOK_EVENTS:
        raise StronkPiError(f"unsupported Codex hook event: {event_name!r}")
    if payload.get("hook_event_name") != event_name:
        raise StronkPiError("Codex hook payload must use hook_event_name")
    missing = sorted(key for key in CODEX_HOOK_REQUIRED_FIELDS[event_name] if key not in payload)
    if missing:
        raise StronkPiError(f"Codex {event_name} payload missing field(s): {', '.join(missing)}")
    if not isinstance(payload.get("session_id"), str) or not payload["session_id"].strip():
        raise StronkPiError(f"Codex {event_name} payload requires session_id")
    if event_name != "SessionStart" and (not isinstance(payload.get("turn_id"), str) or not payload["turn_id"].strip()):
        raise StronkPiError(f"Codex {event_name} payload requires turn_id")
    if not isinstance(payload.get("cwd"), str) or not payload["cwd"].strip():
        raise StronkPiError(f"Codex {event_name} payload requires cwd")
    if not isinstance(payload.get("model"), str) or not payload["model"].strip():
        raise StronkPiError(f"Codex {event_name} payload requires model")
    if not isinstance(payload.get("permission_mode"), str) or not payload["permission_mode"].strip():
        raise StronkPiError(f"Codex {event_name} payload requires permission_mode")
    transcript = payload.get("transcript_path")
    if transcript is not None and not isinstance(transcript, str):
        raise StronkPiError(f"Codex {event_name} transcript_path must be string or null")
    if event_name == "SessionStart":
        if payload.get("source") not in {"startup", "resume", "clear"}:
            raise StronkPiError("Codex SessionStart source must be startup, resume, or clear")
    elif event_name == "UserPromptSubmit":
        if not isinstance(payload.get("prompt"), str):
            raise StronkPiError("Codex UserPromptSubmit prompt must be a string")
    elif event_name in {"PreToolUse", "PermissionRequest", "PostToolUse"}:
        if not isinstance(payload.get("tool_name"), str) or not payload["tool_name"].strip():
            raise StronkPiError(f"Codex {event_name} requires tool_name")
        if not is_plain_object(payload.get("tool_input")):
            raise StronkPiError(f"Codex {event_name} tool_input must be a JSON object")
        if event_name in {"PreToolUse", "PostToolUse"}:
            if not isinstance(payload.get("tool_use_id"), str) or not payload["tool_use_id"].strip():
                raise StronkPiError(f"Codex {event_name} requires tool_use_id")
        if event_name == "PostToolUse" and not is_plain_object(payload.get("tool_response")):
            raise StronkPiError("Codex PostToolUse tool_response must be a JSON object")
    elif event_name == "Stop":
        if not isinstance(payload.get("stop_hook_active"), bool):
            raise StronkPiError("Codex Stop stop_hook_active must be boolean")
        if payload.get("last_assistant_message") is not None and not isinstance(payload["last_assistant_message"], str):
            raise StronkPiError("Codex Stop last_assistant_message must be string or null")
    return event_name


def cmd_codex_hook(_args: argparse.Namespace) -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
        if not is_plain_object(payload):
            raise StronkPiError("codex-hook input must be a JSON object")
        event_name = validate_codex_hook_payload(payload)
        json_out({"continue": True, "hookSpecificOutput": {"hookEventName": event_name}})
        return 0
    except StronkPiError as exc:
        json_out({"continue": True, "warning": str(redact(str(exc)))})
        return 0
    except Exception as exc:
        json_out({"continue": True, "warning": f"unexpected codex-hook failure: {redact(str(exc))}"})
        return 0


def cmd_url_check(_args: argparse.Namespace) -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
        if not is_plain_object(payload):
            raise StronkPiError("url-check input must be a JSON object")
        url = payload.get("url")
        if not isinstance(url, str) or not url.strip():
            raise StronkPiError("url-check requires url")
        json_out({"allow": True, **check_public_http_url(url, "url-check URL")})
        return 0
    except StronkPiError as exc:
        json_out({"allow": False, "reason": str(redact(str(exc)))})
        return 0
    except Exception as exc:
        json_out({"allow": False, "reason": f"unexpected url-check failure: {redact(str(exc))}"})
        return 0


def cmd_telegram(_args: argparse.Namespace) -> int:
    try:
        raw = sys.stdin.read() or "{}"
        payload = redact(json.loads(raw))
    except Exception:
        payload = {"type": "unparseable", "payload": "<redacted>"}
    transport = os.environ.get("STRONK_PI_TELEGRAM_TRANSPORT")
    if not transport:
        return 0
    try:
        subprocess.run(
            [transport],
            input=json.dumps(payload, sort_keys=True),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False,
            text=True,
        )
    except Exception:
        return 0
    return 0


def state_root() -> Path:
    return resolve_state_root()


def xdg_config_home() -> Path:
    raw = os.environ.get("XDG_CONFIG_HOME")
    root = Path(raw).expanduser() if raw else Path.home() / ".config"
    if not root.is_absolute():
        raise StronkPiError(f"XDG_CONFIG_HOME must be absolute: {root}")
    return root


def default_mcp_registry_path() -> Path:
    raw = os.environ.get("STRONKPI_MCP_REGISTRY") or os.environ.get("STRONK_PI_MCP_REGISTRY")
    if raw:
        return Path(raw).expanduser()
    return xdg_config_home() / "mcp" / "registry.toml"


def ensure_private_dir(path: Path) -> Path:
    if path.exists() and path.is_symlink():
        raise StronkPiError(f"directory must not be a symlink: {path}")
    path.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise StronkPiError(f"not a safe directory: {path}")
    if path.stat().st_uid != os.getuid():
        raise StronkPiError(f"directory is not owned by current user: {path}")
    os.chmod(path, 0o700)
    return path.resolve()


def runtime_backup_root(root: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / "runtime-backups" / stamp


def migrate_legacy_managed_symlinks(root: Path, *, dry_run: bool) -> list[Path]:
    backups: list[Path] = []
    backup_root = runtime_backup_root(root)
    for relative_path in LEGACY_MANAGED_RUNTIME_PATHS:
        path = root / relative_path
        if not path.is_symlink():
            continue
        backup_path = backup_root / (relative_path.as_posix().replace("/", "-") + ".symlink-target.txt")
        if dry_run:
            backups.append(backup_path)
            continue
        try:
            target = os.readlink(path)
        except FileNotFoundError:
            continue
        ensure_private_dir(root / "runtime-backups")
        ensure_private_dir(backup_path.parent)
        backup_path.write_text(target + "\n", encoding="utf-8")
        os.chmod(backup_path, 0o600)
        backups.append(backup_path)
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    return backups


def migrate_legacy_generated_agents_symlink(root: Path, *, dry_run: bool) -> Path | None:
    backups = migrate_legacy_managed_symlinks(root, dry_run=dry_run)
    for backup in backups:
        if backup.name == "agent-agents.symlink-target.txt":
            return backup
    return None


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StronkPiError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StronkPiError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise StronkPiError(f"JSON file must contain an object: {path}")
    return data


def strip_toml_comment(line: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(line):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\" and quote == '"':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "#":
            return line[:index].strip()
    return line.strip()


def split_top_level_commas(value: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\" and quote == '"':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char in "[{(":
            depth += 1
        elif char in "]})":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    tail = value[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def parse_toml_key(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return str(json.loads(value))
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def parse_simple_toml_value(value: str) -> Any:
    value = value.strip()
    if not value:
        raise StronkPiError("empty TOML value")
    if value.startswith('"') and value.endswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_simple_toml_value(part) for part in split_top_level_commas(inner)]
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        table: dict[str, Any] = {}
        if not inner:
            return table
        for part in split_top_level_commas(inner):
            if "=" not in part:
                raise StronkPiError(f"invalid inline TOML table item: {part}")
            key, item = part.split("=", 1)
            table[parse_toml_key(key)] = parse_simple_toml_value(item)
        return table
    if re.fullmatch(r"[+-]?\d+", value):
        return int(value)
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    raise StronkPiError(f"unsupported TOML value: {value}")


def load_simple_toml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current: dict[str, Any] = data
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = strip_toml_comment(raw_line)
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            if not section:
                raise StronkPiError(f"invalid TOML section at line {line_number}")
            current = data
            for part in section.split("."):
                key = parse_toml_key(part)
                child = current.setdefault(key, {})
                if not isinstance(child, dict):
                    raise StronkPiError(f"TOML section conflicts with scalar at line {line_number}")
                current = child
            continue
        if "=" not in line:
            raise StronkPiError(f"invalid TOML assignment at line {line_number}")
        key, value = line.split("=", 1)
        current[parse_toml_key(key)] = parse_simple_toml_value(value)
    return data


def load_mcp_registry_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return load_simple_toml(path)
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:  # type: ignore[name-defined]
        raise StronkPiError(f"invalid MCP registry TOML: {exc}") from exc
    if not isinstance(data, dict):
        raise StronkPiError("MCP registry TOML must contain a table")
    return data


def load_toml_document(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return load_simple_toml(path)
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise StronkPiError(f"missing TOML file: {path}") from exc
    except tomllib.TOMLDecodeError as exc:  # type: ignore[name-defined]
        raise StronkPiError(f"invalid TOML file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise StronkPiError(f"TOML file must contain a table: {path}")
    return data


def toml_quote(value: str) -> str:
    return json.dumps(value)


def dev_overrides_enabled() -> bool:
    return os.environ.get("STRONK_PI_DEV_OVERRIDES") == "1" or os.environ.get("STRONKPI_DEV_OVERRIDES") == "1"


def state_root_env_value() -> str | None:
    raw_setup = os.environ.get("STRONKPI_STATE_ROOT")
    raw_runtime = os.environ.get("STRONK_PI_STATE_ROOT")
    if raw_setup and raw_runtime and raw_setup != raw_runtime:
        raise StronkPiError("STRONKPI_STATE_ROOT and STRONK_PI_STATE_ROOT disagree")
    return raw_setup or raw_runtime


def resolve_state_root() -> Path:
    raw = state_root_env_value()
    if raw and not dev_overrides_enabled():
        raise StronkPiError("STRONKPI_STATE_ROOT/STRONK_PI_STATE_ROOT requires STRONK_PI_DEV_OVERRIDES=1")
    root = Path(raw).expanduser() if raw else Path.home() / ".stronk-pi"
    if not root.is_absolute():
        raise StronkPiError(f"state root must be absolute: {root}")
    if root.exists() and root.is_symlink():
        raise StronkPiError(f"state root must not be a symlink: {root}")
    return root


def harness_state_root() -> Path:
    return resolve_state_root()


def state_config_root(root: Path) -> Path:
    return root / "config"


def state_cache_root(root: Path) -> Path:
    return root / "cache"


def state_log_root(root: Path) -> Path:
    return root / "logs"


def state_tmp_root(root: Path) -> Path:
    return root / "tmp"


def state_agent_dir(root: Path) -> Path:
    return root / "agent"


def state_session_dir(root: Path) -> Path:
    return state_agent_dir(root) / "sessions"


def state_web_search_config_path(root: Path) -> Path:
    return state_config_root(root) / "pi" / "web-search.json"


def state_intercom_bridge_path(root: Path, name: str = "stronk-pi-intercom") -> Path:
    return state_agent_dir(root) / "extensions" / name


def real_home_write_risks(home: Path, root: Path) -> list[str]:
    return [str(home / relative) for relative in REAL_HOME_WRITE_RISK_RELATIVES] + [str(root / "home")]


def ensure_state_root_layout(root: Path) -> None:
    ensure_private_dir(root)
    for path in (
        state_config_root(root),
        state_config_root(root) / "pi",
        state_agent_dir(root),
        state_agent_dir(root) / "agents",
        state_agent_dir(root) / "extensions",
        state_session_dir(root),
        state_log_root(root),
        state_cache_root(root),
        state_tmp_root(root),
    ):
        ensure_private_dir(path)


def expand_runtime_path(raw: str, root: Path | None = None) -> Path:
    if raw == "~/.stronk-pi" or raw.startswith("~/.stronk-pi/"):
        base = root if root is not None else Path.home() / ".stronk-pi"
        suffix = raw.removeprefix("~/.stronk-pi").lstrip("/")
        return (base / suffix).resolve(strict=False)
    return Path(raw).expanduser().resolve(strict=False)


def resolve_manifest_relative(manifest_path: Path, raw: str, root: Path) -> Path:
    if raw.startswith("~"):
        return expand_runtime_path(raw, root)
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = manifest_path.parent / candidate
    return candidate.resolve(strict=False)


def write_managed_text(
    path: Path,
    content: str,
    *,
    dry_run: bool,
    mode: int = 0o600,
    require_marker: bool = True,
) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() and path.is_file() else None
    if existing == content:
        if not dry_run:
            os.chmod(path, mode)
        return False
    if dry_run:
        return True
    if path.exists():
        if path.is_symlink():
            raise StronkPiError(f"managed file must not be a symlink: {path}")
        if require_marker and existing is not None and not is_managed_content(existing):
            raise StronkPiError(f"refusing to overwrite unmanaged file; use roles.local.toml for local overrides: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(tmp, mode)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise
    return True


def is_managed_content(content: str) -> bool:
    return MANAGED_MARKER in content or any(marker in content for marker in LEGACY_MANAGED_MARKERS)


def write_private_runtime_text(path: Path, content: str, *, dry_run: bool, mode: int = 0o600) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() and path.is_file() else None
    if existing == content:
        if not dry_run:
            os.chmod(path, mode)
        return False
    if dry_run:
        return True
    if path.exists() and not path.is_file():
        raise StronkPiError(f"managed runtime file path is not a regular file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(tmp, mode)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise
    return True


def write_executable_script(path: Path, content: str) -> None:
    if path.exists() and path.is_dir():
        raise StronkPiError(f"install target is a directory: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        path.unlink()
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(tmp, 0o755)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise


def public_role_templates() -> list[Path]:
    template_dir = setup_root() / ROLE_TEMPLATE_RELATIVE
    return sorted(template_dir.glob("*.toml"))


def role_template_name(path: Path) -> str:
    data = load_toml_document(path)
    name = data.get("name") or path.stem
    if not isinstance(name, str) or not ROLE_NAME_RE.fullmatch(name):
        raise StronkPiError(f"invalid role template name in {path}")
    return name


ROLE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def extract_role_description(instructions: str, role_name: str) -> str:
    for line in instructions.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("role:"):
            description = stripped.split(":", 1)[1].strip().rstrip(".")
            if description:
                return description[:180]
    return role_name.replace("-", " ")


def validate_public_role_templates() -> list[str]:
    templates = public_role_templates()
    if not templates:
        raise StronkPiError("no public role templates found")
    names = [role_template_name(path) for path in templates]
    if len(set(names)) != len(names):
        raise StronkPiError("duplicate public role template names")
    for path in templates:
        data = load_toml_document(path)
        instructions = data.get("developer_instructions")
        if not isinstance(instructions, str) or not instructions.strip():
            raise StronkPiError(f"role template missing developer_instructions: {path.name}")
    return sorted(names)


def role_manifest_template(root: Path) -> str:
    source = (setup_root() / DEFAULT_ROLE_MANIFEST_RELATIVE).read_text(encoding="utf-8")
    return source.replace("~/.stronk-pi/config/role-templates", str(root / "config" / "role-templates")).replace(
        "~/.stronk-pi/agent/agents",
        str(root / "agent" / "agents"),
    )


def defaults_template(root: Path) -> str:
    source = (setup_root() / DEFAULTS_RELATIVE).read_text(encoding="utf-8")
    return source.replace("~/.stronk-pi", str(root))


def install_role_templates(root: Path, *, dry_run: bool) -> list[Path]:
    changed: list[Path] = []
    target_dir = root / "config" / "role-templates"
    for source in public_role_templates():
        target = target_dir / source.name
        if target.is_file() and IMPORTED_CODEX_ROLE_MARKER in target.read_text(
            encoding="utf-8",
            errors="ignore",
        ):
            continue
        if write_managed_text(target, source.read_text(encoding="utf-8"), dry_run=dry_run):
            changed.append(target)
    return changed


def discover_codex_role_dir(source: str | None = None) -> Path:
    if source:
        candidate = Path(source).expanduser()
        if not candidate.is_absolute():
            candidate = (Path.cwd() / candidate).resolve(strict=False)
        if not candidate.is_dir():
            raise StronkPiError(f"Codex role source directory missing: {candidate}")
        return candidate.resolve(strict=False)
    home = Path.home()
    checked: list[Path] = []
    for relative in DEFAULT_CODEX_ROLE_DIR_CANDIDATES:
        candidate = (home / relative).resolve(strict=False)
        checked.append(candidate)
        if candidate.is_dir() and any(candidate.glob("*.toml")):
            return candidate
    raise StronkPiError(
        "no Codex role source directory found; checked "
        + ", ".join(str(path) for path in checked)
    )


def codex_role_files(source_dir: Path) -> list[Path]:
    files = sorted(source_dir.glob("*.toml"))
    if not files:
        raise StronkPiError(f"no Codex role TOMLs found under {source_dir}")
    for path in files:
        if not path.is_file():
            raise StronkPiError(f"Codex role TOML must be a file: {path}")
        if not ROLE_NAME_RE.fullmatch(path.stem):
            raise StronkPiError(f"invalid Codex role filename: {path.name}")
    return files


def normalized_imported_role(path: Path) -> tuple[str, str]:
    role = load_toml_document(path)
    raw_name = role.get("name") or path.stem
    if not isinstance(raw_name, str) or not ROLE_NAME_RE.fullmatch(raw_name):
        raise StronkPiError(f"invalid Codex role name in {path}")
    instructions = role.get("developer_instructions")
    if not isinstance(instructions, str) or not instructions.strip():
        raise StronkPiError(f"Codex role missing developer_instructions: {path}")
    raw_description = role.get("description")
    description = (
        raw_description.strip()
        if isinstance(raw_description, str) and raw_description.strip()
        else extract_role_description(instructions, raw_name)
    )
    lines = [
        "# Imported from a local Codex role definition by stronkpi-setup.",
        "# Pi model selection stays in the Stronk Pi role manifest and local overlay.",
        f"name = {toml_quote(raw_name)}",
        f"description = {toml_quote(description)}",
        f"{MANAGED_MARKER}",
        IMPORTED_CODEX_ROLE_MARKER,
    ]
    for source_key, target_key in (
        ("model", "codex_model"),
        ("model_reasoning_effort", "codex_model_reasoning_effort"),
        ("model_reasoning_summary", "codex_model_reasoning_summary"),
    ):
        value = role.get(source_key)
        if isinstance(value, str) and value.strip():
            lines.append(f"{target_key} = {toml_quote(value.strip())}")
    lines.append(f"developer_instructions = {toml_quote(instructions.strip())}")
    return raw_name, "\n".join(lines) + "\n"


def import_codex_roles(
    *,
    source: str | None = None,
    root: Path | None = None,
    dry_run: bool = False,
    refresh: bool = True,
) -> dict[str, Any]:
    target_root = root or state_root()
    source_dir = discover_codex_role_dir(source)
    source_files = codex_role_files(source_dir)
    outputs: dict[Path, str] = {}
    role_names: list[str] = []
    target_dir = target_root / "config" / "role-templates"
    for source_file in source_files:
        role_name, content = normalized_imported_role(source_file)
        role_names.append(role_name)
        outputs[target_dir / f"{role_name}.toml"] = content
    if len(set(role_names)) != len(role_names):
        raise StronkPiError("duplicate Codex role names")

    bootstrap_changes: list[str] = []
    if not dry_run:
        bootstrap = install_bundle_defaults(root=target_root, dry_run=False)
        bootstrap_changes = list(bootstrap["changed"])

    changed: list[str] = []
    for path, content in sorted(outputs.items()):
        if write_managed_text(path, content, dry_run=dry_run):
            changed.append(str(path))

    generated_changed: list[str] = []
    generated_dir = target_root / "agent" / "agents"
    if refresh:
        if dry_run:
            generated_changed = [str(generated_dir / f"{name}.md") for name in sorted(role_names)]
        else:
            generated_changed = [str(path) for path in generate_pi_agents(target_root, dry_run=False)]

    return {
        "ok": True,
        "sourceDir": str(source_dir),
        "stateRoot": str(target_root),
        "targetTemplatesDir": str(target_dir),
        "generatedAgentsDir": str(generated_dir),
        "importedRoles": sorted(role_names),
        "importedRoleCount": len(role_names),
        "bootstrapChanged": bootstrap_changes,
        "changed": changed,
        "generatedChanged": generated_changed,
        "changedCount": len(changed) + len(generated_changed),
        "dryRun": dry_run,
        "refreshed": refresh,
    }


def load_runtime_role_config(root: Path) -> tuple[Path, Path | None, dict[str, Any], list[Path], Path]:
    manifest_path = root / "config" / "roles.toml"
    local_manifest_path = root / "config" / "roles.local.toml"
    manifest = load_toml_document(manifest_path)
    local_manifest = load_toml_document(local_manifest_path) if local_manifest_path.exists() else {}

    paths = manifest.get("paths")
    pi_cfg = manifest.get("pi")
    if not isinstance(paths, dict) or not isinstance(pi_cfg, dict):
        raise StronkPiError("role manifest requires [paths] and [pi] tables")

    merged_pi = dict(pi_cfg)
    if local_manifest:
        local_pi = local_manifest.get("pi")
        if local_pi is not None:
            if not isinstance(local_pi, dict):
                raise StronkPiError("local role overlay [pi] must be a table")
            merged_pi.update(local_pi)

    role_dirs = [resolve_manifest_relative(manifest_path, str(paths.get("codex_roles_dir") or ""), root)]
    local_paths = local_manifest.get("paths") if local_manifest else None
    if local_paths is not None:
        if not isinstance(local_paths, dict):
            raise StronkPiError("local role overlay [paths] must be a table")
        local_dir = local_paths.get("codex_roles_dir")
        if isinstance(local_dir, str) and local_dir.strip():
            role_dirs.append(resolve_manifest_relative(local_manifest_path, local_dir, root))
        extra_dirs = local_paths.get("extra_codex_roles_dirs")
        if extra_dirs is not None:
            if not isinstance(extra_dirs, list) or not all(isinstance(item, str) for item in extra_dirs):
                raise StronkPiError("local role overlay paths.extra_codex_roles_dirs must be a string list")
            role_dirs.extend(resolve_manifest_relative(local_manifest_path, item, root) for item in extra_dirs)

    generated_raw = str(paths.get("pi_agents_dir") or root / "agent" / "agents")
    generated_dir = resolve_manifest_relative(manifest_path, generated_raw, root)
    return manifest_path, local_manifest_path if local_manifest else None, merged_pi, role_dirs, generated_dir


def string_list_config(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise StronkPiError(f"{label} must be a string list")
    return list(value)


def tools_for_role(role_name: str, pi_cfg: dict[str, Any]) -> list[str]:
    read_tools = string_list_config(pi_cfg.get("read_tools") or ["read", "grep", "find", "ls"], "pi.read_tools")
    write_tools = string_list_config(pi_cfg.get("write_tools") or read_tools, "pi.write_tools")
    write_roles = set(string_list_config(pi_cfg.get("write_roles") or [], "pi.write_roles"))
    return write_tools if role_name in write_roles else read_tools


def role_extensions(pi_cfg: dict[str, Any], root: Path) -> list[str]:
    extensions = string_list_config(pi_cfg.get("extensions") or [], "pi.extensions")
    resolved: list[str] = []
    for item in extensions:
        if item == "stronk-pi-intercom":
            resolved.append(str(state_intercom_bridge_path(root, "stronk-pi-intercom")))
        elif item == "~/.stronk-pi" or item.startswith("~/.stronk-pi/"):
            resolved.append(str(expand_runtime_path(item, root)))
        else:
            resolved.append(item)
    return resolved


def render_pi_role(role_path: Path, role: dict[str, Any], pi_cfg: dict[str, Any], root: Path) -> str:
    name = role_template_name(role_path)
    description = str(role.get("description") or name.replace("-", " ")).strip()
    instructions = str(role.get("developer_instructions") or "").strip()
    if not instructions:
        raise StronkPiError(f"role template missing developer_instructions: {role_path}")
    tools = ", ".join(tools_for_role(name, pi_cfg))
    extensions = role_extensions(pi_cfg, root)
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        f"tools: {tools}",
        f"systemPromptMode: {pi_cfg.get('system_prompt_mode', 'replace')}",
        f"inheritProjectContext: {str(bool(pi_cfg.get('inherit_project_context', True))).lower()}",
        f"inheritSkills: {str(bool(pi_cfg.get('inherit_skills', False))).lower()}",
        f"defaultContext: {pi_cfg.get('default_context', 'fresh')}",
    ]
    if extensions:
        lines.append("extensions: " + ", ".join(extensions))
    model = role.get("model")
    if name == "vision":
        model = pi_cfg.get("vision_model") or model
    if isinstance(model, str) and model:
        lines.append(f"model: {model}")
    lines.append("---")
    source_hash = sha256_file(role_path)
    return (
        "\n".join(lines)
        + "\n\n"
        + f"<!-- Generated at runtime by stronkpi-setup from public role template {role_path.name}; source-sha256={source_hash}. -->\n\n"
        + f"<!-- {MANAGED_MARKER} -->\n\n"
        + f"You are the Pi adapter for the Stronk role `{name}`.\n\n"
        + "Runtime policy:\n"
        + "- This file is generated runtime output under the Stronk Pi state root; do not track it as source.\n"
        + "- Follow the active Stronk Pi role manifest and local overlay supplied by the harness.\n"
        + "- Read-only roles must not edit files or run mutating commands.\n"
        + "- Write-capable roles may mutate only when the operator task and guard policy explicitly allow it.\n\n"
        + "Role instructions:\n\n"
        + instructions
        + "\n"
    )


def role_files_from_dirs(role_dirs: list[Path]) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for directory in role_dirs:
        if not directory.is_dir():
            raise StronkPiError(f"role template directory missing: {directory}")
        for path in sorted(directory.glob("*.toml")):
            name = role_template_name(path)
            files[name] = path
    if not files:
        raise StronkPiError("no runtime role templates found")
    return files


def generate_pi_agents(root: Path, *, dry_run: bool) -> list[Path]:
    _manifest, _local, pi_cfg, role_dirs, generated_dir = load_runtime_role_config(root)
    outputs: dict[Path, str] = {}
    for name, role_path in role_files_from_dirs(role_dirs).items():
        outputs[generated_dir / f"{name}.md"] = render_pi_role(role_path, load_toml_document(role_path), pi_cfg, root)
    changed: list[Path] = []
    for path, content in sorted(outputs.items()):
        if write_managed_text(path, content, dry_run=dry_run):
            changed.append(path)
    return changed


def ensure_state_pi_config(root: Path, *, web_search_content: str, dry_run: bool) -> list[Path]:
    target = state_web_search_config_path(root)
    if not dry_run:
        ensure_private_dir(target.parent)
    changed: list[Path] = []
    if write_private_runtime_text(target, web_search_content, dry_run=dry_run):
        changed.append(target)
    return changed


def install_bundle_defaults(*, root: Path | None = None, dry_run: bool = False) -> dict[str, Any]:
    target_root = root or state_root()
    changes: list[str] = []
    if not dry_run:
        ensure_state_root_layout(target_root)
    for backup_path in migrate_legacy_managed_symlinks(target_root, dry_run=dry_run):
        changes.append(str(backup_path))
    defaults_path = target_root / "config" / "defaults.toml"
    roles_path = target_root / "config" / "roles.toml"
    if write_managed_text(defaults_path, defaults_template(target_root), dry_run=dry_run):
        changes.append(str(defaults_path))
    if write_managed_text(roles_path, role_manifest_template(target_root), dry_run=dry_run):
        changes.append(str(roles_path))
    for path in install_role_templates(target_root, dry_run=dry_run):
        changes.append(str(path))
    web_search_content = (setup_root() / "config" / "pi" / "web-search.json").read_text(encoding="utf-8")
    agent_files = {
        target_root / "agent" / "AGENTS.md": (setup_root() / "config" / "pi" / "agent" / "AGENTS.md").read_text(encoding="utf-8"),
        target_root / "agent" / "models.json": (setup_root() / "config" / "pi" / "agent" / "models.json").read_text(encoding="utf-8"),
        target_root / "agent" / "settings.json": (setup_root() / "config" / "pi" / "agent" / "settings.base.json").read_text(encoding="utf-8"),
    }
    for path, content in agent_files.items():
        if write_managed_text(path, content, dry_run=dry_run, require_marker=False):
            changes.append(str(path))
    for path in ensure_state_pi_config(target_root, web_search_content=web_search_content, dry_run=dry_run):
        changes.append(str(path))
    if dry_run and not roles_path.exists():
        for source in public_role_templates():
            changes.append(str(target_root / "agent" / "agents" / f"{source.stem}.md"))
    else:
        for path in generate_pi_agents(target_root, dry_run=dry_run):
            changes.append(str(path))
    return {
        "stateRoot": str(target_root),
        "roleManifest": str(roles_path),
        "localRoleManifest": str(target_root / "config" / "roles.local.toml"),
        "generatedAgentsDir": str(target_root / "agent" / "agents"),
        "changed": changes,
        "dryRun": dry_run,
    }


def private_home_cleanup_file_action(root: Path, obsolete_home: Path, path: Path, info: os.stat_result) -> dict[str, str]:
    if info.st_nlink > 1:
        raise StronkPiError(f"obsolete private home file has multiple hardlinks: {path}")
    relative = path.relative_to(obsolete_home)
    if relative == Path(".pi") / "web-search.json":
        return {
            "action": "migrate",
            "source": str(path),
            "target": str(state_web_search_config_path(root)),
        }
    parts = relative.parts
    if len(parts) >= 3 and parts[0] in LEGACY_PRIVATE_HOME_AGENT_DIRS and parts[1] == "log":
        legacy_namespace = parts[0].lstrip(".")
        return {
            "action": "migrate",
            "source": str(path),
            "target": str(state_log_root(root) / "legacy-private-home" / legacy_namespace / Path(*parts[2:])),
        }
    if len(parts) >= 3 and parts[0] in LEGACY_PRIVATE_HOME_AGENT_DIRS and parts[1] == "sessions":
        legacy_namespace = parts[0].lstrip(".")
        return {
            "action": "migrate",
            "source": str(path),
            "target": str(state_session_dir(root) / "legacy-private-home" / legacy_namespace / Path(*parts[2:])),
        }
    if private_home_cache_like_path(relative):
        return {"action": "delete", "source": str(path)}
    raise StronkPiError(f"obsolete private home contains unknown non-cache file: {path}")


def private_home_cache_like_path(relative: Path) -> bool:
    parts = relative.parts
    if not parts:
        return False
    if parts[0] in {".npm", ".cache"}:
        return True
    if len(parts) >= 2 and parts[0] == "Library" and parts[1] in {"Caches", "Logs"}:
        return True
    if len(parts) >= 2 and parts[0] == ".pi" and parts[1] in {"cache", "logs", "tmp"}:
        return True
    if len(parts) >= 2 and parts[0] in LEGACY_PRIVATE_HOME_AGENT_DIRS and parts[1] in {"cache", "tmp"}:
        return True
    return False


def plan_private_home_cleanup(root: Path) -> dict[str, Any]:
    obsolete_home = root / "home"
    result: dict[str, Any] = {
        "ok": True,
        "obsoleteHome": str(obsolete_home),
        "exists": False,
        "actions": [],
        "directories": [],
    }
    try:
        home_info = obsolete_home.lstat()
    except FileNotFoundError:
        return result
    result["exists"] = True
    if stat.S_ISLNK(home_info.st_mode):
        raise StronkPiError(f"obsolete private home must not be a symlink: {obsolete_home}")
    if not stat.S_ISDIR(home_info.st_mode):
        raise StronkPiError(f"obsolete private home is not a directory: {obsolete_home}")

    actions: list[dict[str, str]] = []
    directories: list[Path] = []

    def scan(path: Path) -> None:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            raise StronkPiError(f"obsolete private home contains symlink: {path}")
        if stat.S_ISDIR(info.st_mode):
            for child in sorted(path.iterdir(), key=lambda item: item.name):
                scan(child)
            directories.append(path)
            return
        if stat.S_ISREG(info.st_mode):
            actions.append(private_home_cleanup_file_action(root, obsolete_home, path, info))
            return
        raise StronkPiError(f"obsolete private home contains unsupported file type: {path}")

    scan(obsolete_home)
    result["actions"] = actions
    result["directories"] = [str(path) for path in directories]
    return result


def apply_private_home_cleanup(plan: dict[str, Any]) -> None:
    for action in plan["actions"]:
        source = Path(action["source"])
        if action["action"] == "migrate":
            target = Path(action["target"])
            ensure_private_dir(target.parent)
            if target.exists():
                if target.is_symlink() or not target.is_file():
                    raise StronkPiError(f"cleanup target is not a safe regular file: {target}")
                if source.read_bytes() != target.read_bytes():
                    raise StronkPiError(f"cleanup target already exists with different content: {target}")
                source.unlink()
            else:
                source.replace(target)
                os.chmod(target, 0o600)
        elif action["action"] == "delete":
            source.unlink()
        else:
            raise StronkPiError(f"unknown cleanup action: {action['action']}")
    directories = sorted((Path(path) for path in plan["directories"]), key=lambda item: len(item.parts), reverse=True)
    for directory in directories:
        try:
            directory.rmdir()
        except FileNotFoundError:
            continue


def cleanup_private_home(root: Path, *, dry_run: bool) -> dict[str, Any]:
    plan = plan_private_home_cleanup(root)
    plan["dryRun"] = dry_run
    if not dry_run and plan["exists"]:
        apply_private_home_cleanup(plan)
        plan["removed"] = not (root / "home").exists()
    else:
        plan["removed"] = False
    return plan


def inspect_bundle_status(root: Path | None = None) -> dict[str, Any]:
    target_root = root or state_root()
    config_root = target_root / "config"
    role_manifest = config_root / "roles.toml"
    local_manifest = config_root / "roles.local.toml"
    template_dir = config_root / "role-templates"
    generated_dir = target_root / "agent" / "agents"
    plugin_path = target_root / DEFAULT_PLUGIN_RELATIVE
    runtime = target_root / "pi-fork-runtime" / "node_modules" / ".bin" / "pi"
    trust_pin = target_root / "pi-fork-trust.json"
    installed_templates = sorted(template_dir.glob("*.toml")) if template_dir.is_dir() else []
    generated_agents = sorted(generated_dir.glob("*.md")) if generated_dir.is_dir() else []
    return {
        "stateRoot": str(target_root),
        "config": {
            "defaults": str(config_root / "defaults.toml"),
            "defaultsExists": (config_root / "defaults.toml").is_file(),
            "schemaVersion": CONFIG_SCHEMA_VERSION,
        },
        "harness": {
            "source": str(setup_root() / "bin" / "stronkpi"),
            "exists": (setup_root() / "bin" / "stronkpi").is_file(),
        },
        "roles": {
            "manifest": str(role_manifest),
            "manifestExists": role_manifest.is_file(),
            "localManifest": str(local_manifest),
            "localManifestExists": local_manifest.is_file(),
            "templatesDir": str(template_dir),
            "templateCount": len(installed_templates),
            "generatedAgentsDir": str(generated_dir),
            "generatedAgentCount": len(generated_agents),
        },
        "plugin": {
            "expectedPath": str(plugin_path),
            "installed": plugin_path.is_file(),
        },
        "runtime": {
            "trustPin": str(trust_pin),
            "trustPinExists": trust_pin.is_file(),
            "piBinary": str(runtime),
            "piBinaryExists": runtime.is_file(),
        },
    }


def static_http_url_check(value: str, label: str) -> None:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise StronkPiError(f"{label} must be an http(s) URL")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise StronkPiError(f"{label} URL has no host")
    if host in BLOCKED_WEB_HOSTS or any(host.endswith(suffix) for suffix in BLOCKED_WEB_SUFFIXES):
        raise StronkPiError(f"{label} private/local host denied: {host}")
    literal = parse_ip_literal(host)
    if literal is not None:
        assert_public_ip(literal, label)


def string_has_secret(value: str) -> bool:
    return any(pattern.search(value) for pattern in SECRET_VALUE_PATTERNS)


def contains_personal_path(value: str) -> bool:
    text = str(value)
    home = str(Path.home())
    if home not in {"", "/"} and home in text:
        return True
    return PERSONAL_PATH_RE.search(text) is not None


def load_mcp_tools(path: Path) -> list[str]:
    tools: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if not MCP_SERVER_NAME_RE.fullmatch(line):
            raise StronkPiError(f"invalid MCP tool name at {path}:{line_number}: {line}")
        tools.append(line)
    return tools


def validate_mcp_tools_path(path: Path) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise StronkPiError(f"MCP tools allowlist missing: {path}") from exc
    if stat.S_ISLNK(info.st_mode):
        raise StronkPiError(f"MCP tools allowlist must not be a symlink: {path}")
    if not stat.S_ISREG(info.st_mode):
        raise StronkPiError(f"MCP tools allowlist must be a regular file: {path}")
    if info.st_uid != os.getuid():
        raise StronkPiError(f"MCP tools allowlist must be owned by the current user: {path}")
    if info.st_mode & stat.S_IWGRP:
        raise StronkPiError(f"MCP tools allowlist must not be group-writable: {path}")
    if info.st_mode & stat.S_IWOTH:
        raise StronkPiError(f"MCP tools allowlist must not be world-writable: {path}")


def validate_mcp_registry(
    path: Path,
    *,
    tools_path: Path | None = None,
    allow_missing: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "resolvedPath": None,
        "symlink": False,
        "ok": False,
        "serverCount": 0,
        "servers": [],
        "selectedTools": [],
        "env": {},
        "warnings": [],
        "errors": [],
    }
    errors = result["errors"]
    warnings = result["warnings"]

    if not path.exists():
        message = f"MCP registry missing: {path}"
        if allow_missing:
            warnings.append(message)
            result["ok"] = True
            return result
        errors.append(message)
        return result
    registry_file = path
    if path.is_symlink():
        result["symlink"] = True
        registry_file = path.resolve()
        result["resolvedPath"] = str(registry_file)
    if not registry_file.is_file():
        errors.append(f"MCP registry is not a regular file: {path}")
        return result
    stat_result = registry_file.stat()
    if stat_result.st_uid != os.getuid():
        errors.append(f"MCP registry is not owned by the current user: {path}")
    mode = stat_result.st_mode
    if mode & stat.S_IWOTH or mode & stat.S_IWGRP:
        errors.append(f"MCP registry must not be group/world writable: {path}")

    try:
        data = load_mcp_registry_toml(registry_file)
    except (OSError, StronkPiError) as exc:
        errors.append(str(exc))
        return result

    if data.get("version") != 1:
        errors.append("MCP registry version must be 1")
    servers = data.get("servers")
    if not isinstance(servers, dict) or not servers:
        errors.append("MCP registry must define at least one [servers.<name>] table")
        return result

    selected: list[str] = []
    if tools_path is None:
        default_tools = Path.cwd() / ".mcp-tools"
        tools_path = default_tools if default_tools.exists() else None
    if tools_path is not None:
        try:
            validate_mcp_tools_path(tools_path)
            selected = load_mcp_tools(tools_path)
            result["selectedTools"] = selected
        except (OSError, StronkPiError) as exc:
            errors.append(str(exc))

    selected_set = set(selected)
    server_names: list[str] = []
    env_status: dict[str, str] = {}
    for name, server in sorted(servers.items()):
        if not isinstance(name, str) or not MCP_SERVER_NAME_RE.fullmatch(name):
            errors.append(f"invalid MCP server name: {name}")
            continue
        server_names.append(name)
        if not isinstance(server, dict):
            errors.append(f"MCP server {name} must be a table")
            continue
        command = server.get("command")
        if not isinstance(command, str) or not command.strip():
            errors.append(f"MCP server {name} command must be a non-empty string")
        elif "/" not in command and shutil.which(command) is None:
            errors.append(f"MCP server {name} command is not on PATH: {command}")
        elif contains_personal_path(command):
            errors.append(f"MCP server {name} command contains a personal path")

        args = server.get("args", [])
        if args is None:
            args = []
        if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
            errors.append(f"MCP server {name} args must be a list of strings")
            args = []
        for arg in args:
            if contains_personal_path(arg):
                errors.append(f"MCP server {name} arg contains a personal path")
            if string_has_secret(arg):
                errors.append(f"MCP server {name} arg contains a secret-like value")
            if "://" in arg:
                try:
                    static_http_url_check(arg, f"MCP server {name} URL")
                except StronkPiError as exc:
                    errors.append(str(exc))
            try:
                fail_if_floating_mcp_arg(f"MCP server {name} arg", arg)
            except StronkPiError as exc:
                errors.append(str(exc))

        env_vars = server.get("env_vars", [])
        if env_vars is None:
            env_vars = []
        if not isinstance(env_vars, list) or not all(isinstance(item, str) for item in env_vars):
            errors.append(f"MCP server {name} env_vars must be a list of strings")
            env_vars = []
        for env_name in env_vars:
            if not ENV_NAME_RE.fullmatch(env_name):
                errors.append(f"MCP server {name} env var name is invalid: {env_name}")
                continue
            status = "set" if os.environ.get(env_name) else "missing"
            env_status[f"{name}.{env_name}"] = status
            if status == "missing" and name in selected_set:
                errors.append(f"MCP server {name} selected env var is missing: {env_name}")
            elif status == "missing":
                warnings.append(f"MCP server {name} env var is missing: {env_name}")

        env = server.get("env", {})
        if env is None:
            env = {}
        if not isinstance(env, dict):
            errors.append(f"MCP server {name} env must be a table")
            env = {}
        for key, value in env.items():
            if not isinstance(key, str) or not ENV_NAME_RE.fullmatch(key):
                errors.append(f"MCP server {name} env key is invalid: {key}")
            if SECRET_KEY_PATTERN.search(str(key)):
                errors.append(f"MCP server {name} env must not store secret-like key {key}; use env_vars")
            if isinstance(value, str) and string_has_secret(value):
                errors.append(f"MCP server {name} env contains a secret-like value")

        timeout = server.get("startup_timeout_sec")
        if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
            errors.append(f"MCP server {name} startup_timeout_sec must be a positive integer")

    for selected_name in selected:
        if selected_name not in servers:
            errors.append(f"MCP selected tool is not in registry: {selected_name}")

    result["serverCount"] = len(server_names)
    result["servers"] = server_names
    result["env"] = env_status
    result["ok"] = not errors
    return result


def unique_ordered(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def default_mcp_tools_path(cwd: Path) -> Path | None:
    candidate = cwd / ".mcp-tools"
    return candidate if candidate.exists() else None


def find_project_mcp_configs(cwd: Path) -> list[Path]:
    return [cwd / relative for relative in PROJECT_MCP_BYPASS_CONFIG_RELATIVES if (cwd / relative).exists()]


def project_generated_mcp_config_path(cwd: Path, root: Path) -> Path:
    return cwd.resolve(strict=False) / PROJECT_GENERATED_MCP_CONFIG_RELATIVE


def selected_mcp_tools_for_runtime(cwd: Path, tools_path: Path | None = None) -> tuple[Path | None, list[str]]:
    selected_path = tools_path or default_mcp_tools_path(cwd)
    if selected_path is None:
        return None, []
    validate_mcp_tools_path(selected_path)
    return selected_path, unique_ordered(load_mcp_tools(selected_path))


def write_generated_mcp_config(path: Path, content: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() and path.is_file() else None
    if existing == content:
        os.chmod(path, 0o600)
        return False
    if path.exists():
        if path.is_symlink():
            raise StronkPiError(f"generated MCP config must not be a symlink: {path}")
        if not path.is_file():
            raise StronkPiError(f"generated MCP config path is not a regular file: {path}")
    ensure_private_dir(path.parent)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(tmp, 0o600)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass
        raise
    return True


def mcp_registry_file_for_read(path: Path) -> Path:
    return path.resolve() if path.exists() and path.is_symlink() else path


def build_mcp_adapter_config(registry_path: Path, selected_tools: list[str]) -> dict[str, Any]:
    registry = load_mcp_registry_toml(mcp_registry_file_for_read(registry_path))
    servers = registry.get("servers")
    if not isinstance(servers, dict):
        raise StronkPiError("MCP registry must define [servers]")
    mcp_servers: dict[str, dict[str, Any]] = {}
    for name in unique_ordered(selected_tools):
        server = servers.get(name)
        if not isinstance(server, dict):
            raise StronkPiError(f"MCP selected tool is not in registry: {name}")
        entry: dict[str, Any] = {
            "command": str(server.get("command") or ""),
            "args": list(server.get("args") or []),
            "lifecycle": "lazy",
        }
        env: dict[str, str] = {}
        raw_env = server.get("env", {})
        if isinstance(raw_env, dict):
            env.update({str(key): str(value) for key, value in raw_env.items()})
        for env_name in server.get("env_vars") or []:
            env[str(env_name)] = "${" + str(env_name) + "}"
        if env:
            entry["env"] = env
        mcp_servers[name] = entry
    return {
        "settings": {
            "toolPrefix": "server",
            "directTools": False,
            "idleTimeout": 10,
        },
        "mcpServers": mcp_servers,
    }


def validate_package_pin_value(name: str, version: str) -> None:
    """Validate a resolved runtime package pin is concrete and syntactically safe.

    Default pins are trusted constants, but ``runtime_package_pin`` also accepts
    overrides from ``defaults.toml``; a malicious defaults file could otherwise redirect
    runtime discovery to a floating version or an arbitrary package name.
    """
    if not PACKAGE_PIN_NAME_RE.fullmatch(name):
        raise StronkPiError(f"runtime package pin has invalid name: {name!r}")
    if not PACKAGE_PIN_VERSION_RE.fullmatch(version):
        raise StronkPiError(f"runtime package pin has invalid version: {version!r}")
    if FLOATING_VERSION_RE.search(version):
        raise StronkPiError(f"runtime package pin must be pinned, not floating: {name}@{version}")


def runtime_package_pin(defaults: dict[str, Any], key: str) -> tuple[str, str]:
    fallback = DEFAULT_PACKAGE_PINS.get(key)
    if fallback is None:
        raise StronkPiError(f"unknown runtime package pin: {key}")
    pins = defaults.get("package_pins")
    if not isinstance(pins, dict):
        result = fallback
    else:
        package = pins.get(key)
        if not isinstance(package, dict):
            result = fallback
        else:
            name = package.get("name")
            version = package.get("version")
            result = (
                name if isinstance(name, str) and name.strip() else fallback[0],
                version if isinstance(version, str) and version.strip() else fallback[1],
            )
    validate_package_pin_value(*result)
    return result


def mcp_adapter_pin(defaults: dict[str, Any]) -> tuple[str, str]:
    return runtime_package_pin(defaults, "mcp_adapter")


def runtime_package_candidate_paths(root: Path, name: str, version: str) -> list[Path]:
    return [
        root / "agent" / "npm" / "node_modules" / name,
        root / "artifacts" / f"{name}-{version}" / "package",
    ]


def subagents_parent_skill_name(version: str) -> str:
    if version == SUBAGENTS_LEGACY_PARENT_SKILL_VERSION:
        return SUBAGENTS_LEGACY_PARENT_SKILL
    return SUBAGENTS_PARENT_SKILL


def package_archive_required_members(name: str, version: str) -> tuple[str, ...]:
    members = PACKAGE_ARCHIVE_REQUIRED_MEMBERS.get(name, ())
    if name != "stronk-pi-subagents":
        return members
    skill_name = subagents_parent_skill_name(version)
    return (*members, f"package/skills/{skill_name}/SKILL.md")


def runtime_package_required_paths(name: str, version: str) -> tuple[str, ...]:
    paths = RUNTIME_PACKAGE_REQUIRED_PATHS.get(name, ())
    if name != "stronk-pi-subagents":
        return paths
    skill_name = subagents_parent_skill_name(version)
    return (*paths, f"skills/{skill_name}/SKILL.md")


def matching_package_root(path: Path, *, name: str, version: str) -> bool:
    package_json = path / "package.json"
    if not package_json.is_file():
        return False
    try:
        package_data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if package_data.get("name") != name or package_data.get("version") != version:
        return False
    for relative in runtime_package_required_paths(name, version):
        if not (path / relative).is_file():
            return False
    return True


def resolve_mcp_adapter_package(root: Path, defaults: dict[str, Any]) -> tuple[Path, bool]:
    name, version = mcp_adapter_pin(defaults)
    candidates = runtime_package_candidate_paths(root, name, version)
    for candidate in candidates:
        if matching_package_root(candidate, name=name, version=version):
            return candidate, True
    return candidates[0], False


def runtime_package_status(root: Path, defaults: dict[str, Any], key: str) -> dict[str, Any]:
    name, version = runtime_package_pin(defaults, key)
    candidates = runtime_package_candidate_paths(root, name, version)
    package_path = candidates[0]
    installed = False
    for candidate in candidates:
        if matching_package_root(candidate, name=name, version=version):
            package_path = candidate
            installed = True
            break
    return {
        "key": key,
        "packageName": name,
        "packageVersion": version,
        "packagePath": str(package_path),
        "installed": installed,
    }


def runtime_symlink_matches(link: Path, target: Path) -> bool:
    if not link.is_symlink():
        return False
    try:
        return link.resolve(strict=True) == target.resolve(strict=True)
    except FileNotFoundError:
        return False


def ensure_runtime_symlink(link: Path, target: Path, label: str) -> bool:
    ensure_private_dir(link.parent)
    if link.is_symlink():
        try:
            if runtime_symlink_matches(link, target):
                return False
        except FileNotFoundError:
            pass
        link.unlink()
    elif link.exists():
        raise StronkPiError(f"{label} path already exists and is not a managed symlink: {link}")
    link.symlink_to(target, target_is_directory=target.is_dir())
    return True


def inspect_mcp_adapter_runtime(root: Path, *, cwd: Path | None = None) -> dict[str, Any]:
    launch_cwd = cwd or Path.cwd()
    defaults = load_runtime_defaults(root)
    name, version = mcp_adapter_pin(defaults)
    adapter_path, adapter_installed = resolve_mcp_adapter_package(root, defaults)
    tools_path, selected = selected_mcp_tools_for_runtime(launch_cwd)
    project_configs = find_project_mcp_configs(launch_cwd)
    config_path = project_generated_mcp_config_path(launch_cwd, root)
    return {
        "configured": bool(selected),
        "enabled": bool(selected) and adapter_installed and not project_configs,
        "packageName": name,
        "packageVersion": version,
        "adapterPath": str(adapter_path),
        "adapterInstalled": adapter_installed,
        "configPath": str(config_path),
        "registryPath": str(default_mcp_registry_path()),
        "toolsPath": str(tools_path) if tools_path else None,
        "selectedTools": selected,
        "projectConfigFiles": [str(path) for path in project_configs],
    }


def prepare_mcp_adapter_runtime(root: Path, *, cwd: Path | None = None) -> dict[str, Any]:
    launch_cwd = cwd or Path.cwd()
    tools_path, selected = selected_mcp_tools_for_runtime(launch_cwd)
    defaults = load_runtime_defaults(root)
    adapter_path, adapter_installed = resolve_mcp_adapter_package(root, defaults)
    status = inspect_mcp_adapter_runtime(root, cwd=launch_cwd)
    if not selected:
        return status
    project_configs = find_project_mcp_configs(launch_cwd)
    if project_configs:
        paths = ", ".join(str(path) for path in project_configs)
        raise StronkPiError(
            "project MCP config file(s) would bypass the Stronk selected-server boundary: "
            f"{paths}; move selected server names to .mcp-tools and definitions to the MCP registry"
        )
    registry_path = default_mcp_registry_path()
    mcp = validate_mcp_registry(registry_path, tools_path=tools_path, allow_missing=False)
    if not mcp["ok"]:
        raise StronkPiError("MCP registry invalid: " + "; ".join(str(error) for error in mcp["errors"]))
    if not adapter_installed:
        name, version = mcp_adapter_pin(defaults)
        raise StronkPiError(
            f"MCP adapter package missing: expected {name}@{version} at {adapter_path}; "
            "install a verified adapter package before launching with selected MCP servers"
        )
    config = build_mcp_adapter_config(registry_path, selected)
    config_path = project_generated_mcp_config_path(launch_cwd, root)
    if write_generated_mcp_config(config_path, json.dumps(config, indent=2, sort_keys=True) + "\n"):
        status["configChanged"] = True
    else:
        status["configChanged"] = False
    status.update(
        {
            "enabled": True,
            "adapterPath": str(adapter_path),
            "configPath": str(config_path),
            "selectedTools": selected,
        }
    )
    return status


def inspect_subagent_runtime(root: Path) -> dict[str, Any]:
    defaults = load_runtime_defaults(root)
    facade = harness_string(defaults, "subagent_facade", "stronk")
    adapter = harness_string(defaults, "subagent_adapter", "intercom")
    configured = bool(facade) and facade not in {"off", "0"} and adapter == "intercom"
    packages = {
        key: runtime_package_status(root, defaults, key)
        for key in SUBAGENT_RUNTIME_PACKAGE_KEYS
    }
    missing = [item for item in packages.values() if not item["installed"]]
    extension_paths = [
        str(packages[key]["packagePath"])
        for key in SUBAGENT_RUNTIME_PACKAGE_KEYS
        if packages[key]["installed"]
    ]
    intercom_package = packages["intercom"]
    intercom_bridge_path = state_intercom_bridge_path(root, "stronk-pi-intercom")
    intercom_bridge_target = (
        Path(str(intercom_package["packagePath"])) if intercom_package["installed"] else None
    )
    return {
        "configured": configured,
        "enabled": configured and not missing,
        "facade": facade,
        "adapter": adapter,
        "packages": packages,
        "missingPackages": missing,
        "extensionPaths": extension_paths if configured and not missing else [],
        "intercomBridgePath": str(intercom_bridge_path),
        "intercomBridgeTarget": intercom_package["packagePath"] if intercom_package["installed"] else None,
        "intercomBridgeLinked": (
            runtime_symlink_matches(intercom_bridge_path, intercom_bridge_target)
            if intercom_bridge_target is not None
            else False
        ),
    }


def prepare_subagent_runtime(root: Path) -> dict[str, Any]:
    status = inspect_subagent_runtime(root)
    if status["configured"] and not status["enabled"]:
        missing = ", ".join(
            f"{item['packageName']}@{item['packageVersion']} at {item['packagePath']}"
            for item in status["missingPackages"]
        )
        raise StronkPiError(
            "subagent runtime package missing: "
            f"expected {missing}; install the pinned package runtime before launching live Stronk Pi subagents"
        )
    if status["enabled"]:
        intercom_target = Path(str(status["packages"]["intercom"]["packagePath"]))
        bridge_path = Path(str(status["intercomBridgePath"]))
        status["intercomBridgeChanged"] = ensure_runtime_symlink(
            bridge_path,
            intercom_target,
            "stronk-pi-intercom bridge",
        )
        status["intercomBridgeLinked"] = runtime_symlink_matches(bridge_path, intercom_target)
    return status


def check_network_access(url: str) -> dict[str, Any]:
    result: dict[str, Any] = {"url": url, "ok": False, "skipped": False}
    if os.environ.get("STRONKPI_NO_NETWORK") == "1":
        result["skipped"] = True
        result["reason"] = "STRONKPI_NO_NETWORK=1"
        return result
    checked = check_public_http_url(url, "doctor network URL")
    request = urllib.request.Request(checked["url"], method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result["status"] = getattr(response, "status", None)
            result["finalUrl"] = response.geturl()
    except urllib.error.HTTPError as exc:
        if exc.code < 500:
            result["status"] = exc.code
            result["finalUrl"] = exc.geturl()
        else:
            raise StronkPiError(f"network check failed with HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise StronkPiError(f"network check failed: {exc.reason}") from exc
    result["host"] = checked["hostname"]
    result["addresses"] = checked["addresses"]
    result["ok"] = True
    return result


def require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise StronkPiError(f"manifest field {key!r} must be a non-empty string")
    return value.strip()


def require_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value < 0:
        raise StronkPiError(f"manifest field {key!r} must be a non-negative integer")
    return value


def require_iso_utc(data: dict[str, Any], key: str) -> str:
    value = require_string(data, key)
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise StronkPiError(f"manifest field {key!r} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise StronkPiError(f"manifest field {key!r} must be UTC")
    return value


def artifact_path(manifest_path: Path, item: dict[str, Any]) -> Path:
    local_path = item.get("artifactPath")
    url = item.get("artifactUrl")
    if local_path is not None:
        if not isinstance(local_path, str) or not local_path.strip():
            raise StronkPiError("artifactPath must be a non-empty string")
        if local_path.startswith("file:"):
            raise StronkPiError("local file URLs are denied")
        candidate = Path(local_path)
        if candidate.is_absolute():
            raise StronkPiError("local absolute artifact paths are denied")
        resolved = (manifest_path.parent / candidate).resolve()
        fixture_root = (setup_root() / "tests" / "fixtures").resolve()
        if not is_relative_to(resolved, fixture_root):
            raise StronkPiError("relative local artifacts are limited to offline fixtures")
        return resolved
    if url is None:
        raise StronkPiError("artifact must include artifactPath or artifactUrl")
    if os.environ.get("STRONKPI_NO_NETWORK") == "1":
        raise StronkPiError("network artifact download denied by STRONKPI_NO_NETWORK=1")
    if not isinstance(url, str):
        raise StronkPiError("artifactUrl must be a string")
    checked = check_public_http_url(url, "artifact URL")
    if urlparse(checked["url"]).scheme != "https":
        raise StronkPiError("artifact URL must use HTTPS")
    return download_artifact(checked["url"])


def download_artifact(url: str) -> Path:
    request = urllib.request.Request(url, headers={"User-Agent": f"stronkpi-setup/{VERSION}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        final_url = response.geturl()
        checked = check_public_http_url(final_url, "artifact redirect URL")
        if urlparse(checked["url"]).scheme != "https":
            raise StronkPiError("artifact redirect URL must use HTTPS")
        fd, tmp_name = tempfile.mkstemp(prefix="stronkpi-artifact.", suffix=".tgz")
        with os.fdopen(fd, "wb") as handle:
            shutil.copyfileobj(response, handle)
    return Path(tmp_name)


def validate_archive(path: Path, *, expected_name: str, expected_version: str) -> None:
    if not path.is_file():
        raise StronkPiError(f"missing artifact: {path}")
    with tarfile.open(path, "r:gz") as archive:
        package_json: dict[str, Any] | None = None
        member_names: set[str] = set()
        with tempfile.TemporaryDirectory(prefix="stronkpi-archive-check.") as tmp:
            root = Path(tmp).resolve()
            for member in archive.getmembers():
                name = member.name
                if not name or name.startswith("/") or WINDOWS_DRIVE_RE.match(name):
                    raise StronkPiError(f"archive member path denied: {name}")
                parts = Path(name).parts
                if ".." in parts:
                    raise StronkPiError(f"archive member path traversal denied: {name}")
                if member.issym() or member.islnk():
                    raise StronkPiError(f"archive links are denied: {name}")
                if not (member.isfile() or member.isdir()):
                    raise StronkPiError(f"archive special file denied: {name}")
                target = (root / name).resolve()
                if not is_relative_to(target, root):
                    raise StronkPiError(f"archive member escapes extraction root: {name}")
                if member.isfile():
                    member_names.add(name)
                if name == "package/package.json" and member.isfile():
                    handle = archive.extractfile(member)
                    if handle is None:
                        raise StronkPiError("artifact package.json could not be read")
                    try:
                        package_json = json.loads(handle.read(65536).decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise StronkPiError("artifact package.json must be valid JSON") from exc
        if not isinstance(package_json, dict):
            raise StronkPiError("artifact missing package/package.json")
        if package_json.get("name") != expected_name:
            raise StronkPiError(f"artifact package name must be {expected_name}")
        if package_json.get("version") != expected_version:
            raise StronkPiError(f"artifact package version must be {expected_version}")
        missing_members = sorted(set(package_archive_required_members(expected_name, expected_version)) - member_names)
        if missing_members:
            raise StronkPiError(
                f"artifact {expected_name} missing required package content: "
                + ", ".join(missing_members)
            )


def validate_package_pins(package_pins: Any) -> dict[str, Any]:
    if not isinstance(package_pins, dict):
        raise StronkPiError("manifest bundle.packagePins must be an object")
    normalized: dict[str, Any] = {}
    for key in PACKAGE_PIN_KEYS:
        item = package_pins.get(key)
        if not isinstance(item, dict):
            raise StronkPiError(f"manifest bundle.packagePins.{key} must be an object")
        name = item.get("name")
        version = item.get("version")
        if not isinstance(name, str) or not name:
            raise StronkPiError(f"manifest bundle.packagePins.{key}.name must be a non-empty string")
        if not isinstance(version, str) or not version:
            raise StronkPiError(f"manifest bundle.packagePins.{key}.version must be a non-empty string")
        fail_if_floating(f"bundle.packagePins.{key}.version", version)
        normalized[key] = {"name": name, "version": version}
    return normalized


def validate_artifact_identity(
    *,
    name: str,
    version: str,
    source_repo: str,
    immutable_tag: str,
    release_url: str,
    artifact_url: Any,
    attestation: str,
    sha256: str,
    item: dict[str, Any],
) -> None:
    expected = EXPECTED_ARTIFACT_IDENTITIES.get(name)
    if expected is None:
        raise StronkPiError(f"unknown artifact identity: {name}")
    expected_repo = expected["sourceRepo"]
    if source_repo != expected_repo:
        raise StronkPiError(f"artifact {name} sourceRepo must be {expected_repo}")
    expected_tag = f"{expected['tagPrefix']}{version}"
    if immutable_tag != expected_tag:
        raise StronkPiError(f"artifact {name} immutableTag must be {expected_tag}")
    expected_release_url = f"https://github.com/{expected_repo}/releases/tag/{expected_tag}"
    if release_url != expected_release_url:
        raise StronkPiError(f"artifact {name} releaseUrl must be {expected_release_url}")
    expected_asset = f"{expected['assetPrefix']}{version}.tgz"
    if artifact_url is not None:
        expected_artifact_url = f"https://github.com/{expected_repo}/releases/download/{expected_tag}/{expected_asset}"
        if artifact_url != expected_artifact_url:
            raise StronkPiError(f"artifact {name} artifactUrl must be {expected_artifact_url}")
    expected_attestation = f"github-attestation:{expected_repo}/{expected_asset}@sha256:{sha256}"
    if attestation != expected_attestation:
        raise StronkPiError(f"artifact {name} attestation must be {expected_attestation}")
    for field in ARTIFACT_PROVENANCE_METADATA_FIELDS:
        expected_value = expected.get(field)
        if expected_value is None:
            continue
        value = require_string(item, field)
        if value != expected_value:
            raise StronkPiError(f"artifact {name} {field} must be {expected_value}")


def validate_required_artifact_set(artifacts: list[Any]) -> None:
    names: list[str] = []
    for index, raw_item in enumerate(artifacts):
        if not isinstance(raw_item, dict):
            raise StronkPiError(f"artifact {index} must be an object")
        names.append(require_string(raw_item, "name"))
    duplicate_names = sorted({name for name in names if names.count(name) > 1})
    if duplicate_names:
        raise StronkPiError("duplicate artifact identity: " + ", ".join(duplicate_names))
    expected_names = set(EXPECTED_ARTIFACT_IDENTITIES)
    actual_names = set(names)
    missing = sorted(expected_names - actual_names)
    extra = sorted(actual_names - expected_names)
    if missing:
        raise StronkPiError("manifest missing required artifact(s): " + ", ".join(missing))
    if extra:
        raise StronkPiError("manifest includes unsupported artifact(s): " + ", ".join(extra))


def validate_runtime_artifact_pins(pins: dict[str, Any], artifact_versions: dict[str, str]) -> None:
    expected_runtime_artifacts = {
        "subagents": "stronk-pi-subagents",
        "intercom": "stronk-pi-intercom",
    }
    for pin_key, artifact_name in expected_runtime_artifacts.items():
        pin = pins.get(pin_key)
        if not isinstance(pin, dict):
            raise StronkPiError(f"manifest bundle.packagePins.{pin_key} must be an object")
        if pin.get("name") != artifact_name:
            raise StronkPiError(f"manifest bundle.packagePins.{pin_key}.name must be {artifact_name}")
        if pin.get("version") != artifact_versions.get(artifact_name):
            raise StronkPiError(
                f"manifest bundle.packagePins.{pin_key}.version must match {artifact_name} artifact"
            )


def verify_remote_artifact_attestation(
    *,
    path: Path,
    name: str,
    version: str,
    source_repo: str,
    source_commit: str,
    sha256: str,
) -> None:
    expected = EXPECTED_ARTIFACT_IDENTITIES[name]
    signer_workflow = expected.get("signerWorkflow")
    if not signer_workflow:
        raise StronkPiError(f"artifact {name} missing expected signer workflow")
    gh = shutil.which("gh")
    if gh is None:
        raise StronkPiError("gh CLI is required to verify GitHub artifact attestations")
    proc = subprocess.run(
        [
            gh,
            "attestation",
            "verify",
            str(path),
            "--repo",
            source_repo,
            "--source-digest",
            source_commit,
            "--signer-workflow",
            signer_workflow,
            "--format",
            "json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=90,
        check=False,
    )
    if proc.returncode != 0:
        detail = nonempty(proc.stderr) or nonempty(proc.stdout) or "no output"
        raise StronkPiError(f"artifact {name} attestation verification failed: {detail}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise StronkPiError(f"artifact {name} attestation output was not JSON") from exc
    if not isinstance(payload, list) or not payload:
        raise StronkPiError(f"artifact {name} attestation verification returned no attestations")
    expected_asset = f"{expected['assetPrefix']}{version}.tgz"
    for item in payload:
        if not isinstance(item, dict):
            continue
        for subject in attestation_subjects(item):
            if not isinstance(subject, dict):
                continue
            digest = subject.get("digest")
            if (
                subject.get("name") == expected_asset
                and isinstance(digest, dict)
                and digest.get("sha256") == sha256
            ):
                return
    raise StronkPiError(f"artifact {name} attestation subject must match {expected_asset}@sha256:{sha256}")


def attestation_subjects(item: dict[str, Any]) -> list[Any]:
    verification = item.get("verificationResult")
    if isinstance(verification, dict):
        statement = verification.get("statement")
        subjects = statement.get("subject") if isinstance(statement, dict) else None
        if isinstance(subjects, list):
            return subjects

    attestation = item.get("attestation")
    bundle = attestation.get("bundle") if isinstance(attestation, dict) else None
    envelope = bundle.get("dsseEnvelope") if isinstance(bundle, dict) else None
    payload = envelope.get("payload") if isinstance(envelope, dict) else None
    if not isinstance(payload, str):
        return []
    try:
        padded_payload = payload + ("=" * (-len(payload) % 4))
        statement = json.loads(base64.b64decode(padded_payload).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    subjects = statement.get("subject") if isinstance(statement, dict) else None
    return subjects if isinstance(subjects, list) else []


def validate_bundle_contract_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    bundle = manifest.get("bundle")
    if not isinstance(bundle, dict):
        raise StronkPiError("manifest must include a bundle contract")
    if bundle.get("configSchemaVersion") != CONFIG_SCHEMA_VERSION:
        raise StronkPiError(f"manifest bundle.configSchemaVersion must be {CONFIG_SCHEMA_VERSION}")
    if bundle.get("stateRoot") != "~/.stronk-pi":
        raise StronkPiError("manifest bundle.stateRoot must be ~/.stronk-pi")
    expected_paths = {
        "defaultConfigPath": "~/.stronk-pi/config/defaults.toml",
        "defaultRoleManifestPath": "~/.stronk-pi/config/roles.toml",
        "localRoleManifestPath": "~/.stronk-pi/config/roles.local.toml",
        "roleTemplatesPath": "~/.stronk-pi/config/role-templates",
        "generatedAgentsPath": "~/.stronk-pi/agent/agents",
    }
    for key, expected in expected_paths.items():
        if bundle.get(key) != expected:
            raise StronkPiError(f"manifest bundle.{key} must be {expected}")
    harness = bundle.get("harness")
    if not isinstance(harness, dict):
        raise StronkPiError("manifest bundle.harness must be an object")
    if harness.get("command") != "stronkpi" or harness.get("owner") != "stronk-pi":
        raise StronkPiError("manifest bundle.harness must declare stronk-pi-owned stronkpi")
    models = bundle.get("models")
    if not isinstance(models, dict):
        raise StronkPiError("manifest bundle.models must be an object")
    for key in ("default", "vision"):
        value = models.get(key)
        if not isinstance(value, str) or not value:
            raise StronkPiError(f"manifest bundle.models.{key} must be a non-empty string")
    pins = validate_package_pins(bundle.get("packagePins"))
    return {"models": models, "packagePins": pins}


def verify_manifest(manifest_path: Path) -> list[ArtifactResult]:
    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != 1:
        raise StronkPiError("manifest schemaVersion must be 1")
    compatibility = require_string(manifest, "compatibilityVersion")
    fail_if_floating("compatibilityVersion", compatibility)
    bundle_info = validate_bundle_contract_manifest(manifest)
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise StronkPiError("manifest artifacts must be an array")
    validate_required_artifact_set(artifacts)
    results: list[ArtifactResult] = []
    artifact_versions: dict[str, str] = {}
    for index, raw_item in enumerate(artifacts):
        if not isinstance(raw_item, dict):
            raise StronkPiError(f"artifact {index} must be an object")
        name = require_string(raw_item, "name")
        version = require_string(raw_item, "version")
        source_repo = require_string(raw_item, "sourceRepo")
        source_commit = require_string(raw_item, "sourceCommit")
        immutable_tag = require_string(raw_item, "immutableTag")
        release_url = require_string(raw_item, "releaseUrl")
        sha256 = require_string(raw_item, "sha256")
        byte_size = require_int(raw_item, "byteSize")
        workflow_run_id = require_string(raw_item, "workflowRunId")
        attestation = require_string(raw_item, "attestation")
        artifact_compatibility = require_string(raw_item, "compatibilityVersion")
        require_iso_utc(raw_item, "createdAt")
        if "sbom" in raw_item:
            require_string(raw_item, "sbom")
        for label, value in (
            ("name", name),
            ("version", version),
            ("sourceRepo", source_repo),
            ("immutableTag", immutable_tag),
            ("releaseUrl", release_url),
            ("sha256", sha256),
        ):
            fail_if_floating(label, value)
        if not COMMIT_RE.fullmatch(source_commit):
            raise StronkPiError("sourceCommit must be a full 40-character lowercase SHA")
        if not re.fullmatch(r"[0-9a-f]{64}", sha256):
            raise StronkPiError("sha256 must be a lowercase SHA-256 hex digest")
        remote_artifact = raw_item.get("artifactUrl") is not None and raw_item.get("artifactPath") is None
        if remote_artifact and not re.fullmatch(r"\d+", workflow_run_id):
            raise StronkPiError(f"artifact {name} workflowRunId must be a numeric GitHub Actions run id")
        validate_artifact_identity(
            name=name,
            version=version,
            source_repo=source_repo,
            immutable_tag=immutable_tag,
            release_url=release_url,
            artifact_url=raw_item.get("artifactUrl"),
            attestation=attestation,
            sha256=sha256,
            item=raw_item,
        )
        release_check = check_public_http_url(release_url, "release URL")
        if urlparse(release_check["url"]).scheme != "https":
            raise StronkPiError("release URL must use HTTPS")
        if artifact_compatibility != compatibility:
            raise StronkPiError(f"wrong compatibilityVersion for {name}")
        path = artifact_path(manifest_path, raw_item)
        if not path.is_file():
            raise StronkPiError(f"missing artifact: {path}")
        actual_size = path.stat().st_size
        if actual_size != byte_size:
            raise StronkPiError(f"byte size mismatch for {name}: {actual_size} != {byte_size}")
        actual_sha = sha256_file(path)
        if actual_sha != sha256:
            raise StronkPiError(f"checksum mismatch for {name}")
        if remote_artifact:
            verify_remote_artifact_attestation(
                path=path,
                name=name,
                version=version,
                source_repo=source_repo,
                source_commit=source_commit,
                sha256=sha256,
            )
        provenance = raw_item.get("provenance")
        if not isinstance(provenance, dict):
            raise StronkPiError("provenance must be an object")
        for key, expected in (
            ("sourceRepo", source_repo),
            ("sourceCommit", source_commit),
            ("immutableTag", immutable_tag),
            ("workflowRunId", raw_item["workflowRunId"]),
        ):
            if provenance.get(key) != expected:
                raise StronkPiError(f"wrong provenance for {name}: {key}")
        expected_identity = EXPECTED_ARTIFACT_IDENTITIES[name]
        artifact_versions[name] = version
        for key in ARTIFACT_PROVENANCE_METADATA_FIELDS:
            if key not in expected_identity:
                continue
            if provenance.get(key) != expected_identity[key]:
                raise StronkPiError(f"wrong provenance for {name}: {key}")
        validate_archive(path, expected_name=name, expected_version=version)
        results.append(ArtifactResult(name, version, path, actual_sha, actual_size))
    validate_runtime_artifact_pins(bundle_info["packagePins"], artifact_versions)
    return results


def install_artifacts(results: list[ArtifactResult], dry_run: bool) -> None:
    if dry_run:
        return
    root = ensure_private_dir(state_root())
    installs = ensure_private_dir(root / "artifacts")
    for result in results:
        dest = installs / f"{result.name}-{result.version}"
        tmp = Path(tempfile.mkdtemp(prefix=f".{result.name}.", dir=installs))
        try:
            safe_extract_artifact(result.path, tmp)
            replace_artifact_dir(tmp, dest)
        except Exception:
            shutil.rmtree(tmp, ignore_errors=True)
            raise


def safe_extract_artifact(archive_path: Path, dest: Path) -> None:
    root = dest.resolve()
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            name = member.name
            if not name or name.startswith("/") or WINDOWS_DRIVE_RE.match(name):
                raise StronkPiError(f"archive member path denied during install: {name}")
            if ".." in Path(name).parts:
                raise StronkPiError(f"archive member path traversal denied during install: {name}")
            if member.issym() or member.islnk():
                raise StronkPiError(f"archive links are denied during install: {name}")
            if not (member.isfile() or member.isdir()):
                raise StronkPiError(f"archive special file denied during install: {name}")
            target = (root / name).resolve()
            if not is_relative_to(target, root):
                raise StronkPiError(f"archive member escapes extraction root during install: {name}")
        archive.extractall(root, members=members)


def verify_installed_artifacts(results: list[ArtifactResult], root: Path) -> list[dict[str, str]]:
    installed: list[dict[str, str]] = []
    for result in results:
        package_root = root / "artifacts" / f"{result.name}-{result.version}" / "package"
        if not matching_package_root(package_root, name=result.name, version=result.version):
            raise StronkPiError(
                f"installed artifact package root failed validation for {result.name}@{result.version}: "
                f"{package_root}"
            )
        installed.append(
            {
                "name": result.name,
                "version": result.version,
                "packageRoot": str(package_root),
            }
        )
    return installed


def replace_artifact_dir(source: Path, dest: Path) -> None:
    backup: Path | None = None
    if dest.exists():
        if dest.is_symlink() or not dest.is_dir():
            raise StronkPiError(f"artifact install target must be a directory: {dest}")
        backup = dest.with_name(f".{dest.name}.previous.{os.getpid()}")
        shutil.rmtree(backup, ignore_errors=True)
        os.replace(dest, backup)
    try:
        os.replace(source, dest)
    except Exception:
        if backup is not None and backup.exists():
            shutil.rmtree(dest, ignore_errors=True)
            os.replace(backup, dest)
        raise
    else:
        if backup is not None:
            shutil.rmtree(backup, ignore_errors=True)


def cmd_validate(args: argparse.Namespace) -> int:
    root = setup_root()
    required = [
        root / "bin" / "stronkpi",
        root / "bin" / "stronkpi-setup",
        root / "install.sh",
        root / "config" / "defaults.toml",
        root / "lib" / "stronk-pi-guard.py",
        root / "config" / "pi" / "agent" / "AGENTS.md",
        root / "config" / "pi" / "agent" / "models.json",
        root / "config" / "pi" / "agent" / "settings.base.json",
        root / "config" / "pi" / "web-search.json",
        root / "manifests" / "current.json",
        root / "roles" / "stronk" / "roles.toml",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        raise StronkPiError("missing required setup files: " + ", ".join(missing))
    load_toml_document(root / "config" / "defaults.toml")
    load_toml_document(root / "roles" / "stronk" / "roles.toml")
    validate_public_role_templates()
    manifest = load_json(root / "manifests" / "current.json")
    if manifest.get("schemaVersion") != 1:
        raise StronkPiError("manifest schemaVersion must be 1")
    validate_bundle_contract_manifest(manifest)
    for json_path in (
        root / "config" / "pi" / "agent" / "models.json",
        root / "config" / "pi" / "agent" / "settings.base.json",
        root / "config" / "pi" / "web-search.json",
        root / "manifests" / "current.json",
    ):
        load_json(json_path)
    forbidden_bins = [
        root / "bin" / "sp",
        root / "bin" / "pi",
        root / "bin" / "stronk-pi-setup",
    ]
    found = [path.name for path in forbidden_bins if path.exists()]
    if found:
        raise StronkPiError("forbidden compatibility commands present: " + ", ".join(found))
    print("stronkpi-setup validate: ok")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    registry_path = Path(args.mcp_registry).expanduser()
    if not registry_path.is_absolute():
        registry_path = (Path.cwd() / registry_path).resolve()
    tools_path = None
    if args.mcp_tools:
        tools_path = Path(args.mcp_tools).expanduser()
        if not tools_path.is_absolute():
            tools_path = (Path.cwd() / tools_path).resolve()

    dependencies = {
        "python3": {
            "ok": True,
            "path": shutil.which("python3") or sys.executable,
            "version": sys.version.split()[0],
        },
        "curl": {
            "ok": shutil.which("curl") is not None,
            "path": shutil.which("curl"),
            "required": bool(args.check_network),
        },
    }
    errors: list[str] = []
    if args.check_network and not dependencies["curl"]["ok"]:
        errors.append("curl is not on PATH for operator-requested network checks")
    mcp = validate_mcp_registry(
        registry_path,
        tools_path=tools_path,
        allow_missing=args.allow_missing_mcp,
    )
    errors.extend(str(error) for error in mcp.get("errors", []))
    warnings: list[str] = [str(warning) for warning in mcp.get("warnings", [])]

    network: dict[str, Any] = {
        "url": args.network_url,
        "ok": False,
        "skipped": True,
        "reason": "not requested",
    }
    if args.check_network:
        try:
            network = check_network_access(args.network_url)
        except StronkPiError as exc:
            network = {
                "url": args.network_url,
                "ok": False,
                "skipped": False,
                "error": str(exc),
            }
            errors.append(str(exc))

    env_status = {name: ("set" if os.environ.get(name) else "missing") for name in ENV_NAMES}
    bundle_status = inspect_bundle_status()
    payload = {
        "ok": not errors,
        "version": VERSION,
        "setupRoot": str(setup_root()),
        "stateRoot": str(state_root()),
        "noNetwork": os.environ.get("STRONKPI_NO_NETWORK") == "1",
        "bundle": {
            "compatibilityVersion": BUNDLE_CONTRACT_VERSION,
            "configSchemaVersion": CONFIG_SCHEMA_VERSION,
            "manifest": str(setup_root() / "manifests" / "current.json"),
            "setupOwnsHarness": True,
        },
        "harness": bundle_status["harness"],
        "roleConfig": bundle_status["roles"],
        "pluginArtifact": bundle_status["plugin"],
        "runtime": bundle_status["runtime"],
        "dependencies": dependencies,
        "env": env_status,
        "mcpRegistry": mcp,
        "network": network,
        "warnings": warnings,
        "errors": errors,
    }
    if args.json:
        json_out(payload)
    else:
        print("stronkpi-setup doctor: ok" if payload["ok"] else "stronkpi-setup doctor: failed")
        for key, value in payload.items():
            print(f"{key}={redact(value)}")
    return 0 if payload["ok"] else 1


def cmd_update(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser()
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()
    results = verify_manifest(manifest_path)
    bundle = install_bundle_defaults(dry_run=args.dry_run)
    install_artifacts(results, args.dry_run)
    installed = [] if args.dry_run else verify_installed_artifacts(results, state_root())
    mode = "dry-run" if args.dry_run else "installed"
    print(f"stronkpi-setup update: {mode} verified {len(results)} artifact(s)")
    for result in results:
        print(f"- {result.name} {result.version} {result.sha256}")
    for item in installed:
        print(f"- materialized {item['name']} {item['version']} {item['packageRoot']}")
    print(f"stronkpi-setup update: {mode} bundle config {bundle['roleManifest']}")
    print(f"stronkpi-setup update: {mode} generated agents {bundle['generatedAgentsDir']}")
    return 0


def cmd_refresh_config(args: argparse.Namespace) -> int:
    bundle = install_bundle_defaults(dry_run=args.dry_run)
    mode = "dry-run" if args.dry_run else "refreshed"
    payload = {
        "ok": True,
        "mode": mode,
        "stateRoot": bundle["stateRoot"],
        "roleManifest": bundle["roleManifest"],
        "localRoleManifest": bundle["localRoleManifest"],
        "generatedAgentsDir": bundle["generatedAgentsDir"],
        "changed": bundle["changed"],
        "changedCount": len(bundle["changed"]),
        "dryRun": bundle["dryRun"],
    }
    if args.json:
        json_out(payload)
        return 0
    print(f"stronkpi-setup refresh-config: {mode}")
    print(f"state_root={payload['stateRoot']}")
    print(f"role_manifest={payload['roleManifest']}")
    print(f"roles_local={payload['localRoleManifest']}")
    print(f"generated_agents={payload['generatedAgentsDir']}")
    print(f"changed_count={payload['changedCount']}")
    return 0


def cmd_cleanup_private_home(args: argparse.Namespace) -> int:
    payload = cleanup_private_home(state_root(), dry_run=not args.apply)
    if args.json:
        json_out(payload)
        return 0
    mode = "dry-run" if payload["dryRun"] else "applied"
    print(f"stronkpi-setup cleanup-private-home: {mode}")
    print(f"obsolete_home={payload['obsoleteHome']}")
    print(f"exists={str(payload['exists']).lower()}")
    print(f"action_count={len(payload['actions'])}")
    print(f"removed={str(payload['removed']).lower()}")
    return 0


def cmd_import_codex_roles(args: argparse.Namespace) -> int:
    payload = import_codex_roles(
        source=args.source,
        dry_run=args.dry_run,
        refresh=not args.no_refresh,
    )
    mode = "dry-run" if args.dry_run else "imported"
    if args.json:
        json_out(payload)
        return 0
    print(f"stronkpi-setup import-codex-roles: {mode}")
    print(f"source_dir={payload['sourceDir']}")
    print(f"target_templates={payload['targetTemplatesDir']}")
    print(f"generated_agents={payload['generatedAgentsDir']}")
    print(f"imported_role_count={payload['importedRoleCount']}")
    print(f"changed_count={payload['changedCount']}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    root = setup_root()
    guard = root / "lib" / "stronk-pi-guard.py"
    harness = root / "bin" / "stronkpi"
    prefix = Path(args.prefix).expanduser()
    if not prefix.is_absolute():
        raise StronkPiError("--prefix must be absolute")
    bin_dir = prefix / "bin"
    setup_target = bin_dir / "stronkpi-setup"
    harness_target = bin_dir / "stronkpi"
    if args.dry_run:
        print(f"stronkpi-setup install: would install {setup_target}")
        print(f"stronkpi-setup install: would install {harness_target}")
        print("stronkpi-setup install: no compatibility aliases will be created")
        return 0
    setup_script = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import runpy",
            "",
            f"runpy.run_path({str(guard)!r}, run_name='__main__')",
            "",
        ]
    )
    harness_script = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import runpy",
            "",
            f"runpy.run_path({str(harness)!r}, run_name='__main__')",
            "",
        ]
    )
    write_executable_script(setup_target, setup_script)
    write_executable_script(harness_target, harness_script)
    print(f"stronkpi-setup install: installed {setup_target}")
    print(f"stronkpi-setup install: installed {harness_target}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.dry_run:
        raise StronkPiError("live provider/runtime sessions are not started by setup validation")
    cmd_validate(args)
    install_bundle_defaults(dry_run=True)
    print("stronkpi-setup run: dry-run ok")
    return 0


def validate_harness_control_env() -> None:
    if dev_overrides_enabled():
        return
    blocked: list[str] = []
    for name, value in os.environ.items():
        if not value:
            continue
        if name in CONTROL_PLANE_ENV_NAMES:
            blocked.append(name)
            continue
        if not name.startswith(("STRONK_PI_", "STRONKPI_", "PI_")):
            continue
        if name in CONTROL_PLANE_PREFIX_ALLOWLIST_EXACT:
            continue
        if any(name.startswith(prefix) for prefix in CONTROL_PLANE_PREFIX_ALLOWLIST_PREFIXES):
            continue
        if name in ENV_NAMES or SECRET_KEY_PATTERN.search(name):
            continue
        blocked.append(name)
    if blocked:
        raise StronkPiError(
            "control-plane env override(s) require STRONK_PI_DEV_OVERRIDES=1: "
            + ", ".join(sorted(blocked))
        )


def load_runtime_defaults(root: Path) -> dict[str, Any]:
    defaults_path = root / "config" / "defaults.toml"
    if defaults_path.is_file():
        return load_toml_document(defaults_path)
    return load_toml_document(setup_root() / DEFAULTS_RELATIVE)


def harness_string(defaults: dict[str, Any], key: str, fallback: str) -> str:
    harness = defaults.get("harness")
    if isinstance(harness, dict):
        value = harness.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return fallback


def operator_home_path() -> Path:
    raw = os.environ.get("HOME")
    home = Path(raw).expanduser() if raw else Path.home()
    if not home.is_absolute():
        raise StronkPiError(f"HOME must be absolute: {home}")
    return home.resolve(strict=False)


def validate_optional_absolute_env_path(env: dict[str, str], name: str) -> None:
    raw = env.get(name)
    if not raw:
        return
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise StronkPiError(f"{name} must be absolute: {path}")


def trusted_python_executable() -> str:
    candidate = Path(sys.executable).resolve(strict=False)
    if candidate.is_absolute() and candidate.exists():
        return str(candidate)
    resolved = shutil.which("python3")
    if resolved:
        return str(Path(resolved).resolve(strict=False))
    raise StronkPiError("unable to resolve trusted Python interpreter")


def sanitized_harness_path(root: Path) -> str:
    entries: list[str] = []
    seen: set[str] = set()

    def append(path: Path) -> None:
        text = str(path)
        if text and text not in seen:
            seen.add(text)
            entries.append(text)

    append(root / "pi-fork-runtime" / "node_modules" / ".bin")
    for raw in os.environ.get("PATH", "").split(os.pathsep):
        if not raw or raw == ".":
            continue
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            continue
        append(candidate.resolve(strict=False))
    return os.pathsep.join(entries)


def git_root_or_self(path: Path) -> Path:
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip()).resolve(strict=False)
    return path.resolve(strict=False)


def dirs_between(root: Path, leaf: Path) -> list[Path]:
    try:
        relative = leaf.relative_to(root)
    except ValueError:
        return [leaf]
    dirs = [root]
    current = root
    for part in relative.parts:
        current = current / part
        dirs.append(current)
    return dirs


def append_skill_root(
    roots: list[dict[str, str]],
    seen: set[str],
    candidate: Path,
    scope: str,
    *,
    owner_root: Path | None = None,
    label: str = "skill root",
) -> None:
    if not candidate.is_dir():
        return
    candidate_real = candidate.resolve(strict=False)
    if owner_root is not None:
        owner_real = owner_root.resolve(strict=False)
        if not is_relative_to(candidate_real, owner_real):
            raise StronkPiError(f"{label} escapes owner root: {candidate} -> {candidate_real}")
    resolved = str(candidate_real)
    if resolved not in seen:
        seen.add(resolved)
        roots.append({"path": resolved, "scope": scope})


def discover_skill_roots(*, cwd: Path | None = None, home: Path | None = None) -> list[dict[str, str]]:
    launch_cwd = (cwd or Path.cwd()).resolve(strict=False)
    operator_home = (home or Path.home()).resolve(strict=False)
    roots: list[dict[str, str]] = []
    seen: set[str] = set()

    for directory in dirs_between(git_root_or_self(launch_cwd), launch_cwd):
        candidate = directory / ".agents" / "skills"
        directory_real = directory.resolve(strict=False)
        append_skill_root(roots, seen, candidate, "repo", owner_root=directory_real, label="repo skill root")

    user_root = operator_home / ".agents" / "skills"
    append_skill_root(roots, seen, user_root, "user")

    return roots


def runtime_skill_roots(root: Path) -> list[dict[str, str]]:
    defaults = load_runtime_defaults(root)
    roots: list[dict[str, str]] = []
    seen: set[str] = set()
    root_real = root.resolve(strict=False)
    for key in SUBAGENT_RUNTIME_PACKAGE_KEYS:
        package = runtime_package_status(root, defaults, key)
        if not package["installed"]:
            continue
        package_root = Path(str(package["packagePath"]))
        package_root_real = package_root.resolve(strict=False)
        # Reject symlinked or escaping runtime package roots before exporting system skill
        # roots. Without this check, a symlinked candidate dir could resolve outside the
        # state root and make the skills path look "inside" the escaping owner root.
        if not is_relative_to(package_root_real, root_real):
            raise StronkPiError(
                f"{package['packageName']} runtime package root escapes state root: "
                f"{package_root} -> {package_root_real}"
            )
        append_skill_root(
            roots,
            seen,
            package_root / "skills",
            "system",
            owner_root=package_root_real,
            label=f"{package['packageName']} skill root",
        )
    return roots


def harness_skill_roots(root: Path, *, cwd: Path | None = None, home: Path | None = None) -> list[dict[str, str]]:
    roots = discover_skill_roots(cwd=cwd, home=home)
    seen = {item["path"] for item in roots}
    for item in runtime_skill_roots(root):
        if item["path"] in seen:
            continue
        seen.add(item["path"])
        roots.append(item)
    return roots


def scrub_harness_env(env: dict[str, str]) -> dict[str, str]:
    """Strip injection-prone environment variables before launching the Pi runtime.

    Node, the dynamic loader, Python, npm, and Bun honor a family of env vars that can
    load arbitrary code, rewrite module resolution, pin a custom CA, or disable TLS
    verification. These must never reach ``harness_environment()`` output even when the
    caller's shell sets them.
    """
    for name in list(env):
        if name in HARNESS_ENV_INJECTION_DENY_EXACT:
            env.pop(name, None)
        elif name.startswith(HARNESS_ENV_INJECTION_DENY_PREFIXES):
            env.pop(name, None)
    return env


def harness_environment(root: Path) -> dict[str, str]:
    guard_script = setup_root() / "lib" / "stronk-pi-guard.py"
    defaults = load_runtime_defaults(root)
    skill_roots = harness_skill_roots(root)
    ensure_state_root_layout(root)
    home = operator_home_path()
    python = trusted_python_executable()
    env = scrub_harness_env(os.environ.copy())
    env["HOME"] = str(home)
    validate_optional_absolute_env_path(env, "XDG_CONFIG_HOME")
    validate_optional_absolute_env_path(env, "XDG_CACHE_HOME")
    env.update(
        {
            "PATH": sanitized_harness_path(root),
            "PI_SKIP_VERSION_CHECK": "1",
            "PI_CODING_AGENT_DIR": str(state_agent_dir(root)),
            "PI_CODING_AGENT_SESSION_DIR": str(state_session_dir(root)),
            "STRONK_PI_GUARD": str(guard_script),
            "STRONK_PI_HOOK_COMMAND_JSON": json.dumps([python, str(guard_script), "hook"]),
            "STRONK_PI_CODEX_HOOK_COMMAND_JSON": json.dumps([python, str(guard_script), "codex-hook"]),
            "STRONK_PI_URL_CHECK_COMMAND_JSON": json.dumps([python, str(guard_script), "url-check"]),
            "STRONK_PI_TELEGRAM_COMMAND_JSON": json.dumps([python, str(guard_script), "telegram"]),
            "STRONK_PI_STATE_ROOT": str(root),
            "STRONK_PI_CONFIG_ROOT": str(state_config_root(root)),
            "STRONK_PI_LOG_ROOT": str(state_log_root(root)),
            "STRONK_PI_CACHE_ROOT": str(state_cache_root(root)),
            "STRONK_PI_TMP_ROOT": str(state_tmp_root(root)),
            "STRONK_PI_MCP_CONFIG_PATH": str(project_generated_mcp_config_path(Path.cwd(), root)),
            "STRONK_PI_WEB_SEARCH_CONFIG": str(state_web_search_config_path(root)),
            "STRONK_PI_INTERCOM_BRIDGE": str(state_intercom_bridge_path(root)),
            "STRONK_PI_ROLE_MANIFEST": str(state_config_root(root) / "roles.toml"),
            "STRONK_PI_SUBAGENT_FACADE": harness_string(defaults, "subagent_facade", "stronk"),
            "STRONK_PI_SUBAGENT_ADAPTER": harness_string(defaults, "subagent_adapter", "intercom"),
            "STRONK_PI_SKILL_ROOTS": json.dumps(skill_roots, separators=(",", ":")),
        }
    )
    search_provider = harness_string(defaults, "search_provider", "")
    if search_provider and not env.get("STRONK_PI_SEARCH_PROVIDER"):
        env["STRONK_PI_SEARCH_PROVIDER"] = search_provider
    dangerous_hook = default_dangerous_command_hook_path()
    if dangerous_hook.is_file():
        env["STRONK_PI_DANGEROUS_COMMAND_HOOK"] = str(dangerous_hook)
    local_manifest = root / "config" / "roles.local.toml"
    if local_manifest.is_file():
        env["STRONK_PI_ROLE_MANIFEST_LOCAL"] = str(local_manifest)
    if not env.get("KIMI_API_KEY") and env.get("KIMI_CODE_API_KEY"):
        env["KIMI_API_KEY"] = env["KIMI_CODE_API_KEY"]
    return env


def harness_payload(root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    status = inspect_bundle_status(root)
    skill_roots = harness_skill_roots(root)
    home = operator_home_path()
    warnings: list[str] = []
    if not status["plugin"]["installed"]:
        warnings.append("plugin artifact is not installed; live launch will fail closed until setup update installs it")
    if not status["runtime"]["piBinaryExists"]:
        warnings.append("trusted Pi runtime is not installed; live launch will fail closed until a trust-pinned runtime is installed")
    mcp_status = inspect_mcp_adapter_runtime(root)
    if mcp_status["configured"] and not mcp_status["adapterInstalled"]:
        warnings.append("selected MCP servers are configured but pi-mcp-adapter is not installed; live launch will fail closed")
    if mcp_status["projectConfigFiles"]:
        warnings.append("project MCP config files are present; live launch will fail closed to preserve the .mcp-tools boundary")
    subagent_status = inspect_subagent_runtime(root)
    if subagent_status["enabled"]:
        subagent_status = prepare_subagent_runtime(root)
    elif subagent_status["configured"]:
        missing = ", ".join(
            f"{item['packageName']}@{item['packageVersion']}"
            for item in subagent_status["missingPackages"]
        )
        warnings.append(f"Stronk Pi subagent intercom runtime packages are missing ({missing}); live launch will fail closed")
    payload = {
        "ok": True,
        "version": VERSION,
        "setupRoot": str(setup_root()),
        "stateRoot": str(root),
        "effectiveHome": str(home),
        "configRoot": str(state_config_root(root)),
        "cacheRoot": str(state_cache_root(root)),
        "logRoot": str(state_log_root(root)),
        "tmpRoot": str(state_tmp_root(root)),
        "agentDir": str(state_agent_dir(root)),
        "sessionDir": str(state_session_dir(root)),
        "mcpConfigPath": str(mcp_status["configPath"]),
        "intercomBridgePath": str(subagent_status["intercomBridgePath"]),
        "blockedRealHomeWriteRisks": real_home_write_risks(home, root),
        "bundle": {
            "compatibilityVersion": BUNDLE_CONTRACT_VERSION,
            "configSchemaVersion": CONFIG_SCHEMA_VERSION,
            "changed": bundle["changed"],
        },
        "harness": status["harness"],
        "roleConfig": status["roles"],
        "pluginArtifact": status["plugin"],
        "runtime": status["runtime"],
        "mcpAdapter": mcp_status,
        "subagentRuntime": subagent_status,
        "skillRoots": skill_roots,
        "warnings": warnings,
    }
    return payload


def print_harness_text(label: str, payload: dict[str, Any]) -> None:
    print(f"stronkpi {label}: ok")
    print(f"effective_home={payload['effectiveHome']}")
    print(f"state_root={payload['stateRoot']}")
    print(f"config_root={payload['configRoot']}")
    print(f"cache_root={payload['cacheRoot']}")
    print(f"log_root={payload['logRoot']}")
    print(f"tmp_root={payload['tmpRoot']}")
    print(f"agent_dir={payload['agentDir']}")
    print(f"session_dir={payload['sessionDir']}")
    print(f"role_manifest={payload['roleConfig']['manifest']}")
    print(f"roles_local={payload['roleConfig']['localManifest']}")
    print(f"roles_local_exists={payload['roleConfig']['localManifestExists']}")
    print(f"generated_agents={payload['roleConfig']['generatedAgentsDir']}")
    print(f"generated_agent_count={payload['roleConfig']['generatedAgentCount']}")
    print(f"plugin_installed={payload['pluginArtifact']['installed']}")
    print(f"runtime_installed={payload['runtime']['piBinaryExists']}")
    print(f"skill_roots={json.dumps(payload.get('skillRoots', []), separators=(',', ':'))}")
    print(f"mcp_selected_tools={','.join(payload['mcpAdapter']['selectedTools'])}")
    print(f"mcp_adapter_installed={payload['mcpAdapter']['adapterInstalled']}")
    print(f"mcp_adapter_enabled={payload['mcpAdapter']['enabled']}")
    print(f"mcp_config={payload['mcpConfigPath']}")
    print(f"subagent_adapter={payload['subagentRuntime']['adapter']}")
    print(f"subagent_runtime_enabled={payload['subagentRuntime']['enabled']}")
    print(f"subagent_extensions={','.join(payload['subagentRuntime']['extensionPaths'])}")
    print(f"intercom_bridge={payload['intercomBridgePath']}")
    for warning in payload.get("warnings", []):
        print(f"warning={warning}")


def build_pi_launch_args(
    *,
    plugin_path: Path,
    session_dir: Path,
    skill_roots: list[dict[str, str]] | None = None,
    mcp_status: dict[str, Any] | None = None,
    subagent_status: dict[str, Any] | None = None,
    offline: bool = False,
) -> list[str]:
    launch_args = [
        "pi",
        "--no-extensions",
        "--extension",
        str(plugin_path),
        "--no-skills",
    ]
    for root in skill_roots or []:
        path = root.get("path") if isinstance(root, dict) else None
        if isinstance(path, str) and path:
            launch_args.extend(["--skill", path])
    launch_args.extend(
        [
            "--no-prompt-templates",
            "--no-themes",
            "--session-dir",
            str(session_dir),
        ]
    )
    if subagent_status and subagent_status.get("enabled"):
        for extension_path in subagent_status.get("extensionPaths") or []:
            launch_args.extend(["--extension", str(extension_path)])
        launch_args.extend(["--exclude-tools", "subagent"])
    if mcp_status and mcp_status.get("enabled"):
        launch_args.extend(
            [
                "--extension",
                str(mcp_status["adapterPath"]),
                "--mcp-config",
                str(mcp_status["configPath"]),
            ]
        )
    if offline:
        launch_args.append("--offline")
    return launch_args


def validate_pi_passthrough_args(pi_args: list[str]) -> None:
    controlled_prefixes = tuple(f"{flag}=" for flag in CONTROLLED_PI_FLAGS if flag.startswith("--"))
    for arg in pi_args:
        if arg in CONTROLLED_PI_FLAGS:
            raise StronkPiError(f"flag is owned by stronkpi and cannot be passed through: {arg}")
        if controlled_prefixes and arg.startswith(controlled_prefixes):
            raise StronkPiError(f"flag is owned by stronkpi and cannot be passed through: {arg.split('=', 1)[0]}")


def parse_harness_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="stronkpi")
    parser.add_argument("--version", action="version", version=f"stronkpi {VERSION}")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--json", action="store_true")
    args, pi_args = parser.parse_known_args(argv)
    if pi_args and pi_args[0] == "--":
        pi_args = pi_args[1:]
    args.pi_args = pi_args
    if (args.validate_only or args.diagnose) and args.pi_args:
        raise StronkPiError("--validate-only/--diagnose do not accept Pi passthrough args")
    validate_pi_passthrough_args(args.pi_args)
    return args


def harness_main(argv: list[str] | None = None) -> int:
    args = parse_harness_args(argv)

    validate_harness_control_env()
    root = harness_state_root()
    bundle = install_bundle_defaults(root=root, dry_run=False)
    payload = harness_payload(root, bundle)

    if args.diagnose:
        if args.json:
            json_out(payload)
        else:
            print_harness_text("diagnose", payload)
        return 0
    if args.validate_only:
        if args.json:
            json_out(payload)
        else:
            print_harness_text("validate", payload)
        return 0

    if not payload["pluginArtifact"]["installed"]:
        raise StronkPiError("plugin artifact missing; run stronkpi-setup update before live launch")
    pi_binary = Path(payload["runtime"]["piBinary"])
    if not pi_binary.is_file() or not os.access(pi_binary, os.X_OK):
        raise StronkPiError("trusted Pi runtime missing; install a trust-pinned runtime before live launch")
    env = harness_environment(root)
    skill_roots = harness_skill_roots(root)
    plugin_path = Path(payload["pluginArtifact"]["expectedPath"])
    session_dir = root / "agent" / "sessions"
    subagent_status = prepare_subagent_runtime(root)
    mcp_status = prepare_mcp_adapter_runtime(root)
    offline = os.environ.get("STRONKPI_NO_NETWORK") == "1"
    if offline:
        env["PI_OFFLINE"] = "1"
    launch_args = build_pi_launch_args(
        plugin_path=plugin_path,
        session_dir=session_dir,
        skill_roots=skill_roots,
        mcp_status=mcp_status,
        subagent_status=subagent_status,
        offline=offline,
    )
    os.execvpe(str(pi_binary), [*launch_args, *args.pi_args], env)
    return 127


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stronkpi-setup")
    parser.add_argument("--version", action="version", version=f"stronkpi-setup {VERSION}")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("validate").set_defaults(func=cmd_validate)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--redact", action="store_true")
    doctor.add_argument("--mcp-registry", default=str(default_mcp_registry_path()))
    doctor.add_argument("--mcp-tools")
    doctor.add_argument("--allow-missing-mcp", action="store_true")
    doctor.add_argument("--check-network", action="store_true")
    doctor.add_argument("--network-url", default=DEFAULT_NETWORK_URL)
    doctor.set_defaults(func=cmd_doctor)

    update = sub.add_parser("update")
    update.add_argument("--dry-run", action="store_true")
    update.add_argument("--manifest", default=str(setup_root() / "manifests" / "current.json"))
    update.set_defaults(func=cmd_update)

    refresh_config = sub.add_parser("refresh-config")
    refresh_config.add_argument("--dry-run", action="store_true")
    refresh_config.add_argument("--json", action="store_true")
    refresh_config.set_defaults(func=cmd_refresh_config)

    cleanup = sub.add_parser("cleanup-private-home")
    cleanup_mode = cleanup.add_mutually_exclusive_group()
    cleanup_mode.add_argument("--dry-run", action="store_true")
    cleanup_mode.add_argument("--apply", action="store_true")
    cleanup.add_argument("--json", action="store_true")
    cleanup.set_defaults(func=cmd_cleanup_private_home)

    import_codex_roles_parser = sub.add_parser("import-codex-roles")
    import_codex_roles_parser.add_argument(
        "--source",
        help=(
            "Codex role TOML directory; defaults to ~/.codex/roles/stronk, "
            "then ~/.agents/roles/stronk, then ~/.agents/codex/roles/stronk"
        ),
    )
    import_codex_roles_parser.add_argument("--dry-run", action="store_true")
    import_codex_roles_parser.add_argument("--json", action="store_true")
    import_codex_roles_parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="import role templates without regenerating runtime Pi agent Markdown",
    )
    import_codex_roles_parser.set_defaults(func=cmd_import_codex_roles)

    install = sub.add_parser("install")
    install.add_argument("--dry-run", action="store_true")
    install.add_argument("--prefix", default=str(Path.home() / ".local"))
    install.set_defaults(func=cmd_install)

    run = sub.add_parser("run")
    run.add_argument("--dry-run", action="store_true")
    run.set_defaults(func=cmd_run)

    sub.add_parser("hook").set_defaults(func=cmd_hook)
    sub.add_parser("codex-hook").set_defaults(func=cmd_codex_hook)
    sub.add_parser("url-check").set_defaults(func=cmd_url_check)
    sub.add_parser("telegram").set_defaults(func=cmd_telegram)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    try:
        return int(args.func(args))
    except (StronkPiError, urllib.error.URLError, OSError) as exc:
        print(f"stronkpi-setup: {redact(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
