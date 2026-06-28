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
SUBAGENTS_PACKAGE = "stronk-pi-subagents"
SUBAGENTS_VERSION = "0.22.0-stronk.4"


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

    def test_mcp_tools_file_must_be_regular_owned_and_not_writable(self):
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
            target = self.write_tools(tmp, "example")
            linked = tmp / "linked-tools"
            linked.symlink_to(target)
            result = guard.validate_mcp_registry(registry, tools_path=linked)
            self.assertFalse(result["ok"])
            self.assertIn("must not be a symlink", "\n".join(result["errors"]))

            directory_tools = tmp / "directory-tools"
            directory_tools.mkdir()
            result = guard.validate_mcp_registry(registry, tools_path=directory_tools)
            self.assertFalse(result["ok"])
            self.assertIn("regular file", "\n".join(result["errors"]))

            target.chmod(0o620)
            result = guard.validate_mcp_registry(registry, tools_path=target)
            self.assertFalse(result["ok"])
            self.assertIn("group-writable", "\n".join(result["errors"]))

            target.chmod(0o602)
            result = guard.validate_mcp_registry(registry, tools_path=target)
            self.assertFalse(result["ok"])
            self.assertIn("world-writable", "\n".join(result["errors"]))

            target.chmod(0o600)
            result = guard.validate_mcp_registry(registry, tools_path=target)
            self.assertTrue(result["ok"], result)

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

    def write_runtime_package(self, root: Path, name: str, version: str) -> Path:
        package = root / "agent" / "npm" / "node_modules" / name
        package.mkdir(parents=True)
        (package / "package.json").write_text(
            json.dumps({"name": name, "version": version, "pi": {"extensions": ["./index.ts"]}}) + "\n",
            encoding="utf-8",
        )
        (package / "index.ts").write_text("export default function extension() {}\n", encoding="utf-8")
        if name == SUBAGENTS_PACKAGE:
            required_files = {
                "src/extension/index.ts": "export default function subagents() {}\n",
                "src/agents/agents.ts": "export function discoverAgents() { return []; }\n",
                "src/agents/skills.ts": "export function discoverAvailableSkills() { return []; }\n",
                "src/agents/user-agent-dir.ts": "export function resolveUserAgentDir() { return ''; }\n",
                "agents/delegate.md": "---\nname: delegate\ndescription: delegate\n---\n",
                "agents/worker.md": "---\nname: worker\ndescription: worker\n---\n",
                "skills/stronkpi-agents/SKILL.md": "---\ndescription: Stronk Pi subagent swarm orchestration\n---\n",
            }
            for relative, content in required_files.items():
                target = package / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
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
            home = tmp / "home"
            xdg = tmp / "xdg"
            xdg_cache = tmp / "xdg-cache"
            project.mkdir()
            home.mkdir()
            (xdg / "mcp").mkdir(parents=True)
            xdg_cache.mkdir()
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

            config_path = guard.project_generated_mcp_config_path(project, root)
            config_text = config_path.read_text(encoding="utf-8")
            config_mode = config_path.stat().st_mode & 0o777
            project_mcp_exists = (project / ".mcp.json").is_file()
            launch_args = guard.build_pi_launch_args(
                plugin_path=root / "artifacts" / f"stronk-pi-plugin-{guard.DEFAULT_PLUGIN_VERSION}" / "package" / "src" / "index.mjs",
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
        self.assertEqual(config_path, project.resolve(strict=False) / ".mcp.json")
        self.assertEqual(config_mode, 0o600)
        self.assertEqual(launch_args.count("--extension"), 2)
        self.assertEqual(str(registry), status["registryPath"])
        self.assertFalse((root / "agent" / "mcp.json").exists())
        self.assertTrue(project_mcp_exists)

    def test_subagent_runtime_launch_args_include_intercom_extensions(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            self.write_runtime_defaults(root)
            subagents = self.write_runtime_package(root, SUBAGENTS_PACKAGE, SUBAGENTS_VERSION)
            intercom = self.write_runtime_package(root, "pi-intercom", "0.6.0")

            status = guard.prepare_subagent_runtime(root)
            inspected = guard.inspect_subagent_runtime(root)
            launch_args = guard.build_pi_launch_args(
                plugin_path=root / "artifacts" / f"stronk-pi-plugin-{guard.DEFAULT_PLUGIN_VERSION}" / "package" / "src" / "index.mjs",
                session_dir=root / "agent" / "sessions",
                subagent_status=status,
            )
            bridge_link = root / "agent" / "extensions" / "pi-intercom"
            bridge_is_symlink = bridge_link.is_symlink()
            bridge_target = bridge_link.resolve()

        self.assertTrue(status["enabled"])
        self.assertEqual(status["packages"]["subagents"]["packageName"], SUBAGENTS_PACKAGE)
        self.assertEqual(status["packages"]["subagents"]["packageVersion"], SUBAGENTS_VERSION)
        self.assertEqual(status["packages"]["intercom"]["packageName"], "pi-intercom")
        self.assertEqual(status["packages"]["intercom"]["packageVersion"], "0.6.0")
        self.assertEqual(status["extensionPaths"], [str(subagents), str(intercom)])
        self.assertEqual(status["intercomBridgePath"], str(bridge_link))
        self.assertTrue(status["intercomBridgeLinked"])
        self.assertTrue(inspected["intercomBridgeLinked"])
        self.assertTrue(bridge_is_symlink)
        self.assertEqual(bridge_target, intercom.resolve())
        self.assertEqual(launch_args.count("--extension"), 3)
        self.assertIn(str(subagents), launch_args)
        self.assertIn(str(intercom), launch_args)
        self.assertIn("--exclude-tools", launch_args)
        self.assertIn("subagent", launch_args)
        self.assertLess(launch_args.index(str(intercom)), launch_args.index("--exclude-tools"))
        self.assertIn("--exclude-tools", guard.CONTROLLED_PI_FLAGS)
        self.assertIn("-xt", guard.CONTROLLED_PI_FLAGS)

    def test_subagent_runtime_launch_args_hide_raw_subagent_tool(self):
        launch_args = guard.build_pi_launch_args(
            plugin_path=Path("/tmp/plugin/src/index.mjs"),
            session_dir=Path("/tmp/session"),
            subagent_status={
                "enabled": True,
                "extensionPaths": ["/tmp/stronk-pi-subagents", "/tmp/pi-intercom"],
            },
        )

        self.assertIn("--exclude-tools", launch_args)
        self.assertIn("subagent", launch_args)
        self.assertEqual(launch_args[launch_args.index("--exclude-tools") + 1], "subagent")
        with self.assertRaisesRegex(guard.StronkPiError, "flag is owned by stronkpi"):
            guard.validate_pi_passthrough_args(["--exclude-tools", "subagent"])
        with self.assertRaisesRegex(guard.StronkPiError, "flag is owned by stronkpi"):
            guard.validate_pi_passthrough_args(["--exclude-tools=subagent"])
        with self.assertRaisesRegex(guard.StronkPiError, "flag is owned by stronkpi"):
            guard.validate_pi_passthrough_args(["-xt", "subagent"])

    def test_diagnose_json_reports_linked_subagent_runtime(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            subagents = self.write_runtime_package(root, SUBAGENTS_PACKAGE, SUBAGENTS_VERSION)
            intercom = self.write_runtime_package(root, "pi-intercom", "0.6.0")
            env = os.environ.copy()
            env.update(
                {
                    "STRONK_PI_DEV_OVERRIDES": "1",
                    "STRONKPI_STATE_ROOT": str(root),
                }
            )

            proc = subprocess.run(
                [sys.executable, str(ROOT / "bin" / "stronkpi"), "--diagnose", "--json"],
                cwd=tmp,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                check=False,
            )

            payload = json.loads(proc.stdout)

        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertTrue(payload["ok"], payload)
        self.assertEqual(payload["effectiveHome"], str(Path(env.get("HOME", str(Path.home()))).expanduser().resolve(strict=False)))
        self.assertEqual(payload["stateRoot"], str(root))
        self.assertEqual(payload["configRoot"], str(root / "config"))
        self.assertEqual(payload["cacheRoot"], str(root / "cache"))
        self.assertEqual(payload["logRoot"], str(root / "logs"))
        self.assertEqual(payload["tmpRoot"], str(root / "tmp"))
        self.assertEqual(payload["agentDir"], str(root / "agent"))
        self.assertEqual(payload["sessionDir"], str(root / "agent" / "sessions"))
        self.assertEqual(payload["mcpConfigPath"], str(tmp.resolve(strict=False) / ".mcp.json"))
        self.assertEqual(payload["intercomBridgePath"], str(root / "agent" / "extensions" / "pi-intercom"))
        self.assertIn(str(root / "home"), payload["blockedRealHomeWriteRisks"])
        subagent_runtime = payload["subagentRuntime"]
        self.assertTrue(subagent_runtime["configured"], subagent_runtime)
        self.assertTrue(subagent_runtime["enabled"], subagent_runtime)
        self.assertEqual(subagent_runtime["adapter"], "intercom")
        self.assertTrue(subagent_runtime["intercomBridgeLinked"], subagent_runtime)
        self.assertEqual(subagent_runtime["packages"]["subagents"]["packageName"], SUBAGENTS_PACKAGE)
        self.assertEqual(subagent_runtime["packages"]["subagents"]["packageVersion"], SUBAGENTS_VERSION)
        self.assertEqual(subagent_runtime["packages"]["intercom"]["packageName"], "pi-intercom")
        self.assertEqual(subagent_runtime["packages"]["intercom"]["packageVersion"], "0.6.0")
        self.assertIn(str(subagents), subagent_runtime["extensionPaths"])
        self.assertIn(str(intercom), subagent_runtime["extensionPaths"])

    def test_subagent_runtime_fails_closed_when_intercom_packages_missing(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            self.write_runtime_defaults(root)
            inspected = guard.inspect_subagent_runtime(root)

            with self.assertRaisesRegex(guard.StronkPiError, "subagent runtime package missing"):
                guard.prepare_subagent_runtime(root)
        missing = {(item["packageName"], item["packageVersion"]) for item in inspected["missingPackages"]}
        self.assertIn((SUBAGENTS_PACKAGE, SUBAGENTS_VERSION), missing)
        self.assertIn(("pi-intercom", "0.6.0"), missing)
        self.assertFalse(inspected["enabled"])
        self.assertFalse(inspected["intercomBridgeLinked"])

    def test_subagent_runtime_rejects_package_json_only_fork_stub(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            self.write_runtime_defaults(root)
            stub = root / "agent" / "npm" / "node_modules" / SUBAGENTS_PACKAGE
            stub.mkdir(parents=True)
            (stub / "package.json").write_text(
                json.dumps({"name": SUBAGENTS_PACKAGE, "version": SUBAGENTS_VERSION}) + "\n",
                encoding="utf-8",
            )
            self.write_runtime_package(root, "pi-intercom", "0.6.0")

            inspected = guard.inspect_subagent_runtime(root)

            with self.assertRaisesRegex(guard.StronkPiError, "subagent runtime package missing"):
                guard.prepare_subagent_runtime(root)
        missing = {(item["packageName"], item["packageVersion"]) for item in inspected["missingPackages"]}
        self.assertIn((SUBAGENTS_PACKAGE, SUBAGENTS_VERSION), missing)
        self.assertFalse(inspected["packages"]["subagents"]["installed"])

    def test_generated_subagent_roles_allow_pi_intercom_bridge(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            plugin_path = (root / guard.DEFAULT_PLUGIN_RELATIVE).resolve(strict=False)
            bridge_path = root / "agent" / "extensions" / "pi-intercom"

            guard.install_bundle_defaults(root=root, dry_run=False)
            role_text = (root / "agent" / "agents" / "technical-researcher.md").read_text(encoding="utf-8")
            extensions_line = next(line for line in role_text.splitlines() if line.startswith("extensions: "))
            extension_items = [item.strip() for item in extensions_line.removeprefix("extensions: ").split(",")]

        self.assertIn("extensions: ", role_text)
        self.assertIn(str(plugin_path), extension_items)
        self.assertIn(str(bridge_path), extension_items)
        self.assertNotIn("~/.stronk-pi", extensions_line)
        self.assertNotIn("pi-intercom", extension_items)

    def test_prepare_runtime_refreshes_project_mcp_json(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            home = tmp / "home"
            xdg = tmp / "xdg"
            xdg_cache = tmp / "xdg-cache"
            project.mkdir()
            home.mkdir()
            (xdg / "mcp").mkdir(parents=True)
            xdg_cache.mkdir()
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
            (project / ".mcp.json").write_text(
                '{"mcpServers":{"bypass":{"command":"python3"}}}\n',
                encoding="utf-8",
            )

            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}, clear=False):
                status = guard.prepare_mcp_adapter_runtime(root, cwd=project)

            generated = json.loads((project / ".mcp.json").read_text(encoding="utf-8"))

        self.assertTrue(status["enabled"])
        self.assertEqual(status["configPath"], str(project.resolve(strict=False) / ".mcp.json"))
        self.assertEqual(sorted(generated["mcpServers"].keys()), ["example"])
        self.assertNotIn("bypass", generated["mcpServers"])

    def test_prepare_runtime_rejects_project_pi_mcp_config(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            xdg = tmp / "xdg"
            project.mkdir()
            (project / ".pi").mkdir()
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
            (project / ".pi" / "mcp.json").write_text(
                '{"mcpServers":{"bypass":{"command":"python3"}}}\n',
                encoding="utf-8",
            )

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
        self.assertFalse((project / ".mcp.json").exists())

    def test_stronkpi_entrypoint_launches_with_mcp_adapter(self):
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            root = tmp / "state"
            project = tmp / "project"
            home = tmp / "home"
            xdg = tmp / "xdg"
            xdg_cache = tmp / "xdg-cache"
            project.mkdir()
            home.mkdir()
            (xdg / "mcp").mkdir(parents=True)
            xdg_cache.mkdir()
            self.write_adapter_package(root)
            subagents = self.write_runtime_package(root, SUBAGENTS_PACKAGE, SUBAGENTS_VERSION)
            intercom = self.write_runtime_package(root, "pi-intercom", "0.6.0")
            plugin_path = root / "artifacts" / f"stronk-pi-plugin-{guard.DEFAULT_PLUGIN_VERSION}" / "package" / "src" / "index.mjs"
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
                        "(root / 'child-env.json').write_text(json.dumps({",
                        "    'HOME': os.environ.get('HOME'),",
                        "    'XDG_CONFIG_HOME': os.environ.get('XDG_CONFIG_HOME'),",
                        "    'XDG_CACHE_HOME': os.environ.get('XDG_CACHE_HOME'),",
                        "    'STRONK_PI_CONFIG_ROOT': os.environ.get('STRONK_PI_CONFIG_ROOT'),",
                        "    'STRONK_PI_CACHE_ROOT': os.environ.get('STRONK_PI_CACHE_ROOT'),",
                        "    'STRONK_PI_LOG_ROOT': os.environ.get('STRONK_PI_LOG_ROOT'),",
                        "    'STRONK_PI_TMP_ROOT': os.environ.get('STRONK_PI_TMP_ROOT'),",
                        "    'STRONK_PI_MCP_CONFIG_PATH': os.environ.get('STRONK_PI_MCP_CONFIG_PATH'),",
                        "}) + '\\n', encoding='utf-8')",
                        "(root / 'subagent-env.json').write_text(json.dumps({",
                        "    'facade': os.environ.get('STRONK_PI_SUBAGENT_FACADE'),",
                        "    'adapter': os.environ.get('STRONK_PI_SUBAGENT_ADAPTER'),",
                        "}) + '\\n', encoding='utf-8')",
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
                    "HOME": str(home),
                    "XDG_CONFIG_HOME": str(xdg),
                    "XDG_CACHE_HOME": str(xdg_cache),
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

            config_path = guard.project_generated_mcp_config_path(project, root)
            config_text = config_path.read_text(encoding="utf-8")
            config = json.loads(config_text)
            launch_args = json.loads((root / "launch-argv.json").read_text(encoding="utf-8"))
            resolved_launch_args = [
                str(Path(item).resolve()) if isinstance(item, str) and item.startswith("/") else item
                for item in launch_args
            ]
            agent_dir_text = (root / "pi-agent-dir.txt").read_text(encoding="utf-8").strip()
            child_env = json.loads((root / "child-env.json").read_text(encoding="utf-8"))
            subagent_env = json.loads((root / "subagent-env.json").read_text(encoding="utf-8"))
            offline_text = (root / "pi-offline.txt").read_text(encoding="utf-8").strip()
            project_mcp_exists = (project / ".mcp.json").is_file()

        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(config["mcpServers"]["example"]["env"]["STRONKPI_SMOKE_SECRET"], "${STRONKPI_SMOKE_SECRET}")
        self.assertEqual(config["mcpServers"]["example"]["env"]["STRONKPI_SMOKE_MODE"], "live")
        self.assertNotIn("do-not-write-me", config_text)
        self.assertEqual(sorted(config["mcpServers"].keys()), ["example"])
        self.assertEqual(launch_args.count("--extension"), 4)
        self.assertIn(str(subagents), launch_args)
        self.assertIn(str(intercom), launch_args)
        self.assertIn("--mcp-config", launch_args)
        self.assertIn(str(config_path.resolve()), resolved_launch_args)
        self.assertIn("--offline", launch_args)
        self.assertEqual(child_env["HOME"], str(home.resolve(strict=False)))
        self.assertEqual(child_env["XDG_CONFIG_HOME"], str(xdg))
        self.assertEqual(child_env["XDG_CACHE_HOME"], str(xdg_cache))
        self.assertEqual(child_env["STRONK_PI_CONFIG_ROOT"], str(root / "config"))
        self.assertEqual(child_env["STRONK_PI_CACHE_ROOT"], str(root / "cache"))
        self.assertEqual(child_env["STRONK_PI_LOG_ROOT"], str(root / "logs"))
        self.assertEqual(child_env["STRONK_PI_TMP_ROOT"], str(root / "tmp"))
        self.assertEqual(child_env["STRONK_PI_MCP_CONFIG_PATH"], str(config_path))
        self.assertEqual(subagent_env["facade"], "stronk")
        self.assertEqual(subagent_env["adapter"], "intercom")
        self.assertEqual(agent_dir_text, str(root / "agent"))
        self.assertEqual(offline_text, "1")
        self.assertEqual(str(registry), str(xdg / "mcp" / "registry.toml"))
        self.assertFalse((root / "agent" / "mcp.json").exists())
        self.assertTrue(project_mcp_exists)
        self.assertFalse((home / ".pi").exists())
        self.assertFalse((home / ".config" / "pi").exists())
        self.assertFalse((home / ".local" / "share" / "pi").exists())
        self.assertFalse((home / ".cache" / "pi").exists())
        self.assertFalse((root / "home").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
