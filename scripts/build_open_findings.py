#!/usr/bin/env python3
"""Registre unique des findings ouverts, d'ou les compteurs P0/P1/P2 descendent.

Un total qui ne se ramene pas a une liste d'identifiants n'est pas verifiable.
Chaque finding porte donc un identifiant stable, une severite et sa preuve
d'origine ; les agregats sont exactement la longueur des listes correspondantes.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/OPEN_FINDINGS.json"
MD_TARGET = ROOT / "audit/OPEN_FINDINGS.md"
GENERATED_BY = "scripts/build_open_findings.py"


def _load(root: Path, relative: str) -> dict[str, Any] | None:
    path = root / relative
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build(root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    missing_evidence: list[str] = []

    # 1. Clones de production : un finding par objet excedentaire.
    clones = _load(root, "audit/CLONE_DISPOSITION_LEDGER.json")
    if clones is None:
        missing_evidence.append("audit/CLONE_DISPOSITION_LEDGER.json")
    else:
        product_dispositions = {
            "SOURCE_CLONE_WITH_DISTINCT_IDS",
            "ACCIDENTAL_RENDER_DUPLICATION",
            "ASSEMBLY_DUPLICATION",
        }
        for group in clones["groups"]:
            if group["disposition"] not in product_dispositions:
                continue
            members = [m["path"] for m in group["members"]]
            # Le canonique reste ; chaque autre membre est un finding nomme.
            for path in sorted(members)[1:]:
                findings.append({
                    "id": f"CLONE-{group['digest'][:12]}-{Path(path).stem}",
                    "severity": "P0",
                    "kind": "TRUE_PRODUCT_CLONE",
                    "path": path,
                    "group_digest": group["digest"],
                    "disposition": group["disposition"],
                    "evidence": "audit/CLONE_DISPOSITION_LEDGER.json",
                })

    # 2. Derives enonce/corrige.
    binding = _load(root, "audit/EX_CO_SEMANTIC_BINDING.json")
    if binding is None:
        missing_evidence.append("audit/EX_CO_SEMANTIC_BINDING.json")
    else:
        for drift in binding["statement_drift"]:
            findings.append({
                "id": f"DRIFT-{Path(drift['correction']).stem}",
                "severity": "P0",
                "kind": "STUDENT_TEACHER_STATEMENT_DRIFT",
                "path": drift["correction"],
                "declared_target": drift["declared_target"],
                "evidence": "audit/EX_CO_SEMANTIC_BINDING.json",
            })
        for unresolved in binding["unresolved_targets"]:
            findings.append({
                "id": f"UNRESOLVED-{Path(unresolved['correction']).stem}",
                "severity": "P0",
                "kind": "UNRESOLVED_CORRECTION_TARGET",
                "path": unresolved["correction"],
                "evidence": "audit/EX_CO_SEMANTIC_BINDING.json",
            })

    # 3. Couverture programme : une lacune reelle n'a pas la meme gravite qu'une
    #    matrice incomplete devant un contenu qui existe.
    triage = _load(root, "audit/FALSE_COVERAGE_TRIAGE.json")
    if triage is None:
        missing_evidence.append("audit/FALSE_COVERAGE_TRIAGE.json")
    else:
        for entry in triage["entries"]:
            if entry["state"] == "TRUE_CONTENT_GAP":
                findings.append({
                    "id": f"GAP-{entry['atom_id']}",
                    "severity": "P1",
                    "kind": "TRUE_CONTENT_GAP",
                    "atom_id": entry["atom_id"],
                    "manual": entry["manual"],
                    "capacity": entry.get("capacity"),
                    "evidence": "audit/FALSE_COVERAGE_TRIAGE.json",
                })
            elif entry["state"] == "COVERED_BY_REAL_CONTENT":
                findings.append({
                    "id": f"UNREGISTERED-{entry['atom_id']}",
                    "severity": "P2",
                    "kind": "COVERAGE_SOURCE_NOT_REGISTERED",
                    "atom_id": entry["atom_id"],
                    "manual": entry["manual"],
                    "candidate_source": entry.get("candidate_source"),
                    "evidence": "audit/FALSE_COVERAGE_TRIAGE.json",
                })

    # 4. Lignee non tranchee : seule une vraie impasse remonte a l'auteur.
    lineage = _load(root, "audit/PREFILLER_LINEAGE.json")
    if lineage is None:
        missing_evidence.append("audit/PREFILLER_LINEAGE.json")
    else:
        for group in lineage["groups"]:
            if group["lineage_case"] in {"ALL_EMPTY_PRE_FILLER", "MULTIPLE_PREEXISTING_CONTENT"}:
                findings.append({
                    "id": f"AUTHOR-{group['digest'][:12]}",
                    "severity": "P1",
                    "kind": "UNRESOLVED_AUTHOR_DECISION",
                    "group_digest": group["digest"],
                    "lineage_case": group["lineage_case"],
                    "evidence": "audit/PREFILLER_LINEAGE.json",
                })

    for relative in missing_evidence:
        findings.append({
            "id": f"EVIDENCE-{Path(relative).stem}",
            "severity": "P0",
            "kind": "MISSING_EVIDENCE",
            "path": relative,
            "evidence": None,
        })

    findings.sort(key=lambda f: (f["severity"], f["id"]))
    by_severity: dict[str, list[str]] = collections.defaultdict(list)
    for finding in findings:
        by_severity[finding["severity"]].append(finding["id"])
    by_kind = collections.Counter(f["kind"] for f in findings)

    duplicates = [i for i, n in collections.Counter(f["id"] for f in findings).items() if n > 1]

    summary = {
        "TOTAL_P0_OPEN": len(by_severity["P0"]),
        "TOTAL_P1_OPEN": len(by_severity["P1"]),
        "TOTAL_P2_OPEN": len(by_severity["P2"]),
        "TRUE_PRODUCT_CLONES_OPEN": by_kind["TRUE_PRODUCT_CLONE"],
        "STUDENT_TEACHER_STATEMENT_DRIFT": by_kind["STUDENT_TEACHER_STATEMENT_DRIFT"],
        "TRUE_CONTENT_GAPS": by_kind["TRUE_CONTENT_GAP"],
        "COVERAGE_SOURCE_NOT_REGISTERED": by_kind["COVERAGE_SOURCE_NOT_REGISTERED"],
        "UNRESOLVED_AUTHOR_DECISION": by_kind["UNRESOLVED_AUTHOR_DECISION"],
        "MISSING_EVIDENCE": by_kind["MISSING_EVIDENCE"],
        "DUPLICATE_FINDING_IDS": len(duplicates),
        "BY_KIND": dict(by_kind),
    }
    # Les agregats ne sont pas ecrits : ils sont la longueur des listes.
    assert summary["TOTAL_P0_OPEN"] == len(by_severity["P0"])
    assert summary["TRUE_PRODUCT_CLONES_OPEN"] == sum(
        1 for f in findings if f["kind"] == "TRUE_PRODUCT_CLONE"
    )

    return {
        "artifact_type": "open_findings",
        "schema_version": "1.0.0",
        "generated_by": GENERATED_BY,
        "findings": findings,
        "finding_ids_by_severity": {k: sorted(v) for k, v in sorted(by_severity.items())},
        "clone_finding_ids": [f["id"] for f in findings if f["kind"] == "TRUE_PRODUCT_CLONE"],
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = build(args.root)
    JSON_TARGET.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = ["# Findings ouverts", ""]
    for key, value in report["summary"].items():
        lines.append(f"- **{key}** : `{json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value}`")
    MD_TARGET.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report["summary"].items() if k != "BY_KIND"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
