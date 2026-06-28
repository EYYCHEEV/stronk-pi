#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
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


def getaddrinfo_for(*addresses: str):
    def fake_getaddrinfo(_host, _port, *args, **kwargs):
        return [(None, None, None, "", (address, 443)) for address in addresses]

    return fake_getaddrinfo


class UrlGuardTests(unittest.TestCase):
    def test_blocks_unsafe_literal_urls(self):
        for url in (
            "http://127.0.0.1/",
            "http://169.254.169.254/latest/meta-data/",
            "file:///etc/passwd",
            "http://localhost/",
            "http://metadata.google.internal/",
        ):
            with self.subTest(url=url):
                with self.assertRaises(guard.StronkPiError):
                    guard.check_public_http_url(url, "test URL")

    def test_blocks_private_dns_answers(self):
        with patch("socket.getaddrinfo", getaddrinfo_for("127.0.0.1")):
            with self.assertRaisesRegex(guard.StronkPiError, "private/local IP denied"):
                guard.check_public_http_url("https://example.com/", "test URL")

    def test_allows_dns_proxy_addresses_for_hostnames(self):
        with patch("socket.getaddrinfo", getaddrinfo_for("198.18.0.7")):
            checked = guard.check_public_http_url("https://example.com/page", "test URL")
        self.assertEqual(checked["hostname"], "example.com")


class RedactionTests(unittest.TestCase):
    def test_redacts_secret_like_values(self):
        fake_secret = "sk-" + "a" * 24
        redacted = guard.redact({"api_key": fake_secret, "nested": {"command": f"token={fake_secret}"}})
        self.assertEqual(redacted["api_key"], "<redacted>")
        self.assertNotIn(fake_secret, str(redacted))


