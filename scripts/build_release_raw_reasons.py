#!/usr/bin/env python3
"""Inventaire brut et taxonomie dérivée des motifs de blocage de release.

Remplace `BLOCKER_TAXONOMY`, dont la liste de bloqueurs était écrite en dur
(deux items) : `PRODUCT_P0_COUNT = 0` y était une tautologie, pas une mesure.

Ici, chaque motif provient d'un producteur réel. Deux notions distinctes :

* `RAW_REASONS`    — un motif tel que le gate l'émet (`555` aujourd'hui) ;
* `ROOT_BLOCKERS`  — la cause dont plusieurs motifs sont des symptômes.

Fail-closed : un motif qu'aucune règle ne reconnaît est compté dans
`UNMAPPED_RAW_REASONS`, jamais silencieusement écarté.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit/RELEASE_RAW_REASONS.json"
OUTPUT_MD = ROOT / "audit/RELEASE_RAW_REASONS.md"

TAXONOMIES = (
    "PRODUCT_P0",
    "PRODUCT_P1",
    "PRODUCT_P2",
    "CERTIFICATION_BLOCKER",
    "RELEASE_POLICY_BLOCKER",
    "GOVERNANCE_BLOCKER",
)

# (regex, taxonomie, producteur, identifiant de cause racine)
#
# Produit      : quelque chose est faux/absent/incomplet dans le manuel.
# Certification: le produit peut être bon, mais la preuve manque ou est stale.
# Release policy: produit et preuve bons, condition formelle de promotion ouverte.
# Gouvernance  : décision humaine pure, contenu et preuve déjà validés.
RULES: tuple[tuple[str, str, str, str], ...] = (
    (r"^qualification_invalide:(?P<fp>[0-9a-f]+):(?P<msg>.*)$",
     "CERTIFICATION_BLOCKER", "inventory_collection.invalid_qualifications",
     "ROOT-QUALIFICATION-STALE"),
    (r"^qualifications_illisibles:(?P<msg>.*)$",
     "CERTIFICATION_BLOCKER", "inventory_collection.invalid_qualifications",
     "ROOT-QUALIFICATION-UNREADABLE"),

    (r"^CONTENT:(?P<chapter>[^:]+):assessments:GAP$",
     "PRODUCT_P1", "build_publish_readiness_chapter_matrix", "ROOT-ASSESSMENT-COVERAGE"),
    (r"^CONTENT:(?P<chapter>[^:]+):qcm:GAP$",
     "PRODUCT_P1", "build_qcm_gap_metrics", "ROOT-QCM-COVERAGE"),
    (r"^CONTENT:(?P<chapter>[^:]+):ex_co_graph:GAP$",
     "PRODUCT_P1", "build_ex_co_graph", "ROOT-EXERCISE-CORRECTION-GRAPH"),
    (r"^CONTENT:(?P<chapter>[^:]+):ex_co_graph:NOT_AUDITED$",
     "CERTIFICATION_BLOCKER", "build_ex_co_graph", "ROOT-EXERCISE-CORRECTION-GRAPH-NOT-AUDITED"),
    (r"^CONTENT:(?P<chapter>[^:]+):pedagogical_role_coverage:GAP$",
     "PRODUCT_P1", "build_true_pedagogical_coverage", "ROOT-PEDAGOGICAL-ROLE-COVERAGE"),
    (r"^CONTENT:(?P<chapter>[^:]+):pedagogical_richness:GAP$",
     "PRODUCT_P2", "build_chapter_richness_matrix", "ROOT-PEDAGOGICAL-RICHNESS"),
    (r"^CONTENT:(?P<chapter>[^:]+):course_assembly_truth:GAP$",
     "PRODUCT_P1", "build_course_assembly_truth", "ROOT-COURSE-ASSEMBLY"),
    (r"^CONTENT:(?P<chapter>[^:]+):oracle:GAP$",
     "CERTIFICATION_BLOCKER", "build_qcm_independent_evidence_v2", "ROOT-ORACLE-EVIDENCE"),
    (r"^CONTENT:(?P<chapter>[^:]+):oracle:NO_RECEIPTS$",
     "CERTIFICATION_BLOCKER", "build_qcm_independent_evidence_v2", "ROOT-ORACLE-EVIDENCE"),
    (r"^CONTENT:(?P<chapter>[^:]+):cross_discipline_content:NOT_AUDITED$",
     "CERTIFICATION_BLOCKER", "build_nsi_cross_discipline_ledger", "ROOT-CROSS-DISCIPLINE-AUDIT"),
    (r"^CONTENT:(?P<chapter>[^:]+):vertical_machine_status:INCOMPLETE$",
     "CERTIFICATION_BLOCKER", "build_publish_readiness_chapter_matrix", "ROOT-VERTICAL-MACHINE-STATUS"),

    (r"^CONTENT_PRODUCER_STALE_OR_RED:(?P<producer>[^:]+):rc=(?P<rc>\d+)$",
     "CERTIFICATION_BLOCKER", "inventory_collection.content_integrity", "ROOT-PRODUCER-STALE"),
    (r"^CONTENT_MATRIX:(?P<key>[^:]+):(?P<value>.*)$",
     "CERTIFICATION_BLOCKER", "inventory_collection.content_integrity", "ROOT-CONTENT-MATRIX-INCOMPLETE"),

    (r"^HUMAN_REVIEW_PENDING:(?P<chapter>.+)$",
     "CERTIFICATION_BLOCKER", "build_human_review_queue", "ROOT-HUMAN-REVIEW-QUEUE"),
    (r"^HUMAN_REVIEW_QUEUE_OPEN:(?P<count>\d+)$",
     "CERTIFICATION_BLOCKER", "build_human_review_queue", "ROOT-HUMAN-REVIEW-QUEUE"),

    (r"^(?P<manual>[A-Z0-9_]+):chapitres_manquants:(?P<source>[^:]+):(?P<detail>.*)$",
     "PRODUCT_P0", "inventory_collection.deliverable_matrix", "ROOT-MISSING-CHAPTERS"),
    (r"^(?P<manual>[A-Z0-9_]+):livrable_non_compile:(?P<source>[^:]+):(?P<detail>.*)$",
     "PRODUCT_P1", "inventory_collection.deliverable_matrix", "ROOT-DELIVERABLE-NOT-COMPILED"),
    (r"^(?P<manual>[A-Z0-9_]+):assemblage_déclaré_absent:(?P<variant>.+)$",
     "PRODUCT_P1", "inventory_collection.deliverable_matrix", "ROOT-DELIVERABLE-NOT-DECLARED"),
    (r"^(?P<manual>[A-Z0-9_]+):build_observé_absent:(?P<variant>.+)$",
     "PRODUCT_P1", "inventory_collection.observed_build_coverage", "ROOT-DELIVERABLE-NOT-BUILT"),
    (r"^(?P<manual>[A-Z0-9_]+):statuts_non_approuves:(?P<source>[^:]+):(?P<detail>.*)$",
     "GOVERNANCE_BLOCKER", "inventory_collection.statuses", "ROOT-NON-APPROVED-STATUSES"),
    (r"^(?P<manual>[A-Z0-9_]+):anomalie:blocking_statuses:(?P<source>[^:]+):(?P<count>\d+)$",
     "GOVERNANCE_BLOCKER", "inventory_collection.anomalies", "ROOT-NON-APPROVED-STATUSES"),

    (r"^COLLECTION:publication_snapshots:(?P<state>[^:]+):(?P<count>\d+)$",
     "RELEASE_POLICY_BLOCKER", "inventory_collection.collection_blockers", "ROOT-PUBLICATION-SNAPSHOT-UNDECIDED"),
    (r"^COLLECTION:(?P<code>[^:]+):(?P<source>[^:]+):(?P<detail>.*)$",
     "RELEASE_POLICY_BLOCKER", "inventory_collection.collection_blockers", "ROOT-COLLECTION-POLICY"),

    (r"^dimension_non_couverte:(?P<dimension>.+)$",
     "CERTIFICATION_BLOCKER", "inventory_collection.gate_dimensions", "ROOT-DIMENSION-NOT-COVERED"),
    (r"^build_receipt_producteurs_non_intégrés$",
     "CERTIFICATION_BLOCKER", "inventory_collection.observed_build_integration", "ROOT-BUILD-RECEIPT-NOT-INTEGRATED"),
    (r"^check_error:(?P<msg>.*)$",
     "CERTIFICATION_BLOCKER", "inventory_collection", "ROOT-GATE-CHECK-ERROR"),
    (r"^inventaire_indisponible:(?P<msg>.*)$",
     "CERTIFICATION_BLOCKER", "inventory_collection", "ROOT-INVENTORY-UNAVAILABLE"),
)

ROOT_BLOCKER_TITLES = {
    "ROOT-QUALIFICATION-STALE": "Qualifications dérivées invalidées par une mutation de source",
    "ROOT-QUALIFICATION-UNREADABLE": "Qualifications illisibles",
    "ROOT-ASSESSMENT-COVERAGE": "Couverture d'évaluations incomplète",
    "ROOT-QCM-COVERAGE": "Couverture QCM incomplète",
    "ROOT-EXERCISE-CORRECTION-GRAPH": "Graphe exercice/corrigé incomplet",
    "ROOT-EXERCISE-CORRECTION-GRAPH-NOT-AUDITED": "Graphe exercice/corrigé non audité",
    "ROOT-PEDAGOGICAL-ROLE-COVERAGE": "Rôles pédagogiques non couverts",
    "ROOT-PEDAGOGICAL-RICHNESS": "Richesse pédagogique insuffisante",
    "ROOT-COURSE-ASSEMBLY": "Assemblage de cours incomplet",
    "ROOT-ORACLE-EVIDENCE": "Preuve oracle QCM absente",
    "ROOT-CROSS-DISCIPLINE-AUDIT": "Contenu inter-disciplinaire non audité",
    "ROOT-VERTICAL-MACHINE-STATUS": "Chaîne machine verticale incomplète",
    "ROOT-PRODUCER-STALE": "Producteurs de preuve stale ou rouges",
    "ROOT-CONTENT-MATRIX-INCOMPLETE": "Matrice de contenu machine incomplète",
    "ROOT-HUMAN-REVIEW-QUEUE": "File de revue humaine ouverte",
    "ROOT-MISSING-CHAPTERS": "Chapitres attendus absents de l'inventaire",
    "ROOT-DELIVERABLE-NOT-COMPILED": "Livrables déclarés non compilés",
    "ROOT-DELIVERABLE-NOT-DECLARED": "Assemblages de variantes non déclarés",
    "ROOT-DELIVERABLE-NOT-BUILT": "Variantes déclarées jamais construites",
    "ROOT-NON-APPROVED-STATUSES": "Objets et contrats non approuvés",
    "ROOT-PUBLICATION-SNAPSHOT-UNDECIDED": "Snapshots de publication non arbitrés",
    "ROOT-COLLECTION-POLICY": "Règle de collection non satisfaite",
    "ROOT-DIMENSION-NOT-COVERED": "Dimensions de certification sans preuve",
    "ROOT-BUILD-RECEIPT-NOT-INTEGRATED": "Reçus de build non intégrés",
    "ROOT-GATE-CHECK-ERROR": "Erreur fatale de contrôle du gate",
    "ROOT-INVENTORY-UNAVAILABLE": "Inventaire indisponible",
}


def classify(reason: str) -> dict[str, Any] | None:
    for pattern, taxonomy, producer, root_cause_id in RULES:
        match = re.match(pattern, reason)
        if match:
            groups = match.groupdict()
            target = (
                groups.get("chapter")
                or groups.get("manual")
                or groups.get("producer")
                or groups.get("dimension")
                or groups.get("fp")
                or groups.get("code")
                or groups.get("key")
                or "COLLECTION"
            )
            return {
                "reason_id": "RSN-" + hashlib.sha256(reason.encode("utf-8")).hexdigest()[:16],
                "producer": producer,
                "target": target,
                "object_id": groups.get("fp"),
                "category": taxonomy,
                "evidence": reason,
                "status": "OPEN",
                "root_cause_id": root_cause_id,
            }
    return None


def build(gate_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Union des motifs observés, chaque motif gardant sa provenance.

    Un gate s'arrête au premier étage qui échoue : une seule exécution ne voit
    donc jamais l'ensemble des motifs. On agrège plusieurs observations réelles
    plutôt que d'en inventer une synthétique, et chaque motif porte le nom de
    l'exécution qui l'a produit.
    """
    raw_reasons: list[dict[str, Any]] = []
    unmapped: list[str] = []
    seen: dict[str, dict[str, Any]] = {}

    for payload in gate_payloads:
        provenance = payload.get("observation_id") or payload.get("gate", "?")
        for reason in payload.get("reasons", []):
            text = str(reason)
            entry = classify(text)
            if entry is None:
                if text not in unmapped:
                    unmapped.append(text)
                continue
            if entry["reason_id"] in seen:
                seen[entry["reason_id"]]["observed_in"].append(provenance)
                continue
            entry["observed_in"] = [provenance]
            seen[entry["reason_id"]] = entry
            raw_reasons.append(entry)

    ids = Counter(entry["reason_id"] for entry in raw_reasons)
    duplicates = sorted(rid for rid, count in ids.items() if count > 1)

    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in raw_reasons:
        grouped[entry["root_cause_id"]].append(entry["reason_id"])

    root_blockers = []
    for root_id, reason_ids in sorted(grouped.items()):
        taxonomies = {
            entry["category"] for entry in raw_reasons if entry["root_cause_id"] == root_id
        }
        if len(taxonomies) != 1:
            raise SystemExit(
                f"BLOCKER_CLASSIFICATION_CONFLICT: {root_id} -> {sorted(taxonomies)}"
            )
        root_blockers.append({
            "root_blocker_id": root_id,
            "title": ROOT_BLOCKER_TITLES.get(root_id, root_id),
            "taxonomy": taxonomies.pop(),
            "dependent_reason_count": len(reason_ids),
            "dependent_reason_ids": sorted(reason_ids),
        })

    per_taxonomy = Counter(b["taxonomy"] for b in root_blockers)
    conflicts = [b for b in root_blockers if b["taxonomy"] not in TAXONOMIES]

    summary = {
        "RAW_REASON_COUNT": len(raw_reasons),
        "ROOT_BLOCKER_COUNT": len(root_blockers),
        "UNMAPPED_RAW_REASONS": len(unmapped),
        "DUPLICATE_REASON_IDS": len(duplicates),
        "BLOCKER_CLASSIFICATION_CONFLICTS": len(conflicts),
        "PRODUCT_P0": per_taxonomy.get("PRODUCT_P0", 0),
        "PRODUCT_P1": per_taxonomy.get("PRODUCT_P1", 0),
        "PRODUCT_P2": per_taxonomy.get("PRODUCT_P2", 0),
        "CERTIFICATION_BLOCKERS": per_taxonomy.get("CERTIFICATION_BLOCKER", 0),
        "RELEASE_POLICY_BLOCKERS": per_taxonomy.get("RELEASE_POLICY_BLOCKER", 0),
        "GOVERNANCE_BLOCKERS": per_taxonomy.get("GOVERNANCE_BLOCKER", 0),
        "RAW_REASONS_BY_TAXONOMY": dict(
            Counter(entry["category"] for entry in raw_reasons)
        ),
    }

    return {
        "artifact_type": "release_raw_reasons",
        "schema_version": 2,
        "generated_by": "scripts/build_release_raw_reasons.py",
        "gate_observations": [
            {
                "observation_id": p.get("observation_id"),
                "gate": p.get("gate"),
                "exit_code": p.get("exit_code"),
                "success": p.get("success"),
                "reason_count": len(p.get("reasons", [])),
            }
            for p in gate_payloads
        ],
        "summary": summary,
        "root_blockers": root_blockers,
        "unmapped_raw_reasons": sorted(unmapped),
        "raw_reasons": sorted(raw_reasons, key=lambda e: (e["root_cause_id"], e["evidence"])),
    }


