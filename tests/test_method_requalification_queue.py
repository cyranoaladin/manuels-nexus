"""La file de re-qualification informe le relecteur, elle ne le remplace pas.

Le seul service rendu est de distinguer un changement d'accents d'un
changement de fond. Cette distinction doit etre stricte : le moindre chiffre
deplace doit sortir de la classe ACCENT_ONLY, sans quoi l'information
deviendrait un blanc-seing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_method_requalification_queue as Q  # noqa: E402


# -- Le classifieur ----------------------------------------------------------


def test_adding_accents_alone_is_accent_only() -> None:
    assert Q.classify_change("la derivee est negative", "la dérivée est négative") == (
        "ACCENT_ONLY"
    )


def test_an_identical_text_is_not_a_change() -> None:
    assert Q.classify_change("meme texte", "meme texte") == "UNCHANGED"


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("la dérivée vaut 2", "la dérivée vaut 3"),
        ("f(x) = x^2", "f(x) = x^3"),
        ("la dérivée est positive", "la dérivée est négative"),
        ("un mot", "un mot de plus"),
        ("$u_n = 2n$", "$u_n = 2n + 1$"),
    ],
)
def test_any_other_edit_leaves_the_accent_only_class(before: str, after: str) -> None:
    assert Q.classify_change(before, after) == "SUBSTANTIVE_CHANGE"


def test_a_removed_accent_is_still_only_an_accent_change() -> None:
    """La classe porte sur les accents, dans les deux sens."""

    assert Q.classify_change("dérivée", "derivee") == "ACCENT_ONLY"


def test_the_class_is_not_fooled_by_whitespace() -> None:
    assert Q.classify_change("deux  mots", "deux mots") == "SUBSTANTIVE_CHANGE"


# -- L'artefact --------------------------------------------------------------


@pytest.fixture(scope="module")
def payload() -> dict:
    return Q.build_queue()


def test_the_queue_never_approves_and_never_requalifies(payload: dict) -> None:
    assert payload["approves_nothing"] is True
    assert payload["machine_cannot_requalify"] is True
    serialised = json.dumps(payload, ensure_ascii=False)
    assert "APPROVED" not in serialised
    assert all(
        item.get("requalification") == "REQUIRED_HUMAN"
        for item in payload["items"]
        if item["state"] == "STALE"
    )


def test_every_stale_entry_stays_release_blocking(payload: dict) -> None:
    stale = [item for item in payload["items"] if item["state"] == "STALE"]
    assert stale, "la campagne diacritiques a bien perime des qualifications"
    assert all(item["release_blocking"] is True for item in stale)


def test_the_comparison_never_uses_a_moving_reference(payload: dict) -> None:
    """Le texte compare est celui que la decision a fige, pas HEAD.

    Contre HEAD, la classe s'evanouissait des le commit de la correction ;
    contre `baseline_sha`, 72 fiches n'existaient pas encore. La reference est
    donc la revision dont le contenu porte `method_source_sha`.
    """

    assert payload["compared_against"] == "method_source_sha de chaque qualification"
    stale = [item for item in payload["items"] if item["state"] == "STALE"]
    # Les classes PARTITIONNENT les perimees. `ACCENT_ONLY` n'est plus la
    # seule : reecrire une fiche qualifiee produit un `SUBSTANTIVE_CHANGE`,
    # et les confondre ferait passer une reecriture pour une correction
    # d'accent.
    assert sum(payload["change_classes"].values()) == len(stale)
    assert set(payload["change_classes"]) <= {"ACCENT_ONLY", "SUBSTANTIVE_CHANGE"}
    assert payload["change_classes"] == {
        klass: sum(1 for item in stale if item["change_class"] == klass)
        for klass in payload["change_classes"]
    }


def test_the_totals_close(payload: dict) -> None:
    totals = payload["totals"]
    assert totals["still_current"] + len(payload["items"]) == (
        totals["method_qualifications"]
    )
    assert totals["stale_requiring_human_requalification"] == sum(
        payload["stale_by_chapter"].values()
    )


def test_the_committed_artifact_is_current() -> None:
    stored = ROOT / "audit/METHOD_REQUALIFICATION_QUEUE.json"
    assert stored.is_file()
    assert json.loads(stored.read_text(encoding="utf-8")) == json.loads(
        Q.render_json(Q.build_queue())
    )


def test_accent_only_refuses_anything_beyond_the_accents() -> None:
    """ACCENT_ONLY n'est vrai que si TOUT le reste est identique.

    Cette classe decide si une qualification humaine peut etre presumee
    encore pertinente. Une classification trop large ferait passer une
    reecriture pour une correction de diacritiques, et laisserait une
    approbation couvrir un texte qu'elle n'a jamais lu.
    """
    classify = Q.classify_change

    assert classify("La suite est croissante.", "La suite est croissante.") == (
        "UNCHANGED"
    )
    assert classify(
        "La suite est definie par recurrence.",
        "La suite est définie par récurrence.",
    ) == "ACCENT_ONLY"

    # Accent CORRIGE, mais un mot change en meme temps.
    assert classify(
        "La suite est definie par recurrence.",
        "La suite est définie par récurrence stricte.",
    ) == "SUBSTANTIVE_CHANGE"

    # Accent corrige, mais une formule change.
    assert classify(
        "On pose u_{n+1} = 2u_n, definie ainsi.",
        "On pose u_{n+1} = 3u_n, définie ainsi.",
    ) == "SUBSTANTIVE_CHANGE"

    # Accent corrige, mais la capacite declaree change.
    assert classify(
        '% META: {"capacites_codes": ["C1"]}\nMethode definie.',
        '% META: {"capacites_codes": ["C2"]}\nMéthode définie.',
    ) == "SUBSTANTIVE_CHANGE"

    # Un mot retire sans aucun accent en jeu.
    assert classify("un deux trois", "un trois") == "SUBSTANTIVE_CHANGE"

    # La ponctuation n'est pas un accent.
    assert classify("Soit n un entier", "Soit n, un entier") == (
        "SUBSTANTIVE_CHANGE"
    )
