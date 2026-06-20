#!/usr/bin/env python3
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = [
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / "install.sh",
    ROOT / "bin",
    ROOT / "lib",
    ROOT / "config",
    ROOT / "docs",
    ROOT / "manifests",
    ROOT / "templates",
    ROOT / ".codex-plugin",
    ROOT / ".github",
]

FORBIDDEN_SIMPLE = [
    "agentic-workstation",
    "STRONK_PI_DEV_OVERRIDES",
    "STRONK_PI_PLUGIN_REPO",
    "curl | sh",
    "curl|sh",
    "curl | bash",
    "wget | sh",
    "unsafe eval",
    "latest",
    "@latest",
    "releases/latest",
    "curl | sh",
    "curl|sh",
    "curl | bash",
    "wget | sh",
    "unsafe eval",
    "/bin/zsh",
    "env zsh",
    "zsh -n",
    "zsh tests/",
    "run_offline.zsh",
    "test_install_dry_run.zsh",
    "test_dogfood.zsh",
    "Ensure zsh",
]

ALLOWED_SUBSTRINGS = {
    "lib/stronk-pi-guard.py": [
        "latest",
        "@latest",
        "file:",
    ],
}

COMMAND_PATTERNS = [
    re.compile(r"`(?:sp|pi)`"),
    re.compile(r"(^|[\s;|&])(?:sp|pi)(?:\s|$)"),
]

CONSTRUCTED_PRIVATE_PATH_PATTERNS = [
    re.compile(r"['\"]/Users/['\"]\s*\+"),
    re.compile(r"['\"]/home/['\"]\s*\+"),
]


def public_files() -> list[Path]:
    files: list[Path] = []
    for path in PUBLIC_PATHS:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(
                item for item in path.rglob("*")
                if item.is_file() and "__pycache__" not in item.parts
            )
    return sorted(set(files))


class PublicSurfaceTests(unittest.TestCase):
    def test_no_forbidden_public_strings(self):
        offenders: list[str] = []
        for path in public_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = path.relative_to(ROOT).as_posix()
            for forbidden in FORBIDDEN_SIMPLE:
                if forbidden in ALLOWED_SUBSTRINGS.get(rel, []):
                    continue
                if forbidden in text:
                    offenders.append(f"{rel}: {forbidden}")
            if "upgrade-pi" in text:
                offenders.append(f"{rel}: maintainer command name")
        self.assertEqual(offenders, [])

    def test_no_public_short_command_surface(self):
        offenders: list[str] = []
        for path in public_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = path.relative_to(ROOT).as_posix()
            for pattern in COMMAND_PATTERNS:
                if pattern.search(text):
                    offenders.append(f"{rel}: {pattern.pattern}")
        self.assertEqual(offenders, [])

    def test_no_constructed_private_path_markers(self):
        offenders: list[str] = []
        for path in public_files():
            text = path.read_text(encoding="utf-8", errors="ignore")
            rel = path.relative_to(ROOT).as_posix()
            for pattern in CONSTRUCTED_PRIVATE_PATH_PATTERNS:
                if pattern.search(text):
                    offenders.append(f"{rel}: {pattern.pattern}")
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
