#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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


class McpDoctorTests(unittest.TestCase):
    def write_registry(self, directory: Path, body: str) -> Path:
        registry = directory / "registry.toml"
        registry.write_text(body.strip() + "\n", encoding="utf-8")
        return registry

    def write_tools(self, directory: Path, body: str) -> Path:
        tools = directory / ".mcp-tools"
        tools.write_text(body.strip() + "\n", encoding="utf-8")
        return tools

    def write_empty_tools(self, directory: Path) -> Path:
        return self.write_tools(directory, "")

    def test_valid_registry_and_selected_tool_pass(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            registry = self.write_registry(
                tmp,
                """
                version = 1

                [servers.example]
                command = "python3"
                args = ["-c", "print('ok')"]
                env_vars = ["STRONKPI_TEST_MCP_KEY"]
                env = { STRONKPI_TEST_MODE = "fixture" }
                """,
            )
            tools = self.write_tools(tmp, "example")
            with patch.dict(os.environ, {"STRONKPI_TEST_MCP_KEY": "set"}, clear=False):
                result = guard.validate_mcp_registry(registry, tools_path=tools)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["selectedTools"], ["example"])

    def test_user_owned_registry_symlink_passes(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            target = self.write_registry(
                tmp,
                """
                version = 1

                [servers.example]
                command = "python3"
                args = []
                """,
            )
            registry = tmp / "linked-registry.toml"
            registry.symlink_to(target)
            result = guard.validate_mcp_registry(registry, tools_path=self.write_empty_tools(tmp))
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["symlink"])
        self.assertEqual(result["serverCount"], 1)

    def test_missing_selected_env_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            registry = self.write_registry(
                tmp,
                """
                version = 1

                [servers.example]
                command = "python3"
                args = []
                env_vars = ["STRONKPI_TEST_MISSING_KEY"]
                """,
            )
            tools = self.write_tools(tmp, "example")
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("STRONKPI_TEST_MISSING_KEY", None)
                result = guard.validate_mcp_registry(registry, tools_path=tools)
        self.assertFalse(result["ok"])
        self.assertIn("selected env var is missing", "\n".join(result["errors"]))

    def test_unknown_selected_tool_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            registry = self.write_registry(
                tmp,
                """
                version = 1

                [servers.example]
                command = "python3"
                args = []
                """,
            )
            tools = self.write_tools(tmp, "missing")
            result = guard.validate_mcp_registry(registry, tools_path=tools)
        self.assertFalse(result["ok"])
        self.assertIn("selected tool is not in registry", "\n".join(result["errors"]))

    def test_floating_mcp_package_ref_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            registry = self.write_registry(
                tmp,
                """
                version = 1

                [servers.example]
                command = "python3"
                args = ["mcp-remote@latest"]
                """,
            )
            result = guard.validate_mcp_registry(registry, tools_path=self.write_empty_tools(tmp))
        self.assertFalse(result["ok"])
        self.assertIn("floating", "\n".join(result["errors"]))

    def test_javascript_path_is_not_floating_ref(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            script = tmp / "dist" / "index.js"
            script.parent.mkdir()
            script.write_text("console.log('ok')\n", encoding="utf-8")
            registry = self.write_registry(
                tmp,
                f"""
                version = 1

                [servers.example]
                command = "python3"
                args = ["{script}"]
                """,
            )
            result = guard.validate_mcp_registry(registry, tools_path=self.write_empty_tools(tmp))
        self.assertTrue(result["ok"], result)

    def test_personal_path_markers_fail_generically(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            macos_home_command = "/" + "Users" + "/example/bin/mcp-server"
            linux_home_arg = "/" + "home" + "/example/.local/share/server.js"
            registry = self.write_registry(
                tmp,
                f"""
                version = 1

                [servers.example]
                command = "{macos_home_command}"
                args = ["{linux_home_arg}"]
                """,
            )
            result = guard.validate_mcp_registry(registry, tools_path=self.write_empty_tools(tmp))
        self.assertFalse(result["ok"])
        errors = "\n".join(result["errors"])
        self.assertIn("command contains a personal path", errors)
        self.assertIn("arg contains a personal path", errors)

    def test_inline_secret_env_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            registry = self.write_registry(
                tmp,
                """
                version = 1

                [servers.example]
                command = "python3"
                args = []
                env = { EXAMPLE_API_KEY = "sk-aaaaaaaaaaaaaaaaaaaaaaaa" }
                """,
            )
            result = guard.validate_mcp_registry(registry, tools_path=self.write_empty_tools(tmp))
        self.assertFalse(result["ok"])
        errors = "\n".join(result["errors"])
        self.assertIn("secret-like key", errors)
        self.assertIn("secret-like value", errors)

    def test_doctor_entrypoint_reports_mcp_registry(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            registry = self.write_registry(
                tmp,
                """
                version = 1

                [servers.example]
                command = "python3"
                args = ["-c", "print('ok')"]
                """,
            )
            tools = self.write_empty_tools(tmp)
            env = os.environ.copy()
            env["STRONKPI_NO_NETWORK"] = "1"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "bin" / "stronkpi-setup"),
                    "doctor",
                    "--json",
                    "--mcp-registry",
                    str(registry),
                    "--mcp-tools",
                    str(tools),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mcpRegistry"]["serverCount"], 1)


class McpAdapterRuntimeTests(unittest.TestCase):
    def write_registry(self, directory: Path, body: str) -> Path:
        registry = directory / "registry.toml"
        registry.write_text(body.strip() + "\n", encoding="utf-8")
        return registry

    def write_tools(self, directory: Path, body: str) -> Path:
        tools = directory / ".mcp-tools"
        tools.write_text(body.strip() + "\n", encoding="utf-8")
        return tools

    def write_adapter_package(self, root: Path) -> Path:
        package = root / "agent" / "npm" / "node_modules" / "pi-mcp-adapter"
        package.mkdir(parents=True)
        (package / "package.json").write_text(
            json.dumps({"name": "pi-mcp-adapter", "version": "2.9.0", "pi": {"extensions": ["./index.ts"]}}) + "\n",
            encoding="utf-8",
        )
        (package / "index.ts").write_text("export default function adapter() {}\n", encoding="utf-8")
        return package

    def write_runtime_defaults(self, root: Path) -> None:
        target = root / "config" / "defaults.toml"
        target.parent.mkdir(parents=True)
        target.write_text((ROOT / "config" / "defaults.toml").read_text(encoding="utf-8"), encoding="utf-8")

    def test_adapter_config_uses_selected_servers_and_env_placeholders(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            registry = self.write_registry(
                tmp,
                """
                version = 1

                [servers.selected]
                command = "python3"
                args = ["-m", "selected"]
                env_vars = ["STRONKPI_TEST_SECRET"]
                env = { STRONKPI_TEST_MODE = "fixture" }

                [servers.unselected]
                command = "python3"
                args = ["-m", "unselected"]
                """,
            )

            config = guard.build_mcp_adapter_config(registry, ["selected"])

        self.assertEqual(sorted(config["mcpServers"].keys()), ["selected"])
        selected = config["mcpServers"]["selected"]
        self.assertEqual(selected["lifecycle"], "lazy")
        self.assertEqual(selected["env"]["STRONKPI_TEST_SECRET"], "${STRONKPI_TEST_SECRET}")
        self.assertEqual(selected["env"]["STRONKPI_TEST_MODE"], "fixture")
        self.assertFalse(config["settings"]["directTools"])

    def test_prepare_runtime_writes_config_and_launch_args(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            xdg = tmp / "xdg"
            project.mkdir()
            (xdg / "mcp").mkdir(parents=True)
            self.write_runtime_defaults(root)
            adapter = self.write_adapter_package(root)
            registry = self.write_registry(
                xdg / "mcp",
                """
                version = 1

                [servers.example]
                command = "python3"
                args = ["-c", "print('ok')"]
                env_vars = ["STRONKPI_TEST_SECRET"]
                """,
            )
            self.write_tools(project, "example")
            with patch.dict(
                os.environ,
                {
                    "XDG_CONFIG_HOME": str(xdg),
                    "STRONKPI_TEST_SECRET": "actual-secret-value",
                },
                clear=False,
            ):
                status = guard.prepare_mcp_adapter_runtime(root, cwd=project)

            config_path = root / "agent" / "mcp.json"
            config_text = config_path.read_text(encoding="utf-8")
            launch_args = guard.build_pi_launch_args(
                plugin_path=root / "artifacts" / "stronk-pi-plugin-0.1.0" / "package" / "src" / "index.mjs",
                session_dir=root / "agent" / "sessions",
                mcp_status=status,
            )

        self.assertTrue(status["enabled"])
        self.assertEqual(status["adapterPath"], str(adapter))
        self.assertEqual(status["selectedTools"], ["example"])
        self.assertNotIn("actual-secret-value", config_text)
        self.assertIn("${STRONKPI_TEST_SECRET}", config_text)
        self.assertIn("--mcp-config", launch_args)
        self.assertIn(str(config_path), launch_args)
        self.assertEqual(launch_args.count("--extension"), 2)
        self.assertEqual(str(registry), status["registryPath"])

    def test_prepare_runtime_rejects_project_mcp_configs(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            xdg = tmp / "xdg"
            project.mkdir()
            (xdg / "mcp").mkdir(parents=True)
            self.write_runtime_defaults(root)
            self.write_adapter_package(root)
            self.write_registry(
                xdg / "mcp",
                """
                version = 1

                [servers.example]
                command = "python3"
                args = []
                """,
            )
            self.write_tools(project, "example")
            (project / ".mcp.json").write_text('{"mcpServers":{"bypass":{"command":"python3"}}}\n', encoding="utf-8")

            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}, clear=False):
                with self.assertRaisesRegex(guard.StronkPiError, "bypass the Stronk selected-server boundary"):
                    guard.prepare_mcp_adapter_runtime(root, cwd=project)

    def test_prepare_runtime_fails_closed_when_adapter_missing(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            xdg = tmp / "xdg"
            project.mkdir()
            (xdg / "mcp").mkdir(parents=True)
            self.write_runtime_defaults(root)
            self.write_registry(
                xdg / "mcp",
                """
                version = 1

                [servers.example]
                command = "python3"
                args = []
                """,
            )
            self.write_tools(project, "example")

            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}, clear=False):
                with self.assertRaisesRegex(guard.StronkPiError, "MCP adapter package missing"):
                    guard.prepare_mcp_adapter_runtime(root, cwd=project)

    def test_prepare_runtime_is_disabled_without_selected_tools(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            project.mkdir()
            self.write_runtime_defaults(root)

            status = guard.prepare_mcp_adapter_runtime(root, cwd=project)

        self.assertFalse(status["configured"])
        self.assertFalse(status["enabled"])
        self.assertFalse((root / "agent" / "mcp.json").exists())

    def test_stronkpi_entrypoint_launches_with_mcp_adapter(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            xdg = tmp / "xdg"
            project.mkdir()
            (xdg / "mcp").mkdir(parents=True)
            self.write_adapter_package(root)
            plugin_path = root / "artifacts" / "stronk-pi-plugin-0.1.0" / "package" / "src" / "index.mjs"
            plugin_path.parent.mkdir(parents=True)
            plugin_path.write_text("export default function plugin() {}\n", encoding="utf-8")
            pi_binary = root / "pi-fork-runtime" / "node_modules" / ".bin" / "pi"
            pi_binary.parent.mkdir(parents=True)
            pi_binary.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env python3",
                        "import json, os, pathlib, sys",
                        "root = pathlib.Path(os.environ['STRONK_PI_STATE_ROOT'])",
                        "(root / 'launch-argv.json').write_text(json.dumps(sys.argv[1:]) + '\\n', encoding='utf-8')",
                        "(root / 'pi-agent-dir.txt').write_text(os.environ['PI_CODING_AGENT_DIR'] + '\\n', encoding='utf-8')",
                        "(root / 'pi-offline.txt').write_text(os.environ.get('PI_OFFLINE', '') + '\\n', encoding='utf-8')",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            pi_binary.chmod(0o755)
            registry = self.write_registry(
                xdg / "mcp",
                """
                version = 1

                [servers.example]
                command = "python3"
                args = ["-c", "print('mcp smoke')"]
                env_vars = ["STRONKPI_SMOKE_SECRET"]
                env = { STRONKPI_SMOKE_MODE = "live" }
                """,
            )
            self.write_tools(project, "example")
            env = os.environ.copy()
            env.update(
                {
                    "STRONK_PI_DEV_OVERRIDES": "1",
                    "STRONKPI_STATE_ROOT": str(root),
                    "XDG_CONFIG_HOME": str(xdg),
                    "STRONKPI_SMOKE_SECRET": "do-not-write-me",
                    "STRONKPI_NO_NETWORK": "1",
                }
            )

            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "stronkpi")],
                cwd=project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
            )

            config_text = (root / "agent" / "mcp.json").read_text(encoding="utf-8")
            config = json.loads(config_text)
            launch_args = json.loads((root / "launch-argv.json").read_text(encoding="utf-8"))
            agent_dir_text = (root / "pi-agent-dir.txt").read_text(encoding="utf-8").strip()
            offline_text = (root / "pi-offline.txt").read_text(encoding="utf-8").strip()

        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(config["mcpServers"]["example"]["env"]["STRONKPI_SMOKE_SECRET"], "${STRONKPI_SMOKE_SECRET}")
        self.assertEqual(config["mcpServers"]["example"]["env"]["STRONKPI_SMOKE_MODE"], "live")
        self.assertNotIn("do-not-write-me", config_text)
        self.assertEqual(sorted(config["mcpServers"].keys()), ["example"])
        self.assertEqual(launch_args.count("--extension"), 2)
        self.assertIn("--mcp-config", launch_args)
        self.assertIn(str(root / "agent" / "mcp.json"), launch_args)
        self.assertIn("--offline", launch_args)
        self.assertEqual(agent_dir_text, str(root / "agent"))
        self.assertEqual(offline_text, "1")
        self.assertEqual(str(registry), str(xdg / "mcp" / "registry.toml"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
