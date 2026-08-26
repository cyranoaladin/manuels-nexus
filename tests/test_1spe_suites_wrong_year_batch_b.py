from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques" / "manuel-maths"
CHAPTER = MANUAL / "chapitres" / "1SPE-SUITES"
PYTHON_049 = CHAPTER / "python" / "1SPE-SUITES-EX-049.py"
BOUNDARY_SCRIPT = ROOT / "scripts" / "check_1spe_suites_programme_boundary.py"
VERIFY_SCRIPT = MANUAL / "scripts" / "verify_sympy.py"


def _source(kind: str, number: str) -> Path:
    directory = "exercices" if kind == "EX" else "corriges"
    return CHAPTER / directory / f"1SPE-SUITES-{kind}-{number}.tex"


BATCH_PATHS = tuple(
    _source(kind, number)
    for number in ("027", "037", "040", "043", "048", "049")
    for kind in ("EX", "CO")
)
EXPECTED_CAPACITIES = {
    "027": ("C3", "C4", "C8"),
    "037": ("C1", "C5", "C8"),
    "040": ("C1", "C5", "C8"),
    "043": ("C3", "C5", "C6", "C8"),
    "048": ("C1", "C3", "C5", "C8"),
    "049": ("C3", "C4", "C5", "C6", "C7", "C8"),
}


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _rendered(path: Path) -> str:
    boundary = _load(BOUNDARY_SCRIPT, "batch_b_boundary")
    return boundary.strip_non_rendered_comments(_text(path))


def _meta(path: Path) -> dict:
    first_line = _text(path).splitlines()[0]
    assert first_line.startswith("% META: ")
    return json.loads(first_line.removeprefix("% META: "))


def _evaluate_expression(expression: ast.expr, **values: float) -> float | bool:
    compiled = compile(ast.Expression(expression), str(PYTHON_049), "eval")
    return eval(compiled, {"__builtins__": {}}, values)


def _assert_python_049_semantics(source: str) -> None:
    tree = ast.parse(source, filename=str(PYTHON_049))
    assert len(tree.body) == 3
    initial_values: dict[str, int | float] = {}
    for node in tree.body[:2]:
        assert isinstance(node, ast.Assign)
        assert len(node.targets) == 1
        target = node.targets[0]
        assert isinstance(target, ast.Name) and target.id in {"u", "v"}
        initial_values[target.id] = ast.literal_eval(node.value)
    assert initial_values == {"u": 100, "v": 100}

    loops = [
        node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))
    ]
    assert len(loops) == 1
    loop = tree.body[2]
    assert loops[0] is loop
    assert isinstance(loop, ast.For)
    assert isinstance(loop.target, ast.Name) and loop.target.id == "n"
    assert isinstance(loop.iter, ast.Call)
    assert isinstance(loop.iter.func, ast.Name) and loop.iter.func.id == "range"
    assert [ast.literal_eval(arg) for arg in loop.iter.args] == [1, 21]
    assert loop.orelse == []
    assert len(loop.body) == 3

    updates: dict[str, ast.expr] = {}
    expected_updates = {
        "u": ast.parse("u = 1.05 * u").body[0].value,
        "v": ast.parse("v = v + 0.05 * v * (1 - v / 500)").body[0].value,
    }
    for node, name in zip(loop.body[:2], ("u", "v"), strict=True):
        assert isinstance(node, ast.Assign)
        assert len(node.targets) == 1
        target = node.targets[0]
        assert isinstance(target, ast.Name) and target.id == name
        assert ast.dump(node.value) == ast.dump(expected_updates[name])
        updates[name] = node.value
    for value in (0.0, 100.0, 321.5):
        assert _evaluate_expression(updates["u"], u=value, v=17.0) == pytest.approx(
            1.05 * value
        )
    for value in (0.0, 100.0, 250.0, 499.0, 500.0):
        expected = value + 0.05 * value * (1 - value / 500)
        assert _evaluate_expression(updates["v"], u=17.0, v=value) == pytest.approx(
            expected
        )

    conditional = loop.body[2]
    assert isinstance(conditional, ast.If)
    expected_condition = ast.parse("n in [5, 10, 20]", mode="eval").body
    assert ast.dump(conditional.test) == ast.dump(expected_condition)
    assert conditional.orelse == []
    selected = [
        n
        for n in range(1, 21)
        if _evaluate_expression(conditional.test, n=n, u=0.0, v=0.0)
    ]
    assert selected == [5, 10, 20]

    print_calls = [
        node
        for node in ast.walk(conditional)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "print"
    ]
    all_print_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "print"
    ]
    assert len(print_calls) == 1
    assert all_print_calls == print_calls
    assert len(print_calls[0].args) == 1
    printed_expression = print_calls[0].args[0]
    assert isinstance(printed_expression, ast.JoinedStr)
    expected_print = ast.parse(
        'f"n={n} : u={u:.1f}, v={v:.1f}"', mode="eval"
    ).body
    assert ast.dump(printed_expression) == ast.dump(expected_print)


