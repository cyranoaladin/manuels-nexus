from __future__ import annotations

import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_archive_portability as portability


def write_source_tar(path: Path) -> None:
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw) / "nsi-enseignement"
        base.mkdir()
        for rel in portability.REQUIRED_FILES:
            target = base / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("contenu\n", encoding="utf-8")
        scripts = base / "scripts"
        scripts.mkdir(exist_ok=True)
        for script in portability.CHECKS:
            target = base / script
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("print('PASS')\n", encoding="utf-8")
        with tarfile.open(path, "w:gz") as archive:
            archive.add(base, arcname="nsi-enseignement")


class ArchivePortabilityModesTest(unittest.TestCase):
    def test_source_clean_mode_does_not_require_git_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            dist = root / "dist"
            dist.mkdir()
            write_source_tar(dist / "source_clean.tar.gz")

            result = portability.analyze_archive_portability(root)

            self.assertEqual([], result.errors)


if __name__ == "__main__":
    unittest.main()
