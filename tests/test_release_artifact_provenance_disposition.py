"""Disposition des artefacts sans provenance complete : preuves et mutations.

Le ledger ne decide rien : il verifie des dispositions humaines contre des
preuves calculees. Il ne vaut donc que s'il refute une disposition fausse.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_release_artifact_provenance_disposition as gate  # noqa: E402


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def row_for(payload: dict, disposition: str) -> dict:
    return next(row for row in payload["artifacts"] if row["disposition"] == disposition)


def _evidence(**overrides) -> dict:
    base = {
        "path": "audit/FIXTURE.json",
        "exists": True,
        "sha256": "0" * 64,
        "producer": {
            "generated_by": None,
            "generated_by_resolves": False,
            "producer_path": None,
            "scripts_declaring_the_target": [],
            "has_producer": False,
        },
        "references": [],
        "reference_counts": {},
        "CURRENT_RELEASE_CONSUMERS": 0,
        "history": {
            "tracked_at_head": True,
            "commits_touching_the_artifact": 3,
            "preserved_in_git_history": True,
        },
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Verite courante
# ---------------------------------------------------------------------------
def test_the_three_dispositions_are_confirmed(payload) -> None:
    assert payload["summary"]["DOCKETED_ARTIFACTS"] == 3
    assert payload["summary"]["REFUTED_DISPOSITIONS"] == 0
    assert payload["summary"]["UNKNOWN_DISPOSITIONS"] == 0
    assert payload["summary"]["ACTIVE_RELEASE_ARTIFACTS_WITHOUT_PRODUCER"] == 0
    assert payload["summary"]["GATE"] == "PASS"


def test_the_obsolete_artifact_has_zero_producer_and_zero_consumer(payload) -> None:
    row = row_for(payload, gate.DISPOSITION_OBSOLETE)
    assert row["evidence"]["CURRENT_RELEASE_CONSUMERS"] == 0
    assert row["evidence"]["producer"]["has_producer"] is False
    assert row["evidence"]["producer"]["scripts_declaring_the_target"] == []
    assert row["evidence"]["history"]["preserved_in_git_history"] is True


def test_the_superseded_artifact_snapshots_are_ancestors_of_head(payload) -> None:
    row = row_for(payload, gate.DISPOSITION_SUPERSEDED)
    snapshot = row["evidence"]["snapshot"]
    assert snapshot["snapshot_shas"]
    assert snapshot["all_ancestors_of_head"] is True
    for entry in snapshot["snapshot_shas"]:
        assert entry["is_ancestor_of_head"] is True
    assert row["evidence"]["CURRENT_RELEASE_CONSUMERS"] == 0
    assert row["evidence"]["history"]["preserved_in_git_history"] is True


def test_the_active_artifact_declares_a_producer_that_resolves(payload) -> None:
    row = row_for(payload, gate.DISPOSITION_ACTIVE)
    producer = row["evidence"]["producer"]
    assert producer["generated_by_resolves"] is True
    assert (ROOT / producer["producer_path"]).is_file()
    assert producer["producer_path"] in producer["scripts_declaring_the_target"]
    assert payload["summary"]["CURRENT_PREFLIGHT_PROVENANCE"] == "PASS"


def test_the_docket_is_data_not_code() -> None:
    entries, sources = gate.load_docket()
    assert sources, "le docket vit dans une decision humaine, pas dans le code"
    for source in sources:
        assert source.startswith("audit/HUMAN_DECISION_")
    source_code = (
        ROOT / "scripts/build_release_artifact_provenance_disposition.py"
    ).read_text(encoding="utf-8")
    for entry in entries:
        assert entry["path"] not in source_code


def test_the_published_artifact_is_reproducible() -> None:
    built = gate.build_payload()
    assert gate.JSON_TARGET.read_text(encoding="utf-8") == gate.render_json(built)
    assert gate.MD_TARGET.read_text(encoding="utf-8") == gate.render_markdown(built)
    assert gate.main(["--check"]) == 0


# ---------------------------------------------------------------------------
# Le scanner voit bien les consommateurs quand il y en a
# ---------------------------------------------------------------------------
def test_the_reference_scanner_is_not_vacuous() -> None:
    """Sur un artefact reellement consomme, le scanner compte le consommateur."""

    consumed = next(
        artifact
        for artifact in sorted((ROOT / "audit").glob("*.json"))
        if any(
            artifact.name in script.read_text(encoding="utf-8", errors="replace")
            for script in sorted((ROOT / "scripts").rglob("*.py"))
            if "__pycache__" not in script.parts
            and script.name != "build_release_artifact_provenance_disposition.py"
        )
    )
    references = gate.references_to(
        consumed.relative_to(ROOT).as_posix(), None, []
    )
    assert any(row["role"] == gate.ROLE_RELEASE_CONSUMER for row in references)


def test_reference_roles_separate_release_from_history() -> None:
    assert gate._classify_reference("scripts/x.py", None, []) == (
        gate.ROLE_RELEASE_CONSUMER
    )
    assert gate._classify_reference("tests/x.py", None, []) == gate.ROLE_TEST
    assert gate._classify_reference("audit/X.md", None, []) == gate.ROLE_COMPANION
    assert gate._classify_reference("audit/Y.json", None, []) == gate.ROLE_PROVENANCE
    assert gate._classify_reference("scripts/p.py", "scripts/p.py", []) == (
        gate.ROLE_PRODUCER
    )


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------
def test_mutation_an_active_artifact_without_producer_is_refuted() -> None:
    entry = {
        "path": "audit/FIXTURE.json",
        "disposition": gate.DISPOSITION_ACTIVE,
        "required_evidence": {"PROVENANCE": "PASS"},
    }
    rows = gate.evaluate([entry], {"audit/FIXTURE.json": _evidence()})
    assert rows[0]["verdict"] == "REFUTED"
    assert "ACTIVE_WITHOUT_PRODUCER" in rows[0]["failures"]


def test_mutation_a_historical_artifact_still_consumed_is_refuted() -> None:
    entry = {
        "path": "audit/FIXTURE.json",
        "disposition": gate.DISPOSITION_OBSOLETE,
        "required_evidence": {"CURRENT_RELEASE_CONSUMERS": 0},
    }
    evidence = _evidence(
        CURRENT_RELEASE_CONSUMERS=1,
        references=[{"path": "scripts/reader.py", "role": gate.ROLE_RELEASE_CONSUMER}],
    )
    rows = gate.evaluate([entry], {"audit/FIXTURE.json": evidence})
    assert rows[0]["verdict"] == "REFUTED"
    assert "HISTORICAL_BUT_STILL_CONSUMED" in rows[0]["failures"]
    assert "CURRENT_RELEASE_CONSUMERS_EXPECTED_0_OBSERVED_1" in rows[0]["failures"]


def test_mutation_a_snapshot_sha_that_is_not_an_ancestor_is_refuted() -> None:
    entry = {
        "path": "audit/FIXTURE.json",
        "disposition": gate.DISPOSITION_SUPERSEDED,
        "snapshot_sha_fields": ["upstream_sha"],
        "required_evidence": {"SNAPSHOT_SHAS_ARE_ANCESTORS_OF_HEAD": True},
    }
    evidence = _evidence(
        snapshot={
            "snapshot_shas": [
                {"field": "upstream_sha", "sha": "dead", "is_ancestor_of_head": False}
            ],
            "all_ancestors_of_head": False,
        }
    )
    rows = gate.evaluate([entry], {"audit/FIXTURE.json": evidence})
    assert rows[0]["verdict"] == "REFUTED"
    assert any("SNAPSHOT_SHAS" in failure for failure in rows[0]["failures"])


def test_mutation_an_unnamed_disposition_counts_as_unknown() -> None:
    entry = {"path": "audit/FIXTURE.json", "disposition": "PROBABLY_FINE"}
    rows = gate.evaluate([entry], {"audit/FIXTURE.json": _evidence()})
    assert rows[0]["verdict"] == "REFUTED"
    assert "DISPOSITION_UNKNOWN:PROBABLY_FINE" in rows[0]["failures"]


def test_mutation_an_artifact_erased_from_git_history_is_refuted() -> None:
    entry = {"path": "audit/FIXTURE.json", "disposition": gate.DISPOSITION_OBSOLETE}
    evidence = _evidence(
        history={
            "tracked_at_head": False,
            "commits_touching_the_artifact": 0,
            "preserved_in_git_history": False,
        }
    )
    rows = gate.evaluate([entry], {"audit/FIXTURE.json": evidence})
    assert rows[0]["verdict"] == "REFUTED"
    assert "GIT_HISTORY_NOT_PRESERVED" in rows[0]["failures"]


def test_mutation_a_requirement_the_ledger_cannot_verify_is_refuted() -> None:
    entry = {
        "path": "audit/FIXTURE.json",
        "disposition": gate.DISPOSITION_OBSOLETE,
        "required_evidence": {"SOMEONE_LOOKED_AT_IT": True},
    }
    rows = gate.evaluate([entry], {"audit/FIXTURE.json": _evidence()})
    assert rows[0]["verdict"] == "REFUTED"
    assert "UNVERIFIABLE_REQUIREMENT:SOMEONE_LOOKED_AT_IT" in rows[0]["failures"]
