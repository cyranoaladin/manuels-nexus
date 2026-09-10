"""Un rapport ne doit pas périmer une preuve en se commitant lui-même.

`RAPPORT_FINAL_CONSOLIDATION_2026_09_10.md` décrivait `d2f677fd2` comme l'état
de `main` ; le commit qui l'ajoutait faisait avancer `main` à `8ebc18c8c`. Le
rapport s'invalidait donc au moment même de sa publication, et toute preuve
jugée fraîche « parce que son commit est le HEAD » devenait périmée sans qu'un
seul octet de manuel ait bougé.

Quatre identités distinctes, et une seule sert à juger la fraîcheur :

    AUDITED_SOURCE_SHA     le commit dont les sources ont été observées
    REPORT_COMMIT_SHA      le commit qui porte le rapport — traçabilité seule
    SEMANTIC_SOURCE_DIGEST l'empreinte des sources canoniques : LE critère
    RELEASE_TAG_SHA        le tag de release, quand il existe

Une preuve reste courante tant que `SEMANTIC_SOURCE_DIGEST` n'a pas changé,
quel que soit le nombre de commits d'audit intervenus depuis.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_the_canonical_source_roots_are_declared_and_exist() -> None:
    assert freshness.SEMANTIC_SOURCE_ROOTS
    for root in freshness.SEMANTIC_SOURCE_ROOTS:
        assert (ROOT / root).is_dir(), f"racine de source déclarée mais absente : {root}"


def test_no_audit_directory_enters_the_semantic_digest() -> None:
    """Un artefact d'audit ne décrit pas les manuels : il les observe."""
    for root in freshness.SEMANTIC_SOURCE_ROOTS:
        assert not root.startswith("audit"), root
        assert "audit/" not in root, root


def test_the_digest_is_stable_across_a_commit_that_touches_only_audit() -> None:
    """Le cas exact qui a motivé ce contrat.

    `d2f677fd2` est le commit audité ; `8ebc18c8c` celui qui a ajouté le
    rapport. Entre les deux, aucune source de manuel n'a bougé.
    """
    audite = freshness.semantic_source_digest(commit="d2f677fd2")
    rapport = freshness.semantic_source_digest(commit="8ebc18c8c")
    assert audite == rapport, (
        "un commit qui ne touche que audit/ a modifié le digest sémantique"
    )


def test_the_digest_changes_when_a_manual_source_changes() -> None:
    """Le digest doit rester sensible à ce qu'il décrit."""
    avant = freshness.semantic_source_digest(commit="274a7b811")
    maintenant = freshness.semantic_source_digest(commit="HEAD")
    assert avant != maintenant, "le digest ne distingue plus deux corpus différents"


def test_provenance_separates_the_four_identities() -> None:
    provenance = freshness.provenance(audited_source_sha=git("rev-parse", "HEAD"))
    assert set(provenance) >= {
        "AUDITED_SOURCE_SHA",
        "REPORT_COMMIT_SHA",
        "SEMANTIC_SOURCE_DIGEST",
        "RELEASE_TAG_SHA",
    }
    assert provenance["SEMANTIC_SOURCE_DIGEST"].startswith("sha256:")
    assert provenance["RELEASE_TAG_SHA"] is None or len(provenance["RELEASE_TAG_SHA"]) == 40


@pytest.mark.parametrize("commit", ["d2f677fd2", "8ebc18c8c"])
def test_evidence_stays_current_while_the_sources_do(commit: str) -> None:
    """La question n'est jamais « quel commit ? » mais « quelles sources ? »."""
    assert freshness.semantically_current(observed_commit=commit) is True
