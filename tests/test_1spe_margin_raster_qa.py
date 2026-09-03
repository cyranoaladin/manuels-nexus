"""Chaque note de marge laisse une trace, et la mesure sait dire le contraire.

Le compositeur a capturé 3 990 notes et n'en a dessiné aucune pendant toute une
campagne : le Form XObject existait, sa boîte était juste, son contenu était
vide d'encre. Aucune vérification de géométrie ne pouvait le voir, parce que la
géométrie, elle, était parfaite.

Ce module vérifie donc l'encre, et seulement elle : la géométrie a son propre
contrôle, sur le même PDF livré. Puis il fabrique une note invisible pour
prouver que la mesure la refuse.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_margin_raster_qa as gate  # noqa: E402

fitz = pytest.importorskip("fitz")


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Le verdict
# ---------------------------------------------------------------------------


def test_the_whole_chain_closes_on_every_expected_item(
    payload: dict[str, Any],
) -> None:
    """Identifiant source -> page -> côté -> rectangle -> encre, sur 100 %."""

    summary = payload["summary"]
    for name in (
        "MISSING",
        "DUPLICATE",
        "WRONG_PAGE",
        "WRONG_SIDE",
        "EMPTY_RENDER",
        "UNKNOWN",
    ):
        assert summary[name] == 0, name
    assert "MARGIN_SOURCE_ID" in payload["the_chain_that_is_proved"]
    # Le total inspecté doit égaler ce que le contrat déclare attendu visible.
    contract = json.loads(
        (ROOT / "audit/1SPE_MARGIN_CONTENT_CONTRACT.json").read_text(encoding="utf-8")
    )
    assert (
        summary["MARGIN_NOTES_INSPECTED"]
        == contract["summary"]["EXPECTED_VISIBLE_MARGIN_ITEMS"]
        == contract["summary"]["RENDERED_VISIBLE_MARGIN_ITEMS"]
    )


def test_every_placed_margin_note_leaves_ink(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert summary["MARGIN_NOTES_WITHOUT_TRACE"] == 0
    assert summary["MARGIN_NOTES_OUTSIDE_THEIR_PAGE"] == 0
    assert summary["MARGIN_NOTES_NOT_INSPECTED"] == 0
    # Le contrôle serait vide de sens si presque rien n'était inspecté.
    assert summary["MARGIN_NOTES_INSPECTED"] > 3900


def test_each_variant_inspects_all_the_notes_it_declares(
    payload: dict[str, Any],
) -> None:
    for variant in payload["variants"]:
        assert variant["MARGIN_NOTES_INSPECTED"] == variant[
            "declared_placed_notes"
        ], variant["variant"]
        assert variant["traceless"] == [], variant["variant"]
        for role in variant["roles"]:
            assert role["without_trace"] == 0, role
            assert role["inspected"] > 0, role


def test_the_threshold_stays_far_below_the_faintest_real_note(
    payload: dict[str, Any],
) -> None:
    weakest = payload["summary"]["WEAKEST_INK_COVERAGE"]
    threshold = payload["minimum_ink_coverage"]
    # Le seuil sépare « de l'encre » de « pas d'encre ». Une note invisible
    # marque exactement zéro -- ce que prouve la mutation plus bas ; la note la
    # plus discrète du corpus, un identifiant professeur court dans un rail
    # large, en marque presque trois fois le seuil. C'est cet écart-là qu'il
    # faut surveiller, et non un facteur choisi une fois pour toutes.
    assert weakest > threshold * 2, (
        "la note la moins encrée s'approche du seuil : le seuil est à revoir, "
        f"trace={weakest}, seuil={threshold}"
    )
    # Chaque classe publie sa propre trace la plus faible : une dérive doit
    # pouvoir être attribuée, pas seulement constatée.
    for variant in payload["variants"]:
        for role in variant["roles"]:
            assert role["weakest_ink_coverage"] > threshold, (variant["variant"], role)


def test_the_geometry_is_left_to_its_own_authority(payload: dict[str, Any]) -> None:
    """Une seule idée de l'endroit où les notes vivent, pas deux."""

    elsewhere = payload["geometry_is_verified_elsewhere"]
    assert (ROOT / elsewhere["by"]).is_file()
    assert payload["the_boxes_are_read_from_the_ledger_not_recomputed"]
    source = (ROOT / "scripts/build_1spe_margin_raster_qa.py").read_text(
        encoding="utf-8"
    )
    # Le rectangle vient du ledger, jamais d'un calcul refait ici.
    assert 'entry["bbox_sp"]' in source
    assert "reconstruct_margin_ledger" in source
    assert "safe_rect" not in source


