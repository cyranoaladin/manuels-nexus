"""Les ouvertures, regardées sur le rendu — et la mesure sait dire non.

Tenir sur une page ne dit rien de ce qu'on y voit. Ce module vérifie les vingt
ouvertures rendues à 300 dpi, puis fabrique les défauts que la mesure doit
attraper : un texte qui ne laisse aucune trace, un texte qui franchit le format
fini, une bande de page restée vide.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_chapter_opener_raster_qa as gate  # noqa: E402

fitz = pytest.importorskip("fitz")


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Le verdict
# ---------------------------------------------------------------------------


def test_the_twenty_openers_render_without_defect(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert summary["OPENERS_INSPECTED"] == 20
    assert summary["OPENER_TEXT_WITHOUT_TRACE"] == 0
    assert summary["OPENER_CLIPPING"] == 0
    assert summary["OPENER_EMPTY_ZONE"] == 0
    assert summary["OPENER_ORPHAN_PAGE"] == 0
    assert summary["OPENER_MISSING_CONTENT"] == 0
    assert summary["OPENER_UNKNOWN"] == 0


def test_the_threshold_stays_far_below_the_faintest_real_text(
    payload: dict[str, Any],
) -> None:
    """Le seuil ne vaut que si le corpus lui laisse de la marge."""

    weakest = payload["summary"]["WEAKEST_INK_COVERAGE"]
    assert weakest > 0
    assert weakest > payload["minimum_ink_coverage"] * 3, (
        "le fragment le moins encré s'approche du seuil : le seuil est à revoir, "
        f"trace={weakest}, seuil={payload['minimum_ink_coverage']}"
    )


def test_the_rejected_measures_are_recorded_so_nobody_retries_them(
    payload: dict[str, Any],
) -> None:
    """Deux mesures ont échoué avant celle-ci ; le dire évite de recommencer."""

    rejected = payload["measures_tried_and_rejected"]
    assert len(rejected) == 2
    for row in rejected:
        assert row["measure"].strip()
        assert row["why_rejected"].strip()
    assert any("chiffre" in row["why_rejected"] for row in rejected)
    assert any("WCAG" in row["measure"] for row in rejected)


def test_what_is_measured_elsewhere_is_taken_not_recomputed(
    payload: dict[str, Any],
) -> None:
    reuse = payload["what_is_measured_elsewhere_is_not_measured_twice"]
    source = ROOT / reuse["artifact"]
    assert source.is_file()
    span = json.loads(source.read_text(encoding="utf-8"))["summary"]
    assert payload["summary"]["OPENER_ORPHAN_PAGE"] == span["MULTI_PAGE_OPENERS"]
    assert (
        payload["summary"]["OPENER_MISSING_CONTENT"]
        == span["OPENER_MISSING_CONTENT"]
    )


def test_it_is_the_rendered_page_that_is_read(payload: dict[str, Any]) -> None:
    assert payload["raster_dpi"] == 300
    for variant in payload["variants"]:
        pdf = ROOT / variant["pdf_path"]
        assert pdf.is_file(), variant["pdf_path"]
        assert len(variant["openers"]) == 10, variant["variant"]


# ---------------------------------------------------------------------------
#  Mutations : trois défauts fabriqués, trois refus
# ---------------------------------------------------------------------------


def _blank_page(tmp_path: Path, draw) -> Any:
    document = fitz.open()
    page = document.new_page(width=595, height=842)
    draw(page)
    path = tmp_path / "sonde.pdf"
    document.save(path)
    document.close()
    return fitz.open(path)[0]


def test_white_text_on_white_leaves_no_trace(tmp_path: Path) -> None:
    """Le défaut exact que l'on cherche : présent dans le PDF, absent de la page."""

    def draw(page: Any) -> None:
        page.insert_text((100, 100), "Temps estimés : 14 h", fontsize=10,
                         color=(1, 1, 1))
        page.insert_text((100, 200), "Un texte bien visible", fontsize=10,
                         color=(0, 0, 0))

    findings, weakest = gate.span_traces(_blank_page(tmp_path, draw))

    assert [row["text"] for row in findings] == ["Temps estimés : 14 h"]
    assert findings[0]["ink_coverage"] == 0.0
    assert weakest == 0.0


def test_visible_text_of_every_size_keeps_its_trace(tmp_path: Path) -> None:
    """La mesure ne doit pas crier sur un glyphe minuscule mais bien encré."""

    def draw(page: Any) -> None:
        page.insert_text((100, 100), ".", fontsize=6, color=(0, 0, 0))
        page.insert_text((100, 200), "Titre", fontsize=32, color=(0.1, 0.1, 0.6))

    findings, weakest = gate.span_traces(_blank_page(tmp_path, draw))

    assert findings == []
    assert weakest >= gate.MINIMUM_INK_COVERAGE


class _Page:
    """Une page réduite à sa TrimBox et à ses lignes de texte."""

    def __init__(self, trim, lines) -> None:
        self.trimbox = fitz.Rect(trim)
        self._lines = lines

    def get_text(self, _kind: str) -> dict[str, Any]:
        return {
            "blocks": [
                {
                    "lines": [
                        {"bbox": bbox, "spans": [{"text": text, "size": 10.0}]}
                        for bbox, text in self._lines
                    ]
                }
            ]
        }


def test_text_crossing_the_trim_edge_is_caught() -> None:
    """Le bord lu est celui de la page, pas une valeur écrite dans le contrôle."""

    page = _Page(
        (50, 50, 545, 792),
        [
            ((10, 90, 120, 105), "Débordement à gauche"),
            ((200, 390, 300, 405), "Au centre"),
            ((400, 780, 500, 800), "Débordement en bas"),
        ],
    )

    clipped = gate.clipped_text(page)

    assert [row["text"] for row in clipped] == [
        "Débordement à gauche",
        "Débordement en bas",
    ]
    assert clipped[0]["trimbox"] == [50.0, 50.0, 545.0, 792.0]


def test_an_empty_band_is_caught(tmp_path: Path) -> None:
    """Une bannière absente laisse la moitié haute de la page blanche."""

    def draw(page: Any) -> None:
        # Rien dans la moitié haute ; de l'encre dans les blocs et dans le pied.
        page.insert_text((100, 600), "Bloc de capacités", fontsize=10,
                         color=(0, 0, 0))
        page.insert_text((100, 820), "Pied de page", fontsize=8, color=(0, 0, 0))

    zones = gate.empty_zones(_blank_page(tmp_path, draw))

    assert [row["zone"] for row in zones] == ["banniere"]
    assert zones[0]["ink_ratio"] < gate.MINIMUM_INK_RATIO


def test_a_missing_span_artifact_is_refused_rather_than_assumed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sans la mesure d'étendue, il n'y a pas d'ouvertures à regarder."""

    monkeypatch.setattr(gate, "SPAN_ARTIFACT", tmp_path / "absent.json")

    with pytest.raises(gate.RasterError):
        gate.build()
    assert gate.main(["--check"]) == 2
