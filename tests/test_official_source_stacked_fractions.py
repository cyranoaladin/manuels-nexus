"""Une fraction du programme officiel ne doit jamais arriver à plat.

Le texte extrait du PDF officiel conserve la *disposition* d'une fraction, pas
sa structure : le numérateur se retrouve sur la ligne du dessus, le
dénominateur sur celle du dessous, et la ligne de texte garde un blanc à
l'endroit de la barre. Joindre ces lignes dans l'ordre de lecture produit une
phrase qui ne veut rien dire :

    « ... Si m 2σ désigne la moyenne d'un échantillon, calculer la proportion
    des cas où l'écart entre m et μ est inférieur ou égal à . √n »

Une revue humaine a refusé cette représentation : elle ne peut pas être
attestée fidèle au programme officiel. Ce module fige la correction.

Ce qui identifie la fraction n'est pas deviné : c'est l'alignement des deux
étages sur une même colonne, et le fait que cette colonne tombe dans un blanc
de la ligne qu'ils encadrent. Cet alignement EST la barre de fraction.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_official_source_segments as gate  # noqa: E402

BO_1SPE = ROOT / "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt"
SEGMENTS = ROOT / "audit/OFFICIAL_SOURCE_SEGMENTS_2026_2027.json"
LEDGER = ROOT / "audit/OFFICIAL_SOURCE_SEGMENT_LEDGER.json"
COVERAGE = ROOT / "audit/OFFICIAL_PROGRAM_COVERAGE_2026_2027.json"
REFERENTIAL = (
    ROOT
    / "Mathematiques/manuel-maths/referentiel/capacites_1SPE_VARIABLES_ALEATOIRES.json"
)

#: L'atome 179 du programme applicable : la condition porte sur 2σ/√n.
ATOM_179 = "1SPE-OFFICIAL-179"
FRACTION = "2\U0001d70e/√n"


# ---------------------------------------------------------------------------
#  Le cas réel, tel que le document officiel le dispose
# ---------------------------------------------------------------------------


def test_the_official_source_still_lays_the_fraction_out_in_two_storeys() -> None:
    """Si le document changeait, la correction ne s'appliquerait plus au même endroit."""

    lines = BO_1SPE.read_text(encoding="utf-8").split("\n")
    numerator, text, denominator = lines[664], lines[665], lines[666]

    assert numerator.strip() == "2\U0001d70e"
    assert denominator.strip() == "√n"
    # Les deux étages partagent leur colonne : c'est la barre de fraction.
    assert gate._column(numerator) == gate._column(denominator) == 125
    # Et cette colonne tombe dans un blanc de la ligne encadrée.
    assert "inférieur ou égal à" in text
    assert text[119:130].isspace()


def test_the_fraction_is_recomposed_at_the_gap_it_left() -> None:
    lines = BO_1SPE.read_text(encoding="utf-8").split("\n")

    folded, records = gate.fold_stacked_fractions(lines)

    fraction = next(row for row in records if row["fraction"] == FRACTION)
    assert fraction["numerator_line"] == 665
    assert fraction["text_line"] == 666
    assert fraction["denominator_line"] == 667
    assert fraction["shared_column"] == 125
    assert folded[665].strip().endswith(
        f"est inférieur ou égal à {FRACTION}."
    )


def test_the_folded_lines_keep_the_line_numbering_intact() -> None:
    """Les ancres de source nomment des lignes du document officiel.

    Supprimer les deux étages décalerait toutes les lignes suivantes et
    ferait mentir chaque ancre du registre.
    """

    lines = BO_1SPE.read_text(encoding="utf-8").split("\n")

    folded, _ = gate.fold_stacked_fractions(lines)

    assert len(folded) == len(lines)
    assert folded[664] == gate.FOLDED_INTO_NEIGHBOUR
    assert folded[666] == gate.FOLDED_INTO_NEIGHBOUR


# ---------------------------------------------------------------------------
#  La structure analogue, sur des cas construits
# ---------------------------------------------------------------------------


