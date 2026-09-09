import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit" / "PUBLISH_STATUS_DEBT_CLASSIFICATION.json"


def test_status_debt_classification_is_complete_and_unknown_free():
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    rows = payload["entries"]

    # Les totaux suivent le contenu : les figer ferait echouer le test a chaque
    # objet ajoute ou revu, et inviterait a recopier le nouveau chiffre plutot
    # qu'a examiner ce qui a bouge. Ce qui doit tenir est la coherence interne
    # du classement, et l'absence de tout objet non classe.
    assert rows, "une classification vide ne prouve aucune absence de dette"
    assert payload["summary"]["classified"] == len(rows)
    assert payload["summary"]["unknown"] == 0
    assert payload["summary"]["current_status_claim_authorized"] is False
    assert payload["source"]["current_source_status_slice_revalidated"] is False
    assert len({(row["manual"], row["scope"], row["path"], row["id"]) for row in rows}) == len(rows)

    required = {
        "current_status",
        "manual",
        "object_type",
        "publishable",
        "review_state",
        "programme_state",
        "scientific_state",
        "pedagogical_state",
        "reason_cluster",
    }
    assert all(required <= row.keys() for row in rows)
    assert all(row["publishable"] is False for row in rows)
    assert all(row["reason_cluster"] != "UNKNOWN" for row in rows)
    assert all(row["current_status_provenance"] == "STALE_INVENTORY_SNAPSHOT" for row in rows)


def test_status_debt_cluster_counts_are_reproducible():
    """Le classement partitionne la dette, sans categorie fourre-tout.

    Chaque objet tombe dans exactement un motif du vocabulaire declare, et le
    resume publie doit compter la meme chose que les entrees publiees. Une
    divergence entre les deux signalerait un resume qui ne decrit plus son
    propre contenu.
    """
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    actual = Counter(row["reason_cluster"] for row in payload["entries"])
    declared = payload["summary"]["by_cluster"]

    assert set(actual) <= set(declared), "motif hors du vocabulaire declare"
    assert all(declared[cluster] == actual.get(cluster, 0) for cluster in declared)
    assert sum(actual.values()) == len(payload["entries"])
    assert "UNKNOWN" not in actual and "OTHER" not in actual

    by_manual = payload["summary"]["by_manual"]
    assert sum(entry["total"] for entry in by_manual.values()) == len(payload["entries"])
    for manual, entry in by_manual.items():
        observed = Counter(
            row["reason_cluster"] for row in payload["entries"] if row["manual"] == manual
        )
        assert entry["total"] == sum(observed.values())
        assert all(entry["by_cluster"][cluster] == observed.get(cluster, 0)
                   for cluster in entry["by_cluster"])


def test_status_debt_artifacts_match_generator():
    completed = subprocess.run(
        [sys.executable, "scripts/classify_publish_status_debt.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
