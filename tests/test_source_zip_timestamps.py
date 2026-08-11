from __future__ import annotations

import os
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.build_source_zip as build_source_zip


class SourceZipTimestampsTest(unittest.TestCase):
    def test_zip_entries_use_stable_non_future_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            future_file = root / "Makefile"
            future_file.write_text("audit-extracted-source:\n\t@echo ok\n", encoding="utf-8")
            future = time.time() + 86400
            os.utime(future_file, (future, future))
            target = Path(raw) / "nsi-enseignement_source_clean.zip"

            build_source_zip.build_zip(root, target)

            with zipfile.ZipFile(target) as archive:
                entries = archive.infolist()
            self.assertTrue(entries)
            self.assertTrue(all(info.date_time == build_source_zip.STABLE_ZIP_DATETIME for info in entries))


if __name__ == "__main__":
    unittest.main()
