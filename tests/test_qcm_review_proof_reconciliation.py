"""La preuve de revue QCM doit avoir une identite PAR QUESTION.

La preuve historique lie chaque ligne au sha256 du fichier entier : une seule
question modifiee perime toutes les lignes du fichier. Ces tests fixent la
semantique de remplacement, dans les deux sens.

Aucun de ces tests n'approuve quoi que ce soit : la reconciliation dit
seulement quelles preuves sont reportables et lesquelles doivent etre refaites.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_qcm_review_proof_reconciliation as R  # noqa: E402

ARTIFACT = ROOT / "audit" / "QCM_REVIEW_PROOF_RECONCILIATION.json"
VARALEA = "1SPE-VARIABLES-ALEATOIRES"


@pytest.fixture(scope="module")
def payload() -> dict:
    return R.build_reconciliation()


# -- Le compte doit fermer, par identifiants exacts --------------------------


def test_the_partition_covers_the_current_corpus_exactly(payload: dict) -> None:
    counts = payload["counts"]
    assert counts["OLD_PROOF_QUESTION_COUNT"] == 331
    assert counts["CURRENT_QCM_QUESTION_COUNT"] == 337
    assert (
        counts["CARRIED_FORWARD_UNCHANGED"] + counts["REPROOF_REQUIRED"]
        == counts["CURRENT_QCM_QUESTION_COUNT"]
    )
    assert counts["PROOF_ROWS_WITHOUT_CURRENT_QUESTION"] == 0

    carried = {(e["chapter"], e["question_id"]) for e in payload["carried_forward"]}
    reproof = {(e["chapter"], e["question_id"]) for e in payload["reproof_required"]}
    assert carried & reproof == set()
    assert len(carried) + len(reproof) == 337


def test_every_varalea_question_needs_a_new_proof(payload: dict) -> None:
    """La campagne C6/C7 change le perimetre : le chapitre entier est a reprouver."""

    reproof = {
        e["question_id"] for e in payload["reproof_required"] if e["chapter"] == VARALEA
    }
    assert len(reproof) == 21
    assert reproof == {f"Q{index}" for index in range(1, 22)}
    assert not any(e["chapter"] == VARALEA for e in payload["carried_forward"])


def test_the_six_new_questions_are_named_and_never_proven(payload: dict) -> None:
    new = sorted(
        e["question_id"]
        for e in payload["reproof_required"]
        if e["reason"] == "NEW_QUESTION_NEVER_PROVEN"
    )
    assert new == ["Q16", "Q17", "Q18", "Q19", "Q20", "Q21"]


def test_the_only_real_option_change_is_flagged_as_semantic(payload: dict) -> None:
    """Q1 remplace 1/2 par 1/5 : ce n'est pas un simple changement de rendu."""

    entry = next(
        e
        for e in payload["reproof_required"]
        if e["chapter"] == VARALEA and e["question_id"] == "Q1"
    )
    assert "DISTRACTOR_SEMANTIC_CHANGE" in entry["delta_classes"]

    reordered_only = [
        e["question_id"]
        for e in payload["reproof_required"]
        if e["chapter"] == VARALEA
        and "OPTION_REORDER_ONLY" in e["delta_classes"]
        and "DISTRACTOR_SEMANTIC_CHANGE" not in e["delta_classes"]
    ]
    assert len(reordered_only) == 0
    assert "Q1" not in reordered_only


def test_a_key_that_only_moves_letter_is_not_a_value_change(payload: dict) -> None:
    changed = [
        e
        for e in payload["reproof_required"]
        if "KEY_POSITION_CHANGED_BUT_VALUE_SAME" in e["delta_classes"]
    ]
    # Le condense etant indexe par VALEUR, une permutation ne fait plus
    # sortir la question du report : seules restent celles dont la preuve
    # doit vraiment etre refaite.
    assert len(changed) == 2
    assert not any(
        "KEY_VALUE_CHANGED" in e["delta_classes"] for e in payload["reproof_required"]
    )


# -- Une modification de VARALEA ne perime que VARALEA -----------------------


