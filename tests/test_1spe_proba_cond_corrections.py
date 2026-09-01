"""Le corrige doit repondre a la question posee, et l'annoncer juste.

Sept exercices de 1SPE-PROBA-COND demandent « Construire l'arbre pondere ».
Aucun de leurs corriges ne le construisait : l'edition professeur laissait
sans reponse la question que l'eleve doit traiter en premier, et dont tout le
reste depend.

Un defaut scientifique s'y cachait. Dans CO-015, les evenements etaient
etiquetes a l'envers : le corrige imprimait $P(S \\cap \\overline{R}) = 3/50$,
valeur qui est en realite celle de $P(\\overline{S} \\cap R)$. La somme des
quatre chemins valait quand meme 1, ce qui rendait la verification muette.
"""

from __future__ import annotations

import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "Mathematiques/manuel-maths/chapitres/1SPE-PROBA-COND"

TREE_EXERCISES = ("015", "019", "021", "041", "044", "045", "047")


def _correction(number: str) -> str:
    return (CHAPTER / f"corriges/1SPE-PROBCOND-CO-{number}.tex").read_text(
        encoding="utf-8"
    )


def test_every_tree_question_receives_a_tree_answer() -> None:
    """La branche et sa probabilite doivent figurer, pas seulement le resultat."""
    missing = []
    for number in TREE_EXERCISES:
        text = _correction(number)
        if "arbre" not in text.lower():
            missing.append(number)
    assert missing == [], (
        f"corriges sans construction de l'arbre demandee : {missing}"
    )


def test_the_revision_tree_labels_match_their_values() -> None:
    """CO-015 : R = « a revise », S = « reussit ».

    P(S inter R-barre) vaut P(R-barre) x P_R-barre(S) = 2/5 x 7/10 = 14/50,
    et non 3/50.
    """
    text = _correction("015")
    revised, success_if_revised, success_if_not = (
        Fraction(3, 5),
        Fraction(9, 10),
        Fraction(7, 10),
    )
    expected = {
        r"P(S \cap R)": revised * success_if_revised,
        r"P(S \cap \overline{R})": (1 - revised) * success_if_not,
        r"P(\overline{S} \cap R)": revised * (1 - success_if_revised),
        r"P(\overline{S} \cap \overline{R})": (1 - revised) * (1 - success_if_not),
    }
    for label, value in expected.items():
        numerator = value * 50
        pattern = re.escape(label) + r"\s*=\s*[^.]*?\\frac\{" + str(int(numerator)) + r"\}\{50\}"
        assert re.search(pattern, text), (
            f"{label} doit valoir {int(numerator)}/50 dans CO-015"
        )
