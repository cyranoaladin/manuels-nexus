"""Zéro alerte dans les journaux LaTeX, et rien qui échappe au classement.

Le registre figé qui précédait comptait vingt-cinq lignes Overfull/Underfull et
renvoyait quatre familles à un « triage séparé » -- dont 943 et 3 008 alertes du
moteur de sortie. Compter n'est pas fermer. Ce module vérifie que les journaux
réellement produits ne portent plus aucune alerte, que la partition des familles
est close, puis mute les journaux pour prouver que le contrôle sait refuser.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_latex_log_warning_gate as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  Le verdict
# ---------------------------------------------------------------------------


def test_the_produced_logs_carry_no_warning_at_all(payload: dict[str, Any]) -> None:
    assert payload["summary"]["LATEX_WARNINGS"] == 0
    assert payload["summary"]["UNCLASSIFIED_WARNING_LINES"] == 0
    for variant in payload["variants"]:
        assert variant["LATEX_WARNINGS"] == 0, variant["variant"]
        assert variant["unclassified"] == [], variant["variant"]
        for family, count in variant["by_family"].items():
            assert count == 0, (variant["variant"], family)


def test_the_two_logs_were_actually_read(payload: dict[str, Any]) -> None:
    """Un journal vide donnerait lui aussi zéro : il faut qu'il y ait matière."""

    assert [row["variant"] for row in payload["variants"]] == ["eleve", "professeur"]
    for variant in payload["variants"]:
        assert variant["log_lines"] > 10_000, variant["variant"]
        assert variant["INFORMATION_LINES_NOT_WARNINGS"] > 0, variant["variant"]


def test_every_family_says_what_it_was_and_what_closed_it(
    payload: dict[str, Any],
) -> None:
    for name, detail in payload["families"].items():
        assert detail["occurrences"] == 0, name
        assert detail["cause"].strip(), name
        assert detail["resolution"].strip(), name
        assert detail["closed_by"].strip(), name


def test_an_information_line_is_never_counted_as_a_warning(
    payload: dict[str, Any],
) -> None:
    """microtype en émet des milliers ; ce n'est pas une alerte."""

    assert payload["summary"]["INFORMATION_LINES_NOT_WARNINGS"] > 1000
    assert "Info" in payload["an_info_line_is_not_a_warning"]


def test_the_gate_supersedes_the_frozen_ledger(payload: dict[str, Any]) -> None:
    superseded = payload["supersedes"]
    assert superseded["artifact"] == "audit/LATEX_LAYOUT_WARNING_LEDGER.json"
    assert (ROOT / superseded["artifact"]).is_file()
    assert superseded["why"].strip()


# ---------------------------------------------------------------------------
#  Mutations : chaque famille éteinte doit pouvoir se rallumer
# ---------------------------------------------------------------------------


REVIVALS = {
    "PDF_BACKEND_POP_EMPTY_COLOR_PAGE_STACK": (
        "warning  (pdf backend): pop empty color page stack 0"
    ),
    "REQUESTED_NAME_DIFFERS_FROM_PROVIDED_NAME": (
        "LaTeX Warning: You have requested package `x', but the package provides `y'."
    ),
    "SCRLAYER_FOOTHEIGHT_TOO_LOW": (
        "Package scrlayer-scrpage Warning: \\footheight to low."
    ),
    "TYPEAREA_DIV_NOT_DEFINED_FOR_FONTSIZE": (
        "Package typearea Warning: DIV for 9.5pt and used papersize"
    ),
    "UNDERFULL_HBOX": "Underfull \\hbox (badness 5217) in paragraph at lines 21--21",
    "OVERFULL_HBOX": "Overfull \\hbox (0.95421pt too wide) in paragraph at lines 3--4",
}


