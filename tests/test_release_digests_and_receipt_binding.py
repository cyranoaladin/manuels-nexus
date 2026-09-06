"""Empreintes canoniques et falsification réelle du reçu.

Le test précédent, `test_receipt_digest_mismatch_fails`, levait lui-même le
`ValueError` qu'il prétendait vérifier : il ne touchait aucune ligne du dépôt.
Ici, chaque test construit une racine synthétique réelle, calcule les
empreintes avec le **producteur du dépôt**, fabrique un reçu lié, puis mute un
octet et vérifie que **le code du dépôt** refuse le reçu.
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


# --- Racine synthétique -------------------------------------------------------

def _object(meta: dict, body: str) -> str:
    return "% META: " + json.dumps(meta, ensure_ascii=False) + "\n" + body


@pytest.fixture
def fake_root(tmp_path: Path) -> Path:
    """Deux objets canoniques, plus les preuves pré-décision attendues."""
    (tmp_path / "audit").mkdir()
    (tmp_path / "chapitres/DEMO").mkdir(parents=True)

    (tmp_path / "chapitres/DEMO/DEMO-COURS-C1.tex").write_text(
        _object(
            {"id": "DEMO-COURS-C1", "chapitre": "DEMO", "type_objet": "cours",
             "capacites": ["DEMO-BO-01"], "status": "needs_review"},
            "\\section{Suites}\nUne suite est dite arithmétique si...\n",
        ),
        encoding="utf-8",
    )
    (tmp_path / "chapitres/DEMO/DEMO-EX-001.tex").write_text(
        _object(
            {"id": "DEMO-EX-001", "chapitre": "DEMO", "type_objet": "exercice",
             "capacites": ["DEMO-BO-01"], "status": "generated"},
            "\\begin{exercice}\nCalculer $u_5$.\n\\end{exercice}\n",
        ),
        encoding="utf-8",
    )

    (tmp_path / "audit/INVENTAIRE_COLLECTION.json").write_text(
        json.dumps({"manuals": {"DEMO": {"chapters": {"DEMO": {"objects": [
            {"id": "DEMO-COURS-C1", "path": "chapitres/DEMO/DEMO-COURS-C1.tex",
             "status": "needs_review"},
            {"id": "DEMO-EX-001", "path": "chapitres/DEMO/DEMO-EX-001.tex",
             "status": "generated"},
        ]}}}}}),
        encoding="utf-8",
    )

    for rel in digests.ACCEPTANCE_EVIDENCE_ARTIFACTS:
        (tmp_path / rel).write_text(
            json.dumps({"artifact": Path(rel).stem, "summary": {}}), encoding="utf-8"
        )
    return tmp_path


def _receipt_for(root: Path) -> dict:
    """Reçu réellement lié, produit à partir des empreintes calculées."""
    current = digests.compute_all(root)
    return {
        "reviewer_identity": "abenrhouma",
        "decision": "ACCEPT_FROZEN_RELEASE_CONTENT",
        "decision_status": "APPROVED",
        "scope": "canonical_release_content_only",
        "object_set_digest": current["OBJECT_SET_DIGEST"],
        "pedagogical_content_digest": current["PEDAGOGICAL_CONTENT_DIGEST"],
        "acceptance_evidence_bundle_digest": current["ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST"],
        "timestamp": "2026-09-06T00:00:00+01:00",
    }


# --- Le reçu lié est accepté --------------------------------------------------

def test_untampered_receipt_is_accepted(fake_root: Path) -> None:
    receipt = _receipt_for(fake_root)
    assert validator.receipt_binding_violations(receipt, fake_root) == []


# --- Mutation d'un contenu pédagogique ---------------------------------------

def test_pedagogical_content_mutation_invalidates_the_receipt(fake_root: Path) -> None:
    receipt = _receipt_for(fake_root)
    target = fake_root / "chapitres/DEMO/DEMO-COURS-C1.tex"
    target.write_text(
        target.read_text(encoding="utf-8") + "\nUn ajout pédagogique.\n", encoding="utf-8"
    )

    violations = validator.receipt_binding_violations(receipt, fake_root)
    assert any("PEDAGOGICAL_CONTENT_DIGEST" in v for v in violations), violations
    with pytest.raises(validator.ReceiptTamperError):
        validator.assert_receipt_binds(receipt, fake_root)


# --- Mutation d'un identifiant d'objet ---------------------------------------

def test_object_id_mutation_invalidates_the_receipt(fake_root: Path) -> None:
    receipt = _receipt_for(fake_root)
    inventory_path = fake_root / "audit/INVENTAIRE_COLLECTION.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    objects = inventory["manuals"]["DEMO"]["chapters"]["DEMO"]["objects"]
    objects[1]["id"] = "DEMO-EX-999"
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")

    violations = validator.receipt_binding_violations(receipt, fake_root)
    assert any("OBJECT_SET_DIGEST" in v for v in violations), violations


# --- Mutation d'un audit de preuve -------------------------------------------

def test_evidence_audit_mutation_invalidates_the_receipt(fake_root: Path) -> None:
    receipt = _receipt_for(fake_root)
    evidence = fake_root / "audit/SEMANTIC_ALIGNMENT_AUDIT.json"
    evidence.write_text(
        json.dumps({"artifact": "SEMANTIC_ALIGNMENT_AUDIT",
                    "summary": {"SEMANTIC_ALIGNMENT_ALIGNED": 371}}),
        encoding="utf-8",
    )

    violations = validator.receipt_binding_violations(receipt, fake_root)
    assert any("ACCEPTANCE_EVIDENCE_BUNDLE_DIGEST" in v for v in violations), violations


# --- Mutation d'une métadonnée de pure gouvernance ---------------------------

def test_governance_metadata_mutation_leaves_the_receipt_valid(fake_root: Path) -> None:
    """Comportement attendu, explicitement défini : une transition de maturité
    ne déplace pas `PEDAGOGICAL_CONTENT_DIGEST`, donc le reçu reste liant.

    C'est précisément la propriété qui manquait à l'ancienne empreinte : elle
    confondait gouvernance et contenu, et se cassait à chaque changement de
    statut. Le mouvement reste visible dans `BUILD_SOURCE_CLOSURE_DIGEST`.
    """
    receipt = _receipt_for(fake_root)
    before_build = digests.build_source_closure_digest(fake_root)

    target = fake_root / "chapitres/DEMO/DEMO-EX-001.tex"
    lines = target.read_text(encoding="utf-8").splitlines()
    meta = json.loads(lines[0][len("% META:"):])
    meta["status"] = "approved"
    meta["origin"] = "generated"
    meta["status_history"] = ["generated", "audited", "accepted", "approved"]
    target.write_text(
        "% META: " + json.dumps(meta, ensure_ascii=False) + "\n" + "\n".join(lines[1:]) + "\n",
        encoding="utf-8",
    )

    assert validator.receipt_binding_violations(receipt, fake_root) == []
    assert digests.build_source_closure_digest(fake_root) != before_build, (
        "BUILD_SOURCE_CLOSURE_DIGEST doit refléter le mouvement d'octets"
    )


# --- Le test ne lève jamais lui-même son exception ---------------------------

def test_tamper_tests_do_not_raise_their_own_exception() -> None:
    """Garde anti-tautologie : le fichier ne fabrique pas le refus qu'il teste.

    Les motifs sont assemblés à l'exécution, sinon la ligne d'assertion se
    citerait elle-même et le test échouerait sur son propre texte.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    verb = "".join(["ra", "ise"])
    for needle in (f"{verb} ValueError", f"{verb} validator.ReceiptTamperError"):
        assert needle not in source, f"le test fabrique lui-même le refus : {needle}"


