"""Une ouverture de chapitre, une page — et le contrôle doit pouvoir échouer.

Le débordement d'une ouverture ne produit aucun avertissement : `\\vfill` avale
la coupure, `Overfull = 0` reste vrai, et le journal LaTeX ne dit rien. Il ne se
voit que sur la page rendue. Ce module vérifie l'invariant sur les deux manuels
construits, compile une ouverture à la hauteur maximale observée pour que le
système ne redevienne pas fragile, et en compile une volontairement trop haute
pour prouver que la mesure sait dire non.
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
MANUAL_ROOT = ROOT / "Mathematiques/manuel-maths"
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_chapter_opener_span as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
#  L'invariant, sur les deux manuels construits
# ---------------------------------------------------------------------------


def test_every_chapter_opener_holds_on_a_single_page(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    assert summary["OPENERS_FOUND"] == summary["OPENERS_EXPECTED"] == 20
    assert summary["MULTI_PAGE_OPENERS"] == 0
    assert summary["SINGLE_PAGE_OPENERS"] == 20
    for variant in payload["variants"]:
        assert len(variant["openers"]) == 10, variant["variant"]
        for opener in variant["openers"]:
            assert opener["opening_start_page"] == opener["opening_end_page"], opener
            assert opener["page_span"] == 1, opener


def test_no_opener_information_is_pushed_to_a_second_page(
    payload: dict[str, Any],
) -> None:
    """L'invariant C : rien ne doit être rejeté par la seule mise en page."""

    assert payload["summary"]["OPENER_MISSING_CONTENT"] == 0
    for variant in payload["variants"]:
        for opener in variant["openers"]:
            assert opener["missing_on_the_opening_page"] == [], opener
            assert opener["pushed_to_the_overflow_page"] == [], opener


def test_the_estimated_time_stayed_on_the_opener(payload: dict[str, Any]) -> None:
    """Cinq ouvertures sur dix ne rejetaient QUE ces vingt-neuf caractères."""

    assert "estimated_time" in gate.REQUIRED_CONTENT
    for variant in payload["variants"]:
        for opener in variant["openers"]:
            assert "estimated_time" not in opener["missing_on_the_opening_page"]


def test_no_page_number_is_written_into_the_producer(
    payload: dict[str, Any],
) -> None:
    """L'ouverture est trouvée par ce qu'elle porte, jamais par son folio."""

    assert payload["no_page_number_is_written_down"] is True
    source = (ROOT / "scripts/build_1spe_chapter_opener_span.py").read_text(
        encoding="utf-8"
    )
    start = source.index("BANNER = re.compile")
    end = source.index("class SpanError")
    detection = source[start:end]
    # Ce qui est interdit, c'est un FOLIO écrit en dur -- pas le mot « page »,
    # que les commentaires emploient forcément pour expliquer ce qu'ils font.
    # Bannir le mot faisait échouer ce contrôle sur une prose parfaitement
    # saine, et ne disait rien du défaut qu'il vise.
    for line in detection.splitlines():
        code = line.split("#", 1)[0]
        if not code.strip() or code.lstrip().startswith(('"', "'")):
            continue
        assert not re.search(r"\b\d{2,4}\b", code), (
            f"un numéro de page semble écrit en dur : {line.strip()}"
        )
    assert "EXPECTED_OPENERS" not in detection


# ---------------------------------------------------------------------------
#  Compilations : la hauteur maximale, et une hauteur volontairement excessive
# ---------------------------------------------------------------------------


def _opener_document(capacities: list[str], hook: str) -> str:
    items = "\n".join(
        f"\\item \\textbf{{C{index}}} --- {text}"
        for index, text in enumerate(capacities, start=1)
    )
    return (
        "\\documentclass{gabarits/nexus-manuel-v5}\n"
        "\\usepackage{gabarits/nexus-charte-v6}\n"
        "\\nxVSuppressTabtrue\n\\nxVersionProfesseurfalse\n"
        "\\matiere{Mathématiques}\\niveau{Première spécialité}\n"
        "\\begin{document}\\nxActiverDecor\n"
        "\\ouverturechapitre{Chapitre de contrainte}"
        f"{{\\begin{{itemize}}\n{items}\n\\end{{itemize}}}}"
        f"{{{hook}}}"
        "{\\parcoursUn~12 h \\quad \\parcoursDeux~10 h \\quad \\parcoursTrois~8 h}\n"
        "\\end{document}\n"
    )


def _compile_pages(tmp_path: Path, source: str) -> int:
    document = tmp_path / "opener.tex"
    document.write_text(source, encoding="utf-8")
    environment = os.environ.copy()
    environment.update(
        {
            "NEXUS_MARGIN_RUN_NONCE": "0" * 32,
            "NEXUS_MARGIN_VARIANT": "eleve",
            "NEXUS_MARGIN_PASS_NUMBER": "1",
        }
    )
    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            f"-output-directory={tmp_path}",
            str(document),
        ],
        cwd=MANUAL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    pdf = tmp_path / "opener.pdf"
    assert pdf.is_file(), result.stdout[-4000:]
    fitz = pytest.importorskip("fitz")
    with fitz.open(pdf) as rendered:
        return rendered.page_count