@pytest.mark.parametrize("family,line", sorted(REVIVALS.items()))
def test_each_closed_family_is_seen_again_if_it_returns(
    family: str, line: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build = tmp_path / "MANUEL_1SPE"
    build.mkdir()
    for variant in gate.VARIANTS:
        (build / f"MANUEL_1SPE_{variant}.log").write_text(
            "Package microtype Info: rien à signaler.\n" + line + "\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(gate, "BUILD", build)

    result = gate.build()

    assert result["summary"]["LATEX_WARNINGS"] == 2
    assert result["summary"]["UNCLASSIFIED_WARNING_LINES"] == 0
    assert result["families"][family]["occurrences"] == 2
    assert gate.main(["--check"]) == 1


def test_a_warning_family_nobody_declared_is_blocking_not_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Une famille inconnue ne peut pas être « bénigne » : on ne l'a pas vue."""

    build = tmp_path / "MANUEL_1SPE"
    build.mkdir()
    for variant in gate.VARIANTS:
        (build / f"MANUEL_1SPE_{variant}.log").write_text(
            "Package hyperref Warning: Token not allowed in a PDF string.\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(gate, "BUILD", build)

    result = gate.build()

    assert result["summary"]["UNCLASSIFIED_WARNING_LINES"] == 2
    assert result["summary"]["LATEX_WARNINGS"] == 2
    assert "hyperref" in result["variants"][0]["unclassified"][0]["text"]
    assert gate.main(["--check"]) == 1


def test_a_missing_log_is_refused_rather_than_reported_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gate, "BUILD", tmp_path)

    with pytest.raises(gate.WarningGateError):
        gate.build()
    assert gate.main(["--check"]) == 2


# ---------------------------------------------------------------------------
#  Les causes, telles qu'elles ont été refermées dans les sources
# ---------------------------------------------------------------------------


def test_the_margin_colour_group_closes_inside_the_captured_box() -> None:
    rail = (ROOT / "gabarits/common/nexus-margin-rail.tex").read_text(encoding="utf-8")

    assert "\\nxMargeCouleurDebut" in rail
    assert "\\nxMargeCouleurFin" in rail
    assert "\\color@begingroup" in rail and "\\color@endgroup" in rail
    # La boîte capturée doit refermer la couleur avant sa propre accolade.
    capture = rail[rail.index("\\nxMarginCaptureBox=\\vbox{") :]
    capture = capture[: capture.index("\\directlua")]
    assert capture.index("\\nxMargeCouleurDebut") < capture.index("#2")
    assert capture.index("#2") < capture.index("\\nxMargeCouleurFin")


def test_the_foot_height_is_measured_and_not_written_down() -> None:
    """Aucune constante : la hauteur vient de la pastille la plus haute."""

    cls = (ROOT / "gabarits/common/nexus-manuel.cls").read_text(encoding="utf-8")
    block = cls[cls.index("\\newsavebox{\\nxFolioPastilleLaPlusHaute}") :][:700]

    assert "\\sbox{\\nxFolioPastilleLaPlusHaute}{\\strut\\nxFolioPastille{000}}" in block
    assert "\\setlength{\\footheight}{" in block
    assert re.search(r"\\setlength\{\\footheight\}\{\s*[\d.]+pt", block) is None


def test_the_page_geometry_is_written_and_not_inferred() -> None:
    """`DIV=6` est écrit : plus aucune table n'est cherchée puis manquée."""

    cls = (ROOT / "gabarits/common/nexus-manuel.cls").read_text(encoding="utf-8")

    loads = [block[: block.index("]")] for block in cls.split("\\LoadClass[")[1:]]
    assert len(loads) == 2
    for options in loads:
        assert "DIV=6" in options
        assert "calc" not in options


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_the_written_div_is_the_one_the_calculation_gives(tmp_path: Path) -> None:
    """Écrire `DIV=6` ne devait rien changer : il faut le prouver, pas le dire.

    typearea ne tabule aucun DIV pour un corps de 9,5 pt : il le CALCULAIT, et
    le signalait. La classe écrit désormais le résultat de ce calcul. Ce
    contrôle demande donc à typearea, seul et sans la classe, ce qu'il calcule
    pour ce papier et ce corps — et compare au nombre écrit.

    La mise en page finale du manuel n'est pas mesurée ici : `geometry` la
    fixe après typearea, et la relire ne dirait rien de la valeur écrite. La
    tentative précédente comparait justement ces longueurs-là, et un
    `\\KOMAoptions{DIV=calc}` tardif y écrasait `geometry` — le test échouait
    pour une raison qui n'était pas celle qu'il visait.
    """

    document = tmp_path / "typearea.tex"
    document.write_text(
        "\\documentclass[a4paper,fontsize=9.5pt,DIV=calc,twoside]{scrbook}\n"
        "\\begin{document}Texte.\\end{document}\n",
        encoding="utf-8",
    )
    subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            f"-output-directory={tmp_path}",
            str(document),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    log = (tmp_path / "typearea.log").read_text(encoding="utf-8", errors="replace")

    calculated = re.findall(r"DIV\s+=\s+(\d+)", log)
    assert calculated, "typearea n'a annoncé aucun DIV"
    # Aucun avertissement : `DIV=calc` est demandé, donc aucune table n'est
    # cherchée puis manquée.
    assert "typearea Warning" not in log

    cls = (ROOT / "gabarits/common/nexus-manuel.cls").read_text(encoding="utf-8")
    written = re.search(r"DIV=(\d+)", cls)
    assert written is not None
    assert written.group(1) == calculated[-1], (
        f"la classe écrit DIV={written.group(1)} là où le calcul donne "
        f"DIV={calculated[-1]}"
    )


def test_every_charter_file_declares_the_name_it_is_loaded_by() -> None:
    declared = sorted(
        path
        for path in ROOT.glob("**/gabarits/**/*.sty")
        if "reference-v4" not in path.parts
    ) + sorted(
        path
        for path in ROOT.glob("**/gabarits/**/*.cls")
        if "reference-v4" not in path.parts
    )
    assert declared, "aucun gabarit trouvé"
    for path in declared:
        text = path.read_text(encoding="utf-8")
        match = re.search(r"\\Provides(?:Class|Package)\{([^}]*)\}", text)
        if match is None:
            continue
        assert match.group(1) == "\\@currpath\\@currname", path
