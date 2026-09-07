#!/usr/bin/env python3
"""Le banc d'essai de la normalisation des clones.

Un detecteur de clones se trompe de deux facons, et les deux sont graves.

Un FAUX POSITIF fusionne deux objets differents : on declare clone un
exercice qui ne l'est pas, on le retire, et l'eleve perd un contenu
authentique. Un FAUX NEGATIF laisse passer une copie : c'est exactement ce
qui s'est produit, neuf cents fois, parce que le corps compare portait encore
l'identifiant de l'objet.

Ce module ne contient que des fixtures : des paires d'objets dont on SAIT ce
que la normalisation doit en faire. Elles sont ecrites a la main, lisibles, et
volontairement proches des cas reels du corpus -- l'exercice de variations
recopie dans quinze chapitres, la meme consigne avec un autre nombre, la meme
formule avec un autre exposant.

La normalisation retire l'identite technique et RIEN d'autre : ni nombres, ni
formules, ni code, ni texte, ni donnees, ni options de QCM, ni references
pedagogiques, ni figures, ni noms de concepts.
"""

from __future__ import annotations

import json
from typing import Any

#: Un exercice complet, tel qu'il vit sur le disque.
def objet(
    identifiant: str,
    corps: str,
    *,
    chapitre: str = "CH",
    capacites: list[str] | None = None,
    environnement: str = "exercice",
    reference: str | None = None,
    entete: str = "",
) -> str:
    meta: dict[str, Any] = {
        "id": identifiant,
        "chapitre": chapitre,
        "type_objet": environnement,
    }
    if capacites is not None:
        meta["capacites_codes"] = capacites
    if reference:
        meta["exercice_ref"] = reference
    argument = reference or identifiant
    return (
        "% META: " + json.dumps(meta, ensure_ascii=False) + "\n"
        + entete
        + "\\begin{" + environnement + "}{" + argument + "}{1}{10}\n"
        + corps
        + "\n\\end{" + environnement + "}\n"
    )


VARIATIONS = "Étudier les variations de $f(x) = x^3 - 3x^2 + 2$ sur $\\mathbb{R}$."
ORACLE = (
    "% BEGIN-VERIFY\n"
    "% from sympy import *\n"
    "% x = symbols('x')\n"
    "% assert diff(x**3 - 3*x**2 + 2, x) == 3*x**2 - 6*x\n"
    "% END-VERIFY\n"
)

#: Paires que la normalisation DOIT rendre identiques : seule une identite
#: technique les separe. Chacune reproduit un cas observe dans le corpus.
MUST_MATCH: tuple[tuple[str, str, str], ...] = (
    (
        "meme exercice, autre identifiant d'objet",
        objet("TEXP-ARI-EX-010", VARIATIONS, chapitre="TEXP-ARITHMETIQUE"),
        objet("TCOMPL-AIR-EX-010", VARIATIONS, chapitre="TCOMPL-CALCULS-AIRES"),
    ),
    (
        "meme exercice, identifiant present aussi dans le bloc oracle",
        objet("A-EX-001", VARIATIONS, entete=ORACLE),
        objet("B-EX-001", VARIATIONS, entete=ORACLE),
    ),
    (
        "meme corrige, autre exercice servi",
        objet(
            "A-CO-010",
            "On derive : $f'(x) = 3x^2 - 6x$, nul en $0$ et en $2$.",
            environnement="corrige",
            reference="A-EX-010",
        ),
        objet(
            "B-CO-010",
            "On derive : $f'(x) = 3x^2 - 6x$, nul en $0$ et en $2$.",
            environnement="corrige",
            reference="B-EX-010",
        ),
    ),
    (
        "meme exercice, chapitre declare different",
        objet("A-EX-002", VARIATIONS, chapitre="TEXP-GRAPHES"),
        objet("B-EX-002", VARIATIONS, chapitre="TCOMPL-INFERENCE-BAYESIENNE"),
    ),
    (
        "meme exercice, capacite declaree differente sans changement de corps",
        objet("A-EX-003", VARIATIONS, capacites=["C1"]),
        objet("B-EX-003", VARIATIONS, capacites=["C7"]),
    ),
)

