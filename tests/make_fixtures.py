#!/usr/bin/env python3
"""Generate deterministic offline manifest/artifact fixtures."""

from __future__ import annotations

import hashlib
import gzip
import io
import json
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "tests" / "fixtures" / "artifacts"
MANIFEST_DIR = ROOT / "tests" / "fixtures" / "manifests"
SOURCE_COMMIT = "0123456789abcdef0123456789abcdef01234567"
PLUGIN_REPO = "EYYCHEEV/stronk-pi-plugin"
PLUGIN_VERSION = "0.1.0"
PLUGIN_TAG = f"stronk-pi-plugin-v{PLUGIN_VERSION}"
PLUGIN_ASSET = f"stronk-pi-plugin-{PLUGIN_VERSION}.tgz"


def bundle_contract() -> dict:
    return {
        "configSchemaVersion": 1,
        "stateRoot": "~/.stronk-pi",
        "defaultConfigPath": "~/.stronk-pi/config/defaults.toml",
        "defaultRoleManifestPath": "~/.stronk-pi/config/roles.toml",
        "localRoleManifestPath": "~/.stronk-pi/config/roles.local.toml",
        "roleTemplatesPath": "~/.stronk-pi/config/role-templates",
        "generatedAgentsPath": "~/.stronk-pi/agent/agents",
        "harness": {
            "command": "stronkpi",
            "owner": "stronk-pi",
        },
        "models": {
            "default": "kimi-coding/kimi-for-coding:xhigh",
            "vision": "kimi-coding/kimi-for-coding:xhigh",
        },
        "packagePins": {
            "mcp_adapter": {"name": "pi-mcp-adapter", "version": "2.5.3"},
            "subagents": {"name": "pi-subagents", "version": "0.22.0"},
            "intercom": {"name": "pi-intercom", "version": "0.6.0"},
            "jiti": {"name": "jiti", "version": "2.7.0"},
            "ask_user": {"name": "pi-ask-user", "version": "0.8.0"},
            "tsx": {"name": "tsx", "version": "4.22.4"},
            "typebox": {"name": "typebox", "version": "1.1.39"},
            "esbuild": {"name": "esbuild", "version": "0.28.0"},
        },
    }


def write_tgz(path: Path, files: dict[str, bytes], *, symlink: bool = False, hardlink: bool = False) -> None:
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=1) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for name, payload in files.items():
                    info = tarfile.TarInfo(name)
                    info.mtime = 1
                    if symlink:
                        info.type = tarfile.SYMTYPE
                        info.linkname = "../outside"
                        info.size = 0
                        archive.addfile(info)
                        continue
                    if hardlink:
                        info.type = tarfile.LNKTYPE
                        info.linkname = "../outside"
                        info.size = 0
                        archive.addfile(info)
                        continue
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_manifest(artifact_path: Path, sha: str, size: int) -> dict:
    rel = artifact_path if not artifact_path.is_absolute() else artifact_path.relative_to(MANIFEST_DIR)
    return {
        "schemaVersion": 1,
        "compatibilityVersion": "stronkpi-setup-v1",
        "bundle": bundle_contract(),
        "artifacts": [
            {
                "name": "stronk-pi-plugin",
                "version": PLUGIN_VERSION,
                "sourceRepo": PLUGIN_REPO,
                "sourceCommit": SOURCE_COMMIT,
                "immutableTag": PLUGIN_TAG,
                "releaseUrl": f"https://github.com/{PLUGIN_REPO}/releases/tag/{PLUGIN_TAG}",
                "artifactPath": rel.as_posix(),
                "sha256": sha,
                "byteSize": size,
                "workflowRunId": "fixture-run-1",
                "attestation": "fixture-attestation",
                "sbom": "fixture-sbom",
                "compatibilityVersion": "stronkpi-setup-v1",
                "createdAt": "2026-06-16T00:00:00Z",
                "provenance": {
                    "sourceRepo": PLUGIN_REPO,
                    "sourceCommit": SOURCE_COMMIT,
                    "immutableTag": PLUGIN_TAG,
                    "workflowRunId": "fixture-run-1"
                }
            }
        ]
    }


def base_https_manifest(artifact_url: str, sha: str, size: int) -> dict:
    manifest = base_manifest(Path("../artifacts") / PLUGIN_ASSET, sha, size)
    item = manifest["artifacts"][0]
    item.pop("artifactPath")
    item["artifactUrl"] = artifact_url
    return manifest


