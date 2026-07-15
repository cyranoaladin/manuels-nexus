r"""Gate d'exécution NSI (règle R2) : la vérité est exécutable.

Trois contrôles par objet .tex :
1. Bloc % BEGIN-VERIFY ... % END-VERIFY : script Python (asserts/pytest-style) exécuté
   en sandbox (python -I, timeout, cwd temporaire). fail si code retour != 0.
2. Blocs de trace : % BEGIN-TRACE ... % EXPECTED ... % END-TRACE : le code est exécuté
   et sa sortie standard comparée EXACTEMENT au bloc EXPECTED — aucune sortie de
   programme affichée dans le manuel n'est écrite de tête.
3. Style : le code des environnements \begin{python}...\end{python} est extrait et
   passé à ruff (gate séparé désactivable par --no-ruff).

Verdicts (validation.schema.json) écrits dans chapitres/{CHAP}/validations/ :
   verified | fail | manual_review (aucun bloc et aucun listing : rien à vérifier).
"""
import argparse
import datetime
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from common import ROOT, write_json

VERIFY = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)
TRACE = re.compile(r"% BEGIN-TRACE\n(.*?)% EXPECTED\n(.*?)% END-TRACE", re.S)
PYENV = re.compile(r"\\begin\{python\}(.*?)\\end\{python\}", re.S)
SUBDIRS = ("exercices", "corriges", "evaluations", "ece", "projet", "cours", "methodes", "remediation")


def strip_percent(block: str) -> str:
    return "\n".join(re.sub(r"^%\s?", "", l) for l in block.splitlines())


def run_sandbox(script: str, timeout: int = 30) -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "verify.py"
        path.write_text(script, encoding="utf-8")
        try:
            proc = subprocess.run([sys.executable, "-I", str(path)], capture_output=True,
                                  text=True, timeout=timeout, cwd=tmp)
        except subprocess.TimeoutExpired:
            return 1, "", "timeout"
        return proc.returncode, proc.stdout, proc.stderr


def ruff_check(code: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name
    proc = subprocess.run(["ruff", "check", "--quiet",
                           "--ignore", "E501,F821",  # lignes manuel + fragments pédagogiques
                           path], capture_output=True, text=True)
    Path(path).unlink(missing_ok=True)
    return proc.returncode == 0, proc.stdout[-1500:]


def check_object(tex: Path, no_ruff: bool = False) -> dict:
    src = tex.read_text(encoding="utf-8")
    checks, verdict = [], "verified"

    verify_blocks = VERIFY.findall(src)
    trace_blocks = TRACE.findall(src)
    listings = PYENV.findall(src)

    if not verify_blocks and not trace_blocks and not listings:
        return {"verdict": "manual_review",
                "checks": [{"type": "none", "detail": "aucun bloc VERIFY/TRACE ni listing : revue humaine requise"}]}

    for i, block in enumerate(verify_blocks):
        rc, out, err = run_sandbox(strip_percent(block))
        ok = rc == 0
        checks.append({"type": "verify", "index": i, "pass": ok,
                       "detail": (err or out)[-800:] if not ok else ""})
        if not ok:
            verdict = "fail"

    for i, (code, expected) in enumerate(trace_blocks):
        rc, out, err = run_sandbox(strip_percent(code))
        exp = strip_percent(expected).strip()
        ok = rc == 0 and out.strip() == exp
        checks.append({"type": "trace", "index": i, "pass": ok,
                       "detail": "" if ok else f"attendu:\n{exp}\nobtenu:\n{out.strip()[-600:]}\n{err[-300:]}"})
        if not ok:
            verdict = "fail"

    if not no_ruff:
        for i, code in enumerate(listings):
            ok, detail = ruff_check(code)
            checks.append({"type": "ruff", "index": i, "pass": ok, "detail": detail if not ok else ""})
            if not ok and verdict != "fail":
                verdict = "fail"

    return {"verdict": verdict, "checks": checks}


def main(chap: str, no_ruff: bool) -> int:
    chap_dir = ROOT / "chapitres" / chap
    failures = 0
    for sub in SUBDIRS:
        for tex in sorted((chap_dir / sub).glob("*.tex")):
            result = check_object(tex, no_ruff)
            record = {
                "objet_id": tex.stem, "gate": "sympy",  # champ 'gate' du schéma : exécution
                "verdict": "pass" if result["verdict"] == "verified" else result["verdict"],
                "details": {"checks": result["checks"]},
                "reviewer": "verify_python.py",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            record["gate"] = "sympy"  # compat schéma ; sémantique : gate d'exécution
            write_json(chap_dir / "validations" / f"{tex.stem}.execution.json", record)
            tag = {"pass": "OK    ", "fail": "FAIL  ", "manual_review": "REVIEW"}[record["verdict"]]
            first_fail = next((c["detail"] for c in result["checks"] if not c.get("pass", True)), "")
            print(f"[{tag}] {tex.stem} {first_fail[:90]}")
            if record["verdict"] == "fail":
                failures += 1
    return failures


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    ap.add_argument("--no-ruff", action="store_true")
    args = ap.parse_args()
    sys.exit(1 if main(args.chap, args.no_ruff) else 0)
