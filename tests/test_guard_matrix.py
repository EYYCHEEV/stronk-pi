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


if __name__ == "__main__":
    unittest.main(verbosity=2)

