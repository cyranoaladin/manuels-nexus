from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATOMS = ROOT / "audit" / "OFFICIAL_PROGRAM_ATOMS_2026_2027.json"


def test_corrected_1spe_atoms_use_clean_official_scope() -> None:
    atoms = json.loads(ATOMS.read_text(encoding="utf-8"))["atoms"]
    choose_form = next(
        atom
        for atom in atoms
        if atom["manual"] == "1SPE"
        and "Choisir une forme adaptée" in atom["short_official_wording_or_paraphrase"]
    )
    norm_identities = next(
        atom
        for atom in atoms
        if atom["manual"] == "1SPE"
        and "Formule d’Al-Kashi" in atom["short_official_wording_or_paraphrase"]
        and "Développement" in atom["short_official_wording_or_paraphrase"]
    )

    assert choose_form["type"] in {"MANDATORY_CAPACITY", "MANDATORY_SKILL"}
    assert choose_form["mandatory"] == "YES"
    assert "référentiel" not in choose_form["short_official_wording_or_paraphrase"]
    assert norm_identities["type"] == "MANDATORY_KNOWLEDGE"
    assert norm_identities["mandatory"] == "YES"
    assert "médiane" not in norm_identities["short_official_wording_or_paraphrase"]


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
    # La campagne diacritiques a accentue le titre : la recherche est faite
    # sans accents pour rester vraie dans les deux graphies.
    import unicodedata

    def _plain(text: str) -> str:
        decomposed = unicodedata.normalize("NFD", text)
        return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")

    plain_course = _plain(course)
    assert plain_course.index(_plain("Approfondissement — Vers la Terminale")) < plain_course.index(
        "Formule de la mediane"
    )
    for stem in ("045", "048", "050"):
        for folder, prefix in (("exercices", "EX"), ("corriges", "CO")):
            text = (chapter / folder / f"1SPE-PRODSCAL-{prefix}-{stem}.tex").read_text(encoding="utf-8")
            assert '"programme_alignment":"OPTIONAL_EXTENSION"' in text
            assert '"extension_codes":["X1"]' in text
            assert "Approfondissement — Vers la Terminale" in text
