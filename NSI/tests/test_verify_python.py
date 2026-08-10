"""Régression du gate d'exécution : TRACE juste = pass, TRACE fausse = fail."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_python  # noqa: E402
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


def test_main_check_calcule_sans_ecrire(tmp_path, monkeypatch, capsys):
    chap_dir = tmp_path / "chapitres" / "CHAPITRE-TEST"
    tex_dir = chap_dir / "cours"
    validation_dir = chap_dir / "validations"
    tex_dir.mkdir(parents=True)
    validation_dir.mkdir()
    tex = tex_dir / "objet.tex"
    receipt = validation_dir / "objet.execution.json"
    tex.write_text(GOOD, encoding="utf-8")
    receipt.write_text(json.dumps({"verdict": "old"}), encoding="utf-8")
    before = {
        path: path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    monkeypatch.setattr(verify_python, "ROOT", tmp_path)

    assert verify_python.main("CHAPITRE-TEST", True, check=True) == 0

    output = capsys.readouterr().out
    assert "[OK" in output
    after = {
        path: path.read_bytes()
        for path in tmp_path.rglob("*")
        if path.is_file()
    }
    assert after == before


def test_cli_accepte_check():
    script = ROOT / "scripts" / "verify_python.py"
    proc = subprocess.run(
        [sys.executable, str(script), "--chap", "CHAPITRE-ABSENT", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
