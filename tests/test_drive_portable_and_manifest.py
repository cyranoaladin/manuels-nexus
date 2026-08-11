from __future__ import annotations

import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_drive_enrichment_traceability_portable as drive_portable
import scripts.check_manifest_source_trace_consistency as manifest_consistency
import scripts.check_drive_trace_no_absolute_local_paths as no_absolute_paths
import scripts.check_no_sensitive_drive_in_source_clean as no_sensitive_archive


FIELDS = (
    "drive_url,drive_folder,file_name,mime_type,local_copy,sha256,niveau,theme,"
    "sequence_possible,qualite_initiale,decision,raison\n"
)


def write_report(root: Path, decision: str = "integrated_adapted") -> None:
    (root / "reports").mkdir(exist_ok=True)
    (root / "reports" / "drive_enrichment_report.md").write_text(
        "| Ressource Drive | Existe localement | Hash | Décision | Support enrichi | Type de reprise | RGPD | Statut final | Commentaire |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        f"| source.pdf | oui | {'a' * 64} | {decision} | support.md | adaptation_drive | conforme | needs_review | test |\n",
        encoding="utf-8",
    )


def write_trace(root: Path, source: str = "Documents_DRIVE/source.pdf", support: str = "support.md") -> None:
    (root / "support_source_trace.yml").write_text(
        "supports:\n"
        f"  - support: {support}\n"
        "    source_officielle: BO 2019\n"
        f"    source_locale_drive: {source}\n"
        "    type_reprise: adaptation_drive\n"
        f"    hash_source: {'a' * 64}\n"
        "    statut_rgpd: conforme - aucune donnée personnelle intégrée\n"
        "    statut_relecture: needs_review\n",
        encoding="utf-8",
    )


def write_tar(path: Path, entries: dict[str, str]) -> None:
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        for name, content in entries.items():
            target = base / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        with tarfile.open(path, "w:gz") as archive:
            for target in base.rglob("*"):
                if target.is_file():
                    archive.add(target, arcname=target.relative_to(base).as_posix())


class DrivePortableAndManifestTest(unittest.TestCase):
    def test_portable_traceability_does_not_require_local_drive_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + f"url,folder,source.pdf,application/pdf,Documents_DRIVE/source.pdf,{'a' * 64},premiere,theme,P01,non_auditee,integrated_adapted,adapté\n",
                encoding="utf-8",
            )
            write_trace(root)
            (root / "support.md").write_text(
                "---\nstatus: needs_review\n---\nSource : Documents_DRIVE/source.pdf\n",
                encoding="utf-8",
            )
            write_report(root)

            result = drive_portable.analyze_drive_enrichment_traceability_portable(root)

            self.assertEqual(result.errors, [])

    def test_portable_traceability_rejects_sensitive_integrated_resource(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + f"url,folder,NotesEleves.csv,text/csv,Documents_DRIVE/NotesEleves.csv,{'b' * 64},premiere,donnees,P01,non_publiable,integrated_adapted,interdit\n",
                encoding="utf-8",
            )
            write_trace(root, source="Documents_DRIVE/NotesEleves.csv")
            (root / "support.md").write_text("---\nstatus: needs_review\n---\n", encoding="utf-8")
            write_report(root)

            result = drive_portable.analyze_drive_enrichment_traceability_portable(root)

            self.assertTrue(any("sensible" in error for error in result.errors))

    def test_manifest_source_trace_rejects_adaptation_marked_generated(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_trace(root, support="support.md")
            (root / "manifest.csv").write_text(
                "chemin,source,statut\nsupport.md,generated,needs_review\n",
                encoding="utf-8",
            )

            result = manifest_consistency.analyze_manifest_source_trace_consistency(root)

            self.assertTrue(any("generated" in error and "adaptation_drive" in error for error in result.errors))

    def test_absolute_personal_path_in_versioned_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            personal_path = "/home/" + "alaeddine/Documents/NSI/Documents_DRIVE/source.pdf"
            (root / "qa_report.md").write_text(
                f"Source locale : {personal_path}\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text("supports: []\n", encoding="utf-8")

            result = no_absolute_paths.analyze_drive_trace_no_absolute_local_paths(root)

            self.assertTrue(any("/home/" in error for error in result.errors))

    def test_source_clean_with_sensitive_drive_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            dist = root / "dist"
            dist.mkdir()
            archive = dist / "source_clean.tar.gz"
            write_tar(archive, {"nsi-enseignement/NotesEleves.csv": "nom,note\nAda,20\n"})

            result = no_sensitive_archive.analyze_no_sensitive_drive_in_source_clean(root)

            self.assertTrue(any("NotesEleves.csv" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