def test_027_introduces_the_geometric_sequence_without_redundancy_or_circularity() -> None:
    exercise = _rendered(_source("EX", "027"))
    correction = _rendered(_source("CO", "027"))
    exercise_q1 = exercise.split(r"\begin{enumerate}", 1)[1].split(r"\item Exprimer", 1)[0]
    correction_q1 = correction.split("Question 1", 1)[1].split("Question 2", 1)[0]
    correction_q2 = correction.split("Question 2", 1)[1].split("Question 3", 1)[0]

    assert r"u_{n+1}=\dfrac{1}{2}u_n" in exercise
    assert "suite géométrique de premier terme" not in exercise.split(
        r"\begin{enumerate}", 1
    )[0]
    assert "Reconnaître directement" in exercise_q1
    assert r"\dfrac{u_{n+1}}{u_n}" not in exercise_q1
    assert "par définition" in correction_q1
    assert r"\frac{u_{n+1}}{u_n}" not in correction_q1
    assert r"256 \times \left(\dfrac{1}{2}\right)^n" not in correction_q1
    assert r"u_n = u_0 \times q^n" in correction_q2


@pytest.mark.parametrize("path", BATCH_PATHS, ids=lambda path: path.stem)
def test_batch_b_pairs_have_exact_qualified_capacities(path: Path) -> None:
    meta = _meta(path)
    number = path.stem[-3:]
    codes = EXPECTED_CAPACITIES[number]

    assert tuple(meta["capacites_codes"]) == codes
    assert tuple(meta["capacites"]) == tuple(
        f"1SPE-SUITES-{code}" for code in codes
    )


def test_ex043_uses_the_statement_initial_value_as_its_only_meta_oracle_value() -> None:
    exercise = _text(_source("EX", "043"))
    meta = _meta(_source("EX", "043"))

    assert meta["parametres_sympy"]["u0"] == 600
    assert "% u0 = 600" in exercise
    assert "u0b" not in exercise
    assert "% u0 = 1000" not in exercise


@pytest.mark.parametrize("path", BATCH_PATHS, ids=lambda path: path.stem)
def test_batch_b_has_no_rendered_terminal_limit_or_log_method(path: Path) -> None:
    rendered = _rendered(path)
    forbidden = (
        r"\ln",
        r"\log",
        r"\lim",
        r"\to",
        r"\longrightarrow",
        "passage à la limite",
        "théorème de convergence",
        "donc elle converge",
        "admettre qu'elle converge",
    )

    assert all(token not in rendered for token in forbidden), rendered


def test_027_replaces_formal_limit_with_numeric_conjecture_and_aligned_rubric() -> None:
    correction = _rendered(_source("CO", "027"))

    assert all(token in correction for token in (r"S_7", r"S_9", r"S_{15}"))
    assert all(token in correction for token in ("510", "511{,}5", "511{,}992"))
    assert "On conjecture" in correction
    assert "semblent se rapprocher de $512$" in correction
    assert "calculs numériques et conjecture" in correction
    assert "comportement asymptotique" not in correction


def test_037_keeps_only_point_fixed_observation_and_conjecture() -> None:
    correction = _rendered(_source("CO", "037"))

    assert "unique point fixe" in correction
    assert "si un terme vaut $6$, le suivant vaut encore $6$" in correction
    assert "sans la démontrer" in correction
    assert "la suite descend vers $6$" not in correction
    assert "ce n'est pas une suite standard" not in correction


