"""Un reçu humain ne neutralise jamais un contrôle d'intégrité factuel.

Cinq neutralisations avaient été ajoutées à `inventory_collection.py`, toutes
conditionnées à la présence de `audit/RELEASE_OWNER_DECISION_RECEIPT.json` :
fiche méthode STALE, packet de revue STALE, statut promu sans revue,
OPTIONAL_EXTENSION modifiée, et un `raise InventoryError` remplacé par un
`continue`.

Chaque test ci-dessous est une *mutation* : on place un reçu parfaitement
valide dans la racine synthétique, puis on vérifie que la violation factuelle
est **toujours** signalée. Un reçu satisfait une exigence de gouvernance ; il ne
transforme pas `stale -> fresh`, `ambiguous -> resolved`, `missing -> present`
ni `invalid -> valid`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import inventory_collection as ic  # noqa: E402

POLICY_REL = "audit/A4_METHOD_REVIEW_DEBT_POLICY.md"


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_receipt(root: Path) -> None:
    """Un reçu Release Owner complet, valide et cohérent."""
    (root / "audit").mkdir(parents=True, exist_ok=True)
    receipt = {
        "artifact_type": "release_owner_decision_receipt",
        "reviewer_identity": "abenrhouma",
        "decision": "ACCEPT_FROZEN_RELEASE_CONTENT",
        "decision_status": "APPROVED",
        "scope": "canonical_release_content_only",
        "content_source_closure_digest": "sha256:" + "9" * 64,
        "receipt_digest": "sha256:" + "4" * 64,
    }
    (root / "audit/RELEASE_OWNER_DECISION_RECEIPT.json").write_text(
        json.dumps(receipt), encoding="utf-8"
    )


def _make_method_root(tmp_path: Path, *, meta: dict) -> tuple[Path, dict]:
    """Racine synthétique avec une fiche méthode et sa qualification dérivée."""
    root = tmp_path
    (root / "audit").mkdir(parents=True, exist_ok=True)
    policy = root / POLICY_REL
    policy.write_text("# Politique A4\n", encoding="utf-8")
    policy_digest = "sha256:" + _sha_bytes(policy.read_bytes())

    source_rel = "chapitres/DEMO/methodes/DEMO-ME-001.tex"
    source = root / source_rel
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(
        "% META: " + json.dumps(meta, ensure_ascii=False) + "\n\\section{Démo}\n",
        encoding="utf-8",
    )

    packet_rel = "audit/DEMO_REVIEW_PACKET.json"
    packet = root / packet_rel
    packet.write_text(json.dumps({"packet": "demo"}), encoding="utf-8")

    record = {
        "fingerprint": "demofingerprint01",
        "decision_ref": ic.A4_METHOD_REVIEW_DEBT_DECISION_REF,
        "source": source_rel,
        "qualification_policy_digest": policy_digest,
        "method_source_sha": _sha_bytes(source.read_bytes()),
        "review_packet": packet_rel,
        "review_packet_sha": _sha_bytes(packet.read_bytes()),
    }
    return root, record


def _violations(root: Path, record: dict) -> list[str]:
    return ic._a4_method_review_debt_violations(root, record)


# --- Bypass 1 : fiche méthode STALE ------------------------------------------

def test_stale_method_sheet_is_reported_even_with_a_valid_receipt(tmp_path: Path) -> None:
    meta = {"id": "DEMO-ME-001", "status": "needs_review"}
    root, record = _make_method_root(tmp_path, meta=meta)

    assert not any("STALE" in v for v in _violations(root, record)), (
        "état de référence : la qualification doit être fraîche"
    )

    # Mutation réelle de la source : la qualification devient stale.
    source = root / record["source"]
    source.write_text(source.read_text(encoding="utf-8") + "\n% dérive\n", encoding="utf-8")
    _write_receipt(root)

    violations = _violations(root, record)
    assert any("fiche méthode modifiée après qualification (STALE)" in v for v in violations), (
        f"un reçu ne rend pas une source stale à nouveau fraîche ; obtenu : {violations}"
    )


# --- Bypass 2 : packet de revue STALE ----------------------------------------

def test_stale_review_packet_is_reported_even_with_a_valid_receipt(tmp_path: Path) -> None:
    meta = {"id": "DEMO-ME-001", "status": "needs_review"}
    root, record = _make_method_root(tmp_path, meta=meta)

    packet = root / record["review_packet"]
    packet.write_text(json.dumps({"packet": "muté"}), encoding="utf-8")
    _write_receipt(root)

    violations = _violations(root, record)
    assert any("packet de revue modifié après qualification (STALE)" in v for v in violations), (
        f"un reçu ne rend pas un packet stale à nouveau frais ; obtenu : {violations}"
    )


# --- Bypass 3 : statut promu sans revue humaine ------------------------------

def test_status_promoted_without_review_is_reported_even_with_a_valid_receipt(
    tmp_path: Path,
) -> None:
    meta = {
        "id": "DEMO-ME-001",
        "status": "approved",
        "origin": "needs_review",
        "release_acceptance": "RELEASE_OWNER_BATCH_ACCEPTANCE",
        "acceptance_closure_digest": "sha256:" + "9" * 64,
        "acceptance_receipt_digest": "sha256:" + "4" * 64,
    }
    root, record = _make_method_root(tmp_path, meta=meta)
    _write_receipt(root)

    violations = _violations(root, record)
    assert any("statut promu sans revue humaine" in v for v in violations), (
        "un reçu de gouvernance ne referme pas une dette A4 ouverte ; "
        f"obtenu : {violations}"
    )


# --- Bypass 5 : migration ambiguë ne doit pas être silencieusement ignorée ----

def test_ambiguous_migration_target_raises_instead_of_being_skipped() -> None:
    """`occurrences == 0` doit rester fatal, pas devenir un `continue`."""
    source = (ROOT / "scripts/inventory_collection.py").read_text(encoding="utf-8")
    marker = "L'anomalie n'est plus active dans le corpus courant"
    assert marker not in source, (
        "le `continue` qui absorbait « cible de migration absente ou ambiguë » "
        "a été réintroduit : une anomalie disparue n'est pas une anomalie résolue"
    )


# --- Garde structurelle : plus aucun contrôle conditionné au reçu ------------

def test_no_integrity_check_is_conditioned_on_the_presence_of_a_receipt() -> None:
    source = (ROOT / "scripts/inventory_collection.py").read_text(encoding="utf-8")
    assert "_is_formally_accepted_by_release_owner" not in source, (
        "un helper conditionnant des contrôles d'intégrité à l'existence d'un "
        "reçu humain a été réintroduit dans le gate"
    )
    assert "RELEASE_OWNER_DECISION_RECEIPT" not in source, (
        "le gate d'intégrité lit à nouveau le reçu humain ; la gouvernance ne "
        "doit jamais être une entrée d'un contrôle factuel"
    )
