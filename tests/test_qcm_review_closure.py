"""La clôture des QCM doit prouver, pas ressembler.

Deux erreurs symétriques la menacent. Une dérivation qui lirait la clé et la
renverrait : elle ne prouverait rien tout en affichant `PROVEN`. Une revue
conceptuelle qui affirmerait sans réfuter : elle ne distinguerait pas la bonne
réponse d'un distracteur plausible. Ces tests interdisent les deux.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_qcm_review_closure as closure  # noqa: E402
import qcm_reviews as declarations  # noqa: E402

ARTIFACT = ROOT / "audit/QCM_REVIEW_CLOSURE.json"


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_the_artifact_approves_nothing(payload) -> None:
    assert payload["approves_nothing"] is True


def test_every_open_question_is_accounted_for(payload) -> None:
    """Aucun item perdu : les états somment à la population."""
    s = payload["summary"]
    etats = (
        s["QCM_MECHANICAL_PROVEN"] + s["QCM_CONCEPTUAL_REVIEWED"]
        + s["QCM_REVIEW_OPEN"] + s["QCM_KEY_DISAGREEMENTS"]
        + s["QCM_DERIVATION_FAILURES"]
    )
    assert etats == s["QCM_HUMAN_REVIEW_POPULATION"] == len(payload["questions"])


def test_no_question_is_closed_without_a_regime(payload) -> None:
    for ligne in payload["questions"]:
        if ligne["state"] in ("MECHANICALLY_PROVEN", "CONCEPTUALLY_REVIEWED"):
            assert ligne["regime"] in ("MECHANICAL", "CONCEPTUAL"), ligne


def test_a_derivation_never_sees_the_answer_key() -> None:
    """L'indépendance est structurelle : la dérivation ne reçoit que les options.

    On lui donne une question dont la clé est connue de nous, jamais d'elle :
    tout ce qu'elle reçoit est inspecté et doit se limiter aux options.
    """
    recu = {}

    def espionne(options):
        recu["cles"] = sorted(options)
        recu["valeurs"] = sorted(options.values())
        return "A"

    question = {
        "options": {"A": "vrai", "B": "faux"},
        "cle": "A",
        "diagnostics": {"B": {"erreur": "…"}},
    }
    verdict = closure._evaluer_mecanique(question, declarations.PYTHON, espionne)

    assert verdict["state"] == "MECHANICALLY_PROVEN"
    assert recu["cles"] == ["A", "B"]
    assert recu["valeurs"] == ["faux", "vrai"]
    # Ni la clé ni les diagnostics n'ont pu être lus : ils ne sont pas passés.
    assert "cle" not in recu and "diagnostics" not in recu


def test_a_derivation_cannot_mutate_the_question() -> None:
    """Une dérivation qui écrirait dans les options ne doit pas contaminer."""
    def vandale(options):
        options["A"] = "réécrit"
        return "A"

    question = {"options": {"A": "vrai", "B": "faux"}, "cle": "A"}
    closure._evaluer_mecanique(question, declarations.PYTHON, vandale)
    assert question["options"]["A"] == "vrai"


def test_a_wrong_key_is_reported_not_absorbed() -> None:
    """Si la clé et la dérivation divergent, l'artefact le DIT."""
    question = {"options": {"A": "vrai", "B": "faux"}, "cle": "B"}
    verdict = closure._evaluer_mecanique(
        question, declarations.PYTHON, lambda options: "A"
    )
    assert verdict["state"] == "KEY_DISAGREEMENT"
    assert "A" in verdict["detail"] and "B" in verdict["detail"]


def test_a_derivation_that_does_not_conclude_is_a_failure() -> None:
    def indecise(options):
        raise ValueError("deux options conviennent")

    question = {"options": {"A": "vrai", "B": "faux"}, "cle": "A"}
    verdict = closure._evaluer_mecanique(
        question, declarations.PYTHON, indecise
    )
    assert verdict["state"] == "DERIVATION_FAILED"


def test_a_review_missing_one_refutation_is_refused() -> None:
    question = {
        "options": {"A": "vrai", "B": "faux", "C": "faux aussi"},
        "cle": "A",
    }
    revue = {
        "reponse": "A",
        "raisonnement": "parce que.",
        "source_cours": "scripts/qcm_reviews.py",
        "source_programme": "X::C1",
        "refutations": {"B": "B est faux parce qu'il confond deux notions."},
    }
    verdict = closure._evaluer_conceptuelle(question, revue, ROOT)
    assert verdict["state"] == "DERIVATION_FAILED"
    assert "C" in verdict["detail"]


def test_a_review_naming_an_absent_course_is_refused() -> None:
    question = {"options": {"A": "vrai", "B": "faux"}, "cle": "A"}
    revue = {
        "reponse": "A",
        "raisonnement": "parce que.",
        "source_cours": "NSI/chapitres/CHAPITRE-QUI-N-EXISTE-PAS/cours/x.tex",
        "source_programme": "X::C1",
        "refutations": {"B": "B confond la précondition et la postcondition."},
    }
    verdict = closure._evaluer_conceptuelle(question, revue, ROOT)
    assert verdict["state"] == "DERIVATION_FAILED"
    assert "absent du dépôt" in verdict["detail"]


def test_a_review_with_a_token_refutation_is_refused() -> None:
    """« Faux. » n'établit rien, et ne doit pas passer pour une réfutation."""
    question = {"options": {"A": "vrai", "B": "faux"}, "cle": "A"}
    revue = {
        "reponse": "A",
        "raisonnement": "parce que.",
        "source_cours": "scripts/qcm_reviews.py",
        "source_programme": "X::C1",
        "refutations": {"B": "Faux."},
    }
    verdict = closure._evaluer_conceptuelle(question, revue, ROOT)
    assert verdict["state"] == "DERIVATION_FAILED"
    assert "trop brèves" in verdict["detail"]


def test_every_named_course_object_exists(payload) -> None:
    for ligne in payload["questions"]:
        chemin = ligne.get("source_cours")
        if chemin:
            assert (ROOT / chemin).is_file(), ligne


def test_the_declared_reviews_cover_exactly_the_open_population(payload) -> None:
    declarees = set(declarations.MECHANICAL_DERIVATIONS) | set(
        declarations.CONCEPTUAL_REVIEWS
    )
    population = {
        (ligne["chapter"], ligne["question_id"]) for ligne in payload["questions"]
    }
    assert declarees == population, sorted(declarees ^ population)


def test_the_closure_is_reproducible(payload) -> None:
    """Un artefact recopié à la main divergerait de son producteur."""
    reconstruit = closure.build()
    assert reconstruit["closure_digest"] == payload["closure_digest"]
    assert reconstruit["summary"] == payload["summary"]
