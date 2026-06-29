#!/usr/bin/env python3
"""Import a released Stronk Pi artifact into the setup manifest."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    print(f"stronk-pi import-artifact-release: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_guard_module():
    guard_path = ROOT / "lib" / "stronk-pi-guard.py"
    spec = importlib.util.spec_from_file_location("stronk_pi_guard_import_release", guard_path)
    if spec is None or spec.loader is None:
        fail(f"unable to load guard module from {guard_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = load_guard_module()


def load_build_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("BUILD-MANIFEST.json must contain an object")
    return data


def require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"BUILD-MANIFEST.json missing non-empty {key}")
    return value.strip()


def require_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or value <= 0:
        fail(f"BUILD-MANIFEST.json {key} must be a positive integer")
    return value


def artifact_name_for_source(source_repo: str) -> str:
    matches = [
        name
        for name, expected in guard.EXPECTED_ARTIFACT_IDENTITIES.items()
        if expected.get("sourceRepo") == source_repo
    ]
    if len(matches) != 1:
        fail(f"sourceRepo is not a supported Stronk artifact repo: {source_repo}")
    return matches[0]


def parse_release(data: dict[str, Any]) -> dict[str, Any]:
    source_repo = require_string(data, "sourceRepo")
    name = artifact_name_for_source(source_repo)
    expected = guard.EXPECTED_ARTIFACT_IDENTITIES[name]

    tag = require_string(data, "tag")
    tag_prefix = expected["tagPrefix"]
    if not tag.startswith(tag_prefix):
        fail(f"tag must start with {tag_prefix}")
    version = tag.removeprefix(tag_prefix)
    if not VERSION_RE.fullmatch(version):
        fail(f"tag does not contain a valid semver: {tag}")

    artifact = require_string(data, "artifact")
    expected_artifact = f"{expected['assetPrefix']}{version}.tgz"
    if artifact != expected_artifact:
        fail(f"artifact must be {expected_artifact}")

    sha256 = require_string(data, "sha256")
    if not SHA256_RE.fullmatch(sha256):
        fail("sha256 must be a lowercase hex SHA-256 digest")

    source_commit = require_string(data, "sourceCommit")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        fail("sourceCommit must be a 40-character lowercase git SHA")

    workflow_run_id = str(data.get("workflowRunId") or "").strip()
    if not workflow_run_id:
        fail("workflowRunId is required")

    return {
        "name": name,
        "version": version,
        "tag": tag,
        "artifact": artifact,
        "byteSize": require_int(data, "byteSize"),
        "sha256": sha256,
        "sourceRepo": source_repo,
        "sourceCommit": source_commit,
        "workflowRunId": workflow_run_id,
        "createdAt": require_string(data, "createdAt"),
    }


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        fail(f"expected one match in {path.relative_to(ROOT)}")
    path.write_text(updated, encoding="utf-8")


def artifact_order(item: dict[str, Any]) -> int:
    order = ["stronk-pi-plugin", "stronk-pi-subagents", "stronk-pi-intercom"]
    try:
        return order.index(str(item.get("name")))
    except ValueError:
        return len(order)


def update_manifest(release: dict[str, Any], data: dict[str, Any]) -> None:
    manifest_path = ROOT / "manifests" / "current.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        fail("manifest artifacts must be a list")
    matches = [item for item in artifacts if isinstance(item, dict) and item.get("name") == release["name"]]
    if len(matches) > 1:
        fail(f"manifest contains multiple {release['name']} artifacts")
    if matches:
        item = matches[0]
    else:
        item = {"name": release["name"]}
        artifacts.append(item)
        artifacts.sort(key=artifact_order)

    release_url = f"https://github.com/{release['sourceRepo']}/releases/tag/{release['tag']}"
    artifact_url = f"https://github.com/{release['sourceRepo']}/releases/download/{release['tag']}/{release['artifact']}"
    attestation = f"github-attestation:{release['sourceRepo']}/{release['artifact']}@sha256:{release['sha256']}"
    expected = guard.EXPECTED_ARTIFACT_IDENTITIES[release["name"]]
    metadata = {
        field: data.get(field) or expected[field]
        for field in guard.ARTIFACT_PROVENANCE_METADATA_FIELDS
        if field in expected
    }
    item.clear()
    item.update(
        {
            "name": release["name"],
            "version": release["version"],
            "sourceRepo": release["sourceRepo"],
            "sourceCommit": release["sourceCommit"],
            "immutableTag": release["tag"],
            "releaseUrl": release_url,
            "artifactUrl": artifact_url,
            "sha256": release["sha256"],
            "byteSize": release["byteSize"],
            "workflowRunId": release["workflowRunId"],
            "attestation": attestation,
            "compatibilityVersion": guard.BUNDLE_CONTRACT_VERSION,
            "createdAt": release["createdAt"],
            **metadata,
            "provenance": {
                "sourceRepo": release["sourceRepo"],
                "sourceCommit": release["sourceCommit"],
                "immutableTag": release["tag"],
                "workflowRunId": release["workflowRunId"],
                **metadata,
            },
        }
    )

    pins = manifest.get("bundle", {}).get("packagePins")
    if not isinstance(pins, dict):
        fail("manifest bundle.packagePins must be an object")
    if release["name"] == "stronk-pi-subagents":
        pins["subagents"] = {"name": release["name"], "version": release["version"]}
    elif release["name"] == "stronk-pi-intercom":
        pins["intercom"] = {"name": release["name"], "version": release["version"]}

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def update_version_surfaces(release: dict[str, Any]) -> None:
    name = release["name"]
    version = release["version"]
    if name == "stronk-pi-plugin":
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
    elif name == "stronk-pi-subagents":
        replace_once(
            ROOT / "lib" / "stronk-pi-guard.py",
            r'^    "subagents": \("stronk-pi-subagents", "[^"]+"\),$',
            f'    "subagents": ("stronk-pi-subagents", "{version}"),',
        )
        replace_once(
            ROOT / "config" / "defaults.toml",
            r'^subagents = \{ name = "stronk-pi-subagents", version = "[^"]+" \}$',
            f'subagents = {{ name = "stronk-pi-subagents", version = "{version}" }}',
        )
        replace_once(
            ROOT / "tests" / "make_fixtures.py",
            r'^SUBAGENTS_VERSION = "[^"]+"$',
            f'SUBAGENTS_VERSION = "{version}"',
        )
    elif name == "stronk-pi-intercom":
        replace_once(
            ROOT / "lib" / "stronk-pi-guard.py",
            r'^    "intercom": \("stronk-pi-intercom", "[^"]+"\),$',
            f'    "intercom": ("stronk-pi-intercom", "{version}"),',
        )
        replace_once(
            ROOT / "config" / "defaults.toml",
            r'^intercom = \{ name = "stronk-pi-intercom", version = "[^"]+" \}$',
            f'intercom = {{ name = "stronk-pi-intercom", version = "{version}" }}',
        )
        replace_once(
            ROOT / "tests" / "make_fixtures.py",
            r'^INTERCOM_VERSION = "[^"]+"$',
            f'INTERCOM_VERSION = "{version}"',
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_manifest", help="Path to BUILD-MANIFEST.json from a Stronk artifact release")
    parser.add_argument("--no-regenerate-fixtures", action="store_true")
    args = parser.parse_args(argv)

    build_manifest = Path(args.build_manifest).expanduser()
    if not build_manifest.is_absolute():
        build_manifest = (Path.cwd() / build_manifest).resolve()

    data = load_build_manifest(build_manifest)
    release = parse_release(data)

    update_manifest(release, data)
    update_version_surfaces(release)

    if not args.no_regenerate_fixtures:
        subprocess.run([sys.executable, str(ROOT / "tests" / "make_fixtures.py")], check=True)

    print(f"stronk-pi import-artifact-release: {release['name']} {release['version']}")
    print("manifest=manifests/current.json")
    print(f"fixtures_regenerated={not args.no_regenerate_fixtures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
