"""Vérification de l'invariance stricte du corps didactique après transition des métadonnées."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "audit/RELEASE_MATURITY_TRANSITION_AUDIT.json"


@pytest.fixture(scope="module")
def audit_data():
    assert AUDIT_PATH.is_file(), "Le registre de transition doit exister"
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def test_pedagogical_content_integrity(audit_data: dict) -> None:
    summary = audit_data["summary"]
    assert summary["PEDAGOGICAL_CONTENT_MUTATIONS"] == 0
    assert summary["PEDAGOGICAL_INTEGRITY_VERDICT"] == "PASS"
    assert summary["UNAUTHORIZED_STATUS_PROMOTION"] == 0
    assert summary["PROMOTED_OBJECTS_SUBSET_OF_ACCEPTED"] is True
    assert summary["PROMOTED_OBJECTS_COUNT"] == 2120


def test_sample_pedagogical_body_exact_match(audit_data: dict) -> None:
    for obj in audit_data.get("promoted_objects_sample", []):
        file_path = ROOT / obj["path"]
        assert file_path.is_file(), f"Fichier introuvable: {obj[path]}"
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
        lines = raw_text.splitlines()
        body = "\n".join(lines[1:])
        current_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        assert current_hash == obj["body_hash"], f"Altération détectée dans {obj[id]}"
