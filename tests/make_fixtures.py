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
        "artifacts": [
            {
                "name": "stronk-pi-plugin",
                "version": "0.1.0",
                "sourceRepo": "EYYCHEEV/stronk-pi",
                "sourceCommit": SOURCE_COMMIT,
                "immutableTag": "stronk-pi-v0.1.0",
                "releaseUrl": "https://github.com/EYYCHEEV/stronk-pi/releases/tag/stronk-pi-v0.1.0",
                "artifactPath": rel.as_posix(),
                "sha256": sha,
                "byteSize": size,
                "workflowRunId": "fixture-run-1",
                "attestation": "fixture-attestation",
                "sbom": "fixture-sbom",
                "compatibilityVersion": "stronkpi-setup-v1",
                "createdAt": "2026-06-16T00:00:00Z",
                "provenance": {
                    "sourceRepo": "EYYCHEEV/stronk-pi",
                    "sourceCommit": SOURCE_COMMIT,
                    "immutableTag": "stronk-pi-v0.1.0",
                    "workflowRunId": "fixture-run-1"
                }
            }
        ]
    }


def base_https_manifest(artifact_url: str, sha: str, size: int) -> dict:
    manifest = base_manifest(Path("../artifacts/stronk-pi-plugin-0.1.0.tgz"), sha, size)
    item = manifest["artifacts"][0]
    item.pop("artifactPath")
    item["artifactUrl"] = artifact_url
    return manifest


def write_manifest(name: str, data: dict) -> None:
    (MANIFEST_DIR / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    good = ARTIFACT_DIR / "stronk-pi-plugin-0.1.0.tgz"
    traversal = ARTIFACT_DIR / "archive-traversal.tgz"
    symlink = ARTIFACT_DIR / "symlink-escape.tgz"
    hardlink = ARTIFACT_DIR / "hardlink-escape.tgz"

    write_tgz(
        good,
        {
            "package/bin/stronkpi": b"#!/usr/bin/env zsh\nprint -r -- fixture\n",
            "package/lib/stronk-pi-guard.py": b"print('fixture')\n",
            "package/package.json": b'{"name":"stronk-pi-plugin","version":"0.1.0"}\n',
        },
    )
    write_tgz(traversal, {"../escape": b"bad\n"})
    write_tgz(symlink, {"package/link": b""}, symlink=True)
    write_tgz(hardlink, {"package/link": b""}, hardlink=True)

    good_sha = digest(good)
    good_size = good.stat().st_size
    good_manifest = base_manifest(Path("../artifacts") / good.name, good_sha, good_size)
    write_manifest("good-local.json", good_manifest)
    write_manifest(
        "good-https-artifact.json",
        base_https_manifest(
            "https://github.com/EYYCHEEV/stronk-pi/releases/download/stronk-pi-v0.1.0/stronk-pi-plugin-0.1.0.tgz",
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
    http_release["artifacts"][0]["releaseUrl"] = "http://github.com/EYYCHEEV/stronk-pi/releases/tag/stronk-pi-v0.1.0"
    write_manifest("http-release-url-denied.json", http_release)

    missing_provenance = json.loads(json.dumps(good_manifest))
    missing_provenance["artifacts"][0].pop("provenance")
    write_manifest("missing-provenance.json", missing_provenance)

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
