from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.run_audit_extracted_source as run_audit_extracted_source


class AuditExtractedSourceNoHangTest(unittest.TestCase):
    def test_makefile_uses_bounded_tp_runtime_gate(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        target = makefile.split("audit-extracted-source-local:", 1)[1].split("\n\n", 1)[0]

        self.assertIn("timeout 90 python -m scripts.check_tp_pedagogical_assets_runtime", target)
        self.assertNotIn("\n\tpython -m scripts.check_tp_pedagogical_assets\n", target)

    def test_makefile_delegates_git_checkout_to_source_clean_wrapper(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        target = makefile.split("audit-extracted-source:", 1)[1].split("\n\n", 1)[0]

        self.assertIn("scripts.run_audit_extracted_source", target)
        self.assertIn("audit-extracted-source-local", makefile)

    def test_wrapper_runs_audit_inside_extracted_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".git").mkdir()
            (root / "dist").mkdir()
            source_root = root / "source" / "nsi-enseignement"
            source_root.mkdir(parents=True)
            (source_root / "MARKER").write_text("ok\n", encoding="utf-8")
            (source_root / "Makefile").write_text(
                "audit-extracted-source:\n"
                "\t@test ! -d .git\n"
                "\t@test -f MARKER\n",
                encoding="utf-8",
            )
            archive = root / "dist" / "source_clean.tar.gz"
            with tarfile.open(archive, "w:gz") as handle:
                handle.add(source_root, arcname="nsi-enseignement")

            status = run_audit_extracted_source.run_audit_extracted_source(root)

            self.assertEqual(status, 0)

    def test_safe_extract_tar_rejects_parent_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            archive = root / "evil.tar.gz"
            payload = root / "payload.txt"
            payload.write_text("evil\n", encoding="utf-8")
            with tarfile.open(archive, "w:gz") as handle:
                handle.add(payload, arcname="../evil.txt")

            with tarfile.open(archive, "r:gz") as handle:
                with self.assertRaisesRegex(ValueError, "hors du repertoire cible|Zip-Slip"):
                    run_audit_extracted_source.safe_extract_tar(handle, root / "out")
            self.assertFalse((root / "evil.txt").exists())

    def test_safe_extract_tar_rejects_absolute_member(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            archive = root / "absolute.tar.gz"
            with tarfile.open(archive, "w:gz") as handle:
                payload = b"evil\n"
                info = tarfile.TarInfo("/tmp/evil.txt")
                info.size = len(payload)
                handle.addfile(info, io.BytesIO(payload))

            with tarfile.open(archive, "r:gz") as handle:
                with self.assertRaisesRegex(ValueError, "chemin archive absolu|Zip-Slip"):
                    run_audit_extracted_source.safe_extract_tar(handle, root / "out")

    def test_safe_extract_tar_accepts_normal_source_clean_layout(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            archive = root / "normal.tar.gz"
            source = root / "source" / "nsi-enseignement"
            source.mkdir(parents=True)
            (source / "README.md").write_text("ok\n", encoding="utf-8")
            with tarfile.open(archive, "w:gz") as handle:
                handle.add(source, arcname="nsi-enseignement")

            destination = root / "out"
            with tarfile.open(archive, "r:gz") as handle:
                run_audit_extracted_source.safe_extract_tar(handle, destination)

            self.assertEqual((destination / "nsi-enseignement" / "README.md").read_text(encoding="utf-8"), "ok\n")

    def test_source_clean_audit_extracted_source_finishes_without_drive_mirror(self) -> None:
        # RC3 : Générer des caches factices avant le build pour reproduire
        # le scénario CI (ruff + pytest génèrent des caches, puis le build
        # doit les exclure de l'archive).
        fake_caches = []
        for name in ("__pycache__", ".pytest_cache", ".ruff_cache"):
            d = ROOT / "tests" / name
            if not d.exists():
                d.mkdir(parents=True)
                (d / "dummy.dat").write_bytes(b"cache")
                fake_caches.append(d)

        try:
            completed_build = subprocess.run(
                [sys.executable, "-m", "scripts.build_source_archive"],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=60,
            )
        finally:
            for d in fake_caches:
                if d.exists():
                    shutil.rmtree(d)
        self.assertEqual(completed_build.returncode, 0, completed_build.stdout)

        archive = ROOT / "dist" / "source_clean.tar.gz"
        self.assertTrue(archive.exists(), "dist/source_clean.tar.gz doit être généré par ce test")

        # Vérifier qu'aucun cache n'a fui dans l'archive
        completed_check = subprocess.run(
            ["tar", "-tzf", str(archive)],
            stdout=subprocess.PIPE, text=True, timeout=10,
        )
        cache_leaks = [
            line for line in completed_check.stdout.splitlines()
            if any(c in line for c in ("__pycache__", ".pytest_cache", ".ruff_cache", ".pyc"))
        ]
        self.assertEqual(cache_leaks, [], f"Caches ont fui dans l'archive : {cache_leaks}")
        with tempfile.TemporaryDirectory() as raw:
            completed_extract = subprocess.run(
                ["tar", "-xzf", str(archive), "-C", raw],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=30,
            )
            self.assertEqual(completed_extract.returncode, 0, completed_extract.stdout)

            extracted = Path(raw) / "nsi-enseignement"
            env = os.environ.copy()
            env.pop("NSI_DOCUMENTS_DRIVE_ROOT", None)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            completed_audit = subprocess.run(
                ["timeout", "180", "make", "audit-extracted-source"],
                cwd=extracted,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=190,
            )
            self.assertEqual(completed_audit.returncode, 0, completed_audit.stdout)
            residue = list(extracted.rglob("__pycache__")) + list(extracted.rglob("*.pyc"))
            if residue:
                for path in residue:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
            self.assertEqual([], residue)


if __name__ == "__main__":
    unittest.main()
