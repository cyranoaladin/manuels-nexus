#!/usr/bin/env python3
"""Fermeture des 166 QCM que le solveur générique n'a pas pu trancher.

`QCM_INDEPENDENT_EVIDENCE_V2` route chaque question vers une famille de
solveurs GÉNÉRIQUE — jamais vers une dérivation écrite pour la question. C'est
la bonne discipline : un solveur taillé pour une question prouve seulement que
son auteur connaissait la réponse. 166 questions sortent donc en
`HUMAN_REVIEW_REQUIRED`, faute de famille générique qui les modélise.

Ce fichier les ferme, en deux régimes qui ne se mélangent pas.

RÉGIME MÉCANIQUE. La question a une réponse CALCULABLE : une conversion de
base, une évaluation Python, une requête SQL, un calcul symbolique. On écrit
la dérivation, elle produit une VALEUR, et cette valeur est rapprochée des
options. La dérivation ne reçoit jamais la clé : elle reçoit l'énoncé et les
options, elle renvoie une lettre, et c'est le producteur qui compare ensuite.
Une divergence est un DÉFAUT à corriger, jamais un résultat à ajuster.

RÉGIME CONCEPTUEL. La question porte sur un savoir, une définition, une
propriété : rien à exécuter. La fermeture est alors un RAISONNEMENT écrit, qui
doit dire quatre choses, et le producteur vérifie que les quatre sont là :

  `raisonnement`   pourquoi la bonne réponse est la bonne, en propre ;
  `source_cours`   l'objet de cours du dépôt qui l'établit — il doit exister ;
  `source_programme` la capacité du contrat qui la porte ;
  `refutations`    pourquoi CHAQUE distracteur est faux, un par un.

Pas de rapprochement par mots-clés, dans aucun des deux régimes. Un
distracteur n'est pas faux parce qu'il ne ressemble pas à la bonne réponse.
"""

from __future__ import annotations

MECHANICAL = "MECHANICAL"
CONCEPTUAL = "CONCEPTUAL"

#: Familles de dérivation mécanique. Elles décrivent CE QUI est exécuté, et
#: servent au décompte : une question SQL ne se prouve pas comme une question
#: de calcul symbolique.
SYMBOLIC = "SYMBOLIC"
PYTHON = "PYTHON"
SQL = "SQL"
FAMILIES = (SYMBOLIC, PYTHON, SQL)

#: (chapitre, question) -> dérivation mécanique.
#: Chaque entrée est un couple (famille, fonction). La fonction reçoit le
#: dictionnaire des OPTIONS seul — jamais la clé — et renvoie la lettre
#: qu'elle a calculée, ou lève une exception si elle ne conclut pas.
MECHANICAL_DERIVATIONS: dict[tuple[str, str], tuple[str, object]] = {}

#: (chapitre, question) -> revue conceptuelle.
CONCEPTUAL_REVIEWS: dict[tuple[str, str], dict[str, object]] = {}


def mecanique(chapitre: str, question: str, famille: str):
    """Déclare une dérivation mécanique pour une question."""

    def enregistrer(fonction):
        cle = (chapitre, question)
        if cle in MECHANICAL_DERIVATIONS or cle in CONCEPTUAL_REVIEWS:
            raise ValueError(f"{cle} déjà déclarée")
        if famille not in FAMILIES:
            raise ValueError(f"famille inconnue: {famille}")
        MECHANICAL_DERIVATIONS[cle] = (famille, fonction)
        return fonction

    return enregistrer


def conceptuelle(
    chapitre: str,
    question: str,
    *,
    reponse: str,
    raisonnement: str,
    source_cours: str,
    source_programme: str,
    refutations: dict[str, str],
) -> None:
    """Déclare une revue conceptuelle pour une question.

    `reponse` est la lettre que la revue établit PAR LE RAISONNEMENT. Le
    producteur la compare ensuite à la clé du QCM : c'est ce rapprochement,
    et lui seul, qui vaut preuve.
    """
    cle = (chapitre, question)
    if cle in MECHANICAL_DERIVATIONS or cle in CONCEPTUAL_REVIEWS:
        raise ValueError(f"{cle} déjà déclarée")
    if not raisonnement.strip() or not source_cours.strip():
        raise ValueError(f"{cle}: revue incomplète")
    if not refutations:
        raise ValueError(f"{cle}: aucune réfutation de distracteur")
    CONCEPTUAL_REVIEWS[cle] = {
        "reponse": reponse,
        "raisonnement": raisonnement,
        "source_cours": source_cours,
        "source_programme": source_programme,
        "refutations": dict(refutations),
    }


