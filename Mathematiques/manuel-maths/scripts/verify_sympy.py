"""Gate SymPy (règle R2) : vérifie les affirmations calculables des exercices/corrigés.

Convention : chaque exercice peut embarquer dans son .tex un bloc de vérification
    % BEGIN-VERIFY
    % from sympy import *
    % n = symbols('n')
    % assert simplify(...) == 0
    % END-VERIFY
Les lignes (sans le préfixe '% ') sont exécutées dans un sous-processus Python isolé (-I). Verdict :
    verified        -> toutes les assertions passent
    fail            -> une assertion échoue (erreur mathématique)
    manual_review   -> pas de bloc VERIFY (raisonnement non calculable)
Écrit le verdict dans chapitres/{CHAP}/validations/ (schéma validation.schema.json).
"""
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from common import ROOT, write_json

BLOCK = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)

# Exécuté dans un processus Python isolé. Un retour nul ne suffit pas : chaque
# bloc doit atteindre une assertion et aucune assertion fausse ne peut être
# absorbée par un except du programme vérifié. Le témoin n'est écrit qu'après
# la fin normale de tous les blocs, ce qui refuse aussi sys.exit(0).
CHECKED_RUNNER = r'''
import __future__
import ast
import json
import sys
from pathlib import Path

programs = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
namespace = {"__name__": "__main__", "__file__": sys.argv[1]}
observations = []
future_flags = 0
future_mask = sum(getattr(__future__, name).compiler_flag for name in __future__.all_feature_names)

class ObserveAssertions(ast.NodeTransformer):
    def visit_Assert(self, node):
        self.generic_visit(node)
        def call(name):
            return ast.Expr(value=ast.Call(func=ast.Name(id=name, ctx=ast.Load()), args=[], keywords=[]))
        # Garder l'assert originale dans son contexte : pas de lambda qui
        # changerait la portée d'une affectation := ou l'évaluation du message.
        return ast.copy_location(ast.Try(
            body=[call("__nexus_started_assertion__"), node],
            handlers=[ast.ExceptHandler(type=ast.Name(id="__nexus_BaseException__", ctx=ast.Load()),
                       name=None, body=[call("__nexus_failed_assertion__"), ast.Raise()])],
            orelse=[], finalbody=[]), node)

def execute(program, number):
    global future_flags
    counts = {"assertions_executed": 0, "failed_assertions": 0}
    def started():
        counts["assertions_executed"] += 1
    def failed():
        counts["failed_assertions"] += 1
    namespace.update(__nexus_started_assertion__=started, __nexus_failed_assertion__=failed,
                     __nexus_BaseException__=BaseException)
    tree = ObserveAssertions().visit(ast.parse(program))
    ast.fix_missing_locations(tree)
    code = compile(tree, "<oracle-block-%s>" % number, "exec", flags=future_flags, dont_inherit=True)
    future_flags |= code.co_flags & future_mask
    exec(code, namespace)
    if not counts["assertions_executed"] or counts["failed_assertions"]:
        raise RuntimeError("oracle block has no exercised assertion or an absorbed failure")
    observations.append(counts)

for number, program in enumerate(programs, 1):
    execute(program, number)
Path(sys.argv[2]).write_text(json.dumps({"complete": True, "blocks": observations}))
'''


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


def run_sandbox(script: str | list[str], timeout: int = 30) -> tuple[str, str]:
    programs = [script] if isinstance(script, str) else script
    with tempfile.TemporaryDirectory(prefix="nexus-oracle-") as directory:
        path = Path(directory) / "programs.json"
        completion = Path(directory) / "completion.json"
        path.write_text(json.dumps(programs), encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-c", CHECKED_RUNNER, str(path), str(completion)],
                capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return "fail", "timeout"
        if proc.returncode:
            return "fail", (proc.stderr or proc.stdout).strip()[-2000:]
        if not completion.is_file():
            return "fail", "oracle exited before checked completion"
        observation = json.loads(completion.read_text())
        blocks = observation.get("blocks", [])
        if (not programs or observation.get("complete") is not True
                or len(blocks) != len(programs)
                or any(b["assertions_executed"] < 1 or b["failed_assertions"] for b in blocks)):
            return "fail", "incomplete assertion evidence"
        return "pass", proc.stdout.strip()


def verify_chapter(chap: str) -> int:
    chap_dir = ROOT / "chapitres" / chap
    failures = 0
    # Les fiches methode portent des blocs de verification depuis toujours ;
    # ce repertoire manquait a la liste, si bien que quatre-vingt-dix-huit
    # oracles ecrits n'etaient jamais executes. Un oracle qu'on n'execute pas
    # ne prouve rien -- il rassure, ce qui est pire.
    tex_dirs = ["exercices", "corriges", "evaluations", "remediation", "cours",
                "qcm", "methodes"]
    all_tex = []
    for d in tex_dirs:
        sub = chap_dir / d
        if sub.is_dir():
            all_tex.extend(sub.glob("*.tex"))
    for tex in sorted(all_tex):
        source = tex.read_bytes()
        scripts = extract_scripts(source.decode("utf-8"))
        if not scripts:
            verdict, details = "manual_review", "aucun bloc VERIFY : revue humaine requise"
        else:
            verdict, details = run_sandbox(scripts)
        if tex.read_bytes() != source:
            verdict, details = "fail", "source changed during oracle execution"
        # Un recu qui ne nomme pas la source qu'il atteste ne peut pas
        # PERIMER : un « pass » d'il y a trois mois continue de certifier un
        # contenu modifie depuis. C'est la meme cecite que le P0
        # SELF_CONFIRMING_AGGREGATE_CHECK -- une preuve insensible a la faute
        # qu'elle devrait voir. Le recu porte donc le chemin et le digest du
        # contenu exact qu'il a verifie.
        record = {
            "objet_id": tex.stem, "gate": "sympy",
            "verdict": "pass" if verdict == "pass" else verdict,
            "details": {"output": details},
            "reviewer": "verify_sympy.py",
            "verification_protocol": "EXECUTED_ASSERTIONS_PER_BLOCK_V1",
            "verifier_sha256": "sha256:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source_path": str(tex.relative_to(ROOT)),
            "source_sha256": "sha256:" + hashlib.sha256(source).hexdigest(),
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
