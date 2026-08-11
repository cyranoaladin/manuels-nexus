from __future__ import annotations

import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_delivered_archive_exactly_source_clean as exact_archive


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


class DeliveredArchiveExactlySourceCleanTest(unittest.TestCase):
    def test_only_dist_source_clean_is_accepted_as_delivered_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            dist = root / "dist"
            dist.mkdir(parents=True)
            archive = dist / "source_clean.tar.gz"
            write_tar(archive, {"nsi-enseignement/README.md": "ok"})

            errors = exact_archive.analyze_delivered_archive_exactly_source_clean(root, archive)

            self.assertEqual(errors, [])

    def test_parent_global_archive_with_git_is_rejected_even_when_not_delivered(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            dist = root / "dist"
            dist.mkdir(parents=True)
            write_tar(dist / "source_clean.tar.gz", {"nsi-enseignement/README.md": "ok"})
            write_tar(Path(raw) / "nsi-enseignement.tar", {"nsi-enseignement/.git/HEAD": "ref: main"})

            errors = exact_archive.analyze_delivered_archive_exactly_source_clean(root, dist / "source_clean.tar.gz")

            self.assertTrue(any("archive parent" in error and ".git" in error for error in errors))

    def test_source_clean_must_not_contain_git_bundle_or_nested_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            dist = root / "dist"
            dist.mkdir(parents=True)
            archive = dist / "source_clean.tar.gz"
            write_tar(
                archive,
                {
                    "nsi-enseignement/dist/git_bundle.bundle": "bundle",
                    "nsi-enseignement/nsi-enseignement.tar": "nested",
                },
            )

            errors = exact_archive.analyze_delivered_archive_exactly_source_clean(root, archive)

            self.assertTrue(any("git_bundle.bundle" in error for error in errors))
            self.assertTrue(any("archive globale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
