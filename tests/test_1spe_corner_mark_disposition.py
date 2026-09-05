"""Une équerre qui ressemble à un repère de coupe n'en est pas un.

Le contrat d'impression interdit les traits de coupe non demandés. Encore
faut-il savoir les reconnaître : ce module vérifie que la mesure distingue une
équerre de maquette d'un vrai repère technique — et, surtout, qu'elle refuse
un vrai repère si on lui en pose un.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_corner_mark_disposition as gate  # noqa: E402

PT_PER_MM = gate.PT_PER_MM
ARM = gate.ARM_MM * PT_PER_MM
# Un A4 avec 3 mm de fond perdu sur chaque bord, comme le manuel livré.
MEDIA = (0.0, 0.0, 216 * PT_PER_MM, 303 * PT_PER_MM)
TRIM = (3 * PT_PER_MM, 3 * PT_PER_MM, 213 * PT_PER_MM, 300 * PT_PER_MM)


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class Box:
    def __init__(self, rect: tuple[float, float, float, float]) -> None:
        self.x0, self.y0, self.x1, self.y1 = rect


class FakePage:
    def __init__(self, drawings: list[dict[str, Any]]) -> None:
        self._drawings = drawings
        self.mediabox = Box(MEDIA)
        self.trimbox = Box(TRIM)

    def get_drawings(self) -> list[dict[str, Any]]:
        return self._drawings


class FakeDocument:
    def __init__(self, pages: list[FakePage]) -> None:
        self._pages = pages
        self.page_count = len(pages)

    def __getitem__(self, index: int) -> FakePage:
        return self._pages[index]

    def __enter__(self) -> "FakeDocument":
        return self

    def __exit__(self, *_: object) -> None:
        return None


class FakeFitz:
    def __init__(self, document: FakeDocument) -> None:
        self._document = document

    def open(self, _path: Path) -> FakeDocument:
        return self._document


def corner(
    x: float,
    y: float,
    *,
    dx: float,
    dy: float,
    colour: tuple[float, ...] | None,
    width: float,
) -> dict[str, Any]:
    """Une équerre : deux bras de 4,2 mm partant d'un même point."""

    return {
        "color": colour,
        "width": width,
        "items": [
            ("l", Point(x, y), Point(x + dx * ARM, y)),
            ("l", Point(x, y), Point(x, y + dy * ARM)),
        ],
    }


def design_mark() -> dict[str, Any]:
    """Ce que la maquette dessine : 7 mm dans le format, en couleur, 1 pt."""

    inset = 7 * PT_PER_MM
    return corner(
        inset, inset, dx=1, dy=1, colour=(0.180, 0.490, 0.820), width=1.0
    )


def technical_crop_mark() -> dict[str, Any]:
    """Ce qu'un prestataire poserait : dans le fond perdu, noir, filet, sortant."""

    return corner(
        1.0 * PT_PER_MM, 1.0 * PT_PER_MM, dx=-1, dy=-1, colour=(0.0, 0.0, 0.0), width=0.25
    )


@pytest.fixture
def measured(monkeypatch: pytest.MonkeyPatch) -> Any:
    def install(drawings: list[dict[str, Any]]) -> None:
        document = FakeDocument([FakePage(drawings)])
        monkeypatch.setattr(gate, "_fitz", lambda: FakeFitz(document))
        monkeypatch.setattr(gate.Path, "is_file", lambda _self: True)

    return install


# ---------------------------------------------------------------------------
#  La distinction
# ---------------------------------------------------------------------------


def test_a_design_corner_is_not_counted_as_a_crop_mark(measured: Any) -> None:
    measured([design_mark()])

    payload = gate.build()

    assert payload["summary"]["CORNER_MARKS"] == 4
    assert payload["summary"]["UNREQUESTED_CROP_MARKS"] == 0
    assert payload["summary"]["MARKS_OUTSIDE_TRIMBOX"] == 0
    assert payload["summary"]["MARKS_ACHROMATIC"] == 0


