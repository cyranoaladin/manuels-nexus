from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques" / "manuel-maths"
CHAPTER = MANUAL / "chapitres" / "1SPE-SUITES"
EXERCISES = CHAPTER / "exercices"
CORRECTIONS = CHAPTER / "corriges"
PYTHON = CHAPTER / "python"


def _path(kind: str, number: str) -> Path:
    directory = EXERCISES if kind == "EX" else CORRECTIONS
    return directory / f"1SPE-SUITES-{kind}-{number}.tex"


def _text(kind: str, number: str) -> str:
    return _path(kind, number).read_text(encoding="utf-8")


def _meta(kind: str, number: str) -> dict:
    first_line = _text(kind, number).splitlines()[0]
    assert first_line.startswith("% META: ")
    return json.loads(first_line.removeprefix("% META: "))


def _assert_exact_program(path: Path, expected: str, stdout: str) -> None:
    source = path.read_text(encoding="utf-8")
    assert ast.dump(ast.parse(source), include_attributes=False) == ast.dump(
        ast.parse(expected), include_attributes=False
    )
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=MANUAL,
        text=True,
        capture_output=True,
        check=False,
        timeout=2,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert completed.stdout == stdout


def test_recurrence_language_is_unambiguous_and_fibonacci_claim_is_honest() -> None:
    exercise_003 = _text("EX", "003")
    correction_003 = _text("CO", "003")
    correction_005 = _text("CO", "005")

    assert "par une relation de récurrence" in exercise_003
    assert "définie par une \\textbf{relation de récurrence}" in correction_003
    assert "lorsqu'on utilise uniquement la relation de récurrence donnée" in correction_003.lower()
    assert "nécessite impérativement la connaissance du terme précédent" not in correction_003
    assert "on ne peut pas calculer $u_5$ directement" not in correction_003
    assert "aucune formule explicite n'est donnée ici" in correction_005
    assert "aucune formule ne permet de calculer" not in correction_005


def test_015_proves_strict_positivity_before_forming_the_quotient() -> None:
    exercise = _text("EX", "015")
    correction = _text("CO", "015")

    assert exercise.index("Tous les termes") < exercise.index(
        r"Calculer $\dfrac{u_{n+1}}{u_n}$"
    )
    question_1 = correction.split("Question 1", 1)[1].split("Question 2", 1)[0]
    question_2 = correction.split("Question 2", 1)[1].split("Question 3", 1)[0]
    assert "strictement positifs" in question_1
    assert r"\dfrac{u_{n+1}}{u_n}" not in question_1
    assert r"\dfrac{u_{n+1}}{u_n}" in question_2
    assert "Puisque $u_n > 0$" in question_2


def test_latex_relations_and_arithmetic_sum_indexing_are_well_formed() -> None:
    correction_011 = _text("CO", "011")
    correction_016 = _text("CO", "016")
    correction_023 = _text("CO", "023")
    correction_024 = _text("CO", "024")

    assert r"S = u_0 + \cdots + u_n = (n+1) \times \frac{u_0+u_n}{2}" in correction_011
    assert r"$\nearrow$" in correction_016
    assert "$\n" + "earrow$" not in correction_016
    assert r"40 \not> 40" in correction_023
    assert r"S_n = u_0 + \cdots + u_n = \frac{(n+1)(u_0+u_n)}{2}" in correction_024


def test_threshold_boundary_values_explicitly_prove_minimality() -> None:
    correction_024 = _text("CO", "024")
    correction_025 = _text("CO", "025")

    assert "Ces deux valeurs consécutives prouvent que $n=28$ est le plus petit rang" in correction_024
    assert "Ces deux valeurs consécutives prouvent que $n=17$ est le plus petit rang" in correction_025


def test_020_uses_one_executable_python_source_with_exact_semantics() -> None:
    path = PYTHON / "1SPE-SUITES-EX-020.py"
    listing = "chapitres/1SPE-SUITES/python/1SPE-SUITES-EX-020.py"

    assert rf"\lstinputlisting[language=Python]{{{listing}}}" in _text("EX", "020")
    assert r"\texttt{u = 2}\\" not in _text("EX", "020")
    assert r"\texttt{u = 2}\\" not in _text("CO", "020")
    _assert_exact_program(
        path,
        """u = 2
for k in range(5):
    u = 2 * u + 3
print(u)
""",
        "157\n",
    )
    assert "affiche donc \\textbf{157}" in _text("CO", "020")


def test_021_uses_one_executable_python_source_with_exact_semantics() -> None:
    path = PYTHON / "1SPE-SUITES-EX-021.py"
    listing = "chapitres/1SPE-SUITES/python/1SPE-SUITES-EX-021.py"

    assert rf"\lstinputlisting[language=Python]{{{listing}}}" in _text("EX", "021")
    assert r"\texttt{u = 3}\\" not in _text("EX", "021")
    _assert_exact_program(
        path,
        """u = 3
S = 3
for k in range(4):
    u = 2 * u
    S = S + u
print(S)
""",
        "93\n",
    )
    assert "affiche donc \\textbf{93}" in _text("CO", "021")


def test_ten_capacity_pairs_have_exact_qualified_metadata() -> None:
    expected = {
        "007": {"C2", "C5"},
        "010": {"C3", "C5"},
        "012": {"C3", "C4"},
        "015": {"C3", "C5"},
        "017": {"C2", "C6"},
        "018": {"C3", "C6"},
        "019": {"C3", "C6"},
        "021": {"C4", "C7"},
        "023": {"C1", "C2", "C5"},
        "024": {"C2", "C4", "C6"},
    }

    for number, expected_codes in expected.items():
        expected_qualified = {f"1SPE-SUITES-{code}" for code in expected_codes}
        for kind in ("EX", "CO"):
            metadata = _meta(kind, number)
            assert set(metadata["capacites_codes"]) == expected_codes
            assert set(metadata["capacites"]) == expected_qualified


def test_mastery_exercises_001_025_already_have_required_baremes() -> None:
    mastery_numbers = {
        f"{number:03d}"
        for number in range(1, 26)
        if _meta("EX", f"{number:03d}")["parcours"] == 2
    }

    assert mastery_numbers == {"022", "023", "024", "025"}
    for number in mastery_numbers:
        assert r"\baremeIndicatif{" in _text("CO", number)
