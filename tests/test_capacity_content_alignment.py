"""Une capacite se derive du contenu, jamais d'un compteur.

Le remplissage attribuait les codes en tournant sur la table du contrat : un
exercice de convexite devenait `TEXP-ARI-C3` -- « divisibilite, primalite,
chiffrement » -- sans que rien dans son enonce ne l'y rattache. Ces tests
verrouillent les deux voies qui rendent cela impossible, et surtout leurs
deux bords : le detecteur doit voir la rotation reelle, et se taire sur une
progression deliberee.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "audit/CAPACITY_CONTENT_ALIGNMENT.json"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location(
        "capacity_alignment", ROOT / "scripts/build_capacity_content_alignment.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["capacity_alignment"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def payload() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


# --- la voie structurelle -------------------------------------------------


def test_the_historical_rotation_is_detected(producer) -> None:
    """La suite reelle de TEXP-ARITHMETIQUE avant decontamination.

    Cinq exercices authentiques, puis quarante-cinq codes engendres par un
    compteur balayant les neuf capacites du contrat.
    """

    contrat = [f"C{n}" for n in range(1, 10)]
    authentiques = ["C1", "C2", "C4", "C8", "C3"]
    rotation = [contrat[(n - 1) % 9] for n in range(6, 51)]
    verdict = producer.detect_round_robin(authentiques + rotation, contrat)
    assert verdict["detected"] is True
    assert verdict["period"] == 9
    assert verdict["from_index"] == 5


def test_a_deliberate_series_on_one_capacity_is_not_a_rotation(producer) -> None:
    """Quinze exercices de suite sur `C3` sont une serie, pas un compteur.

    Une queue constante est periodique pour n'importe quelle periode : sans le
    garde, tout chapitre bien construit serait accuse.
    """

    verdict = producer.detect_round_robin(["C3"] * 20, ["C1", "C2", "C3"])
    assert verdict["detected"] is False


def test_alternating_two_capacities_is_not_a_rotation(producer) -> None:
    """Dans un chapitre a deux capacites, alterner est la seule progression."""

    verdict = producer.detect_round_robin(["C1", "C2"] * 15, ["C1", "C2"])
    assert verdict["detected"] is False


def test_a_short_run_never_proves_a_counter(producer) -> None:
    contrat = ["C1", "C2", "C3"]
    verdict = producer.detect_round_robin(contrat * 2, contrat)
    assert verdict["detected"] is False


# --- la voie semantique ---------------------------------------------------


def test_a_convexity_exercise_declared_arithmetic_is_refused(producer) -> None:
    """La mutation exigee : un contenu d'analyse sous une capacite d'arithmetique."""

    corps = (
        "\\begin{exercice}{X}{1}{12}\n"
        "Étudier les variations de $f(x) = x^3 - 3x^2 + 2$ sur $\\mathbb{R}$.\n"
        "\\end{exercice}"
    )
    signature = producer.signatures.signature_for("TEXP-ARITHMETIQUE", "C3")
    assert signature is not None
    verdict = producer.evaluate_signature(corps, signature)
    assert verdict["aligned"] is False
    # Un marqueur INTERDIT doit avoir parle : c'est la preuve positive d'un
    # contenu d'analyse. Un simple marqueur requis manquant ne prouverait
    # rien, et ne suffirait pas a fonder un desalignement.
    assert verdict["forbidden_markers_found"], verdict


def test_a_genuine_arithmetic_exercise_is_accepted(producer) -> None:
    corps = (
        "\\begin{exercice}{X}{2}{15}\n"
        "On chiffre une lettre en associant à sa position $m$ la position "
        "$c=(3m+5)\\bmod26$. Justifier que ce chiffrement est déchiffrable.\n"
        "\\end{exercice}"
    )
    signature = producer.signatures.signature_for("TEXP-ARITHMETIQUE", "C3")
    verdict = producer.evaluate_signature(corps, signature)
    assert verdict["aligned"] is True, verdict


def test_a_missing_marker_is_not_a_misalignment(producer) -> None:
    """Ne pas crier au loup : l'absence d'un marqueur n'est pas une preuve.

    Un enonce peut demander une derivee en ecrivant `f'(x)` sans employer le
    mot, ou une limite de suite geometrique sans ecrire « geometrique ». La
    signature ne voit alors rien, mais rien ne dit que la capacite est
    fausse. Compter cela comme un desalignement desarmerait le gate a force
    de faux cris -- et le vrai desalignement passerait avec eux.
    """

    corps = (
        "\\begin{exercice}{X}{1}{12}\n"
        "On chiffre par $c=(3m+5)\\bmod26$ ; calculer $c$ pour $m=1$.\n"
        "\\end{exercice}"
    )
    signature = {"required": [[r"marqueur_absent_du_corpus"]], "forbidden": []}
    verdict = producer.evaluate_signature(corps, signature)
    assert verdict["aligned"] is False
    assert verdict["missing_required_groups"]
    assert verdict["forbidden_markers_found"] == []


def test_an_unsigned_capacity_is_declared_unverified_not_aligned(
    payload: dict,
) -> None:
    """Ne pas compter comme un succes ce qu'on n'a pas verifie."""

    assert payload["summary"]["NO_SIGNATURE_DECLARED"] > 0
    for assignment in payload["assignments"]:
        if assignment["state"] == "NO_SIGNATURE_DECLARED":
            assert assignment["evidence"] is None


def test_the_corpus_carries_no_rotation_and_no_misalignment(payload: dict) -> None:
    assert payload["summary"]["ROUND_ROBIN_CAPACITY_ASSIGNMENT"] == 0
    assert payload["summary"]["CAPACITY_CONTENT_MISALIGNMENT"] == 0
    assert payload["summary"]["STATES_SUM_EQUALS_TOTAL"] is True


def test_the_committed_alignment_matches_the_producer(producer) -> None:
    assert producer.main(["--check"]) == 0


def test_a_periodic_pattern_is_still_published_when_content_explains_it(
    payload: dict,
) -> None:
    """La forme de la suite reste visible, meme quand elle s'explique.

    Un chapitre equilibre -- autant d'exercices par capacite, ecrits dans
    l'ordre du contrat -- produit naturellement une suite periodique. La
    regle structurelle existait faute de preuve de contenu ; quand chaque
    attribution du chapitre est corroboree par sa signature, la periodicite
    n'est plus un soupcon. Elle n'est pas effacee pour autant : le motif est
    publie, et l'ecart entre les deux compteurs dit exactement ce qui a ete
    disculpe et par quoi.
    """

    summary = payload["summary"]
    assert summary["ROUND_ROBIN_PATTERN_CHAPTERS"] >= summary[
        "ROUND_ROBIN_CAPACITY_ASSIGNMENT"
    ]
    assert (
        summary["ROUND_ROBIN_EXPLAINED_BY_CONTENT"]
        == summary["ROUND_ROBIN_PATTERN_CHAPTERS"]
        - summary["ROUND_ROBIN_CAPACITY_ASSIGNMENT"]
    )
    for chapitre in payload["round_robin_pattern_chapters"]:
        info = payload["chapters"][chapitre]
        assert info["round_robin"]["detected"] is True
        if not info["round_robin_unexplained"]:
            assert info["content_corroborated"] is True


def test_a_rotation_without_content_proof_is_never_excused(producer) -> None:
    """Sans signature, une rotation reste une rotation.

    C'est l'etat exact du corpus au moment du remplissage : aucune signature
    declaree, et une suite engendree par un compteur. La disculpe ne doit
    jamais s'appliquer par defaut.
    """

    chapitres = {
        "SANS_PREUVE": {
            "round_robin": {"detected": True},
            "content_corroborated": False,
        }
    }
    assert chapitres["SANS_PREUVE"]["round_robin"]["detected"]
    assert not chapitres["SANS_PREUVE"]["content_corroborated"]
    # Sur le corpus : un chapitre sans signature ne peut pas etre corrobore.
    payload = producer.build()
    for chapitre, info in payload["chapters"].items():
        if info.get("content_corroborated"):
            assignations = [
                a for a in payload["assignments"] if a["chapter"] == chapitre
            ]
            assert assignations
            assert all(a["state"] == "ALIGNED" for a in assignations)
