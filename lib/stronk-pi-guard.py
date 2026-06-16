#!/usr/bin/env python3
"""Stronk Pi setup guard, validator, and manifest verifier."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import re
import shlex
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
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[/\\]")
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
    request = urllib.request.Request(url, headers={"User-Agent": f"stronkpi/{VERSION}"})
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
        require_string(raw_item, "compatibilityVersion")
        require_string(raw_item, "createdAt")
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
        check_public_http_url(release_url, "release URL")
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
        root / "bin" / "stronkpi",
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
    forbidden_bins = [root / "bin" / "sp", root / "bin" / "pi"]
    found = [path.name for path in forbidden_bins if path.exists()]
    if found:
        raise StronkPiError("forbidden compatibility commands present: " + ", ".join(found))
    print("stronkpi validate: ok")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    env_status = {name: ("set" if os.environ.get(name) else "missing") for name in ENV_NAMES}
    payload = {
        "ok": True,
        "version": VERSION,
        "setupRoot": str(setup_root()),
        "stateRoot": str(state_root()),
        "noNetwork": os.environ.get("STRONKPI_NO_NETWORK") == "1",
        "env": env_status,
    }
    if args.json:
        json_out(payload)
    else:
        print("stronkpi doctor: ok")
        for key, value in payload.items():
            print(f"{key}={redact(value)}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser()
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()
    results = verify_manifest(manifest_path)
    install_artifacts(results, args.dry_run)
    mode = "dry-run" if args.dry_run else "installed"
    print(f"stronkpi update: {mode} verified {len(results)} artifact(s)")
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
    target = bin_dir / "stronkpi"
    if args.dry_run:
        print(f"stronkpi install: would install {target}")
        print("stronkpi install: no compatibility aliases will be created")
        return 0
    bin_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            [
                "#!/usr/bin/env zsh",
                "set -euo pipefail",
                f"export STRONKPI_SETUP_ROOT={shlex.quote(str(root))}",
                f"exec python3 {shlex.quote(str(guard))} \"$@\"",
                "",
            ]
        ),
        encoding="utf-8",
    )
    os.chmod(target, 0o755)
    print(f"stronkpi install: installed {target}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    if not args.dry_run:
        raise StronkPiError("live provider/runtime sessions are not started by setup validation")
    cmd_validate(args)
    print("stronkpi run: dry-run ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stronkpi")
    parser.add_argument("--version", action="version", version=f"stronkpi {VERSION}")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("validate").set_defaults(func=cmd_validate)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    doctor.add_argument("--redact", action="store_true")
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
        print(f"stronkpi: {redact(str(exc))}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