class PathTests(unittest.TestCase):
    def test_relative_fixture_artifacts_must_stay_under_fixtures(self):
        with self.assertRaisesRegex(guard.StronkPiError, "fixtures"):
            guard.artifact_path(ROOT / "manifests" / "current.json", {"artifactPath": "../README.md"})

    def test_floating_version_detection(self):
        for value in ("latest", "tool@latest", "^1.2.3", "1.x"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(guard.StronkPiError, "floating|mutable"):
                    guard.fail_if_floating("version", value)


class ToolGuardTests(unittest.TestCase):
    def test_image_read_is_allowed_as_distribution_safe_tool(self):
        cases = (
            ("image_read", {"paths": ["screenshots/example.png"]}),
            ("image_preflight_read", {"handle": "image-preflight-00000000-0000-0000-0000-000000000000"}),
        )
        for tool, payload in cases:
            with self.subTest(tool=tool):
                result = guard.guarded_tool_decision(tool, payload, ROOT, {})
                self.assertTrue(result["allow"])
                self.assertEqual(result["reason"], "distribution-owned safe tool class")

    def test_image_preflight_read_requires_generated_handle_shape(self):
        for payload in ({}, {"handle": "not-a-handle"}, {"handle": "../image-preflight-00000000-0000-0000-0000-000000000000"}):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(guard.StronkPiError, "valid image preflight handle"):
                    guard.guarded_tool_decision("image_preflight_read", payload, ROOT, {})

    def test_stale_search_compatibility_tools_are_not_safe_allowlisted(self):
        for tool in ("get_search_content", "stronk_fetch_content"):
            with self.subTest(tool=tool):
                result = guard.guarded_tool_decision(tool, {}, ROOT, {})
                self.assertFalse(result["allow"])
                self.assertIn("unknown tool denied by default", result["reason"])

    def test_raw_subagent_is_denied_while_stronk_subagent_is_allowed(self):
        raw = guard.guarded_tool_decision("subagent", {"action": "spawn"}, ROOT, {})
        guarded = guard.guarded_tool_decision("stronk_subagent", {"action": "status"}, ROOT, {})

        self.assertFalse(raw["allow"])
        self.assertIn("raw subagent tool denied", raw["reason"])
        self.assertTrue(guarded["allow"])

    def test_stronk_subagent_cwd_override_is_denied(self):
        for payload in (
            {"action": "spawn", "role": "executor", "task": "inspect", "cwd": "/Users/example"},
            {"action": "spawn", "role": "executor", "task": "inspect", "nested": {"cwd": "/"}},
            {"action": "wait_all", "childIds": ["sp-child-1"], "meta": [{"cwd": "/"}]},
            {"action": "close_all", "childIds": [{"cwd": "/"}]},
            {"action": "read_output", "outputHandle": "subagent-output-00000000-0000-0000-0000-000000000000", "meta": [{"cwd": "/"}]},
        ):
            with self.subTest(payload=payload):
                result = guard.guarded_tool_decision("stronk_subagent", payload, ROOT, {})
                self.assertFalse(result["allow"])
                self.assertIn("stronk_subagent cwd override denied", result["reason"])

    def test_stronk_subagent_recursive_overrides_are_denied(self):
        for payload, key in (
            ({"action": "wait_all", "childIds": ["sp-child-1"], "meta": [{"model": "override"}]}, "model"),
            ({"action": "close_all", "childIds": ["sp-child-1"], "meta": {"tools": ["bash"]}}, "tools"),
            ({"action": "read_output", "outputHandle": "subagent-output-00000000-0000-0000-0000-000000000000", "outputMode": "raw"}, "outputMode"),
        ):
            with self.subTest(payload=payload):
                result = guard.guarded_tool_decision("stronk_subagent", payload, ROOT, {})
                self.assertFalse(result["allow"])
                self.assertIn(f"stronk_subagent override denied: {key}", result["reason"])


class BashSafetyScreenTests(unittest.TestCase):
    def test_blocked_upstream_gh_commands_are_targeted(self):
        for command in (
            "gh pr create --repo earendil-works/pi",
            "gh pr comment 123 --repo badlogic/pi-mono",
            "gh issue create --repo nicobailon/pi-subagents",
            "gh repo clone earendil-works/pi",
            "gh release create v1 --repo badlogic/pi-mono",
            "git clone https://github.com/earendil-works/pi",
            "git push https://github.com/earendil-works/pi main",
            "git push git@github.com:badlogic/pi-mono.git main",
            "git push nicobailon/pi-subagents main",
            "git remote add pi https://github.com/earendil-works/pi",
            "cd /tmp && git push origin main && gh pr create --repo earendil-works/pi",
        ):
            with self.subTest(command=command):
                self.assertTrue(
                    guard.command_targets_blocked_upstream(command),
                    f"expected blocked upstream action: {command!r}",
                )

    def test_non_blocked_commands_are_not_targeted(self):
        for command in (
            "gh pr create --repo EYYCHEEV/stronk-pi",
            "git push origin main",
            "git push EYYCHEEV/stronk-pi main",
            "git log --oneline",
            "git clone https://github.com/EYYCHEEV/stronk-pi",
            "cd /tmp/earendil-works/pi && echo hi",
            "ls -la",
            "echo push earendil-works/pi",
        ):
            with self.subTest(command=command):
                self.assertFalse(
                    guard.command_targets_blocked_upstream(command),
                    f"expected non-targeted command: {command!r}",
                )

    def test_internally_screen_bash_denies_blocked_upstream_actions(self):
        for command in (
            "gh pr create --repo earendil-works/pi",
            "git push https://github.com/badlogic/pi-mono",
        ):
            with self.subTest(command=command):
                allowed, reason = guard.internally_screen_bash(command)
                self.assertFalse(allowed)
                self.assertIn("blocked upstream", reason)

    def test_blocked_upstream_bash_denied_even_with_permissive_shared_hook(self):
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_name:
            hook = Path(tmp_name) / "permissive-hook.py"
            hook.write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
            hook.chmod(0o755)
            old_hook = os.environ.get("STRONK_PI_DANGEROUS_COMMAND_HOOK")
            try:
                os.environ["STRONK_PI_DANGEROUS_COMMAND_HOOK"] = str(hook)
                blocked = guard.guarded_tool_decision(
                    "bash",
                    {"command": "git push https://github.com/earendil-works/pi main"},
                    ROOT,
                    {},
                )
                self.assertFalse(blocked["allow"])
                self.assertIn("blocked upstream", blocked["reason"])
                # A non-blocked command still consults the permissive shared hook and is allowed,
                # proving the hook wiring works and the deny is specific to the upstream action.
                allowed = guard.guarded_tool_decision("bash", {"command": "echo hi"}, ROOT, {})
                self.assertTrue(allowed["allow"])
            finally:
                if old_hook is None:
                    os.environ.pop("STRONK_PI_DANGEROUS_COMMAND_HOOK", None)
                else:
                    os.environ["STRONK_PI_DANGEROUS_COMMAND_HOOK"] = old_hook


if __name__ == "__main__":
    unittest.main(verbosity=2)
