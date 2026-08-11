import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class Lot1DriveGateBoundaryTests(unittest.TestCase):
    def test_policy_documents_clone_clean_and_drive_required_gates(self) -> None:
        policy = (ROOT / "qa_gate_policy.md").read_text(encoding="utf-8")

        self.assertIn("Gates clone-propre", policy)
        self.assertIn("Gates Drive-requis", policy)
        self.assertIn("scripts/check_drive_enrichment_traceability.py", policy)
        self.assertIn("scripts/check_drive_enrichment_traceability_portable.py", policy)

    def test_portable_audit_and_ci_do_not_call_drive_required_gates(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        audit_extracted = makefile.split("audit-extracted-source:", 1)[1].split("\n\n", 1)[0]
        drive_required = {
            "scripts.check_local_drive_traceability",
            "scripts.check_drive_integration_plan",
            "scripts.check_drive_enrichment_traceability\n",
        }

        for command in drive_required:
            self.assertNotIn(command, audit_extracted)
            self.assertNotIn(command, ci)

    def test_drive_required_gate_fails_loudly_when_drive_root_is_empty(self) -> None:
        import scripts.check_drive_enrichment_traceability as local_drive_gate

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "repo"
            root.mkdir()
            (root.parent / "Documents_DRIVE").mkdir()
            (root / "reports").mkdir()
            digest = hashlib.sha256(b"source").hexdigest()
            (root / "drive_inventory.csv").write_text(
                "drive_url,drive_folder,file_name,mime_type,local_copy,sha256,niveau,theme,"
                "sequence,qualite_initiale,decision,raison\n"
                f"url,folder,source.pdf,application/pdf,Documents_DRIVE/source.pdf,{digest},"
                "premiere,theme,P01,non_auditee,integrated_adapted,adapté\n",
                encoding="utf-8",
            )
            (root / "support_source_trace.yml").write_text(
                "supports:\n"
                "  - support: support.md\n"
                "    source_locale_drive: Documents_DRIVE/source.pdf\n"
                "    type_reprise: adaptation_drive\n"
                "    statut_rgpd: conforme\n"
                "    hash_source: " + digest + "\n"
                "    statut_relecture: needs_review\n",
                encoding="utf-8",
            )
            (root / "support.md").write_text("---\nstatus: needs_review\n---\n", encoding="utf-8")
            (root / "reports" / "drive_enrichment_report.md").write_text(
                "| Ressource Drive | Existe localement | Hash | Décision | Support enrichi | "
                "Type de reprise | RGPD | Statut final | Commentaire |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                f"| source.pdf | oui | {digest} | integrated_adapted | support.md | "
                "adaptation_drive | conforme | needs_review | test |\n",
                encoding="utf-8",
            )

            result = local_drive_gate.analyze_drive_enrichment_traceability(root)

        self.assertTrue(result.errors)
        self.assertTrue(any("copie locale absente" in error for error in result.errors), result.errors)


if __name__ == "__main__":
    unittest.main()
