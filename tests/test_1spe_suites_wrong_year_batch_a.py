from __future__ import annotations

import ast
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques" / "manuel-maths" / "chapitres" / "1SPE-SUITES"
EXERCISES = CHAPTER / "exercices"
CORRECTIONS = CHAPTER / "corriges"
PYTHON = CHAPTER / "python"

EX026 = EXERCISES / "1SPE-SUITES-EX-026.tex"
CO026 = CORRECTIONS / "1SPE-SUITES-CO-026.tex"
EX031 = EXERCISES / "1SPE-SUITES-EX-031.tex"
CO031 = CORRECTIONS / "1SPE-SUITES-CO-031.tex"
EX044 = EXERCISES / "1SPE-SUITES-EX-044.tex"
CO044 = CORRECTIONS / "1SPE-SUITES-CO-044.tex"
EX046 = EXERCISES / "1SPE-SUITES-EX-046.tex"
CO046 = CORRECTIONS / "1SPE-SUITES-CO-046.tex"
PY044 = PYTHON / "1SPE-SUITES-EX-044.py"

TARGET_TEX = (EX026, CO026, EX031, CO031, EX044, CO044, EX046, CO046)


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _rendered(path: Path) -> str:
    rendered: list[str] = []
    for line in _source(path).splitlines():
        for index, character in enumerate(line):
            if character != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                line = line[:index]
                break
        rendered.append(line)
    return "\n".join(rendered)


def _meta(path: Path) -> dict:
    first_line = _source(path).splitlines()[0]
    assert first_line.startswith("% META: ")
    return json.loads(first_line.removeprefix("% META: "))


def _section(source: str, start: str, end: str) -> str:
    return source.split(start, 1)[1].split(end, 1)[0]


def _oracle(path: Path) -> str:
    lines = _source(path).splitlines()
    start = lines.index("% BEGIN-VERIFY")
    end = lines.index("% END-VERIFY")
    return "\n".join(
        line[2:] if line.startswith("% ") else line[1:]
        for line in lines[start + 1 : end]
    )


def _assert_repayment_script_ast_contract(source: str) -> dict[str, int | float]:
    module = ast.parse(source)
    assert len(module.body) == 6

    assignments: dict[str, int | float] = {}
    for statement in module.body[:4]:
        assert isinstance(statement, ast.Assign)
        assert len(statement.targets) == 1
        target = statement.targets[0]
        assert isinstance(target, ast.Name)
        value = ast.literal_eval(statement.value)
        assert isinstance(value, int | float)
        assignments[target.id] = value
    assert assignments == {"C": 120000, "t": 0.005, "m": 800, "n": 0}

    loop = module.body[4]
    assert isinstance(loop, ast.While)
    expected_test = ast.parse("C > 0", mode="eval").body
    assert ast.dump(loop.test) == ast.dump(expected_test)
    expected_body = ast.parse("C = (1 + t) * C - m\nn = n + 1").body
    assert [ast.dump(statement) for statement in loop.body] == [
        ast.dump(statement) for statement in expected_body
    ]
    assert loop.orelse == []

    output = module.body[5]
    assert isinstance(output, ast.Expr)
    assert isinstance(output.value, ast.Call)
    call = output.value
    assert isinstance(call.func, ast.Name) and call.func.id == "print"
    assert len(call.args) == 1
    assert isinstance(call.args[0], ast.Name) and call.args[0].id == "n"
    assert call.keywords == []
    return assignments


def test_026_statement_uses_readings_and_a_first_spe_threshold_method() -> None:
    exercise = _rendered(EX026)

    assert "huit relevés" in exercise
    assert "aux instants $0$ h, $1$ h, $\\ldots$, $7$ h" in exercise
    assert "bactéries accumulées" not in exercise
    assert all(token in exercise for token in (r"u_5", r"u_6", "essais successifs"))
    assert r"\log" not in exercise
    assert r"\ln" not in exercise


def test_026_correction_is_non_circular_and_proves_the_exact_boundary() -> None:
    correction = _rendered(CO026)
    question_1 = _section(correction, "Question 1", "Question 2")

    assert r"u_{n+1} = 2 \, u_n" in question_1
    assert "par définition" in question_1
    assert r"\frac{u_{n+1}}{u_n}" not in question_1
    assert r"u_n = 3 \times 2^n" not in question_1
    assert "somme des huit relevés" in correction
    assert all(token in correction for token in (r"u_5 = 3 \times 2^5", "96", r"u_6 = 3 \times 2^6", "192"))
    assert "au bout de $6$ heures" in correction
    assert r"\log" not in correction
    assert r"\ln" not in correction
    assert "passage au log" not in correction


def test_031_replaces_logarithms_with_the_reciprocal_sequence() -> None:
    exercise = _rendered(EX031)
    correction = _rendered(CO031)

    assert r"v_n = \dfrac{1}{u_n}" in exercise
    assert "suite géométrique" in _section(exercise, r"v_n = \dfrac{1}{u_n}", r"\end{enumerate}")
    assert r"\frac{1}{2}\left(\frac{3}{5}\right)^n" in correction
    assert r"q_v = \dfrac{3}{5}" in correction
    assert "strictement décroissante" in correction
    for source in (exercise, correction):
        assert r"\log" not in source
        assert r"\ln" not in source
    for path in (EX031, CO031):
        assert set(_meta(path)["capacites_codes"]) == {"C3", "C5"}


