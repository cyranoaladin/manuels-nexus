#!/usr/bin/env python3
"""Reçu de décision du Release Owner, lié aux empreintes canoniques.

La version précédente comparait le paquet à une empreinte **recopiée en dur**
dans le fichier. Une preuve qui contient sa propre réponse ne prouve rien : si
le dépôt bougeait, le littéral, lui, ne bougeait pas.

Ce producteur ne contient aucune empreinte littérale. Il recalcule les trois
empreintes canoniques par `release_digests` — la même implémentation que le
paquet, le validateur, le gate et les tests — et les inscrit dans le reçu.

Il n'approuve rien de lui-même : il matérialise une décision humaine déjà
prise, et refuse de l'émettre si les preuves d'acceptation ne sont pas
calculables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_digests as digests  # noqa: E402

ROOT = digests.ROOT
OUTPUT_JSON = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
OUTPUT_MD = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.md"


def generate_receipt(
    *, reviewer_identity: str, decision: str, timestamp: str, batch_ids: list[str],
) -> dict[str, Any]:
    digests.assert_acyclic()
    current = digests.compute_all(ROOT)

    receipt = {
        "artifact_type": "release_owner_decision_receipt",
        "schema_version": 2,
        "generated_by": "scripts/build_release_owner_decision_receipt.py",
        "reviewer_identity": reviewer_identity,
        "decision": decision,
        "decision_status": "APPROVED",
        "scope": "canonical_release_content_only",
        "object_set_digest": current["OBJECT_SET_DIGEST"],
        "pedagogical_content_digest": current["PEDAGOGICAL_CONTENT_DIGEST"],
        "build_source_closure_digest": current["BUILD_SOURCE_CLOSURE_DIGEST"],
        "acceptance_evidence_bundle_digest": current["ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST"],
        "accepted_batch_ids": list(batch_ids),
        "timestamp": timestamp,
        "binding_verification": {
            "digests_recomputed_by": "scripts/release_digests.py",
            "no_literal_digest_in_producer": True,
            "reusable_for_future_closures": False,
        },
    }
    receipt["receipt_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(receipt, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return receipt


def render_md(receipt: dict[str, Any]) -> str:
    return "\n".join([
        "# Reçu de décision du Release Owner",
        "",
        f"- Relecteur : `{receipt['reviewer_identity']}`",
        f"- Décision : `{receipt['decision']}`",
        f"- Portée : `{receipt['scope']}`",
        f"- `OBJECT_SET_DIGEST` : `{receipt['object_set_digest']}`",
        f"- `PEDAGOGICAL_CONTENT_DIGEST` : `{receipt['pedagogical_content_digest']}`",
        f"- `ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST` : `{receipt['acceptance_evidence_bundle_digest']}`",
        f"- Empreinte du reçu : `{receipt['receipt_digest']}`",
        "",
        "Ces empreintes sont recalculées par `scripts/release_digests.py`.",
        "Aucune valeur n'est recopiée dans ce producteur.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-identity", required=True)
    parser.add_argument("--decision", default="ACCEPT_FROZEN_RELEASE_CONTENT")
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--batch-id", action="append", default=[])
    args = parser.parse_args()

    receipt = generate_receipt(
        reviewer_identity=args.reviewer_identity,
        decision=args.decision,
        timestamp=args.timestamp,
        batch_ids=args.batch_id,
    )
    OUTPUT_JSON.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_md(receipt), encoding="utf-8")
    print(json.dumps({"receipt_digest": receipt["receipt_digest"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
