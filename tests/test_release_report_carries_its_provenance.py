"""Le verdict de release doit dire de quel etat il parle.

Le rapport le plus autoritaire du depot ne portait ni commit source, ni etat de
l'arbre de travail : `provenance` etait absent. Rien n'y distinguait un verdict
calcule sur les sources courantes d'un verdict recopie d'une execution passee,
et c'est ainsi qu'un « 12/12 PUBLISH_READY » a pu survivre trois semaines a des
sources qui ne le portaient plus.

Un verdict sans provenance n'est pas un verdict : c'est une affirmation.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "audit" / "RELEASE_ALL_CHECK.json"
READINESS = ROOT / "audit" / "COLLECTION_PUBLISH_READINESS.json"


def test_the_release_report_records_the_commit_it_observed() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    provenance = payload["provenance"]
    assert len(provenance["AUDITED_SOURCE_SHA"]) == 40
    assert len(provenance["REPORT_COMMIT_SHA"]) == 40
    assert provenance["SEMANTIC_SOURCE_DIGEST"].startswith("sha256:")
    assert isinstance(provenance["worktree_dirty"], bool)
    assert provenance["generated_by"] == payload["generated_by"]
    assert provenance["scope"] in {
        "WORKTREE_BOUND_BY_INPUT_DIGESTS",
        "HEAD_BOUND_BY_INPUT_DIGESTS",
    }


def test_the_report_commit_is_never_a_freshness_criterion() -> None:
    """Publier le rapport ne doit perimer aucune preuve.

    Le rapport du 10 septembre decrivait d2f677fd2 ; son propre commit a
    fait avancer main a 8ebc18c8c. Juger la fraicheur sur le commit rendait
    le rapport faux au moment meme de sa publication.
    """
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from evidence_freshness import semantic_source_digest

    provenance = json.loads(REPORT.read_text(encoding="utf-8"))["provenance"]
    assert provenance["SEMANTIC_SOURCE_DIGEST"] == semantic_source_digest()
    # Les deux commits du rapport de consolidation partagent le meme digest :
    # aucun des deux ne decrit des sources differentes.
    assert semantic_source_digest(commit="d2f677fd2") == semantic_source_digest(
        commit="8ebc18c8c"
    )


def test_a_dirty_worktree_is_never_presented_as_a_committed_state() -> None:
    provenance = json.loads(REPORT.read_text(encoding="utf-8"))["provenance"]
    if provenance["worktree_dirty"]:
        assert provenance["scope"] == "WORKTREE_BOUND_BY_INPUT_DIGESTS"
        assert provenance["worktree_dirty_entries"] > 0, "arbre sale sans aucune entree"
    else:
        assert provenance["scope"] == "HEAD_BOUND_BY_INPUT_DIGESTS"
        assert provenance["worktree_dirty_entries"] == 0


def test_the_provenance_never_publishes_the_paths_it_observed() -> None:
    """Enumerer les chemins modifies ferait du rapport une reference vers eux.

    Le graphe de reference du depot lit les artefacts pour savoir qui cite qui.
    Un rapport qui publie la liste de l'arbre de travail se met a « citer » des
    fichiers qu'il ne fait qu'observer, et fausse ce graphe.
    """
    provenance = json.loads(REPORT.read_text(encoding="utf-8"))["provenance"]
    assert "worktree_status" not in provenance
    assert isinstance(provenance["worktree_dirty_entries"], int)


def test_the_published_readiness_shares_that_provenance() -> None:
    readiness = json.loads(READINESS.read_text(encoding="utf-8"))
    assert readiness["provenance"] == json.loads(REPORT.read_text(encoding="utf-8"))["provenance"]


def test_no_signoff_is_claimed_without_a_recorded_human_decision() -> None:
    """Un signoff est une decision humaine : il ne se deduit d'aucun calcul."""
    summary = json.loads(REPORT.read_text(encoding="utf-8"))["summary"]
    if summary["RELEASE_OWNER_FINAL_SIGNOFF"]:
        decisions = list((ROOT / "audit").glob("HUMAN_DECISION_*SIGNOFF*.json"))
        assert decisions, "signoff annonce sans decision humaine enregistree"
