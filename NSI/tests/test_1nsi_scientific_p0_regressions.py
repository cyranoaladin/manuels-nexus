"""Regressions scientifiques P0 pour les cours 1NSI."""
import contextlib
import hashlib
import io
import re
import runpy
import sys
from pathlib import Path


NSI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = NSI_ROOT.parent
COURSE = NSI_ROOT / "chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex"
PYTHON_SOURCE = NSI_ROOT / "chapitres/1NSI-LANGAGE/code/maximum_bugue.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import review_1nsi_content as review_module  # noqa: E402


def _uncomment(block: str) -> str:
    return "\n".join(re.sub(r"^%\s?", "", line) for line in block.splitlines())


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
    assert "% PYTHON-SOURCE: code/maximum_bugue.py" in tex

    python_match = re.search(r"\\begin\{python\}(.*?)\\end\{python\}", tex, re.DOTALL)
    assert python_match is not None
    assert python_match.group(1) == f"\n{source_code}"

    console_match = re.search(r"\\begin\{console\}(.*?)\\end\{console\}", tex, re.DOTALL)
    assert console_match is not None
    assert console_match.group(1) == f"\n{stdout.getvalue()}"

    trace_match = re.search(
        r"% BEGIN-TRACE\n(.*?)% EXPECTED\n(.*?)% END-TRACE", tex, re.DOTALL
    )
    assert trace_match is not None
    assert _uncomment(trace_match.group(1)) == source_code.rstrip("\n")
    assert _uncomment(trace_match.group(2)) == stdout.getvalue().rstrip("\n")

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
