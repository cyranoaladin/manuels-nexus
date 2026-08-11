from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_drive_enrichment_traceability as drive_enrichment


FIELDS = (
    "drive_url,drive_folder,file_name,mime_type,local_copy,sha256,niveau,theme,"
    "sequence_possible,qualite_initiale,decision,raison\n"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def write_minimal_report(root: Path, name: str = "source.pdf") -> None:
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "drive_enrichment_report.md").write_text(
        "| Ressource Drive | Existe localement | Hash | Décision | Support enrichi | Type de reprise | RGPD | Statut final | Commentaire |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        f"| {name} | oui | hash | integrated_adapted | support.md | adaptation | conforme | needs_review | test |\n",
        encoding="utf-8",
    )


class DriveEnrichmentTraceabilityTest(unittest.TestCase):
    def test_drive_gate_rejects_absent_or_empty_documents_drive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            (root / "drive_inventory.csv").write_text(FIELDS, encoding="utf-8")
            (root / "support_source_trace.yml").write_text("supports: []\n", encoding="utf-8")
            write_minimal_report(root)

            absent_result = drive_enrichment.analyze_drive_enrichment_traceability(root)
            self.assertTrue(any("Documents_DRIVE" in error and "absent" in error for error in absent_result.errors))

            drive = root.parent / "Documents_DRIVE"
            drive.mkdir()
            empty_result = drive_enrichment.analyze_drive_enrichment_traceability(root)
            self.assertTrue(any("Documents_DRIVE" in error and "vide" in error for error in empty_result.errors))

    def test_integrated_drive_resource_without_hash_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            drive = root.parent / "Documents_DRIVE"
            drive.mkdir(exist_ok=True)
            source = drive / "source.pdf"
            source.write_text("contenu", encoding="utf-8")
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + "url,folder,source.pdf,application/pdf,Documents_DRIVE/source.pdf,,premiere,theme,P01,non_auditee,integrated_adapted,adapté\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text(
                "supports:\n"
                "  - support: support.md\n"
                "    source_officielle: BO 2019\n"
                "    source_locale_drive: Documents_DRIVE/source.pdf\n"
                "    type_reprise: adaptation_drive\n"
                "    hash_source: ''\n"
                "    statut_rgpd: conforme\n"
                "    statut_relecture: needs_review\n",
                encoding="utf-8",
            )
            (root / "support.md").write_text("---\nstatus: needs_review\n---\n", encoding="utf-8")
            write_minimal_report(root)

            result = drive_enrichment.analyze_drive_enrichment_traceability(root)

            self.assertTrue(any("sha256 requis" in error or "hash_source requis" in error for error in result.errors))

    def test_integrated_drive_resource_without_rgpd_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            drive = root.parent / "Documents_DRIVE"
            drive.mkdir(exist_ok=True)
            source = drive / "source.pdf"
            source.write_text("contenu", encoding="utf-8")
            digest = sha256(source)
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + f"url,folder,source.pdf,application/pdf,Documents_DRIVE/source.pdf,{digest},premiere,theme,P01,non_auditee,integrated_adapted,adapté\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text(
                "supports:\n"
                "  - support: support.md\n"
                "    source_officielle: BO 2019\n"
                "    source_locale_drive: Documents_DRIVE/source.pdf\n"
                "    type_reprise: adaptation_drive\n"
                f"    hash_source: {digest}\n"
                "    statut_rgpd: ''\n"
                "    statut_relecture: needs_review\n",
                encoding="utf-8",
            )
            (root / "support.md").write_text("---\nstatus: needs_review\n---\n", encoding="utf-8")
            write_minimal_report(root)

            result = drive_enrichment.analyze_drive_enrichment_traceability(root)

            self.assertTrue(any("statut_rgpd" in error for error in result.errors))

    def test_drive_reference_in_support_without_trace_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "drive_inventory.csv").write_text(FIELDS, encoding="utf-8")
            (root / "support_source_trace.yml").write_text("supports: []\n", encoding="utf-8")
            (root / "support.md").write_text(
                "---\nstatus: needs_review\n---\nSource : Documents_DRIVE/source.pdf\n",
                encoding="utf-8",
            )
            write_minimal_report(root)

            result = drive_enrichment.analyze_drive_enrichment_traceability(root)

            self.assertTrue(any("utilisée sans trace" in error for error in result.errors))

    def test_sensitive_student_file_marked_integrated_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            drive = root.parent / "Documents_DRIVE"
            drive.mkdir(exist_ok=True)
            source = drive / "NotesEleves.csv"
            source.write_text("nom,note\nAda,20\n", encoding="utf-8")
            digest = sha256(source)
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + f"url,folder,NotesEleves.csv,text/csv,Documents_DRIVE/NotesEleves.csv,{digest},premiere,donnees_eleves,P01,non_publiable,integrated_adapted,interdit\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text("supports: []\n", encoding="utf-8")
            write_minimal_report(root, name="NotesEleves.csv")

            result = drive_enrichment.analyze_drive_enrichment_traceability(root)

            self.assertTrue(any("ressource sensible" in error for error in result.errors))

    def test_missing_local_copy_marked_integrated_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + "url,folder,missing.pdf,application/pdf,Documents_DRIVE/missing.pdf,abc,premiere,theme,P01,non_auditee,integrated_adapted,adapté\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text("supports: []\n", encoding="utf-8")
            write_minimal_report(root, name="missing.pdf")

            result = drive_enrichment.analyze_drive_enrichment_traceability(root)

            self.assertTrue(any("copie locale absente" in error for error in result.errors))

    def test_valid_adapted_drive_resource_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            drive = root.parent / "Documents_DRIVE"
            drive.mkdir(exist_ok=True)
            source = drive / "source.pdf"
            source.write_text("contenu disciplinaire anonymisé", encoding="utf-8")
            digest = sha256(source)
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + f"url,folder,source.pdf,application/pdf,Documents_DRIVE/source.pdf,{digest},premiere,theme,P01,non_auditee,integrated_adapted,adapté\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text(
                "supports:\n"
                "  - support: support.md\n"
                "    source_officielle: BO 2019\n"
                "    source_locale_drive: Documents_DRIVE/source.pdf\n"
                "    type_reprise: adaptation_drive\n"
                f"    hash_source: {digest}\n"
                "    statut_rgpd: conforme - aucune donnée personnelle intégrée\n"
                "    statut_relecture: needs_review\n",
                encoding="utf-8",
            )
            (root / "support.md").write_text(
                "---\nstatus: needs_review\nsource_creation: adapted_from_drive\n---\nSource : Documents_DRIVE/source.pdf\n",
                encoding="utf-8",
            )
            write_minimal_report(root)

            result = drive_enrichment.analyze_drive_enrichment_traceability(root)

            self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