#: Paires que la normalisation DOIT laisser distinctes. Un seul de ces cas
#: qui fusionne, et le detecteur supprimerait du contenu authentique.
MUST_DIFFER: tuple[tuple[str, str, str], ...] = (
    (
        "une valeur numerique differente",
        objet("A-EX-010", "Étudier les variations de $f(x) = x^3 - 3x^2 + 2$."),
        objet("B-EX-010", "Étudier les variations de $f(x) = x^3 - 3x^2 + 5$."),
    ),
    (
        "une formule differente",
        objet("A-EX-011", "Dériver $f(x) = x\\ln x$ sur $]0;+\\infty[$."),
        objet("B-EX-011", "Dériver $f(x) = x^2\\ln x$ sur $]0;+\\infty[$."),
    ),
    (
        "un contexte different, meme mathematiques",
        objet(
            "A-EX-012",
            "Un artisan produit $x$ pieces. Le cout vaut $C(x) = x^2 + 4$.",
        ),
        objet(
            "B-EX-012",
            "Une bacterie se divise. La population vaut $P(x) = x^2 + 4$.",
        ),
    ),
    (
        "une question ajoutee",
        objet(
            "A-EX-013",
            "\\begin{enumerate}\n  \\item Calculer $f'(x)$.\n\\end{enumerate}",
        ),
        objet(
            "B-EX-013",
            "\\begin{enumerate}\n  \\item Calculer $f'(x)$.\n"
            "  \\item En déduire le tableau de variations.\n\\end{enumerate}",
        ),
    ),
    (
        "une donnee modifiee",
        objet("A-EX-014", "Le rayon de la Terre vaut $R = 6371$~km."),
        objet("B-EX-014", "Le rayon de la Terre vaut $R = 6378$~km."),
    ),
    (
        "une capacite differente accompagnee d'un vrai changement de contenu",
        objet(
            "A-EX-015",
            "Déterminer le PGCD de $126$ et $84$ par l'algorithme d'Euclide.",
            capacites=["C1"],
        ),
        objet(
            "B-EX-015",
            "Étudier la convexité de $f(x) = x^3 - 3x^2 + 2$.",
            capacites=["C3"],
        ),
    ),
    (
        "une option de QCM modifiee",
        objet(
            "A-EX-016",
            "Cocher : (a) $3x^2$ \\quad (b) $3x^2 - 6x$ \\quad (c) $x^2 - 6x$",
        ),
        objet(
            "B-EX-016",
            "Cocher : (a) $3x^2$ \\quad (b) $3x^2 - 6$ \\quad (c) $x^2 - 6x$",
        ),
    ),
    (
        "une ligne de code modifiee",
        objet("A-EX-017", "\\texttt{return (a*m + b) \\% 26}"),
        objet("B-EX-017", "\\texttt{return (a*m - b) \\% 26}"),
    ),
    (
        "un nom de concept modifie",
        objet("A-EX-018", "Démontrer le théorème de Bézout."),
        objet("B-EX-018", "Démontrer le théorème de Gauss."),
    ),
    (
        "une figure differente",
        objet("A-EX-019", "\\includegraphics{cercle_trigonometrique}"),
        objet("B-EX-019", "\\includegraphics{tableau_variations}"),
    ),
    (
        "une reference pedagogique substantielle differente",
        objet("A-EX-020", "Voir la fiche méthode M2 avant de commencer."),
        objet("B-EX-020", "Voir la fiche méthode M7 avant de commencer."),
    ),
    (
        "un oracle different sur un enonce identique",
        objet("A-EX-021", VARIATIONS, entete=ORACLE),
        objet(
            "B-EX-021",
            VARIATIONS,
            entete=ORACLE.replace("3*x**2 - 6*x", "3*x**2 - 6"),
        ),
    ),
)


#: Les sous-objets d'une fiche portent aussi le prefixe du chapitre. Ces
#: jetons sont de l'identite ; une reference a un objet d'un AUTRE chapitre
#: est du contenu, et doit survivre.
FICHE_A = objet(
    "TEXP-ARI-RE-C04",
    "\\begin{exercice}{TEXP-ARI-FR-R4-EX1}{1}{10}\n"
    "Déterminer $\\lim_{x \\to +\\infty} \\dfrac{x^3}{\\mathrm{e}^x}$.\n"
    "\\end{exercice}",
    chapitre="TEXP-ARITHMETIQUE",
    environnement="remediation",
)
FICHE_B = objet(
    "TCOMPL-ECH-RE-C04",
    "\\begin{exercice}{TCOMPL-ECH-FR-R4-EX1}{1}{10}\n"
    "Déterminer $\\lim_{x \\to +\\infty} \\dfrac{x^3}{\\mathrm{e}^x}$.\n"
    "\\end{exercice}",
    chapitre="TCOMPL-ECHANTILLONNAGE",
    environnement="remediation",
)
MUST_MATCH = MUST_MATCH + (
    ("meme fiche, sous-objets renommes au prefixe du chapitre", FICHE_A, FICHE_B),
)
MUST_DIFFER = MUST_DIFFER + (
    (
        "une reference a un objet d'un autre chapitre est du contenu",
        objet(
            "A-EX-030",
            "Reprendre la methode de \\ref{TSPE-DERCONV-ME-001}.",
            chapitre="CH-A",
        ),
        objet(
            "A-EX-031",
            "Reprendre la methode de \\ref{TSPE-LIMFCT-ME-004}.",
            chapitre="CH-A",
        ),
    ),
)
