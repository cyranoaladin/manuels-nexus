from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import scripts.check_local_drive_traceability as drive_trace


class LocalDriveTraceabilityTest(unittest.TestCase):
    def test_candidate_source_without_trace_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "P01_cours_test.md"
            support.write_text(
                "---\nsource: \"BO 2019 ; ressource locale candidate : Documents_DRIVE/missing.pdf\"\n---\n",
                encoding="utf-8",
            )

            result = drive_trace.analyze_drive_traceability(root, trace_path=root / "support_source_trace.yml")

            self.assertTrue(any("ressource locale candidate" in error for error in result.errors))

    def test_generated_from_program_is_accepted_without_drive_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            support = root / "P01_cours_test.md"
            support.write_text(
                "---\nsource: \"BO 2019\"\nsource_creation: \"generated_from_program\"\n---\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text(
                "supports:\n"
                "  - support: P01_cours_test.md\n"
                "    source_officielle: BO 2019\n"
                "    source_locale_drive: ''\n"
                "    type_reprise: création originale\n"
                "    hash_source: ''\n"
                "    statut_rgpd: non concerné\n"
                "    statut_relecture: needs_review\n",
                encoding="utf-8",
            )

            result = drive_trace.analyze_drive_traceability(root, trace_path=root / "support_source_trace.yml")

            self.assertEqual(result.errors, [])

    def test_backticked_drive_path_with_spaces_is_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            workspace = Path(raw)
            root = workspace / "repo"
            root.mkdir()
            drive = workspace / "Documents_DRIVE"
            source = drive / "dossier avec espaces" / "source.pdf"
            source.parent.mkdir(parents=True)
            source.write_text("source", encoding="utf-8")
            support = root / "P01_cours_test.md"
            support.write_text(
                "---\nsource_creation: adapted_from_drive\nstatus: needs_review\n---\n"
                "Source : `Documents_DRIVE/dossier avec espaces/source.pdf`\n",
                encoding="utf-8",
            )
            digest = drive_trace.sha256(source)
            (root / "support_source_trace.yml").write_text(
                "supports:\n"
                "  - support: P01_cours_test.md\n"
                "    source_officielle: BO 2019\n"
                "    source_locale_drive: Documents_DRIVE/dossier avec espaces/source.pdf\n"
                "    type_reprise: adaptation_drive\n"
                f"    hash_source: {digest}\n"
                "    statut_rgpd: conforme\n"
                "    statut_relecture: needs_review\n",
                encoding="utf-8",
            )

            result = drive_trace.analyze_drive_traceability(root, trace_path=root / "support_source_trace.yml")

            self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main()