# La contrainte n'est pas imaginée : elle est LUE dans le corpus. Le chapitre
# le plus chargé du manuel fournit la fixture, si bien qu'allonger ses capacités
# fait échouer ce test AVANT toute reconstruction. C'est ce que demande
# l'anti-fragilité : la mesure suit le contenu, elle ne le devine pas.
def _heaviest_chapter() -> tuple[str, list[str], str]:
    yaml = pytest.importorskip("yaml")
    chapters = sorted(
        (MANUAL_ROOT / "chapitres").glob("1SPE-*/contrat.yaml")
    )
    assert chapters, "aucun contrat de chapitre 1SPE"
    worst = None
    for path in chapters:
        contract = yaml.safe_load(path.read_text(encoding="utf-8"))
        capacities = [item["libelle_eleve"] for item in contract["capacites"]]
        hook = contract.get("situation_accroche", "")
        weight = sum(len(text) for text in capacities) + len(hook)
        if worst is None or weight > worst[0]:
            worst = (weight, path.parent.name, capacities, hook)
    return worst[1], worst[2], worst[3]


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_the_heaviest_chapter_of_the_corpus_holds_on_one_page(
    tmp_path: Path,
) -> None:
    """La contrainte réelle du corpus, recompilée seule : elle doit tenir."""

    name, capacities, hook = _heaviest_chapter()
    pages = _compile_pages(tmp_path, _opener_document(capacities, hook))

    assert pages == 1, f"{name} ne tient plus sur une page"


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_one_capacity_more_than_the_corpus_maximum_is_visibly_multi_page(
    tmp_path: Path,
) -> None:
    """La mutation : le budget est mesuré, pas suppose.

    Le chapitre le plus lourd du corpus, augmente de sa propre capacite la plus
    longue, doit deborder. Sans cette borne, le controle precedent pourrait
    passer parce que la mise en page tolere tout plutot que parce qu'elle tient,
    et la marge reelle resterait inconnue.
    """

    _name, capacities, hook = _heaviest_chapter()
    longest = max(capacities, key=len)
    pages = _compile_pages(tmp_path, _opener_document(capacities + [longest] * 3, hook))

    assert pages > 1


# ---------------------------------------------------------------------------
#  La règle d'étendue, éprouvée sur des pages synthétiques
# ---------------------------------------------------------------------------


class _FakeDocument:
    """Un document réduit à ses textes de page."""

    def __init__(self, pages: list[str]) -> None:
        self._pages = pages
        self.page_count = len(pages)

    def __getitem__(self, index: int) -> Any:
        text = self._pages[index]
        return type("Page", (), {"get_text": lambda self, *a, **k: text})()


BANNER_PAGE = (
    "MATHÉMATIQUES ⋅Première spécialité 1 CHAPITRE 1 Suites numériques "
    "Objectifs — Capacités attendues ▶C1 — Je sais compter. "
    "À RETENIR Une situation d'accroche. Temps estimés : 12 h 10 h 8 h"
)
CHAPTER_OUVERTURE_SECTION = (
    "OUVERTURE Ouverture Contrat du chapitre Ce que tu vas savoir faire "
    "À la fin de ce chapitre, tu seras capable de : C1 Calculer les termes"
)


def test_the_chapter_ouverture_section_is_not_an_overflow() -> None:
    """La section d'ouverture porte la même rubrique : elle n'est pas un débord.

    C'est le piège qui faisait compter quatre débordements sur une mise en
    page saine.
    """

    rows = gate.opener_spans(
        _FakeDocument([BANNER_PAGE, CHAPTER_OUVERTURE_SECTION, "COURS Cours ..."])
    )

    assert len(rows) == 1
    assert rows[0]["page_span"] == 1
    assert rows[0]["single_page"] is True
    assert rows[0]["missing_on_the_opening_page"] == []


def test_a_time_line_pushed_to_the_next_page_is_an_overflow() -> None:
    """Le défaut réel : vingt-neuf caractères seuls sur une page entière."""

    banner_without_time = BANNER_PAGE.replace("Temps estimés : 12 h 10 h 8 h", "")
    rows = gate.opener_spans(
        _FakeDocument(
            [
                banner_without_time,
                "OUVERTURE Ouverture Temps estimés : 12 h 10 h 8 h",
                "COURS Cours ...",
            ]
        )
    )

    assert rows[0]["page_span"] == 2
    assert rows[0]["single_page"] is False
    assert rows[0]["missing_on_the_opening_page"] == ["estimated_time"]
    assert rows[0]["pushed_to_the_overflow_page"] == ["estimated_time"]


def test_a_hook_pushed_to_the_next_page_is_an_overflow() -> None:
    banner_without_hook = BANNER_PAGE.replace(
        "À RETENIR Une situation d'accroche. ", ""
    )
    rows = gate.opener_spans(
        _FakeDocument(
            [
                banner_without_hook,
                "OUVERTURE Ouverture À RETENIR Une situation d'accroche.",
                "COURS Cours ...",
            ]
        )
    )

    assert rows[0]["page_span"] == 2
    assert rows[0]["missing_on_the_opening_page"] == ["hook"]
