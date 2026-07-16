"""Régression du gate d'exécution : TRACE juste = pass, TRACE fausse = fail."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_python import check_object  # noqa: E402

GOOD = "% BEGIN-TRACE\n% print(1 + 1)\n% EXPECTED\n% 2\n% END-TRACE\n"
BAD = "% BEGIN-TRACE\n% print(1 + 1)\n% EXPECTED\n% 3\n% END-TRACE\n"


def _run(tmp_path, content):
    tex = tmp_path / "obj.tex"
    tex.write_text(content, encoding="utf-8")
    return check_object(tex, no_ruff=True)


def test_trace_correcte(tmp_path):
    assert _run(tmp_path, GOOD)["verdict"] == "verified"


def test_trace_fausse_detectee(tmp_path):
    assert _run(tmp_path, BAD)["verdict"] == "fail"


def test_objet_sans_code_en_revue(tmp_path):
    assert _run(tmp_path, "\\section{Texte pur}")["verdict"] == "manual_review"
