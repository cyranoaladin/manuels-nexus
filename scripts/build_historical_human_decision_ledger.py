#!/usr/bin/env python3
"""Registre des décisions humaines devenues non autoritatives.

La décision du Release Owner du 2026-09-06 a réellement eu lieu et reste dans
l'histoire du dépôt. Ce qui est invalide, c'est son *usage comme preuve
cryptographique de la release courante*, pour deux raisons factuelles :

1. `CONTENT_SOURCE_CLOSURE_DIGEST` agrégeait neuf artefacts de `audit/`, dont
   `BLOCKER_TAXONOMY.json` — lequel change précisément parce que le reçu
   existe. L'empreinte ne peut donc jamais rester valide après sa propre
   acceptation ; elle ne liait pas non plus le contenu pédagogique.

2. Le contenu pédagogique a muté *après* l'acceptation : un bloc `\\remarque{}`
   de 10 lignes a été ajouté à `TNSI-PROJET-ANNUEL.tex` dans un commit de
   statut.

Ce registre n'efface rien : il enregistre la décision, l'empreinte alors
déclarée, l'erreur de conception, la mutation postérieure et la raison de
non-applicabilité.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
OUTPUT_JSON = ROOT / "audit/HISTORICAL_HUMAN_DECISIONS.json"
OUTPUT_MD = ROOT / "audit/HISTORICAL_HUMAN_DECISIONS.md"

HISTORICAL_STATUS = "HISTORICAL_HUMAN_DECISION"
NON_AUTHORITATIVE_REASON = (
    "NON_AUTHORITATIVE_FOR_CURRENT_RELEASE_DUE_TO_INVALID_CONTENT_BINDING"
    "_AND_POST_ACCEPTANCE_CONTENT_MUTATION"
)

ACCEPTED_HEAD = "2e51a9be56ee704da1389876611c55b1dac76e2c"
MUTATED_OBJECT = "NSI/chapitres/TNSI-PROJET/projet/TNSI-PROJET-ANNUEL.tex"
MUTATING_COMMIT = "e76064c5"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _body_after_meta(blob: bytes) -> str:
    return "\n".join(blob.decode("utf-8", "replace").splitlines()[1:])


def build() -> dict[str, Any]:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    accepted_body = _git("show", f"{ACCEPTED_HEAD}:{MUTATED_OBJECT}")
    current_body = _body_after_meta((ROOT / MUTATED_OBJECT).read_bytes())
    accepted_body_only = "\n".join(accepted_body.splitlines()[1:])

    return {
        "artifact_type": "historical_human_decisions",
        "schema_version": 1,
        "generated_by": "scripts/build_historical_human_decision_ledger.py",
        "summary": {
            "HISTORICAL_DECISIONS_COUNT": 1,
            "HISTORICAL_RECEIPT_CAN_AUTHORIZE_CURRENT_RELEASE": False,
        },
        "decisions": [
            {
                "decision_id": "HHD-2026-09-06-001",
                "reviewer_identity": receipt.get("reviewer_identity"),
                "original_decision": receipt.get("decision"),
                "original_decision_status": "APPROVED",
                "current_status": HISTORICAL_STATUS,
                "non_authoritative_reason": NON_AUTHORITATIVE_REASON,
                "timestamp": receipt.get("timestamp"),
                "head_at_acceptance": ACCEPTED_HEAD,
                "declared_digest": {
                    "name": "CONTENT_SOURCE_CLOSURE_DIGEST",
                    "value": receipt.get("content_source_closure_digest"),
                },
                "receipt_digest": receipt.get("receipt_digest"),
                "design_defect": {
                    "kind": "CIRCULAR_AND_MISNAMED_DIGEST",
                    "detail": (
                        "L'empreinte agrégeait neuf artefacts de audit/, dont "
                        "BLOCKER_TAXONOMY.json qui bascule OPEN -> RESOLVED "
                        "dès que le reçu existe. Une preuve ne peut pas "
                        "dépendre de la décision qu'elle authentifie. De plus "
                        "l'empreinte ne couvrait aucun octet de contenu "
                        "pédagogique malgré son nom."
                    ),
                    "cycle": [
                        "RECEIPT -> BLOCKER_TAXONOMY.json",
                        "BLOCKER_TAXONOMY.json -> CONTENT_SOURCE_CLOSURE_DIGEST",
                        "CONTENT_SOURCE_CLOSURE_DIGEST -> RECEIPT",
                    ],
                },
                "post_acceptance_content_mutation": {
                    "object_path": MUTATED_OBJECT,
                    "introduced_by_commit": MUTATING_COMMIT,
                    "commit_subject": "[STATUS] apply digest-bound publication maturity transitions",
                    "accepted_body_sha256": "sha256:" + hashlib.sha256(
                        accepted_body_only.encode("utf-8")
                    ).hexdigest(),
                    "post_acceptance_body_sha256": "sha256:" + hashlib.sha256(
                        current_body.encode("utf-8")
                    ).hexdigest(),
                    "detail": (
                        "Ajout d'un bloc \\remarque{} de 10 lignes sur le "
                        "périmètre d'exigibilité, dans un commit dont le "
                        "contrat était limité à la maturité."
                    ),
                },
                "supersedes_nothing": True,
                "retained_for_history": True,
            }
        ],
    }


def render_md(payload: dict[str, Any]) -> str:
    decision = payload["decisions"][0]
    return "\n".join([
        "# Décisions humaines historiques",
        "",
        "Ces décisions ont réellement eu lieu et sont conservées. Elles "
        "n'autorisent plus aucune release courante.",
        "",
        f"- `HISTORICAL_RECEIPT_CAN_AUTHORIZE_CURRENT_RELEASE` : "
        f"`{payload['summary']['HISTORICAL_RECEIPT_CAN_AUTHORIZE_CURRENT_RELEASE']}`",
        "",
        f"## {decision['decision_id']}",
        "",
        f"- Relecteur : `{decision['reviewer_identity']}`",
        f"- Décision d'origine : `{decision['original_decision']}` "
        f"(`{decision['original_decision_status']}`)",
        f"- Statut courant : `{decision['current_status']}`",
        f"- Raison de non-applicabilité : `{decision['non_authoritative_reason']}`",
        f"- HEAD accepté : `{decision['head_at_acceptance']}`",
        f"- Empreinte alors déclarée : `{decision['declared_digest']['value']}`",
        "",
        "### Erreur de conception de l'empreinte",
        "",
        decision["design_defect"]["detail"],
        "",
        "Cycle constaté : " + " → ".join(decision["design_defect"]["cycle"]),
        "",
        "### Mutation pédagogique postérieure",
        "",
        f"- Objet : `{decision['post_acceptance_content_mutation']['object_path']}`",
        f"- Commit : `{decision['post_acceptance_content_mutation']['introduced_by_commit']}`"
        f" — {decision['post_acceptance_content_mutation']['commit_subject']}",
        "",
        decision["post_acceptance_content_mutation"]["detail"],
        "",
    ])


def demote_receipt(decision: dict[str, Any]) -> None:
    """Prive le reçu de son autorité sans effacer ce qu'il disait.

    Le contenu d'origine est conservé intégralement sous `original_receipt` :
    la décision a eu lieu, elle reste lisible. Seule change sa capacité à
    autoriser une release courante.
    """
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("decision_status") == HISTORICAL_STATUS:
        return
    demoted = {
        "artifact_type": "release_owner_decision_receipt",
        "schema_version": receipt.get("schema_version", 1),
        "generated_by": "scripts/build_historical_human_decision_ledger.py",
        "reviewer_identity": receipt.get("reviewer_identity"),
        "decision": receipt.get("decision"),
        "decision_status": HISTORICAL_STATUS,
        "non_authoritative_reason": NON_AUTHORITATIVE_REASON,
        "historical_decision_id": decision["decision_id"],
        "can_authorize_current_release": False,
        "superseded_at_head": _git("rev-parse", "HEAD"),
        "original_receipt": receipt,
    }
    RECEIPT_PATH.write_text(
        json.dumps(demoted, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    md = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.md"
    md.write_text("\n".join([
        "# Reçu de décision du Release Owner — HISTORIQUE",
        "",
        f"- Statut : `{HISTORICAL_STATUS}`",
        f"- Raison : `{NON_AUTHORITATIVE_REASON}`",
        f"- Décision d'origine : `{receipt.get('decision')}` par "
        f"`{receipt.get('reviewer_identity')}` le `{receipt.get('timestamp')}`",
        f"- Empreinte alors déclarée : `{receipt.get('content_source_closure_digest')}`",
        "",
        "Cette décision a réellement eu lieu et reste consignée. Elle n'autorise",
        "plus aucune release courante : voir `HISTORICAL_HUMAN_DECISIONS.md`.",
        "",
    ]), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendered:
            print("HISTORICAL_HUMAN_DECISIONS check: OK")
            return 0
        print("HISTORICAL_HUMAN_DECISIONS check: STALE")
        return 1

    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    demote_receipt(payload["decisions"][0])
    print(json.dumps(payload["summary"], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
