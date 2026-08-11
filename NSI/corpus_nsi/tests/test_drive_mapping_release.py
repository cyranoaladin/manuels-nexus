from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_drive_mapping_release as drive_release


FIELDS = (
    "drive_url,drive_folder,file_name,mime_type,local_copy,sha256,niveau,theme,"
    "sequence_possible,qualite_initiale,decision,raison\n"
)


class DriveMappingReleaseTest(unittest.TestCase):
    def test_release_reports_classified_drive_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "drive_inventory.csv").write_text(
                FIELDS
                + "url,folder,source.pdf,application/pdf,Documents_DRIVE/source.pdf,abc,premiere,theme,P01,non_auditee,integrated_adapted,adapté\n"
                + "url,folder,missing.pdf,application/pdf,NA_REMOTE_NOT_DOWNLOADED,NA_REMOTE_NOT_DOWNLOADED,premiere,theme,P01,non_auditee,missing_local_copy,absent\n"
                + "url,folder,NotesEleves.csv,text/csv,NA_REMOTE_NOT_DOWNLOADED,NA_REMOTE_NOT_DOWNLOADED,premiere,donnees_eleves,NA,non_publiable,rejected_sensitive,sensible\n",
                encoding="utf-8",
            )

            errors = drive_release.analyze_drive_mapping_release(root)

            joined = "\n".join(errors)
            self.assertIn("missing_local_copy=1", joined)
            self.assertIn("rejected_sensitive=1", joined)
            self.assertIn("missing.pdf", joined)
            self.assertNotIn("non intégrées localement: source.pdf", joined)


if __name__ == "__main__":
    unittest.main()
