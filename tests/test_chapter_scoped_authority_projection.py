"""Une ligne d'autorité d'un autre chapitre ne périme pas ce gel-ci.

Le contrat de fraîcheur le déclare depuis longtemps —
`authority_line_of_another_chapter: NOT_STALE` — mais la projection par
chapitre n'était appliquée qu'à un seul des quatre chemins d'autorité. Les
trois autres étaient comparés fichier entier. Corriger un atome de Variables
aléatoires périmait donc le gel de Suites, alors que le contenu de Suites
n'avait pas bougé d'un octet : douze tests rouges pour un faux positif.

Ces trois artefacts ne portent pas `chapter` sur leurs lignes. Le rattachement
est donc dérivé de la chaîne canonique — segment → atomes → chapitre — dont la
matrice de couverture est l'autorité. Rien n'est déduit du texte libre, du nom
de fichier, d'une heuristique lexicale ni de la position d'une ligne.

Ce qui ne peut pas être rattaché n'est jamais attribué au hasard : la ligne est
conservée dans la projection de chaque chapitre. Échouer fermé, pour qu'une
vraie modification de programme ne disparaisse jamais du calcul.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_suites_review_source_freeze as freeze  # noqa: E402

COVERAGE = "audit/official_program_coverage/1SPE.json"
LEDGER = "audit/OFFICIAL_SOURCE_SEGMENT_LEDGER.json"
CROSSWALK = "audit/OFFICIAL_SOURCE_ATOM_CROSSWALK_2026_2027.json"
SECOND_PASS = "audit/OFFICIAL_ATOMIZATION_SECOND_PASS.json"

#: Les trois artefacts qui provoquaient le faux positif.
NEWLY_SCOPED = (LEDGER, CROSSWALK, SECOND_PASS)

#: Le segment corrigé par la revue humaine : sa formule 2σ/√n appartient à
#: l'atome 179, donc au chapitre Variables aléatoires.
VARALEA_SEGMENT = "1SPE-SOURCE-SEG-179"


def payload(path: str) -> bytes:
    return (ROOT / path).read_bytes()


def rows_of(path: str, document: dict[str, Any]) -> list[dict[str, Any]]:
    return document[freeze._AUTHORITY_ROW_KEYS[path]]


def mutate(path: str, predicate) -> bytes:
    """Édite les lignes retenues par `predicate`, laisse les autres intactes."""

    document = json.loads(payload(path).decode("utf-8"))
    touched = 0
    for row in rows_of(path, document):
        if predicate(row):
            row["__edit__"] = "modifiee pour le test"
            touched += 1
    assert touched, (path, "aucune ligne a editer : le cas de test est vide")
    return json.dumps(document, ensure_ascii=False).encode("utf-8")


def chapter_of(row: dict[str, Any]) -> set[str] | None:
    return freeze._row_chapters(row, freeze._atom_chapters(), freeze._segment_atoms())


def belongs_to(chapter: str):
    return lambda row: chapter_of(row) == {chapter}


# ---------------------------------------------------------------------------
#  Les quatre chemins d'autorité sont désormais projetés
# ---------------------------------------------------------------------------


def test_the_four_authority_paths_are_chapter_scoped() -> None:
    assert set(freeze.CHAPTER_SCOPED_AUTHORITY_PATHS) == {
        COVERAGE,
        LEDGER,
        CROSSWALK,
        SECOND_PASS,
    }


def test_the_coverage_matrix_remains_the_behavioural_reference() -> None:
    """Le chemin déjà correct n'a pas changé de comportement."""

    document = json.loads(payload(COVERAGE).decode("utf-8"))
    assert any("chapter" in row for row in document["rows"])

    before = freeze.programme_authority_projection(COVERAGE, payload(COVERAGE))
    foreign = mutate(COVERAGE, lambda row: row.get("chapter") != freeze.CHAPTER_ID)

    assert freeze.programme_authority_projection(COVERAGE, foreign) == before


# ---------------------------------------------------------------------------
#  1 & 3 — une ligne d'un autre chapitre ne périme pas SUITES
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", NEWLY_SCOPED)
def test_a_varalea_line_does_not_stale_suites(path: str) -> None:
    """Le cas réel : la correction C7 touche Variables aléatoires, pas Suites."""

    before = freeze.programme_authority_projection(path, payload(path))
    edited = mutate(path, belongs_to("1SPE-VARIABLES-ALEATOIRES"))

    assert freeze.programme_authority_projection(path, edited) == before


@pytest.mark.parametrize("path", NEWLY_SCOPED)
def test_a_georep_line_does_not_stale_suites(path: str) -> None:
    before = freeze.programme_authority_projection(path, payload(path))
    edited = mutate(path, belongs_to("1SPE-GEOMETRIE-REPEREE"))

    assert freeze.programme_authority_projection(path, edited) == before


# ---------------------------------------------------------------------------
#  2 — une ligne du chapitre lui-même périme bien le gel
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", NEWLY_SCOPED)
def test_a_suites_line_still_stales_suites(path: str) -> None:
    """La correction ne doit pas affaiblir la détection réelle."""

    before = freeze.programme_authority_projection(path, payload(path))
    edited = mutate(path, belongs_to(freeze.CHAPTER_ID))

    assert freeze.programme_authority_projection(path, edited) != before


