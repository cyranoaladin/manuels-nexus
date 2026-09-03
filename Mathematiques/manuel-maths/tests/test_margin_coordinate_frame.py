"""Le repère du compositeur de marges : déclaré, vérifié, invariant au fond perdu.

Défaut mesuré le 2026-09-03 sur le manuel 1SPE :
`MARGIN_COMPOSITOR_COORDINATE_FRAME_MISMATCH`, 559 403 sp — soit 8,53 bp, soit
exactement les 3 mm de fond perdu — entre le `safe_rect` du rail et l'obstacle
déclaré. La configuration du compositeur était prise dans `\\AtBeginDocument`,
où `\\hoffset` valait encore 0 pt, tandis que tout obstacle déclaré dans le
corps du document arrivait avec `\\hoffset` = 3 mm. Les deux coordonnées
disaient « x » dans deux repères différents.

Ce module ne vérifie PAS l'écart de 3 mm : il vérifie la cause. Le repère est
nommé une seule fois (la page composée, dont le coin est l'origine du
TrimBox), le runtime le reçoit et le refuse s'il ne correspond pas aux
registres réellement en vigueur, et la géométrie logique doit être identique
au sp près pour un fond perdu de 0 mm, 1 mm ou 3 mm.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MANUAL_ROOT.parents[1]
CLASS_PATH = REPO_ROOT / "gabarits/common/nexus-manuel.cls"
RAIL_PATH = REPO_ROOT / "gabarits/common/nexus-margin-rail.tex"
SHIPOUT_PATH = REPO_ROOT / "gabarits/common/nexus-margin-shipout.lua"
RUN_NONCE = "0123456789abcdef0123456789abcdef"
MAX_PASSES = 6

# Conversion des millimètres en points d'échelle, comme TeX la fait : 1 mm =
# 7227/2540 pt et 1 pt = 65536 sp, le quotient étant tronqué. C'est pourquoi
# 3 mm valent 559 403 sp et non 559 404 — le nombre exact du diagnostic.
def _millimetres_sp(millimetres: int) -> int:
    return (millimetres * 7227 * 65536) // 2540


ONE_MM_SP = _millimetres_sp(1)
BLEED_3MM_SP = _millimetres_sp(3)
BP_TO_SP_EXACT = Fraction(7227 * 65536, 7200)


# --------------------------------------------------------------------------
#  Sources : le repère est nommé une seule fois
# --------------------------------------------------------------------------


def test_the_composed_page_origin_is_declared_once_and_feeds_every_consumer() -> None:
    """\\hoffset, /TrimBox et le compositeur descendent de la même longueur."""

    source = CLASS_PATH.read_text(encoding="utf-8")

    # Le fond perdu est posé en un seul endroit et l'origine en découle.
    assert r"\newcommand{\nxFixerFondPerdu}[1]{" in source
    assert r"\nxFixerFondPerdu{\nxFondPerduDim}" in source

    # \hoffset/\voffset viennent de l'origine déclarée, pas d'une constante
    # répétée.
    assert r"\hoffset=\nxOrigineTrimX" in source
    assert r"\voffset=\nxOrigineTrimY" in source

    # Le coin du TrimBox aussi.
    assert r"/TrimBox [\nxDimEnBp{\nxOrigineTrimX}" in source
    assert r"\nxDimEnBp{\nxOrigineTrimY}" in source


def test_the_rail_geometry_carries_no_typesetting_offset() -> None:
    """Les quatre longueurs du rail sont dans le repère de la page composée."""

    source = RAIL_PATH.read_text(encoding="utf-8")

    for accessor in (
        r"\newcommand{\nxMargeRailGaucheImpaire}",
        r"\newcommand{\nxMargeRailGauchePaire}",
        r"\newcommand{\nxMargeRailHaut}",
        r"\newcommand{\nxMargeRailBas}",
    ):
        assert accessor in source, accessor

    # Le rail est passé par ces accesseurs, et par eux seuls.
    for field, accessor in (
        ("odd_rail_left_sp", r"\nxMargeRailGaucheImpaire"),
        ("even_rail_left_sp", r"\nxMargeRailGauchePaire"),
        ("rail_top_sp", r"\nxMargeRailHaut"),
        ("rail_bottom_sp", r"\nxMargeRailBas"),
    ):
        assert f"{field} = \\number{accessor}," in source, field

    # Aucune coordonnée n'embarque le décalage de composition. Seuls
    # support_offset_* le transportent, et c'est le repère, pas une position.
    coordinates = re.sub(r"support_offset_[xy]_sp = \\number\\[hv]offset,", "", source)
    coordinates = "\n".join(
        line for line in coordinates.splitlines() if not line.lstrip().startswith("%")
    )
    assert r"\hoffset" not in coordinates
    assert r"\voffset" not in coordinates

    # La configuration est prise APRÈS que la classe ait posé le fond perdu.
    assert r"\AddToHook{begindocument/end}{%" in source
    assert r"\AtBeginDocument{%" not in source


def test_the_composed_page_is_the_single_frame_named_by_the_runtime() -> None:
    """Le module Lua nomme son repère et n'a qu'une conversion."""

    source = SHIPOUT_PATH.read_text(encoding="utf-8")

    assert "REPERE UNIQUE : la PAGE COMPOSEE" in source
    assert "local function composed_page_x_sp(" in source
    assert "local function composed_page_y_from_top_sp(" in source
    # Une seule conversion de chaque côté : `pdf.getpos()` est la seule source
    # de coordonnées en espace utilisateur du PDF dans le runtime, et elle
    # n'est appelée qu'une fois. On ne compte que les appels, pas les
    # commentaires qui les décrivent.
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("--")
    )
    assert code.count("pdf.getpos()") == 1


# --------------------------------------------------------------------------
#  Le garde : le runtime refuse un repère incohérent
# --------------------------------------------------------------------------


_STUB_HARNESS = """
-- Charge le compositeur hors LuaTeX, avec les seules dependances qu'il
-- touche au chargement, pour eprouver la verification de repere seule.
local created = 0
luatexbase = {
  newuserwhatsitid = function() created = created + 1 return created end,
  add_to_callback = function() end,
}
node = { subtype = function() return nil end }
texio = { write_nl = function() end }

