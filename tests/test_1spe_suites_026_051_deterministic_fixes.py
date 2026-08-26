from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"
EXERCISES = CHAPTER / "exercices"
CORRECTIONS = CHAPTER / "corriges"
PYTHON = CHAPTER / "python"


def _exercise(number: int) -> Path:
    return EXERCISES / f"1SPE-SUITES-EX-{number:03d}.tex"


def _correction(number: int) -> Path:
    return CORRECTIONS / f"1SPE-SUITES-CO-{number:03d}.tex"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _meta(path: Path) -> dict:
    first_line = _source(path).splitlines()[0]
    assert first_line.startswith("% META: ")
    return json.loads(first_line.removeprefix("% META: "))


def _run_python(number: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PYTHON / f"1SPE-SUITES-EX-{number:03d}.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )


def _oracle(path: Path) -> str:
    lines = _source(path).splitlines()
    start = lines.index("% BEGIN-VERIFY")
    end = lines.index("% END-VERIFY")
    return "\n".join(
        line[2:] if line.startswith("% ") else line[1:]
        for line in lines[start + 1 : end]
    )


def test_changed_inline_oracles_execute() -> None:
    for number in (29, 32, 33, 34, 35, 39, 41, 42, 45, 47, 50, 51):
        for path in (_exercise(number), _correction(number)):
            exec(compile(_oracle(path), str(path), "exec"), {})


@pytest.mark.parametrize(
    ("number", "codes"),
    (
        (32, ("C3", "C5", "C6")),
        (33, ("C2", "C5", "C6")),
        (34, ("C3", "C6", "C7")),
        (35, ("C2", "C6", "C7")),
        (39, ("C2", "C3", "C6")),
        (45, ("C1", "C3", "C5", "C8")),
        (50, ("C3", "C6", "C7")),
    ),
)
@pytest.mark.parametrize("path_factory", (_exercise, _correction))
def test_capacity_metadata_matches_the_exercised_work(
    number: int, codes: tuple[str, ...], path_factory
) -> None:
    meta = _meta(path_factory(number))

    assert meta["capacites_codes"] == list(codes)
    assert meta["capacites"] == [f"1SPE-SUITES-{code}" for code in codes]


def test_ex035_uses_the_strict_threshold_and_interprets_the_sum_honestly() -> None:
    exercise = _source(_exercise(35))
    correction = _source(_correction(35))

    assert "somme des douze relevés de population" in exercise
    assert "population totale cumulée" not in exercise
    assert "while N <= 2000:" in _source(PYTHON / "1SPE-SUITES-EX-035.py")
    assert all(token in exercise for token in (r"N_{16}", r"N_{17}"))
    assert "ne représente ni la population présente" in correction
    assert "ni un nombre d'habitants distincts" in correction
    assert r"S = u_0 + \cdots + u_n = (n+1) \times \frac{u_0+u_n}{2}" in correction
    assert r"\frac{p \times (u_1+u_p)}{2}" not in correction
    assert all(token in correction for token in ("2037", "2050", r"N_{16}", r"N_{17}"))
    assert "2036" not in correction


@pytest.mark.parametrize(
    ("number", "rendered_in", "expected_output"),
    (
        (34, "exercise", "n=9, K=3102.66\n"),
        (35, "exercise", "Annee : 2037\nPopulation : 2050\n"),
        (47, "correction", ""),
        (50, "exercise", "n=19, v=2157.85\n"),
    ),
)
def test_rendered_python_has_one_canonical_executable_source(
    number: int, rendered_in: str, expected_output: str
) -> None:
    script = PYTHON / f"1SPE-SUITES-EX-{number:03d}.py"
    source = _source(script)
    ast.parse(source)
    result = _run_python(number)
    assert result.returncode == 0, result.stdout + result.stderr
    if number == 47:
        lines = result.stdout.splitlines()
        assert lines == [
            f"n={n}, u_n={n**2 + n + 1}, d_n={2*n + 2}"
            for n in range(21)
        ]
    else:
        assert result.stdout == expected_output

    include = (
        rf"\lstinputlisting[language=Python]"
        rf"{{chapitres/1SPE-SUITES/python/1SPE-SUITES-EX-{number:03d}.py}}"
    )
    exercise = _source(_exercise(number))
    correction = _source(_correction(number))
    rendered_source = exercise if rendered_in == "exercise" else correction
    assert include in rendered_source
    assert (exercise + correction).count(include) == 1
    assert r"\begin{lstlisting}" not in exercise + correction


def test_ex039_proves_the_specific_comparison_with_first_spe_tools() -> None:
    exercise = _source(_exercise(39))
    correction = _source(_correction(39))

    assert r"A_{n+1}-A_n" in exercise
    assert r"B_{n+1}-B_n" in exercise
    assert r"pour tout entier $n \geq 2$" in exercise
    assert all(
        token in correction
        for token in (
            r"A_{n+1}-A_n=0{,}07A_n",
            r"0{,}07A_n \geq 224{,}70 > 210",
            r"A_{n+1}-B_{n+1}",
            r"A_n-B_n",
        )
    )
    rendered = exercise + correction
    assert "l'exponentielle domine" not in rendered
    assert "croissance exponentielle" not in rendered
    assert "à long terme" not in rendered.lower()


def test_ex029_has_no_duplicate_variation_question() -> None:
    exercise = _source(_exercise(29))
    correction = _source(_correction(29))

    assert "Comparer $u_n$ et $u_{n+1}$" not in exercise
    assert "Question 3 — Comparaison" not in correction
    assert "Question 3 — Étude de $(v_n)$" in correction
    assert "Question 4 — Étude de $(w_n)$" in correction
    assert "Q5" not in correction


def test_ex032_is_noncircular_and_uses_the_strict_lexical_threshold() -> None:
    exercise = _source(_exercise(32))
    correction = _source(_correction(32))
    question_1 = correction.split("Question 1", 1)[1].split("Question 2", 1)[0]

    assert r"C_n > 1\,200" in exercise
    assert r"C_n \geq 1\,200" not in exercise
    assert "d'après la relation de récurrence" in question_1.lower()
    assert r"C_n = 800 \times 1{,}03^n" not in question_1
    assert r"\frac{C_{n+1}}{C_n}" not in question_1
    assert r"C_n > 1\,200" in correction
    assert r"C_{13} < 1\,200 < C_{14}" in correction


def test_co033_does_not_invent_a_calendar_origin() -> None:
    correction = _source(_correction(33))

    assert "2020" not in correction
    assert "2038" not in correction
    assert "rang $n=18$" in correction


def test_co041_proves_minimality_over_every_preceding_integer() -> None:
    correction = _source(_correction(41))

    for n in range(9):
        assert f"{n} &" in correction
    assert "Ainsi, aucun rang de $0$ à $7$" in correction
    assert r"La plus petite valeur est $\boxed{n = 8}$" in correction


@pytest.mark.parametrize("path", (_exercise(42), _correction(42)))
def test_ex042_stays_in_the_canonical_first_spe_path(path: Path) -> None:
    meta = _meta(path)

    assert set(meta["capacites_codes"]) == {"C4", "C5", "C8"}
    assert "programme_role" not in meta
    assert "mandatory_for_coverage" not in meta
    assert "release_acceptance" not in meta
    assert "extension_codes" not in meta


def test_ex042_uses_only_geometric_sums_and_intuitive_observation() -> None:
    exercise = _source(_exercise(42))
    correction = _source(_correction(42))

    rendered = exercise + correction
    assert r"u_n=2\left(\frac34\right)^n" in exercise
    assert r"S_n=8\left(1-\left(\frac34\right)^{n+1}\right)" in correction
    assert r"S_{n+1}-S_n=u_{n+1}>0" in correction
    assert "On conjecture" in correction
    assert "sans preuve formelle" in correction
    assert "décomposition en éléments simples" not in rendered.lower()
    assert r"\frac{A}{k}" not in rendered


def test_ex034_never_uses_logarithms_even_in_embedded_verification() -> None:
    for path in (_exercise(34), _correction(34)):
        source = _source(path)
        assert "math.log" not in source
        assert "import math" not in source


def test_ex045_has_exact_generalized_difference_and_conjectural_c8_wording() -> None:
    exercise = _source(_exercise(45))
    correction = _source(_correction(45))

    assert "semblent-elles se rapprocher d'une valeur" in exercise
    assert "semblent-elles converger" not in exercise
    assert r"u_{n+1}-u_n=-\left(\frac12\right)^n" in correction
    assert r"-\left(\frac12\right)^{n+1}" not in correction
    assert "On conjecture que ses termes se rapprochent de $6$" in correction
    assert "décroît vers $6$" not in correction


def test_ex050_is_a_real_algorithmic_adaptation_not_a_completion_clone() -> None:
    exercise = _source(_exercise(50))
    correction = _source(_correction(50))

    assert "Compléter" not in exercise
    assert "fonction" in exercise
    assert r"seuil de $2\,500$" in exercise
    assert r"premier\_depassement" in exercise
    assert all(token in correction for token in (r"v_{20}", r"v_{21}", r"2\,500"))


def test_ex051_is_an_independent_mastery_task_and_exercises_representation() -> None:
    exercise = _source(_exercise(51))
    correction = _source(_correction(51))

    assert all(
        token in exercise
        for token in (
            r"a_n=1+\frac{1}{n+1}",
            r"b_n=3n+2",
            r"c_n=2+(-1)^n",
            "représenter",
            "points $(n;a_n)$",
        )
    )
    assert r"3+\left(\frac12\right)^n" not in exercise
    assert r"n^2" not in exercise
    assert all(token in correction for token in (r"\frac32", r"\frac43", r"\frac76", r"\frac{12}{11}"))
    assert "sans démonstration formelle" in correction
