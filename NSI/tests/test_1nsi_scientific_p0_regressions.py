"""Regressions scientifiques P0 pour les cours 1NSI."""
import contextlib
import hashlib
import importlib.util
import io
import re
import runpy
import subprocess
from pathlib import Path

import pytest


NSI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = NSI_ROOT.parent
COURSE = NSI_ROOT / "chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex"
PYTHON_SOURCE = NSI_ROOT / "chapitres/1NSI-LANGAGE/code/maximum_bugue.py"
MINIMUM_CORRECTION = (
    NSI_ROOT / "chapitres/1NSI-LANGAGE/corriges/1NSI-LANGAGE-RE-C4-CORRIGE.tex"
)
MINIMUM_REMEDIATION = (
    NSI_ROOT / "chapitres/1NSI-LANGAGE/remediation/1NSI-LANGAGE-RE-C4.tex"
)
MINIMUM_SOURCE = NSI_ROOT / "chapitres/1NSI-LANGAGE/code/minimum.py"
AVANCEMENT_COURSE = (
    NSI_ROOT
    / "chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C2.tex"
)
AVANCEMENT_SOURCE = (
    NSI_ROOT / "chapitres/1NSI-PROJET-METHODES/code/avancement.py"
)
WEIGHTED_MEAN_COURSE = (
    NSI_ROOT
    / "chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C3.tex"
)
WEIGHTED_MEAN_SOURCE = (
    NSI_ROOT
    / "chapitres/1NSI-PROJET-METHODES/code/moyenne_ponderee.py"
)
REVIEW_SCRIPT = REPO_ROOT / "scripts/review_1nsi_content.py"

_REVIEW_SPEC = importlib.util.spec_from_file_location(
    "review_1nsi_content", REVIEW_SCRIPT
)
assert _REVIEW_SPEC is not None and _REVIEW_SPEC.loader is not None
review_module = importlib.util.module_from_spec(_REVIEW_SPEC)
_REVIEW_SPEC.loader.exec_module(review_module)


MARKED_MAXIMUM_SEQUENCE = re.compile(
    r"(?m)^% PYTHON-SOURCE: code/maximum_bugue\.py\n"
    r"\\begin\{python\}(?P<python>.*?)\\end\{python\}\n\n"
    r"\\begin\{console\}(?P<console>.*?)\\end\{console\}\n\n"
    r"% BEGIN-TRACE\n(?P<trace>.*?)% EXPECTED\n(?P<expected>.*?)% END-TRACE",
    re.DOTALL,
)


def _uncomment(block: str) -> str:
    return "\n".join(re.sub(r"^%\s?", "", line) for line in block.splitlines())