# --- Acyclicité (§4.2) --------------------------------------------------------

def test_digest_dependency_graph_has_no_cycles() -> None:
    assert digests.count_digest_dependency_cycles() == 0


def test_acceptance_evidence_excludes_decision_dependent_artifacts() -> None:
    overlap = set(digests.ACCEPTANCE_EVIDENCE_ARTIFACTS) & digests.DECISION_DEPENDENT_ARTIFACTS
    assert overlap == set(), (
        f"une preuve d'acceptation dépend de la décision qu'elle authentifie : {overlap}"
    )
    digests.assert_acyclic()


def test_blocker_taxonomy_is_never_an_acceptance_evidence_input() -> None:
    """Le défaut historique exact : BLOCKER_TAXONOMY entrait dans la closure."""
    assert "audit/BLOCKER_TAXONOMY.json" not in digests.ACCEPTANCE_EVIDENCE_ARTIFACTS
    assert "audit/BLOCKER_TAXONOMY.json" in digests.DECISION_DEPENDENT_ARTIFACTS


# --- Une seule implémentation canonique (§4.3) -------------------------------

def test_no_producer_hardcodes_an_acceptance_digest() -> None:
    """Aucun digest d'acceptation recopié en littéral dans les producteurs."""
    offenders = []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "9b3ccf9a81c5520fbb7e03b7b2d3e7bf2057a02834b6d908bf3be5f49f3b553f" in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == [], (
        f"empreinte d'acceptation recopiée en dur dans : {offenders}"
    )
