from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_no_build_artifacts_in_index as artifacts


class BuildArtifactCheckTest(unittest.TestCase):
    def test_source_clean_zip_is_allowed_delivery_side_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            dist = root / "dist"
            dist.mkdir()
            (dist / "source_clean.tar.gz").write_bytes(b"tar")
            (dist / "git_bundle.bundle").write_bytes(b"bundle")
            (dist / "nsi-enseignement_source_clean.zip").write_bytes(b"zip")

            found = artifacts.find_artifacts(root, require_archives=True)

            self.assertEqual(found, [])

    def test_source_clean_zip_is_not_required_for_audit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            dist = root / "dist"
            dist.mkdir()
            (dist / "source_clean.tar.gz").write_bytes(b"tar")
            (dist / "git_bundle.bundle").write_bytes(b"bundle")

            found = artifacts.find_artifacts(root, require_archives=True)

            self.assertEqual(found, [])

    def test_check_reports_python_cache_without_deleting_it(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cache = root / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            pyc = cache / "module.cpython-312.pyc"
            pyc.write_bytes(b"bytecode")

            found = artifacts.find_artifacts(root, require_archives=False)

            self.assertIn(cache, found)
            self.assertIn(pyc, found)
            self.assertTrue(cache.exists())
            self.assertTrue(pyc.exists())

    def test_git_checkout_ignores_untracked_local_venv(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / "README.md").write_text("ok\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / ".venv" / "bin").mkdir(parents=True)
            (root / ".venv" / "bin" / "python").write_text("local\n", encoding="utf-8")

            found = artifacts.find_artifacts(root, require_archives=False)

            self.assertEqual(found, [])

    def test_git_checkout_rejects_tracked_python_cache(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            cache = root / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            pyc = cache / "module.pyc"
            pyc.write_bytes(b"bytecode")
            subprocess.run(["git", "add", str(pyc.relative_to(root))], cwd=root, check=True, stdout=subprocess.DEVNULL)

            found = artifacts.find_artifacts(root, require_archives=False)

            self.assertIn(cache, found)
            self.assertIn(pyc, found)

    def test_lot_validation_logs_are_not_build_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            log = root / "reports" / "lot1" / "pytest_validation.log"
            log.parent.mkdir(parents=True)
            log.write_text("evidence\n", encoding="utf-8")
            subprocess.run(["git", "add", str(log.relative_to(root))], cwd=root, check=True, stdout=subprocess.DEVNULL)

            found = artifacts.find_artifacts(root, require_archives=False)

            self.assertEqual(found, [])


if __name__ == "__main__":
    unittest.main()
