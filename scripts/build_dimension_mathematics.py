#!/usr/bin/env python3
"""Dimension de certification `mathematics` — exactitude scientifique vérifiable.

Portée déterminée par le contrat, pas devinée : la dimension couvre les objets
qui portent une assertion mathématique **mécaniquement vérifiable**. Deux
sources existent déjà dans le dépôt et sont ici exploitées comme oracles :

* les blocs `% VERIFY ... % END-VERIFY` des fiches méthode, qui contiennent des
  assertions SymPy écrites par les auteurs ;
* les paramètres `parametres_sympy` / `sympy_params` déclarés en `% META:`.

Un objet sans assertion vérifiable est déclaré `NOT_APPLICABLE` pour cette
dimension — et `NOT_APPLICABLE` n'est **pas** `PASS` : il est compté et
rapporté séparément, et la dimension ne peut passer que si au moins une cible a
réellement été examinée.

Le producteur échoue par mutation réelle : une assertion fausse dans un bloc
VERIFY produit un constat bloquant.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certification_dimensions as cd  # noqa: E402

ROOT = cd.ROOT
OUTPUT = ROOT / "audit/DIMENSION_MATHEMATICS.json"
NON_FORMALIZABLE_CLOSURE = ROOT / "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.json"
PRODUCER_VERSION = "2.0.0"

VERIFY_BLOCK = re.compile(r"^% BEGIN-VERIFY\s*$(.*?)^% END-VERIFY\s*$", re.S | re.M)
COMMENT_LINE = re.compile(r"^%[ \t]?(.*)$")
def assertion_count(programme: str) -> int | None:
    """Nombre d'assertions du programme, ou `None` s'il ne compile pas.

    Le detecteur precedent cherchait `^\\s*assert` : il ne voyait pas
    `E = p; assert E == Rational(3, 10)`, ou l'assertion suit un point-virgule.
    Quatorze objets sur les vingt-deux signales « bloc present mais sans
    assertion executable » en contenaient pourtant. Un motif textuel se
    tromperait aussi sur le mot `assert` dans une chaine ou un commentaire.

    Python sait analyser du Python : on compte des noeuds `ast.Assert`, pas des
    lignes qui y ressemblent. Un bloc qui ne compile pas ne renvoie pas zero —
    ce serait le confondre avec un bloc vide, alors que c'est un autre defaut.
    """
    import ast  # noqa: PLC0415

    try:
        tree = ast.parse(programme)
    except SyntaxError:
        return None
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assert))

MATHS_MANUALS = frozenset({"1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES"})

#: Notation mathématique dans le corps imprimé.
MATH_NOTATION = re.compile(r"\$|\\dfrac|\\frac|\\sqrt|\\int|\\sum|\\lim|\\vec|\\begin\{align")

#: Types d'objets dont l'attendu est un accompagnement ou un jugement, pas une
#: assertion calculable : un coup de pouce reformule une étape, une méthode
#: décrit une démarche, un QCM est prouvé par la chaîne d'oracle QCM dédiée.
NON_FORMALIZABLE_TYPES = frozenset({
    "coup_de_pouce", "methode", "qcm", "qcm_diagnostics", "projet",
    "experimentation", "remediation", "amenagee", "algorithme",
})

#: Types dont un objet mathématique *pourrait* porter un bloc de vérification.
ORACLE_CAPABLE_TYPES = frozenset({
    "cours", "exercice", "corrige", "evaluation", "corrige_evaluation",
})


def classify_not_applicable(manual: str, type_objet: str | None, body: str) -> str:
    """Pourquoi cet objet ne porte pas d'assertion vérifiable.

    `NOT_APPLICABLE` ne doit pas servir de fourre-tout : un contenu
    mathématique sans oracle n'est pas hors sujet, il est simplement non
    outillé, et cela doit se voir.
    """
    mathematical = manual in MATHS_MANUALS or bool(MATH_NOTATION.search(body))
    if not mathematical:
        return "TRULY_NOT_MATHEMATICAL"
    if type_objet in NON_FORMALIZABLE_TYPES:
        return "MATHEMATICAL_NON_FORMALIZABLE"
    if type_objet in ORACLE_CAPABLE_TYPES:
        return "MISSING_ORACLE"
    return "UNKNOWN"


def extract_program(block_body: str) -> list[str]:
    """Le programme Python que les auteurs ont écrit derrière les `%`."""
    lines = []
    for raw in block_body.splitlines():
        match = COMMENT_LINE.match(raw)
        if match is None:
            continue
        lines.append(match.group(1))
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def _run_assertions(source_lines: list[str]) -> tuple[bool, str]:
    """Exécute le programme du bloc VERIFY dans un espace de noms isolé.

    Le bloc est exécuté d'un seul tenant : les auteurs y déclarent leurs
    symboles avant de les utiliser, et découper ligne à ligne casserait ces
    définitions.
    """
    import contextlib
    import io
    import sympy

    namespace: dict[str, Any] = {"__builtins__": __builtins__}
    namespace.update({name: getattr(sympy, name) for name in dir(sympy) if not name.startswith("_")})
    program = "\n".join(source_lines)
    try:
        # Certains blocs impriment leurs résultats intermédiaires : on capture
        # cette sortie pour que le producteur reste lisible.
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(program, "<verify>", "exec"), namespace)
        return True, ""
    except AssertionError as exc:
        return False, f"assertion fausse : {exc}" if str(exc) else "assertion fausse"
    except Exception as exc:  # noqa: BLE001 - on rapporte, on ne masque pas
        return False, f"{type(exc).__name__}: {exc}"


def build() -> dict[str, Any]:
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    evidence = cd.DimensionEvidence(
        dimension="mathematics",
        scope=(
            "objets porteurs d'une assertion mathématique mécaniquement vérifiable "
            "(blocs % VERIFY SymPy) dans les manuels de mathématiques et NSI"
        ),
        producer="scripts/build_dimension_mathematics.py",
        producer_version=PRODUCER_VERSION,
        evidence_head=cd.current_head(),
        input_digest="",
    )

    from collections import Counter

    na_partition: Counter = Counter()
    inputs: list[Path] = [ROOT / "audit/INVENTAIRE_COLLECTION.json"]
    examined: list[str] = []
    assertions_run = 0
    objects_with_verify = 0
    not_applicable = 0

    for manual, mval in sorted(inventory.get("manuals", {}).items()):
        for chapter, cval in sorted(mval.get("chapters", {}).items()):
            for obj in cval.get("objects", []):
                path = ROOT / obj["path"]
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                block = VERIFY_BLOCK.search(text)
                if not block:
                    not_applicable += 1
                    lines_of_body = text.splitlines()[1:]
                    meta = json.loads(text.split("\n", 1)[0][len("% META:"):]) if text.startswith("% META:") else {}
                    na_partition[
                        classify_not_applicable(
                            manual, meta.get("type_objet"), "\n".join(lines_of_body)
                        )
                    ] += 1
                    continue
                inputs.append(path)
                objects_with_verify += 1
                lines = extract_program(block.group(1))
                compte = assertion_count("\n".join(lines))
                if compte is None:
                    evidence.findings.append(cd.Finding(
                        target=obj["id"], code="UNPARSABLE_VERIFY_BLOCK",
                        detail="bloc % VERIFY présent mais syntaxiquement invalide",
                        blocking=False,
                    ))
                elif compte == 0:
                    evidence.findings.append(cd.Finding(
                        target=obj["id"], code="EMPTY_VERIFY_BLOCK",
                        detail="bloc % VERIFY présent mais sans assertion exécutable",
                        blocking=False,
                    ))
                    continue
                examined.append(obj["id"])
                assertions_run += compte
                ok, detail = _run_assertions(lines)
                if not ok:
                    evidence.findings.append(cd.Finding(
                        target=obj["id"], code="MATHEMATICAL_ASSERTION_FAILED",
                        detail=f"{obj['path']} — {detail}",
                    ))

    evidence.input_digest = cd.digest_inputs(inputs)
    evidence.input_paths = cd.relative_paths(inputs)
    evidence.not_applicable_targets = {
        "objects_without_verifiable_assertion": str(not_applicable),
        "semantics": (
            "NOT_APPLICABLE n'est pas PASS : ces objets ne portent aucune assertion "
            "mécaniquement vérifiable et relèvent d'une autre preuve"
        ),
        **{key: str(value) for key, value in sorted(na_partition.items())},
    }
    if na_partition.get("UNKNOWN"):
        evidence.findings.append(cd.Finding(
            target="ALL", code="MATHEMATICS_UNKNOWN_CLASSIFICATION",
            detail=f"{na_partition['UNKNOWN']} objet(s) non classés",
        ))
    # QUATRIÈME CONDITION. Un objet mathématique sans oracle n'est pas hors
    # champ : il est simplement hors de portée du calcul. Tant que personne
    # n'a établi son exactitude autrement, la dimension ne sait rien de lui —
    # et une dimension qui passe en ignorant ce qu'elle ne sait pas ne prouve
    # rien. Le rouge que cette condition produit est sain : il dit ce qui
    # reste à faire au lieu de le taire.
    non_formalizable_pending = None
    if NON_FORMALIZABLE_CLOSURE.is_file():
        closure = json.loads(
            NON_FORMALIZABLE_CLOSURE.read_text(encoding="utf-8")
        )
        resume = closure.get("summary") or {}
        non_formalizable_pending = int(
            resume.get("MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING", -1)
        )
        inputs.append(NON_FORMALIZABLE_CLOSURE)
        if not resume.get("STATES_SUM_EQUALS_TOTAL"):
            evidence.findings.append(cd.Finding(
                target="ALL", code="NON_FORMALIZABLE_CLOSURE_INCOHERENT",
                detail=(
                    "la fermeture des objets non formalisables ne totalise pas "
                    "sa propre population : elle ne peut rien établir"
                ),
            ))
        if non_formalizable_pending:
            evidence.findings.append(cd.Finding(
                target="ALL", code="MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING",
                detail=(
                    f"{non_formalizable_pending} objet(s) mathématiques sans "
                    "oracle possible n'ont reçu aucune revue mathématique : "
                    "leur exactitude n'est établie ni par le calcul ni par un "
                    "raisonnement écrit. La dimension ne peut pas passer en "
                    "ignorant ce qu'elle n'a pas examiné."
                ),
            ))
    else:
        non_formalizable_pending = -1
        evidence.findings.append(cd.Finding(
            target="ALL", code="NON_FORMALIZABLE_CLOSURE_MISSING",
            detail=(
                "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.json absent : la "
                "quatrième condition de la dimension ne peut pas être évaluée"
            ),
        ))

    if na_partition.get("MISSING_ORACLE"):
        evidence.findings.append(cd.Finding(
            target="ALL", code="MATHEMATICAL_CONTENT_WITHOUT_ORACLE",
            detail=(
                f"{na_partition['MISSING_ORACLE']} objet(s) mathématiques d'un type "
                "qui pourrait porter un bloc % BEGIN-VERIFY n'en portent pas : leur "
                "exactitude n'est pas mécaniquement établie. Un objet qu'on "
                "*pourrait* vérifier et qu'on ne vérifie pas n'est pas hors "
                "champ : la dimension ne peut donc pas passer."
            ),
        ))
    evidence.coverage = {
        "targets_examined": examined,
        "objects_with_verify_block": objects_with_verify,
        "assertions_executed": assertions_run,
        "objects_not_applicable": not_applicable,
        "maths_manuals_in_scope": sorted(MATHS_MANUALS),
    }

    payload = cd.render_evidence(evidence)
    payload["summary"] = {
        "OBJECTS_WITH_VERIFIABLE_ASSERTIONS": objects_with_verify,
        "ASSERTIONS_EXECUTED": assertions_run,
        "MATHEMATICAL_ASSERTION_FAILURES": sum(
            1 for f in evidence.findings if f.code == "MATHEMATICAL_ASSERTION_FAILED"
        ),
        "EMPTY_VERIFY_BLOCKS": sum(
            1 for f in evidence.findings if f.code == "EMPTY_VERIFY_BLOCK"
        ),
        "OBJECTS_NOT_APPLICABLE": not_applicable,
        "NOT_APPLICABLE_PARTITION": dict(sorted(na_partition.items())),
        "MATHEMATICS_UNKNOWN": na_partition.get("UNKNOWN", 0),
        "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING": non_formalizable_pending,
        "PASS_CONDITIONS": [
            "MATHEMATICAL_ASSERTION_FAILURES = 0",
            "MISSING_ORACLE = 0",
            "MATHEMATICS_UNKNOWN = 0",
            "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING = 0",
        ],
    }
    return payload


def write(payload: dict[str, Any]) -> dict[str, Any]:
    """Depose la preuve. Seule etape qui touche le disque."""
    OUTPUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        if not OUTPUT.is_file():
            print("DIMENSION_MATHEMATICS check: MISSING")
            return 1
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
            print("DIMENSION_MATHEMATICS check: STALE")
            return 1
        print("DIMENSION_MATHEMATICS check: OK")
        return 0
    write(payload)
    print(json.dumps({"status": payload["status"], **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
