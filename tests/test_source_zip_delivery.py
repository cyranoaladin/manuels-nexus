from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.build_source_zip as build_source_zip


class SourceZipDeliveryTest(unittest.TestCase):
    def test_zip_excludes_git_dist_bundle_and_caches(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "nsi-enseignement_source_clean.zip"

            build_source_zip.build_zip(ROOT, target)

            with zipfile.ZipFile(target) as archive:
                entries = archive.namelist()
            self.assertTrue(any(entry.startswith("nsi-enseignement/") for entry in entries))
            forbidden = [entry for entry in entries if "/.git/" in entry or "/dist/" in entry]
            forbidden.extend(entry for entry in entries if entry.endswith("git_bundle.bundle"))
            forbidden.extend(entry for entry in entries if "__pycache__" in entry or entry.endswith(".pyc"))
            self.assertEqual([], forbidden)


if __name__ == "__main__":
    unittest.main()
