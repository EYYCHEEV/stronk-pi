#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = ROOT / "lib" / "stronk-pi-guard.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("stronk_pi_guard_under_test", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load guard from {GUARD_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


guard = load_guard()
PLUGIN_VERSION = guard.DEFAULT_PLUGIN_VERSION
PLUGIN_TAG = f"stronk-pi-plugin-v{PLUGIN_VERSION}"
PLUGIN_ASSET = f"stronk-pi-plugin-{PLUGIN_VERSION}.tgz"


class ManifestVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(ROOT / "tests" / "make_fixtures.py")], check=True)

    def manifest(self, name: str) -> Path:
        return ROOT / "tests" / "fixtures" / "manifests" / name

    def test_good_local_manifest_verifies(self):
        results = guard.verify_manifest(self.manifest("good-local.json"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "stronk-pi-plugin")

    def test_good_https_artifact_manifest_verifies_with_mocked_download(self):
        expected_url = (
            "https://github.com/EYYCHEEV/stronk-pi-plugin/releases/download/"
            f"{PLUGIN_TAG}/{PLUGIN_ASSET}"
        )

        class FakeResponse(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                self.close()
                return False

            def geturl(self):
                return expected_url

        old_getaddrinfo = guard.socket.getaddrinfo
        old_urlopen = guard.urllib.request.urlopen
        old_no_network = os.environ.get("STRONKPI_NO_NETWORK")
        fixture = ROOT / "tests" / "fixtures" / "artifacts" / PLUGIN_ASSET

        def fake_getaddrinfo(host, port, type=0):
            self.assertEqual(host, "github.com")
            return [(guard.socket.AF_INET, guard.socket.SOCK_STREAM, 6, "", ("140.82.112.3", port))]

        def fake_urlopen(request, timeout=30):
            self.assertEqual(timeout, 30)
            self.assertEqual(request.full_url, expected_url)
            return FakeResponse(fixture.read_bytes())

        try:
            os.environ.pop("STRONKPI_NO_NETWORK", None)
            guard.socket.getaddrinfo = fake_getaddrinfo
            guard.urllib.request.urlopen = fake_urlopen
            results = guard.verify_manifest(self.manifest("good-https-artifact.json"))
        finally:
            guard.socket.getaddrinfo = old_getaddrinfo
            guard.urllib.request.urlopen = old_urlopen
            if old_no_network is None:
                os.environ.pop("STRONKPI_NO_NETWORK", None)
            else:
                os.environ["STRONKPI_NO_NETWORK"] = old_no_network

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "stronk-pi-plugin")

    def assert_manifest_fails(self, name: str, text: str):
        with self.assertRaisesRegex(guard.StronkPiError, text):
            guard.verify_manifest(self.manifest(name))

    def test_checksum_mismatch_fails(self):
        self.assert_manifest_fails("checksum-mismatch.json", "checksum mismatch")

    def test_missing_artifact_fails_without_network_fallback(self):
        self.assert_manifest_fails("missing-artifact.json", "missing artifact")

    def test_floating_version_fails(self):
        self.assert_manifest_fails("latest-denied.json", "floating|mutable")

    def test_absolute_path_fails(self):
        self.assert_manifest_fails("absolute-path-denied.json", "absolute")

    def test_wrong_provenance_fails(self):
        self.assert_manifest_fails("wrong-provenance.json", "provenance")

    def test_wrong_internal_package_identity_fails(self):
        self.assert_manifest_fails("wrong-package-identity.json", "package name")

    def test_old_plugin_source_repo_fails(self):
        path = self.manifest("good-local.json")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        item = manifest["artifacts"][0]
        item["sourceRepo"] = "EYYCHEEV/stronk-pi"
        item["immutableTag"] = f"stronk-pi-v{PLUGIN_VERSION}"
        item["releaseUrl"] = f"https://github.com/EYYCHEEV/stronk-pi/releases/tag/stronk-pi-v{PLUGIN_VERSION}"
        item["provenance"]["sourceRepo"] = "EYYCHEEV/stronk-pi"
        item["provenance"]["immutableTag"] = f"stronk-pi-v{PLUGIN_VERSION}"
        with tempfile.NamedTemporaryFile("w", suffix=".json", dir=path.parent, delete=False, encoding="utf-8") as handle:
            json.dump(manifest, handle)
            temp_path = Path(handle.name)
        try:
            with self.assertRaisesRegex(guard.StronkPiError, "sourceRepo"):
                guard.verify_manifest(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_weak_manifest_metadata_fails(self):
        for name, expected in (
            ("missing-attestation.json", "attestation"),
            ("compatibility-mismatch.json", "compatibilityVersion"),
            ("invalid-created-at.json", "createdAt"),
            ("http-release-url-denied.json", "releaseUrl"),
            ("missing-provenance.json", "provenance"),
            ("missing-bundle.json", "bundle contract"),
            ("floating-package-pin-denied.json", "floating|mutable"),
        ):
            with self.subTest(name=name):
                self.assert_manifest_fails(name, expected)

    def test_archive_escape_fixtures_fail(self):
        for name, expected in (
            ("archive-traversal-denied.json", "traversal"),
            ("symlink-escape-denied.json", "links are denied"),
            ("hardlink-escape-denied.json", "links are denied"),
        ):
            with self.subTest(name=name):
                self.assert_manifest_fails(name, expected)

    def test_no_network_denies_remote_artifact(self):
        old = os.environ.get("STRONKPI_NO_NETWORK")
        os.environ["STRONKPI_NO_NETWORK"] = "1"
        try:
            with self.assertRaisesRegex(guard.StronkPiError, "NO_NETWORK"):
                guard.artifact_path(
                    self.manifest("good-local.json"),
                    {
                        "artifactUrl": f"https://github.com/EYYCHEEV/stronk-pi-plugin/releases/download/{PLUGIN_TAG}/a.tgz"
                    },
                )
        finally:
            if old is None:
                os.environ.pop("STRONKPI_NO_NETWORK", None)
            else:
                os.environ["STRONKPI_NO_NETWORK"] = old

    def test_harness_parser_passes_pi_flags_through(self):
        args = guard.parse_harness_args(["-p", "smoke", "--model", "kimi-coding/kimi-for-coding"])
        self.assertFalse(args.validate_only)
        self.assertEqual(args.pi_args, ["-p", "smoke", "--model", "kimi-coding/kimi-for-coding"])

    def test_harness_parser_blocks_validate_passthrough_mix(self):
        with self.assertRaisesRegex(guard.StronkPiError, "do not accept"):
            guard.parse_harness_args(["--validate-only", "-p", "smoke"])

    def test_harness_parser_blocks_controlled_pi_flags(self):
        for flag in ("--extension", "-e", "--session-dir=/tmp/sessions", "--provider"):
            with self.subTest(flag=flag):
                with self.assertRaisesRegex(guard.StronkPiError, "owned by stronkpi"):
                    guard.parse_harness_args([flag])

    def test_harness_control_env_blocks_external_guard_override(self):
        old_setup_root = os.environ.get("STRONKPI_SETUP_ROOT")
        old_state_root = os.environ.get("STRONKPI_STATE_ROOT")
        old_guard = os.environ.get("STRONK_PI_GUARD")
        old_code_hook = os.environ.get("STRONK_PI_CODEX_HOOK_COMMAND_JSON")
        old_dev = os.environ.get("STRONK_PI_DEV_OVERRIDES")
        try:
            os.environ["STRONK_PI_GUARD"] = "/tmp/fake-guard"
            os.environ.pop("STRONK_PI_DEV_OVERRIDES", None)
            with self.assertRaisesRegex(guard.StronkPiError, "STRONK_PI_GUARD"):
                guard.validate_harness_control_env()
            os.environ.pop("STRONK_PI_GUARD", None)
            os.environ["STRONK_PI_CODEX_HOOK_COMMAND_JSON"] = json.dumps(["/tmp/fake-helper"])
            with self.assertRaisesRegex(guard.StronkPiError, "STRONK_PI_CODEX_HOOK_COMMAND_JSON"):
                guard.validate_harness_control_env()
            os.environ.pop("STRONK_PI_CODEX_HOOK_COMMAND_JSON", None)
            os.environ["STRONKPI_SETUP_ROOT"] = "/tmp/fake-setup"
            with self.assertRaisesRegex(guard.StronkPiError, "STRONKPI_SETUP_ROOT"):
                guard.validate_harness_control_env()
            os.environ.pop("STRONKPI_SETUP_ROOT", None)
            os.environ["STRONKPI_STATE_ROOT"] = "/tmp/fake-state"
            with self.assertRaisesRegex(guard.StronkPiError, "STRONKPI_STATE_ROOT"):
                guard.validate_harness_control_env()
        finally:
            if old_setup_root is None:
                os.environ.pop("STRONKPI_SETUP_ROOT", None)
            else:
                os.environ["STRONKPI_SETUP_ROOT"] = old_setup_root
            if old_state_root is None:
                os.environ.pop("STRONKPI_STATE_ROOT", None)
            else:
                os.environ["STRONKPI_STATE_ROOT"] = old_state_root
            if old_guard is None:
                os.environ.pop("STRONK_PI_GUARD", None)
            else:
                os.environ["STRONK_PI_GUARD"] = old_guard
            if old_code_hook is None:
                os.environ.pop("STRONK_PI_CODEX_HOOK_COMMAND_JSON", None)
            else:
                os.environ["STRONK_PI_CODEX_HOOK_COMMAND_JSON"] = old_code_hook
            if old_dev is None:
                os.environ.pop("STRONK_PI_DEV_OVERRIDES", None)
            else:
                os.environ["STRONK_PI_DEV_OVERRIDES"] = old_dev

    def test_setup_and_state_root_env_require_dev_override(self):
        old_setup_root = os.environ.get("STRONKPI_SETUP_ROOT")
        old_state_root = os.environ.get("STRONKPI_STATE_ROOT")
        old_runtime_root = os.environ.get("STRONK_PI_STATE_ROOT")
        old_dev = os.environ.get("STRONK_PI_DEV_OVERRIDES")
        try:
            os.environ.pop("STRONK_PI_DEV_OVERRIDES", None)
            os.environ.pop("STRONK_PI_STATE_ROOT", None)
            os.environ["STRONKPI_SETUP_ROOT"] = "/tmp/fake-setup"
            with self.assertRaisesRegex(guard.StronkPiError, "STRONKPI_SETUP_ROOT"):
                guard.setup_root()
            os.environ.pop("STRONKPI_SETUP_ROOT", None)
            os.environ["STRONKPI_STATE_ROOT"] = "/tmp/fake-state"
            with self.assertRaisesRegex(guard.StronkPiError, "STRONKPI_STATE_ROOT"):
                guard.state_root()

            os.environ["STRONK_PI_DEV_OVERRIDES"] = "1"
            self.assertEqual(guard.state_root(), Path("/tmp/fake-state"))
        finally:
            if old_setup_root is None:
                os.environ.pop("STRONKPI_SETUP_ROOT", None)
            else:
                os.environ["STRONKPI_SETUP_ROOT"] = old_setup_root
            if old_state_root is None:
                os.environ.pop("STRONKPI_STATE_ROOT", None)
            else:
                os.environ["STRONKPI_STATE_ROOT"] = old_state_root
            if old_runtime_root is None:
                os.environ.pop("STRONK_PI_STATE_ROOT", None)
            else:
                os.environ["STRONK_PI_STATE_ROOT"] = old_runtime_root
            if old_dev is None:
                os.environ.pop("STRONK_PI_DEV_OVERRIDES", None)
            else:
                os.environ["STRONK_PI_DEV_OVERRIDES"] = old_dev

    def test_harness_environment_installs_setup_guard_helper(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            root = Path(tmp_name) / "state"
            env = guard.harness_environment(root)

            self.assertEqual(env["STRONK_PI_GUARD"], str(GUARD_PATH))
            self.assertEqual(env["STRONK_PI_SEARCH_PROVIDER"], "exa")
            self.assertEqual(env["STRONK_PI_SUBAGENT_FACADE"], "stronk")
            self.assertEqual(env["STRONK_PI_SUBAGENT_ADAPTER"], "intercom")
            self.assertEqual(json.loads(env["STRONK_PI_CODEX_HOOK_COMMAND_JSON"]), ["python3", str(GUARD_PATH), "codex-hook"])
            payload = {
                "session_id": "session-1",
                "turn_id": "turn-1",
                "transcript_path": "/tmp/transcript.jsonl",
                "cwd": str(ROOT),
                "hook_event_name": "UserPromptSubmit",
                "model": "deepseek/deepseek-v4-pro",
                "permission_mode": "default",
                "prompt": "ship it",
            }
            proc = subprocess.run(
                json.loads(env["STRONK_PI_CODEX_HOOK_COMMAND_JSON"]),
                input=json.dumps(payload),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                env=env,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            parsed = json.loads(proc.stdout)
            self.assertIs(parsed["continue"], True)
            self.assertEqual(parsed["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")

    def test_harness_environment_uses_runtime_harness_defaults(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            root = Path(tmp_name) / "state"
            config = root / "config"
            config.mkdir(parents=True)
            (config / "defaults.toml").write_text(
                "\n".join(
                    [
                        'managed_by = "stronk-pi"',
                        "[harness]",
                        'search_provider = "tavily"',
                        'subagent_facade = "stronk"',
                        'subagent_adapter = "dry-run"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            env = guard.harness_environment(root)

            self.assertEqual(env["STRONK_PI_SEARCH_PROVIDER"], "tavily")
            self.assertEqual(env["STRONK_PI_SUBAGENT_FACADE"], "stronk")
            self.assertEqual(env["STRONK_PI_SUBAGENT_ADAPTER"], "dry-run")

    def test_harness_environment_preserves_explicit_search_provider_override(self):
        old_provider = os.environ.get("STRONK_PI_SEARCH_PROVIDER")
        try:
            os.environ["STRONK_PI_SEARCH_PROVIDER"] = "brave"
            with tempfile.TemporaryDirectory() as tmp_name:
                env = guard.harness_environment(Path(tmp_name) / "state")
            self.assertEqual(env["STRONK_PI_SEARCH_PROVIDER"], "brave")
        finally:
            if old_provider is None:
                os.environ.pop("STRONK_PI_SEARCH_PROVIDER", None)
            else:
                os.environ["STRONK_PI_SEARCH_PROVIDER"] = old_provider

    def test_write_executable_script_replaces_symlink_not_target(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            target = tmp / "bin" / "stronkpi"
            linked_target = tmp / "linked-target"
            target.parent.mkdir()
            linked_target.write_text("old target\n", encoding="utf-8")
            target.symlink_to(linked_target)

            guard.write_executable_script(target, "#!/usr/bin/env python3\nprint('new')\n")

            self.assertFalse(target.is_symlink())
            self.assertTrue(os.access(target, os.X_OK))
            self.assertEqual(linked_target.read_text(encoding="utf-8"), "old target\n")

    def test_migrate_legacy_generated_agents_symlink(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            root = Path(tmp_name) / "state"
            legacy_target = Path(tmp_name) / "legacy-agents"
            (root / "agent").mkdir(parents=True)
            legacy_target.mkdir()
            (root / "agent" / "agents").symlink_to(legacy_target, target_is_directory=True)
            (root / "agent" / "AGENTS.md").symlink_to(Path(tmp_name) / "legacy-AGENTS.md")

            backups = guard.migrate_legacy_managed_symlinks(root, dry_run=False)

            self.assertEqual(len(backups), 2)
            self.assertFalse((root / "agent" / "agents").exists())
            self.assertFalse((root / "agent" / "AGENTS.md").exists())
            backup_text = "\n".join(path.read_text(encoding="utf-8").strip() for path in backups)
            self.assertIn(str(legacy_target), backup_text)
            self.assertIn(str(Path(tmp_name) / "legacy-AGENTS.md"), backup_text)

    def test_install_bundle_replaces_private_home_web_search_symlink(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            root = Path(tmp_name) / "state"
            legacy_target = Path(tmp_name) / "legacy-web-search.json"
            (root / "home" / ".pi").mkdir(parents=True)
            legacy_target.write_text("{}\n", encoding="utf-8")
            (root / "home" / ".pi" / "web-search.json").symlink_to(legacy_target)

            result = guard.install_bundle_defaults(root=root, dry_run=False)

            target = root / "home" / ".pi" / "web-search.json"
            self.assertFalse(target.is_symlink())
            self.assertTrue(target.is_file())
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), json.loads((ROOT / "config" / "pi" / "web-search.json").read_text(encoding="utf-8")))
            self.assertIn(str(target), result["changed"])
            backups = sorted((root / "runtime-backups").glob("*/home-.pi-web-search.json.symlink-target.txt"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8").strip(), str(legacy_target))

    def test_install_bundle_migrates_legacy_setup_managed_marker(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            root = Path(tmp_name) / "state"
            (root / "config").mkdir(parents=True)
            target = root / "config" / "defaults.toml"
            target.write_text('schema_version = 1\nmanaged_by = "stronk-pi-setup"\n', encoding="utf-8")

            result = guard.install_bundle_defaults(root=root, dry_run=False)

            self.assertIn(str(target), result["changed"])
            text = target.read_text(encoding="utf-8")
            self.assertIn('managed_by = "stronk-pi"', text)
            self.assertNotIn('managed_by = "stronk-pi-setup"', text)

    def test_install_bundle_refuses_unmanaged_defaults(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            root = Path(tmp_name) / "state"
            (root / "config").mkdir(parents=True)
            target = root / "config" / "defaults.toml"
            target.write_text("schema_version = 1\n", encoding="utf-8")

            with self.assertRaisesRegex(guard.StronkPiError, "refusing to overwrite unmanaged file"):
                guard.install_bundle_defaults(root=root, dry_run=False)

    def test_install_artifacts_replaces_existing_plugin_directory(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            artifact_root = tmp / "artifact-root"
            package_root = artifact_root / "package"
            package_root.mkdir(parents=True)
            (package_root / "package.json").write_text(
                json.dumps({"name": "stronk-pi-plugin", "version": PLUGIN_VERSION}) + "\n",
                encoding="utf-8",
            )
            (package_root / "new.txt").write_text("new\n", encoding="utf-8")
            archive_path = tmp / PLUGIN_ASSET
            with tarfile.open(archive_path, "w:gz") as archive:
                archive.add(package_root, arcname="package")

            state_root = tmp / "home" / ".stronk-pi"
            existing = state_root / "artifacts" / f"stronk-pi-plugin-{PLUGIN_VERSION}" / "package"
            existing.mkdir(parents=True)
            (existing / "old.txt").write_text("old\n", encoding="utf-8")
            env = os.environ.copy()
            env["HOME"] = str(tmp / "home")
            old_home = os.environ.get("HOME")
            try:
                os.environ["HOME"] = env["HOME"]
                guard.install_artifacts(
                    [
                        guard.ArtifactResult(
                            name="stronk-pi-plugin",
                            version=PLUGIN_VERSION,
                            path=archive_path,
                            sha256="test",
                            byte_size=archive_path.stat().st_size,
                        )
                    ],
                    dry_run=False,
                )
            finally:
                if old_home is None:
                    os.environ.pop("HOME", None)
                else:
                    os.environ["HOME"] = old_home

            installed = state_root / "artifacts" / f"stronk-pi-plugin-{PLUGIN_VERSION}" / "package"
            self.assertTrue((installed / "new.txt").is_file())
            self.assertFalse((installed / "old.txt").exists())

    def test_refresh_config_command_installs_runtime_settings(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(tmp / "home"),
                    "XDG_CONFIG_HOME": str(tmp / "xdg-config"),
                    "STRONKPI_NO_NETWORK": "1",
                }
            )
            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "stronkpi-setup"), "refresh-config", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                env=env,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["mode"], "refreshed")
            settings = json.loads((tmp / "home" / ".stronk-pi" / "agent" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(settings["defaultProvider"], "kimi-coding")
            self.assertEqual(settings["defaultModel"], "kimi-for-coding")
            self.assertEqual(settings["defaultThinkingLevel"], "xhigh")
            self.assertIn("kimi-coding/kimi-for-coding:xhigh", settings["enabledModels"])
            defaults = guard.load_toml_document(tmp / "home" / ".stronk-pi" / "config" / "defaults.toml")
            self.assertEqual(defaults["models"]["vision"], "kimi-coding/kimi-for-coding:xhigh")
            self.assertEqual(defaults["image_preflight"]["enabled"], True)
            self.assertEqual(defaults["image_preflight"]["model"], "kimi-coding/kimi-for-coding:xhigh")
            self.assertEqual(defaults["image_preflight"]["max_images"], 12)
            self.assertEqual(defaults["image_preflight"]["max_bytes"], 5242880)
            self.assertEqual(defaults["image_preflight"]["timeout_ms"], 90000)
            self.assertEqual(defaults["image_preflight"]["max_output_tokens"], 4096)
            self.assertEqual(defaults["image_preflight"]["failure_mode"], "soft")

    def test_import_codex_roles_autodiscovers_codex_home_roles(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            home = tmp / "home"
            source = home / ".codex" / "roles" / "stronk"
            source.mkdir(parents=True)
            actual_role = tmp / "custom-executor.toml"
            actual_role.write_text(
                "\n".join(
                    [
                        'model = "gpt-5.5"',
                        'model_reasoning_effort = "xhigh"',
                        'model_reasoning_summary = "auto"',
                        'developer_instructions = """',
                        "Role: custom executor for imported Codex role testing.",
                        "",
                        "Keep changes scoped and verified.",
                        '"""',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (source / "custom-executor.toml").symlink_to(actual_role)
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "XDG_CONFIG_HOME": str(tmp / "xdg-config"),
                    "STRONKPI_NO_NETWORK": "1",
                }
            )

            dry_run = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "stronkpi-setup"), "import-codex-roles", "--dry-run", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                env=env,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            dry_payload = json.loads(dry_run.stdout)
            self.assertTrue(dry_payload["dryRun"])
            self.assertEqual(dry_payload["importedRoles"], ["custom-executor"])
            self.assertFalse((home / ".stronk-pi").exists())

            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "stronkpi-setup"), "import-codex-roles", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["sourceDir"], str(source.resolve(strict=False)))
            self.assertEqual(payload["importedRoles"], ["custom-executor"])

            template = home / ".stronk-pi" / "config" / "role-templates" / "custom-executor.toml"
            generated = home / ".stronk-pi" / "agent" / "agents" / "custom-executor.md"
            template_text = template.read_text(encoding="utf-8")
            generated_text = generated.read_text(encoding="utf-8")
            self.assertIn('managed_by = "stronk-pi"', template_text)
            self.assertIn('codex_model = "gpt-5.5"', template_text)
            self.assertNotIn("model: gpt-5.5", generated_text)
            self.assertIn("You are the Pi adapter for the Stronk role `custom-executor`.", generated_text)

    def test_import_codex_roles_autodiscovers_agents_home_roles(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            home = tmp / "home"
            source = home / ".agents" / "roles" / "stronk"
            source.mkdir(parents=True)
            (source / "reviewer.toml").write_text(
                "\n".join(
                    [
                        'developer_instructions = """',
                        "Role: reviewer imported from the agents role directory.",
                        "",
                        "Inspect carefully and report concrete findings.",
                        '"""',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "XDG_CONFIG_HOME": str(tmp / "xdg-config"),
                    "STRONKPI_NO_NETWORK": "1",
                }
            )
            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "stronkpi-setup"), "import-codex-roles", "--dry-run", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                env=env,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["sourceDir"], str(source.resolve(strict=False)))
            self.assertEqual(payload["importedRoles"], ["reviewer"])
            self.assertTrue(payload["dryRun"])

    def test_imported_codex_role_survives_refresh_config(self):
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            home = tmp / "home"
            source = tmp / "codex-roles"
            source.mkdir()
            (source / "executor.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.5"',
                        'developer_instructions = """',
                        "Role: imported executor role that should survive refresh.",
                        "",
                        "This text proves refresh-config preserved the imported template.",
                        '"""',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "XDG_CONFIG_HOME": str(tmp / "xdg-config"),
                    "STRONKPI_NO_NETWORK": "1",
                }
            )
            import_proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "bin" / "stronkpi-setup"),
                    "import-codex-roles",
                    "--source",
                    str(source),
                    "--json",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                env=env,
            )
            self.assertEqual(import_proc.returncode, 0, import_proc.stderr)
            refresh_proc = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "stronkpi-setup"), "refresh-config", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                text=True,
                env=env,
            )
            self.assertEqual(refresh_proc.returncode, 0, refresh_proc.stderr)

            template = home / ".stronk-pi" / "config" / "role-templates" / "executor.toml"
            generated = home / ".stronk-pi" / "agent" / "agents" / "executor.md"
            template_text = template.read_text(encoding="utf-8")
            generated_text = generated.read_text(encoding="utf-8")
            self.assertIn('source_of_truth = "codex-role-toml"', template_text)
            self.assertIn('codex_model = "gpt-5.5"', template_text)
            self.assertIn("imported executor role that should survive refresh", generated_text)
            self.assertNotIn("model: gpt-5.5", generated_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
