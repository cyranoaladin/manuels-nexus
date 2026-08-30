"""Adresser une option ou un diagnostic par son CONTENU, jamais par sa lettre.

La politique editoriale Nexus impose une distribution des cles : les quatre
lettres employees, ecart au plus 1, deux bonnes reponses consecutives au plus
sur la meme lettre. Le reequilibrage permute donc les options -- en emportant
leur diagnostic, dont la liaison est verifiee valeur par valeur.

Une assertion ecrite sur `options["C"]` ou `diagnostics["A"]` prend alors pour
invariant une position que la politique rend deliberement mobile. Elle casse au
premier reequilibrage sans qu'aucune mathematique n'ait bouge. Ces aides
expriment la meme exigence sur ce qui, lui, ne bouge pas : le texte.
"""

from __future__ import annotations

import unicodedata
from typing import Any


def _sans_accent(texte: str) -> str:
    """Projection utilisee pour comparer les textes.

    La campagne diacritiques accentue le corpus publie sans rien changer aux
    mathematiques. Un fragment attendu ecrit « integrale » ne doit pas cesser
    de correspondre parce que la source porte desormais « integrale » accentue.
    """

    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


class OptionIntrouvable(AssertionError):
    """Aucune option, ou plusieurs, ne correspond au texte demande."""


def lettre_de_option(question: dict[str, Any], texte: str) -> str:
    """Lettre de l'UNIQUE option dont le texte contient `texte`."""

    lettres = [
        lettre
        for lettre, option in question["options"].items()
        if _sans_accent(texte) in _sans_accent(option)
    ]
    if len(lettres) != 1:
        raise OptionIntrouvable(
            f"{question['id']}: {texte!r} designe {len(lettres)} options "
            f"({lettres}) au lieu d'une seule"
        )
    return lettres[0]


def option_correcte(question: dict[str, Any]) -> str:
    """Texte de l'option designee par la cle."""

    return question["options"][question["correcte"]]


def diagnostic_de_option(question: dict[str, Any], texte: str) -> str:
    """Diagnostic attache a l'option dont le texte contient `texte`."""

    lettre = lettre_de_option(question, texte)
    if lettre == question["correcte"]:
        raise OptionIntrouvable(
            f"{question['id']}: {texte!r} designe la bonne reponse, "
            "qui ne porte pas de diagnostic d'erreur"
        )
    return question["diagnostics"][lettre]["erreur"]


def diagnostics_de_distracteurs(question: dict[str, Any]) -> dict[str, str]:
    """Diagnostics des distracteurs, indexes par leur lettre courante."""

    return {
        lettre: entree["erreur"]
        for lettre, entree in (question.get("diagnostics") or {}).items()
        if lettre != question["correcte"]
    }


def diagnostic_unique_contenant(question: dict[str, Any], fragment: str) -> str:
    """Diagnostic de distracteur qui contient `fragment`, et lui seul."""

    trouves = [
        erreur
        for erreur in diagnostics_de_distracteurs(question).values()
        if _sans_accent(fragment) in _sans_accent(erreur)
    ]
    if len(trouves) != 1:
        raise OptionIntrouvable(
            f"{question['id']}: {fragment!r} apparait dans {len(trouves)} "
            "diagnostics de distracteurs au lieu d'un seul"
        )
    return trouves[0]


def diagnostic_unique_contenant_tous(
    question: dict[str, Any], fragments: tuple[str, ...]
) -> str:
    """Diagnostic de distracteur contenant TOUS les fragments, et lui seul."""

    trouves = [
        erreur
        for erreur in diagnostics_de_distracteurs(question).values()
        if all(_sans_accent(f) in _sans_accent(erreur) for f in fragments)
    ]
    if len(trouves) != 1:
        raise OptionIntrouvable(
            f"{question['id']}: {fragments!r} designent {len(trouves)} "
            "diagnostics de distracteurs au lieu d'un seul"
        )
    return trouves[0]