def test_a_real_crop_mark_is_refused(measured: Any) -> None:
    """La mutation qui donne sa valeur au contrôle."""

    measured([technical_crop_mark()])

    payload = gate.build()

    assert payload["summary"]["UNREQUESTED_CROP_MARKS"] == 4
    assert gate.main(["--check"]) == 1


def test_each_criterion_alone_is_not_enough(measured: Any) -> None:
    """Un trait noir n'est pas un repère ; un trait fin non plus.

    Ce qui fait un repère de coupe, c'est d'être dehors ET achromatique ET fin
    ET tourné vers l'extérieur. Confondre un seul critère avec le tout ferait
    condamner un filet de maquette.
    """

    inset = 7 * PT_PER_MM
    only_black = corner(
        inset, inset, dx=1, dy=1, colour=(0.0, 0.0, 0.0), width=1.0
    )
    only_thin = corner(
        inset, inset, dx=1, dy=1, colour=(0.18, 0.49, 0.82), width=0.25
    )
    measured([only_black, only_thin])

    assert gate.build()["summary"]["UNREQUESTED_CROP_MARKS"] == 0


def test_a_page_without_any_corner_is_refused_rather_than_declared_clean(
    measured: Any,
) -> None:
    """Zéro équerre mesurée ne prouve rien : ça prouve qu'on n'a pas mesuré."""

    measured([])

    with pytest.raises(gate.CornerMarkError, match="aucune equerre"):
        gate.build()


def test_a_segment_of_another_length_is_not_a_corner(measured: Any) -> None:
    inset = 7 * PT_PER_MM
    rule = {
        "color": (0.18, 0.49, 0.82),
        "width": 0.5,
        "items": [("l", Point(inset, inset), Point(inset + 40 * PT_PER_MM, inset))],
    }
    measured([design_mark(), rule])

    assert gate.build()["summary"]["CORNER_MARKS"] == 4


# ---------------------------------------------------------------------------
#  Le manuel livré
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def test_the_delivered_manual_carries_no_unrequested_crop_mark(
    payload: dict[str, Any],
) -> None:
    for metric in gate.BLOCKING:
        assert payload["summary"][metric] == 0, metric


def test_the_corners_are_classified_as_design_and_measured_as_such(
    payload: dict[str, Any],
) -> None:
    assert payload["classification"] == "DESIGN_ELEMENT"
    summary = payload["summary"]
    assert summary["CORNER_MARKS"] > 1000
    assert summary["MARKS_OUTSIDE_TRIMBOX"] == 0
    assert summary["MARKS_ACHROMATIC"] == 0
    # Une couleur par rubrique : un repère de coupe n'en changerait pas.
    assert summary["DISTINCT_MARK_COLOURS"] >= 5
    assert len(payload["why_this_classification_is_measured"]) == 4


def test_the_classification_does_not_close_the_decision(
    payload: dict[str, Any],
) -> None:
    """§16 : un élément de maquette ne devient pas accepté parce qu'il est classé."""

    assert payload["approves_nothing"] is True
    # La disposition a ete rendue par le Release Owner, sur ces mesures-ci.
    # Ce que le module continue de ne pas faire : la rendre lui-meme.
    assert payload["d7_disposition"] == "ACCEPTED_AS_INTENTIONAL_DESIGN_ELEMENT"
    assert payload["d7_disposition_rendered_by"] == "abenrhouma"
    assert "n'est pas acquise" in payload["this_is_not_an_acceptance"]
    assert "defaut visuel" in payload["d7_disposition_motive"]


def test_the_producer_is_named_and_really_draws_them(payload: dict[str, Any]) -> None:
    assert "nexus-decor.sty" in payload["producer"]
    source = (ROOT / "gabarits/common/nexus-decor.sty").read_text(encoding="utf-8")
    assert "\\nxDecorDessin" in source
    assert f"{gate.ARM_MM}mm" in source
