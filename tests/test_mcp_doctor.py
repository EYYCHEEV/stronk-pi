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
            result = guard.validate_mcp_registry(registry)
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
            result = guard.validate_mcp_registry(registry)
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
            result = guard.validate_mcp_registry(registry)
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
            result = guard.validate_mcp_registry(registry)
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
            result = guard.validate_mcp_registry(registry)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
