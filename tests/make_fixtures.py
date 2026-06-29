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
PLUGIN_VERSION = "0.2.3"
PLUGIN_TAG = f"stronk-pi-plugin-v{PLUGIN_VERSION}"
PLUGIN_ASSET = f"stronk-pi-plugin-{PLUGIN_VERSION}.tgz"
SUBAGENTS_REPO = "EYYCHEEV/stronk-pi-subagents"
SUBAGENTS_VERSION = "0.22.0-stronk.5"
SUBAGENTS_TAG = f"stronk-pi-subagents-v{SUBAGENTS_VERSION}"
SUBAGENTS_ASSET = f"stronk-pi-subagents-{SUBAGENTS_VERSION}.tgz"
SUBAGENTS_UPSTREAM_REPO = "nicobailon/pi-subagents"
SUBAGENTS_UPSTREAM_VERSION = "0.22.0"
SUBAGENTS_UPSTREAM_COMMIT = "1fd371d2a068458741a15507edc6cd49a9807486"
INTERCOM_REPO = "EYYCHEEV/stronk-pi-intercom"
INTERCOM_VERSION = "0.6.0-stronk.1"
INTERCOM_TAG = f"stronk-pi-intercom-v{INTERCOM_VERSION}"
INTERCOM_ASSET = f"stronk-pi-intercom-{INTERCOM_VERSION}.tgz"
INTERCOM_UPSTREAM_REPO = "nicobailon/pi-intercom"
INTERCOM_UPSTREAM_VERSION = "0.6.0"
INTERCOM_UPSTREAM_COMMIT = "5caa4aa1bd060cf0aebbf1a5dfbb1abb6e23e457"
INTERCOM_SEED_TYPE = "npm-tarball"
INTERCOM_SEED_PACKAGE = "pi-intercom"
INTERCOM_SEED_VERSION = "0.6.0"
INTERCOM_SEED_TARBALL_URL = "https://registry.npmjs.org/pi-intercom/-/pi-intercom-0.6.0.tgz"
INTERCOM_SEED_TARBALL_SHA256 = "76c0d5284661aac437248bb6c7a32879fe863296bd15cb533751b27cafc44818"
INTERCOM_SOURCE_ARCHIVE_SHA256 = "3ce238f4a75ce9c66ad76766ee878ef19dd83eef620739b73fe08e35c84311c6"


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
            "mcp_adapter": {"name": "pi-mcp-adapter", "version": "2.9.0"},
            "subagents": {"name": "stronk-pi-subagents", "version": SUBAGENTS_VERSION},
            "intercom": {"name": "stronk-pi-intercom", "version": INTERCOM_VERSION},
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


def github_attestation(repo: str, asset: str, sha: str) -> str:
    return f"github-attestation:{repo}/{asset}@sha256:{sha}"


