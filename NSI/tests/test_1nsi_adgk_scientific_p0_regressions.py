"""Regressions des P0 scientifiques du chapitre ADGK 1NSI."""

import contextlib
import io
import re
import runpy
import subprocess
import sys
from pathlib import Path

import pytest


NSI_ROOT = Path(__file__).resolve().parents[1]
CHAPTER = NSI_ROOT / "chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN"
GREEDY_COURSE = CHAPTER / "cours/1NSI-ADGK-COURS-C2.tex"
GREEDY_SOURCE = CHAPTER / "code/rendu_glouton.py"
KNN_COURSE = CHAPTER / "cours/1NSI-ADGK-COURS-C3.tex"
KNN_SOURCE = CHAPTER / "code/k_plus_proches_voisins.py"


def _assert_canonical_listing(course: Path, source: Path, title: str) -> str:
    source_code = source.read_text(encoding="utf-8")
    course_text = course.read_text(encoding="utf-8")
    marker_text = f"% PYTHON-SOURCE: code/{source.name}"
    marker = re.escape(marker_text)
    hidden_regions = re.findall(r"\\iffalse.*?\\fi", course_text, re.DOTALL)
    forbidden_routing = re.compile(
        r"\\(?:newif|newcommand|renewcommand|providecommand|let|"
        r"if[A-Za-z@]*|else|fi)\b"
    )
    alternate_code_environment = re.compile(
        r"\\begin\{(?:lstlisting|minted|verbatim|Verbatim)\}"
    )
    reference = re.compile(
        rf"(?m)^\\begin\{{codereference\}}\{{{re.escape(title)}\}}"
        rf"(?P<body>.*?)^\\end\{{codereference\}}",
        re.DOTALL | re.MULTILINE,
    )
    references = list(reference.finditer(course_text))

    assert course_text.count(r"\begin{python}") == 1, (
        "un seul listing Python visible est autorise"
    )
    assert not any(marker_text in region for region in hidden_regions), (
        "le listing Python visible ne doit pas etre masque"
    )
    assert forbidden_routing.search(course_text) is None, (
        "le listing Python visible ne doit pas etre route par une macro"
    )
    assert alternate_code_environment.search(course_text) is None, (
        "le listing Python visible doit etre l'unique environnement de code"
    )
    assert len(references) == 1, "le listing Python visible doit etre dans sa reference"
    body = references[0].group("body")
    assert marker_text in body, "le listing Python visible doit suivre son marqueur"
    pattern = re.compile(
        rf"(?m)^{marker}\n\\begin\{{python\}}(?P<python>.*?)\\end\{{python\}}",
        re.DOTALL,
    )
    matches = list(pattern.finditer(body))

    assert len(matches) == 1, "le listing Python canonique doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"
    assert source_code.isascii()
    return source_code


def _load_source(source: Path, expected_stdout: str) -> dict[str, object]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(source))
    assert stdout.getvalue() == expected_stdout
    return namespace


def test_canonical_listing_rejects_a_hidden_decoy(tmp_path: Path) -> None:
    source = tmp_path / "example.py"
    source.write_text('print("canonical")\n', encoding="utf-8")
    course = tmp_path / "course.tex"
    course.write_text(
        r'''\begin{python}
print("visible decoy")
\end{python}

\iffalse
% PYTHON-SOURCE: code/example.py
\begin{python}
print("canonical")
\end{python}
\fi
''',
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="listing Python visible"):
        _assert_canonical_listing(course, source, "Expected reference")


@pytest.mark.parametrize(
    "routing",
    [
        (
            r"""\newif\ifshowcanonical
\showcanonicalfalse
\ifshowcanonical
{reference}
\fi
"""
        ),
        (
            r"""\newcommand{{\unusedcanonical}}{{%
{reference}
}}
"""
        ),
    ],
)
def test_canonical_listing_rejects_custom_hidden_routing(
    tmp_path: Path, routing: str
) -> None:
    source = tmp_path / "example.py"
    source.write_text('print("canonical")\n', encoding="utf-8")
    reference = r"""\begin{codereference}{Expected reference}
% PYTHON-SOURCE: code/example.py
\begin{python}
print("canonical")
\end{python}
\end{codereference}"""
    course = tmp_path / "course.tex"
    course.write_text(
        routing.format(reference=reference)
        + r"""\begin{lstlisting}
print("visible decoy")
\end{lstlisting}
""",
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="listing Python visible"):
        _assert_canonical_listing(course, source, "Expected reference")