def stacked(numerator: str, denominator: str, *, column: int = 40) -> list[str]:
    """Trois lignes disposées comme le PDF dispose une fraction."""

    pad = " " * column
    return [
        "  Un enonce qui commence et s'interrompt",
        pad + numerator,
        "  se poursuit et se termine par             .",
        pad + denominator,
        "",
    ]


@pytest.mark.parametrize(
    ("numerator", "denominator"),
    [
        ("2\U0001d70e", "√n"),
        ("d\U0001d466", "d\U0001d465"),
        ("1", "n"),
        ("σ", "√n"),
        ("a+b", "2"),
    ],
)
def test_any_two_storey_fraction_is_recomposed(
    numerator: str, denominator: str
) -> None:
    folded, records = gate.fold_stacked_fractions(stacked(numerator, denominator))

    assert len(records) == 1
    assert records[0]["fraction"] == f"{numerator}/{denominator}"
    assert f"{numerator}/{denominator}." in folded[2]


def test_two_storeys_at_different_columns_are_not_a_fraction() -> None:
    """Sans alignement, il n'y a pas de barre — et donc rien à recomposer."""

    lines = stacked("2\U0001d70e", "√n")
    lines[3] = " " * 12 + "√n"

    _, records = gate.fold_stacked_fractions(lines)

    assert records == []


def test_a_gap_that_does_not_span_the_column_is_not_a_fraction() -> None:
    lines = stacked("2\U0001d70e", "√n", column=90)

    _, records = gate.fold_stacked_fractions(lines)

    assert records == []


def test_a_sentence_is_never_taken_for_a_numerator() -> None:
    lines = stacked("2\U0001d70e", "√n")
    lines[1] = " " * 40 + "designe la moyenne."

    _, records = gate.fold_stacked_fractions(lines)

    assert records == []


def test_a_bullet_line_is_never_taken_for_a_storey() -> None:
    lines = stacked("2\U0001d70e", "√n")
    lines[1] = " " * 40 + "− 2\U0001d70e"

    _, records = gate.fold_stacked_fractions(lines)

    assert records == []


# ---------------------------------------------------------------------------
#  Ce que la chaîne dérivée doit porter
# ---------------------------------------------------------------------------


def published(path: Path) -> dict:
    if not path.is_file():
        pytest.skip(f"artefact absent : {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def test_no_published_segment_carries_a_flattened_fraction() -> None:
    """La signature du défaut : un « à . » suivi plus loin d'un dénominateur."""

    payload = published(SEGMENTS)
    offenders = [
        row["segment_id"]
        for row in payload["segments"]
        if "égal à . " in row["source_wording_short"]
        or "égal à .√" in row["source_wording_short"]
    ]
    assert offenders == []


def test_the_1spe_segment_179_states_the_official_condition() -> None:
    payload = published(SEGMENTS)
    row = next(
        item
        for item in payload["segments"]
        if item["segment_id"] == "1SPE-SOURCE-SEG-179"
    )

    assert row["source_anchor"] == "lines:664-667"
    assert row["source_wording_short"].endswith(
        f"est inférieur ou égal à {FRACTION}."
    )
    assert "Si m désigne la moyenne" in row["source_wording_short"]


def test_the_recomposition_is_declared_in_the_artifact() -> None:
    payload = published(SEGMENTS)
    folds = payload["source_documents"]["1SPE"]["stacked_fractions_recomposed"]

    assert [row["fraction"] for row in folds] == ["d\U0001d466/d\U0001d465", FRACTION]


def test_the_atom_and_the_capacity_carry_the_corrected_wording() -> None:
    """Ce que le relecteur voit doit être ce que le programme dit."""

    coverage = published(COVERAGE)
    atom = next(
        row for row in coverage["rows"] if row["atom_id"] == ATOM_179
    )
    assert atom["official_wording_or_short_paraphrase"].endswith(
        f"est inférieur ou égal à {FRACTION}."
    )

    referential = published(REFERENTIAL)
    c7 = next(
        row
        for row in referential["capacites"]
        if row["id"].endswith("C7")
    )
    assert FRACTION in c7["libelle_bo"]
    assert "égal à . " not in c7["libelle_bo"]
    assert ATOM_179 in c7["atomes_officiels"]
