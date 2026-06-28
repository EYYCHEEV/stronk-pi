#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def copy_into_temp(root: Path, rel: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / rel, target)


class ReleaseScriptTests(unittest.TestCase):
    def test_project_scope_release_skill_points_at_release_commands(self):
        skill = ROOT / ".agents" / "skills" / "stronk-pi-release" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        self.assertIn("name: stronk-pi-release", text)
        self.assertIn("python3 scripts/bump-version.py <version>", text)
        self.assertIn("python3 scripts/import-plugin-release.py", text)
        self.assertIn("STRONKPI_NO_NETWORK=1 sh scripts/verify-release-candidate.sh", text)
        self.assertIn("release attestation has been", text)
        self.assertIn("Rollback And Recovery", text)

        evals = json.loads(
            (ROOT / ".agents" / "skills" / "stronk-pi-release" / "evals" / "evals.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(evals["skill_name"], "stronk-pi-release")
        self.assertGreaterEqual(len(evals["evals"]), 4)

    def test_bump_version_updates_setup_only(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            for rel in (
                "scripts/bump-version.py",
                "lib/stronk-pi-guard.py",
                ".codex-plugin/plugin.json",
            ):
                copy_into_temp(tmp, rel)

            proc = subprocess.run(
                [sys.executable, str(tmp / "scripts" / "bump-version.py"), "0.2.0"],
                cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            guard_text = (tmp / "lib" / "stronk-pi-guard.py").read_text(encoding="utf-8")
            plugin = json.loads((tmp / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
            self.assertIn('VERSION = "0.2.0"', guard_text)
            self.assertIn('DEFAULT_PLUGIN_VERSION = "0.2.0"', guard_text)
            self.assertEqual(plugin["version"], "0.2.0")

    def test_import_plugin_release_updates_distribution_surfaces(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            for rel in (
                "scripts/import-plugin-release.py",
                "lib/stronk-pi-guard.py",
                "roles/stronk/roles.toml",
                "manifests/current.json",
                "tests/make_fixtures.py",
            ):
                copy_into_temp(tmp, rel)
            build_manifest = tmp / "BUILD-MANIFEST.json"
            build_manifest.write_text(
                json.dumps(
                    {
                        "sourceRepo": "EYYCHEEV/stronk-pi-plugin",
                        "tag": "stronk-pi-plugin-v0.2.0",
                        "artifact": "stronk-pi-plugin-0.2.0.tgz",
                        "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                        "byteSize": 12345,
                        "sourceCommit": "abcdef0123456789abcdef0123456789abcdef01",
                        "workflowRunId": "123456789",
                        "createdAt": "2026-06-23T00:00:00Z",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    str(tmp / "scripts" / "import-plugin-release.py"),
                    str(build_manifest),
                    "--no-regenerate-fixtures",
                ],
                cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            manifest = json.loads((tmp / "manifests" / "current.json").read_text(encoding="utf-8"))
            artifact = manifest["artifacts"][0]
            self.assertEqual(artifact["version"], "0.2.0")
            self.assertEqual(artifact["sourceRepo"], "EYYCHEEV/stronk-pi-plugin")
            self.assertEqual(artifact["immutableTag"], "stronk-pi-plugin-v0.2.0")
            self.assertTrue(artifact["artifactUrl"].endswith("/stronk-pi-plugin-0.2.0.tgz"))
            self.assertEqual(artifact["provenance"]["sourceCommit"], "abcdef0123456789abcdef0123456789abcdef01")

            guard_text = (tmp / "lib" / "stronk-pi-guard.py").read_text(encoding="utf-8")
            roles_text = (tmp / "roles" / "stronk" / "roles.toml").read_text(encoding="utf-8")
            fixtures_text = (tmp / "tests" / "make_fixtures.py").read_text(encoding="utf-8")
            self.assertIn('DEFAULT_PLUGIN_VERSION = "0.2.0"', guard_text)
            self.assertIn("stronk-pi-plugin-0.2.0/package/src/index.mjs", roles_text)
            self.assertIn('PLUGIN_VERSION = "0.2.0"', fixtures_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
