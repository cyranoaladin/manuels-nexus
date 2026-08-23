from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATOMS = ROOT / "audit" / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"


def test_corrected_1spe_atoms_use_clean_official_scope() -> None:
    atoms = json.loads(ATOMS.read_text(encoding="utf-8"))["atoms"]
    atom_016 = next(atom for atom in atoms if atom["atom_id"] == "1SPE-ATOM-016")
    atom_050 = next(atom for atom in atoms if atom["atom_id"] == "1SPE-ATOM-050")

    assert atom_016["short_official_wording_or_paraphrase"] == (
        "Choisir une forme adaptée d'une fonction polynôme du second degré "
        "pour résoudre un problème (équation, inéquation, optimisation, variations)"
    )
    assert "référentiel" not in atom_016["short_official_wording_or_paraphrase"]
    assert atom_050["short_official_wording_or_paraphrase"] == (
        "Développer les carrés des normes de u+v et u-v ; formule d'Al-Kashi"
    )
    assert "médiane" not in atom_050["short_official_wording_or_paraphrase"]


def test_1spe_median_formula_is_only_an_explicit_extension() -> None:
    chapter = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-PRODUIT-SCALAIRE"
    referential = json.loads(
        (
            ROOT / "Mathematiques" / "manuel-maths" / "referentiel"
            / "capacites_1SPE_PRODUIT_SCALAIRE.json"
        ).read_text(encoding="utf-8")
    )
    capacity_c5 = next(item for item in referential["capacites"] if item["id"].endswith("-C5"))

    assert "médiane" not in capacity_c5["libelle_bo"]
    assert referential["extensions"] == [
        {
            "id": "1SPE-PRODUIT-SCALAIRE-X1",
            "label": "Approfondissement — Vers la Terminale",
            "libelle": "Formule de la médiane, conséquence des identités du produit scalaire",
            "programme_alignment": "OPTIONAL_EXTENSION",
        }
    ]
    course = (chapter / "cours" / "14_C5_al_kashi.tex").read_text(encoding="utf-8")
    assert course.index("Approfondissement — Vers la Terminale") < course.index("Formule de la mediane")
    for stem in ("045", "048", "050"):
        for folder, prefix in (("exercices", "EX"), ("corriges", "CO")):
            text = (chapter / folder / f"1SPE-PRODSCAL-{prefix}-{stem}.tex").read_text(encoding="utf-8")
            assert '"programme_alignment":"OPTIONAL_EXTENSION"' in text
            assert '"extension_codes":["X1"]' in text
            assert "Approfondissement — Vers la Terminale" in text
