#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
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
        class FakeResponse(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                self.close()
                return False

            def geturl(self):
                return "https://github.com/EYYCHEEV/stronk-pi/releases/download/stronk-pi-v0.1.0/stronk-pi-plugin-0.1.0.tgz"

        old_getaddrinfo = guard.socket.getaddrinfo
        old_urlopen = guard.urllib.request.urlopen
        old_no_network = os.environ.get("STRONKPI_NO_NETWORK")
        fixture = ROOT / "tests" / "fixtures" / "artifacts" / "stronk-pi-plugin-0.1.0.tgz"

        def fake_getaddrinfo(host, port, type=0):
            self.assertEqual(host, "github.com")
            return [(guard.socket.AF_INET, guard.socket.SOCK_STREAM, 6, "", ("140.82.112.3", port))]

        def fake_urlopen(request, timeout=30):
            self.assertEqual(timeout, 30)
            self.assertEqual(request.full_url, "https://github.com/EYYCHEEV/stronk-pi/releases/download/stronk-pi-v0.1.0/stronk-pi-plugin-0.1.0.tgz")
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

    def test_weak_manifest_metadata_fails(self):
        for name, expected in (
            ("missing-attestation.json", "attestation"),
            ("compatibility-mismatch.json", "compatibilityVersion"),
            ("invalid-created-at.json", "createdAt"),
            ("http-release-url-denied.json", "HTTPS"),
            ("missing-provenance.json", "provenance"),
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
                        "artifactUrl": "https://github.com/EYYCHEEV/stronk-pi/releases/download/stronk-pi-v0.1.0/a.tgz"
                    },
                )
        finally:
            if old is None:
                os.environ.pop("STRONKPI_NO_NETWORK", None)
            else:
                os.environ["STRONKPI_NO_NETWORK"] = old


if __name__ == "__main__":
    unittest.main(verbosity=2)
