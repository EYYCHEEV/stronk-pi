#!/usr/bin/env python3
from __future__ import annotations

import os
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_VERSION = "0.1.0"
PLUGIN_SOURCE_ROOT = Path(os.environ.get("STRONK_PI_PLUGIN_SOURCE_ROOT", ROOT.parent / "stronk-pi-plugin"))
INSTALLED_PLUGIN_ROOT = Path(
    os.environ.get(
        "STRONK_PI_INSTALLED_PLUGIN_ROOT",
        Path.home() / ".stronk-pi" / "artifacts" / f"stronk-pi-plugin-{PLUGIN_VERSION}" / "package",
    )
)
FIXTURE_ARCHIVE = ROOT / "tests" / "fixtures" / "artifacts" / f"stronk-pi-plugin-{PLUGIN_VERSION}.tgz"


class PluginStateRootTests(unittest.TestCase):
    def assert_plugin_contract(self, index_text: str, ledger_text: str, label: str) -> None:
        self.assertIn("firstString(env.STRONK_PI_STATE_ROOT) || '~/.stronk-pi'", index_text, label)
        self.assertIn("join(stateRoot, 'agent', 'sessions')", index_text, label)
        self.assertIn("join(stronkStateRoot(), 'agent', 'sessions')", index_text, label)
        self.assertIn("process.env.STRONK_PI_STATE_ROOT || join(homedir(), '.stronk-pi')", ledger_text, label)
        banned = [
            "STRONK_PI_PRIVATE_HOME",
            ".stronk-pi/home",
            "'.stronk-pi', 'home'",
            '"home/.pi"',
            "'home/.pi'",
            "join(homedir(), '.pi')",
            "~/.pi",
        ]
        combined = index_text + "\n" + ledger_text
        for marker in banned:
            with self.subTest(label=label, marker=marker):
                self.assertNotIn(marker, combined)

    def assert_plugin_root_contract(self, plugin_root: Path, label: str) -> None:
        index_path = plugin_root / "src" / "index.mjs"
        ledger_path = plugin_root / "src" / "subagents" / "ledger.mjs"
        self.assertTrue(index_path.is_file(), f"{label}: missing {index_path}")
        self.assertTrue(ledger_path.is_file(), f"{label}: missing {ledger_path}")
        self.assert_plugin_contract(
            index_path.read_text(encoding="utf-8"),
            ledger_path.read_text(encoding="utf-8"),
            label,
        )

    def test_fixture_plugin_artifact_honors_state_root_when_contract_files_exist(self):
        self.assertTrue(FIXTURE_ARCHIVE.is_file(), f"missing fixture archive: {FIXTURE_ARCHIVE}")
        with tarfile.open(FIXTURE_ARCHIVE, "r:gz") as archive:
            index_member = archive.extractfile("package/src/index.mjs")
            self.assertIsNotNone(index_member)
            assert index_member is not None
            index_text = index_member.read().decode("utf-8")
            try:
                ledger_member = archive.extractfile("package/src/subagents/ledger.mjs")
            except KeyError:
                ledger_member = None
            if ledger_member is None or "STRONK_PI_STATE_ROOT" not in index_text:
                self.skipTest("fixture artifact is a minimal manifest-verifier package")
            self.assert_plugin_contract(
                index_text,
                ledger_member.read().decode("utf-8"),
                "fixture artifact",
            )

    def test_adjacent_plugin_source_honors_state_root_when_available(self):
        if not PLUGIN_SOURCE_ROOT.exists():
            self.skipTest(f"plugin source not available: {PLUGIN_SOURCE_ROOT}")
        self.assert_plugin_root_contract(PLUGIN_SOURCE_ROOT, "plugin source")

    def test_active_installed_plugin_artifact_honors_state_root_when_available(self):
        if not INSTALLED_PLUGIN_ROOT.exists():
            self.skipTest(f"installed plugin artifact not available: {INSTALLED_PLUGIN_ROOT}")
        self.assert_plugin_root_contract(INSTALLED_PLUGIN_ROOT, "installed plugin artifact")


if __name__ == "__main__":
    unittest.main(verbosity=2)
