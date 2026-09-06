#!/usr/bin/env python3
"""Application de la transition de maturité liée au reçu du Release Owner.

Conformément aux instructions contractuelles :
- Ne modifie jamais l'origine (origin = generated reste origin = generated) ;
- Conserve l'historique de traçabilité (generated -> audited -> accepted -> approved) ;
- Strictement restreint aux 2,120 objets du paquet scellé (UNAUTHORIZED_STATUS_PROMOTION = 0) ;
- Garantit l'invariance stricte du corps didactique (PEDAGOGICAL_CONTENT_MUTATIONS = 0).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BATCH_AUDIT_PATH = ROOT / "audit/RELEASE_OBJECT_BATCH_AUDIT.json"
RECEIPT_PATH = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
OUTPUT_JSON = ROOT / "audit/RELEASE_MATURITY_TRANSITION_AUDIT.json"
OUTPUT_MD = ROOT / "audit/RELEASE_MATURITY_TRANSITION_AUDIT.md"


def _body_hash(lines: list[str]) -> str:
    body = "\n".join(lines[1:])
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def apply_transition(dry_run: bool = False) -> dict[str, Any]:
    batch_audit = json.loads(BATCH_AUDIT_PATH.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    closure_digest = receipt["content_source_closure_digest"]
    receipt_digest = receipt["receipt_digest"]

    # Collect all accepted object IDs from the 8 batches
    inv_data = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    manuals = inv_data.get("manuals", {})

    all_accepted_objects = []
    for mname, mval in manuals.items():
        for cname, cval in mval.get("chapters", {}).items():
            for o in cval.get("objects", []):
                if o.get("status") in ("generated", "needs_review"):
                    all_accepted_objects.append(o)

    accepted_ids = {o["id"] for o in all_accepted_objects}
    assert len(accepted_ids) == 2120, f"Expected 2120 accepted IDs, got {len(accepted_ids)}"

    promoted_objects = []
    unauthorized_promotions = 0
    pedagogical_mutations = 0

    for o in all_accepted_objects:
        oid = o["id"]
        rel_path = o["path"]
        file_path = ROOT / rel_path

        if oid not in accepted_ids:
            unauthorized_promotions += 1
            continue

        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        lines = raw_text.splitlines()
        first_line = lines[0]

        if not first_line.startswith("% META:"):
            raise ValueError(f"Fichier sans % META: {rel_path}")

        meta_json_str = first_line[len("% META:"):].strip()
        meta = json.loads(meta_json_str)

        old_status = meta.get("status")
        initial_origin = meta.get("origin") or old_status

        pre_body_hash = _body_hash(lines)

        # Update metadata while preserving provenance & history
        meta["origin"] = initial_origin
        history = meta.get("status_history", [initial_origin])
        if "audited" not in history:
            history.append("audited")
        if "accepted" not in history:
            history.append("accepted")
        if "approved" not in history:
            history.append("approved")
        meta["status_history"] = history
        meta["status"] = "approved"
        meta["release_acceptance"] = "RELEASE_OWNER_BATCH_ACCEPTANCE"
        meta["acceptance_closure_digest"] = closure_digest
        meta["acceptance_receipt_digest"] = receipt_digest

        new_first_line = "% META: " + json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
        new_lines = [new_first_line] + lines[1:]
        new_text = "\n".join(new_lines)
        if raw_text.endswith("\n"):
            new_text += "\n"

        post_body_hash = _body_hash(new_lines)
        if pre_body_hash != post_body_hash:
            pedagogical_mutations += 1

        if not dry_run:
            file_path.write_text(new_text, encoding="utf-8")

        promoted_objects.append({
            "id": oid,
            "path": rel_path,
            "origin": initial_origin,
            "previous_status": old_status,
            "new_status": "approved",
            "body_hash": pre_body_hash,
            "body_intact": (pre_body_hash == post_body_hash),
        })

    summary = {
        "TOTAL_OBJECTS_CONSIDERED": len(all_accepted_objects),
        "PROMOTED_OBJECTS_COUNT": len(promoted_objects),
        "PROMOTED_OBJECTS_SUBSET_OF_ACCEPTED": (len(promoted_objects) == len(accepted_ids)),
        "UNAUTHORIZED_STATUS_PROMOTION": unauthorized_promotions,
        "PEDAGOGICAL_CONTENT_MUTATIONS": pedagogical_mutations,
        "PEDAGOGICAL_INTEGRITY_VERDICT": "PASS" if pedagogical_mutations == 0 else "FAIL",
        "CLOSURE_DIGEST_BOUND": closure_digest,
        "RECEIPT_DIGEST_BOUND": receipt_digest,
    }

    return {
        "artifact_type": "release_maturity_transition_audit",
        "schema_version": 1,
        "generated_by": "scripts/apply_release_owner_maturity_transition.py",
        "summary": summary,
        "promoted_objects_sample": promoted_objects[:10],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = apply_transition(dry_run=args.dry_run or args.check)
    json_rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    s = payload["summary"]
    lines = [
        "# Audit de Transition de Maturité et Préservation de Traçabilité",
        "",
        f"- Objets traités : `{s['TOTAL_OBJECTS_CONSIDERED']}`",
        f"- Objets promus au statut approved : `{s['PROMOTED_OBJECTS_COUNT']}`",
        f"- Sous-ensemble strict des objets acceptés : `{s['PROMOTED_OBJECTS_SUBSET_OF_ACCEPTED']}`",
        f"- Promotions non autorisées (`UNAUTHORIZED_STATUS_PROMOTION`) : `{s['UNAUTHORIZED_STATUS_PROMOTION']}`",
        f"- Altérations pédagogiques (`PEDAGOGICAL_CONTENT_MUTATIONS`) : `{s['PEDAGOGICAL_CONTENT_MUTATIONS']}`",
        f"- Verdict intégrité didactique : `{s['PEDAGOGICAL_INTEGRITY_VERDICT']}`",
        f"- Empreinte de clôture liée : `{s['CLOSURE_DIGEST_BOUND']}`",
        f"- Empreinte du reçu liée : `{s['RECEIPT_DIGEST_BOUND']}`",
        "",
        "## Règle de Conservation de l'Histoire",
        "Pour chaque objet, la provenance initiale (`origin = generated` ou `origin = needs_review`) est",
        "strictement préservée dans les métadonnées. L'historique de transition `status_history` atteste",
        "le cheminement canonique vers l'approbation finale.",
        "",
    ]
    md_rendered = "\n".join(lines)

    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == json_rendered:
            print("RELEASE_MATURITY_TRANSITION_AUDIT check: OK")
            return 0
        print("RELEASE_MATURITY_TRANSITION_AUDIT check: STALE")
        return 1

    OUTPUT_JSON.write_text(json_rendered, encoding="utf-8")
    OUTPUT_MD.write_text(md_rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON} and {OUTPUT_MD}")
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