def plugin_artifact(artifact_path: Path, sha: str, size: int) -> dict:
    rel = artifact_path if not artifact_path.is_absolute() else artifact_path.relative_to(MANIFEST_DIR)
    return {
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
        "attestation": github_attestation(PLUGIN_REPO, PLUGIN_ASSET, sha),
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


def subagents_artifact(artifact_path: Path, sha: str, size: int) -> dict:
    rel = artifact_path if not artifact_path.is_absolute() else artifact_path.relative_to(MANIFEST_DIR)
    return {
        "name": "stronk-pi-subagents",
        "version": SUBAGENTS_VERSION,
        "sourceRepo": SUBAGENTS_REPO,
        "sourceCommit": SOURCE_COMMIT,
        "immutableTag": SUBAGENTS_TAG,
        "releaseUrl": f"https://github.com/{SUBAGENTS_REPO}/releases/tag/{SUBAGENTS_TAG}",
        "artifactPath": rel.as_posix(),
        "sha256": sha,
        "byteSize": size,
        "workflowRunId": "fixture-run-subagents",
        "attestation": github_attestation(SUBAGENTS_REPO, SUBAGENTS_ASSET, sha),
        "compatibilityVersion": "stronkpi-setup-v1",
        "createdAt": "2026-06-16T00:00:00Z",
        "upstreamRepo": SUBAGENTS_UPSTREAM_REPO,
        "upstreamVersion": SUBAGENTS_UPSTREAM_VERSION,
        "upstreamCommit": SUBAGENTS_UPSTREAM_COMMIT,
        "provenance": {
            "sourceRepo": SUBAGENTS_REPO,
            "sourceCommit": SOURCE_COMMIT,
            "immutableTag": SUBAGENTS_TAG,
            "workflowRunId": "fixture-run-subagents",
            "upstreamRepo": SUBAGENTS_UPSTREAM_REPO,
            "upstreamVersion": SUBAGENTS_UPSTREAM_VERSION,
            "upstreamCommit": SUBAGENTS_UPSTREAM_COMMIT
        }
    }


def intercom_artifact(artifact_path: Path, sha: str, size: int) -> dict:
    rel = artifact_path if not artifact_path.is_absolute() else artifact_path.relative_to(MANIFEST_DIR)
    return {
        "name": "stronk-pi-intercom",
        "version": INTERCOM_VERSION,
        "sourceRepo": INTERCOM_REPO,
        "sourceCommit": SOURCE_COMMIT,
        "immutableTag": INTERCOM_TAG,
        "releaseUrl": f"https://github.com/{INTERCOM_REPO}/releases/tag/{INTERCOM_TAG}",
        "artifactPath": rel.as_posix(),
        "sha256": sha,
        "byteSize": size,
        "workflowRunId": "fixture-run-intercom",
        "attestation": github_attestation(INTERCOM_REPO, INTERCOM_ASSET, sha),
        "compatibilityVersion": "stronkpi-setup-v1",
        "createdAt": "2026-06-16T00:00:00Z",
        "upstreamRepo": INTERCOM_UPSTREAM_REPO,
        "upstreamVersion": INTERCOM_UPSTREAM_VERSION,
        "upstreamCommit": INTERCOM_UPSTREAM_COMMIT,
        "seedType": INTERCOM_SEED_TYPE,
        "seedPackage": INTERCOM_SEED_PACKAGE,
        "seedVersion": INTERCOM_SEED_VERSION,
        "seedTarballUrl": INTERCOM_SEED_TARBALL_URL,
        "seedTarballSha256": INTERCOM_SEED_TARBALL_SHA256,
        "sourceArchiveSha256": INTERCOM_SOURCE_ARCHIVE_SHA256,
        "provenance": {
            "sourceRepo": INTERCOM_REPO,
            "sourceCommit": SOURCE_COMMIT,
            "immutableTag": INTERCOM_TAG,
            "workflowRunId": "fixture-run-intercom",
            "upstreamRepo": INTERCOM_UPSTREAM_REPO,
            "upstreamVersion": INTERCOM_UPSTREAM_VERSION,
            "upstreamCommit": INTERCOM_UPSTREAM_COMMIT,
            "seedType": INTERCOM_SEED_TYPE,
            "seedPackage": INTERCOM_SEED_PACKAGE,
            "seedVersion": INTERCOM_SEED_VERSION,
            "seedTarballUrl": INTERCOM_SEED_TARBALL_URL,
            "seedTarballSha256": INTERCOM_SEED_TARBALL_SHA256,
            "sourceArchiveSha256": INTERCOM_SOURCE_ARCHIVE_SHA256,
        }
    }


def base_manifest(
    plugin_path: Path,
    plugin_sha: str,
    plugin_size: int,
    subagents_path: Path,
    subagents_sha: str,
    subagents_size: int,
    intercom_path: Path,
    intercom_sha: str,
    intercom_size: int,
) -> dict:
    return {
        "schemaVersion": 1,
        "compatibilityVersion": "stronkpi-setup-v1",
        "bundle": bundle_contract(),
        "artifacts": [
            plugin_artifact(plugin_path, plugin_sha, plugin_size),
            subagents_artifact(subagents_path, subagents_sha, subagents_size),
            intercom_artifact(intercom_path, intercom_sha, intercom_size),
        ]
    }


def base_https_manifest(
    artifact_url: str,
    plugin_sha: str,
    plugin_size: int,
    subagents_path: Path,
    subagents_sha: str,
    subagents_size: int,
    intercom_path: Path,
    intercom_sha: str,
    intercom_size: int,
) -> dict:
    manifest = base_manifest(
        Path("../artifacts") / PLUGIN_ASSET,
        plugin_sha,
        plugin_size,
        subagents_path,
        subagents_sha,
        subagents_size,
        intercom_path,
        intercom_sha,
        intercom_size,
    )
    item = manifest["artifacts"][0]
    item.pop("artifactPath")
    item["artifactUrl"] = artifact_url
    item["workflowRunId"] = "123456789"
    item["provenance"]["workflowRunId"] = "123456789"
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
    subagents = ARTIFACT_DIR / SUBAGENTS_ASSET
    subagents_stub = ARTIFACT_DIR / "stronk-pi-subagents-stub.tgz"
    intercom = ARTIFACT_DIR / INTERCOM_ASSET
    intercom_stub = ARTIFACT_DIR / "stronk-pi-intercom-stub.tgz"

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
    write_tgz(
        subagents,
        {
            "package/package.json": (
                json.dumps(
                    {
                        "name": "stronk-pi-subagents",
                        "version": SUBAGENTS_VERSION,
                        "pi": {"extensions": ["./src/extension/index.ts"]},
                    },
                    sort_keys=True,
                )
                + "\n"
            ).encode(),
            "package/src/extension/index.ts": b"export default function subagents() {}\n",
            "package/src/agents/agents.ts": b"export function discoverAgents() { return []; }\n",
            "package/src/agents/skills.ts": b"export function discoverAvailableSkills() { return []; }\n",
            "package/src/agents/user-agent-dir.ts": b"export function resolveUserAgentDir() { return process.env.PI_CODING_AGENT_DIR || ''; }\n",
            "package/agents/delegate.md": b"---\nname: delegate\ndescription: delegate\n---\n",
            "package/agents/worker.md": b"---\nname: worker\ndescription: worker\n---\n",
            "package/skills/stronkpi-agents/SKILL.md": b"---\ndescription: Stronk Pi subagent swarm orchestration\n---\n",
        },
    )
    write_tgz(
        subagents_stub,
        {
            "package/package.json": (
                json.dumps({"name": "stronk-pi-subagents", "version": SUBAGENTS_VERSION}, sort_keys=True) + "\n"
            ).encode(),
        },
    )
    write_tgz(
        intercom,
        {
            "package/package.json": (
                json.dumps(
                    {
                        "name": "stronk-pi-intercom",
                        "version": INTERCOM_VERSION,
                        "pi": {"extensions": ["./index.ts"], "skills": ["./skills"]},
                    },
                    sort_keys=True,
                )
                + "\n"
            ).encode(),
            "package/index.ts": b"export default function intercom() {}\n",
            "package/config.ts": b"export const configPath = 'state-root-aware';\n",
            "package/types.ts": b"export type Intercom = object;\n",
            "package/state-root.ts": b"export function getStronkStateRoot() { return ''; }\n",
            "package/reply-tracker.ts": b"export class ReplyTracker {}\n",
            "package/broker/broker.ts": b"export function broker() {}\n",
            "package/broker/client.ts": b"export function client() {}\n",
            "package/broker/framing.ts": b"export function frame() {}\n",
            "package/broker/paths.ts": b"export function paths() {}\n",
            "package/broker/spawn.ts": b"export function spawnBroker() {}\n",
            "package/ui/compose.ts": b"export function compose() {}\n",
            "package/ui/inline-message.ts": b"export function inlineMessage() {}\n",
            "package/ui/session-list.ts": b"export function sessionList() {}\n",
            "package/skills/stronk-pi-intercom/SKILL.md": b"---\ndescription: Stronk Pi intercom\n---\n",
        },
    )
    write_tgz(
        intercom_stub,
        {
            "package/package.json": (
                json.dumps({"name": "stronk-pi-intercom", "version": INTERCOM_VERSION}, sort_keys=True) + "\n"
            ).encode(),
        },
    )

    good_sha = digest(good)
    good_size = good.stat().st_size
    subagents_sha = digest(subagents)
    subagents_size = subagents.stat().st_size
    intercom_sha = digest(intercom)
    intercom_size = intercom.stat().st_size
    good_manifest = base_manifest(
        Path("../artifacts") / good.name,
        good_sha,
        good_size,
        Path("../artifacts") / subagents.name,
        subagents_sha,
        subagents_size,
        Path("../artifacts") / intercom.name,
        intercom_sha,
        intercom_size,
    )
    write_manifest("good-local.json", good_manifest)
    write_manifest(
        "good-https-artifact.json",
        base_https_manifest(
            f"https://github.com/{PLUGIN_REPO}/releases/download/{PLUGIN_TAG}/{PLUGIN_ASSET}",
            good_sha,
            good_size,
            Path("../artifacts") / subagents.name,
            subagents_sha,
            subagents_size,
            Path("../artifacts") / intercom.name,
            intercom_sha,
            intercom_size,
        ),
    )

    checksum = json.loads(json.dumps(good_manifest))
    checksum["artifacts"][0]["sha256"] = "0" * 64
    checksum["artifacts"][0]["attestation"] = github_attestation(PLUGIN_REPO, PLUGIN_ASSET, "0" * 64)
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
        Path("../artifacts") / subagents.name,
        subagents_sha,
        subagents_size,
        Path("../artifacts") / intercom.name,
        intercom_sha,
        intercom_size,
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
        manifest = base_manifest(
            Path("../artifacts") / artifact.name,
            digest(artifact),
            artifact.stat().st_size,
            Path("../artifacts") / subagents.name,
            subagents_sha,
            subagents_size,
            Path("../artifacts") / intercom.name,
            intercom_sha,
            intercom_size,
        )
        write_manifest(filename, manifest)

    subagents_stub_manifest = json.loads(json.dumps(good_manifest))
    stub_sha = digest(subagents_stub)
    stub_item = subagents_artifact(
        Path("../artifacts") / subagents_stub.name,
        stub_sha,
        subagents_stub.stat().st_size,
    )
    subagents_stub_manifest["artifacts"][1] = stub_item
    write_manifest("subagents-stub-denied.json", subagents_stub_manifest)

    intercom_stub_manifest = json.loads(json.dumps(good_manifest))
    intercom_stub_sha = digest(intercom_stub)
    intercom_stub_item = intercom_artifact(
        Path("../artifacts") / intercom_stub.name,
        intercom_stub_sha,
        intercom_stub.stat().st_size,
    )
    intercom_stub_manifest["artifacts"][2] = intercom_stub_item
    write_manifest("intercom-stub-denied.json", intercom_stub_manifest)

    missing_intercom = json.loads(json.dumps(good_manifest))
    missing_intercom["artifacts"] = missing_intercom["artifacts"][:2]
    missing_intercom["bundle"]["packagePins"]["intercom"] = {"name": "pi-intercom", "version": "0.6.0"}
    write_manifest("legacy-intercom-only-denied.json", missing_intercom)

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