local module = assert(loadfile(arg[1]))()
local values = {
  variant = "eleve",
  page_width_sp = 39158276,
  page_height_sp = 55380990,
  trim_origin_x_sp = tonumber(arg[2]),
  trim_origin_y_sp = tonumber(arg[3]),
  support_offset_x_sp = tonumber(arg[4]),
  support_offset_y_sp = tonumber(arg[5]),
  rail_width_sp = 5780518,
  odd_rail_left_sp = 31979276,
  even_rail_left_sp = 1398482,
  rail_top_sp = 4475220,
  rail_bottom_sp = 50532812,
  report_box_number = 12,
  report_decoration_height_sp = 1170548,
}
local ok, err = pcall(module.configure, values)
if ok then
  print("ACCEPTED")
else
  print("REJECTED:" .. tostring(err))
end
"""


def _configure_under_frame(
    tmp_path: Path,
    *,
    trim_origin: tuple[int, int],
    support_offset: tuple[int, int],
) -> str:
    harness = tmp_path / "frame-harness.lua"
    harness.write_text(_STUB_HARNESS, encoding="utf-8")
    environment = os.environ.copy()
    # Le garde doit se déclencher avant toute lecture d'artefact.
    environment.pop("NEXUS_MARGIN_LAYOUT_PREVIOUS", None)
    environment.pop("NEXUS_MARGIN_LAYOUT_NEXT", None)
    environment["NEXUS_MARGIN_VARIANT"] = "eleve"
    environment["NEXUS_MARGIN_RUN_NONCE"] = RUN_NONCE
    environment["NEXUS_MARGIN_PASS_NUMBER"] = "1"
    result = subprocess.run(
        [
            "texlua",
            str(harness),
            str(SHIPOUT_PATH),
            str(trim_origin[0]),
            str(trim_origin[1]),
            str(support_offset[0]),
            str(support_offset[1]),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout.strip()


@pytest.mark.skipif(shutil.which("texlua") is None, reason="texlua absent")
def test_the_runtime_refuses_the_exact_regression_measured_on_the_manual(
    tmp_path: Path,
) -> None:
    """Origine déclarée à 3 mm, décalage réel à 0 pt : c'est le défaut, il échoue.

    C'est littéralement l'état d'avant la correction : la classe posait le fond
    perdu dans « begindocument/end » et la configuration était lue dans
    `\\AtBeginDocument`, donc avec `\\hoffset` encore nul.
    """

    observed = _configure_under_frame(
        tmp_path,
        trim_origin=(BLEED_3MM_SP, BLEED_3MM_SP),
        support_offset=(0, 0),
    )

    assert observed.startswith("REJECTED:")
    assert "coordinate frame mismatch in x" in observed
    assert f"declared trim origin {BLEED_3MM_SP} sp" in observed
    assert "typesetting offset 0 sp" in observed
    # L'écart nommé dans le diagnostic, au sp près.
    assert BLEED_3MM_SP == 559403


@pytest.mark.skipif(shutil.which("texlua") is None, reason="texlua absent")
def test_the_runtime_refuses_a_vertical_frame_mismatch_too(tmp_path: Path) -> None:
    observed = _configure_under_frame(
        tmp_path,
        trim_origin=(0, BLEED_3MM_SP),
        support_offset=(0, 0),
    )

    assert observed.startswith("REJECTED:")
    assert "coordinate frame mismatch in y" in observed


@pytest.mark.skipif(shutil.which("texlua") is None, reason="texlua absent")
@pytest.mark.parametrize("bleed_mm", [0, 1, 3])
def test_the_runtime_accepts_any_coherent_bleed(tmp_path: Path, bleed_mm: int) -> None:
    """Le compositeur ne connaît pas la valeur du fond perdu, seulement sa cohérence."""

    origin = _millimetres_sp(bleed_mm)
    observed = _configure_under_frame(
        tmp_path,
        trim_origin=(origin, origin),
        support_offset=(origin, origin),
    )

    assert observed == "ACCEPTED", observed


# --------------------------------------------------------------------------
#  Invariance au fond perdu, mesurée sur des compilations réelles
# --------------------------------------------------------------------------


_FIXTURE = r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\nxFixerFondPerdu{%(bleed)s}
\begin{document}
\nxMarginReserveRect{sonde-impaire}{%%
  %(odd_left)s}{5cm}{%%
  %(odd_right)s}{9cm}
Page impaire\margeAppui{Note sur page impaire, rail exterieur droit.}
\newpage
\nxMarginReserveRect{sonde-paire}{%%
  %(even_left)s}{5cm}{%%
  %(even_right)s}{9cm}
Page paire\margeAppui{Note sur page paire, rail exterieur gauche.}
\end{document}
"""

