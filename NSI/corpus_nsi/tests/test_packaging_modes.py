from __future__ import annotations

import io
import tarfile
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.build_source_archive as build_source_archive


class PackagingModesTest(unittest.TestCase):
    def test_source_archive_mode_without_git_skips_bundle_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "nsi-enseignement"
            (repo / "scripts").mkdir(parents=True)
            (repo / "README.md").write_text("source archive\n", encoding="utf-8")

            old_root = build_source_archive.ROOT
            old_dist = build_source_archive.DIST
            old_source_tar = build_source_archive.SOURCE_TAR
            old_bundle = build_source_archive.BUNDLE
            try:
                build_source_archive.ROOT = repo
                build_source_archive.DIST = repo / "dist"
                build_source_archive.SOURCE_TAR = build_source_archive.DIST / "source_clean.tar.gz"
                build_source_archive.BUNDLE = build_source_archive.DIST / "git_bundle.bundle"

                output = io.StringIO()
                with redirect_stdout(output):
                    exit_code = build_source_archive.main()

                self.assertEqual(0, exit_code)
                self.assertTrue(build_source_archive.SOURCE_TAR.exists())
                self.assertFalse(build_source_archive.BUNDLE.exists())
                self.assertIn("git bundle non généré", output.getvalue())
                with tarfile.open(build_source_archive.SOURCE_TAR, "r:gz") as archive:
                    names = archive.getnames()
                self.assertIn("nsi-enseignement/README.md", names)
            finally:
                build_source_archive.ROOT = old_root
                build_source_archive.DIST = old_dist
                build_source_archive.SOURCE_TAR = old_source_tar
                build_source_archive.BUNDLE = old_bundle


if __name__ == "__main__":
    unittest.main()