@pytest.mark.parametrize("path", NEWLY_SCOPED)
def test_the_chapter_actually_owns_lines_in_each_artifact(path: str) -> None:
    """Un test de non-régression vide ne prouverait rien."""

    document = json.loads(payload(path).decode("utf-8"))
    owned = [row for row in rows_of(path, document) if chapter_of(row) == {freeze.CHAPTER_ID}]

    assert owned, path


# ---------------------------------------------------------------------------
#  4 — ce qui n'est pas rattachable est conservé, jamais attribué au hasard
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", NEWLY_SCOPED)
def test_an_unattributable_line_is_kept_not_guessed(path: str) -> None:
    """Échouer fermé : une ligne sans atome connu reste dans la projection."""

    document = json.loads(payload(path).decode("utf-8"))
    orphans = [row for row in rows_of(path, document) if chapter_of(row) is None]
    assert orphans, (path, "aucune ligne non rattachable : le cas est vide")

    before = freeze.programme_authority_projection(path, payload(path))
    edited = mutate(path, lambda row: chapter_of(row) is None)

    # Conservée dans TOUTES les projections : la modifier périme donc ce gel.
    assert freeze.programme_authority_projection(path, edited) != before


def test_a_line_citing_an_unknown_atom_is_not_attributed() -> None:
    row = {"segment_id": "INEXISTANT", "atom_ids": ["1SPE-OFFICIAL-999999"]}

    assert freeze._row_chapters(row, freeze._atom_chapters(), freeze._segment_atoms()) is None


def test_a_line_citing_no_atom_at_all_is_not_attributed() -> None:
    row = {"segment_id": "1SPE-SOURCE-SEG-001", "first_pass_atom_ids": []}

    chapters = freeze._row_chapters(
        row, freeze._atom_chapters(), freeze._segment_atoms()
    )
    assert chapters is None


# ---------------------------------------------------------------------------
#  5 — aucun atome rattaché à deux chapitres
# ---------------------------------------------------------------------------


def test_no_atom_is_credited_to_two_chapters() -> None:
    collisions = {
        atom: sorted(chapters)
        for atom, chapters in freeze._atom_chapters().items()
        if len(chapters) > 1
    }

    assert collisions == {}


def test_the_attachment_comes_only_from_the_canonical_matrix() -> None:
    """Aucune table parallèle : le lien est lu là où il fait autorité."""

    assert freeze.COVERAGE_MATRIX_PATH == COVERAGE
    source = (ROOT / "scripts/build_1spe_suites_review_source_freeze.py").read_text(
        encoding="utf-8"
    )
    # Le rattachement se lit dans la matrice et le registre d'atomes, pas dans
    # un dictionnaire ecrit a la main.
    assert "_atom_chapters" in source and "_segment_atoms" in source


# ---------------------------------------------------------------------------
#  6 — déterminisme
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", (COVERAGE,) + NEWLY_SCOPED)
def test_the_projection_is_deterministic(path: str) -> None:
    digests = {
        freeze.programme_authority_projection(path, payload(path)) for _ in range(3)
    }

    assert len(digests) == 1


@pytest.mark.parametrize("path", (COVERAGE,) + NEWLY_SCOPED)
def test_a_pure_envelope_refresh_does_not_change_the_projection(path: str) -> None:
    """Régénérer un artefact sans changer une ligne ne périme rien.

    C'est ce que le contrat appelle `derived_envelope_refreshed: NOT_STALE`.
    Le crosswalk en est l'illustration exacte : ses 985 lignes étaient
    inchangées après la correction, et sa seule enveloppe suffisait à périmer
    tous les chapitres.
    """

    document = json.loads(payload(path).decode("utf-8"))
    before = freeze.programme_authority_projection(path, payload(path))
    document["source_digest"] = "sha256:" + "0" * 64
    document["summary"] = {"regenere": True}
    refreshed = json.dumps(document, ensure_ascii=False).encode("utf-8")

    assert freeze.programme_authority_projection(path, refreshed) == before


# ---------------------------------------------------------------------------
#  7 — le cas réel qui a provoqué les douze échecs
# ---------------------------------------------------------------------------


def test_the_c7_correction_belongs_to_variables_aleatoires() -> None:
    """Le segment corrigé porte l'atome 179, rattaché à Variables aléatoires."""

    document = json.loads(payload(LEDGER).decode("utf-8"))
    row = next(r for r in document["rows"] if r["segment_id"] == VARALEA_SEGMENT)

    assert row["first_pass_atom_ids"] == ["1SPE-OFFICIAL-179"]
    assert chapter_of(row) == {"1SPE-VARIABLES-ALEATOIRES"}
    assert "2\U0001d70e/√n" in row["source_wording_short"]


def test_the_suites_freeze_is_current_without_any_re_freeze() -> None:
    binding = json.loads(
        (ROOT / "audit/1SPE_SUITES_CURRENT_FREEZE_BINDING.json").read_text(
            encoding="utf-8"
        )
    )

    assert binding["binding_state"] == "CURRENT_EQUIVALENT_TO_FROZEN_CONTENT"
    assert binding["programme_authority_identity_pass"] is True
    assert binding["findings"]["programme_authority_drift"] == []
    # Le contenu du chapitre n'a jamais bougé : c'est bien le calcul de
    # fraîcheur qui était trop large, et le gel n'a pas été refait.
    assert binding["freeze_content_projection"] == binding["current_object_set_digest"]
    assert binding["findings"]["modified_objects"] == []
    assert binding["findings"]["missing_objects"] == []
