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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def test_the_content_globs_cover_every_source_that_decides_what_is_read() -> None:
    """Les motifs doivent couvrir ce qui decide du contenu, nommement.

    Verifier qu'un motif « existe » ne prouve rien : ce qui compte est que les
    fichiers dont depend le contenu soient effectivement classes CONTENT. Le
    manifeste de livre est le cas qui manquait.
    """
    critiques = (
        "NSI/manifests/books/TNSI.json",
        "NSI/manifests/books/1NSI.json",
        "NSI/chapitres/1NSI-TABLES/methodes/1NSI-TAB-M1.tex",
        "Mathematiques/manuel-maths/chapitres/1SPE-SECOND-DEGRE/cours/00_ouverture.tex",
        "NSI/referentiel/capacites_TNSI_ALGORITHMIQUE.json",
        "NSI/scripts/assemble_manuel.py",
    )
    for chemin in critiques:
        assert (ROOT / chemin).is_file(), f"fichier critique absent : {chemin}"
        assert freshness.classify(chemin) == {"CONTENT"}, chemin


def test_no_audit_directory_enters_the_semantic_digest() -> None:
    """Un artefact d'audit ne décrit pas les manuels : il les observe."""
    for root in freshness.CONTENT_SEMANTIC_GLOBS:
        assert not root.startswith("audit"), root
        assert "audit/" not in root, root


def test_the_digest_is_stable_across_a_commit_that_touches_only_audit() -> None:
    """Le cas exact qui a motivé ce contrat.

    `d2f677fd2` est le commit audité ; `8ebc18c8c` celui qui a ajouté le
    rapport. Entre les deux, aucune source de manuel n'a bougé.
    """
    audite = freshness.content_semantic_digest(commit="d2f677fd2")
    rapport = freshness.content_semantic_digest(commit="8ebc18c8c")
    assert audite == rapport, (
        "un commit qui ne touche que audit/ a modifié le digest sémantique"
    )


def test_the_digest_changes_when_a_manual_source_changes() -> None:
    """Le digest doit rester sensible à ce qu'il décrit."""
    avant = freshness.content_semantic_digest(commit="274a7b811")
    maintenant = freshness.content_semantic_digest(commit="HEAD")
    assert avant != maintenant, "le digest ne distingue plus deux corpus différents"


def test_provenance_separates_the_four_identities() -> None:
    provenance = freshness.provenance(audited_source_sha=git("rev-parse", "HEAD"))
    assert set(provenance) >= {
        "AUDITED_SOURCE_SHA",
        "REPORT_GENERATED_FROM_SHA",
        "CONTENT_SEMANTIC_DIGEST",
        "RENDER_SOURCE_DIGEST",
        "TOOLCHAIN_DIGEST",
        "RELEASE_TAG_NAME",
    }
    assert provenance["CONTENT_SEMANTIC_DIGEST"].startswith("sha256:")
    assert provenance["RELEASE_TAG_NAME"] is None


def test_two_commits_that_differ_only_by_a_report_share_their_content_digest() -> None:
    """La question n'est jamais « quel commit ? » mais « quelles sources ? ».

    `8ebc18c8c` n'ajoute qu'un rapport a `d2f677fd2`. Une preuve valable pour
    l'un l'est pour l'autre, et le restera quel que soit le nombre de rapports
    publies entre-temps.
    """
    assert freshness.semantically_current(
        observed_commit="d2f677fd2",
        observed_digest=freshness.content_semantic_digest(commit="8ebc18c8c"),
    ) is False or freshness.content_semantic_digest(
        commit="d2f677fd2"
    ) == freshness.content_semantic_digest(commit="8ebc18c8c")
    assert freshness.content_semantic_digest(
        commit="d2f677fd2"
    ) == freshness.content_semantic_digest(commit="8ebc18c8c")


def test_a_proof_taken_at_head_is_current_at_head() -> None:
    assert freshness.semantically_current(observed_commit="HEAD") is True
