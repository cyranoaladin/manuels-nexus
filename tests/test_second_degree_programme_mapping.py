"""La scission locale signe/factorisation et la famille de trinômes ont leur preuve."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "audit/official_program_coverage/1SPE.json"


def _row(atom):
    return next(r for r in json.loads(MATRIX.read_text())["rows"] if r["atom_id"] == atom)


def test_factorized_sign_is_attached_to_sign_capacity():
    row = _row("1SPE-OFFICIAL-071")
    assert row["contract_capacity"] == "1SPE-SECOND-DEGRE-C8"
    assert row["method_sources"][0].endswith("1SPE-SECDEG-ME-008.tex")
    assert row["remediation_sources"][0].endswith("1SPE-SECDEG-RE-C8.tex")


def test_two_roots_requirement_uses_the_new_family_content():
    row = _row("1SPE-OFFICIAL-072")
    assert row["contract_capacity"] == "1SPE-SECOND-DEGRE-C7"
    assert row["course_sources"][0].endswith("16_C7_somme_produit_racines.tex")
    assert row["exercise_sources"][0].endswith("1SPE-SECDEG-EX-101.tex")
    assert row["correction_sources"][0].endswith("1SPE-SECDEG-CO-101.tex")
    # Le rattachement programme n'est ni une revue scientifique ni une signature.
    assert row["scientific_state"] == row["pedagogical_state"] == "PENDING"