def test_040_distinguishes_proved_bounds_from_the_numeric_conjecture() -> None:
    exercise = _rendered(_source("EX", "040"))
    correction = _rendered(_source("CO", "040"))

    assert r"\sqrt{3} \leq u_{n+1} \leq u_n" in exercise
    assert "sans constituer une preuve de limite" in exercise
    assert "intersection positive" in correction
    assert "semblent se rapprocher" in correction
    assert "sans la prouver" in correction
    assert "sans établir formellement une limite" in correction
    assert "se rapprochent les uns des autres" not in correction


def test_043_values_are_independent_exact_and_support_only_a_conjecture() -> None:
    exercise = _rendered(_source("EX", "043"))
    correction = _rendered(_source("CO", "043"))
    values = {
        n: Fraction(1000) - Fraction(400) * Fraction(4, 5) ** n
        for n in (5, 10, 20)
    }

    assert values == {
        5: Fraction(108616, 125),
        10: Fraction(373847784, 390625),
        20: Fraction(3797105079580584, 3814697265625),
    }
    assert all(token in exercise for token in (r"u_5", r"u_{10}", r"u_{20}"))
    assert all(token in correction for token in ("868{,}9", "957{,}1", "995{,}4"))
    assert "On conjecture" in correction
    assert "semblent s'en rapprocher" in correction


def test_048_uses_definition_numeric_boundary_and_finite_ratio_exploration() -> None:
    exercise = _rendered(_source("EX", "048"))
    correction = _rendered(_source("CO", "048"))
    question_2 = correction.split("2. Nature", 1)[1].split("3. Variations", 1)[0]

    assert r"u_{n+1} = \frac{1}{3}u_n" in question_2
    assert "par définition" in question_2
    assert r"\frac{u_{n+1}}{u_n}" not in question_2
    assert all(token in exercise for token in (r"u_4", r"u_6", r"u_8"))
    assert all(token in correction for token in (r"\frac{2}{729}", r"\frac{2}{2187}"))
    assert "Le plus petit entier" in correction and "$n = 7$" in correction
    assert all(token in exercise for token in (r"\frac{1}{2}", r"-\frac{1}{2}", "$1$", "$-1$", "$2$"))
    assert "On conjecture" in correction
    assert "On conjecture qu'ils semblent" not in correction
    assert "Ces valeurs suggèrent un rapprochement vers $0$" in correction
    assert (
        "On conjecture, à partir de ces cinq expériences finies, que les deux "
        "premières suites se rapprochent de $0$"
    ) in correction
    assert "que les deux premières suites semblent se rapprocher" not in correction


def test_048_independent_values_and_threshold_are_exact() -> None:
    values = {n: Fraction(2) * Fraction(1, 3) ** n for n in (4, 6, 7, 8)}

    assert values == {
        4: Fraction(2, 81),
        6: Fraction(2, 729),
        7: Fraction(2, 2187),
        8: Fraction(2, 6561),
    }
    assert values[6] > Fraction(1, 1000)
    assert values[7] < Fraction(1, 1000)


