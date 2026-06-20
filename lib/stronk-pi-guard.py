#!/usr/bin/env python3
"""Stronk Pi setup guard, validator, and manifest verifier."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import re
import shutil
import socket
import stat
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


VERSION = "0.1.0"
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
DEFAULT_NETWORK_URL = "https://github.com/EYYCHEEV/stronk-pi-setup"
PERSONAL_PATH_RE = re.compile(r"(?<![A-Za-z0-9_.-])(?:/Users|/home)/[^/\s\"':,;)]+")
ENV_NAMES = (
    "DEEPSEEK_API_KEY",
    "MOONSHOT_API_KEY",
    "KIMI_CODE_API_KEY",
    "ALIBABA_CLOUD_CODING_PLAN_API_KEY",
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


def state_root() -> Path:
    raw = os.environ.get("STRONKPI_STATE_ROOT")
    root = Path(raw).expanduser() if raw else Path.home() / ".stronk-pi"
    if not root.is_absolute():
        raise StronkPiError(f"state root must be absolute: {root}")
    if root.exists() and root.is_symlink():
        raise StronkPiError(f"state root must not be a symlink: {root}")
    return root


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
        if not tools_path.exists():
            errors.append(f"MCP tools allowlist missing: {tools_path}")
        elif tools_path.is_symlink():
            errors.append(f"MCP tools allowlist must not be a symlink: {tools_path}")
        else:
            try:
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


def validate_archive(path: Path) -> None:
    if not path.is_file():
        raise StronkPiError(f"missing artifact: {path}")
    with tarfile.open(path, "r:gz") as archive:
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


def verify_manifest(manifest_path: Path) -> list[ArtifactResult]:
    manifest = load_json(manifest_path)
    if manifest.get("schemaVersion") != 1:
        raise StronkPiError("manifest schemaVersion must be 1")
    compatibility = require_string(manifest, "compatibilityVersion")
    fail_if_floating("compatibilityVersion", compatibility)
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        raise StronkPiError("manifest artifacts must be an array")
    results: list[ArtifactResult] = []
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
        require_string(raw_item, "workflowRunId")
        require_string(raw_item, "attestation")
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
        validate_archive(path)
        results.append(ArtifactResult(name, version, path, actual_sha, actual_size))
    return results


def install_artifacts(results: list[ArtifactResult], dry_run: bool) -> None:
    root = ensure_private_dir(state_root())
    if dry_run:
        return
    installs = ensure_private_dir(root / "artifacts")
    for result in results:
        dest = installs / f"{result.name}-{result.version}"
        tmp = Path(tempfile.mkdtemp(prefix=f".{result.name}.", dir=installs))
        try:
            with tarfile.open(result.path, "r:gz") as archive:
                archive.extractall(tmp)
            os.replace(tmp, dest)
        except Exception:
            shutil.rmtree(tmp, ignore_errors=True)
            raise


def cmd_validate(args: argparse.Namespace) -> int:
    root = setup_root()
    required = [
        root / "bin" / "stronkpi-setup",
        root / "install.sh",
        root / "lib" / "stronk-pi-guard.py",
        root / "config" / "pi" / "agent" / "AGENTS.md",
        root / "config" / "pi" / "agent" / "models.json",
        root / "config" / "pi" / "agent" / "settings.base.json",
        root / "config" / "pi" / "web-search.json",
        root / "manifests" / "current.json",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        raise StronkPiError("missing required setup files: " + ", ".join(missing))
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
        root / "bin" / "stronkpi",
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
    payload = {
        "ok": not errors,
        "version": VERSION,
        "setupRoot": str(setup_root()),
        "stateRoot": str(state_root()),
        "noNetwork": os.environ.get("STRONKPI_NO_NETWORK") == "1",
        "dependencies": dependencies,
        "env": env_status,
        "mcpRegistry": mcp,
        "network": network,
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
    install_artifacts(results, args.dry_run)
    mode = "dry-run" if args.dry_run else "installed"
    print(f"stronkpi-setup update: {mode} verified {len(results)} artifact(s)")
    for result in results:
        print(f"- {result.name} {result.version} {result.sha256}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    root = setup_root()
    guard = root / "lib" / "stronk-pi-guard.py"
    prefix = Path(args.prefix).expanduser()
    if not prefix.is_absolute():
        raise StronkPiError("--prefix must be absolute")
    bin_dir = prefix / "bin"
    setup_target = bin_dir / "stronkpi-setup"
    if args.dry_run:
        print(f"stronkpi-setup install: would install {setup_target}")
        print("stronkpi-setup install: will not install or wrap stronkpi")
        print("stronkpi-setup install: no compatibility aliases will be created")
        return 0
    bin_dir.mkdir(parents=True, exist_ok=True)
    setup_target.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from __future__ import annotations",
                "",
                "import os",
                "import runpy",
                "",
                f"os.environ.setdefault('STRONKPI_SETUP_ROOT', {str(root)!r})",
                f"runpy.run_path({str(guard)!r}, run_name='__main__')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    os.chmod(setup_target, 0o755)
    print(f"stronkpi-setup install: installed {setup_target}")
    print("stronkpi-setup install: left stronkpi untouched")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.dry_run:
        raise StronkPiError("live provider/runtime sessions are not started by setup validation")
    cmd_validate(args)
    print("stronkpi-setup run: dry-run ok")
    return 0


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

    install = sub.add_parser("install")
    install.add_argument("--dry-run", action="store_true")
    install.add_argument("--prefix", default=str(Path.home() / ".local"))
    install.set_defaults(func=cmd_install)

    run = sub.add_parser("run")
    run.add_argument("--dry-run", action="store_true")
    run.set_defaults(func=cmd_run)
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
