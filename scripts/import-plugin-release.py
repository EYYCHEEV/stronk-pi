#!/usr/bin/env python3
"""Import a released stronk-pi-plugin artifact into the setup manifest."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_REPO = "EYYCHEEV/stronk-pi-plugin"
PLUGIN_NAME = "stronk-pi-plugin"
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    print(f"stronk-pi import-plugin-release: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_build_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("BUILD-MANIFEST.json must contain an object")
    return data


def require_string(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"BUILD-MANIFEST.json missing non-empty {key}")
    return value


def parse_release(data: dict) -> tuple[str, str, str, int, str, str, str, str]:
    source_repo = require_string(data, "sourceRepo")
    if source_repo != PLUGIN_REPO:
        fail(f"sourceRepo must be {PLUGIN_REPO}")

    tag = require_string(data, "tag")
    prefix = f"{PLUGIN_NAME}-v"
    if not tag.startswith(prefix):
        fail(f"tag must start with {prefix}")
    version = tag.removeprefix(prefix)
    if not VERSION_RE.fullmatch(version):
        fail(f"tag does not contain a valid semver: {tag}")

    artifact = require_string(data, "artifact")
    expected_artifact = f"{PLUGIN_NAME}-{version}.tgz"
    if artifact != expected_artifact:
        fail(f"artifact must be {expected_artifact}")

    sha256 = require_string(data, "sha256")
    if not SHA256_RE.fullmatch(sha256):
        fail("sha256 must be a lowercase hex SHA-256 digest")

    byte_size = data.get("byteSize")
    if not isinstance(byte_size, int) or byte_size <= 0:
        fail("byteSize must be a positive integer")

    source_commit = require_string(data, "sourceCommit")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        fail("sourceCommit must be a 40-character lowercase git SHA")

    workflow_run_id = str(data.get("workflowRunId") or "").strip()
    if not workflow_run_id:
        fail("workflowRunId is required")

    created_at = require_string(data, "createdAt")
    return version, tag, artifact, byte_size, sha256, source_commit, workflow_run_id, created_at


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        fail(f"expected one match in {path.relative_to(ROOT)}")
    path.write_text(updated, encoding="utf-8")


def update_manifest(
    version: str,
    tag: str,
    artifact: str,
    byte_size: int,
    sha256: str,
    source_commit: str,
    workflow_run_id: str,
    created_at: str,
) -> None:
    manifest_path = ROOT / "manifests" / "current.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        fail("manifest artifacts must be a list")
    matches = [item for item in artifacts if isinstance(item, dict) and item.get("name") == PLUGIN_NAME]
    if len(matches) != 1:
        fail(f"manifest must contain exactly one {PLUGIN_NAME} artifact")

    item = matches[0]
    release_url = f"https://github.com/{PLUGIN_REPO}/releases/tag/{tag}"
    artifact_url = f"https://github.com/{PLUGIN_REPO}/releases/download/{tag}/{artifact}"
    attestation = f"github-attestation:{PLUGIN_REPO}/{artifact}@sha256:{sha256}"
    item.update(
        {
            "version": version,
            "sourceRepo": PLUGIN_REPO,
            "sourceCommit": source_commit,
            "immutableTag": tag,
            "releaseUrl": release_url,
            "artifactUrl": artifact_url,
            "sha256": sha256,
            "byteSize": byte_size,
            "workflowRunId": workflow_run_id,
            "attestation": attestation,
            "createdAt": created_at,
            "provenance": {
                "sourceRepo": PLUGIN_REPO,
                "sourceCommit": source_commit,
                "immutableTag": tag,
                "workflowRunId": workflow_run_id,
            },
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def update_version_surfaces(version: str) -> None:
    replace_once(
        ROOT / "lib" / "stronk-pi-guard.py",
        r'^DEFAULT_PLUGIN_VERSION = "[^"]+"$',
        f'DEFAULT_PLUGIN_VERSION = "{version}"',
    )
    replace_once(
        ROOT / "roles" / "stronk" / "roles.toml",
        r"stronk-pi-plugin-[^/]+/package/src/index\.mjs",
        f"stronk-pi-plugin-{version}/package/src/index.mjs",
    )
    replace_once(
        ROOT / "tests" / "make_fixtures.py",
        r'^PLUGIN_VERSION = "[^"]+"$',
        f'PLUGIN_VERSION = "{version}"',
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_manifest", help="Path to BUILD-MANIFEST.json from the plugin release")
    parser.add_argument("--no-regenerate-fixtures", action="store_true")
    args = parser.parse_args(argv)

    build_manifest = Path(args.build_manifest).expanduser()
    if not build_manifest.is_absolute():
        build_manifest = (Path.cwd() / build_manifest).resolve()

    data = load_build_manifest(build_manifest)
    version, tag, artifact, byte_size, sha256, source_commit, workflow_run_id, created_at = parse_release(data)

    update_manifest(version, tag, artifact, byte_size, sha256, source_commit, workflow_run_id, created_at)
    update_version_surfaces(version)

    if not args.no_regenerate_fixtures:
        subprocess.run([sys.executable, str(ROOT / "tests" / "make_fixtures.py")], check=True)

    print(f"stronk-pi import-plugin-release: {PLUGIN_NAME} {version}")
    print("manifest=manifests/current.json")
    print(f"fixtures_regenerated={not args.no_regenerate_fixtures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
