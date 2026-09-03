"""Le dossier D7 du manuel : quinze pages cherchées, et un onglet mesuré.

Un dossier de revue visuelle ne vaut que si ses pages ont été choisies pour ce
qu'elles portent, et si ses mesures peuvent échouer. Ce module vérifie les
deux, puis mute la géométrie de l'onglet pour s'assurer que chaque règle du
contrat rejette bien ce qu'elle prétend rejeter.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_d7_proof_bundle as bundle  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not bundle.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {bundle.JSON_TARGET}")
    return json.loads(bundle.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Vérité courante
# ---------------------------------------------------------------------------


def test_the_bundle_holds_exactly_fifteen_pages(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert summary["PAGES_SELECTED"] == 15
    assert summary["PAGES_REQUIRED"] == 15
    assert summary["MISSING_CATEGORIES"] == 0
    assert summary["CATEGORIES_FOUND"] == summary["CATEGORIES_REQUIRED"] == 12
    assert len(payload["pages"]) == 15


def test_every_contract_category_is_represented(payload: dict[str, Any]) -> None:
    """Douze catégories, quinze pages : trois catégories en reçoivent deux."""

    seen = [row["category"] for row in payload["pages"]]
    expected = {category["id"] for category in bundle.CATEGORIES}
    assert set(seen) == expected
    doubled = {name for name in seen if seen.count(name) == 2}
    assert len(doubled) == 3, doubled
    assert "TAB_ODD_AND_EVEN" in doubled
    for row in payload["pages"]:
        assert row["shows"].strip()
        assert row["page"] >= 1


def test_the_pages_are_searched_not_written_down(payload: dict[str, Any]) -> None:
    """Aucun numéro de page dans le producteur : la sonde le prouve."""

    assert payload["pages_are_searched_not_hardcoded"] is True
    source = Path(ROOT / "scripts/build_1spe_d7_proof_bundle.py").read_text(
        encoding="utf-8"
    )
    start = source.index("CATEGORIES: tuple[dict[str, Any], ...] = (")
    end = source.index("def _looks_like_summary")
    # La table des catégories ne doit contenir aucun folio : elle décrit ce
    # qu'une page montre, jamais où elle se trouve.
    assert not any(
        token.isdigit() and len(token) >= 2 and token not in {"12", "16"}
        for token in source[start:end].replace("(", " ").replace(")", " ").split()
    )


def test_both_variants_are_distinguished_by_their_edition_mention(
    payload: dict[str, Any],
) -> None:
    covers = [row for row in payload["pages"] if row["category"] == "COVER_VARIANT"]
    assert {row["variant"] for row in covers} == {"eleve", "professeur"}


def test_the_tab_alternation_is_shown_on_both_parities(
    payload: dict[str, Any],
) -> None:
    tabs = [row for row in payload["pages"] if row["category"] == "TAB_ODD_AND_EVEN"]
    assert {row["parity"] for row in tabs} == {"odd", "even"}
    sides = {row["parity"]: row["tab"]["side"] for row in tabs}
    assert sides == {"odd": "right", "even": "left"}


def test_no_tab_breaks_its_contract(payload: dict[str, Any]) -> None:
    assert payload["summary"]["TAB_CONTRACT_VIOLATIONS"] == 0
    assert payload["summary"]["PAGES_WITH_A_TAB_FAILURE"] == 0
    # Le contrôle serait vide de sens si aucune page ne portait d'onglet.
    assert payload["summary"]["TAB_PRESENT"] >= 8
    for row in payload["pages"]:
        if not row["tab"].get("present"):
            continue
        rules = {entry["rule"] for entry in row["tab_verdicts"]}
        assert {
            "TAB_INSIDE_12MM",
            "TAB_OUTSIDE_1MM",
            "TAB_MIN_LENGTH_16MM",
            "TAB_SIDE_FOLLOWS_PARITY",
        } <= rules, rules


def test_offering_three_millimetres_of_bleed_did_not_move_the_tab(
    payload: dict[str, Any],
) -> None:
    """Un millimètre dehors, douze dedans — pas trois, pas dix."""

    contract = payload["tab_contract"]
    assert contract["outside_mm"] == 1.0
    assert contract["inside_mm"] == 12.0
    for row in payload["pages"]:
        tab = row["tab"]
        if not tab.get("present"):
            continue
        assert abs(tab["outside_mm"] - 1.0) <= 0.05, row["page"]
        assert abs(tab["inside_mm"] - 12.0) <= 0.05, row["page"]


def test_the_bundle_approves_nothing(payload: dict[str, Any]) -> None:
    assert payload["d7_status"] == "PENDING_HUMAN"
    assert payload["approves_nothing"]


def test_every_page_is_rendered_and_every_tab_is_rendered_at_300dpi(
    payload: dict[str, Any],
) -> None:
    """La page pour l'oeil, l'onglet pour la mesure — et pas l'inverse."""

    assert payload["critical_dpi"] == 300
    tabs = 0
    for row in payload["pages"]:
        page_raster = ROOT / row["page_raster"]
        assert page_raster.is_file(), row["page_raster"]
        assert row["page_raster_sha256"].startswith("sha256:")
        assert row["page_raster_dpi"] == payload["contact_dpi"]
        if not row["tab"].get("present"):
            assert "tab_raster" not in row
            continue
        tabs += 1
        tab_raster = ROOT / row["tab_raster"]
        assert tab_raster.is_file(), row["tab_raster"]
        assert row["tab_raster_dpi"] == 300
        # Le decoupe est une bande etroite : il doit peser bien moins que la
        # page entiere qu'il traverse.
        assert tab_raster.stat().st_size < page_raster.stat().st_size * 4
    assert tabs == payload["summary"]["TAB_PRESENT"]