def test_greedy_change_rejects_nonpositive_coins_without_looping() -> None:
    _assert_canonical_listing(GREEDY_COURSE, GREEDY_SOURCE, "Rendu de monnaie glouton")
    script = """
import runpy
import sys

rendu_glouton = runpy.run_path(sys.argv[1])["rendu_glouton"]
try:
    rendu_glouton(3, [2, 0, 1])
except ValueError as error:
    if str(error) != "les pieces doivent etre strictement positives":
        raise RuntimeError(f"message inattendu: {error}")
else:
    raise AssertionError("une piece nulle doit etre refusee")
"""

    completed = subprocess.run(
        [sys.executable, "-I", "-O", "-c", script, str(GREEDY_SOURCE)],
        check=False,
        capture_output=True,
        text=True,
        timeout=2,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_greedy_change_rejects_a_partial_result() -> None:
    _assert_canonical_listing(GREEDY_COURSE, GREEDY_SOURCE, "Rendu de monnaie glouton")
    namespace = _load_source(GREEDY_SOURCE, "[50, 20, 5, 2, 1]\n")

    with pytest.raises(
        ValueError,
        match="l'algorithme glouton n'a pas trouve de rendu exact",
    ):
        namespace["rendu_glouton"](3, [2])


def test_greedy_failure_does_not_claim_mathematical_impossibility() -> None:
    _assert_canonical_listing(GREEDY_COURSE, GREEDY_SOURCE, "Rendu de monnaie glouton")
    namespace = _load_source(GREEDY_SOURCE, "[50, 20, 5, 2, 1]\n")

    with pytest.raises(
        ValueError,
        match="l'algorithme glouton n'a pas trouve de rendu exact",
    ):
        namespace["rendu_glouton"](6, [4, 3])
    assert sum([3, 3]) == 6

    course = GREEDY_COURSE.read_text(encoding="utf-8")
    normalized_course = " ".join(course.split())
    assert "la stratégie gloutonne ne trouve pas de rendu exact" in normalized_course
    assert "le montant n'est pas représentable" not in normalized_course


@pytest.mark.parametrize("k", [0, -1, 3, 1.0, True])
def test_knn_rejects_k_outside_the_dataset_or_non_integer(k: object) -> None:
    _assert_canonical_listing(
        KNN_COURSE,
        KNN_SOURCE,
        "Algorithme des k plus proches voisins",
    )
    _load_source(KNN_SOURCE, "A\nB\n")
    script = f"""
import runpy
import sys

k_plus_proches_voisins = runpy.run_path(sys.argv[1])["k_plus_proches_voisins"]
points = [(1, 1, "A"), (8, 8, "B")]
try:
    k_plus_proches_voisins(points, (1.5, 1.5), {k!r})
except ValueError as error:
    if str(error) != "k doit etre un entier compris entre 1 et le nombre de points":
        raise RuntimeError(f"message inattendu: {{error}}")
else:
    raise AssertionError("k hors domaine doit etre refuse")
"""

    completed = subprocess.run(
        [sys.executable, "-I", "-O", "-c", script, str(KNN_SOURCE)],
        check=False,
        capture_output=True,
        text=True,
        timeout=2,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_knn_accepts_integer_boundaries_and_rejects_an_empty_dataset() -> None:
    _assert_canonical_listing(
        KNN_COURSE,
        KNN_SOURCE,
        "Algorithme des k plus proches voisins",
    )
    namespace = _load_source(KNN_SOURCE, "A\nB\n")
    classifier = namespace["k_plus_proches_voisins"]
    points = [(1, 1, "A"), (2, 1, "A"), (8, 8, "B")]

    assert classifier(points, (1.5, 1.2), 1) == "A"
    assert classifier(points, (1.5, 1.2), len(points)) == "A"
    with pytest.raises(
        ValueError,
        match="k doit etre un entier compris entre 1 et le nombre de points",
    ):
        classifier([], (1.5, 1.2), 1)
