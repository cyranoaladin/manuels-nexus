#!/usr/bin/env python3
"""Validateur de reçu Release Owner et garde de promotion.

Deux règles gouvernent ce module.

1. Un reçu n'est valide que s'il est *lié* à l'état qu'il prétend accepter. La
   liaison est recalculée ici, par `release_digests`, jamais recopiée depuis un
   littéral.

2. Un reçu satisfait une exigence de gouvernance. Il ne transforme jamais
   `stale -> fresh`, `ambiguous -> resolved`, `missing -> present`, ni
   `invalid -> valid`. Aucun contrôle d'intégrité factuel n'est ici conditionné
   à la présence d'un reçu.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import release_digests as digests

ROOT = digests.ROOT
RECEIPT_PATH = ROOT / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"

#: Statut d'un reçu conservé pour l'histoire mais privé d'autorité courante.
HISTORICAL_STATUS = "HISTORICAL_HUMAN_DECISION"

REQUIRED_FIELDS = (
    "reviewer_identity",
    "decision",
    "decision_status",
    "scope",
    "object_set_digest",
    "pedagogical_content_digest",
    "acceptance_evidence_bundle_digest",
    "timestamp",
)


class ReceiptTamperError(ValueError):
    """Le reçu ne correspond plus à l'état qu'il prétend accepter."""


def receipt_binding_violations(
    receipt: Mapping[str, Any],
    root: Path = ROOT,
) -> list[str]:
    """Motifs pour lesquels ce reçu n'autorise pas la release courante.

    Liste vide == reçu valide et liant. Chaque motif est factuel et recalculé.
    """
    violations: list[str] = []

    if receipt.get("decision_status") == HISTORICAL_STATUS:
        violations.append(
            f"RECEIPT_IS_HISTORICAL:{receipt.get('non_authoritative_reason', 'unspecified')}"
        )

    for field in REQUIRED_FIELDS:
        if not receipt.get(field):
            violations.append(f"RECEIPT_FIELD_MISSING:{field}")
    if violations:
        return violations

    if receipt["decision"] != "ACCEPT_FROZEN_RELEASE_CONTENT":
        violations.append(f"RECEIPT_DECISION_NOT_ACCEPT:{receipt['decision']}")

    current = digests.compute_all(root)
    for field, key in (
        ("object_set_digest", "OBJECT_SET_DIGEST"),
        ("pedagogical_content_digest", "PEDAGOGICAL_CONTENT_DIGEST"),
        ("acceptance_evidence_bundle_digest", "ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST"),
    ):
        if receipt[field] != current[key]:
            violations.append(
                f"RECEIPT_DIGEST_MISMATCH:{key}:receipt={receipt[field]}:current={current[key]}"
            )

    return violations


def receipt_is_valid_for_current_release(
    receipt: Mapping[str, Any],
    root: Path = ROOT,
) -> bool:
    return not receipt_binding_violations(receipt, root)


def load_receipt(root: Path = ROOT) -> dict[str, Any] | None:
    path = root / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def assert_receipt_binds(receipt: Mapping[str, Any], root: Path = ROOT) -> None:
    """Lève ReceiptTamperError si le reçu ne lie pas l'état courant."""
    violations = receipt_binding_violations(receipt, root)
    if violations:
        raise ReceiptTamperError("; ".join(violations))


# --- Garde de promotion (§29) ------------------------------------------------

def promotion_decision(
    root: Path = ROOT,
    *,
    release_strict_pass: bool,
    final_blockers: list[str],
) -> dict[str, Any]:
    """`PROMOTION_ALLOWED` ssi les quatre conditions sont simultanément vraies.

    Aucune de ces conditions n'admet de dérogation, de whitelist ni de seuil.
    """
    refusals: list[str] = []

    if not release_strict_pass:
        refusals.append("RELEASE_STRICT_NOT_PASS")
    if final_blockers:
        refusals.append(f"FINAL_BLOCKERS_NONEMPTY:{len(final_blockers)}")

    receipt = load_receipt(root)
    if receipt is None:
        refusals.append("RELEASE_OWNER_RECEIPT_ABSENT")
    else:
        binding = receipt_binding_violations(receipt, root)
        if binding:
            refusals.append("VALID_RELEASE_OWNER_RECEIPT_FALSE")
            refusals.extend(binding)

    return {
        "PROMOTION_ALLOWED": not refusals,
        "REFUSAL_REASONS": refusals,
    }


if __name__ == "__main__":
    receipt = load_receipt()
    print(json.dumps({
        "receipt_present": receipt is not None,
        "binding_violations": receipt_binding_violations(receipt) if receipt else ["ABSENT"],
    }, indent=2, ensure_ascii=False))
