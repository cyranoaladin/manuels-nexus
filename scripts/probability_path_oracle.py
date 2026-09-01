#!/usr/bin/env python3
"""Chaque chemin sous SON evenement -- pas seulement une somme qui vaut 1.

P0_VERIFICATION_INVARIANT_BLINDNESS / SELF_CONFIRMING_AGGREGATE_CHECK.

Un corrige de 1SPE-PROBA-COND avait echange deux etiquettes : il imprimait
$P(S \\cap \\overline{R}) = 3/50$, valeur qui appartient a
$P(\\overline{S} \\cap R)$. La somme des quatre feuilles valait toujours 1, et
le corrige se terminait donc sur une verification qui CONFIRMAIT la faute.

La lecon est generale : un invariant global -- somme, total, cardinal,
bareme, distribution -- est invariant sous une PERMUTATION. Il ne peut donc
jamais prouver l'association entre une etiquette et sa valeur. Il faut
comparer un DICTIONNAIRE, pas un multiensemble.

Cet oracle recalcule chaque probabilite de chemin a partir des donnees de
l'enonce, puis compare `evenement -> valeur` a ce que le corrige imprime.
Echanger deux valeurs entre deux etiquettes le fait echouer, alors que la
somme reste juste : c'est exactement ce que le test de mutation demontre.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Mapping

#: `P(...) = ... = \frac{a}{b}` : on retient l'etiquette et la DERNIERE
#: fraction de la chaine d'egalites, celle qui est affichee comme resultat.
PRINTED = re.compile(
    r"\$P\((?P<label>[^)]*)\)\s*=(?P<chain>[^$]*)\$"
)
FRACTION = re.compile(r"\\d?frac\{(-?\d+)\}\{(\d+)\}")


def normalise_label(raw: str) -> str:
    """Etiquette d'evenement, debarrassee de sa typographie."""

    text = raw.replace(r"\cap", "&").replace(r"\overline", "~")
    text = re.sub(r"[{}\s$]", "", text)
    return text


def printed_paths(correction_body: str) -> dict[str, Fraction]:
    """Ce que le corrige AFFICHE, par evenement."""

    found: dict[str, Fraction] = {}
    for match in PRINTED.finditer(correction_body):
        fractions = FRACTION.findall(match.group("chain"))
        if not fractions:
            continue
        numerator, denominator = fractions[-1]
        found[normalise_label(match.group("label"))] = Fraction(
            int(numerator), int(denominator)
        )
    return found


def expected_paths(
    first_level: Mapping[str, Fraction],
    conditional: Mapping[str, Mapping[str, Fraction]],
) -> dict[str, Fraction]:
    """Ce que l'enonce IMPLIQUE, par evenement.

    `first_level` : probabilites de la premiere etape.
    `conditional` : pour chaque branche de la premiere etape, les
    probabilites conditionnelles de la seconde.
    """

    expected: dict[str, Fraction] = {}
    for first, marginal in first_level.items():
        for second, probability in conditional[first].items():
            expected[normalise_label(f"{second}&{first}")] = marginal * probability
    return expected


def compare(
    printed: Mapping[str, Fraction], expected: Mapping[str, Fraction]
) -> dict[str, dict]:
    """Desaccords etiquette par etiquette. Vide = accord exact."""

    mismatches: dict[str, dict] = {}
    for label, value in expected.items():
        if label not in printed:
            mismatches[label] = {"expected": str(value), "printed": None}
        elif printed[label] != value:
            mismatches[label] = {
                "expected": str(value),
                "printed": str(printed[label]),
            }
    return mismatches


def sum_of_paths(values: Mapping[str, Fraction]) -> Fraction:
    """L'invariant global. Utile, mais JAMAIS suffisant."""

    return sum(values.values(), Fraction(0))
