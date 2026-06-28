#!/usr/bin/env python3
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = [
    ROOT / "README.md",
    ROOT / "SECURITY.md",
    ROOT / ".agents",
    ROOT / "install.sh",
    ROOT / "bin",
    ROOT / "lib",
    ROOT / "config",
    ROOT / "docs",
    ROOT / "manifests",
    ROOT / "roles",
    ROOT / "scripts",
    ROOT / "templates",
    ROOT / ".codex-plugin",
    ROOT / ".github",
]

PUBLIC_EXCLUDED_PREFIXES = [
    "docs/exec-plans/active/",
]

FORBIDDEN_SIMPLE = [
    "agentic-workstation",
    "STRONK_PI_PLUGIN_REPO",
    "~/.agents/stronk",
    "pi-core/.pi/agent",
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
    re.compile("/" + "Users" + r"/[A-Za-z0-9._-]+"),
    re.compile("Documents" + "/" + "Work" + "/" + "Dev" + "/" + "repos"),
    re.compile(r"['\"]/Users/['\"]\s*\+"),
    re.compile(r"['\"]/home/['\"]\s*\+"),
]

PRIVATE_HOME_MIGRATION_MARKERS = [
    "~/.stronk-pi/home",
    ".stronk-pi/home",
    "STRONK_PI_PRIVATE_HOME",
    "home/.pi",
    "root / \"home\"",
    "private_home",
]

PRIVATE_HOME_ALLOWED_PATTERNS = {
    "lib/stronk-pi-guard.py": [
        re.compile(r"real_home_write_risks"),
        re.compile(r"\+ \[str\(root / \"home\"\)\]"),
        re.compile(r"private_home_cleanup"),
        re.compile(r"private_home_cache_like_path"),
        re.compile(r"plan_private_home_cleanup"),
        re.compile(r"apply_private_home_cleanup"),
        re.compile(r"cleanup_private_home"),
        re.compile(r"obsolete private home"),
        re.compile(r"obsolete_home = root / \"home\""),
        re.compile(r"not \(root / \"home\"\)\.exists\(\)"),
        re.compile(r"cleanup-private-home"),
    ],
}


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
    return sorted(
        path for path in set(files)
        if not any(path.relative_to(ROOT).as_posix().startswith(prefix) for prefix in PUBLIC_EXCLUDED_PREFIXES)
    )


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

    def test_no_default_runtime_private_home_markers(self):
        offenders: list[str] = []
        for path in public_files():
            rel = path.relative_to(ROOT).as_posix()
            allowed = PRIVATE_HOME_ALLOWED_PATTERNS.get(rel, [])
            for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if not any(marker in line for marker in PRIVATE_HOME_MIGRATION_MARKERS):
                    continue
                if any(pattern.search(line) for pattern in allowed):
                    continue
                if "legacy" in line.lower() or "obsolete private home" in line.lower():
                    continue
                if rel.endswith(".md") and any(
                    phrase in line.lower()
                    for phrase in (
                        "old development",
                        "must not create",
                        "does not create",
                        "should not create",
                    )
                ):
                    continue
                offenders.append(f"{rel}:{lineno}: {line.strip()}")
        self.assertEqual(offenders, [])

    def test_no_tracked_generated_role_markdown(self):
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in public_files()
            if path.suffix == ".md"
            and (
                path.match("config/pi/agent/agents/*.md")
                or "Generated at runtime by stronkpi-setup" in path.read_text(encoding="utf-8", errors="ignore")
                or "Generated by stronk-role-sync" in path.read_text(encoding="utf-8", errors="ignore")
            )
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
