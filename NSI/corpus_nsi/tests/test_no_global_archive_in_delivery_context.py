from __future__ import annotations

import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_no_global_archive_in_delivery_context as no_global_archive


def write_tar(path: Path, entries: dict[str, str]) -> None:
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        for name, content in entries.items():
            target = base / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        with tarfile.open(path, "w:gz" if path.name.endswith((".tar.gz", ".tgz")) else "w") as archive:
            for target in base.rglob("*"):
                if target.is_file():
                    archive.add(target, arcname=target.relative_to(base).as_posix())


class NoGlobalArchiveInDeliveryContextTest(unittest.TestCase):
    def test_parent_global_archive_with_git_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            write_tar(Path(raw) / "nsi-enseignement.tar", {"nsi-enseignement/.git/HEAD": "ref: main"})

            result = no_global_archive.analyze_no_global_archive_in_delivery_context(root)

            self.assertTrue(any(".git" in error for error in result.errors))

    def test_current_global_archive_with_dist_and_bundle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            write_tar(
                root / "NSI.tar.gz",
                {
                    "nsi-enseignement/dist/source_clean.tar.gz": "source",
                    "nsi-enseignement/dist/git_bundle.bundle": "bundle",
                },
            )

            result = no_global_archive.analyze_no_global_archive_in_delivery_context(root)

            self.assertTrue(any("dist/" in error for error in result.errors))
            self.assertTrue(any("git_bundle.bundle" in error for error in result.errors))

    def test_global_archive_with_nested_archive_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            write_tar(root / "nsi-enseignement.tar.gz", {"nsi-enseignement/archive.tar": "nested"})

            result = no_global_archive.analyze_no_global_archive_in_delivery_context(root)

            self.assertTrue(any("archive imbriquée" in error for error in result.errors))

    def test_absence_of_global_archive_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()

            result = no_global_archive.analyze_no_global_archive_in_delivery_context(root)

            self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
