from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "Mathematiques"
    / "manuel-maths"
    / "chapitres"
    / "1SPE-SUITES"
    / "remediation"
    / "1SPE-SUITES-RE-C8.tex"
)


def _source() -> str:
    return SOURCE.read_text(encoding="utf-8")


def test_c8_remediation_stays_unapproved() -> None:
    first_line = _source().splitlines()[0]
    metadata = json.loads(first_line.removeprefix("% META: "))

    assert metadata["id"] == "1SPE-SUITES-RE-C8"
    assert metadata["capacites_codes"] == ["C8"]
    assert metadata["status"] == "generated"


def test_c8_remediation_contains_the_complete_learning_loop() -> None:
    source = _source()

    for stage in (
        "Diagnostic de l'erreur",
        "Rappel ciblé",
        "Activité guidée",
        "Exercice autonome",
        "Revalidation",
    ):
        assert stage in source

    exercise_ids = re.findall(r"\\begin\{exercice\}\{([^}]+)\}", source)
    correction_ids = re.findall(r"\\begin\{corrige\}\{([^}]+)\}", source)
    assert exercise_ids == [
        "1SPE-SUITES-RE-C8-GUIDE",
        "1SPE-SUITES-RE-C8-AUTONOME",
        "1SPE-SUITES-RE-C8-REVALIDATION",
    ]
    assert correction_ids == exercise_ids
    assert r"\coupDePouce" in source

    ordered_markers = (
        "Diagnostic de l'erreur",
        "Rappel ciblé",
        "Aide graduée",
        r"\coupDePouce",
        "Activité guidée",
        r"\begin{exercice}{1SPE-SUITES-RE-C8-GUIDE}",
        r"\begin{corrige}{1SPE-SUITES-RE-C8-GUIDE}",
        "Exercice autonome",
        r"\begin{exercice}{1SPE-SUITES-RE-C8-AUTONOME}",
        r"\begin{corrige}{1SPE-SUITES-RE-C8-AUTONOME}",
        "Revalidation",
        r"\begin{exercice}{1SPE-SUITES-RE-C8-REVALIDATION}",
        r"\begin{corrige}{1SPE-SUITES-RE-C8-REVALIDATION}",
    )
    positions = [source.index(marker) for marker in ordered_markers]
    assert positions == sorted(positions)


def test_c8_remediation_targets_the_cause_without_formal_limit_theory() -> None:
    source = _source()
    lowered = source.lower()

    assert "observer plusieurs termes" in source
    assert "une moyenne n'est pas une limite" in lowered
    assert "conjecture" in lowered
    assert "sans démonstration formelle" in source
    assert "\\ln" not in source
    assert "théorème de convergence" not in lowered
    assert "passage à la limite" not in lowered


def test_c8_remediation_answers_are_scientifically_exact() -> None:
    source = _source()
    normalized = " ".join(source.split())

    assert r"p_n=5-3^{-n}" in source
    assert r"q_n=-n" in source
    assert r"r_n=(-2)^n" in source

    p_values = [Fraction(5) - Fraction(1, 3**n) for n in range(1, 7)]
    q_values = [-n for n in range(1, 7)]
    r_values = [(-2) ** n for n in range(1, 7)]
    assert p_values == [
        Fraction(14, 3),
        Fraction(44, 9),
        Fraction(134, 27),
        Fraction(404, 81),
        Fraction(1214, 243),
        Fraction(3644, 729),
    ]
    assert q_values == [-1, -2, -3, -4, -5, -6]
    assert r_values == [-2, 4, -8, 16, -32, 64]

    for expected in (
        r"a_6=\dfrac{65}{64}",
        r"b_6=64",
        r"c_6=1",
        r"\dfrac{14}{3},\ \dfrac{44}{9},\ \dfrac{134}{27},\ \dfrac{404}{81},\ \dfrac{1214}{243},\ \dfrac{3644}{729}",
        r"-1,\ -2,\ -3,\ -4,\ -5,\ -6",
        r"-2,\ 4,\ -8,\ 16,\ -32,\ 64",
    ):
        assert expected in source
    for conclusion in (
        "on conjecture une limite finie égale à $5$",
        "on conjecture une limite infinie égale à $-\\infty$",
        "on conjecture l'absence de limite",
    ):
        assert conclusion in normalized
