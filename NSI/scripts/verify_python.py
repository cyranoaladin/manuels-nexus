r"""Gate d'exécution NSI (règle R2) : la vérité est exécutable.

Trois contrôles par objet .tex :
1. Bloc % BEGIN-VERIFY ... % END-VERIFY : script Python (asserts/pytest-style) exécuté
   en sandbox sans réseau : assertions réellement exécutées et fin normale exigées.
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
import sys
from pathlib import Path

if __package__:
    from .common import ROOT, write_json
    from . import execution_protocol as protocol
else:  # Compatibilite avec `python scripts/verify_python.py` depuis NSI/.
    from common import ROOT, write_json
    import execution_protocol as protocol

VERIFY, TRACE, PYENV = protocol.VERIFY, protocol.TRACE, protocol.PYENV
SUBDIRS = ("exercices", "corriges", "evaluations", "ece", "projet", "cours", "methodes", "remediation",
           "banque_ecrite", "banque_pratique", "amenagee")
IMPLEMENTATION_DIGESTS = protocol.implementation_manifest(Path(__file__).resolve().parents[2])


def strip_percent(block: str) -> str:
    return "\n".join(re.sub(r"^%\s?", "", l) for l in block.splitlines())


def _confinement():
    repository = Path(__file__).resolve().parents[2]
    if str(repository) not in sys.path:
        sys.path.insert(0, str(repository))
    from scripts import review_1nsi_content
    return review_1nsi_content


def run_sandbox(script: str, timeout: int = 30) -> tuple[int, str, str]:
    return _confinement()._confined_python(script, timeout=timeout)


def ruff_check(code: str) -> tuple[bool, str]:
    return _confinement()._confined_ruff(code)


def check_object(tex: Path, no_ruff: bool = False) -> dict:
    source = tex.read_bytes()
    src = source.decode("utf-8")
    checks, verdict = [], "verified"
    verify_blocks = [strip_percent(block) for block in VERIFY.findall(src)]
    trace_blocks = TRACE.findall(src)
    listings = PYENV.findall(src)
    dependencies, alignment = protocol.source_dependencies(tex.resolve(), src, ROOT.resolve())
    checks.extend(alignment)
    executed_programs = []
    if not verify_blocks and not trace_blocks and not listings:
        verdict = "manual_review"
        checks.append({"type": "none", "detail": "aucun bloc VERIFY/TRACE ni listing : revue humaine requise"})
    for i, program in enumerate(verify_blocks):
        observation = protocol.checked_assertions(program, run_sandbox)
        checks.append({"type": "verify", "index": i, **observation})
        if observation["pass"]:
            executed_programs.append(program)
        else:
            verdict = "fail"
    for i, (code, expected) in enumerate(trace_blocks):
        program = strip_percent(code)
        completed, out, err = protocol.completed_trace(program, run_sandbox)
        exp = strip_percent(expected)
        # The TeX convention omits the final line terminator, never spaces
        # inside or around the printed output.
        ok = completed and out in (exp, exp + "\n")
        checks.append({"type": "trace", "index": i, "pass": ok,
                       "detail": "" if ok else f"attendu:{exp!r}; obtenu:{out[-600:]!r}; {err[-300:]}"})
        if ok:
            executed_programs.append(program)
        else:
            verdict = "fail"
    for i, code in enumerate(listings):
        linked = protocol.linked_to_executed_program(code, executed_programs)
        checks.append({"type": "listing_execution", "index": i,
                       "state": "LINKED_TO_EXECUTED_PROGRAM" if linked else "PENDING",
                       "detail": "identical AST statements in an executed VERIFY/TRACE program" if linked else "listing has no binding to executed code"})
        if not linked and verdict != "fail":
            verdict = "manual_review"
        if not no_ruff:
            ok, detail = ruff_check(code)
            checks.append({"type": "ruff", "index": i, "pass": ok, "detail": detail if not ok else ""})
            if not ok:
                verdict = "fail"
    for path in dependencies:
        linked = protocol.linked_to_executed_program((ROOT / path).read_text(), executed_programs)
        checks.append({"type": "python_source_execution", "source": path,
                       "state": "LINKED_TO_EXECUTED_PROGRAM" if linked else "PENDING",
                       "detail": "identical AST statements in an executed VERIFY/TRACE program" if linked else "referenced Python has no binding to executed code"})
        if not linked and verdict != "fail":
            verdict = "manual_review"
    if any(row.get("pass") is False for row in alignment):
        verdict = "fail"
    if not protocol.complete_marker_sets(src):
        verdict = "fail"
        checks.append({"type": "marker_coverage", "pass": False, "detail": "malformed or excluded VERIFY/TRACE/listing block"})
    if tex.read_bytes() != source or any(protocol.digest((ROOT / path).read_bytes()) != digest for path, digest in dependencies.items()):
        verdict = "fail"
        checks.append({"type": "source_stability", "pass": False, "detail": "source or dependency changed during execution"})
    if protocol.implementation_manifest(Path(__file__).resolve().parents[2]) != IMPLEMENTATION_DIGESTS:
        verdict = "fail"
        checks.append({"type": "method_stability", "pass": False, "detail": "implementation changed since verifier load"})
    return {"verdict": verdict, "checks": checks, "dependency_digests": dependencies,
            "source_sha256": protocol.digest(source), "implementation_digests": IMPLEMENTATION_DIGESTS.copy(),
            "certifies_documentary_claims": False, "certifies_complete_program_correctness": False,
            "ruff_performed": bool(listings) and not no_ruff}


def main(chap: str, no_ruff: bool, check: bool = False) -> int:
    chap_dir = ROOT / "chapitres" / chap
    discovered = tuple(sorted(path for sub in SUBDIRS for path in (chap_dir / sub).glob("*.tex")))
    if not discovered:
        print(f"[FAIL  ] {chap}: chapitre absent ou vide ; aucun objet TeX à vérifier")
        return 1
    failures = 0
    for tex in discovered:
        if not tex.is_file():
            print(f"[FAIL  ] {chap}: source supprimée du périmètre observé : {tex.relative_to(ROOT)}")
            failures += 1
            continue
        result = check_object(tex, no_ruff)
        if (protocol.digest(tex.read_bytes()) != result["source_sha256"]
                or protocol.implementation_manifest(Path(__file__).resolve().parents[2]) != result["implementation_digests"]
                or any(protocol.digest((ROOT / path).read_bytes()) != digest for path, digest in result["dependency_digests"].items())):
            result["verdict"] = "fail"
            result["checks"].append({"type": "receipt_stability", "pass": False,
                                     "detail": "input changed between execution and receipt"})
        # Un recu qui ne nomme pas la source qu'il atteste ne peut pas
        # PERIMER : un « pass » d'il y a trois mois continue de certifier
        # un contenu reecrit depuis. Le gate de couverture d'evaluations
        # exige d'ailleurs cette liaison, et faute de la trouver ici il
        # refusait chaque evaluation NSI sans qu'aucun defaut ne l'explique.
        # Le recu porte donc le chemin et le digest du contenu exact
        # qu'il a execute, comme le fait deja le gate SymPy des maths.
        record = {
            "objet_id": tex.stem, "gate": "sympy",  # champ 'gate' du schéma : exécution
            "verdict": "pass" if result["verdict"] == "verified" else result["verdict"],
            "details": {"checks": result["checks"]},
            "reviewer": "verify_python.py",
            "verification_protocol": protocol.PROTOCOL,
            "verifier_sha256": result["implementation_digests"]["NSI/scripts/verify_python.py"],
            "implementation_digests": result["implementation_digests"],
            "dependency_digests": result["dependency_digests"],
            "certifies_documentary_claims": False,
            "certifies_complete_program_correctness": False,
            "ruff_performed": result["ruff_performed"],
            "source_path": str(tex.relative_to(ROOT)),
            "source_sha256": result["source_sha256"],
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        record["gate"] = "sympy"  # compat schéma ; sémantique : gate d'exécution
        if not check:
            write_json(chap_dir / "validations" / f"{tex.stem}.execution.json", record)
        tag = {"pass": "OK    ", "fail": "FAIL  ", "manual_review": "REVIEW"}[record["verdict"]]
        first_fail = next((c["detail"] for c in result["checks"] if not c.get("pass", True)), "")
        print(f"[{tag}] {tex.stem} {first_fail[:90]}")
        if record["verdict"] == "fail":
            failures += 1
    current = {path for sub in SUBDIRS for path in (chap_dir / sub).glob("*.tex")}
    if current != set(discovered):
        added = sorted(str(path.relative_to(ROOT)) for path in current - set(discovered))
        removed = sorted(str(path.relative_to(ROOT)) for path in set(discovered) - current)
        print(f"[FAIL  ] {chap}: périmètre modifié pendant vérification ; ajoutés={added}, supprimés={removed}")
        failures += 1
    return failures


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    ap.add_argument("--no-ruff", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    sys.exit(1 if main(args.chap, args.no_ruff, args.check) else 0)