def test_049_uses_one_executable_python_source_and_exact_stdout() -> None:
    exercise = _text(_source("EX", "049"))
    listing_path = "chapitres/1SPE-SUITES/python/1SPE-SUITES-EX-049.py"

    assert PYTHON_049.is_file()
    assert rf"\lstinputlisting[language=Python]{{{listing_path}}}" in exercise
    assert r"\begin{lstlisting}" not in exercise
    completed = subprocess.run(
        [sys.executable, str(PYTHON_049)],
        cwd=MANUAL,
        text=True,
        capture_output=True,
        check=False,
        timeout=2,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert completed.stdout == (
        "n=5 : u=127.6, v=121.2\n"
        "n=10 : u=162.9, v=145.3\n"
        "n=20 : u=265.3, v=201.1\n"
    )


def test_049_python_source_encodes_the_models_loop_ranks_and_dynamic_print() -> None:
    _assert_python_049_semantics(_text(PYTHON_049))


@pytest.mark.parametrize(
    "old,new",
    (
        (
            'print(f"n={n} : u={u:.1f}, v={v:.1f}")',
            'print("n=5 : u=127.6, v=121.2")',
        ),
        ("u = 1.05 * u", "u = 127.6"),
        ("v = v + 0.05 * v * (1 - v / 500)", "v = 121.2"),
        ("for n in range(1, 21):", "for n in [5, 10, 20]:"),
        ("if n in [5, 10, 20]:", "if n in [4, 10, 20]:"),
        ("u = 1.05 * u", "u = 1.05 * u + 0 * u"),
        (
            "v = v + 0.05 * v * (1 - v / 500)",
            "v = v + 0.05 * v * (1 - v / 500) + 0 * v",
        ),
        (
            'print(f"n={n} : u={u:.1f}, v={v:.1f}")',
            'print(f"n={n} : u={u + 0:.1f}, v={v:.1f}")',
        ),
        (
            "u = 100\nv = 100",
            "u = 100\nv = 100\nu_table = [127.6, 162.9, 265.3]\n"
            "v_table = [121.2, 145.3, 201.1]",
        ),
        (
            "for n in range(1, 21):",
            "while False:\n    pass\n\nfor n in range(1, 21):",
        ),
    ),
    ids=(
        "hardcoded-print",
        "hardcoded-u",
        "hardcoded-v",
        "wrong-loop",
        "wrong-ranks",
        "neutral-u-term",
        "neutral-v-term",
        "indirect-formatted-u",
        "constant-tables",
        "extra-loop",
    ),
)
def test_049_python_semantic_mutations_are_rejected(old: str, new: str) -> None:
    source = _text(PYTHON_049)
    mutant = source.replace(old, new)

    assert mutant != source
    with pytest.raises(AssertionError):
        _assert_python_049_semantics(mutant)


def test_049_statement_correction_threshold_output_and_conjectures_align() -> None:
    exercise = _rendered(_source("EX", "049"))
    correction = _rendered(_source("CO", "049"))

    assert "somme des effectifs modélisés" in exercise
    assert "production cumulée" not in exercise
    assert all(token in correction for token in (r"u_{32}", r"u_{33}"))
    assert all(token in correction for token in ("476{,}5", "500{,}3"))
    assert all(token in correction for token in ("121{,}2", "145{,}3", "201{,}1"))
    assert "On conjecture" in correction
    assert "semblent se rapprocher de $500$" in correction
    assert "les incréments deviennent plus petits" not in correction
    assert r"5{,}2 \times 0{,}792 = 4{,}1184" in correction
    assert r"5{,}2 \times 0{,}792 = 4{,}118 \approx" not in correction


def test_049_independent_threshold_and_script_values_are_exact() -> None:
    ratio = Fraction(21, 20)

    def u(n: int) -> Fraction:
        return Fraction(100) * ratio**n

    v = Fraction(100)
    outputs: dict[int, tuple[float, float]] = {}
    for n in range(1, 21):
        v += Fraction(1, 20) * v * (1 - v / 500)
        if n in (5, 10, 20):
            outputs[n] = (float(u(n)), float(v))

    assert u(32) < 500 < u(33)
    assert {
        n: (f"{u_value:.1f}", f"{v_value:.1f}")
        for n, (u_value, v_value) in outputs.items()
    } == {
        5: ("127.6", "121.2"),
        10: ("162.9", "145.3"),
        20: ("265.3", "201.1"),
    }


def test_049_logistic_increments_grow_through_the_published_ranks() -> None:
    v = 100.0
    terms = {0: v}
    for n in range(1, 21):
        v += 0.05 * v * (1 - v / 500)
        terms[n] = v

    increments = {
        n: 0.05 * terms[n] * (1 - terms[n] / 500)
        for n in (5, 10, 20)
    }
    assert increments[5] < increments[10] < increments[20]


@pytest.mark.parametrize("path", BATCH_PATHS, ids=lambda path: path.stem)
def test_batch_b_technical_oracles_still_pass(
    path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.syspath_prepend(str(VERIFY_SCRIPT.parent))
    verifier = _load(VERIFY_SCRIPT, "batch_b_verify_sympy")
    script = verifier.extract_script(_text(path))

    assert script is not None
    verdict, detail = verifier.run_sandbox(script)
    assert verdict == "pass", detail
