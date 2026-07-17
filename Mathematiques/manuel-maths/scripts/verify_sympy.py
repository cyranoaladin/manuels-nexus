"""Gate SymPy (règle R2) : vérifie les affirmations calculables des exercices/corrigés.

Convention : chaque exercice peut embarquer dans son .tex un bloc de vérification
    % BEGIN-VERIFY
    % from sympy import *
    % n = symbols('n')
    % assert simplify(...) == 0
    % END-VERIFY
Les lignes (sans le préfixe '% ') sont exécutées en sandbox. Verdict :
    verified        -> toutes les assertions passent
    fail            -> une assertion échoue (erreur mathématique)
    manual_review   -> pas de bloc VERIFY (raisonnement non calculable)
Écrit le verdict dans chapitres/{CHAP}/validations/ (schéma validation.schema.json).
"""
import argparse
import datetime
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from common import ROOT, write_json

BLOCK = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)


def extract_scripts(tex: str) -> list[str]:
    """Extract ALL BEGIN-VERIFY blocks from a .tex file."""
    matches = BLOCK.findall(tex)
    scripts = []
    for body in matches:
        lines = [re.sub(r"^%\s?", "", l) for l in body.splitlines()]
        scripts.append("\n".join(lines))
    return scripts


def extract_script(tex: str) -> str | None:
    """Legacy: return a single combined script from all blocks."""
    scripts = extract_scripts(tex)
    if not scripts:
        return None
    return "\n".join(scripts)


def run_sandbox(script: str, timeout: int = 30) -> tuple[str, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(script)
        path = f.name
    try:
        proc = subprocess.run([sys.executable, "-I", path], capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "fail", "timeout"
    if proc.returncode == 0:
        return "pass", proc.stdout.strip()
    return "fail", (proc.stderr or proc.stdout).strip()[-2000:]


def verify_chapter(chap: str) -> int:
    chap_dir = ROOT / "chapitres" / chap
    failures = 0
    tex_dirs = ["exercices", "corriges", "evaluations", "remediation", "cours", "qcm"]
    all_tex = []
    for d in tex_dirs:
        sub = chap_dir / d
        if sub.is_dir():
            all_tex.extend(sub.glob("*.tex"))
    for tex in sorted(all_tex):
        script = extract_script(tex.read_text(encoding="utf-8"))
        if script is None:
            verdict, details = "manual_review", "aucun bloc VERIFY : revue humaine requise"
        else:
            verdict, details = run_sandbox(script)
        record = {
            "objet_id": tex.stem, "gate": "sympy",
            "verdict": "pass" if verdict == "pass" else verdict,
            "details": {"output": details},
            "reviewer": "verify_sympy.py",
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        write_json(chap_dir / "validations" / f"{tex.stem}.sympy.json", record)
        symbol = {"pass": "OK ", "fail": "FAIL", "manual_review": "REVIEW"}[record["verdict"]]
        print(f"[{symbol}] {tex.stem}: {details[:100]}")
        if record["verdict"] == "fail":
            failures += 1
    return failures


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    args = ap.parse_args()
    sys.exit(1 if verify_chapter(args.chap) else 0)
