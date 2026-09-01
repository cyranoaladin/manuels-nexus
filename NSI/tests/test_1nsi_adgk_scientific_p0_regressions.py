"""Regressions des P0 scientifiques du chapitre ADGK 1NSI."""

import contextlib
import io
import json
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


def test_knn_tie_is_deterministic_across_hash_seeds() -> None:
    """Une egalite ne doit pas dependre du PYTHONHASHSEED de l'eleve.

    `max(set(classes), key=classes.count)` itere un ensemble de chaines :
    a egalite parfaite, la classe renvoyee change d'une execution a l'autre.
    Un manuel imprime un resultat que l'eleve doit reproduire.
    """
    _assert_canonical_listing(
        KNN_COURSE,
        KNN_SOURCE,
        "Algorithme des k plus proches voisins",
    )
    script = """
import runpy
import sys

k_plus_proches_voisins = runpy.run_path(sys.argv[1])["k_plus_proches_voisins"]
# Egalite parfaite : un voisin de chaque classe, le plus proche etant "Chat".
points = [(0, 0, "Chat"), (10, 0, "Chien")]
print(k_plus_proches_voisins(points, (1, 0), 2))
"""
    verdicts = set()
    for seed in range(12):
        completed = subprocess.run(
            [sys.executable, "-I", "-c", script, str(KNN_SOURCE)],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
            env={"PYTHONHASHSEED": str(seed), "PATH": "/usr/bin:/bin"},
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        # `run_path` execute aussi les `print` de demonstration du module :
        # la prediction cherchee est la derniere ligne emise.
        verdicts.add(completed.stdout.strip().splitlines()[-1])

    assert verdicts == {"Chat"}, (
        "l'egalite doit etre tranchee par le voisin le plus proche, "
        f"or les graines de hachage donnent {sorted(verdicts)}"
    )


def test_knn_tie_rule_is_documented_where_it_is_taught() -> None:
    """La regle qui tranche l'egalite doit etre ecrite, pas seulement codee."""
    course = " ".join(KNN_COURSE.read_text(encoding="utf-8").split())
    method = " ".join(
        (NSI_ROOT / "chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN"
         / "methodes/1NSI-ADGK-ME-003.tex").read_text(encoding="utf-8").split()
    )

    for source in (course, method):
        assert "voisin le plus proche" in source
    assert "rend la prédiction arbitraire" not in method


def test_no_object_still_calls_a_tie_implementation_dependent() -> None:
    """La regle de bris d'egalite est definie : plus rien ne peut la dire indefinie."""
    chapter = CHAPTER
    offenders = []
    for path in sorted(chapter.rglob("*.tex")):
        text = " ".join(path.read_text(encoding="utf-8").split())
        if "détails d'implémentation non garantis" in text:
            offenders.append(str(path.relative_to(chapter)))
    assert offenders == []


def test_k_equal_to_n_claim_admits_the_tie_case() -> None:
    """Avec k = n et une egalite, il n'y a PAS de majorite globale.

    Sur la base de fruits (3 pommes, 3 bananes), k = 6 ne renvoie pas « la
    classe majoritaire globale » : il n'en existe aucune, et c'est le voisin le
    plus proche qui trancher -- donc une reponse qui DEPEND du point classe.
    """
    method = " ".join(
        (CHAPTER / "methodes/1NSI-ADGK-ME-003.tex").read_text(
            encoding="utf-8"
        ).split()
    )
    assert "on renvoie toujours la classe majoritaire globale" not in method

    qcm = json.loads(
        (CHAPTER / "qcm/1NSI-ALGO-DICHO-GLOUTON-KNN-QCM.json").read_text(
            encoding="utf-8"
        )
    )
    question = next(item for item in qcm["questions"] if item["id"] == "Q6")
    assert (
        "identique pour n'importe quel élément"
        not in question["diagnostics"]["C"]["erreur"]
    )


def test_dichotomy_method_sheet_traces_the_real_variant_values() -> None:
    """Le variant descend 7 -> 3 -> 0 ; la fiche imprimait 7 -> 3 -> 1."""
    method = " ".join(
        (CHAPTER / "methodes/1NSI-ADGK-ME-001.tex").read_text(
            encoding="utf-8"
        ).split()
    )
    assert "$7 \\to 3 \\to 0$" in method
    assert "$7 \\to 3 \\to 1$" not in method


def test_dichotomy_absence_sentinel_is_minus_one_across_the_chapter() -> None:
    """La fiche methode M1 renvoyait None la ou tout le chapitre renvoie -1."""
    offenders = []
    for path in sorted(CHAPTER.rglob("*.tex")):
        lines = path.read_text(encoding="utf-8").split("\n")
        for index, line in enumerate(lines):
            if "def recherche_dichotomique(" not in line:
                continue
            for follower in lines[index + 1:]:
                bare = follower[2:] if follower.startswith("% ") else follower
                if bare.strip() and not bare.startswith("    "):
                    break
                if bare.startswith("    return ") and not bare.startswith("        "):
                    if bare.strip() not in ("return -1", "return -1, etapes",
                                            "return -1, variants"):
                        offenders.append((str(path.relative_to(CHAPTER)), bare.strip()))
                    break
    assert offenders == []


def test_greedy_method_sheet_refuses_a_silent_partial_change() -> None:
    """M2 demande a l'eleve de tester un montant inatteignable.

    Sans garde d'exactitude, la reponse a cet exercice est un resultat
    faux rendu en silence -- exactement ce que le cours interdit.
    """
    method = (CHAPTER / "methodes/1NSI-ADGK-ME-002.tex").read_text(encoding="utf-8")
    listing = method.split("\\begin{python}", maxsplit=1)[1].split(
        "\\end{python}", maxsplit=1
    )[0]

    assert "if montant != 0:" in listing
    assert "raise ValueError" in listing
    assert "sorted(pieces, reverse=True)" in listing


def test_every_dichotomy_chapter_exercise_declares_its_reasoning_gestures() -> None:
    """Les deux chapitres du lot couple doivent se mesurer avec la meme regle.

    PARCOURS-TRIS declarait huit gestes distincts sur ses six exercices ;
    DICHO-GLOUTON-KNN n'en declarait aucun, ce qui rendait sa richesse
    `INSUFFICIENT` non pas parce que le chapitre est pauvre, mais parce qu'il
    ne disait rien. Un geste se declare, il ne se devine pas.
    """
    attendus = {
        "1NSI-ADGK-EX-001": ["prouver_terminaison", "tracer_execution"],
        "1NSI-ADGK-EX-002": ["diagnostiquer_bug", "tracer_execution"],
        "1NSI-ADGK-EX-003": ["distinguer_notions", "tracer_execution"],
        "1NSI-ADGK-EX-004": ["traiter_cas_limite", "tracer_execution"],
        "1NSI-ADGK-EX-005": ["construire_contre_exemple", "tracer_execution"],
    }
    observes = {}
    for path in sorted((CHAPTER / "exercices").glob("*.tex")):
        meta = json.loads(
            path.read_text(encoding="utf-8").split("META:", 1)[1].split("\n", 1)[0]
        )
        observes[meta["id"]] = sorted(meta.get("gestes") or [])

    assert observes == {k: sorted(v) for k, v in attendus.items()}

    # Chaque capacite du chapitre recoit au moins deux gestes distincts.
    par_capacite: dict[str, set[str]] = {}
    for path in sorted((CHAPTER / "exercices").glob("*.tex")):
        meta = json.loads(
            path.read_text(encoding="utf-8").split("META:", 1)[1].split("\n", 1)[0]
        )
        for ref in meta["capacites"]:
            par_capacite.setdefault(ref, set()).update(meta.get("gestes") or [])
    assert set(par_capacite) == {"P-ALGO-03", "P-ALGO-04", "P-ALGO-05"}
    assert all(len(gestes) >= 2 for gestes in par_capacite.values()), par_capacite
