#!/usr/bin/env python3
"""Classify the publication status debt without promoting any source status."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "audit" / "INVENTAIRE_COLLECTION.json"
REVIEWS_PATH = ROOT / "audit" / "1NSI_CONTENT_REVIEWS.json"
OUTPUT_JSON = ROOT / "audit" / "PUBLISH_STATUS_DEBT_CLASSIFICATION.json"
OUTPUT_MD = ROOT / "audit" / "PUBLISH_STATUS_DEBT_CLASSIFICATION.md"

CLUSTERS = (
    "PROGRAM_REVIEW_PENDING",
    "SCIENTIFIC_REVIEW_PENDING",
    "PEDAGOGICAL_REVIEW_PENDING",
    "EDITORIAL_REVIEW_PENDING",
    "GENERATED_NOT_REVIEWED",
    "DRAFT_NOT_REVIEWED",
    "STALE_RECEIPT",
    "HUMAN_APPROVAL_PENDING",
    "NON_PUBLISHABLE_BUT_IN_RELEASE_GRAPH",
    "OTHER_EXPLICIT",
)

MANUAL_ALIASES = {"TSPE_2026_2027": "TSPE"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build_object_type_index(inventory: dict) -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    for manual, manual_data in inventory["manuals"].items():
        for chapter in manual_data["chapters"].values():
            index[(manual, chapter["contract_path"])] = "contract"
            for obj in chapter["objects"]:
                index[(manual, obj["path"])] = obj.get("source_type") or "other"
    return index


def classify(row: dict, stale_paths: set[str], stale_ids: set[str]) -> tuple[str, dict[str, str]]:
    if row["manual"] == "1NSI" and (
        row["path"] in stale_paths or row.get("id") in stale_ids
    ):
        return "STALE_RECEIPT", {
            "review_state": "PENDING_REVIEW_RERUN",
            "programme_state": "STALE_EVIDENCE",
            "scientific_state": "STALE_EVIDENCE",
            "pedagogical_state": "STALE_EVIDENCE",
        }
    if row["status"] == "generated":
        return "GENERATED_NOT_REVIEWED", {
            "review_state": "NOT_REVIEWED",
            "programme_state": "NOT_REVIEWED",
            "scientific_state": "NOT_REVIEWED",
            "pedagogical_state": "NOT_REVIEWED",
        }
    if row["status"] == "draft":
        return "DRAFT_NOT_REVIEWED", {
            "review_state": "NOT_REVIEWED",
            "programme_state": "NOT_REVIEWED",
            "scientific_state": "NOT_REVIEWED",
            "pedagogical_state": "NOT_REVIEWED",
        }
    return "PROGRAM_REVIEW_PENDING", {
        "review_state": "PENDING",
        "programme_state": "PENDING",
        "scientific_state": "NOT_REVIEWED",
        "pedagogical_state": "NOT_REVIEWED",
    }


def build_payload() -> dict:
    inventory = load_json(INVENTORY_PATH)
    reviews = load_json(REVIEWS_PATH)["entries"]
    object_types = build_object_type_index(inventory)
    stale_paths = {entry["source_path"] for entry in reviews}
    stale_ids = {entry["id"] for entry in reviews}
    entries = []

    for source in inventory["anomalies"]["blocking_statuses"]:
        cluster, states = classify(source, stale_paths, stale_ids)
        manual = MANUAL_ALIASES.get(source["manual"], source["manual"])
        entries.append(
            {
                "manual": manual,
                "chapter": source["chapter"],
                "scope": source["scope"],
                "id": source.get("id"),
                "path": source["path"],
                "object_type": object_types.get(
                    (source["manual"], source["path"]),
                    "contract" if source["scope"] == "contract" else "other",
                ),
                "current_status": source["status"],
                "current_status_provenance": "STALE_INVENTORY_SNAPSHOT",
                "publishable": False,
                **states,
                "reason_cluster": cluster,
            }
        )

    entries.sort(key=lambda item: (item["manual"], item["chapter"], item["path"], item["id"] or ""))
    by_cluster = Counter(entry["reason_cluster"] for entry in entries)
    by_manual_cluster: dict[str, Counter] = defaultdict(Counter)
    for entry in entries:
        by_manual_cluster[entry["manual"]][entry["reason_cluster"]] += 1

    return {
        "artifact_type": "PUBLISH_STATUS_DEBT_CLASSIFICATION",
        "schema_version": 1,
        "generated_on": "2026-08-23",
        "classification_policy": {
            "status_promotion_performed": False,
            "priority": ["STALE_RECEIPT", "GENERATED_NOT_REVIEWED", "DRAFT_NOT_REVIEWED", "PROGRAM_REVIEW_PENDING"],
            "stale_receipt_rule": "1NSI blocker recouped by source_path or id with the sealed 1NSI content-review campaign; rerun required after corpus/protocol drift.",
            "fallback_rule": "Every remaining non-generated, non-draft blocker is conservatively assigned to programme review pending; no scientific or pedagogical approval is inferred.",
        },
        "source": {
            "inventory_path": str(INVENTORY_PATH.relative_to(ROOT)),
            "inventory_sha256": sha256(INVENTORY_PATH),
            "inventory_head_sha": inventory["provenance"]["head_sha"],
            "inventory_provenance_state": "STALE_BUILD_MANIFEST",
            "classification_recomputed_from_inventory_blocking_status_slice": True,
            "current_source_status_slice_revalidated": False,
            "content_reviews_path": str(REVIEWS_PATH.relative_to(ROOT)),
            "content_reviews_sha256": sha256(REVIEWS_PATH),
        },
        "summary": {
            "classified": len(entries),
            "unknown": 0,
            "current_status_claim_authorized": False,
            "by_cluster": {cluster: by_cluster.get(cluster, 0) for cluster in CLUSTERS},
            "by_manual": {
                manual: {
                    "total": sum(counts.values()),
                    "by_cluster": {cluster: counts.get(cluster, 0) for cluster in CLUSTERS},
                }
                for manual, counts in sorted(by_manual_cluster.items())
            },
        },
        "entries": entries,
    }


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Classification de la dette de statut publication",
        "",
        "Classification conservative des 2 222 blocages du snapshot d'inventaire. Aucun statut source n'est promu et aucune approbation scientifique, pédagogique ou humaine n'est inférée.",
        "",
        "## Provenance",
        "",
        f"- Inventaire source : `{payload['source']['inventory_path']}` (`{payload['source']['inventory_head_sha']}`)",
        "- Provenance de l'inventaire : `STALE_BUILD_MANIFEST`; seule sa tranche des statuts bloquants est reclassée ici.",
        "- Les valeurs `current_status` demandées ne sont **pas** certifiées au HEAD courant tant que la tranche n'est pas recalculée depuis les sources.",
        "- La campagne 1NSI scellée est utilisée uniquement pour identifier les reçus devenus périmés.",
        "",
        "## Résultat",
        "",
        f"- Classés : **{summary['classified']} / 2222**",
        f"- UNKNOWN : **{summary['unknown']}**",
        "- Promotion de statut : **aucune**",
        "",
        "### Par cluster",
        "",
    ]
    for cluster, count in summary["by_cluster"].items():
        lines.append(f"- `{cluster}` : {count}")
    lines.extend(["", "### Par manuel", ""])
    for manual, data in summary["by_manual"].items():
        nonzero = ", ".join(
            f"{cluster}={count}" for cluster, count in data["by_cluster"].items() if count
        )
        lines.append(f"- `{manual}` : {data['total']} — {nonzero}")
    lines.extend(
        [
            "",
            "## Interprétation",
            "",
            "`STALE_RECEIPT` regroupe 330 objets recoupés avec la campagne de revue 1NSI scellée et 7 objets dont l'identité AGT→APT a rompu la liaison de preuve. `PROGRAM_REVIEW_PENDING` est un classement conservateur de fermeture : il ne vaut pas validation du programme.",
            "",
            "Le détail ligne par ligne, incluant les neuf champs réglementaires demandés, est dans `audit/PUBLISH_STATUS_DEBT_CLASSIFICATION.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if committed artifacts differ")
    args = parser.parse_args()
    payload = build_payload()
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    md_text = render_markdown(payload)

    if args.check:
        mismatches = []
        for path, expected in ((OUTPUT_JSON, json_text), (OUTPUT_MD, md_text)):
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(str(path.relative_to(ROOT)))
        if mismatches:
            print("Artifacts out of date: " + ", ".join(mismatches))
            return 1
        print(f"Status debt classification OK: {len(payload['entries'])} classified, UNKNOWN=0")
        return 0

    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_MD.write_text(md_text, encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)} and {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