def test_031_reserves_the_quotient_for_variation_question_2a() -> None:
    exercise = _rendered(EX031)
    correction = _rendered(CO031)
    exercise_q1 = _section(exercise, r"\item", r"\item Étudier")
    exercise_q2 = _section(exercise, r"\item Étudier", r"\item Pour tout")
    correction_q1 = _section(correction, "Question 1", "Question 2")
    correction_q2 = _section(correction, "Question 2", "Question 3")

    assert "Reconnaître directement" in exercise_q1
    assert r"\dfrac{u_{n+1}}{u_n}" not in exercise_q1
    assert r"\dfrac{u_{n+1}}{u_n}" in exercise_q2
    assert "forme explicite" in correction_q1
    assert r"\frac{u_{n+1}}{u_n}" not in correction_q1
    assert r"\dfrac{u_{n+1}}{u_n}" in correction_q2
    assert "identification directe" in correction


def test_044_uses_an_executable_source_and_matches_the_correction() -> None:
    exercise = _rendered(EX044)
    correction = _rendered(CO044)

    assert PY044.is_file()
    assert "1SPE-SUITES" not in _source(PY044)
    assert (
        r"\lstinputlisting[language=Python]"
        r"{chapitres/1SPE-SUITES/python/1SPE-SUITES-EX-044.py}"
    ) in exercise
    assert "lignes manquantes" not in exercise
    assert "Recopier et compléter" not in exercise
    run = subprocess.run(
        [sys.executable, str(PY044)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=2,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout == "278\n"
    assert all(token in correction for token in (r"C_{277}", "757{,}46", r"C_{278}", "-38{,}75"))
    assert "761{,}25" in correction
    assert "dernière mensualité" in correction
    assert r"1{,}005^{277}" in correction
    assert r"1{,}005^{278}" in correction
    assert r"\log" not in correction
    assert r"\ln" not in correction
    assert set(_meta(CO044)["capacites_codes"]) == {"C3", "C6", "C7"}
    assert set(_meta(CO044)["capacites"]) == {
        "1SPE-SUITES-C3",
        "1SPE-SUITES-C6",
        "1SPE-SUITES-C7",
    }


def test_044_python_ast_and_semantics_prove_the_minimal_repayment_rank() -> None:
    source = _source(PY044)
    assignments = _assert_repayment_script_ast_contract(source)

    capital = Fraction(assignments["C"])
    rate = Fraction(str(assignments["t"]))
    payment = Fraction(assignments["m"])
    rank = int(assignments["n"])
    previous = capital
    while capital > 0:
        previous = capital
        capital = (1 + rate) * capital - payment
        rank += 1
        assert rank < 10_000

    assert rank == 278
    assert previous > 0 >= capital


def test_044_python_contract_rejects_a_hardcoded_output() -> None:
    hardcoded = _source(PY044).replace("print(n)", "print(278)")

    with pytest.raises(AssertionError):
        _assert_repayment_script_ast_contract(hardcoded)


def test_046_is_c8_conjectural_and_uses_exact_threshold_values() -> None:
    exercise = _rendered(EX046)
    correction = _rendered(CO046)
    expected_codes = {"C3", "C4", "C6", "C8"}
    expected_qualified = {f"1SPE-SUITES-{code}" for code in expected_codes}

    for path in (EX046, CO046):
        meta = _meta(path)
        assert set(meta["capacites_codes"]) == expected_codes
        assert set(meta["capacites"]) == expected_qualified
    assert all(token in exercise for token in (r"S_{49}", "conjecturer", "semble se rapprocher"))
    assert all(token in correction for token in (r"S_{49}", r"99\,485", "On conjecture"))
    assert "sixième année" in correction
    assert "onzième année" in correction
    assert "après 5 ans" not in correction
    assert all(token in correction for token in (r"S_{20}", r"89\,058", r"S_{21}", r"90\,152"))
    assert "au terme de la $22^\\text{e}$ année" in correction
    assert all(token in correction for token in (r"D_{15}", r"-1\,470", r"D_{16}", r"1\,677"))
    assert r"D_{n+1}-D_n=5\,000-u_{n+1}" in correction
    assert all(token in correction for token in (r"u_6=5\,314{,}41", r"u_7=4\,782{,}969"))
    assert r"$20$ & $89\,058$" in correction
    assert r"$20$ & $87\,842$" not in correction
    for source in (exercise, correction):
        assert r"\log" not in source
        assert r"\ln" not in source
        assert r"\lim" not in source
        assert "converge" not in source


def test_batch_a_corrections_have_aligned_baremes() -> None:
    for path in (CO026, CO031, CO044, CO046):
        correction = _rendered(path)
        assert r"\baremeIndicatif" in correction
        assert "passage au log" not in correction
        assert "propriétés du $\\ln$" not in correction


@pytest.mark.parametrize("path", TARGET_TEX)
def test_batch_a_technical_oracles_execute(path: Path) -> None:
    exec(compile(_oracle(path), str(path), "exec"), {})


def test_batch_a_oracles_lock_new_boundaries() -> None:
    assert "u.subs(n, 5) == 96" in _oracle(EX026)
    assert "u.subs(n, 6) == 3 * 2**6 == 192" in _oracle(CO026)
    assert "Rational(3, 5)" in _oracle(EX031)
    assert "Rational(3, 5)" in _oracle(CO031)
    assert "C_n(277)" in _oracle(CO044)
    assert "C_n(278)" in _oracle(CO044)
    oracle_046 = _oracle(CO046)
    assert "S_formula(49)" in oracle_046
    assert "S_formula(20)" in oracle_046
    assert "S_formula(21)" in oracle_046
    assert "assert rang == 16" in oracle_046
