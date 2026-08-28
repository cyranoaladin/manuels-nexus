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

    assert len(rows) == 2222
    assert payload["summary"]["classified"] == 2222
    assert payload["summary"]["unknown"] == 0
    assert payload["summary"]["current_status_claim_authorized"] is False
    assert payload["source"]["current_source_status_slice_revalidated"] is False
    assert len({(row["manual"], row["scope"], row["path"], row["id"]) for row in rows}) == 2222

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
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    actual = Counter(row["reason_cluster"] for row in payload["entries"])

    assert actual == {
        "GENERATED_NOT_REVIEWED": 1756,
        "STALE_RECEIPT": 337,
        "PROGRAM_REVIEW_PENDING": 122,
        "DRAFT_NOT_REVIEWED": 7,
    }


def test_status_debt_artifacts_match_generator():
    completed = subprocess.run(
        [sys.executable, "scripts/classify_publish_status_debt.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
