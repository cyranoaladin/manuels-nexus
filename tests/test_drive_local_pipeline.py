from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.drive_local_inventory as drive_local_inventory
import scripts.drive_resource_triage as drive_resource_triage


FIELDS = (
    "drive_url,drive_folder,file_name,mime_type,local_copy,sha256,niveau,theme,"
    "sequence_possible,qualite_initiale,decision,raison\n"
)


class DriveLocalPipelineTest(unittest.TestCase):
    def test_local_inventory_hashes_files_and_flags_sensitive_names(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            drive = Path(raw) / "Documents_DRIVE"
            drive.mkdir()
            normal = drive / "cours.pdf"
            normal.write_text("cours", encoding="utf-8")
            sensitive = drive / "NotesEleves.csv"
            sensitive.write_text("nom,note\n", encoding="utf-8")

            entries = drive_local_inventory.collect_local_inventory(drive)
            by_name = {entry.file_name: entry for entry in entries}

            self.assertEqual(by_name["cours.pdf"].sensitive, "non")
            self.assertEqual(len(by_name["cours.pdf"].sha256), 64)
            self.assertEqual(by_name["NotesEleves.csv"].sensitive, "oui")

    def test_resource_triage_marks_existing_refactor_as_deferred_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            drive = root.parent / "Documents_DRIVE"
            drive.mkdir()
            source = drive / "cours.pdf"
            source.write_text("cours", encoding="utf-8")
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + "url,folder,cours.pdf,application/pdf,NA_REMOTE_NOT_DOWNLOADED,NA_REMOTE_NOT_DOWNLOADED,premiere,theme,P01,non_auditee,refactor,à auditer\n",
                encoding="utf-8",
            )

            rows = drive_resource_triage.triage_inventory(root, write=False)

            self.assertEqual(rows[0]["local_copy"], "Documents_DRIVE/cours.pdf")
            self.assertEqual(len(rows[0]["sha256"]), 64)
            self.assertEqual(rows[0]["decision"], "deferred")
            self.assertIn("copie locale trouvée", rows[0]["raison"])
            self.assertIn("NA_REMOTE_NOT_DOWNLOADED", (root / "drive_inventory.csv").read_text(encoding="utf-8"))

    def test_resource_triage_rejects_sensitive_existing_resource(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            drive = root.parent / "Documents_DRIVE"
            drive.mkdir()
            source = drive / "Fichier_Eleves.csv"
            source.write_text("nom,classe\n", encoding="utf-8")
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + "url,folder,Fichier_Eleves.csv,text/csv,NA_REMOTE_NOT_DOWNLOADED,NA_REMOTE_NOT_DOWNLOADED,premiere,donnees_eleves,P01,non_publiable,refactor,à auditer\n",
                encoding="utf-8",
            )

            rows = drive_resource_triage.triage_inventory(root, write=False)

            self.assertEqual(rows[0]["decision"], "rejected_sensitive")
            self.assertEqual(rows[0]["qualite_initiale"], "non_publiable")


if __name__ == "__main__":
    unittest.main()
