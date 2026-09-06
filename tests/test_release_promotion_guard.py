"""Tests de garde-fous interdisant toute promotion vers la publication courante.

Invariants requis :
- UNSIGNED_CANDIDATE_CANNOT_BE_CURRENT
- RELEASE_STRICT_RED_IMPLIES_PROMOTION_FORBIDDEN
- FINAL_BLOCKERS_NONEMPTY_IMPLIES_PROMOTION_FORBIDDEN
- NO_APPROVED_CURRENT_RELEASE_DECLARED
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_no_approved_current_release_declared() -> None:
    """Tant que le signoff humain final n'a pas eu lieu, aucune release courante n'est approuvée."""
    candidates_manifest = ROOT / "audit/CERTIFIED_UNSIGNED_RELEASE_CANDIDATES.json"
    assert candidates_manifest.is_file(), "Le manifeste des candidats doit exister"
    payload = json.loads(candidates_manifest.read_text(encoding="utf-8"))
    assert payload.get("status") == "CERTIFIED_UNSIGNED_RELEASE_CANDIDATE"
    assert payload.get("current_approved_release") == "NO_APPROVED_CURRENT_RELEASE"


def test_unsigned_candidate_cannot_be_current() -> None:
    """Un artefact candidat non signé ne peut pas être marqué comme publication courante approuvée."""
    candidates_manifest = ROOT / "audit/CERTIFIED_UNSIGNED_RELEASE_CANDIDATES.json"
    assert candidates_manifest.is_file()
    payload = json.loads(candidates_manifest.read_text(encoding="utf-8"))
    assert payload.get("status") != "CURRENT_APPROVED_RELEASE"
    for record in payload.get("records", []):
        assert "build/certified_unsigned_release_candidates" in record.get("staged_candidate_path", "")


def test_release_strict_red_implies_promotion_forbidden() -> None:
    """Si release-strict est ROUGE, la promotion atomique vers la publication courante est strictement interdite."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import release_all_check as mod

    report = mod.evaluate_release(release_owner_final_signoff=False)
    summary = report.get("summary", {})
    assert summary.get("RELEASE_OWNER_FINAL_SIGNOFF") is False
    assert summary.get("ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY") is False
    assert summary.get("PUBLISH_READY_COUNT") == 0


def test_final_blockers_nonempty_implies_promotion_forbidden() -> None:
    """Si des bloqueurs finaux subsistent, la promotion est strictement interdite."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import release_all_check as mod

    report = mod.evaluate_release(release_owner_final_signoff=True)
    summary = report.get("summary", {})
    total_blockers = (
        summary.get("TOTAL_P0_OPEN", 0)
        + summary.get("TOTAL_P1_OPEN", 0)
        + summary.get("TOTAL_P2_OPEN", 0)
    )
    if total_blockers > 0:
        assert summary.get("ALL_CANONICAL_MANUALS_ZERO_DEBT_PUBLISH_READY") is False