def _marked_maximum_sequence(tex: str) -> re.Match[str]:
    matches = list(MARKED_MAXIMUM_SEQUENCE.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    return matches[0]


def test_marked_maximum_sequence_ignores_a_valid_decoy_before_the_marker() -> None:
    tex = r'''\begin{python}
print("decoy")
\end{python}

\begin{console}
decoy
\end{console}

% BEGIN-TRACE
% print("decoy")
% EXPECTED
% decoy
% END-TRACE

% PYTHON-SOURCE: code/maximum_bugue.py
\begin{python}
print("marked divergence")
\end{python}

\begin{console}
marked divergence
\end{console}

% BEGIN-TRACE
% print("marked divergence")
% EXPECTED
% marked divergence
% END-TRACE
'''

    sequence = _marked_maximum_sequence(tex)

    assert sequence.group("python") == '\nprint("marked divergence")\n'
    assert sequence.group("console") == "\nmarked divergence\n"
    assert _uncomment(sequence.group("trace")) == 'print("marked divergence")'
    assert _uncomment(sequence.group("expected")) == "marked divergence"


def test_maximum_zero_condition_includes_zero_for_nonempty_lists() -> None:
    assert COURSE.is_file()
    assert PYTHON_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(PYTHON_SOURCE))
    assert stdout.getvalue() == "7\n"

    maximum_bugue = namespace["maximum_bugue"]
    assert maximum_bugue([3, 7, 2]) == 7
    assert maximum_bugue([-5, 0, -8]) == 0
    assert maximum_bugue([-5, -1, -8]) == 0

    source_code = PYTHON_SOURCE.read_text(encoding="utf-8")
    tex = COURSE.read_text(encoding="utf-8")
    sequence = _marked_maximum_sequence(tex)
    assert sequence.group("python") == f"\n{source_code}"
    assert sequence.group("console") == f"\n{stdout.getvalue()}"
    assert _uncomment(sequence.group("trace")) == source_code.rstrip("\n")
    assert _uncomment(sequence.group("expected")) == stdout.getvalue().rstrip("\n")

    course_record = {
        "id": "1NSI-LANG-COURS-C4",
        "path": "NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex",
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-LANGAGE",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": "NSI/chapitres/1NSI-LANGAGE/code/maximum_bugue.py",
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    frequent_error = re.search(r"\\erreurFrequente\{(.*?)\}\n", tex, re.DOTALL)
    assert frequent_error is not None
    error_text = " ".join(frequent_error.group(1).split())
    assert "liste est non vide" in error_text
    assert "valeur positive ou nulle" in error_text
    assert r"\max(\texttt{liste}) \geq 0" in error_text
    assert "[-5, 0, -8]" in error_text
    assert "[-5, -1, -8]" in error_text
    assert "contient au moins une valeur positive" not in error_text


def test_minimum_canonical_source_rejects_empty_list_and_matches_correction() -> None:
    assert MINIMUM_CORRECTION.is_file()
    assert MINIMUM_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(MINIMUM_SOURCE))
    assert stdout.getvalue() == ""

    minimum = namespace["minimum"]
    assert minimum([5, 3, 8]) == 3
    assert minimum([42]) == 42
    assert minimum([-5, -1, -8]) == -8
    with pytest.raises(AssertionError) as error:
        minimum([])
    assert str(error.value) == "liste doit etre non vide"

    source_code = MINIMUM_SOURCE.read_text(encoding="utf-8")
    tex = MINIMUM_CORRECTION.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/minimum\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"

    correction_record = {
        "id": "1NSI-LANGAGE-RE-C4-CORRIGE",
        "path": "NSI/chapitres/1NSI-LANGAGE/corriges/1NSI-LANGAGE-RE-C4-CORRIGE.tex",
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-LANGAGE",
    }
    manifest = review_module.dependency_manifest(
        correction_record, [correction_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": "NSI/chapitres/1NSI-LANGAGE/code/minimum.py",
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    assert '"type_objet": "corrige"' in tex.splitlines()[0]
    assert r"\textbf{Précondition : la liste est non vide.}" in tex
    assert "déclenchant" in tex
    assert "AssertionError" in tex
    assert re.search(
        r"% BEGIN-VERIFY\n"
        r"% def minimum\(liste\):.*?"
        r"% assert minimum\(\[5, 3, 8\]\) == 3.*?"
        r"% try:.*?"
        r"%     minimum\(\[\]\).*?"
        r"% except AssertionError as erreur:.*?"
        r'%     assert str\(erreur\) == "liste doit etre non vide".*?'
        r"% else:.*?"
        r"%     raise AssertionError.*?"
        r"% END-VERIFY",
        tex,
        re.DOTALL,
    )

    verification = subprocess.run(
        ["python", "scripts/verify_python.py", "--chap", "1NSI-LANGAGE", "--check"],
        cwd=NSI_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert verification.returncode == 0, verification.stdout + verification.stderr


def test_minimum_remediation_states_nonempty_precondition_and_matches_answer() -> None:
    assert MINIMUM_REMEDIATION.is_file()
    assert MINIMUM_SOURCE.is_file()

    source_code = MINIMUM_SOURCE.read_text(encoding="utf-8")
    tex = MINIMUM_REMEDIATION.read_text(encoding="utf-8")
    exercise = re.search(
        r"\\begin\{exercice\}.*?\\end\{exercice\}", tex, re.DOTALL
    )
    assert exercise is not None
    visible_text = exercise.group(0)
    normalized_visible = " ".join(visible_text.split())
    assert "liste non vide" in normalized_visible
    assert visible_text.index("liste non vide") < visible_text.index(r"\begin{python}")
    assert r"Le cas \lstinline{[]} est hors précondition." in visible_text
    assert "justifier" in visible_text.lower()
    assert "def minimum(liste):" not in visible_text
    assert 'assert len(liste) > 0, "liste doit etre non vide"' not in visible_text
    assert "AssertionError" not in visible_text

    marker = "% PYTHON-SOURCE: code/minimum.py"
    assert tex.count(marker) == 1
    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 1
    verify_match = verify_matches[0]
    verify_code = _uncomment(verify_match.group("verify"))
    canonical_code = source_code.rstrip("\n")
    assert verify_code.count(canonical_code) == 1
    outside_verify = tex[: verify_match.start()] + tex[verify_match.end() :]
    assert canonical_code not in outside_verify
    assert re.search(
        r"try:\n"
        r"    minimum\(\[\]\)\n"
        r"except AssertionError as erreur:\n"
        r'    assert str\(erreur\) == "liste doit etre non vide"\n'
        r"else:\n"
        r"    raise AssertionError",
        verify_code,
    )

    remediation_record = {
        "id": "1NSI-LANGAGE-RE-C4",
        "path": "NSI/chapitres/1NSI-LANGAGE/remediation/1NSI-LANGAGE-RE-C4.tex",
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-LANGAGE",
    }
    manifest = review_module.dependency_manifest(
        remediation_record, [remediation_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": "NSI/chapitres/1NSI-LANGAGE/code/minimum.py",
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]


def test_avancement_canonical_source_rejects_empty_milestones() -> None:
    assert AVANCEMENT_COURSE.is_file()
    assert AVANCEMENT_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(AVANCEMENT_SOURCE))
    assert stdout.getvalue() == "40.0\nFonctionnalites completes\n"

    avancement = namespace["avancement"]
    prochain_jalon = namespace["prochain_jalon"]
    assert avancement.__doc__ is not None
    assert "Precondition : la liste contient au moins un jalon." in avancement.__doc__
    assert avancement(namespace["jalons"]) == 40.0
    assert avancement([{"nom": "Debut", "termine": False}]) == 0.0
    assert avancement([{"nom": "Fin", "termine": True}]) == 100.0
    with pytest.raises(AssertionError) as error:
        avancement([])
    assert str(error.value) == "au moins un jalon est requis"
    assert prochain_jalon(namespace["jalons"]) == "Fonctionnalites completes"
    assert [jalon["nom"] for jalon in namespace["jalons"]] == [
        "Cahier des charges",
        "Prototype minimal",
        "Fonctionnalites completes",
        "Tests et correction de bugs",
        "Presentation finale",
    ]

    source_code = AVANCEMENT_SOURCE.read_text(encoding="utf-8")
    assert source_code.isascii()
    tex = AVANCEMENT_COURSE.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/avancement\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}\n\n"
        r"\\begin\{console\}(?P<console>.*?)\\end\{console\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"
    assert matches[0].group("console") == f"\n{stdout.getvalue()}"

    course_record = {
        "id": "1NSI-PM-COURS-C2",
        "path": (
            "NSI/chapitres/1NSI-PROJET-METHODES/cours/"
            "1NSI-PM-COURS-C2.tex"
        ),
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-PROJET-METHODES",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": (
                "NSI/chapitres/1NSI-PROJET-METHODES/code/avancement.py"
            ),
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    assert r"\textbf{Précondition : la liste des jalons est non vide.}" in tex
    assert "# 40.0" not in tex
    assert "# Fonctionnalites completes" not in tex
    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 1
    verify_code = _uncomment(verify_matches[0].group("verify"))
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert "assert avancement(jalons) == 40.0" in verify_code
    assert "assert avancement(jalons_non_commences) == 0.0" in verify_code
    assert "assert avancement(jalons_termines) == 100.0" in verify_code
    assert re.search(
        r"try:\n"
        r"    avancement\(\[\]\)\n"
        r"except AssertionError as erreur:\n"
        r'    assert str\(erreur\) == "au moins un jalon est requis"\n'
        r"else:\n"
        r"    raise AssertionError",
        verify_code,
    )


def test_weighted_mean_rejects_negative_and_zero_sum_weights() -> None:
    assert WEIGHTED_MEAN_COURSE.is_file()
    assert WEIGHTED_MEAN_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(WEIGHTED_MEAN_SOURCE))
    assert stdout.getvalue() == ""

    moyenne_ponderee = namespace["moyenne_ponderee"]
    assert moyenne_ponderee([12, 15], [1, 3]) == 14.25

    invalid_cases = [
        (
            [12, 15, 18],
            [1, 2],
            "valeurs et poids doivent avoir la meme longueur",
        ),
        ([12, 15], [1, -0.5], "les poids doivent etre non negatifs"),
        ([12, 15], [0, 0], "la somme des poids doit etre strictement positive"),
        ([], [], "la somme des poids doit etre strictement positive"),
    ]
    for valeurs, poids, message in invalid_cases:
        with pytest.raises(AssertionError) as error:
            moyenne_ponderee(valeurs, poids)
        assert str(error.value) == message

    source_code = WEIGHTED_MEAN_SOURCE.read_text(encoding="utf-8")
    assert source_code.isascii()
    assertions = [
        line.strip()
        for line in source_code.splitlines()
        if line.strip().startswith("assert ")
    ]
    assert assertions == [
        'assert len(valeurs) == len(poids), "valeurs et poids doivent avoir la meme longueur"',
        'assert all(poids_i >= 0 for poids_i in poids), "les poids doivent etre non negatifs"',
        'assert sum(poids) > 0, "la somme des poids doit etre strictement positive"',
    ]

    tex = WEIGHTED_MEAN_COURSE.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/moyenne_ponderee\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"

    course_record = {
        "id": "1NSI-PM-COURS-C3",
        "path": (
            "NSI/chapitres/1NSI-PROJET-METHODES/cours/"
            "1NSI-PM-COURS-C3.tex"
        ),
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-PROJET-METHODES",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": (
                "NSI/chapitres/1NSI-PROJET-METHODES/code/"
                "moyenne_ponderee.py"
            ),
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    assert "combinaison convexe" in tex
    assert r"\min(\texttt{valeurs})" in tex
    assert r"\max(\texttt{valeurs})" in tex
    assert "nécessairement non vide" in tex
    assert "moyenne_ponderee_bugue([12, 15, 18], [1, 2])" in tex
    assert "IndexError: list index out of range" in tex

    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 2
    verify_code = _uncomment(verify_matches[1].group("verify"))
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert "assert moyenne_ponderee([12, 15], [1, 3]) == 14.25" in verify_code
    for valeurs, poids, message in invalid_cases:
        call = f"moyenne_ponderee({valeurs!r}, {poids!r})"
        assert call in verify_code
        assert f'assert str(erreur) == "{message}"' in verify_code
