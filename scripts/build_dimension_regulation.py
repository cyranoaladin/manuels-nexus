#!/usr/bin/env python3
"""Dimension de certification `regulation` — conformité aux programmes officiels.

Portée : les six manuels de la collection. Pour chacun, l'autorité réglementaire
est le référentiel de capacités déposé (`referentiel/capacites_*.json`), lui-même
adossé à un arrêté publié au BO.

Trois exigences, mesurées et non affirmées :

    WRONG_YEAR_AUTHORITY              autorités divergentes ou non identifiées
    OFFICIAL_REQUIREMENTS_UNCOVERED   capacités officielles sans aucun objet
    UNLABELLED_OUT_OF_PROGRAMME_CONTENT
                                      objets hors référentiel non étiquetés

La troisième distingue deux choses que confondrait un simple `set - set` : les
alias locaux de chapitre (`C1`, `TSPE-TRIGONOMETRIE-C1`) et les compétences du
préambule (`BO-PREAMBULE-*`) sont des espaces de nommage internes, pas du
contenu hors programme. Seul un code qui n'appartient ni au référentiel ni à ces
espaces, et qui n'est pas explicitement marqué `OPTIONAL_EXTENSION`, est un
constat bloquant.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certification_dimensions as cd  # noqa: E402

ROOT = cd.ROOT
OUTPUT = ROOT / "audit/DIMENSION_REGULATION.json"
PRODUCER_VERSION = "1.0.0"

REFERENTIAL_DIRS = ("NSI/referentiel", "Mathematiques/manuel-maths/referentiel")
MANUAL_TO_LEVEL = {
    "1NSI": "1NSI", "TNSI": "TNSI", "1SPE": "1SPE",
    "TSPE_2026_2027": "TSPE", "TCOMPL": "TCOMPL", "TEXPERTES": "TEXPERTES",
}

NOR_PATTERN = re.compile(r"MEN[A-Z]\d{7}[A-Z]")
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
#: Espaces de nommage internes : alias de chapitre et compétences du préambule.
LOCAL_ALIAS = re.compile(r"^(C\d+|[A-Z0-9_]+-[A-Z0-9-]+-C\d+|BO-PREAMBULE-[A-Z-]+)$")
UNVERIFIED_MARKER = re.compile(r"a re-verifier|à re-vérifier", re.I)


def load_referentials() -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    capacities: dict[str, dict[str, Any]] = defaultdict(dict)
    authorities: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for directory in REFERENTIAL_DIRS:
        base = ROOT / directory
        if not base.is_dir():
            continue
        for path in sorted(base.glob("capacites_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            level = payload.get("niveau")
            reference = str(payload.get("bo_reference", ""))
            authorities[level].append({
                "file": str(path.relative_to(ROOT)),
                "bo_reference": reference,
                "nor": sorted(set(NOR_PATTERN.findall(reference))),
                "years": sorted({m.group(0) for m in YEAR_PATTERN.finditer(reference)}),
                "self_declared_unverified": bool(UNVERIFIED_MARKER.search(reference)),
            })
            for capacity in payload.get("capacites", []):
                capacities[level][capacity["id"]] = {
                    "theme": payload.get("theme"),
                    "referential_file": path.name,
                    "contenu_bo": capacity.get("contenu_bo", ""),
                }
    return capacities, authorities


def declared_by_manual() -> dict[str, dict[str, list[str]]]:
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    result: dict[str, dict[str, list[str]]] = {}
    for manual, mval in inventory.get("manuals", {}).items():
        codes: dict[str, list[str]] = defaultdict(list)
        for chapter, cval in mval.get("chapters", {}).items():
            for obj in cval.get("objects", []):
                path = ROOT / obj["path"]
                if not path.is_file():
                    continue
                first = path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
                if not first.startswith("% META:"):
                    continue
                meta = json.loads(first[len("% META:"):])
                extension = (
                    meta.get("programme_alignment") == "OPTIONAL_EXTENSION"
                    or bool(meta.get("extension_codes"))
                )
                for code in meta.get("capacites") or []:
                    codes[code].append(f"{obj['id']}|{'EXT' if extension else 'STD'}")
        result[manual] = dict(codes)
    return result


def build() -> dict[str, Any]:
    capacities, authorities = load_referentials()
    declared = declared_by_manual()

    inputs = [ROOT / "audit/INVENTAIRE_COLLECTION.json"]
    for directory in REFERENTIAL_DIRS:
        inputs.extend(sorted((ROOT / directory).glob("capacites_*.json")))

    evidence = cd.DimensionEvidence(
        dimension="regulation",
        scope="les six manuels de la collection, contre leur référentiel de capacités déposé",
        producer="scripts/build_dimension_regulation.py",
        producer_version=PRODUCER_VERSION,
        evidence_head=cd.current_head(),
        input_digest=cd.digest_inputs(inputs),
    )

    examined = []
    coverage_rows = {}
    for manual, level in sorted(MANUAL_TO_LEVEL.items()):
        official = capacities.get(level, {})
        if not official:
            evidence.findings.append(cd.Finding(
                target=manual, code="NO_OFFICIAL_REFERENTIAL",
                detail=f"aucun référentiel déposé pour le niveau {level}",
            ))
            continue
        examined.append(manual)
        codes = declared.get(manual, {})

        # 1. autorité
        entries = authorities.get(level, [])
        nors = {tuple(e["nor"]) for e in entries if e["nor"]}
        missing_nor = [e["file"] for e in entries if not e["nor"]]
        unverified = [e["file"] for e in entries if e["self_declared_unverified"]]
        year_sets = {tuple(e["years"]) for e in entries}
        if len(nors) > 1:
            evidence.findings.append(cd.Finding(
                target=manual, code="WRONG_YEAR_AUTHORITY",
                detail=f"NOR divergents dans un même niveau : {sorted(nors)}",
            ))
        if missing_nor:
            evidence.findings.append(cd.Finding(
                target=manual, code="AUTHORITY_NOR_ABSENT",
                detail=f"{len(missing_nor)} référentiel(s) sans NOR identifiable : {missing_nor[:3]}",
            ))
        if unverified:
            evidence.findings.append(cd.Finding(
                target=manual, code="AUTHORITY_SELF_DECLARED_UNVERIFIED",
                detail=f"{len(unverified)} référentiel(s) portent « à re-vérifier contre le BO »",
            ))
        if len(year_sets) > 1:
            evidence.findings.append(cd.Finding(
                target=manual, code="AUTHORITY_YEAR_DIVERGENCE",
                detail=f"années citées divergentes dans un même niveau : {sorted(year_sets)}",
            ))

        # 2. couverture
        uncovered = sorted(set(official) - set(codes))
        for code in uncovered:
            evidence.findings.append(cd.Finding(
                target=f"{manual}::{code}", code="OFFICIAL_REQUIREMENT_UNCOVERED",
                detail=f"{official[code]['theme']} — {official[code]['contenu_bo']}",
            ))

        # 3. contenu hors programme non étiqueté
        unlabelled = []
        for code, refs in sorted(codes.items()):
            if code in official or LOCAL_ALIAS.match(code):
                continue
            if all(ref.endswith("|EXT") for ref in refs):
                continue  # explicitement marqué OPTIONAL_EXTENSION
            unlabelled.append(code)
        for code in unlabelled:
            evidence.findings.append(cd.Finding(
                target=f"{manual}::{code}", code="UNLABELLED_OUT_OF_PROGRAMME_CONTENT",
                detail="code de capacité hors référentiel, sans marquage OPTIONAL_EXTENSION",
            ))

        coverage_rows[manual] = {
            "official_capacities": len(official),
            "covered": len(set(official) & set(codes)),
            "uncovered": len(uncovered),
            "unlabelled_out_of_programme": len(unlabelled),
        }

    evidence.coverage = {"targets_examined": examined, "per_manual": coverage_rows}
    payload = cd.write_evidence(evidence, OUTPUT)
    payload["summary"] = {
        "WRONG_YEAR_AUTHORITY": sum(
            1 for f in evidence.findings if f.code in {"WRONG_YEAR_AUTHORITY", "AUTHORITY_YEAR_DIVERGENCE"}
        ),
        "AUTHORITY_NOR_ABSENT": sum(1 for f in evidence.findings if f.code == "AUTHORITY_NOR_ABSENT"),
        "AUTHORITY_SELF_DECLARED_UNVERIFIED": sum(
            1 for f in evidence.findings if f.code == "AUTHORITY_SELF_DECLARED_UNVERIFIED"
        ),
        "OFFICIAL_REQUIREMENTS_UNCOVERED": sum(
            1 for f in evidence.findings if f.code == "OFFICIAL_REQUIREMENT_UNCOVERED"
        ),
        "UNLABELLED_OUT_OF_PROGRAMME_CONTENT": sum(
            1 for f in evidence.findings if f.code == "UNLABELLED_OUT_OF_PROGRAMME_CONTENT"
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not OUTPUT.is_file():
            print("DIMENSION_REGULATION check: MISSING")
            return 1
        previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        payload = build()
        if previous == payload:
            print("DIMENSION_REGULATION check: OK")
            return 0
        print("DIMENSION_REGULATION check: STALE")
        return 1
    payload = build()
    print(json.dumps({"status": payload["status"], **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
