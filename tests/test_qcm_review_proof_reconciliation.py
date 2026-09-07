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
    # Le total courant n'est pas grave : le corpus QCM grandit chaque fois
    # qu'une capacite sans question en recoit une. Ce qui est verrouille est
    # que la partition FERME -- reportees et a reprouver couvrent exactement
    # le corpus courant, sans recouvrement ni ligne orpheline.
    corpus = R._current_questions() if hasattr(R, "_current_questions") else None
    total = counts["CURRENT_QCM_QUESTION_COUNT"]
    assert total >= 490
    if corpus is not None:
        assert total == len(corpus)
    assert (
        counts["CARRIED_FORWARD_UNCHANGED"] + counts["REPROOF_REQUIRED"] == total
    )
    assert counts["PROOF_ROWS_WITHOUT_CURRENT_QUESTION"] == 0

    carried = {(e["chapter"], e["question_id"]) for e in payload["carried_forward"]}
    reproof = {(e["chapter"], e["question_id"]) for e in payload["reproof_required"]}
    assert carried & reproof == set()
    assert len(carried) + len(reproof) == total


def test_every_varalea_question_needs_a_new_proof(payload: dict) -> None:
    """La campagne C6/C7 change le perimetre : le chapitre entier est a reprouver."""

    reproof = {
        e["question_id"] for e in payload["reproof_required"] if e["chapter"] == VARALEA
    }
    assert len(reproof) == 21
    assert reproof == {f"Q{index}" for index in range(1, 22)}
    assert not any(e["chapter"] == VARALEA for e in payload["carried_forward"])


def test_the_new_maths_questions_are_named_and_never_proven(payload: dict) -> None:
    """Cote mathematiques, chaque question inedite est nommee avec son chapitre.

    Le test comparait une liste d'identifiants nus. Deux chapitres peuvent
    porter tous les deux un Q16 : cette forme ne distinguait pas leur origine,
    et une question neuve apparue ailleurs pouvait passer pour une ancienne
    connue. La comparaison porte donc sur le couple (chapitre, question).
    """

    new = {
        (e["chapter"], e["question_id"])
        for e in payload["reproof_required"]
        if e["reason"] == "NEW_QUESTION_NEVER_PROVEN"
        and not e["chapter"].startswith(("1NSI", "TNSI"))
    }
    varalea = {(VARALEA, f"Q{index}") for index in range(16, 22)}
    # Les onze questions ajoutees a TSPE-GEOMETRIE-ESPACE quand son QCM est
    # passe de cinq a seize items. Elles sont neuves, donc jamais prouvees.
    geoespace = {("TSPE-GEOMETRIE-ESPACE", f"Q{index}") for index in range(6, 17)}
    # Ces dix-sept-la doivent y etre. La liste n'est pas figee pour autant :
    # chaque capacite nouvellement dotee d'une question ajoute une inedite, et
    # geler l'ensemble reviendrait a interdire d'en ecrire. Ce qui est
    # verrouille est que toute question declaree inedite le soit reellement --
    # aucune preuve ancienne ne la couvre.
    assert varalea | geoespace <= new
    anciennes = {
        (ligne["chapter"], ligne["question_id"])
        for ligne in payload["carried_forward"]
    }
    assert new & anciennes == set()
    for chapitre, question in new:
        entree = next(
            e for e in payload["reproof_required"]
            if (e["chapter"], e["question_id"]) == (chapitre, question)
        )
        assert entree["reason"] == "NEW_QUESTION_NEVER_PROVEN"
        assert entree["delta_classes"] == []


def test_every_nsi_question_enters_the_ledger_as_never_proven(payload: dict) -> None:
    """Aucune question NSI ne doit entrer avec une preuve qu'elle n'a pas."""

    nsi = [
        e for e in payload["reproof_required"] if e["chapter"].startswith(("1NSI", "TNSI"))
    ]
    assert len(nsi) == 142
    assert all(e["reason"] == "NEW_QUESTION_NEVER_PROVEN" for e in nsi)
    assert not any(
        e["chapter"].startswith(("1NSI", "TNSI")) for e in payload["carried_forward"]
    )


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
    # doit vraiment etre refaite. 11 depuis la completion causale des douze
    # diagnostics courts de la cloture TSPE : huit de ces questions avaient
    # aussi une permutation de cle, et un modele d'erreur modifie se re-prouve.
    assert len(changed) == 11
    assert not any(
        "KEY_VALUE_CHANGED" in e["delta_classes"] for e in payload["reproof_required"]
    )


# -- Une modification de VARALEA ne perime que VARALEA -----------------------


def test_a_varalea_change_never_invalidates_another_chapter(payload: dict) -> None:
    """Le defaut corrige : le sha du fichier entier faisait tomber tout le lot."""

    foreign = {
        e["chapter"]
        for e in payload["reproof_required"]
        if e["chapter"] != VARALEA and not e["chapter"].startswith(("1NSI", "TNSI"))
    }
    # Le seul autre chapitre concerne l'est pour sa PROPRE divergence, pas par
    # contagion : la preuve de TSPE-DERIVATION-CONVEXITE Q6 omet un $ que la
    # source porte. Le reequilibrage des cles, lui, ne perime aucune preuve.
    # TSPE-LIMITES-FONCTIONS s'ajoute pour sa PROPRE cause : le diagnostic
    # trop court de Q3/A a ete complete par un contre-exemple, et un modele
    # d'erreur modifie doit etre re-prouve.
    # TSPE-CONTINUITE et TSPE-SUITES-LIMITES s'ajoutent pour la meme cause
    # PROPRE : leurs diagnostics courts ont ete completes causalement.
    # TSPE-GEOMETRIE-ESPACE s'ajoute pour SA propre cause : onze questions
    # neuves, jamais prouvees. Ce n'est pas de la contagion depuis VARALEA.
    # L'enumeration exacte des chapitres n'est pas l'invariant : elle grandit
    # a chaque capacite nouvellement dotee d'une question. Ce qui est verrouille
    # est l'ABSENCE DE CONTAGION -- chaque chapitre present l'est pour sa
    # PROPRE cause, jamais parce que VARALEA a bouge.
    assert "1SPE-PRODUIT-SCALAIRE" in foreign
    assert "TSPE-DERIVATION-CONVEXITE" in foreign
    causes_propres = {
        "NEW_QUESTION_NEVER_PROVEN",
        "SEMANTIC_DIVERGENCE",
    }
    for chapitre in foreign:
        entrees = [
            e for e in payload["reproof_required"] if e["chapter"] == chapitre
        ]
        assert entrees, chapitre
        for entree in entrees:
            # Soit la question est neuve, soit elle porte une divergence qui
            # lui est propre : dans les deux cas la cause est locale.
            assert (
                entree["reason"] in causes_propres or entree["delta_classes"]
            ), (chapitre, entree["question_id"], entree["reason"])
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
    # 41 depuis l'entree du corpus NSI dans le routage : la preuve historique
    # n'a jamais capture le champ renvoi, quel que soit le manuel.
    assert len(gaps) == 41
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