def test_a_varalea_change_never_invalidates_another_chapter(payload: dict) -> None:
    """Le defaut corrige : le sha du fichier entier faisait tomber tout le lot."""

    foreign = {
        e["chapter"] for e in payload["reproof_required"] if e["chapter"] != VARALEA
    }
    # Le seul autre chapitre concerne l'est pour sa PROPRE divergence, pas par
    # contagion : la preuve de TSPE-DERIVATION-CONVEXITE Q6 omet un $ que la
    # source porte. Le reequilibrage des cles, lui, ne perime aucune preuve.
    assert foreign == {"TSPE-DERIVATION-CONVEXITE"}
    entry = next(
        e for e in payload["reproof_required"] if e["chapter"] == "TSPE-DERIVATION-CONVEXITE"
    )
    assert entry["question_id"] == "Q6"
    # Le reequilibrage a permute ses options ; la divergence de transcription
    # du diagnostic, elle, est bien la raison pour laquelle elle reste a
    # reprouver, la permutation seule ne perimant aucune preuve.
    assert "DIAGNOSTIC_TEXT_CHANGE" in entry["delta_classes"]
    assert "KEY_VALUE_CHANGED" not in entry["delta_classes"]

    carried_chapters = {e["chapter"] for e in payload["carried_forward"]}
    assert len(carried_chapters) == 34


# -- Le condense semantique -------------------------------------------------


def test_the_semantic_digest_ignores_accents_only(payload: dict) -> None:
    base = {
        "capacity": "C1",
        "statement": "La derivee est :",
        "options": {"A": "$1$", "B": "$2$"},
        "declared_answer": "A",
        "error_models": {"B": "erreur"},
    }
    accented = copy.deepcopy(base)
    accented["statement"] = R._normalise("La dérivée est :")
    assert R.semantic_question_digest(base) == R.semantic_question_digest(accented)


def test_the_semantic_digest_reacts_to_an_option_value(payload: dict) -> None:
    base = {
        "capacity": "C1",
        "statement": "s",
        "options": {"A": "$1/2$", "B": "$2$"},
        "declared_answer": "B",
        "error_models": {},
    }
    changed = copy.deepcopy(base)
    changed["options"]["A"] = "$1/5$"
    assert R.semantic_question_digest(base) != R.semantic_question_digest(changed)


def test_the_semantic_digest_reacts_to_an_error_model(payload: dict) -> None:
    base = {
        "capacity": "C1",
        "statement": "s",
        "options": {"A": "$1$"},
        "declared_answer": "A",
        "error_models": {"A": "modele"},
    }
    changed = copy.deepcopy(base)
    changed["error_models"]["A"] = "autre modele"
    assert R.semantic_question_digest(base) != R.semantic_question_digest(changed)


# -- Lacunes de couverture ---------------------------------------------------


def test_uncaptured_renvois_are_reported_not_absorbed(payload: dict) -> None:
    """La preuve historique n'a pas capture renvoi ; l'ecart doit etre visible."""

    gaps = payload["proof_field_coverage_gaps"]
    assert len(gaps) == 4
    assert {gap["field"] for gap in gaps} == {"diagnostics.renvoi"}
    assert all(gap["options"] for gap in gaps)
    assert payload["semantic_digest_contract"]["excluded"] == ["diagnostics.renvoi"]


# -- L'artefact ne fabrique aucune approbation -------------------------------


def test_the_artifact_approves_and_rebinds_nothing(payload: dict) -> None:
    assert payload["approves_nothing"] is True
    assert payload["rebinds_nothing"] is True
    assert payload["historical_proof_status"] == "HISTORICAL"
    assert (
        payload["semantic_digest_contract"][
            "never_use_whole_file_sha_as_per_question_identity"
        ]
        is True
    )
    serialised = json.dumps(payload, ensure_ascii=False)
    assert "APPROVED" not in serialised


def test_the_committed_artifact_is_current() -> None:
    assert ARTIFACT.is_file()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert stored == json.loads(R.render_json(R.build_reconciliation()))


def test_the_builder_is_deterministic() -> None:
    assert R.render_json(R.build_reconciliation()) == R.render_json(
        R.build_reconciliation()
    )