def test_the_inventory_read_is_the_one_the_build_publishes(
    payload: dict[str, Any],
) -> None:
    assert payload["the_inventory_is_the_one_the_build_publishes"] is True
    for variant in payload["variants"]:
        inventory = ROOT / variant["inventory_path"]
        assert inventory.is_file(), variant["inventory_path"]
        assert inventory.name.endswith(".margin-layout.json")
        assert json.loads(inventory.read_text(encoding="utf-8"))["state"] == "stable"


# ---------------------------------------------------------------------------
#  Mutations
# ---------------------------------------------------------------------------


def _one_page_pdf(path: Path) -> None:
    """Un PDF minimal mais VALIDE : quatre octets ne s'ouvrent pas."""

    document = fitz.open()
    document.new_page(width=595, height=842)
    document.save(path)
    document.close()


def test_an_invisible_note_leaves_no_trace(tmp_path: Path) -> None:
    """La régression exacte du jour : une boîte juste, et rien dedans."""

    document = fitz.open()
    page = document.new_page(width=595, height=842)
    page.insert_text((450, 100), "Une note bien visible", fontsize=8,
                     color=(0, 0, 0))
    page.insert_text((450, 300), "Une note invisible", fontsize=8,
                     color=(1, 1, 1))
    path = tmp_path / "notes.pdf"
    document.save(path)
    document.close()

    with fitz.open(path) as reopened:
        target = reopened[0]
        visible = gate.ink_coverage(target, fitz.Rect(448, 90, 560, 105))
        invisible = gate.ink_coverage(target, fitz.Rect(448, 290, 560, 305))

    assert visible >= gate.MINIMUM_INK_COVERAGE
    assert invisible == 0.0


def test_a_note_on_the_wrong_page_or_the_wrong_side_is_counted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sans ces deux mutations, WRONG_PAGE et WRONG_SIDE seraient décoratifs."""

    build = tmp_path / "MANUEL_1SPE"
    build.mkdir()
    _one_page_pdf(build / "MANUEL_1SPE_eleve.pdf")
    (build / "MANUEL_1SPE_eleve.margin-layout.json").write_text(
        json.dumps(
            {
                "state": "stable",
                "notes": [
                    {
                        "id": "nxm:eleve:appui:00000001",
                        "role": "appui",
                        "target_shipout_index": 1,
                    }
                ],
                # Le rail de la page 1 est à DROITE.
                "pages": [
                    {
                        "shipout_index": 1,
                        "rail_side": "right",
                        "page_width_sp": 38967463,
                        "page_height_sp": 55137945,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "BUILD", build)
    # Le ledger place la note sur une AUTRE page, et à GAUCHE.
    monkeypatch.setattr(
        gate,
        "rendered_boxes",
        lambda *a, **k: {
            "nxm:eleve:appui:00000001": {
                "target_shipout_index": 7,
                "bbox_sp": [100000, 200000, 900000, 400000],
            }
        },
    )

    result = gate.measure("eleve")

    assert result["WRONG_PAGE"] == 1
    assert result["WRONG_SIDE"] == 1
    assert result["wrong_page"][0]["expected"] == 1
    assert result["wrong_side"][0]["expected"] == "right"


def test_a_note_the_ledger_does_not_know_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Une note que le PDF ne porte pas est COMPTÉE, pas passée sous silence."""

    build = tmp_path / "MANUEL_1SPE"
    build.mkdir()
    _one_page_pdf(build / "MANUEL_1SPE_eleve.pdf")
    (build / "MANUEL_1SPE_eleve.margin-layout.json").write_text(
        json.dumps(
            {
                "state": "stable",
                "notes": [
                    {
                        "id": "nxm:eleve:appui:00000001",
                        "role": "appui",
                        "target_shipout_index": 1,
                    }
                ],
                "pages": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(gate, "BUILD", build)
    monkeypatch.setattr(gate, "rendered_boxes", lambda *a, **k: {})

    result = gate.measure("eleve")

    assert result["MISSING"] == 1
    assert result["missing"] == ["nxm:eleve:appui:00000001"]
    assert result["MARGIN_NOTES_INSPECTED"] == 0


def test_an_unstable_inventory_is_refused_rather_than_measured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Un placement non convergé ne décrit pas la page qu'on regarde."""

    build = tmp_path / "MANUEL_1SPE"
    build.mkdir()
    (build / "MANUEL_1SPE_eleve.pdf").write_bytes(b"%PDF-1.7\n")
    (build / "MANUEL_1SPE_eleve.margin-layout.json").write_text(
        json.dumps({"state": "changed", "notes": [], "pages": []}), encoding="utf-8"
    )
    monkeypatch.setattr(gate, "BUILD", build)

    with pytest.raises(gate.MarginRasterError, match="non stabilisé"):
        gate.measure("eleve")


def test_a_missing_link_inventory_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gate, "BUILD", tmp_path)

    with pytest.raises(gate.MarginRasterError, match="absent"):
        gate.measure("eleve")
    assert gate.main(["--check"]) in (1, 2)