def render_md(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Motifs bruts et bloqueurs racines de la release",
        "",
        "Dérivé intégralement du gate `release-strict`. Aucun compte n'est écrit en dur.",
        "",
        f"- Motifs bruts (`RAW_REASON_COUNT`) : `{s['RAW_REASON_COUNT']}`",
        f"- Bloqueurs racines (`ROOT_BLOCKER_COUNT`) : `{s['ROOT_BLOCKER_COUNT']}`",
        f"- Motifs non classés (`UNMAPPED_RAW_REASONS`) : `{s['UNMAPPED_RAW_REASONS']}`",
        f"- Identifiants dupliqués (`DUPLICATE_REASON_IDS`) : `{s['DUPLICATE_REASON_IDS']}`",
        f"- Conflits de classification : `{s['BLOCKER_CLASSIFICATION_CONFLICTS']}`",
        "",
        "| Taxonomie | Bloqueurs racines |",
        "|---|---|",
        f"| `PRODUCT_P0` | {s['PRODUCT_P0']} |",
        f"| `PRODUCT_P1` | {s['PRODUCT_P1']} |",
        f"| `PRODUCT_P2` | {s['PRODUCT_P2']} |",
        f"| `CERTIFICATION_BLOCKER` | {s['CERTIFICATION_BLOCKERS']} |",
        f"| `RELEASE_POLICY_BLOCKER` | {s['RELEASE_POLICY_BLOCKERS']} |",
        f"| `GOVERNANCE_BLOCKER` | {s['GOVERNANCE_BLOCKERS']} |",
        "",
        "## Bloqueurs racines",
        "",
        "| ID | Taxonomie | Titre | Motifs dépendants |",
        "|---|---|---|---|",
    ]
    for blocker in payload["root_blockers"]:
        lines.append(
            f"| `{blocker['root_blocker_id']}` | `{blocker['taxonomy']}` | "
            f"{blocker['title']} | {blocker['dependent_reason_count']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-gate-json",
        type=Path,
        action="append",
        required=True,
        metavar="OBSERVATION_ID=PATH",
        help=(
            "observation réelle du gate, sous la forme id=chemin ; répétable, "
            "car un gate s'arrête au premier étage en échec"
        ),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payloads = []
    for item in args.from_gate_json:
        observation_id, _, path = str(item).partition("=")
        if not path:
            observation_id, path = "observation", observation_id
        loaded = json.loads(Path(path).read_text(encoding="utf-8"))
        loaded["observation_id"] = observation_id
        payloads.append(loaded)
    payload = build(payloads)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendered:
            print("RELEASE_RAW_REASONS check: OK")
            return 0
        print("RELEASE_RAW_REASONS check: STALE")
        return 1

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
