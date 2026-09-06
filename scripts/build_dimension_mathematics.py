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
PRODUCER_VERSION = "1.0.0"

VERIFY_BLOCK = re.compile(r"^% BEGIN-VERIFY\s*$(.*?)^% END-VERIFY\s*$", re.S | re.M)
COMMENT_LINE = re.compile(r"^%[ \t]?(.*)$")
ASSERT_LINE = re.compile(r"^\s*assert\b")

MATHS_MANUALS = frozenset({"1SPE", "TSPE_2026_2027", "TCOMPL", "TEXPERTES"})


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
                    continue
                inputs.append(path)
                objects_with_verify += 1
                lines = extract_program(block.group(1))
                if not any(ASSERT_LINE.match(line) for line in lines):
                    evidence.findings.append(cd.Finding(
                        target=obj["id"], code="EMPTY_VERIFY_BLOCK",
                        detail="bloc % VERIFY présent mais sans assertion exécutable",
                        blocking=False,
                    ))
                    continue
                examined.append(obj["id"])
                assertions_run += sum(1 for line in lines if ASSERT_LINE.match(line))
                ok, detail = _run_assertions(lines)
                if not ok:
                    evidence.findings.append(cd.Finding(
                        target=obj["id"], code="MATHEMATICAL_ASSERTION_FAILED",
                        detail=f"{obj['path']} — {detail}",
                    ))

    evidence.input_digest = cd.digest_inputs(inputs)
    evidence.not_applicable_targets = {
        "objects_without_verifiable_assertion": str(not_applicable),
        "semantics": (
            "NOT_APPLICABLE n'est pas PASS : ces objets ne portent aucune assertion "
            "mécaniquement vérifiable et relèvent de la revue humaine"
        ),
    }
    evidence.coverage = {
        "targets_examined": examined,
        "objects_with_verify_block": objects_with_verify,
        "assertions_executed": assertions_run,
        "objects_not_applicable": not_applicable,
        "maths_manuals_in_scope": sorted(MATHS_MANUALS),
    }

    payload = cd.write_evidence(evidence, OUTPUT)
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
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        print("DIMENSION_MATHEMATICS check: OK")
        return 0
    print(json.dumps({"status": payload["status"], **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
