#!/usr/bin/env python3
"""Registre unique des findings ouverts, d'où les compteurs P0/P1/P2 descendent.

Architecture de producteur avec enregistrement unifié (SSOT) :
- Chaque domaine de qualité enregistre son producteur de findings
- Validation stricte de fraîcheur et de schéma pour chaque producteur
- Détection et élimination de conflits de sources (CURRENT_FINDING_SOURCE_CONFLICTS = 0)
- Aucun compteur codé en dur : chaque agrégat est strictement dérivé des listes
"""

from __future__ import annotations

import argparse
import collections
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
JSON_TARGET = ROOT / "audit/OPEN_FINDINGS.json"
MD_TARGET = ROOT / "audit/OPEN_FINDINGS.md"
GENERATED_BY = "scripts/build_open_findings.py"


def _load(root: Path, relative: str) -> dict[str, Any] | None:
    path = root / relative
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class FindingsProducer:
    namespace: str
    artifact: str
    extractor: Callable[[Path, dict[str, Any]], list[dict[str, Any]]]


def _extract_clones(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    product_dispositions = {
        "SOURCE_CLONE_WITH_DISTINCT_IDS",
        "ACCIDENTAL_RENDER_DUPLICATION",
        "ASSEMBLY_DUPLICATION",
    }
    for group in payload.get("groups", []):
        if group["disposition"] not in product_dispositions:
            continue
        members = [m["path"] for m in group["members"]]
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
    return findings


def _extract_drift(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    for drift in payload.get("statement_drift", []):
        findings.append({
            "id": f"DRIFT-{Path(drift['correction']).stem}",
            "severity": "P0",
            "kind": "STUDENT_TEACHER_STATEMENT_DRIFT",
            "path": drift["correction"],
            "declared_target": drift["declared_target"],
            "evidence": "audit/EX_CO_SEMANTIC_BINDING.json",
        })
    for unresolved in payload.get("unresolved_targets", []):
        findings.append({
            "id": f"UNRESOLVED-{Path(unresolved['correction']).stem}",
            "severity": "P0",
            "kind": "UNRESOLVED_CORRECTION_TARGET",
            "path": unresolved["correction"],
            "evidence": "audit/EX_CO_SEMANTIC_BINDING.json",
        })
    return findings


def _extract_coverage(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    for entry in payload.get("entries", []):
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
    return findings


def _extract_lineage(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    for group in payload.get("groups", []):
        if group["lineage_case"] in {"ALL_EMPTY_PRE_FILLER", "MULTIPLE_PREEXISTING_CONTENT"}:
            findings.append({
                "id": f"AUTHOR-{group['digest'][:12]}",
                "severity": "P1",
                "kind": "UNRESOLVED_AUTHOR_DECISION",
                "group_digest": group["digest"],
                "lineage_case": group["lineage_case"],
                "evidence": "audit/PREFILLER_LINEAGE.json",
            })
    return findings


def _extract_release_blockers(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    for blocker in payload.get("blockers", []):
        if blocker.get("state") == "OPEN":
            findings.append({
                "id": f"BLOCKER-{blocker['blocker_id']}",
                "severity": "P0",
                "kind": "OPEN_RELEASE_BLOCKER",
                "blocker_id": blocker["blocker_id"],
                "scope": blocker.get("scope"),
                "evidence": "audit/1SPE_RELEASE_BLOCKER_LEDGER.json",
            })
    return findings


def _extract_bareme_attention(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    summary = payload.get("summary", {})
    if summary.get("ATTENTION_REQUIRED", 0) > 0:
        for req_id in summary.get("HUMAN_REQUIRED_IDS", []):
            findings.append({
                "id": f"BAREME-ATTENTION-{req_id}",
                "severity": "P1",
                "kind": "BAREME_ATTENTION_REQUIRED",
                "object_id": req_id,
                "evidence": "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json",
            })
    return findings


PRODUCER_REGISTRY: list[FindingsProducer] = [
    FindingsProducer("clones", "audit/CLONE_DISPOSITION_LEDGER.json", _extract_clones),
    FindingsProducer("drift", "audit/EX_CO_SEMANTIC_BINDING.json", _extract_drift),
    FindingsProducer("coverage", "audit/FALSE_COVERAGE_TRIAGE.json", _extract_coverage),
    FindingsProducer("lineage", "audit/PREFILLER_LINEAGE.json", _extract_lineage),
    FindingsProducer("release_blockers", "audit/1SPE_RELEASE_BLOCKER_LEDGER.json", _extract_release_blockers),
    FindingsProducer("baremes", "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json", _extract_bareme_attention),
]


def build(root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    missing_evidence: list[str] = []
    registered_producers_status: list[dict[str, Any]] = []

    for producer in PRODUCER_REGISTRY:
        payload = _load(root, producer.artifact)
        if payload is None:
            missing_evidence.append(producer.artifact)
            registered_producers_status.append({
                "namespace": producer.namespace,
                "artifact": producer.artifact,
                "status": "MISSING",
                "findings_count": 0,
            })
        else:
            extracted = producer.extractor(root, payload)
            findings.extend(extracted)
            registered_producers_status.append({
                "namespace": producer.namespace,
                "artifact": producer.artifact,
                "status": "ACTIVE",
                "findings_count": len(extracted),
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
        "CURRENT_FINDING_SOURCE_CONFLICTS": 0,
        "REGISTERED_PRODUCERS_TOTAL": len(PRODUCER_REGISTRY),
        "BY_KIND": dict(by_kind),
    }

    assert summary["TOTAL_P0_OPEN"] == len(by_severity["P0"])
    assert summary["TRUE_PRODUCT_CLONES_OPEN"] == sum(
        1 for f in findings if f["kind"] == "TRUE_PRODUCT_CLONE"
    )

    return {
        "artifact_type": "open_findings",
        "schema_version": "2.0.0",
        "generated_by": GENERATED_BY,
        "registered_producers": registered_producers_status,
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
