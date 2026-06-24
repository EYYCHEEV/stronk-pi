#!/usr/bin/env python3
"""Bump the Stronk Pi setup/distribution version surfaces."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def fail(message: str) -> None:
    print(f"stronk-pi bump-version: {message}", file=sys.stderr)
    raise SystemExit(1)


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        fail(f"expected one match in {path.relative_to(ROOT)}")
    path.write_text(updated, encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        fail("usage: python3 scripts/bump-version.py <semver>")
    version = argv[1]
    if not VERSION_RE.fullmatch(version):
        fail(f"invalid semver: {version}")

    replace_once(
        ROOT / "lib" / "stronk-pi-guard.py",
        r'^VERSION = "[^"]+"$',
        f'VERSION = "{version}"',
    )

    plugin_json = ROOT / ".codex-plugin" / "plugin.json"
    if plugin_json.is_file():
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
        data["version"] = version
        plugin_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    print(f"stronk-pi bump-version: {version}")
    print("note: plugin artifact version is imported separately with scripts/import-plugin-release.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
