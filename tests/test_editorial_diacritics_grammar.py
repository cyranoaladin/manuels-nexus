"""Une correction d'accent ne doit jamais etre un pari de grammaire.

`determine` n'est pas un mot francais, mais il admet DEUX accentuations
correctes : `determine` accentue (present) et le participe. Choisir le
participe par defaut ecrit "ce qui determine F" au participe -- une faute de
francais introduite par le correcteur lui-meme.

Ces formes ne sont donc pas des fautes d'accent : ce sont des ambiguites
grammaticales. Elles appartiennent au registre d'arbitrage, jamais au
correcteur automatique.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_editorial_diacritics as A  # noqa: E402


#: Verbes du premier groupe : la forme sans accent recouvre le present
#: (accent sur la seule voyelle interne) ET le participe (accent final).
GRAMMAR_AMBIGUOUS = (
    "demontre",
    "determine",
    "equilibre",
    "majore",
    "minore",
    "modelise",
)


@pytest.mark.parametrize("form", GRAMMAR_AMBIGUOUS)
def test_a_grammar_ambiguous_form_is_never_auto_corrected(form: str) -> None:
    assert form not in A.UNAMBIGUOUS, (
        f"{form!r} admet deux accentuations correctes : le correcteur "
        "choisirait la grammaire a la place de l'auteur"
    )


@pytest.mark.parametrize("form", GRAMMAR_AMBIGUOUS)
def test_a_grammar_ambiguous_form_stays_visible_for_arbitration(form: str) -> None:
    """Retiree du correcteur, la forme doit rester COMPTEE, pas disparaitre."""

    assert form in A.AMBIGUOUS


# -- Les phrases exactes que le correcteur avait corrompues ------------------


@pytest.mark.parametrize(
    "sentence",
    [
        r"$C = y_0 - G(x_0)$, ce qui determine $F$ de maniere unique.",
        r"la fonction ne modelise pas une repartition complete.",
        r"la valeur d'equilibre de la suite",
        r"elle ne le demontre pas (fiche M4 pour la preuve)",
        r"on determine l'inverse de $a$ modulo $n$",
        r"Suite auxiliaire centree sur l'equilibre.",
    ],
)
def test_the_corrector_leaves_these_sentences_untouched(sentence: str) -> None:
    assert A.fix_text(sentence) == sentence


def test_a_participle_with_only_one_spelling_is_still_corrected() -> None:
    """`majoree` ne recouvre AUCUN present : la corriger ne tranche rien.

    L'exclusion porte sur l'ambiguite grammaticale, pas sur le participe.
    """

    source = r"Conjecture : $(u_n)$ est croissante, majoree par 4."
    assert A.fix_text(source) == r"Conjecture : $(u_n)$ est croissante, majorée par 4."


# -- L'invariant de la table -------------------------------------------------


def test_no_entry_bets_on_a_first_group_participle() -> None:
    """Garde-fou : aucune entree ne doit ajouter un accent FINAL a un verbe.

    Les noms en -ite (egalite, propriete) ajoutent aussi un accent final, mais
    leur radical n'est pas un verbe du premier groupe : ils sont sans risque,
    comme les quelques noms nommes ci-dessous.
    """

    #: Noms, non verbes : une seule accentuation existe.
    NOUNS = ("degre", "degres", "ete")
    betting = sorted(
        wrong
        for wrong, right in A.UNAMBIGUOUS.items()
        if right.endswith(("é", "és"))
        and not wrong.endswith(("ite", "ites", "te", "tes"))
        and wrong not in NOUNS
    )
    assert betting == ["enonce", "enonces"], (
        "seules les formes dont le nom est la seule lecture possible dans ce "
        f"corpus sont tolerees ; trouve : {betting}"
    )
