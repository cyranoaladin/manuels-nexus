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


# --- Non-régression des trois causes réellement rencontrées -----------------

def test_regression_a_remediation_correction_is_not_an_orphan() -> None:
    """Cause 1 : le corrigé vise un objet de `remediation/`, pas de `exercices/`."""
    graph = json.loads((ROOT / "audit/EX_CO_GRAPH.json").read_text(encoding="utf-8"))
    remediation = [
        row for row in graph["relations"]
        if "REMEDIATION_CORRECTION" in row["classifications"]
    ]
    assert remediation
    assert all("ORPHAN_CO" not in row["classifications"] for row in remediation)


def test_regression_the_third_question_is_answered_everywhere() -> None:
    """Cause 2 : seize corrigés laissaient la question 3 sans réponse."""
    graph = json.loads((ROOT / "audit/EX_CO_GRAPH.json").read_text(encoding="utf-8"))
    assert graph["relation_counts"].get("ANSWERS_MISSING", 0) == 0


@pytest.mark.parametrize("marker", ["Q1.", "Question 1.", "1.", "Q1 (C6)."])
def test_regression_every_tspe_question_syntax_is_understood(marker) -> None:
    """Cause 3 : trois syntaxes de repérage coexistent dans le corpus."""
    single = "\\begin{enumerate}\n  \\item Une question.\n\\end{enumerate}"
    verdict, _ = coverage.classify(single, f"\\textbf{{{marker}}} Réponse.")
    assert verdict == coverage.ESTABLISHED, marker


def test_remediation_objects_are_not_subject_to_the_cardinality_rule() -> None:
    """Une remédiation n'exige pas de corrigé : elle n'est pas un exercice orphelin."""
    graph = json.loads((ROOT / "audit/EX_CO_GRAPH.json").read_text(encoding="utf-8"))
    assert graph["exercise_cardinality_counts"].get("ORPHAN_EX", 0) == 0
    # Un exercice n'est classe hors MATCH que pour une raison nommee. La
    # seule admise ici : son corrige existe et le nomme, mais le credit
    # pedagogique de la paire n'est pas etabli (P0 de clonage). Toute autre
    # classe -- orpheline, cardinalite multiple, inconnue -- fait echouer.
    assert set(graph["exercise_cardinality_counts"]) <= {
        "MATCH",
        "CORRECTION_ON_INDETERMINATE_CREDIT",
    }, graph["exercise_cardinality_counts"]


def test_an_unrecognised_layout_is_no_longer_tolerated_by_the_chapter_matrix() -> None:
    """`UNKNOWN` ne fait plus partie des verdicts sans conséquence."""
    source = (ROOT / "scripts/build_publish_readiness_chapter_matrix.py").read_text(
        encoding="utf-8"
    )
    block = source.split("NOT_A_FAILURE = {", 1)[1].split("}", 1)[0]
    assert '"UNKNOWN"' not in block
    assert '"REMEDIATION_CORRECTION"' in block
    assert '"SINGLE_PROGRAM_ANSWER"' in block
