from __future__ import annotations

import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_uploaded_archive_policy as archive_policy


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


class UploadedArchivePolicyTest(unittest.TestCase):
    def test_tar_with_git_objects_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            archive = root / "payload.tar"
            write_tar(archive, {"nsi-enseignement/.git/objects/aa/bb": "object"})

            errors = archive_policy.analyze_uploaded_archive_policy(root, delivered_archive=archive, scan_parent=False)

            self.assertTrue(any(".git" in error for error in errors))

    def test_targz_with_git_head_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            archive = root / "payload.tar.gz"
            write_tar(archive, {"nsi-enseignement/.git/HEAD": "ref: refs/heads/main"})

            errors = archive_policy.analyze_uploaded_archive_policy(root, delivered_archive=archive, scan_parent=False)

            self.assertTrue(any(".git" in error for error in errors))

    def test_archive_with_python_cache_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            archive = root / "payload.tar.gz"
            write_tar(archive, {"nsi-enseignement/scripts/__pycache__/x.pyc": "bytecode"})

            errors = archive_policy.analyze_uploaded_archive_policy(root, delivered_archive=archive, scan_parent=False)

            self.assertTrue(any("__pycache__" in error for error in errors))

    def test_global_archive_with_dist_and_git_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            archive = root / "nsi-enseignement.tar"
            write_tar(
                archive,
                {
                    "nsi-enseignement/.git/HEAD": "ref: refs/heads/main",
                    "nsi-enseignement/dist/source_clean.tar.gz": "nested",
                },
            )

            errors = archive_policy.analyze_uploaded_archive_policy(root, delivered_archive=archive, scan_parent=False)

            self.assertTrue(any("archive globale interdite" in error.lower() for error in errors))
            self.assertTrue(any(".git" in error for error in errors))
            self.assertTrue(any("dist/" in error for error in errors))

    def test_clean_source_archive_is_allowed_as_delivered_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            dist = root / "dist"
            dist.mkdir(parents=True)
            archive = dist / "source_clean.tar.gz"
            write_tar(archive, {"nsi-enseignement/README.md": "ok"})

            errors = archive_policy.analyze_uploaded_archive_policy(root, delivered_archive=archive, scan_parent=False)

            self.assertEqual(errors, [])

    def test_source_clean_zip_is_allowed_only_as_side_archive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            dist = root / "dist"
            dist.mkdir(parents=True)
            source_tar = dist / "source_clean.tar.gz"
            write_tar(source_tar, {"nsi-enseignement/README.md": "ok"})
            zip_path = dist / "nsi-enseignement_source_clean.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr("nsi-enseignement/README.md", "ok")

            errors = archive_policy.analyze_uploaded_archive_policy(root, scan_parent=False)

            self.assertEqual(errors, [])

            delivered_errors = archive_policy.analyze_uploaded_archive_policy(
                root,
                delivered_archive=zip_path,
                scan_parent=False,
            )
            self.assertTrue(any("DELIVERED_ARCHIVE doit être dist/source_clean.tar.gz" in error for error in delivered_errors))

    def test_delivered_global_archive_from_tmp_with_git_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw)
            root = workspace / "repo"
            root.mkdir()
            delivered = workspace / "nsi-enseignement.tar"
            write_tar(delivered, {"nsi-enseignement/.git/HEAD": "ref: refs/heads/main"})

            errors = archive_policy.analyze_uploaded_archive_policy(root, delivered_archive=delivered, scan_parent=False)

            self.assertTrue(any("DELIVERED_ARCHIVE" in error for error in errors))
            self.assertTrue(any(".git" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
