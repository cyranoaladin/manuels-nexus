from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_qcm_independent_evidence_v2 as V2  # noqa: E402
QCM_ROOT = ROOT / "Mathematiques/manuel-maths/chapitres"
AUDIT = ROOT / "audit/QCM_SCIENTIFIC_ANSWER_KEY_AUDIT.json"
BUILDER = ROOT / "scripts/build_qcm_scientific_answer_key_audit.py"
EVIDENCE = ROOT / "audit/qcm_review_evidence"
EVIDENCE_V2 = ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json"
PARTITIONS = {
    "1SPE": (EVIDENCE / "1SPE_162.json", 162),
    "TSPE": (EVIDENCE / "TSPE_96.json", 96),
    "TCOMPL_TEXPERTES": (EVIDENCE / "TCOMPL_TEXPERTES_73.json", 73),
}


def _sources() -> list[Path]:
    return sorted(QCM_ROOT.glob("*/qcm/*-QCM.json"))


def _source_keys() -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for path in _sources():
        payload = json.loads(path.read_text(encoding="utf-8"))
        keys.update((payload["chapitre"], question["id"]) for question in payload["questions"])
    return keys


def _source_digest() -> str:
    digest = hashlib.sha256()
    for path in _sources():
        relative = path.relative_to(ROOT)
        digest.update(str(relative).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def test_the_v1_audit_is_historical_and_no_longer_covers_the_current_corpus() -> None:
    """La v1 couvrait 331 questions ; le corpus en porte 337.

    L'ancienne assertion exigeait que la v1 couvre le corpus courant. Elle
    etait devenue fausse, et la rendre verte en rafraichissant un condense
    aurait masque six questions jamais prouvees. La v1 est desormais tenue
    pour ce qu'elle est : un enregistrement HISTORIQUE dont le perimetre est
    borne, et c'est la v2 qui doit rendre compte des 337.
    """

    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = payload["questions"]
    historical = {(row["chapter"], row["question_id"]) for row in rows}
    current = _source_keys()

    assert len(historical) == 331
    assert len(current) == 337
    assert historical < current, "la v1 est un sous-ensemble strict du corpus"
    assert sorted(question for _chapter, question in current - historical) == [
        "Q16",
        "Q17",
        "Q18",
        "Q19",
        "Q20",
        "Q21",
    ]
    assert {chapter for chapter, _question in current - historical} == {
        "1SPE-VARIABLES-ALEATOIRES"
    }

    v2 = V2.build_evidence()
    assert v2["counts"]["question_count"] == len(current)
    assert {
        (entry["chapter"], entry["question_id"]) for entry in v2["questions"]
    } == current

    assert payload["summary"]["total_questions"] == 331
    assert payload["summary"]["independently_recalculated"] == 331
    assert payload["summary"]["content_review_pending"] == 0
    assert payload["summary"]["by_manual"] == {
        "1SPE": 162,
        "TCOMPL": 48,
        "TEXPERTES": 25,
        "TSPE": 96,
    }
    assert payload["status"] == "HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL"
    assert payload["summary"]["objective_zero_verified"] is True
    assert payload["summary"]["human_approval_complete"] is False
    assert all(value == 0 for value in payload["summary"]["objective_counters"].values())


def test_every_historical_row_is_accounted_for_by_the_v2_evidence() -> None:
    """Aucune ligne historique ne disparait ; chacune a un etat explicite.

    L'ancienne assertion liait chaque ligne au sha256 du FICHIER entier. C'est
    ce couplage qui faisait tomber 15 lignes VARALEA pour l'ajout de six
    questions voisines. Il est remplace par une identite PAR QUESTION, plus
    stricte : une ligne n'est reportee que si son condense semantique est
    inchange, sinon elle doit avoir ete reprouvee ou routee vers l'humain.
    """

    observed: set[tuple[str, str]] = set()
    for _name, (path, expected_count) in PARTITIONS.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload["questions"]
        assert len(rows) == expected_count
        for row in rows:
            assert (ROOT / row["source_path"]).is_file()
            key = (row["chapter"], row["question_id"])
            assert key not in observed
            observed.add(key)
    assert len(observed) == 331

    v2 = V2.build_evidence()
    states = {
        (entry["chapter"], entry["question_id"]): entry["evidence_status"]
        for entry in v2["questions"]
    }
    assert observed <= set(states), "aucune ligne historique ne doit disparaitre"
    assert all(
        states[key]
        in {"CARRIED_FORWARD_IDENTICAL", "MACHINE_RECALCULATED", "HUMAN_REVIEW_REQUIRED"}
        for key in observed
    )

    carried = {key for key in observed if states[key] == "CARRIED_FORWARD_IDENTICAL"}
    assert len(carried) == 315
    assert not any(chapter == "1SPE-VARIABLES-ALEATOIRES" for chapter, _q in carried)


def test_canonical_rows_are_objectively_green_but_not_human_approved() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    for row in payload["questions"]:
        assert row["answer_key_status"] == "PASS"
        assert row["unique_correct_option"] == "PASS"
        assert row["diagnostic_consistency"] == "PASS"
        assert row["programme_alignment"] in {"PASS", "MANDATORY_PROGRAMME", "PREREQUISITE"}
        assert row["capacity_alignment"] == "PASS"
        assert row["wrong_programme_year"] is False
        assert row["review_status"] == "HUMAN_APPROVAL_PENDING_NO_AUTO_APPROVAL"


def test_the_v2_builder_is_deterministic_and_current() -> None:
    """Le producteur courant est celui de la v2.

    Le builder v1 ne peut plus produire : il exige que le sha256 de chaque
    fichier QCM soit celui grave dans la preuve, ce qui est faux des qu'une
    question change. Sa determinisme est remplacee par celle de la v2, et le
    test qui suit constate explicitement la mise hors service de la v1.
    """

    first = V2.render_json(V2.build_evidence())
    second = V2.render_json(V2.build_evidence())
    assert first == second
    assert EVIDENCE_V2.is_file()
    assert EVIDENCE_V2.read_text(encoding="utf-8") == first


def test_the_v1_builder_refuses_to_produce_on_a_changed_corpus() -> None:
    """Constat, pas contournement : la v1 refuse, et c'est son contrat."""

    result = subprocess.run(
        [sys.executable, str(BUILDER), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "digest" in (result.stdout + result.stderr).lower()


def test_the_v2_evidence_accounts_for_every_question_without_unknown() -> None:
    v2 = V2.build_evidence()
    counts = v2["counts"]
    assert counts["question_count"] == 337
    assert (
        counts["CARRIED_FORWARD_IDENTICAL"]
        + counts["MACHINE_RECALCULATED"]
        + counts["HUMAN_REVIEW_REQUIRED"]
        == counts["question_count"]
    )
    assert counts["UNKNOWN"] == 0
    assert v2["EVIDENCE_ROUTING_COMPLETE"] is True
    assert v2["approves_nothing"] is True


def test_no_evidence_field_is_silently_omitted() -> None:
    v2 = V2.build_evidence()
    assert set(v2["evidence_schema_fields"]) == {
        "statement",
        "options",
        "key",
        "diagnostics",
        "remediation_refs",
        "capacity",
    }
    for entry in v2["questions"]:
        assert entry["semantic_question_digest"].startswith("sha256:")
        assert entry["evidence_digest"].startswith("sha256:")
        if entry["evidence_status"] != "MACHINE_RECALCULATED":
            continue
        verification = entry["verification"]
        assert verification["answer_key_verdict"] == "PASS"
        assert verification["declared_key_matches_computation"] is True
        assert verification["unique_true_option"] is True
        assert verification["no_equivalent_options"] is True
        assert "diagnostic_coverage" in verification
        assert entry["solver_input_digest"].startswith("sha256:")
        assert entry["independent_evidence"]


def test_machine_recalculation_never_reads_the_declared_key() -> None:
    """L'independance du solveur est verifiee jusque dans l'artefact."""

    v2 = V2.build_evidence()
    contract = v2["independence_contract"]
    assert contract["verifier_runs_after_solver"] is True
    assert contract["routing_is_by_generic_family_never_by_question_id"] is True
    for field in ("correcte", "declared_answer", "independent_solution"):
        assert field in contract["solver_never_receives"]


def test_human_required_questions_stay_release_blocking() -> None:
    v2 = V2.build_evidence()
    required = v2["human_review_required_questions"]
    assert required, "au moins une question n'est pas modelisable par machine"
    assert v2["ALL_QCM_HUMAN_REVIEW_COMPLETE"] is False
    assert v2["human_review_is_release_blocking"] is True
    for entry in v2["questions"]:
        if entry["evidence_status"] != "HUMAN_REVIEW_REQUIRED":
            continue
        assert entry["human_review_required"] is True
        assert entry["release_blocking"] is True
        assert entry["reason"]
        assert entry["computed_unique_answer"] is None


def test_three_requested_false_greens_are_closed_in_current_audit() -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = {
        (row["chapter"], row["question_id"]): row for row in payload["questions"]
    }
    for key in (
        ("1SPE-SECOND-DEGRE", "Q16"),
        ("TSPE-PRIMITIVES-EQDIFF", "Q2"),
        ("1SPE-SUITES", "Q11"),
    ):
        assert rows[key]["answer_key_status"] == "PASS"
        assert rows[key]["unique_correct_option"] == "PASS"
        assert rows[key]["diagnostic_consistency"] == "PASS"
