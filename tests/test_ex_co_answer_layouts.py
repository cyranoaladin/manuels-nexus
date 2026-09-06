"""Les conventions de réponse réellement employées doivent être reconnues.

134 corrigés complets étaient classés « disposition non reconnue » parce que le
classifieur ne connaissait que trois formes de repérage. Trois causes
expliquent la totalité : le marqueur `Q1.`, sa variante annotée `Q1 (C6).`, et
la réponse par programme unique à un énoncé qui énumère les étapes d'un même
livrable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ex_co_answer_coverage as coverage  # noqa: E402

EXERCISE = "\n".join([
    "\\begin{enumerate}",
    "  \\item Première question.",
    "  \\item Deuxième question.",
    "  \\item Troisième question.",
    "\\end{enumerate}",
])


def _answer(*markers: str) -> str:
    return "\n".join(f"\\textbf{{{m}}} Une réponse." for m in markers)


@pytest.mark.parametrize("markers", [
    ("1.", "2.", "3."),
    ("Question 1.", "Question 2.", "Question 3."),
    ("Q1.", "Q2.", "Q3."),
    ("Q1 (C6).", "Q2 (C10).", "Q3 (C9)."),
])
def test_every_real_marker_convention_is_recognised(markers) -> None:
    verdict, _ = coverage.classify(EXERCISE, _answer(*markers))
    assert verdict == coverage.ESTABLISHED, markers


def test_a_genuinely_missing_answer_is_still_reported() -> None:
    verdict, evidence = coverage.classify(EXERCISE, _answer("Q1.", "Q2."))
    assert verdict == coverage.MISSING
    assert evidence["missing"] == [3]


def test_a_single_program_answers_a_list_of_steps() -> None:
    correction = "\\begin{python}\nprint('tout')\n\\end{python}\nExplication."
    verdict, evidence = coverage.classify(EXERCISE, correction)
    assert verdict == coverage.SINGLE_PROGRAM
    assert evidence["code_blocks"] == 1


def test_a_long_question_list_is_not_excused_by_a_code_block() -> None:
    """Au-delà de quatre items, ce sont des questions, pas des étapes."""
    long_exercise = "\n".join(
        ["\\begin{enumerate}"]
        + [f"  \\item Question {i}." for i in range(1, 7)]
        + ["\\end{enumerate}"]
    )
    verdict, _ = coverage.classify(long_exercise, "\\begin{python}\nx=1\n\\end{python}")
    assert verdict == coverage.UNRECOGNISED


def test_prose_without_any_marker_is_still_unrecognised() -> None:
    verdict, _ = coverage.classify(EXERCISE, "Une longue explication sans repère.")
    assert verdict == coverage.UNRECOGNISED


def test_the_corpus_has_no_unrecognised_layout_left() -> None:
    graph = json.loads((ROOT / "audit/EX_CO_GRAPH.json").read_text(encoding="utf-8"))
    assert graph["relation_counts"].get("UNKNOWN", 0) == 0
    assert graph["relation_counts"].get("ORPHAN_CO", 0) == 0
