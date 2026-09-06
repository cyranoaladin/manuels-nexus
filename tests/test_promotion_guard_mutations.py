"""Garde permanente de promotion — tests de mutation réels.

`PROMOTION_ALLOWED` n'est vrai que si les quatre conditions sont
simultanément satisfaites :

    RELEASE_STRICT == PASS
    FINAL_BLOCKERS == []
    VALID_RELEASE_OWNER_RECEIPT == true
    RECEIPT_PEDAGOGICAL_CONTENT_DIGEST == CURRENT_PEDAGOGICAL_CONTENT_DIGEST

Chaque test casse exactement une condition et exige le refus. Un test casse
les quatre à la fois ; un dernier vérifie qu'aucune n'est superflue.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_digests as digests  # noqa: E402
import release_receipt_validator as validator  # noqa: E402


def _object(meta: dict, body: str) -> str:
    return "% META: " + json.dumps(meta, ensure_ascii=False) + "\n" + body


@pytest.fixture
def promotable_root(tmp_path: Path) -> Path:
    """Racine où les quatre conditions sont satisfaites."""
    (tmp_path / "audit").mkdir()
    (tmp_path / "chapitres/DEMO").mkdir(parents=True)
    (tmp_path / "chapitres/DEMO/DEMO-COURS-C1.tex").write_text(
        _object({"id": "DEMO-COURS-C1", "chapitre": "DEMO", "type_objet": "cours",
                 "status": "needs_review"}, "\\section{Démo}\n"),
        encoding="utf-8",
    )
    (tmp_path / "audit/INVENTAIRE_COLLECTION.json").write_text(
        json.dumps({"manuals": {"DEMO": {"chapters": {"DEMO": {"objects": [
            {"id": "DEMO-COURS-C1", "path": "chapitres/DEMO/DEMO-COURS-C1.tex",
             "status": "needs_review"}]}}}}}),
        encoding="utf-8",
    )
    for rel in digests.ACCEPTANCE_EVIDENCE_ARTIFACTS:
        (tmp_path / rel).write_text(json.dumps({"artifact": Path(rel).stem}), encoding="utf-8")

    current = digests.compute_all(tmp_path)
    (tmp_path / "audit/RELEASE_OWNER_DECISION_RECEIPT.json").write_text(
        json.dumps({
            "reviewer_identity": "abenrhouma",
            "decision": "ACCEPT_FROZEN_RELEASE_CONTENT",
            "decision_status": "APPROVED",
            "scope": "canonical_release_content_only",
            "object_set_digest": current["OBJECT_SET_DIGEST"],
            "pedagogical_content_digest": current["PEDAGOGICAL_CONTENT_DIGEST"],
            "acceptance_evidence_bundle_digest": current["ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST"],
            "timestamp": "2026-09-06T00:00:00+01:00",
        }),
        encoding="utf-8",
    )
    return tmp_path


def _decide(root: Path, *, strict: bool = True, blockers: list[str] | None = None) -> dict:
    return validator.promotion_decision(
        root, release_strict_pass=strict, final_blockers=blockers or []
    )


def test_baseline_allows_promotion(promotable_root: Path) -> None:
    decision = _decide(promotable_root)
    assert decision["PROMOTION_ALLOWED"] is True, decision["REFUSAL_REASONS"]


def test_release_strict_red_forbids_promotion(promotable_root: Path) -> None:
    decision = _decide(promotable_root, strict=False)
    assert decision["PROMOTION_ALLOWED"] is False
    assert "RELEASE_STRICT_NOT_PASS" in decision["REFUSAL_REASONS"]


def test_nonempty_final_blockers_forbid_promotion(promotable_root: Path) -> None:
    decision = _decide(promotable_root, blockers=["ROOT-QUALIFICATION-STALE"])
    assert decision["PROMOTION_ALLOWED"] is False
    assert any(r.startswith("FINAL_BLOCKERS_NONEMPTY") for r in decision["REFUSAL_REASONS"])


def test_absent_receipt_forbids_promotion(promotable_root: Path) -> None:
    (promotable_root / "audit/RELEASE_OWNER_DECISION_RECEIPT.json").unlink()
    decision = _decide(promotable_root)
    assert decision["PROMOTION_ALLOWED"] is False
    assert "RELEASE_OWNER_RECEIPT_ABSENT" in decision["REFUSAL_REASONS"]


def test_pedagogical_content_drift_forbids_promotion(promotable_root: Path) -> None:
    """Le contenu bouge après signature : le reçu ne lie plus rien."""
    target = promotable_root / "chapitres/DEMO/DEMO-COURS-C1.tex"
    target.write_text(target.read_text(encoding="utf-8") + "Ajout.\n", encoding="utf-8")

    decision = _decide(promotable_root)
    assert decision["PROMOTION_ALLOWED"] is False
    assert "VALID_RELEASE_OWNER_RECEIPT_FALSE" in decision["REFUSAL_REASONS"]
    assert any("PEDAGOGICAL_CONTENT_DIGEST" in r for r in decision["REFUSAL_REASONS"])


def test_historical_receipt_forbids_promotion(promotable_root: Path) -> None:
    """Une décision conservée pour l'histoire n'autorise plus rien."""
    path = promotable_root / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    receipt["decision_status"] = validator.HISTORICAL_STATUS
    receipt["non_authoritative_reason"] = "NON_AUTHORITATIVE_FOR_CURRENT_RELEASE"
    path.write_text(json.dumps(receipt), encoding="utf-8")

    decision = _decide(promotable_root)
    assert decision["PROMOTION_ALLOWED"] is False
    assert any(r.startswith("RECEIPT_IS_HISTORICAL") for r in decision["REFUSAL_REASONS"])


def test_all_four_conditions_broken(promotable_root: Path) -> None:
    (promotable_root / "audit/RELEASE_OWNER_DECISION_RECEIPT.json").unlink()
    decision = _decide(promotable_root, strict=False, blockers=["X"])
    assert decision["PROMOTION_ALLOWED"] is False
    assert len(decision["REFUSAL_REASONS"]) >= 3


def test_no_condition_is_redundant(promotable_root: Path) -> None:
    """Chacune des quatre conditions refuse seule : aucune n'est décorative."""
    import copy

    assert _decide(promotable_root)["PROMOTION_ALLOWED"] is True

    assert _decide(promotable_root, strict=False)["PROMOTION_ALLOWED"] is False
    assert _decide(promotable_root, blockers=["X"])["PROMOTION_ALLOWED"] is False

    path = promotable_root / "audit/RELEASE_OWNER_DECISION_RECEIPT.json"
    saved = path.read_text(encoding="utf-8")
    path.unlink()
    assert _decide(promotable_root)["PROMOTION_ALLOWED"] is False
    path.write_text(saved, encoding="utf-8")

    receipt = json.loads(saved)
    receipt["pedagogical_content_digest"] = "sha256:" + "0" * 64
    path.write_text(json.dumps(receipt), encoding="utf-8")
    assert _decide(promotable_root)["PROMOTION_ALLOWED"] is False


def test_guard_never_consults_release_strict_bypass_flags() -> None:
    """Aucun mécanisme de dérogation dans le *code* de la garde.

    On inspecte l'AST plutôt que le texte brut : la prose du module explique
    justement qu'il n'y a ni dérogation ni seuil, et une recherche textuelle
    se déclencherait sur cette explication.
    """
    import ast

    tree = ast.parse((ROOT / "scripts/release_receipt_validator.py").read_text(encoding="utf-8"))
    identifiers = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    } | {
        node.arg for node in ast.walk(tree) if isinstance(node, ast.arg) and node.arg
    }
    literals = {
        node.value.lower() for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and not _is_docstring(tree, node)
    }
    haystack = {i.lower() for i in identifiers} | literals
    for forbidden in ("whitelist", "allowlist", "grandfather", "xfail", "waiver", "override"):
        offenders = [h for h in haystack if forbidden in h]
        assert not offenders, f"mécanisme de dérogation détecté : {offenders}"


def _is_docstring(tree, node) -> bool:
    import ast

    for parent in ast.walk(tree):
        if isinstance(parent, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            body = getattr(parent, "body", [])
            if body and isinstance(body[0], ast.Expr) and body[0].value is node:
                return True
    return False
