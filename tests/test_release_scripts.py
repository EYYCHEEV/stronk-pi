#!/usr/bin/env python3
from __future__ import annotations

import json
import os
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
            original_guard_text = (tmp / "lib" / "stronk-pi-guard.py").read_text(encoding="utf-8")
            plugin_default_line = next(
                line for line in original_guard_text.splitlines() if line.startswith("DEFAULT_PLUGIN_VERSION = ")
            )

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
            self.assertIn(plugin_default_line, guard_text)
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

    def test_import_artifact_release_adds_intercom_artifact(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            for rel in (
                "scripts/import-artifact-release.py",
                "lib/stronk-pi-guard.py",
                "config/defaults.toml",
                "roles/stronk/roles.toml",
                "manifests/current.json",
                "tests/make_fixtures.py",
            ):
                copy_into_temp(tmp, rel)
            build_manifest = tmp / "BUILD-MANIFEST.json"
            build_manifest.write_text(
                json.dumps(
                    {
                        "sourceRepo": "EYYCHEEV/stronk-pi-intercom",
                        "tag": "stronk-pi-intercom-v0.6.0-stronk.1",
                        "artifact": "stronk-pi-intercom-0.6.0-stronk.1.tgz",
                        "sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
                        "byteSize": 45678,
                        "sourceCommit": "1234567890abcdef1234567890abcdef12345678",
                        "workflowRunId": "987654321",
                        "createdAt": "2026-06-29T00:00:00Z",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            proc = subprocess.run(
                [
                    sys.executable,
                    str(tmp / "scripts" / "import-artifact-release.py"),
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
            artifact = next(item for item in manifest["artifacts"] if item["name"] == "stronk-pi-intercom")
            self.assertEqual(artifact["version"], "0.6.0-stronk.1")
            self.assertEqual(artifact["sourceRepo"], "EYYCHEEV/stronk-pi-intercom")
            self.assertEqual(artifact["upstreamRepo"], "nicobailon/pi-intercom")
            self.assertEqual(artifact["seedPackage"], "pi-intercom")
            self.assertEqual(
                artifact["seedTarballSha256"],
                "76c0d5284661aac437248bb6c7a32879fe863296bd15cb533751b27cafc44818",
            )
            self.assertTrue(artifact["artifactUrl"].endswith("/stronk-pi-intercom-0.6.0-stronk.1.tgz"))
            self.assertEqual(
                manifest["bundle"]["packagePins"]["intercom"],
                {"name": "stronk-pi-intercom", "version": "0.6.0-stronk.1"},
            )
            defaults_text = (tmp / "config" / "defaults.toml").read_text(encoding="utf-8")
            fixtures_text = (tmp / "tests" / "make_fixtures.py").read_text(encoding="utf-8")
            self.assertIn('intercom = { name = "stronk-pi-intercom", version = "0.6.0-stronk.1" }', defaults_text)
            self.assertIn('INTERCOM_VERSION = "0.6.0-stronk.1"', fixtures_text)

    def test_offline_release_scripts_scrub_inherited_state_root_env(self):
        """Lock in that release/offline scripts scrub inherited Stronk state-root/dev-override
        env so release checks start from a scrubbed temp home and temp state root."""
        shared_scrub_line = (
            "unset STRONKPI_STATE_ROOT STRONK_PI_STATE_ROOT "
            "STRONKPI_DEV_OVERRIDES STRONK_PI_DEV_OVERRIDES STRONKPI_SETUP_ROOT"
        )
        for rel in ("tests/run_offline.sh", "scripts/verify-release-candidate.sh"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            with self.subTest(script=rel):
                self.assertIn("STRONKPI_NO_NETWORK=1", text)
                self.assertIn(shared_scrub_line, text, f"{rel} must scrub state-root env")
                # The broad scrub loop must target all three control-plane prefixes.
                for prefix in ("STRONK_", "STRONKPI_", "PI_"):
                    self.assertIn(prefix, text, f"{rel} must scrub {prefix}* prefix")

    def test_polluted_inherited_state_root_env_cannot_redirect_state_root_sensitive_test(self):
        """Regression: an inherited polluted Stronk state-root + dev-override env must not
        redirect a state-root-sensitive test's stronkpi-setup writes outside its temp root.
        The StronkEnvIsolationMixin scrubs inherited STRONK_*/STRONKPI_*/PI_* env around each
        test, so a live session's state root cannot disagree with a temp root or redirect
        stronkpi-setup writes. Spawning a single state-root-sensitive unittest (not the full
        suite) avoids run_offline.sh recursion while exercising the mixin under attack.
        """
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            escape_home = tmp / "escape-home"
            escape_state = escape_home / ".stronk-pi"
            escape_home.mkdir()
            env = dict(os.environ)
            env.update(
                {
                    "STRONK_PI_DEV_OVERRIDES": "1",
                    "STRONKPI_STATE_ROOT": str(escape_state),
                    "STRONK_PI_STATE_ROOT": str(escape_state),
                }
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "unittest",
                    "-q",
                    "tests.test_manifest_verifier.ManifestVerifierTests."
                    "test_refresh_config_command_installs_runtime_settings",
                ],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertFalse(
                escape_state.exists(),
                "polluted inherited state root redirected stronkpi-setup writes outside temp",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