_TRIM_RAIL = {
    "odd_left": r"\nxMargeRailGaucheImpaire",
    "odd_right": r"\dimexpr\nxMargeRailGaucheImpaire+\marginparwidth\relax",
    "even_left": r"\nxMargeRailGauchePaire",
    "even_right": r"\dimexpr\nxMargeRailGauchePaire+\marginparwidth\relax",
}

# La mutation : le MÊME rail, décalé du fond perdu. C'est ce que produisait un
# appelant qui composait sa coordonnée dans le repère du support.
_SUPPORT_RAIL = {
    "odd_left": r"\dimexpr\nxMargeRailGaucheImpaire+\hoffset\relax",
    "odd_right": (
        r"\dimexpr\nxMargeRailGaucheImpaire+\marginparwidth+\hoffset\relax"
    ),
    "even_left": r"\dimexpr\nxMargeRailGauchePaire+\hoffset\relax",
    "even_right": (
        r"\dimexpr\nxMargeRailGauchePaire+\marginparwidth+\hoffset\relax"
    ),
}


def _load(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _compile_until_stable(
    directory: Path, bleed: str, rail: dict[str, str]
) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    source = directory / "frame.tex"
    source.write_text(_FIXTURE % {"bleed": bleed, **rail}, encoding="utf-8")
    previous = directory / "margin-layout.previous.json"
    following = directory / "margin-layout.next.json"
    links = directory / "margin-links.next.json"

    for pass_number in range(1, MAX_PASSES + 1):
        following.unlink(missing_ok=True)
        environment = os.environ.copy()
        environment.update(
            {
                "NEXUS_MARGIN_RUN_NONCE": RUN_NONCE,
                "NEXUS_MARGIN_VARIANT": "eleve",
                "NEXUS_MARGIN_PASS_NUMBER": str(pass_number),
                "NEXUS_MARGIN_LAYOUT_PREVIOUS": str(previous),
                "NEXUS_MARGIN_LAYOUT_NEXT": str(following),
                "NEXUS_MARGIN_LINK_INVENTORY_NEXT": str(links),
                "NEXUS_MARGIN_MARKER_METADATA": "1",
            }
        )
        result = subprocess.run(
            [
                "lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={directory}",
                str(source),
            ],
            cwd=MANUAL_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-8000:] + result.stderr
        layout = json.loads(following.read_text(encoding="utf-8"))
        os.replace(following, previous)
        if layout["state"] == "stable":
            break
        assert layout["state"] in {"collecting", "changed"}
    else:  # pragma: no cover - la fixture converge en deux passes
        pytest.fail("placements marginaux non stabilisés")

    return {
        "capture": layout,
        "links": json.loads(links.read_text(encoding="utf-8")),
        "pdf": directory / "frame.pdf",
    }


def _logical_geometry(capture: dict[str, Any]) -> dict[str, Any]:
    """Toute la géométrie du compositeur, dans son propre repère."""

    geometry: dict[str, Any] = {}
    for page in capture["pages"]:
        index = page["shipout_index"]
        geometry[f"page{index}.width_sp"] = page["page_width_sp"]
        geometry[f"page{index}.height_sp"] = page["page_height_sp"]
        geometry[f"page{index}.rail_side"] = page["rail_side"]
        for corner, value in page["safe_rect"].items():
            geometry[f"page{index}.safe_rect.{corner}"] = value
        for obstacle in page["obstacles"]:
            for corner in ("left_sp", "top_sp", "right_sp", "bottom_sp"):
                geometry[f"page{index}.obstacle.{corner}"] = obstacle[corner]
    for note in capture["notes"]:
        for field in (
            "origin_y_sp",
            "target_y_sp",
            "target_shipout_index",
            "width_sp",
            "effective_height_sp",
        ):
            geometry[f"{note['id']}.{field}"] = note[field]
    return geometry


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_the_logical_geometry_is_invariant_under_zero_one_and_three_millimetre_bleed(
    tmp_path: Path,
) -> None:
    """Le fond perdu déplace le support, jamais la position logique du contenu.

    Égalité EXACTE en sp, sans tolérance : ces valeurs ne traversent aucune
    conversion PDF, elles sortent du même moteur dans le même repère.
    """

    builds = {
        millimetres: _compile_until_stable(
            tmp_path / f"bleed-{millimetres}mm", f"{millimetres}mm", _TRIM_RAIL
        )
        for millimetres in (0, 1, 3)
    }
    geometries = {
        millimetres: _logical_geometry(build["capture"])
        for millimetres, build in builds.items()
    }

    reference = geometries[0]
    assert reference, "la sonde doit produire de la géométrie"
    for millimetres in (1, 3):
        divergent = {
            key: (reference[key], geometries[millimetres][key])
            for key in reference
            if reference[key] != geometries[millimetres][key]
        }
        assert divergent == {}, f"fond perdu {millimetres} mm : {divergent}"

    # Le fond perdu a bien changé : la sonde n'est pas vide de sens. On le lit
    # dans le PDF, à l'endroit même où il doit apparaître.
    fitz = pytest.importorskip("fitz")
    for millimetres, build in builds.items():
        with fitz.open(build["pdf"]) as document:
            page = document[0]
            expected_bp = millimetres * 72 / 25.4
            assert abs(page.trimbox.x0 - page.mediabox.x0 - expected_bp) < 0.001
            assert abs(page.mediabox.y1 - page.trimbox.y1 - expected_bp) < 0.001


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_odd_and_even_pages_measure_rail_obstacle_and_links_in_one_frame(
    tmp_path: Path,
) -> None:
    """Page impaire à droite, page paire à gauche, fond perdu actif.

    Le rail, l'obstacle, la note rendue et ses rectangles de lien doivent tous
    se mesurer dans la page composée. La preuve est le gate complet du ledger,
    exécuté ici sur un PDF réellement produit par la classe.
    """

    build = _compile_until_stable(tmp_path / "recto-verso", "3mm", _TRIM_RAIL)
    capture = build["capture"]
    contract = _load("margin_contract_frame", MANUAL_ROOT / "scripts/margin_contract.py")
    ledger_module = _load("margin_ledger_frame", MANUAL_ROOT / "scripts/margin_ledger.py")
    stable = contract.materialize_stable_layout(capture)

    pages = {page["shipout_index"]: page for page in capture["pages"]}
    assert [pages[index]["rail_side"] for index in (1, 2)] == ["right", "left"]

    for index, page in pages.items():
        safe = page["safe_rect"]
        assert len(page["obstacles"]) == 1, index
        obstacle = page["obstacles"][0]
        # Même repère : l'obstacle déclaré sur la bande du rail LUI est égal,
        # au sp. C'est l'assertion que l'écart de 3 mm faisait échouer.
        assert obstacle["left_sp"] == safe["left_sp"], index
        assert obstacle["right_sp"] == safe["right_sp"], index
        assert safe["top_sp"] < obstacle["top_sp"] < obstacle["bottom_sp"], index
        assert obstacle["bottom_sp"] < safe["bottom_sp"], index
        # Et le rail reste dans le format fini, du bon côté.
        assert 0 < safe["left_sp"] < safe["right_sp"] < page["page_width_sp"], index
        if page["rail_side"] == "right":
            assert safe["left_sp"] > page["page_width_sp"] // 2, index
        else:
            assert safe["right_sp"] < page["page_width_sp"] // 2, index

    ledger = ledger_module.reconstruct_margin_ledger(
        build["pdf"], capture, stable, build["links"]
    )
    # Le PDF vient du moteur : il ecrit ses nombres a trois decimales, et la
    # borne au sp pres lui est physiquement inaccessible. On le DIT ici, a
    # l'appel, plutot que de relacher le controle pour tout le monde.
    result = ledger_module.verify_margin_layout(
        build["pdf"],
        capture,
        stable,
        ledger,
        rendered_position_tolerance_sp=(
            ledger_module.ENGINE_WRITTEN_POSITION_TOLERANCE_SP
        ),
    )

    assert result.passed is True
    assert result.page_count == 2
    assert result.note_count == 2


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_an_obstacle_offset_by_the_bleed_breaks_the_rail_containment_invariant(
    tmp_path: Path,
) -> None:
    """Mutation : le même obstacle, décalé du fond perdu. L'oracle doit échouer.

    Sans cette sonde, l'égalité obtenue plus haut pourrait être vide de sens.
    Ici l'appelant compose sa coordonnée dans le repère du support — l'erreur
    exacte d'avant la correction — et l'écart mesuré vaut le fond perdu au
    sp près.
    """

    build = _compile_until_stable(tmp_path / "mutant", "3mm", _SUPPORT_RAIL)
    pages = {page["shipout_index"]: page for page in build["capture"]["pages"]}

    for index, page in pages.items():
        safe = page["safe_rect"]
        obstacle = page["obstacles"][0]
        assert obstacle["left_sp"] - safe["left_sp"] == BLEED_3MM_SP, index
        assert obstacle["right_sp"] - safe["right_sp"] == BLEED_3MM_SP, index
        # L'invariant de la sonde nominale est bien violé : elle discrimine.
        assert not (
            safe["left_sp"] <= obstacle["left_sp"]
            and obstacle["right_sp"] <= safe["right_sp"]
        ), index


# --------------------------------------------------------------------------
#  La tolérance de rendu est dérivée du moteur, pas choisie
# --------------------------------------------------------------------------


def test_the_form_bbox_bound_is_the_worst_case_of_the_mechanism() -> None:
    """La borne du /BBox est-elle atteinte, et jamais depassee ?

    Une borne trop large laisse passer un vrai defaut ; une borne trop etroite
    rejette un PDF conforme, ce qui est arrive sur le manuel livre. Elle doit
    donc etre EXACTEMENT le pire ecart que le mecanisme puisse produire. Ce
    controle le verifie en parcourant un intervalle entier de valeurs : aucune
    ne doit depasser la borne, et au moins une doit l'atteindre.
    """

    ledger_module = _load(
        "margin_ledger_bbox_bound", MANUAL_ROOT / "scripts/margin_ledger.py"
    )
    bound = ledger_module.FORM_BBOX_ROUNDING_TOLERANCE_SP
    digits = ledger_module.PDF_DECIMAL_DIGITS
    step = Fraction(1, 10**digits)

    worst = 0
    for exact_sp in range(400_000, 460_000):
        # Le moteur ecrit la valeur en bp, arrondie a `digits` decimales.
        in_bp = Fraction(exact_sp) / BP_TO_SP_EXACT
        written = round(in_bp / step) * step
        # Le controle la relit, et l'arrondit au sp.
        read_back = round(written * BP_TO_SP_EXACT)
        worst = max(worst, abs(read_back - exact_sp))

    assert worst == bound, (
        "la borne du /BBox ne colle plus au mecanisme : "
        f"pire ecart {worst} sp, borne {bound} sp"
    )


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_the_rendered_position_tolerance_is_the_engines_writing_precision(
    tmp_path: Path,
) -> None:
    """La borne vient des chiffres décimaux que LuaTeX écrit, et de rien d'autre."""

    ledger_module = _load(
        "margin_ledger_tolerance", MANUAL_ROOT / "scripts/margin_ledger.py"
    )

    half_ulp_sp = BP_TO_SP_EXACT / (2 * 10**ledger_module.PDF_DECIMAL_DIGITS)
    # Un seul nombre arrondi -- le coin du /BBox du Form -- PLUS le demi-sp de
    # l'arrondi final : la valeur relue est ramenee au sp avant d'etre comparee
    # a une valeur exacte. La borne valait `int(half_ulp)`, soit 32, et
    # oubliait ce demi-sp. Comme les deux quantites comparees sont des ENTIERS,
    # leur ecart ne peut pas valoir 33,39 : la borne juste est le PLANCHER de
    # 32,890880 + 0,5, c'est-a-dire 33. Le manuel l'a montre -- une note de
    # 438 929 sp s'ecrit 6.673 bp et se relit 438 962 sp -- sur un PDF
    # parfaitement conforme.
    assert ledger_module.FORM_BBOX_ROUNDING_TOLERANCE_SP == math.floor(
        half_ulp_sp + Fraction(1, 2)
    )
    # Deux nombres arrondis plus le demi-sp de la conversion pt -> bp.
    assert ledger_module.ENGINE_WRITTEN_POSITION_TOLERANCE_SP == math.ceil(
        2 * half_ulp_sp + Fraction(1, 2)
    )
    # Elle reste très inférieure au dixième de millimètre : une dérive de
    # repère, qui vaut des millimètres, ne peut pas s'y cacher.
    assert ledger_module.ENGINE_WRITTEN_POSITION_TOLERANCE_SP < ONE_MM_SP / 100
    # Et le DÉFAUT reste le sp : la borne du moteur ne se prend qu'à l'appel.
    assert ledger_module.MARGIN_GEOMETRY_TOLERANCE_SP == 1
    import inspect

    signature = inspect.signature(ledger_module.verify_margin_layout)
    assert signature.parameters["rendered_position_tolerance_sp"].default == 1

    # Le moteur écrit bien à trois décimales : on le lit dans un PDF réel.
    build = _compile_until_stable(tmp_path / "digits", "3mm", _TRIM_RAIL)
    pikepdf = pytest.importorskip("pikepdf")
    with pikepdf.Pdf.open(build["pdf"]) as document:
        media = document.pages[0].obj["/MediaBox"]
        decimals = [
            len(str(value).partition(".")[2])
            for value in media
            if "." in str(value)
        ]
    assert decimals, "le /MediaBox doit porter des décimales"
    assert max(decimals) <= ledger_module.PDF_DECIMAL_DIGITS
