"""La permutation des cles preserve tout sauf la lettre.

La politique editoriale de distribution des cles fait de la lettre une
propriete de rendu. Ces tests generiques fixent le contrat des deux cotes :

- une permutation qui emporte diagnostics et renvois laisse chaque assertion
  scientifique inchangee, et la cle suit sa valeur ;
- une permutation qui NE deplace PAS les diagnostics est detectee ;
- le helper de correspondance par contenu refuse toute ambiguite plutot que de
  choisir arbitrairement.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

import _qcm_par_contenu as par_contenu  # noqa: E402
import rebalance_qcm_key_distribution as rebalance  # noqa: E402


def _question() -> dict:
    return {
        "id": "Q1",
        "capacite": "C1",
        "enonce": "Quelle est la dérivée de $x^2$ ?",
        "options": {"A": "$x$", "B": "$2x$", "C": "$x^2$", "D": "$2$"},
        "correcte": "B",
        "diagnostics": {
            "A": {"erreur": "oubli du facteur 2", "renvoi": "C1, derivee de x^n"},
            "C": {"erreur": "recopie sans deriver", "renvoi": "C1, derivee de x^n"},
            "D": {"erreur": "derive deux fois", "renvoi": "C1, derivee de x^n"},
        },
    }


# -- La permutation legitime ne change aucun invariant scientifique ----------


def test_a_swap_moves_key_diagnostic_and_remediation_together() -> None:
    question = _question()
    avant_valeur = par_contenu.option_correcte(question)
    avant_diag = dict(question["diagnostics"])

    rebalance._swap(question, "A")

    assert question["correcte"] == "A"
    assert par_contenu.option_correcte(question) == avant_valeur
    assert question["options"]["A"] == "$2x$"
    # Le diagnostic suit son option : "oubli du facteur 2" reste attache a $x$.
    assert question["diagnostics"]["B"]["erreur"] == avant_diag["A"]["erreur"]
    assert question["diagnostics"]["B"]["renvoi"] == avant_diag["A"]["renvoi"]
    assert "A" not in question["diagnostics"]


def test_content_addressing_is_invariant_under_swap() -> None:
    question = _question()
    reference = {
        "cle": par_contenu.option_correcte(question),
        "diag": par_contenu.diagnostic_de_option(question, "$x^2$"),
    }
    for cible in ("A", "C", "D", "B"):
        permutee = copy.deepcopy(question)
        rebalance._swap(permutee, cible)
        assert par_contenu.option_correcte(permutee) == reference["cle"]
        assert (
            par_contenu.diagnostic_de_option(permutee, "$x^2$") == reference["diag"]
        )
        assert permutee["correcte"] == par_contenu.lettre_de_option(permutee, "$2x$")


# -- La permutation ILLEGITIME est detectee ----------------------------------


def test_a_letter_only_swap_that_forgets_diagnostics_is_caught() -> None:
    question = _question()
    # Falsification : echanger les options SANS deplacer les diagnostics.
    question["options"]["A"], question["options"]["B"] = (
        question["options"]["B"],
        question["options"]["A"],
    )
    question["correcte"] = "A"

    # Le diagnostic attache a la lettre A decrit "oubli du facteur 2" -- mais
    # la lettre A porte desormais la bonne reponse : la liaison est rompue.
    with pytest.raises(par_contenu.OptionIntrouvable):
        par_contenu.diagnostic_de_option(question, "$2x$")


# -- Les collisions de correspondance sont refusees --------------------------


def test_two_options_with_the_same_normalised_text_are_ambiguous() -> None:
    question = _question()
    question["options"]["D"] = "$2X$"  # meme texte apres normalisation ? non --
    question["options"]["D"] = "$2x$"  # collision reelle avec B

    with pytest.raises(par_contenu.OptionIntrouvable):
        par_contenu.lettre_de_option(question, "$2x$")


def test_accent_variants_of_the_same_option_are_ambiguous() -> None:
    question = _question()
    question["options"]["A"] = "reponse exacte"
    question["options"]["C"] = "réponse exacte"

    with pytest.raises(par_contenu.OptionIntrouvable):
        par_contenu.lettre_de_option(question, "reponse exacte")


def test_a_missing_option_is_an_error_not_an_empty_match() -> None:
    with pytest.raises(par_contenu.OptionIntrouvable):
        par_contenu.lettre_de_option(_question(), "$3x$")


def test_equivalent_values_like_one_half_are_not_silently_merged() -> None:
    """$1/2$ et $3/6$ sont textuellement distincts : aucun des deux ne matche
    une recherche de l'autre, et l'equivalence mathematique reste l'affaire du
    validateur d'equivalence, jamais du correspondancier textuel."""

    question = _question()
    question["options"]["A"] = "$1/2$"
    question["options"]["D"] = "$3/6$"

    assert par_contenu.lettre_de_option(question, "$1/2$") == "A"
    assert par_contenu.lettre_de_option(question, "$3/6$") == "D"
