"""« Le référentiel ne déclare pas cette capacité » ne veut pas dire hors programme.

Deux capacités de Variables aléatoires n'avaient aucune entrée locale. Lu vite,
cela invite à les supprimer. Ce serait l'inverse de ce qu'il fallait faire :
les atomes officiels 175 à 179 leur sont rattachés, tous obligatoires, tous
issus du programme applicable à la rentrée 2026-2027.

Ce module vérifie que la réparation va dans le bon sens — l'autorité officielle
écrit, le référentiel enregistre — et que la mesure refuse un référentiel qui
inventerait un attendu ou crédirait un atome à deux capacités.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_referential_capacity_closure as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Le mapping officiel, tel que la revue l'a établi
# ---------------------------------------------------------------------------

EXPECTED_MAPPING = {
    "1SPE-VARIABLES-ALEATOIRES-C6": [
        "1SPE-OFFICIAL-175",
        "1SPE-OFFICIAL-176",
        "1SPE-OFFICIAL-177",
    ],
    "1SPE-VARIABLES-ALEATOIRES-C7": ["1SPE-OFFICIAL-178", "1SPE-OFFICIAL-179"],
}


@pytest.mark.parametrize("capacity", sorted(EXPECTED_MAPPING))
def test_the_official_atoms_are_the_ones_the_review_named(capacity: str) -> None:
    entries = json.loads(
        (
            ROOT
            / "Mathematiques/manuel-maths/referentiel"
            / "capacites_1SPE_VARIABLES_ALEATOIRES.json"
        ).read_text(encoding="utf-8")
    )["capacites"]
    row = next(entry for entry in entries if entry["id"] == capacity)

    assert row["atomes_officiels"] == EXPECTED_MAPPING[capacity]
    assert row["source_officielle_nor"] == [gate.APPLICABLE_NOR]


@pytest.mark.parametrize("capacity", sorted(EXPECTED_MAPPING))
def test_the_bo_wording_is_carried_verbatim_never_written_here(
    capacity: str,
) -> None:
    """Un libellé BO se recopie ; le rédiger serait inventer le programme."""

    official = gate.official_atoms()[capacity]
    entries = json.loads(
        (
            ROOT
            / "Mathematiques/manuel-maths/referentiel"
            / "capacites_1SPE_VARIABLES_ALEATOIRES.json"
        ).read_text(encoding="utf-8")
    )["capacites"]
    row = next(entry for entry in entries if entry["id"] == capacity)

    for atom in official:
        assert atom["wording"] in row["libelle_bo"], atom["atom_id"]
    assert [entry["atom_id"] for entry in row["attendus_officiels"]] == [
        atom["atom_id"] for atom in official
    ]


def test_no_capacity_was_created_or_removed(payload: dict[str, Any]) -> None:
    """La réparation touche le référentiel, jamais la pédagogie."""

    # 55 depuis que le producteur ne s'arrete plus sur une capacite sans
    # `ref_capacite` : trois capacites du second degre n'en portent pas, et le
    # producteur explosait au lieu de les compter -- ce qui les rendait
    # invisibles plutot qu'absentes.
    assert payload["summary"]["CONTRACT_CAPACITIES"] == 55
    # C6 et C7 ont été écrites une fois ; depuis, elles suivent leur autorité.
    # « Réparée » compte une entrée absente, « rafraîchie » une entrée dérivée
    # dont le texte officiel a changé en amont. Les deux touchent le
    # référentiel, jamais la pédagogie.
    assert payload["summary"]["CAPACITIES_REPAIRED"] == 0
    assert payload["summary"]["DERIVED_ENTRY_CONTRADICTING_AUTHORITY"] == 0
    assert "Aucune capacite n'est creee" in payload["nothing_pedagogical_was_touched"]
    for row in payload["repaired"] + payload["refreshed_from_authority"]:
        assert row["capacity"].endswith(("C6", "C7"))


def test_the_closure_is_complete_and_within_the_applicable_year(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    for metric in gate.BLOCKING:
        assert summary[metric] == 0, (metric, summary[metric])
    assert payload["applicable_school_year"] == "2026-2027"
    assert payload["applicable_nor"] == "MENE2602917A"


def test_a_capacity_without_direct_credit_is_declared_not_hidden(
    payload: dict[str, Any],
) -> None:
    """Onze capacités n'ont pas d'atome en propre : c'est dit, pas effacé.

    Huit d'entre elles sont celles du second degre -- la totalite du chapitre.
    Son referentiel local compte cinq atomes, aucun n'est credite a une
    capacite, et trois capacites du contrat ne portent meme pas de reference.
    C'est une question editoriale ouverte, remontee au Release Owner : y
    repondre supposerait d'ecrire du texte officiel, ce qu'un producteur ne
    fait pas.
    """

    assert payload["summary"]["CAPACITY_WITHOUT_DIRECT_ATOM_CREDIT"] == 11
    assert len(payload["capacities_without_direct_atom_credit"]) == 11
    second_degre = [
        row for row in payload["capacities_without_direct_atom_credit"]
        if row["chapter"] == "1SPE-SECOND-DEGRE"
    ]
    assert len(second_degre) == 8
    assert sum(1 for row in second_degre if row["capacity"] is None) == 3
    assert "pas un trou de programme" in (
        payload["why_a_capacity_without_direct_credit_is_not_a_gap"]
    )
    # Et ce n'est pas bloquant : réattribuer un atome est un jugement humain.
    assert "CAPACITY_WITHOUT_DIRECT_ATOM_CREDIT" not in gate.BLOCKING


# ---------------------------------------------------------------------------
#  Ce que la mesure doit refuser
# ---------------------------------------------------------------------------


def test_a_matrix_of_the_wrong_year_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stale = tmp_path / "ancienne.json"
    stale.write_text(
        json.dumps({"applicable_school_year": "2019-2020", "rows": []}),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "OFFICIAL", stale)

    with pytest.raises(gate.ClosureError, match="annee applicable"):
        gate.official_atoms()


def test_an_atom_credited_to_two_capacities_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un même attendu compté deux fois ferait croire à une couverture double."""

    doubled = tmp_path / "double.json"
    row = {
        "manual": "1SPE",
        "atom_id": "1SPE-OFFICIAL-176",
        "NOR": gate.APPLICABLE_NOR,
        "mandatory": "YES",
        "obligation_type": "MANDATORY_ALGORITHM",
        "official_section": "Variables aléatoires réelles",
        "official_page_or_anchor": "lines:660",
        "official_wording_or_short_paraphrase": "Simuler une variable aléatoire.",
    }
    doubled.write_text(
        json.dumps(
            {
                "applicable_school_year": gate.APPLICABLE_YEAR,
                "rows": [
                    {**row, "contract_capacity": "1SPE-VARIABLES-ALEATOIRES-C6"},
                    {**row, "contract_capacity": "1SPE-VARIABLES-ALEATOIRES-C7"},
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "OFFICIAL", doubled)

    result = gate.build(write=False)

    assert result["summary"]["ATOM_CREDITED_TO_A_FOREIGN_CAPACITY"] == 1
    assert gate.main(["--check"]) == 1


def test_an_atom_of_another_programme_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    foreign = tmp_path / "hors-annee.json"
    foreign.write_text(
        json.dumps(
            {
                "applicable_school_year": gate.APPLICABLE_YEAR,
                "rows": [
                    {
                        "manual": "1SPE",
                        "contract_capacity": "1SPE-VARIABLES-ALEATOIRES-C6",
                        "atom_id": "1SPE-OFFICIAL-999",
                        "NOR": "MENE1921247A",
                        "mandatory": "YES",
                        "obligation_type": "MANDATORY_ALGORITHM",
                        "official_section": "Variables aléatoires réelles",
                        "official_page_or_anchor": "lines:1",
                        "official_wording_or_short_paraphrase": "Un attendu de 2019.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "OFFICIAL", foreign)

    result = gate.build(write=False)

    assert result["summary"]["ATOM_OUT_OF_APPLICABLE_YEAR"] == 1


def test_a_missing_referential_file_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gate, "REFERENTIAL", tmp_path)

    with pytest.raises(gate.ClosureError, match="referentiel absent"):
        gate.build(write=False)