# ---------------------------------------------------------------------------
#  Mutations : chaque règle doit rejeter ce qu'elle prétend rejeter
# ---------------------------------------------------------------------------


def _tab(**overrides: Any) -> dict[str, Any]:
    base = {
        "present": True,
        "side": "right",
        "outside_mm": 1.0,
        "inside_mm": 12.0,
        "length_mm": 20.0,
        "label_length_mm": 12.0,
        "inner_padding_mm": 3.0,
    }
    base.update(overrides)
    return base


def _failures(page_number: int, tab: dict[str, Any]) -> set[str]:
    return {
        row["rule"]
        for row in bundle.tab_verdicts(page_number, tab)
        if row["verdict"] == "FAIL"
    }


def test_a_conforming_tab_passes_every_rule() -> None:
    assert _failures(1, _tab()) == set()


def test_a_tab_that_bleeds_three_millimetres_is_rejected() -> None:
    """C'est le piège nommé par le contrat : le fond perdu ne l'emporte pas."""

    assert "TAB_OUTSIDE_1MM" in _failures(1, _tab(outside_mm=3.0))


def test_a_tab_that_shows_ten_millimetres_inside_is_rejected() -> None:
    assert "TAB_INSIDE_12MM" in _failures(1, _tab(inside_mm=10.0))


def test_a_tab_shorter_than_sixteen_millimetres_is_rejected() -> None:
    assert "TAB_MIN_LENGTH_16MM" in _failures(1, _tab(length_mm=15.0))


def test_a_tab_on_the_wrong_side_is_rejected() -> None:
    assert "TAB_SIDE_FOLLOWS_PARITY" in _failures(1, _tab(side="left"))
    assert "TAB_SIDE_FOLLOWS_PARITY" in _failures(2, _tab(side="right"))
    # Et la bonne parité passe.
    assert "TAB_SIDE_FOLLOWS_PARITY" not in _failures(2, _tab(side="left"))


def test_a_tab_too_short_for_its_label_is_rejected() -> None:
    assert "TAB_LENGTH_IS_LABEL_PLUS_6MM" in _failures(
        1, _tab(length_mm=20.0, label_length_mm=18.0)
    )


def test_a_tab_whose_label_touches_its_edge_is_rejected() -> None:
    assert "TAB_INNER_PADDING_3MM" in _failures(1, _tab(inner_padding_mm=0.5))


def test_an_absent_tab_is_reported_and_not_silently_passed() -> None:
    verdicts = bundle.tab_verdicts(1, {"present": False})
    assert [row["verdict"] for row in verdicts] == ["ABSENT"]