def write_manifest(name: str, data: dict) -> None:
    (MANIFEST_DIR / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    good = ARTIFACT_DIR / PLUGIN_ASSET
    wrong_package_identity = ARTIFACT_DIR / "wrong-package-identity.tgz"
    traversal = ARTIFACT_DIR / "archive-traversal.tgz"
    symlink = ARTIFACT_DIR / "symlink-escape.tgz"
    hardlink = ARTIFACT_DIR / "hardlink-escape.tgz"

    write_tgz(
        good,
        {
            "package/bin/stronkpi": b"#!/bin/sh\nprintf '%s\\n' fixture\n",
            "package/lib/stronk-pi-guard.py": b"print('fixture')\n",
            "package/src/index.mjs": b"export default function stronkPiFixture() {}\n",
            "package/package.json": f'{{"name":"stronk-pi-plugin","version":"{PLUGIN_VERSION}"}}\n'.encode(),
        },
    )
    write_tgz(traversal, {"../escape": b"bad\n"})
    write_tgz(
        wrong_package_identity,
        {
            "package/bin/stronkpi": b"#!/bin/sh\nprintf '%s\\n' fixture\n",
            "package/lib/stronk-pi-guard.py": b"print('fixture')\n",
            "package/src/index.mjs": b"export default function stronkPiFixture() {}\n",
            "package/package.json": f'{{"name":"stronk-pi","version":"{PLUGIN_VERSION}"}}\n'.encode(),
        },
    )
    write_tgz(symlink, {"package/link": b""}, symlink=True)
    write_tgz(hardlink, {"package/link": b""}, hardlink=True)

    good_sha = digest(good)
    good_size = good.stat().st_size
    good_manifest = base_manifest(Path("../artifacts") / good.name, good_sha, good_size)
    write_manifest("good-local.json", good_manifest)
    write_manifest(
        "good-https-artifact.json",
        base_https_manifest(
            f"https://github.com/{PLUGIN_REPO}/releases/download/{PLUGIN_TAG}/{PLUGIN_ASSET}",
            good_sha,
            good_size,
        ),
    )

    checksum = json.loads(json.dumps(good_manifest))
    checksum["artifacts"][0]["sha256"] = "0" * 64
    write_manifest("checksum-mismatch.json", checksum)

    missing = json.loads(json.dumps(good_manifest))
    missing["artifacts"][0]["artifactPath"] = "../artifacts/missing.tgz"
    write_manifest("missing-artifact.json", missing)

    floating = json.loads(json.dumps(good_manifest))
    floating["artifacts"][0]["version"] = "latest"
    write_manifest("latest-denied.json", floating)

    absolute = json.loads(json.dumps(good_manifest))
    absolute["artifacts"][0]["artifactPath"] = "/tmp/stronk-pi-plugin.tgz"
    write_manifest("absolute-path-denied.json", absolute)

    wrong = json.loads(json.dumps(good_manifest))
    wrong["artifacts"][0]["provenance"]["sourceCommit"] = "f" * 40
    write_manifest("wrong-provenance.json", wrong)

    missing_attestation = json.loads(json.dumps(good_manifest))
    missing_attestation["artifacts"][0].pop("attestation")
    write_manifest("missing-attestation.json", missing_attestation)

    compatibility = json.loads(json.dumps(good_manifest))
    compatibility["artifacts"][0]["compatibilityVersion"] = "stronkpi-setup-v2"
    write_manifest("compatibility-mismatch.json", compatibility)

    created_at = json.loads(json.dumps(good_manifest))
    created_at["artifacts"][0]["createdAt"] = "not-a-date"
    write_manifest("invalid-created-at.json", created_at)

    http_release = json.loads(json.dumps(good_manifest))
    http_release["artifacts"][0]["releaseUrl"] = f"http://github.com/{PLUGIN_REPO}/releases/tag/{PLUGIN_TAG}"
    write_manifest("http-release-url-denied.json", http_release)

    missing_provenance = json.loads(json.dumps(good_manifest))
    missing_provenance["artifacts"][0].pop("provenance")
    write_manifest("missing-provenance.json", missing_provenance)

    wrong_identity = base_manifest(
        Path("../artifacts") / wrong_package_identity.name,
        digest(wrong_package_identity),
        wrong_package_identity.stat().st_size,
    )
    write_manifest("wrong-package-identity.json", wrong_identity)

    missing_bundle = json.loads(json.dumps(good_manifest))
    missing_bundle.pop("bundle")
    write_manifest("missing-bundle.json", missing_bundle)

    floating_pin = json.loads(json.dumps(good_manifest))
    floating_pin["bundle"]["packagePins"]["subagents"]["version"] = "latest"
    write_manifest("floating-package-pin-denied.json", floating_pin)

    for filename, artifact in (
        ("archive-traversal-denied.json", traversal),
        ("symlink-escape-denied.json", symlink),
        ("hardlink-escape-denied.json", hardlink),
    ):
        manifest = base_manifest(Path("../artifacts") / artifact.name, digest(artifact), artifact.stat().st_size)
        write_manifest(filename, manifest)

    sums = [f"{digest(path)}  {path.name}" for path in sorted(ARTIFACT_DIR.glob("*.tgz"))]
    (ARTIFACT_DIR / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    (ARTIFACT_DIR / "BUILD-MANIFEST.json").write_text(
        json.dumps(
            {
                "createdAt": "2026-06-16T00:00:00Z",
                "sourceCommit": SOURCE_COMMIT,
                "artifacts": [path.name for path in sorted(ARTIFACT_DIR.glob("*.tgz"))],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