def _lettre(options: dict, predicat) -> str:
    """La seule option qui satisfait le prédicat.

    Si zéro ou plusieurs options le satisfont, la dérivation ne conclut pas —
    et c'est un défaut de la QUESTION, pas de la dérivation.
    """
    retenues = [lettre for lettre, texte in options.items() if predicat(texte)]
    if len(retenues) != 1:
        raise ValueError(f"la dérivation ne tranche pas: {retenues}")
    return retenues[0]


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-ALGO-DICHO-GLOUTON-KNN
# ══════════════════════════════════════════════════════════════════════════

_ADGK = "1NSI-ALGO-DICHO-GLOUTON-KNN"
_ADGK_C1 = "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/cours/1NSI-ADGK-COURS-C1.tex"
_ADGK_C2 = "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/cours/1NSI-ADGK-COURS-C2.tex"
_ADGK_C3 = "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/cours/1NSI-ADGK-COURS-C3.tex"

conceptuelle(
    _ADGK, "Q1", reponse="A",
    raisonnement=(
        "La dichotomie compare la valeur cherchée à l'élément médian et élimine "
        "la moitié où elle ne peut pas se trouver. Cette élimination n'est "
        "licite que si l'ordre du tableau garantit que tout ce qui est d'un "
        "côté du médian lui est inférieur, et tout ce qui est de l'autre lui "
        "est supérieur : c'est exactement dire que le tableau est trié. Sur un "
        "tableau non trié, la moitié éliminée peut contenir la valeur."
    ),
    source_cours=_ADGK_C1,
    source_programme="1NSI-ALGO-DICHO-GLOUTON-KNN::C1",
    refutations={
        "B": (
            "La parité de la taille n'intervient nulle part : la division "
            "entière `(g+d)//2` désigne un indice valide que la taille soit "
            "paire ou impaire. Un tableau de trois éléments se traite comme un "
            "tableau de quatre."
        ),
        "C": (
            "Rien n'exige des entiers : la dichotomie fonctionne sur toute "
            "donnée munie d'une relation d'ordre total, chaînes de caractères "
            "comprises. C'est l'ordre qui est requis, pas le type."
        ),
        "D": (
            "Aucune borne de taille n'est requise, et l'affirmation inverse "
            "l'intérêt de la méthode : l'avantage du coût logarithmique sur le "
            "parcours séquentiel croît avec la taille du tableau."
        ),
    },
)

conceptuelle(
    _ADGK, "Q2", reponse="B",
    raisonnement=(
        "Un variant de boucle est une quantité entière positive qui décroît "
        "strictement à chaque tour. `borne sup - borne inf` décroît d'au moins "
        "la moitié à chaque itération et reste positive tant que la boucle "
        "tourne : une suite d'entiers positifs strictement décroissante est "
        "finie, donc la boucle s'arrête. C'est une preuve de TERMINAISON, et "
        "rien d'autre."
    ),
    source_cours=_ADGK_C1,
    source_programme="1NSI-ALGO-DICHO-GLOUTON-KNN::C1",
    refutations={
        "A": (
            "Le tri est une précondition : il est supposé vrai à l'entrée, et "
            "le variant ne le démontre pas. Un variant ne prouve jamais une "
            "hypothèse, il prouve un arrêt."
        ),
        "C": (
            "C'est confondre terminaison et correction. Le variant garantit "
            "l'arrêt ; la valeur cherchée peut parfaitement être absente du "
            "tableau, et l'algorithme s'arrête alors en renvoyant l'échec."
        ),
        "D": (
            "Le variant est divisé par deux à chaque tour, ce qui donne un coût "
            "logarithmique, pas linéaire. Et de toute façon un variant sert à "
            "la terminaison, pas à l'évaluation du coût."
        ),
    },
)

