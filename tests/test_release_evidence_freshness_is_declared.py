"""Une preuve observee sur un autre commit ne peut pas se donner pour courante.

`DOUBLE_BUILD_REPRODUCIBILITY.json` porte le commit qu'il a observe. Quand ce
commit n'est plus le HEAD, la synthese de release continuait pourtant
d'afficher « Reproductibilite Deterministe : PROVEN (12/12) », sans rien qui
distingue une preuve refaite d'une preuve recopiee. Le preflight d'impression,
lui, ne portait aucune provenance du tout.

Une preuve perimee doit se declarer perimee. Elle n'est pas effacee -- elle
reste consultable -- mais elle cesse d'etre presentee comme un acquis courant.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "audit" / "RELEASE_ALL_CHECK.json"


def summary() -> dict:
    return json.loads(REPORT.read_text(encoding="utf-8"))["summary"]


def test_reproducibility_evidence_declares_the_commit_it_observed() -> None:
    payload = summary()
    assert "REPRODUCIBILITY_EVIDENCE_HEAD" in payload
    assert "REPRODUCIBILITY_EVIDENCE_CURRENT" in payload
    assert isinstance(payload["REPRODUCIBILITY_EVIDENCE_CURRENT"], bool)


def test_a_stale_reproducibility_proof_is_never_announced_as_proven() -> None:
    payload = summary()
    if not payload["REPRODUCIBILITY_EVIDENCE_CURRENT"]:
        assert payload["REPRODUCIBILITY_GLOBAL"] == "STALE_EVIDENCE_NOT_REOBSERVED", (
            "une preuve rattachee a un autre commit est presentee comme courante"
        )


def test_the_print_preflight_declares_whether_it_was_reobserved() -> None:
    payload = summary()
    assert "PREFLIGHT_EVIDENCE_CURRENT" in payload
    if not payload["PREFLIGHT_EVIDENCE_CURRENT"]:
        assert payload["PREFLIGHT_ALL_TARGETS"] == "STALE_EVIDENCE_NOT_REOBSERVED"


def test_stale_evidence_cannot_make_a_target_release_ready() -> None:
    payload = json.loads(REPORT.read_text(encoding="utf-8"))
    stale = not (payload["summary"]["REPRODUCIBILITY_EVIDENCE_CURRENT"]
                 and payload["summary"]["PREFLIGHT_EVIDENCE_CURRENT"])
    if stale:
        assert payload["summary"]["CANDIDATE_READY_COUNT"] == 0
        assert all(not t["publish_ready"] for t in payload["targets"])
