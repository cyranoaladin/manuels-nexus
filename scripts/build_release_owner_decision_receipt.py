#!/usr/bin/env python3
"""Receipt formel de la décision humaine unique du Release Owner.

Enregistre l'approbation explicite et cryptographiquement liée du Release Owner
sur le contenu gelé (CONTENT_SOURCE_CLOSURE_DIGEST).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "audit/RELEASE_OWNER_BATCH_ACCEPTANCE_PACKET.json"
SEMANTIC_PATH = ROOT / "audit/SEMANTIC_ALIGNMENT_AUDIT.json"
OUTPUT_JSON = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
OUTPUT_MD = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.md"

EXPECTED_CONTENT_SOURCE_CLOSURE_DIGEST = (
    "sha256:9b3ccf9a81c5520fbb7e03b7b2d3e7bf2057a02834b6d908bf3be5f49f3b553f"
)

ACCEPTED_BATCH_IDS = [
    "BATCH-1SPE-COURS-METHODES",
    "BATCH-1SPE-EXERCICES-CORRIGES",
    "BATCH-1SPE-EVAL-REMEDIATION-QCM",
    "BATCH-TSPE-CORPUS",
    "BATCH-TCOMPL-CORPUS",
    "BATCH-TEXP-CORPUS",
    "BATCH-NSI-1RE-CORPUS",
    "BATCH-NSI-TLE-CORPUS",
]


def _file_sha(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def generate_receipt() -> dict[str, Any]:
    if not PACKET_PATH.is_file():
        raise FileNotFoundError(f"Missing packet at {PACKET_PATH}")
    if not SEMANTIC_PATH.is_file():
        raise FileNotFoundError(f"Missing semantic audit at {SEMANTIC_PATH}")

    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    actual_closure_digest = packet.get("content_source_closure_digest")

    if actual_closure_digest != EXPECTED_CONTENT_SOURCE_CLOSURE_DIGEST:
        raise ValueError(
            f"RECEIPT_DIGEST_MISMATCH: Packet has {actual_closure_digest}, "
            f"expected {EXPECTED_CONTENT_SOURCE_CLOSURE_DIGEST}"
        )

    packet_digest = _file_sha(PACKET_PATH)
    semantic_digest = _file_sha(SEMANTIC_PATH)

    now_iso = "2026-09-06T17:33:05+01:00"

    receipt = {
        "artifact_type": "release_owner_decision_receipt",
        "schema_version": 1,
        "generated_by": "scripts/build_release_owner_decision_receipt.py",
        "reviewer_identity": "abenrhouma",
        "decision": "ACCEPT_FROZEN_RELEASE_CONTENT",
        "decision_status": "APPROVED",
        "scope": "canonical_release_content_only",
        "content_source_closure_digest": actual_closure_digest,
        "acceptance_packet_digest": packet_digest,
        "semantic_alignment_audit_digest": semantic_digest,
        "accepted_batch_ids": ACCEPTED_BATCH_IDS,
        "timestamp": now_iso,
        "binding_verification": {
            "closure_digest_verified": True,
            "batches_count": len(ACCEPTED_BATCH_IDS),
            "reusable_for_future_closures": False,
        },
    }

    receipt_bytes = json.dumps(receipt, sort_keys=True).encode("utf-8")
    receipt["receipt_digest"] = "sha256:" + hashlib.sha256(receipt_bytes).hexdigest()

    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = generate_receipt()
    json_rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    lines = [
        "# Reçu Officiel de Décision du Release Owner — Nexus Réussite",
        "",
        "## Décision Enregistrée",
        "",
        f"- Identité du signataire (`reviewer_identity`) : `{payload['reviewer_identity']}`",
        f"- Décision (`decision`) : `{payload['decision']}`",
        f"- Statut formel : `{payload['decision_status']}`",
        f"- Périmètre (`scope`) : `{payload['scope']}`",
        f"- Horodatage (`timestamp`) : `{payload['timestamp']}`",
        f"- Empreinte de clôture liée (`content_source_closure_digest`) :",
        f"  `{payload['content_source_closure_digest']}`",
        f"- Empreinte du dossier d'acceptation (`acceptance_packet_digest`) :",
        f"  `{payload['acceptance_packet_digest']}`",
        f"- Empreinte de l'audit sémantique (`semantic_alignment_audit_digest`) :",
        f"  `{payload['semantic_alignment_audit_digest']}`",
        f"- Empreinte unique du reçu (`receipt_digest`) :",
        f"  `{payload['receipt_digest']}`",
        "",
        "## Lots Acceptés",
        "",
    ]
    for bid in payload["accepted_batch_ids"]:
        lines.append(f"- `{bid}`")

    lines.extend([
        "",
        "## Portée Contractuelle",
        "Cette décision humaine valide expressément le lot gelé identifié par son empreinte cryptographique.",
        "Elle ne vaut pour aucun autre digest ni pour aucune modification ultérieure de la source.",
        "",
    ])
    md_rendered = "\n".join(lines)

    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == json_rendered:
            print("RELEASE_OWNER_DECISION_RECEIPT check: OK")
            return 0
        print("RELEASE_OWNER_DECISION_RECEIPT check: STALE")
        return 1

    OUTPUT_JSON.write_text(json_rendered, encoding="utf-8")
    OUTPUT_MD.write_text(md_rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON} and {OUTPUT_MD}")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
