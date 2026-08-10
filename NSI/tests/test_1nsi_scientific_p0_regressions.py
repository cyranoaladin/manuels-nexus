"""Regressions scientifiques P0 pour les cours 1NSI."""
import contextlib
import hashlib
import importlib.util
import io
import re
import runpy
from pathlib import Path


NSI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = NSI_ROOT.parent
COURSE = NSI_ROOT / "chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex"
PYTHON_SOURCE = NSI_ROOT / "chapitres/1NSI-LANGAGE/code/maximum_bugue.py"
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