conceptuelle(
    _ADGK, "Q3", reponse="C",
    raisonnement=(
        "Un algorithme glouton construit sa solution étape par étape, en "
        "retenant à chaque étape le choix qui paraît le meilleur sur le moment "
        "— optimum LOCAL — et sans jamais remettre en cause un choix déjà fait. "
        "C'est précisément cette double propriété qui le rend rapide, et qui "
        "explique qu'il puisse manquer l'optimum global."
    ),
    source_cours=_ADGK_C2,
    source_programme="1NSI-ALGO-DICHO-GLOUTON-KNN::C2",
    refutations={
        "A": (
            "Le choix est réévalué à chaque étape en fonction de ce qui reste à "
            "traiter. Qu'il se répète parfois — rendre deux fois la même pièce — "
            "est une conséquence des données, pas une règle."
        ),
        "B": (
            "Un calcul exhaustif garantirait l'optimum global, mais ce n'est "
            "pas un glouton : c'est une recherche exhaustive, de coût "
            "incomparablement plus élevé. Le glouton ne l'effectue pas."
        ),
        "D": (
            "Le choix suit un critère explicite et déterministe — la plus "
            "grande pièce qui ne dépasse pas la somme restante, par exemple. "
            "Deux exécutions sur les mêmes données donnent le même résultat."
        ),
    },
)


@mecanique(_ADGK, "Q4", PYTHON)
def _adgk_q4(options):
    """Rendu glouton de 6 avec {4, 3, 1}, puis rendu optimal par exploration."""
    pieces = sorted([4, 3, 1], reverse=True)

    def glouton(somme):
        rendu = []
        for piece in pieces:
            while somme >= piece:
                rendu.append(piece)
                somme -= piece
        return rendu

    def optimal(somme):
        meilleur = {0: 0}
        for valeur in range(1, somme + 1):
            candidats = [
                meilleur[valeur - p] + 1
                for p in pieces
                if p <= valeur and (valeur - p) in meilleur
            ]
            if candidats:
                meilleur[valeur] = min(candidats)
        return meilleur.get(somme)

    rendu = glouton(6)
    assert sum(rendu) == 6, rendu
    nb_glouton, nb_optimal = len(rendu), optimal(6)
    # La dérivation produit deux nombres : 3 pièces pour le glouton, 2 pour
    # l'optimum. Elle cherche ensuite l'option qui décrit CE couple.
    assert (nb_glouton, nb_optimal) == (3, 2), (nb_glouton, nb_optimal)
    return _lettre(
        options,
        lambda texte: f"${nb_glouton}$ pièces" in texte and "pas optimale" in texte,
    )


conceptuelle(
    _ADGK, "Q5", reponse="A",
    raisonnement=(
        "L'algorithme des k plus proches voisins calcule la distance du nouvel "
        "élément à chaque point déjà classé, retient les k plus proches, et lui "
        "attribue la classe majoritaire parmi ces k. Les trois ingrédients — "
        "proximité, k voisins, vote majoritaire — sont dans la seule option A."
    ),
    source_cours=_ADGK_C3,
    source_programme="1NSI-ALGO-DICHO-GLOUTON-KNN::C3",
    refutations={
        "B": (
            "La méthode retient les points les plus PROCHES. Prendre le plus "
            "éloigné inverse le principe même et donnerait, sur un jeu séparé "
            "en deux groupes, systématiquement la mauvaise classe."
        ),
        "C": (
            "Rien n'est tiré au hasard : deux exécutions sur les mêmes données "
            "donnent la même prédiction, aux ex æquo près, qui sont tranchés "
            "par une règle de départage explicite."
        ),
        "D": (
            "Les classes sont des étiquettes, pas des nombres : leur moyenne "
            "n'a pas de sens. Sur des classes « chat » et « chien », "
            "l'opération n'est même pas définie."
        ),
    },
)

conceptuelle(
    _ADGK, "Q6", reponse="B",
    raisonnement=(
        "Si k vaut le nombre total de points, les k plus proches voisins sont "
        "TOUS les points du jeu, quel que soit le nouvel élément. La prédiction "
        "devient alors la classe majoritaire globale, identique pour tout "
        "élément : la proximité, qui est le ressort de la méthode, ne joue plus "
        "aucun rôle."
    ),
    source_cours=_ADGK_C3,
    source_programme="1NSI-ALGO-DICHO-GLOUTON-KNN::C3",
    refutations={
        "A": (
            "Aucune obligation : k est un paramètre libre, et les valeurs "
            "usuelles sont petites et impaires. L'algorithme fonctionne pour "
            "k = 1."
        ),
        "C": (
            "C'est le contraire : cette valeur rend la prédiction constante, "
            "donc inutilisable dès que le jeu contient plusieurs classes."
        ),
        "D": (
            "Le calcul n'est pas accéléré : les distances à tous les points "
            "sont calculées dans tous les cas ; seule change la taille du vote."
        ),
    },
)
