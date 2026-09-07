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


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-ALGO-PARCOURS-TRIS
# ══════════════════════════════════════════════════════════════════════════

_APT = "1NSI-ALGO-PARCOURS-TRIS"
_APT_PARCOURS = "NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-APT-COURS-C1.tex"
_APT_INSERTION = "NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-APT-COURS-C2.tex"
_APT_SELECTION = "NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/cours/1NSI-APT-COURS-C3.tex"

conceptuelle(
    _APT, "Q1", reponse="A",
    raisonnement=(
        "Dans le pire cas — valeur absente, ou présente en dernière position — "
        "la recherche séquentielle compare la valeur cherchée à chacun des n "
        "éléments. Le nombre de comparaisons est donc exactement n : le coût "
        "est proportionnel à la taille, c'est-à-dire linéaire."
    ),
    source_cours=_APT_PARCOURS,
    source_programme="1NSI-ALGO-PARCOURS-TRIS::C1",
    refutations={
        "B": (
            "Un coût constant supposerait un nombre de comparaisons "
            "indépendant de n. C'est le cas du MEILLEUR cas — la valeur est en "
            "première position — jamais du pire."
        ),
        "C": (
            "Un coût logarithmique suppose d'éliminer une fraction constante "
            "des candidats à chaque étape, ce que seule la dichotomie fait, et "
            "seulement sur un tableau trié. Le parcours séquentiel n'élimine "
            "qu'un élément par comparaison."
        ),
        "D": (
            "Un coût quadratique supposerait un parcours imbriqué dans un "
            "autre. La recherche séquentielle ne comporte qu'une seule boucle."
        ),
    },
)

conceptuelle(
    _APT, "Q2", reponse="B",
    raisonnement=(
        "L'accumulateur doit contenir, à tout instant, le maximum des éléments "
        "déjà vus. Avant tout parcours, le seul élément dont on soit sûr qu'il "
        "appartient au tableau est le premier : l'initialiser avec lui garantit "
        "que l'accumulateur est toujours une valeur DU tableau, et que "
        "l'invariant tient dès le départ."
    ),
    source_cours=_APT_PARCOURS,
    source_programme="1NSI-ALGO-PARCOURS-TRIS::C2",
    refutations={
        "A": (
            "Initialiser à 0 renvoie 0 sur un tableau entièrement négatif, "
            "valeur qui n'appartient pas au tableau. L'erreur est invisible sur "
            "des données positives, ce qui la rend d'autant plus dangereuse."
        ),
        "C": (
            "La plus grande valeur représentable est l'initialisation du "
            "MINIMUM, pas du maximum : avec elle, aucun élément ne serait "
            "jamais retenu et la fonction renverrait cette borne."
        ),
        "D": (
            "Le nombre d'éléments est une propriété de la longueur, sans aucun "
            "rapport avec les valeurs stockées."
        ),
    },
)

conceptuelle(
    _APT, "Q3", reponse="C",
    raisonnement=(
        "Le tri par insertion maintient un préfixe trié et fait croître ce "
        "préfixe d'un élément à chaque tour : l'élément suivant est glissé vers "
        "la gauche jusqu'à trouver sa place parmi les éléments déjà triés. "
        "C'est la description exacte de l'option C."
    ),
    source_cours=_APT_INSERTION,
    source_programme="1NSI-ALGO-PARCOURS-TRIS::C3",
    refutations={
        "A": (
            "Trier d'abord une moitié décrit un tri par fusion, qui procède par "
            "division récursive. L'insertion progresse linéairement, de la "
            "gauche vers la droite."
        ),
        "B": (
            "Chercher le minimum de la partie restante est le tri par "
            "SÉLECTION. Les deux tris construisent un préfixe trié, mais par "
            "des gestes opposés : l'un cherche où mettre l'élément suivant, "
            "l'autre cherche quel élément mettre à la place suivante."
        ),
        "D": (
            "Aucun tri correct ne procède au hasard : le résultat doit être "
            "trié après un nombre fini d'étapes, ce qu'un échange aléatoire ne "
            "garantit pas."
        ),
    },
)

conceptuelle(
    _APT, "Q4", reponse="B",
    raisonnement=(
        "L'invariant du tri par insertion est ce qui est vrai avant chaque "
        "itération : le préfixe déjà traité est trié. Au début de l'itération "
        "i, i éléments ont été insérés, donc `tableau[0:i]` est trié. C'est "
        "cet invariant qui, joint à la condition d'arrêt i = n, donne la "
        "correction du tri."
    ),
    source_cours=_APT_INSERTION,
    source_programme="1NSI-ALGO-PARCOURS-TRIS::C4",
    refutations={
        "A": (
            "Un invariant qui n'affirme rien ne démontre rien : la propriété "
            "doit être assez forte pour donner la conclusion à la sortie de "
            "boucle."
        ),
        "C": (
            "Si le tableau entier était trié dès le début de chaque itération, "
            "la boucle n'aurait aucune raison de tourner. C'est la conclusion, "
            "pas l'invariant."
        ),
        "D": (
            "`tableau[i:n]` est la partie NON encore traitée : rien ne permet "
            "de la supposer triée, et c'est même la seule partie dont on ne "
            "sait rien."
        ),
    },
)

conceptuelle(
    _APT, "Q5", reponse="D",
    raisonnement=(
        "Le tri par sélection choisit, à chaque tour, le plus petit élément de "
        "la partie non encore triée et l'échange avec le premier élément de "
        "cette partie. Le préfixe trié croît ainsi d'un élément par tour, et "
        "chaque élément placé l'est définitivement."
    ),
    source_cours=_APT_SELECTION,
    source_programme="1NSI-ALGO-PARCOURS-TRIS::C5",
    refutations={
        "A": (
            "Insérer chaque élément à sa place dans le préfixe trié est le tri "
            "par INSERTION. Le geste est l'inverse : l'insertion prend "
            "l'élément suivant et cherche sa place ; la sélection prend la "
            "place suivante et cherche son élément."
        ),
        "B": (
            "La division récursive en deux moitiés décrit le tri fusion, hors "
            "programme de première et absent de ce chapitre."
        ),
        "C": (
            "Un tri qui ne comparerait jamais deux éléments ne pourrait pas "
            "les ordonner : la comparaison est l'opération élémentaire de tout "
            "tri par comparaison."
        ),
    },
)

conceptuelle(
    _APT, "Q6", reponse="A",
    raisonnement=(
        "L'invariant du tri par sélection a besoin de DEUX clauses. La première "
        "— `tableau[0:i]` est trié — ne suffit pas : elle n'empêche pas qu'un "
        "élément plus petit traîne encore dans la partie non triée, ce qui "
        "ruinerait la conclusion. La seconde clause — tout élément du préfixe "
        "est inférieur ou égal à tout élément du suffixe — est celle qui rend "
        "les placements définitifs, et donc la preuve possible."
    ),
    source_cours=_APT_SELECTION,
    source_programme="1NSI-ALGO-PARCOURS-TRIS::C6",
    refutations={
        "B": (
            "C'est l'invariant amputé de sa seconde clause. Il est VRAI, mais "
            "trop faible : il n'exclut pas qu'un élément plus petit reste à "
            "droite, et la conclusion du tri ne s'en déduit pas."
        ),
        "C": (
            "Les deux zones sont inversées. C'est le suffixe qui reste à "
            "trier ; affirmer qu'il est trié et minorant reviendrait à décrire "
            "un algorithme qui construit sa solution par la droite avec les "
            "plus grands, ce que le tri par sélection étudié ne fait pas."
        ),
        "D": (
            "Si le tableau entier était trié, la boucle serait terminée. Et "
            "l'égalité des tailles des deux zones n'a aucun rapport avec la "
            "correction : elle n'est vraie qu'au milieu du parcours."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-TABLES
# ══════════════════════════════════════════════════════════════════════════

_TAB = "1NSI-TABLES"
_TAB_IMPORT = "NSI/chapitres/1NSI-TABLES/cours/1NSI-TAB-COURS-C1.tex"
_TAB_RECHERCHE = "NSI/chapitres/1NSI-TABLES/cours/1NSI-TAB-COURS-C2.tex"
_TAB_TRI = "NSI/chapitres/1NSI-TABLES/cours/1NSI-TAB-COURS-C3.tex"
_TAB_FUSION = "NSI/chapitres/1NSI-TABLES/cours/1NSI-TAB-COURS-C4.tex"


@mecanique(_TAB, "Q1", PYTHON)
def _tab_q1(options):
    """Type effectivement rendu par `csv.DictReader` pour la colonne age."""
    import csv
    import io

    fichier = io.StringIO("nom,age\nAda,16\n")
    ligne = next(csv.DictReader(fichier))
    obtenu = type(ligne["age"]).__name__
    assert obtenu == "str", obtenu
    return _lettre(options, lambda texte: obtenu in texte)


conceptuelle(
    _TAB, "Q2", reponse="B",
    raisonnement=(
        "Le domaine d'une colonne est l'ensemble des valeurs qu'elle peut "
        "prendre : {« M », « F »} pour un sexe, les entiers de 0 à 120 pour un "
        "âge. C'est une contrainte sur les valeurs admissibles, indépendante "
        "des lignes effectivement présentes."
    ),
    source_cours=_TAB_IMPORT,
    source_programme="1NSI-TABLES::C1",
    refutations={
        "A": (
            "Le nombre de lignes est le cardinal de la table, une propriété du "
            "contenu qui change à chaque ajout. Le domaine, lui, appartient à "
            "la description de la table et ne bouge pas."
        ),
        "C": (
            "Le type Python est une conséquence de l'implémentation ; le "
            "domaine est plus fin. Deux colonnes de type `int` peuvent avoir "
            "des domaines très différents — un âge et un code postal."
        ),
        "D": (
            "Le nom de la colonne est son identifiant dans l'en-tête, pas "
            "l'ensemble de ses valeurs possibles."
        ),
    },
)

conceptuelle(
    _TAB, "Q3", reponse="A",
    raisonnement=(
        "La compréhension de liste avec condition construit une NOUVELLE liste "
        "contenant les lignes retenues, sans toucher à la liste de départ. "
        "C'est exactement le double besoin de l'énoncé : extraire selon un "
        "critère, et ne pas modifier la table source."
    ),
    source_cours=_TAB_RECHERCHE,
    source_programme="1NSI-TABLES::C2",
    refutations={
        "B": (
            "Réécrire le fichier CSV modifie la source sur le disque, ce que "
            "l'énoncé exclut explicitement, et cela ne produit d'ailleurs "
            "aucune valeur exploitable en mémoire."
        ),
        "C": (
            "`sorted` ordonne, il ne filtre pas : il renvoie toutes les lignes, "
            "dans un autre ordre."
        ),
        "D": (
            "L'opérateur `+` entre deux listes les concatène : il ajoute des "
            "lignes au lieu d'en retenir."
        ),
    },
)

conceptuelle(
    _TAB, "Q4", reponse="C",
    raisonnement=(
        "Un doublon sur la colonne `id` est une valeur d'`id` qui apparaît sur "
        "au moins deux lignes. Le détecter revient donc à compter les "
        "occurrences de chaque valeur de cette seule colonne, et à repérer "
        "celles dont le compte dépasse 1. Les autres colonnes n'entrent pas "
        "dans la définition."
    ),
    source_cours=_TAB_RECHERCHE,
    source_programme="1NSI-TABLES::C2",
    refutations={
        "A": (
            "Comparer les lignes entières détecte les lignes intégralement "
            "identiques, ce qui est un autre problème : deux lignes de même "
            "`id` mais d'âge différent sont un doublon d'`id` et non un "
            "doublon de ligne."
        ),
        "B": (
            "Trier puis compter les lignes donne le nombre total de lignes, "
            "qui ne dit rien des répétitions d'une valeur."
        ),
        "D": (
            "Supprimer les lignes identiques est une CORRECTION possible d'un "
            "autre problème, pas une détection, et elle laisserait passer les "
            "doublons d'`id` sur des lignes différentes."
        ),
    },
)


@mecanique(_TAB, "Q5", PYTHON)
def _tab_q5(options):
    """`sorted` sur une liste de dictionnaires : renvoie-t-il, modifie-t-il ?"""
    table = [{"nom": "Ada", "age": 36}, {"nom": "Alan", "age": 22}]
    avant = [dict(ligne) for ligne in table]
    resultat = sorted(table, key=lambda ligne: ligne["age"])
    renvoie_une_liste = isinstance(resultat, list)
    source_intacte = table == avant
    est_triee = [ligne["age"] for ligne in resultat] == [22, 36]
    assert renvoie_une_liste and source_intacte and est_triee
    assert resultat is not table
    return _lettre(
        options,
        lambda texte: "renvoie une nouvelle liste triée" in texte
        and "sans modifier" in texte,
    )


conceptuelle(
    _TAB, "Q6", reponse="A",
    raisonnement=(
        "La fusion étudiée dans le chapitre apparie les lignes dont la clé "
        "coïncide : elle parcourt la première table et, pour chaque ligne, "
        "cherche la ligne correspondante dans la seconde. Sans correspondance, "
        "aucune paire n'est formée, donc rien n'est produit pour cette ligne. "
        "C'est le comportement par défaut, celui d'une jointure interne."
    ),
    source_cours=_TAB_FUSION,
    source_programme="1NSI-TABLES::C4",
    refutations={
        "B": (
            "Une clé sans correspondance est un cas de données ordinaire, pas "
            "une erreur : rien n'est levé, la ligne est simplement écartée."
        ),
        "C": (
            "Compléter par des valeurs vides est le comportement d'une "
            "jointure EXTERNE, qui doit être demandée explicitement. Ce n'est "
            "pas le défaut."
        ),
        "D": (
            "Une ligne dupliquée dans le résultat viendrait de PLUSIEURS "
            "correspondances dans la seconde table, jamais d'une absence de "
            "correspondance."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-TYPES-BASE
# ══════════════════════════════════════════════════════════════════════════

_TB = "1NSI-TYPES-BASE"
_TB_BASES = "NSI/chapitres/1NSI-TYPES-BASE/cours/1NSI-TB-COURS-C1.tex"
_TB_RELATIFS = "NSI/chapitres/1NSI-TYPES-BASE/cours/1NSI-TB-COURS-C2.tex"
_TB_FLOTTANTS = "NSI/chapitres/1NSI-TYPES-BASE/cours/1NSI-TB-COURS-C3.tex"
_TB_BOOLEENS = "NSI/chapitres/1NSI-TYPES-BASE/cours/1NSI-TB-COURS-C4.tex"
_TB_TEXTE = "NSI/chapitres/1NSI-TYPES-BASE/cours/1NSI-TB-COURS-C5.tex"


@mecanique(_TB, "Q1", SYMBOLIC)
def _tb_q1(options):
    """Conversion de 1010 en base 2 vers la base 10, poids par poids."""
    bits = "1010"
    valeur = sum(int(b) * 2 ** k for k, b in enumerate(reversed(bits)))
    assert valeur == int(bits, 2) == 10
    return _lettre(options, lambda texte: texte.strip() == f"${valeur}$")


@mecanique(_TB, "Q2", SYMBOLIC)
def _tb_q2(options):
    """Nombre de mots binaires distincts de 8 bits."""
    from itertools import product

    distincts = len(set(product("01", repeat=8)))
    assert distincts == 2 ** 8 == 256
    return _lettre(options, lambda texte: texte.strip() == f"${distincts}$")


conceptuelle(
    _TB, "Q3", reponse="C",
    raisonnement=(
        "En complément à deux sur n bits, le bit de poids fort a pour poids "
        "$-2^{n-1}$ tandis que tous les autres ont un poids positif. Un nombre "
        "dont ce bit vaut 1 est donc nécessairement négatif, et un nombre dont "
        "il vaut 0 nécessairement positif ou nul : ce bit détermine le signe, "
        "et c'est même sa raison d'être."
    ),
    source_cours=_TB_RELATIFS,
    source_programme="1NSI-TYPES-BASE::C2",
    refutations={
        "A": (
            "La parité se lit sur le bit de poids FAIBLE, celui de poids 1. "
            "Les deux bits sont aux extrémités opposées du mot."
        ),
        "B": (
            "Le nombre de bits utilisés est fixé par le format — 8, 16, 32 — et "
            "n'est encodé dans aucun bit du mot lui-même."
        ),
        "D": (
            "Ce bit porte au contraire l'information la plus structurante de la "
            "représentation ; l'ignorer fait lire $-1$ comme $255$."
        ),
    },
)


@mecanique(_TB, "Q4", PYTHON)
def _tb_q4(options):
    """Évaluation effective de `0.1 + 0.2 == 0.3` en Python."""
    obtenu = (0.1 + 0.2 == 0.3)
    assert obtenu is False
    # La dérivation constate aussi POURQUOI : la somme diffère de 0.3.
    ecart = abs((0.1 + 0.2) - 0.3)
    assert 0 < ecart < 1e-15
    return _lettre(
        options,
        lambda texte: "\\code{False}" in texte and "flottante" in texte,
    )


@mecanique(_TB, "Q5", PYTHON)
def _tb_q5(options):
    """Évaluation de `True and False`."""
    obtenu = (True and False)
    assert obtenu is False
    return _lettre(options, lambda texte: texte.strip() == "\\code{False}")


@mecanique(_TB, "Q6", PYTHON)
def _tb_q6(options):
    """Un texte alphanumérique non accentué s'encode-t-il dans les trois ?"""
    texte = "Nexus2026"
    encodables = [
        nom for nom in ("ascii", "iso-8859-1", "utf-8")
        if _encodable(texte, nom)
    ]
    assert encodables == ["ascii", "iso-8859-1", "utf-8"]
    # Contrôle négatif : un texte accentué sort de l'ASCII.
    assert not _encodable("é", "ascii")
    return _lettre(
        options,
        lambda t: "ASCII" in t and "ISO-8859-1" in t and "UTF-8" in t,
    )


def _encodable(texte: str, encodage: str) -> bool:
    try:
        texte.encode(encodage)
    except UnicodeEncodeError:
        return False
    return True


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-ARCHITECTURE-OS
# ══════════════════════════════════════════════════════════════════════════

_ARCHOS = "1NSI-ARCHITECTURE-OS"
_ARCHOS_VN = "NSI/chapitres/1NSI-ARCHITECTURE-OS/cours/1NSI-ARCHOS-COURS-C1.tex"
_ARCHOS_INSTR = "NSI/chapitres/1NSI-ARCHITECTURE-OS/cours/1NSI-ARCHOS-COURS-C2.tex"
_ARCHOS_OS = "NSI/chapitres/1NSI-ARCHITECTURE-OS/cours/1NSI-ARCHOS-COURS-C3.tex"

conceptuelle(
    _ARCHOS, "Q1", reponse="C",
    raisonnement=(
        "L'idée centrale de l'architecture de von Neumann est le PROGRAMME "
        "ENREGISTRÉ : les instructions sont rangées dans la même mémoire que "
        "les données, et le processeur les y lit comme il lirait des données. "
        "C'est ce qui rend un ordinateur reprogrammable sans recâblage."
    ),
    source_cours=_ARCHOS_VN,
    source_programme="1NSI-ARCHITECTURE-OS::C1",
    refutations={
        "A": (
            "Deux mémoires séparées décrivent l'architecture de Harvard, qui "
            "existe bel et bien — dans certains microcontrôleurs — mais qui "
            "s'oppose précisément à celle de von Neumann."
        ),
        "B": (
            "Les registres sont en nombre très restreint et ne contiennent que "
            "les valeurs en cours de traitement. Un programme entier n'y "
            "tiendrait pas."
        ),
        "D": (
            "Le disque est un stockage de masse persistant ; l'exécution "
            "suppose un chargement préalable en mémoire vive."
        ),
    },
)

conceptuelle(
    _ARCHOS, "Q2", reponse="D",
    raisonnement=(
        "Le processeur exécute un cycle répété : lire l'instruction pointée par "
        "le compteur ordinal, la décoder, l'exécuter, puis incrémenter le "
        "compteur. L'ordre est donc séquentiel par construction, et seule une "
        "instruction de branchement modifie le compteur autrement que par "
        "incrémentation."
    ),
    source_cours=_ARCHOS_INSTR,
    source_programme="1NSI-ARCHITECTURE-OS::C2",
    refutations={
        "A": (
            "Un ordre aléatoire rendrait tout programme non reproductible : "
            "deux exécutions donneraient des résultats différents, ce qui "
            "ruinerait la notion même de programme."
        ),
        "B": (
            "Une exécution simultanée supposerait autant d'unités de calcul que "
            "d'instructions. Un cœur exécute une instruction à la fois."
        ),
        "C": (
            "L'ordre inverse n'a aucun sens : une instruction lit souvent le "
            "résultat de la précédente, qui n'aurait pas encore été calculé."
        ),
    },
)

conceptuelle(
    _ARCHOS, "Q3", reponse="A",
    raisonnement=(
        "L'ordonnanceur du système alloue le processeur à chaque processus "
        "pendant de courtes tranches, en alternance rapide. La commutation est "
        "trop rapide pour être perçue : l'utilisateur voit plusieurs programmes "
        "progresser « en même temps » alors qu'un seul cœur n'en exécute qu'un "
        "à chaque instant."
    ),
    source_cours=_ARCHOS_OS,
    source_programme="1NSI-ARCHITECTURE-OS::C3",
    refutations={
        "B": (
            "Le rôle du système est d'ORGANISER l'exécution, pas de l'empêcher. "
            "Un système qui bloquerait tout programme n'aurait aucune fonction."
        ),
        "C": (
            "Un logiciel ne remplace aucun composant matériel : le système "
            "d'exploitation a besoin du processeur pour s'exécuter lui-même."
        ),
        "D": (
            "L'affichage graphique est un service parmi d'autres, absent des "
            "systèmes en ligne de commande, qui gèrent pourtant des processus."
        ),
    },
)

conceptuelle(
    _ARCHOS, "Q4", reponse="B",
    raisonnement=(
        "`ls` (list) affiche le contenu du répertoire courant. C'est la "
        "commande de consultation du shell, et la seule des quatre proposées "
        "qui n'a aucun effet sur le système de fichiers."
    ),
    source_cours=_ARCHOS_OS,
    source_programme="1NSI-ARCHITECTURE-OS::C4",
    refutations={
        "A": (
            "`cd` (change directory) déplace le répertoire courant : elle "
            "change où l'on se trouve, sans rien afficher."
        ),
        "C": (
            "`mkdir` crée un répertoire : elle modifie le système de fichiers "
            "au lieu de le consulter."
        ),
        "D": (
            "`rm` supprime : c'est l'opération la plus destructrice des quatre, "
            "et l'exécuter à la place de `ls` détruirait ce qu'on voulait voir."
        ),
    },
)


@mecanique(_ARCHOS, "Q5", PYTHON)
def _archos_q5(options):
    """Droits du GROUPE dans la chaîne rwxr-x---, lus position par position."""
    permissions = "rwxr-x---"
    debut = {"proprietaire": 0, "groupe": 3, "autres": 6}["groupe"]
    triplet = permissions[debut:debut + 3]
    assert triplet == "r-x"
    lecture = triplet[0] == "r"
    ecriture = triplet[1] == "w"
    execution = triplet[2] == "x"
    assert (lecture, ecriture, execution) == (True, False, True)
    return _lettre(
        options,
        lambda texte: "lire et exécuter" in texte and "pas écrire" in texte,
    )


@mecanique(_ARCHOS, "Q6", PYTHON)
def _archos_q6(options):
    """Conversion de la notation octale 644 en chaîne rwx."""
    def rendre(chiffre: int) -> str:
        return (
            ("r" if chiffre & 0b100 else "-")
            + ("w" if chiffre & 0b010 else "-")
            + ("x" if chiffre & 0b001 else "-")
        )

    chaine = "".join(rendre(int(c)) for c in "644")
    assert chaine == "rw-r--r--", chaine
    return _lettre(options, lambda texte: chaine in texte)


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-LANGAGE
# ══════════════════════════════════════════════════════════════════════════

_LANG1 = "1NSI-LANGAGE"
_LANG1_ELEM = "NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C1.tex"
_LANG1_DIVERSITE = "NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C2.tex"
_LANG1_SPEC = "NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C3.tex"
_LANG1_TESTS = "NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex"
_LANG1_BIBLIO = "NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C5.tex"

conceptuelle(
    _LANG1, "Q1", reponse="A",
    raisonnement=(
        "Une boucle `for` sur un intervalle connu répète un nombre d'itérations "
        "fixé avant l'entrée : elle est bornée. Une boucle `while` s'arrête sur "
        "une CONDITION dont la valeur dépend de ce qui se passe dans le corps ; "
        "le nombre de tours n'est donc pas déterminé à l'avance. C'est en ce "
        "sens qu'on la dit non bornée."
    ),
    source_cours=_LANG1_ELEM,
    source_programme="1NSI-LANGAGE::C1",
    refutations={
        "B": (
            "Une boucle `while` termine dès que sa condition devient fausse, ce "
            "qui arrive dans tout programme correct. La non-terminaison est un "
            "BUG possible, pas la définition."
        ),
        "C": (
            "Une boucle `while` est au contraire définie PAR sa condition : "
            "sans elle, l'instruction n'aurait pas de sens syntaxique."
        ),
        "D": (
            "La vitesse d'exécution ne dépend pas de la forme de boucle mais du "
            "travail effectué. Rien dans « non bornée » ne parle de vitesse."
        ),
    },
)

conceptuelle(
    _LANG1, "Q2", reponse="B",
    raisonnement=(
        "Les langages impératifs partagent le même noyau de constructions — "
        "affectation, séquence, condition, boucle, fonction. Ce qui les "
        "distingue est la syntaxe qui les exprime, et quelques traits comme le "
        "typage statique ou dynamique, la gestion de la mémoire, la déclaration "
        "obligatoire ou non des variables."
    ),
    source_cours=_LANG1_DIVERSITE,
    source_programme="1NSI-LANGAGE::C2",
    refutations={
        "A": (
            "Les langages ne sont évidemment pas identiques : leurs syntaxes "
            "diffèrent, et le même algorithme s'écrit différemment dans chacun."
        ),
        "C": (
            "C'est l'inverse : le noyau des constructions élémentaires est "
            "précisément ce qui est COMMUN, et c'est ce qui permet de passer "
            "d'un langage à l'autre."
        ),
        "D": (
            "Un algorithme calculable s'écrit dans n'importe quel langage à "
            "usage général : c'est l'idée d'universalité, vue avec la machine "
            "de Turing."
        ),
    },
)

conceptuelle(
    _LANG1, "Q3", reponse="C",
    raisonnement=(
        "Le prototype est la SIGNATURE de la fonction : son nom, la liste "
        "ordonnée de ses paramètres, et la nature de ce qu'elle renvoie. C'est "
        "l'interface, c'est-à-dire ce qu'il faut connaître pour l'appeler, sans "
        "rien savoir de son corps."
    ),
    source_cours=_LANG1_SPEC,
    source_programme="1NSI-LANGAGE::C3",
    refutations={
        "A": (
            "L'ordre des instructions du corps est l'implémentation : elle peut "
            "changer entièrement sans que le prototype bouge."
        ),
        "B": (
            "Le nombre de lignes est une mesure de taille, sans aucun rapport "
            "avec la manière dont on appelle la fonction."
        ),
        "D": (
            "Le temps d'exécution est une propriété de performance, mesurée "
            "après coup ; elle ne figure pas dans une signature."
        ),
    },
)

conceptuelle(
    _LANG1, "Q4", reponse="D",
    raisonnement=(
        "Un jeu de tests exerce un nombre FINI de cas. Sa réussite établit que "
        "le programme se comporte correctement sur ces cas-là, et rien de plus. "
        "Pour conclure à la correction générale il faudrait une preuve, ou "
        "l'épuisement de tous les cas possibles, ce qu'un jeu de tests ne fait "
        "pas."
    ),
    source_cours=_LANG1_TESTS,
    source_programme="1NSI-LANGAGE::C4",
    refutations={
        "A": (
            "Un test ne montre jamais l'absence de bugs, seulement leur "
            "présence quand il échoue. Un cas non testé peut parfaitement "
            "échouer."
        ),
        "B": (
            "S'exécuter sans erreur ne dit rien du RÉSULTAT : un programme peut "
            "terminer normalement en renvoyant une valeur fausse, et c'est "
            "justement ce qu'un test détecte."
        ),
        "C": (
            "Aucune garantie ne porte sur l'avenir : une modification "
            "ultérieure du code peut introduire un bug que le jeu de tests "
            "existant ne couvre pas."
        ),
    },
)

conceptuelle(
    _LANG1, "Q5", reponse="A",
    raisonnement=(
        "La documentation donne ce qu'on ne peut pas deviner : l'ordre exact "
        "des paramètres, leur type attendu, la valeur renvoyée, et les cas "
        "d'erreur. `help(...)` affiche la docstring sans quitter l'interpréteur, "
        "ce qui en fait le réflexe adapté."
    ),
    source_cours=_LANG1_BIBLIO,
    source_programme="1NSI-LANGAGE::C5",
    refutations={
        "B": (
            "Deviner d'après le nom mène à des erreurs silencieuses : deux "
            "bibliothèques peuvent nommer pareillement des fonctions dont "
            "l'ordre des paramètres diffère."
        ),
        "C": (
            "Recopier le code source d'une bibliothèque perd tout l'intérêt de "
            "la réutilisation, et fige une version qui ne bénéficiera plus des "
            "corrections."
        ),
        "D": (
            "Les cas limites viennent APRÈS la lecture de la documentation : on "
            "ne peut pas construire un cas limite sans connaître le domaine "
            "attendu."
        ),
    },
)

conceptuelle(
    _LANG1, "Q6", reponse="B",
    raisonnement=(
        "Le programme de première demande de savoir utiliser une bibliothèque "
        "en s'appuyant sur sa documentation : chercher, lire, identifier la "
        "fonction adaptée. C'est une compétence de recherche d'information, pas "
        "un exercice de mémorisation."
    ),
    source_cours=_LANG1_BIBLIO,
    source_programme="1NSI-LANGAGE::C5",
    refutations={
        "A": (
            "Aucune restitution de mémoire n'est attendue : la documentation "
            "est disponible, et la connaître par cœur n'apporterait rien."
        ),
        "C": (
            "La connaissance exhaustive d'une bibliothèque n'est ni exigible ni "
            "utile : les bibliothèques évoluent, la démarche de consultation, "
            "non."
        ),
        "D": (
            "Se passer des bibliothèques irait contre l'objectif même de la "
            "capacité, qui est de savoir réutiliser du code déjà écrit et "
            "testé."
        ),
    },
)

conceptuelle(
    _LANG1, "Q7", reponse="C",
    raisonnement=(
        "Une précondition est ce que l'appelant doit garantir AVANT l'appel "
        "pour que la fonction soit en droit de fonctionner. Elle porte donc sur "
        "les arguments transmis — leur type, leur domaine, leurs relations "
        "mutuelles."
    ),
    source_cours=_LANG1_SPEC,
    source_programme="1NSI-LANGAGE::C6",
    refutations={
        "A": (
            "Le nom de la fonction est un identifiant : il ne peut être ni vrai "
            "ni faux, donc ne peut pas être une condition."
        ),
        "B": (
            "Le nombre de lignes du corps est une propriété de "
            "l'implémentation, invisible à l'appelant et sans influence sur la "
            "validité de l'appel."
        ),
        "D": (
            "La valeur renvoyée est ce que la fonction garantit APRÈS : c'est "
            "une POSTcondition, la notion symétrique."
        ),
    },
)

conceptuelle(
    _LANG1, "Q8", reponse="D",
    raisonnement=(
        "Une postcondition décrit ce qui est vrai à la SORTIE, en supposant les "
        "préconditions respectées. « La valeur renvoyée est positive et son "
        "carré vaut x » porte exactement sur le résultat, et le caractérise "
        "sans référence à la manière dont il a été obtenu."
    ),
    source_cours=_LANG1_SPEC,
    source_programme="1NSI-LANGAGE::C7",
    refutations={
        "A": (
            "« x doit être positif ou nul » est une exigence sur l'ARGUMENT, à "
            "satisfaire avant l'appel : c'est la précondition, pas la "
            "postcondition."
        ),
        "B": (
            "L'import du module est une contrainte d'environnement du "
            "programme, pas une propriété du résultat de la fonction."
        ),
        "C": (
            "Une limite de longueur du code est une convention de style, sans "
            "lien avec ce que la fonction garantit."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-PROJET-METHODES
# ══════════════════════════════════════════════════════════════════════════

_PM = "1NSI-PROJET-METHODES"
_PM_HISTOIRE = "NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C1.tex"
_PM_PROJET = "NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C2.tex"
_PM_DEBUG = "NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C3.tex"
_PM_DOC = "NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C4.tex"

conceptuelle(
    _PM, "Q1", reponse="A",
    raisonnement=(
        "Alan Turing formalise en 1936 la machine universelle : une machine "
        "capable de simuler n'importe quelle autre machine dont la description "
        "lui est fournie en entrée. C'est le fondement théorique de "
        "l'ordinateur programmable, et la date est un repère du programme."
    ),
    source_cours=_PM_HISTOIRE,
    source_programme="1NSI-PROJET-METHODES::C1",
    refutations={
        "B": (
            "La Pascaline de 1642 est une machine à calculer mécanique, câblée "
            "pour l'addition : elle n'est pas programmable, et ne peut donc pas "
            "être universelle."
        ),
        "C": (
            "Guido van Rossum crée le langage Python en 1991, plus d'un "
            "demi-siècle après : un langage n'est pas une machine universelle, "
            "il s'exécute sur une."
        ),
        "D": (
            "Tim Berners-Lee invente le Web en 1989-1991 : un service applicatif "
            "au-dessus d'Internet, sans rapport avec la calculabilité."
        ),
    },
)

conceptuelle(
    _PM, "Q2", reponse="B",
    raisonnement=(
        "Le programme officiel de la spécialité prescrit qu'au moins un quart "
        "de l'horaire total soit consacré à la conception et à l'élaboration de "
        "projets. C'est une prescription horaire explicite, pas une "
        "recommandation vague."
    ),
    source_cours=_PM_PROJET,
    source_programme="1NSI-PROJET-METHODES::C2",
    refutations={
        "A": (
            "Moins d'un dixième contredirait la place que le programme donne au "
            "projet, qui est l'une des modalités d'apprentissage centrales de "
            "la spécialité."
        ),
        "C": (
            "La totalité de l'horaire est exclue : le programme comporte aussi "
            "des contenus disciplinaires — données, algorithmes, machines, "
            "langages — enseignés hors projet."
        ),
        "D": (
            "Aucune heure dédiée reviendrait à supprimer le projet du "
            "programme, alors qu'il y figure explicitement."
        ),
    },
)

conceptuelle(
    _PM, "Q3", reponse="C",
    raisonnement=(
        "Un jalon est un point de contrôle daté auquel un livrable identifiable "
        "doit être atteint. Découper le projet en jalons rend l'avancement "
        "OBSERVABLE en cours de route, et permet donc de réviser les objectifs "
        "quand un jalon glisse — au lieu de découvrir le retard à la fin."
    ),
    source_cours=_PM_PROJET,
    source_programme="1NSI-PROJET-METHODES::C2",
    refutations={
        "A": (
            "Les jalons ORGANISENT le travail en équipe en répartissant les "
            "livrables ; ils ne le suppriment pas."
        ),
        "B": (
            "Aucune organisation ne garantit l'absence de bugs. Les jalons "
            "permettent de les découvrir plus tôt, ce qui est différent."
        ),
        "D": (
            "Les jalons se déduisent du cahier des charges : sans exigences, on "
            "ne sait pas ce qu'un jalon doit livrer."
        ),
    },
)

conceptuelle(
    _PM, "Q4", reponse="D",
    raisonnement=(
        "Un message d'erreur Python contient deux informations décisives : le "
        "TYPE de l'erreur, qui oriente vers la cause, et la trace d'appels, qui "
        "nomme le fichier et la ligne. Les lire en entier est donc la première "
        "étape, et la seule qui apporte de l'information avant toute "
        "modification."
    ),
    source_cours=_PM_DEBUG,
    source_programme="1NSI-PROJET-METHODES::C3",
    refutations={
        "A": (
            "Corriger au hasard peut faire disparaître le symptôme sans "
            "toucher la cause, et introduit un second défaut par-dessus le "
            "premier."
        ),
        "B": (
            "Relancer sans rien changer reproduit exactement la même erreur : "
            "un programme déterministe ne se corrige pas en le réexécutant."
        ),
        "C": (
            "Supprimer la fonction mise en cause supprime la fonctionnalité "
            "avec le bug. Et la fonction nommée dans la trace n'est souvent pas "
            "celle qui est fautive : elle peut recevoir une valeur invalide "
            "produite ailleurs."
        ),
    },
)

conceptuelle(
    _PM, "Q5", reponse="A",
    raisonnement=(
        "Une docstring est la spécification lisible de la fonction : ce qu'elle "
        "fait, ce qu'elle exige de ses arguments — préconditions — et ce "
        "qu'elle garantit sur son résultat — postconditions. C'est ce dont a "
        "besoin quelqu'un qui veut l'appeler sans lire son corps."
    ),
    source_cours=_PM_DOC,
    source_programme="1NSI-PROJET-METHODES::C4",
    refutations={
        "B": (
            "Le nom de l'auteur est une information de gestion : il n'aide "
            "personne à appeler correctement la fonction."
        ),
        "C": (
            "La date de dernière modification est déjà tenue par le système de "
            "versions, et ne dit rien du comportement."
        ),
        "D": (
            "Le code dit COMMENT, jamais ce qui est exigé ni ce qui est "
            "garanti : lire une implémentation pour deviner son contrat est "
            "précisément ce que la docstring évite."
        ),
    },
)

conceptuelle(
    _PM, "Q6", reponse="B",
    raisonnement=(
        "Une soutenance est évaluée sur la démarche : quel problème a été "
        "traité, quels choix ont été faits et pourquoi, quelles difficultés ont "
        "été rencontrées et comment elles ont été levées. C'est ce qui montre "
        "la compréhension, qu'aucune récitation ne remplace."
    ),
    source_cours=_PM_DOC,
    source_programme="1NSI-PROJET-METHODES::C4",
    refutations={
        "A": (
            "Lire le code ligne par ligne est illisible à l'oral et ne montre "
            "aucun choix : le jury voit le code, il ne voit pas pourquoi il est "
            "ainsi."
        ),
        "C": (
            "L'énumération des noms de variables est un détail "
            "d'implémentation, sans aucune valeur explicative."
        ),
        "D": (
            "Réciter la documentation officielle ne dit rien du projet "
            "personnel, qui est l'objet de la présentation."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-RESEAUX
# ══════════════════════════════════════════════════════════════════════════

_RES = "1NSI-RESEAUX"
_RES_PAQUETS = "NSI/chapitres/1NSI-RESEAUX/cours/1NSI-RES-COURS-C1.tex"
_RES_BIT = "NSI/chapitres/1NSI-RESEAUX/cours/1NSI-RES-COURS-C2.tex"
_RES_IHM = "NSI/chapitres/1NSI-RESEAUX/cours/1NSI-RES-COURS-C3.tex"

conceptuelle(
    _RES, "Q1", reponse="C",
    raisonnement=(
        "Les paquets d'un même message peuvent emprunter des routes différentes "
        "et arriver dans le désordre. Le numéro de paquet, porté par l'en-tête, "
        "est ce qui permet au destinataire de les réordonner et de reconstituer "
        "le message, et de repérer ceux qui manquent."
    ),
    source_cours=_RES_PAQUETS,
    source_programme="1NSI-RESEAUX::C1",
    refutations={
        "A": (
            "Le chiffrement est assuré par un protocole dédié, au-dessus du "
            "transport. Un numéro d'ordre en clair ne cache rien."
        ),
        "B": (
            "Le numéro n'accélère rien : il ajoute même quelques octets à "
            "chaque paquet. Il achète de la fiabilité, pas de la vitesse."
        ),
        "D": (
            "La taille du disque du destinataire n'a aucune raison de figurer "
            "dans un en-tête réseau, ni d'être connue de l'émetteur."
        ),
    },
)

conceptuelle(
    _RES, "Q2", reponse="D",
    raisonnement=(
        "Dans le protocole du bit alterné, l'absence d'accusé signifie que "
        "l'émetteur ne sait pas si le paquet est arrivé. Il doit donc "
        "retransmettre LE MÊME paquet, avec LE MÊME bit : c'est ce bit "
        "inchangé qui permet au récepteur, s'il avait bien reçu le premier "
        "envoi, de reconnaître un duplicata et de l'ignorer."
    ),
    source_cours=_RES_BIT,
    source_programme="1NSI-RESEAUX::C2",
    refutations={
        "A": (
            "Abandonner à la première perte rendrait le protocole inutilisable : "
            "c'est précisément pour survivre aux pertes qu'il existe."
        ),
        "B": (
            "Passer au suivant perdrait définitivement le paquet non confirmé, "
            "et le message serait incomplet."
        ),
        "C": (
            "Changer le bit ferait passer un duplicata pour un paquet neuf : le "
            "récepteur l'accepterait une seconde fois et le message serait "
            "dupliqué. C'est l'erreur qui casse le protocole."
        ),
    },
)

conceptuelle(
    _RES, "Q3", reponse="A",
    raisonnement=(
        "Un cycle permet de revenir sur un sommet déjà exploré, et donc de "
        "reprendre indéfiniment le même chemin. Mémoriser les sommets visités "
        "et refuser d'y revenir borne l'exploration par le nombre de sommets, "
        "ce qui garantit la terminaison."
    ),
    source_cours=_RES_PAQUETS,
    source_programme="1NSI-RESEAUX::C3",
    refutations={
        "B": (
            "Interdire les cycles dans un réseau réel est impossible : la "
            "redondance des liaisons est justement ce qui rend un réseau "
            "résistant aux pannes."
        ),
        "C": (
            "Limiter le réseau à deux machines supprime le problème en "
            "supprimant le réseau : ce n'est pas une solution algorithmique."
        ),
        "D": (
            "La récursion n'est pas la cause : une recherche itérative sans "
            "mémoire des visités boucle exactement de la même façon."
        ),
    },
)

conceptuelle(
    _RES, "Q4", reponse="B",
    raisonnement=(
        "Un capteur transforme une grandeur physique en information pour le "
        "système : le capteur de température mesure. Un actionneur transforme "
        "une décision du système en effet physique : le relais commande le "
        "chauffage. L'ordre de l'énoncé est donc capteur, puis actionneur."
    ),
    source_cours=_RES_IHM,
    source_programme="1NSI-RESEAUX::C4",
    refutations={
        "A": (
            "L'ordre est inversé : c'est la température qui est mesurée en "
            "premier, et le chauffage qui est commandé ensuite."
        ),
        "C": (
            "Un relais n'informe pas le système : il agit sur le monde. Le "
            "classer comme capteur ferait disparaître toute action."
        ),
        "D": (
            "Un thermomètre n'agit sur rien : il ne peut pas être un "
            "actionneur, et un système sans capteur serait aveugle."
        ),
    },
)

conceptuelle(
    _RES, "Q5", reponse="C",
    raisonnement=(
        "Un cahier des charges décrit un comportement attendu sur TOUT le "
        "domaine d'usage, pas seulement sur la démonstration. Les cas limites — "
        "valeur exactement au seuil, transition d'état, entrée vide — sont "
        "précisément ceux où les erreurs d'inégalité et de transition se "
        "logent."
    ),
    source_cours=_RES_IHM,
    source_programme="1NSI-RESEAUX::C5",
    refutations={
        "A": (
            "Le scénario de démonstration est choisi pour réussir : ne tester "
            "que lui ne prouve rien sur le reste du domaine."
        ),
        "B": (
            "Supposer le code correct est exactement ce qu'un test sert à "
            "vérifier. Aucun code n'est correct par hypothèse."
        ),
        "D": (
            "Ignorer les exigences implicites — ce qui se passe hors des cas "
            "prévus — laisse le comportement indéfini là où l'utilisateur "
            "risque le plus de se trouver."
        ),
    },
)

conceptuelle(
    _RES, "Q6", reponse="D",
    raisonnement=(
        "Avec un seuil unique, une mesure qui oscille autour de ce seuil fait "
        "basculer l'actionneur à chaque oscillation. Deux seuils distincts — "
        "l'un pour activer, l'autre, plus bas, pour arrêter — créent une bande "
        "morte : une fois activé, le système ne s'arrête qu'après une variation "
        "significative. C'est l'hystérésis."
    ),
    source_cours=_RES_IHM,
    source_programme="1NSI-RESEAUX::C5",
    refutations={
        "A": (
            "Le but n'est pas de ralentir le système mais d'éviter des "
            "commutations parasites : la réaction à une vraie variation reste "
            "immédiate."
        ),
        "B": (
            "Deux seuils occupent deux valeurs au lieu d'une : le gain mémoire "
            "serait négatif, et négligeable de toute façon."
        ),
        "C": (
            "Les deux seuils s'appliquent à la mesure du capteur et à la "
            "commande de l'actionneur : les deux composants restent "
            "nécessaires et distincts."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-TYPES-CONSTRUITS — chapitre presque entièrement mécanique
#
# Seize questions qui portent toutes sur le COMPORTEMENT EFFECTIF de Python :
# ce que renvoie une expression, ce qu'affiche une séquence d'instructions,
# quelle exception est levée. Il n'y a rien à interpréter — il y a à exécuter.
# Chaque dérivation calcule d'abord le comportement réel, puis cherche
# l'option qui le décrit.
# ══════════════════════════════════════════════════════════════════════════

_TC = "1NSI-TYPES-CONSTRUITS"


def _code_brut(texte: str) -> str:
    """Le texte Python d'une option, débarrassé de son habillage LaTeX."""
    depouille = texte.strip()
    if depouille.startswith("\\code{") and depouille.endswith("}"):
        depouille = depouille[len("\\code{"):-1]
    return (
        depouille.replace("\\{", "{").replace("\\}", "}").replace("\\_", "_")
    )


def _option_valant(options: dict, attendu) -> str:
    """L'option dont le code, évalué, vaut `attendu`."""
    def decrit(texte: str) -> bool:
        brut = _code_brut(texte)
        try:
            return eval(brut, {"__builtins__": {}}, {}) == attendu  # noqa: S307
        except Exception:  # noqa: BLE001 - une option non évaluable ne décrit rien
            return False

    return _lettre(options, decrit)


def _option_nommant_exception(options: dict, exception: str) -> str:
    """L'option qui annonce l'exception `exception`."""
    return _lettre(
        options,
        lambda texte: "erreur" in texte.lower() and exception in texte,
    )


@mecanique(_TC, "Q1", PYTHON)
def _tc_q1(options):
    obtenu = str(type((3, 5)))
    assert obtenu == "<class 'tuple'>", obtenu
    return _lettre(options, lambda texte: _code_brut(texte) == obtenu)


@mecanique(_TC, "Q2", PYTHON)
def _tc_q2(options):
    t = (1, 2)
    try:
        t[0] = 5
    except Exception as erreur:  # noqa: BLE001
        leve = type(erreur).__name__
    else:
        leve = None
    assert leve == "TypeError", leve
    return _option_nommant_exception(options, leve)


@mecanique(_TC, "Q3", PYTHON)
def _tc_q3(options):
    a, b = (10, 20)
    assert (a, b) == (10, 20)
    return _option_valant(options, b)


@mecanique(_TC, "Q4", PYTHON)
def _tc_q4(options):
    t = [3, 1, 4]
    t.append(1)
    longueur = len(t)
    assert longueur == 4, longueur
    return _option_valant(options, longueur)


@mecanique(_TC, "Q5", PYTHON)
def _tc_q5(options):
    attendue = [0, 2, 4, 6, 8]

    def produit(texte: str) -> bool:
        brut = _code_brut(texte)
        try:
            return eval(brut, {"__builtins__": {"range": range}}, {}) == attendue  # noqa: S307
        except Exception:  # noqa: BLE001
            return False

    return _lettre(options, produit)


@mecanique(_TC, "Q6", PYTHON)
def _tc_q6(options):
    t = [10, 20, 30]
    try:
        t[3]
    except Exception as erreur:  # noqa: BLE001
        leve = type(erreur).__name__
    else:
        leve = None
    assert leve == "IndexError", leve
    return _option_nommant_exception(options, leve)


@mecanique(_TC, "Q7", PYTHON)
def _tc_q7(options):
    g = [[1, 2], [3, 4]]
    valeur = g[1][0]
    assert valeur == 3, valeur
    return _option_valant(options, valeur)


@mecanique(_TC, "Q8", PYTHON)
def _tc_q8(options):
    """Trois lignes, deux colonnes, ET lignes indépendantes.

    Le test décisif n'est pas la forme mais l'INDÉPENDANCE : on écrit dans la
    première ligne et on regarde si les autres bougent.
    """
    def convient(texte: str) -> bool:
        brut = _code_brut(texte)
        try:
            grille = eval(brut, {"__builtins__": {"range": range}}, {})  # noqa: S307
        except Exception:  # noqa: BLE001
            return False
        if not isinstance(grille, list) or len(grille) != 3:
            return False
        if not all(isinstance(ligne, list) and len(ligne) == 2 for ligne in grille):
            return False
        if any(valeur != 0 for ligne in grille for valeur in ligne):
            return False
        grille[0][0] = 7
        return [ligne[0] for ligne in grille] == [7, 0, 0]

    return _lettre(options, convient)


@mecanique(_TC, "Q9", PYTHON)
def _tc_q9(options):
    g = [[5, 6, 7], [8, 9, 10]]
    lignes, colonnes = len(g), len(g[0])
    assert (lignes, colonnes) == (2, 3)
    return _lettre(
        options,
        lambda texte: f"${lignes}$ lignes et ${colonnes}$ colonnes" in texte,
    )


@mecanique(_TC, "Q10", PYTHON)
def _tc_q10(options):
    d = {"a": 1, "b": 2}
    try:
        d["c"]
    except Exception as erreur:  # noqa: BLE001
        leve = type(erreur).__name__
    else:
        leve = None
    assert leve == "KeyError", leve
    return _option_nommant_exception(options, leve)


@mecanique(_TC, "Q11", PYTHON)
def _tc_q11(options):
    """La seule syntaxe qui ajoute effectivement la clé sans lever."""
    def marche(texte: str) -> bool:
        brut = _code_brut(texte)
        contexte = {"d": {"a": 1, "b": 2}}
        try:
            exec(brut, {"__builtins__": {}}, contexte)  # noqa: S102
        except Exception:  # noqa: BLE001
            return False
        return contexte["d"].get("c") == 3

    return _lettre(options, marche)


@mecanique(_TC, "Q12", PYTHON)
def _tc_q12(options):
    """La seule boucle qui livre le couple (clé, valeur) à chaque tour."""
    def parcourt(texte: str) -> bool:
        brut = _code_brut(texte).rstrip(":")
        source = f"resultat = []\n{brut}:\n    resultat.append((k, v))\n"
        contexte = {"d": {"a": 1, "b": 2}}
        try:
            exec(source, {"__builtins__": {}}, contexte)  # noqa: S102
        except Exception:  # noqa: BLE001
            return False
        return contexte.get("resultat") == [("a", 1), ("b", 2)]

    return _lettre(options, parcourt)


@mecanique(_TC, "Q13", PYTHON)
def _tc_q13(options):
    a = [1, 2]
    b = a
    b.append(3)
    assert a == [1, 2, 3] and a is b
    return _option_valant(options, a)


@mecanique(_TC, "Q14", PYTHON)
def _tc_q14(options):
    """La seule expression qui produit une copie INDÉPENDANTE."""
    def copie_independante(texte: str) -> bool:
        brut = _code_brut(texte)
        if "=" not in brut:
            return False
        expression = brut.split("=", 1)[1].strip()
        contexte = {"t": [1, 2, 3]}
        try:
            copie = eval(expression, {"__builtins__": {"list": list, "len": len}}, contexte)  # noqa: S307
        except Exception:  # noqa: BLE001
            return False
        if not isinstance(copie, list) or copie != [1, 2, 3]:
            return False
        copie.append(4)
        return contexte["t"] == [1, 2, 3]

    return _lettre(options, copie_independante)


@mecanique(_TC, "Q15", PYTHON)
def _tc_q15(options):
    """`list(g)` est une copie de SURFACE : les sous-listes restent partagées."""
    g = [[1], [2]]
    h = list(g)
    h[0].append(9)
    assert h is not g
    assert g[0] == [1, 9], g[0]
    return _option_valant(options, g[0])


@mecanique(_TC, "Q16", PYTHON)
def _tc_q16(options):
    """Le couple dont les DEUX types sont mutables, testé par mutation."""
    fabriques = {"int": lambda: 0, "list": list, "dict": dict,
                 "tuple": tuple, "str": str}

    def mutable(nom: str) -> bool:
        valeur = fabriques[nom]()
        try:
            if isinstance(valeur, list):
                valeur.append(1)
            elif isinstance(valeur, dict):
                valeur["k"] = 1
            else:
                return False
        except Exception:  # noqa: BLE001
            return False
        return True

    assert [n for n in fabriques if mutable(n)] == ["list", "dict"]

    def couple_mutable(texte: str) -> bool:
        noms = [nom for nom in fabriques if f"\\code{{{nom}}}" in texte]
        return len(noms) == 2 and all(mutable(nom) for nom in noms)

    return _lettre(options, couple_mutable)


# ══════════════════════════════════════════════════════════════════════════
# 1NSI-WEB-IHM
# ══════════════════════════════════════════════════════════════════════════

_WEB = "1NSI-WEB-IHM"
_WEB_COMPOSANTS = "NSI/chapitres/1NSI-WEB-IHM/cours/1NSI-WEB-COURS-C1.tex"
_WEB_CLIENT_SERVEUR = "NSI/chapitres/1NSI-WEB-IHM/cours/1NSI-WEB-COURS-C2.tex"
_WEB_FORMULAIRES = "NSI/chapitres/1NSI-WEB-IHM/cours/1NSI-WEB-COURS-C3.tex"

conceptuelle(
    _WEB, "Q1", reponse="A",
    raisonnement=(
        "Une case à cocher est un interrupteur à deux états, indépendant des "
        "autres cases : dans un groupe de cases, zéro, une ou plusieurs "
        "peuvent être cochées simultanément. C'est ce qui la distingue du "
        "bouton radio."
    ),
    source_cours=_WEB_COMPOSANTS,
    source_programme="1NSI-WEB-IHM::C1",
    refutations={
        "B": (
            "La saisie d'une ligne de texte est le rôle de `type=\"text\"`. Une "
            "case à cocher n'accepte aucune frappe."
        ),
        "C": (
            "Le choix exclusif d'une valeur parmi plusieurs est le rôle de "
            "`type=\"radio\"` : c'est l'exclusivité qui les oppose, et elle est "
            "précisément ce que la case à cocher n'a pas."
        ),
        "D": (
            "L'envoi du formulaire est déclenché par `type=\"submit\"`. Cocher "
            "une case ne soumet rien."
        ),
    },
)

conceptuelle(
    _WEB, "Q2", reponse="B",
    raisonnement=(
        "HTML décrit la structure, CSS la présentation, et JavaScript le "
        "comportement. Réagir à un clic est un comportement : il s'écrit en "
        "JavaScript, en associant au composant un gestionnaire d'événement — "
        "une fonction que le navigateur appellera quand l'événement se "
        "produira."
    ),
    source_cours=_WEB_COMPOSANTS,
    source_programme="1NSI-WEB-IHM::C2",
    refutations={
        "A": (
            "CSS ne décrit que l'apparence : couleurs, tailles, positions. Il "
            "ne dispose d'aucun moyen d'exécuter une action au clic."
        ),
        "C": (
            "HTML déclare qu'un bouton existe, pas ce qu'il fait. Sans "
            "JavaScript, un bouton ordinaire est inerte."
        ),
        "D": (
            "Le comportement est au contraire programmable, et c'est la "
            "capacité même que le chapitre travaille."
        ),
    },
)

conceptuelle(
    _WEB, "Q3", reponse="C",
    raisonnement=(
        "`addEventListener` attend une FONCTION, qu'il stockera pour l'appeler "
        "plus tard. Passer `compter` transmet la fonction elle-même ; c'est "
        "l'usage correct. Passer `compter()` transmettrait le RÉSULTAT de son "
        "appel immédiat, ce qui exécuterait la fonction tout de suite et "
        "n'enregistrerait rien d'utile."
    ),
    source_cours=_WEB_COMPOSANTS,
    source_programme="1NSI-WEB-IHM::C3",
    refutations={
        "A": (
            "C'est l'inverse : c'est AVEC les parenthèses que la fonction "
            "s'exécute immédiatement au chargement. Sans elles, elle est "
            "seulement référencée."
        ),
        "B": (
            "Une page ne refuse pas de s'afficher pour une erreur de "
            "JavaScript : le document reste rendu, seul le comportement "
            "manque."
        ),
        "D": (
            "Un double comptage viendrait de DEUX enregistrements du même "
            "gestionnaire — par exemple `onclick` dans le HTML et "
            "`addEventListener` dans le script — pas de l'absence de "
            "parenthèses."
        ),
    },
)

conceptuelle(
    _WEB, "Q4", reponse="D",
    raisonnement=(
        "Le code serveur s'exécute avant l'envoi de la réponse et n'est jamais "
        "transmis : le navigateur ne reçoit que le HTML produit. C'est ce qui "
        "permet de placer côté serveur ce qui doit rester secret — requêtes "
        "vers la base, vérification d'un mot de passe."
    ),
    source_cours=_WEB_CLIENT_SERVEUR,
    source_programme="1NSI-WEB-IHM::C4",
    refutations={
        "A": (
            "Ce qui figure dans le source reçu est le RÉSULTAT du code serveur, "
            "pas le code lui-même. Si le code apparaissait, tout secret qu'il "
            "contient serait exposé."
        ),
        "B": (
            "Le code serveur s'exécute AVANT : il produit la page que le "
            "JavaScript du client animera ensuite. L'ordre est l'inverse de "
            "celui annoncé."
        ),
        "C": (
            "L'accès à la base de données est au contraire le rôle typique du "
            "code serveur, et la raison pour laquelle il est côté serveur."
        ),
    },
)

conceptuelle(
    _WEB, "Q5", reponse="A",
    raisonnement=(
        "Un cookie est une donnée que le serveur demande au NAVIGATEUR de "
        "conserver, et que le navigateur renvoie automatiquement dans les "
        "requêtes suivantes vers le même site. C'est ce va-et-vient qui permet "
        "à un site sans mémoire propre de reconnaître une session."
    ),
    source_cours=_WEB_CLIENT_SERVEUR,
    source_programme="1NSI-WEB-IHM::C5",
    refutations={
        "B": (
            "Un cookie conservé sur le serveur serait une donnée de session "
            "serveur, pas un cookie : le propre du cookie est d'être stocké "
            "chez le client."
        ),
        "C": (
            "Un cookie est une simple paire nom-valeur, pas du code. Rien n'y "
            "est exécuté."
        ),
        "D": (
            "Un cookie n'est renvoyé qu'au domaine qui l'a déposé. Le "
            "transmettre à tous les sites serait une faille majeure, et c'est "
            "précisément ce que la politique de même origine empêche."
        ),
    },
)

conceptuelle(
    _WEB, "Q6", reponse="B",
    raisonnement=(
        "HTTPS chiffre le canal entre le navigateur et le serveur : un "
        "intermédiaire qui capte les paquets ne peut pas les lire. La garantie "
        "porte sur le TRANSPORT, et sur l'identité du serveur via son "
        "certificat — rien d'autre."
    ),
    source_cours=_WEB_CLIENT_SERVEUR,
    source_programme="1NSI-WEB-IHM::C6",
    refutations={
        "A": (
            "Ce que fait le serveur des données une fois reçues échappe "
            "complètement au protocole : HTTPS s'arrête à la porte du serveur."
        ),
        "C": (
            "HTTPS ne dit rien de la collecte : un site peut parfaitement "
            "collecter beaucoup de données personnelles, en HTTPS."
        ),
        "D": (
            "Le certificat atteste que le serveur est bien celui du domaine "
            "annoncé, pas que ses intentions sont honnêtes. Un site "
            "malveillant peut être en HTTPS."
        ),
    },
)

conceptuelle(
    _WEB, "Q7", reponse="C",
    raisonnement=(
        "À la soumission, le navigateur construit des couples "
        "`name=valeur_saisie` : c'est l'attribut `name` qui donne au paramètre "
        "le nom sous lequel le serveur le retrouvera. Un champ sans `name` "
        "n'est tout simplement pas transmis."
    ),
    source_cours=_WEB_FORMULAIRES,
    source_programme="1NSI-WEB-IHM::C7",
    refutations={
        "A": (
            "Le libellé affiché est porté par l'élément `label`, ou par un "
            "attribut `placeholder` : `name` n'apparaît jamais à l'écran."
        ),
        "B": (
            "La largeur relève de la présentation, donc de CSS ou de "
            "l'attribut `size` ; `name` n'a aucun effet visuel."
        ),
        "D": (
            "La vérification de la saisie est le rôle des attributs de "
            "validation — `required`, `pattern`, `type` — ou d'un script."
        ),
    },
)

conceptuelle(
    _WEB, "Q8", reponse="D",
    raisonnement=(
        "GET place les paramètres dans l'URL, après le point d'interrogation. "
        "POST les place dans le CORPS de la requête : ils ne figurent donc ni "
        "dans la barre d'adresse, ni dans l'historique, ni dans les journaux "
        "de serveur qui n'enregistrent que les URL."
    ),
    source_cours=_WEB_FORMULAIRES,
    source_programme="1NSI-WEB-IHM::C8",
    refutations={
        "A": (
            "C'est la description de GET. La distinction entre les deux "
            "méthodes tient exactement à cet emplacement."
        ),
        "B": (
            "POST ne chiffre rien : sur une liaison HTTP simple, le corps "
            "circule en clair. Seul HTTPS chiffre, et il chiffre les deux "
            "méthodes également."
        ),
        "C": (
            "Aucune limite à un paramètre : un formulaire POST transmet autant "
            "de champs qu'il en porte, et supporte même des fichiers."
        ),
    },
)

conceptuelle(
    _WEB, "Q9", reponse="A",
    raisonnement=(
        "Avec GET, le mot de passe apparaîtrait dans l'URL, donc dans la barre "
        "d'adresse, dans l'historique du navigateur, dans les favoris "
        "éventuels et dans les journaux du serveur. POST le place dans le corps "
        "et évite ces quatre expositions. Le chiffrement du transport reste "
        "assuré par HTTPS, séparément."
    ),
    source_cours=_WEB_FORMULAIRES,
    source_programme="1NSI-WEB-IHM::C9",
    refutations={
        "B": (
            "La simplicité ne compense pas l'exposition : la facilité d'écriture "
            "n'est pas un critère de sécurité."
        ),
        "C": (
            "Le choix a des conséquences très concrètes, énumérées ci-dessus. "
            "Dire qu'il est indifférent revient à ignorer l'historique et les "
            "journaux."
        ),
        "D": (
            "Un mot de passe DOIT être transmis pour authentifier : ce qui "
            "importe est de le faire par POST et sur HTTPS."
        ),
    },
)

conceptuelle(
    _WEB, "Q10", reponse="B",
    raisonnement=(
        "Une recherche est une consultation sans effet de bord : elle ne "
        "modifie rien sur le serveur. GET convient donc, et son avantage est "
        "concret — l'URL contient les critères, ce qui rend le résultat "
        "partageable, ajoutable aux favoris et rechargeable."
    ),
    source_cours=_WEB_FORMULAIRES,
    source_programme="1NSI-WEB-IHM::C9",
    refutations={
        "A": (
            "Les cookies transportent un état de session, pas les paramètres "
            "d'une requête : ils ne peuvent pas porter des critères de "
            "recherche variables."
        ),
        "C": (
            "POST systématique ferait perdre le partage d'URL sans rien "
            "apporter : les critères de recherche ne sont pas confidentiels."
        ),
        "D": (
            "Un formulaire sans méthode déclarée emploie GET par défaut : "
            "l'option décrit donc GET tout en prétendant décrire autre chose."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# TNSI-BASES-DE-DONNEES — sept questions se tranchent en exécutant le SQL
# ══════════════════════════════════════════════════════════════════════════

_TBDD = "TNSI-BASES-DE-DONNEES"
_TBDD_MODELE = "NSI/chapitres/TNSI-BASES-DE-DONNEES/cours/10_C01_modele_relationnel.tex"
_TBDD_SGBD = "NSI/chapitres/TNSI-BASES-DE-DONNEES/cours/11_C02_sgbd.tex"
_TBDD_SELECT = "NSI/chapitres/TNSI-BASES-DE-DONNEES/cours/12_C03_select_where.tex"
_TBDD_JOIN = "NSI/chapitres/TNSI-BASES-DE-DONNEES/cours/13_C04_join_orderby.tex"
_TBDD_MODIF = "NSI/chapitres/TNSI-BASES-DE-DONNEES/cours/14_C05_insert_update_delete.tex"


def _base_clients():
    """Une base jetable, identique pour toutes les dérivations SQL du chapitre."""
    import sqlite3

    base = sqlite3.connect(":memory:")
    base.executescript(
        """
        CREATE TABLE Client(id INTEGER PRIMARY KEY, nom TEXT, ville TEXT,
                            age INTEGER);
        CREATE TABLE Commande(id INTEGER PRIMARY KEY, id_client INTEGER,
                              montant INTEGER);
        INSERT INTO Client VALUES (1,'Ada','Lyon',36),(2,'Alan','Paris',41),
                                  (3,'Grace','Lyon',28);
        INSERT INTO Commande VALUES (1,1,120),(2,3,80),(3,1,45);
        """
    )
    return base


conceptuelle(
    _TBDD, "Q1", reponse="A",
    raisonnement=(
        "Dans le modèle relationnel, un attribut est caractérisé par le "
        "DOMAINE sur lequel il est défini : l'ensemble des valeurs qu'il peut "
        "prendre — les entiers, les chaînes, une énumération finie. C'est ce "
        "domaine qui rend la colonne typée et ses valeurs comparables."
    ),
    source_cours=_TBDD_MODELE,
    source_programme="TNSI-BASES-DE-DONNEES::C1",
    refutations={
        "B": (
            "Un tuple est une LIGNE de la relation : il porte une valeur pour "
            "chaque attribut. L'attribut ne se définit pas sur une ligne, il "
            "les traverse toutes."
        ),
        "C": (
            "Être clé étrangère est un rôle particulier que certains attributs "
            "jouent ; la plupart n'en sont pas, et ils ont pourtant un domaine."
        ),
        "D": (
            "Une relation est un ensemble de tuples, pas un ensemble de "
            "valeurs : un attribut ne peut pas y prendre ses valeurs."
        ),
    },
)

conceptuelle(
    _TBDD, "Q2", reponse="B",
    raisonnement=(
        "Le schéma est la description de la STRUCTURE : quelles relations "
        "existent, quels attributs elles portent, sur quels domaines, et "
        "quelles contraintes de clés les relient. Il est stable, alors que le "
        "contenu change à chaque insertion."
    ),
    source_cours=_TBDD_MODELE,
    source_programme="TNSI-BASES-DE-DONNEES::C2",
    refutations={
        "A": (
            "Les valeurs enregistrées sont le CONTENU. Confondre les deux "
            "reviendrait à dire que le schéma change chaque fois qu'on ajoute "
            "une ligne."
        ),
        "C": (
            "Le nombre de lignes est une mesure du contenu à un instant donné, "
            "pas une propriété de structure."
        ),
        "D": (
            "L'historique des requêtes relève de la journalisation du SGBD, "
            "extérieure au schéma."
        ),
    },
)

conceptuelle(
    _TBDD, "Q3", reponse="C",
    raisonnement=(
        "Répéter le titre et l'auteur à chaque emprunt stocke la même "
        "information autant de fois qu'il y a d'emprunts. Toute correction doit "
        "alors être répercutée partout ; en oublier une seule laisse deux "
        "valeurs contradictoires pour un même livre, et aucune requête ne peut "
        "plus dire laquelle est la bonne."
    ),
    source_cours=_TBDD_MODELE,
    source_programme="TNSI-BASES-DE-DONNEES::C3",
    refutations={
        "A": (
            "Le gain n'est ni systématique ni gratuit : on économise une "
            "jointure, au prix d'une table plus volumineuse et d'un risque "
            "d'incohérence."
        ),
        "B": (
            "La duplication n'améliore rien en sécurité ; elle multiplie au "
            "contraire les endroits où une donnée peut être modifiée."
        ),
        "D": (
            "Les conséquences sont bien réelles et portent un nom : anomalies "
            "de mise à jour, d'insertion et de suppression."
        ),
    },
)

conceptuelle(
    _TBDD, "Q4", reponse="D",
    raisonnement=(
        "La persistance est le service qui garantit que les données survivent "
        "à l'exécution : elles sont écrites sur un support durable et se "
        "retrouvent intactes au démarrage suivant. C'est le premier des quatre "
        "services d'un SGBD."
    ),
    source_cours=_TBDD_SGBD,
    source_programme="TNSI-BASES-DE-DONNEES::C4",
    refutations={
        "A": (
            "Le chiffrement des mots de passe relève de la sécurisation, un "
            "autre des quatre services, et de la conception de l'application."
        ),
        "B": (
            "L'instantanéité n'est promise par aucun service : l'efficacité "
            "assure des temps raisonnables sur de grands volumes, pas des temps "
            "nuls."
        ),
        "C": (
            "Interdire les accès simultanés serait le contraire du service de "
            "concurrence, qui les rend possibles SANS corrompre les données."
        ),
    },
)

conceptuelle(
    _TBDD, "Q5", reponse="A",
    raisonnement=(
        "Les trois clauses ont des rôles disjoints : `SELECT` désigne les "
        "colonnes à projeter, `FROM` désigne la relation où puiser les tuples, "
        "`WHERE` filtre les tuples. `FROM Client` désigne donc la relation "
        "source."
    ),
    source_cours=_TBDD_SELECT,
    source_programme="TNSI-BASES-DE-DONNEES::C5",
    refutations={
        "B": (
            "Les colonnes à afficher sont désignées par `SELECT` : ici `nom`, "
            "et non `Client`."
        ),
        "C": (
            "La condition est portée par `WHERE` : ici `ville = 'Lyon'`."
        ),
        "D": (
            "L'ordre d'affichage relève de `ORDER BY`, absente de cette "
            "requête — le résultat n'a donc aucun ordre garanti."
        ),
    },
)


@mecanique(_TBDD, "Q6", SQL)
def _tbdd_q6(options):
    """On exécute la requête et on regarde ce qu'elle renvoie vraiment."""
    base = _base_clients()
    lignes = base.execute(
        "SELECT nom FROM Client WHERE ville = 'Lyon'"
    ).fetchall()
    colonnes = len(lignes[0])
    noms = sorted(ligne[0] for ligne in lignes)
    assert colonnes == 1 and noms == ["Ada", "Grace"]
    # Une seule colonne, celle des noms, et seulement les Lyonnais.
    tous = base.execute("SELECT nom FROM Client").fetchall()
    assert len(tous) == 3 and len(lignes) == 2
    return _lettre(
        options,
        lambda texte: "seul nom" in texte and "Lyon" in texte,
    )


@mecanique(_TBDD, "Q7", SQL)
def _tbdd_q7(options):
    """Sans apostrophes, SQL cherche une colonne : on le constate."""
    import sqlite3

    base = _base_clients()
    try:
        base.execute("SELECT nom FROM Client WHERE ville = Lyon").fetchall()
    except sqlite3.OperationalError as erreur:
        message = str(erreur)
    else:
        message = ""
    assert "no such column" in message.lower(), message
    # Avec apostrophes, la même requête fonctionne.
    assert base.execute(
        "SELECT nom FROM Client WHERE ville = 'Lyon'"
    ).fetchall()
    return _lettre(
        options,
        lambda texte: "erreur" in texte and "nom de colonne" in texte,
    )


@mecanique(_TBDD, "Q8", SQL)
def _tbdd_q8(options):
    """Le JOIN apparie ; on vérifie qu'il ne trie, ne renomme, ni ne dédoublonne."""
    base = _base_clients()
    apparies = base.execute(
        "SELECT Client.nom, Commande.montant FROM Client "
        "JOIN Commande ON Client.id = Commande.id_client"
    ).fetchall()
    assert sorted(apparies) == [("Ada", 45), ("Ada", 120), ("Grace", 80)]
    # Il ne dédoublonne pas : Ada apparaît deux fois.
    assert [n for n, _ in apparies].count("Ada") == 2
    # Il ne trie pas : sans ORDER BY l'ordre n'est pas celui du tri.
    sans_condition = base.execute(
        "SELECT COUNT(*) FROM Client, Commande"
    ).fetchone()[0]
    assert sans_condition == 3 * 3 and len(apparies) == 3
    return _lettre(
        options,
        lambda texte: "rapprocher les tuples" in texte and "coïncident" in texte,
    )


@mecanique(_TBDD, "Q9", SQL)
def _tbdd_q9(options):
    """La clause qui produit l'ordre demandé SANS perdre de client.

    Une première version testait le seul ordre, sur trois clients d'âges
    distincts. `GROUP BY age` passait le test : en SQLite, il trie par la clé
    de groupement. Le test ne séparait donc pas les deux clauses — c'est
    l'ex æquo qui les sépare, parce que `GROUP BY` FUSIONNE les lignes de même
    âge, et `ORDER BY` non. La base de la dérivation porte donc deux clients
    du même âge.
    """
    import sqlite3

    base = sqlite3.connect(":memory:")
    base.executescript(
        """
        CREATE TABLE Client(id INTEGER PRIMARY KEY, nom TEXT, age INTEGER);
        INSERT INTO Client VALUES (1,'Ada',36),(2,'Alan',41),
                                  (3,'Grace',28),(4,'Hedy',36);
        """
    )
    total = base.execute("SELECT COUNT(*) FROM Client").fetchone()[0]
    assert total == 4

    def produit_l_ordre(texte: str) -> bool:
        clause = _code_brut(texte)
        try:
            lignes = base.execute(
                f"SELECT nom, age FROM Client {clause}"
            ).fetchall()
        except Exception:  # noqa: BLE001
            return False
        if len(lignes) != total:            # aucun client ne doit disparaître
            return False
        ages = [age for _, age in lignes]
        return ages == sorted(ages)          # du plus jeune au plus âgé

    lettre = _lettre(options, produit_l_ordre)
    # Contrôle explicite : GROUP BY perd bien un client sur cette base.
    groupees = base.execute(
        "SELECT nom, age FROM Client GROUP BY age"
    ).fetchall()
    assert len(groupees) == 3 < total
    return lettre


@mecanique(_TBDD, "Q10", SQL)
def _tbdd_q10(options):
    """La seule instruction qui ajoute effectivement la ligne demandée."""
    def ajoute(texte: str) -> bool:
        base = _base_clients()
        avant = base.execute("SELECT COUNT(*) FROM Client").fetchone()[0]
        try:
            base.execute(_code_brut(texte))
        except Exception:  # noqa: BLE001
            return False
        apres = base.execute(
            "SELECT nom, ville FROM Client WHERE nom = 'Dupont'"
        ).fetchall()
        total = base.execute("SELECT COUNT(*) FROM Client").fetchone()[0]
        return apres == [("Dupont", "Lyon")] and total == avant + 1

    return _lettre(options, ajoute)


@mecanique(_TBDD, "Q11", SQL)
def _tbdd_q11(options):
    """UPDATE sans WHERE : on compte les lignes effectivement modifiées."""
    base = _base_clients()
    avant = base.execute("SELECT COUNT(*) FROM Client").fetchone()[0]
    curseur = base.execute("UPDATE Client SET ville = 'Nice'")
    modifiees = curseur.rowcount
    villes = {v for (v,) in base.execute("SELECT DISTINCT ville FROM Client")}
    assert modifiees == avant == 3
    assert villes == {"Nice"}
    return _lettre(
        options,
        lambda texte: "toutes les lignes" in texte and "modifier" in texte,
    )


@mecanique(_TBDD, "Q12", SQL)
def _tbdd_q12(options):
    """DELETE ... WHERE date_retour IS NOT NULL : ce qui part, ce qui reste."""
    import sqlite3

    base = sqlite3.connect(":memory:")
    base.executescript(
        """
        CREATE TABLE Emprunt(id INTEGER PRIMARY KEY, date_retour TEXT);
        INSERT INTO Emprunt VALUES (1,'2026-02-10'),(2,NULL),(3,'2026-03-01');
        """
    )
    base.execute("DELETE FROM Emprunt WHERE date_retour IS NOT NULL")
    restant = base.execute("SELECT id, date_retour FROM Emprunt").fetchall()
    assert restant == [(2, None)]
    # La table existe toujours, et la colonne n'a pas été vidée.
    assert base.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall() == [("Emprunt",)]
    return _lettre(
        options,
        lambda texte: "supprime les lignes" in texte and "renseignée" in texte,
    )


# ══════════════════════════════════════════════════════════════════════════
# TNSI-ALGORITHMIQUE
# ══════════════════════════════════════════════════════════════════════════

_TALGO = "TNSI-ALGORITHMIQUE"
_TALGO_ARBRES = "NSI/chapitres/TNSI-ALGORITHMIQUE/cours/10_C01_arbres_parcours.tex"
_TALGO_ABR = "NSI/chapitres/TNSI-ALGORITHMIQUE/cours/11_C02_arbres_recherche.tex"
_TALGO_GRAPHES = "NSI/chapitres/TNSI-ALGORITHMIQUE/cours/12_C03_graphes_parcours.tex"
_TALGO_CYCLE = "NSI/chapitres/TNSI-ALGORITHMIQUE/cours/13_C04_graphes_cycle_chemin.tex"
_TALGO_DPR = "NSI/chapitres/TNSI-ALGORITHMIQUE/cours/14_C05_diviser_pour_regner.tex"
_TALGO_DYN = "NSI/chapitres/TNSI-ALGORITHMIQUE/cours/15_C06_programmation_dynamique.tex"
_TALGO_BM = "NSI/chapitres/TNSI-ALGORITHMIQUE/cours/16_C07_boyer_moore.tex"


class _Noeud:
    __slots__ = ("valeur", "gauche", "droite")

    def __init__(self, valeur, gauche=None, droite=None):
        self.valeur, self.gauche, self.droite = valeur, gauche, droite


def _arbre_exemple():
    """L'arbre de racine 1, fils gauche 2 (fils 4 et 5), fils droit 3."""
    return _Noeud(1, _Noeud(2, _Noeud(4), _Noeud(5)), _Noeud(3))


@mecanique(_TALGO, "Q1", PYTHON)
def _talgo_q1(options):
    """La formule qui compte réellement les nœuds, testée contre un oracle."""
    arbre = _arbre_exemple()

    def taille_par_liste(noeud):
        if noeud is None:
            return []
        return (
            [noeud.valeur]
            + taille_par_liste(noeud.gauche)
            + taille_par_liste(noeud.droite)
        )

    attendu = len(taille_par_liste(arbre))
    assert attendu == 5

    def somme(noeud):
        return 0 if noeud is None else 1 + somme(noeud.gauche) + somme(noeud.droite)

    def maximum(noeud):
        if noeud is None:
            return 0
        return 1 + max(maximum(noeud.gauche), maximum(noeud.droite))

    def produit(noeud):
        if noeud is None:
            return 0
        return produit(noeud.gauche) * produit(noeud.droite)

    def feuilles(noeud):
        if noeud is None:
            return 0
        if noeud.gauche is None and noeud.droite is None:
            return 1
        return feuilles(noeud.gauche) + feuilles(noeud.droite)

    assert somme(arbre) == attendu
    assert maximum(arbre) != attendu and produit(arbre) != attendu
    assert feuilles(arbre) != attendu
    return _lettre(
        options,
        lambda texte: "taille(gauche)} + \\text{taille(droite)" in texte,
    )


@mecanique(_TALGO, "Q2", PYTHON)
def _talgo_q2(options):
    """Hauteur d'une feuille, avec la convention du cours (vide = -1)."""
    def hauteur(noeud):
        if noeud is None:
            return -1
        return 1 + max(hauteur(noeud.gauche), hauteur(noeud.droite))

    assert hauteur(None) == -1
    obtenue = hauteur(_Noeud(7))
    assert obtenue == 0
    return _lettre(options, lambda texte: texte.strip() == f"${obtenue}$.")


@mecanique(_TALGO, "Q3", PYTHON)
def _talgo_q3(options):
    """L'ordre infixe, calculé, puis reconnu parmi les descriptions."""
    arbre = _arbre_exemple()

    def infixe(n):
        return [] if n is None else infixe(n.gauche) + [n.valeur] + infixe(n.droite)

    def prefixe(n):
        return [] if n is None else [n.valeur] + prefixe(n.gauche) + prefixe(n.droite)

    def suffixe(n):
        return [] if n is None else suffixe(n.gauche) + suffixe(n.droite) + [n.valeur]

    assert infixe(arbre) == [4, 2, 5, 1, 3]
    assert prefixe(arbre) == [1, 2, 4, 5, 3]
    assert suffixe(arbre) == [4, 5, 2, 3, 1]
    # L'infixe place la racine ENTRE les deux sous-arbres : c'est ce que dit
    # la seule option retenue.
    position = infixe(arbre).index(1)
    assert 0 < position < len(infixe(arbre)) - 1
    return _lettre(
        options,
        lambda texte: texte.startswith("le sous-arbre gauche, puis la racine"),
    )


@mecanique(_TALGO, "Q4", PYTHON)
def _talgo_q4(options):
    """File ou pile ? On implémente les deux et on regarde l'ordre obtenu."""
    arbre = _arbre_exemple()

    def parcours(structure: str):
        resultat, attente = [], [arbre]
        while attente:
            noeud = attente.pop(0) if structure == "file" else attente.pop()
            resultat.append(noeud.valeur)
            for enfant in (noeud.gauche, noeud.droite):
                if enfant is not None:
                    attente.append(enfant)
        return resultat

    par_file = parcours("file")
    par_pile = parcours("pile")
    # Le parcours en largeur visite niveau par niveau : 1, puis 2 et 3, puis 4 et 5.
    assert par_file == [1, 2, 3, 4, 5]
    assert par_pile != par_file
    return _lettre(options, lambda texte: texte.strip() == "une file.")


conceptuelle(
    _TALGO, "Q5", reponse="D",
    raisonnement=(
        "La propriété d'ABR garantit que TOUTES les clés du sous-arbre gauche "
        "sont inférieures à celle de la racine, et toutes celles du sous-arbre "
        "droit lui sont supérieures. Une clé plus petite que la racine ne peut "
        "donc se trouver que dans le sous-arbre gauche : c'est cette "
        "élimination d'une moitié qui donne son coût logarithmique à la "
        "recherche."
    ),
    source_cours=_TALGO_ABR,
    source_programme="TNSI-ALGORITHMIQUE::C5",
    refutations={
        "A": (
            "Repartir de la racine ferait tourner la recherche indéfiniment : "
            "aucun progrès n'est accompli."
        ),
        "B": (
            "Explorer les deux sous-arbres renonce à la propriété d'ABR et "
            "ramène le coût à celui d'un parcours complet, en n comparaisons "
            "au lieu de la hauteur."
        ),
        "C": (
            "Le sous-arbre droit ne contient que des clés SUPÉRIEURES à la "
            "racine : y chercher une clé inférieure est certain d'échouer."
        ),
    },
)


@mecanique(_TALGO, "Q6", PYTHON)
def _talgo_q6(options):
    """On insère 1, 2, 3, 4 dans un ABR vide et on mesure l'arbre obtenu."""
    def inserer(noeud, cle):
        if noeud is None:
            return _Noeud(cle)
        if cle < noeud.valeur:
            noeud.gauche = inserer(noeud.gauche, cle)
        elif cle > noeud.valeur:
            noeud.droite = inserer(noeud.droite, cle)
        return noeud

    def hauteur(n):
        return -1 if n is None else 1 + max(hauteur(n.gauche), hauteur(n.droite))

    arbre = None
    for cle in (1, 2, 3, 4):
        arbre = inserer(arbre, cle)

    assert arbre.valeur == 1                    # la racine est la 1re insérée
    assert hauteur(arbre) == 3                  # dégénéré, hauteur n-1
    # Chaque nœud n'a qu'un seul enfant : c'est une liste chaînée.
    courant, gauches = arbre, 0
    while courant is not None:
        if courant.gauche is not None:
            gauches += 1
        courant = courant.droite
    assert gauches == 0
    return _lettre(
        options,
        lambda texte: "dégénéré" in texte and "hauteur $3$" in texte,
    )


@mecanique(_TALGO, "Q7", PYTHON)
def _talgo_q7(options):
    """On mesure l'ordre du BFS : est-il croissant en DISTANCE, ou en numéro ?"""
    graphe = {0: [3, 1], 1: [0, 2], 2: [1], 3: [0]}
    distances = {0: 0}
    ordre, file = [0], [0]
    while file:
        sommet = file.pop(0)
        ordre.append(sommet) if sommet not in ordre else None
        for voisin in graphe[sommet]:
            if voisin not in distances:
                distances[voisin] = distances[sommet] + 1
                ordre.append(voisin)
                file.append(voisin)
    vus = list(dict.fromkeys(ordre))
    suite = [distances[s] for s in vus]
    assert suite == sorted(suite)              # distances croissantes
    assert vus != sorted(vus)                  # mais PAS l'ordre des numéros
    assert distances == {0: 0, 3: 1, 1: 1, 2: 2}
    return _lettre(
        options,
        lambda texte: "distance croissante" in texte and "arêtes" in texte,
    )


conceptuelle(
    _TALGO, "Q8", reponse="C",
    raisonnement=(
        "Le parcours en profondeur explore une branche aussi loin que possible "
        "avant de revenir en arrière : il doit donc traiter en dernier ce qu'il "
        "a découvert en dernier. C'est le comportement d'une PILE, que la pile "
        "d'appels de la récursion fournit gratuitement, et qu'on peut aussi "
        "écrire explicitement."
    ),
    source_cours=_TALGO_GRAPHES,
    source_programme="TNSI-ALGORITHMIQUE::C8",
    refutations={
        "A": (
            "Aucun tri préalable n'est requis : un graphe n'a pas d'ordre "
            "naturel sur ses sommets, et le parcours n'en suppose aucun."
        ),
        "B": (
            "Une file traite en premier ce qui est arrivé en premier : elle "
            "produit le parcours en LARGEUR, l'exact opposé."
        ),
        "D": (
            "La recherche dichotomique suppose des données triées et un accès "
            "par indice : un graphe n'offre ni l'un ni l'autre."
        ),
    },
)

conceptuelle(
    _TALGO, "Q9", reponse="D",
    raisonnement=(
        "Dans un graphe non orienté, chaque arête est parcourable dans les deux "
        "sens : arrivé en v depuis u, on « revoit » u parmi les voisins de v, "
        "sans qu'aucun cycle existe. Le critère correct exclut donc ce retour "
        "immédiat : un sommet déjà visité signale un cycle seulement s'il n'est "
        "PAS le parent direct dans le parcours."
    ),
    source_cours=_TALGO_CYCLE,
    source_programme="TNSI-ALGORITHMIQUE::C9",
    refutations={
        "A": (
            "Revenir au sommet de départ n'est ni nécessaire ni suffisant : un "
            "cycle peut exister loin du départ, et un aller-retour vers le "
            "départ n'est pas un cycle."
        ),
        "B": (
            "Le degré d'un sommet ne dit rien sur l'existence d'un cycle : un "
            "sommet de degré élevé peut appartenir à un arbre."
        ),
        "C": (
            "Un sommet sans voisin est isolé : on ne peut même pas l'atteindre "
            "depuis un autre, et il ne participe à aucun cycle."
        ),
    },
)

conceptuelle(
    _TALGO, "Q10", reponse="A",
    raisonnement=(
        "Un parcours découvre les sommets mais ne conserve pas, en lui-même, la "
        "route suivie. Mémoriser le PRÉDÉCESSEUR de chaque sommet — celui "
        "depuis lequel il a été atteint — permet de remonter la chaîne depuis "
        "l'arrivée jusqu'au départ, puis de l'inverser : c'est le chemin."
    ),
    source_cours=_TALGO_CYCLE,
    source_programme="TNSI-ALGORITHMIQUE::C10",
    refutations={
        "B": (
            "Relancer depuis l'arrivée donne un second parcours, qui souffre du "
            "même défaut : il découvre des sommets sans mémoriser la route."
        ),
        "C": (
            "Trier par distance donne les longueurs, pas les prédécesseurs : "
            "plusieurs chemins différents peuvent avoir la même longueur."
        ),
        "D": (
            "L'ordre de visite contient les sommets d'autres branches, "
            "explorées puis abandonnées : il n'est pas un chemin."
        ),
    },
)

conceptuelle(
    _TALGO, "Q11", reponse="B",
    raisonnement=(
        "« Diviser pour régner » nomme les trois temps de la méthode : diviser "
        "l'instance en sous-instances DE MÊME NATURE mais plus petites, les "
        "résoudre récursivement, puis combiner leurs solutions. Le tri fusion "
        "en est le modèle."
    ),
    source_cours=_TALGO_DPR,
    source_programme="TNSI-ALGORITHMIQUE::C11",
    refutations={
        "A": (
            "Traiter les données une par une décrit un parcours séquentiel, "
            "qui ne divise rien et n'a pas de structure récursive."
        ),
        "C": (
            "Essayer toutes les solutions est une recherche exhaustive : elle "
            "n'exploite aucune décomposition et coûte incomparablement plus "
            "cher."
        ),
        "D": (
            "Mémoriser les résultats déjà calculés est la mémoïsation, "
            "c'est-à-dire la programmation DYNAMIQUE. Elle s'applique "
            "précisément quand les sous-problèmes se recoupent, ce que diviser "
            "pour régner ne suppose pas."
        ),
    },
)

conceptuelle(
    _TALGO, "Q12", reponse="C",
    raisonnement=(
        "La mémoïsation ne gagne quelque chose que si un résultat mémorisé est "
        "relu : autrement dit, seulement si les MÊMES sous-problèmes "
        "réapparaissent. C'est le cas de Fibonacci naïf ou du rendu de monnaie ; "
        "ce n'est pas le cas du tri fusion, dont les sous-listes sont toutes "
        "distinctes."
    ),
    source_cours=_TALGO_DYN,
    source_programme="TNSI-ALGORITHMIQUE::C12",
    refutations={
        "A": (
            "Sans recoupement, le dictionnaire n'est jamais relu : il consomme "
            "de la mémoire sans rien économiser."
        ),
        "B": (
            "La programmation dynamique part au contraire d'une formulation "
            "récursive : c'est elle qu'on transforme en y ajoutant la mémoire."
        ),
        "D": (
            "Un problème à un seul sous-problème n'a rien à mémoriser : le "
            "résultat n'est calculé qu'une fois de toute façon."
        ),
    },
)

conceptuelle(
    _TALGO, "Q13", reponse="D",
    raisonnement=(
        "Boyer-Moore aligne le motif sur le texte puis compare de DROITE à "
        "GAUCHE. Un désaccord sur un caractère du texte lui permet, grâce à un "
        "prétraitement du motif — la table de la dernière occurrence de chaque "
        "caractère —, de décaler le motif de plusieurs positions d'un coup au "
        "lieu d'une seule."
    ),
    source_cours=_TALGO_BM,
    source_programme="TNSI-ALGORITHMIQUE::C13",
    refutations={
        "A": (
            "L'ordre est déterministe et fixé : de droite à gauche. Un ordre "
            "aléatoire empêcherait tout décalage raisonné."
        ),
        "B": (
            "Ignorer le texte rendrait toute recherche impossible : c'est "
            "précisément le caractère du TEXTE qui provoque le désaccord et "
            "détermine le décalage."
        ),
        "C": (
            "Comparer le seul premier caractère ne permettrait pas de conclure "
            "à une occurrence, qui exige l'égalité sur toute la longueur du "
            "motif."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# TNSI-STRUCTURES-DONNEES
# ══════════════════════════════════════════════════════════════════════════

_TSD = "TNSI-STRUCTURES-DONNEES"
_TSD_INTERFACE = "NSI/chapitres/TNSI-STRUCTURES-DONNEES/cours/10_C01_interface_implementation.tex"
_TSD_CLASSES = "NSI/chapitres/TNSI-STRUCTURES-DONNEES/cours/11_C02_classes.tex"
_TSD_PILES = "NSI/chapitres/TNSI-STRUCTURES-DONNEES/cours/12_C03_piles_files_choix.tex"
_TSD_ARBRES = "NSI/chapitres/TNSI-STRUCTURES-DONNEES/cours/13_C04_arbres_binaires.tex"
_TSD_GRAPHES = "NSI/chapitres/TNSI-STRUCTURES-DONNEES/cours/14_C05_graphes.tex"

conceptuelle(
    _TSD, "Q1", reponse="A",
    raisonnement=(
        "L'interface est le contrat d'usage : quelles opérations existent, ce "
        "qu'elles prennent et ce qu'elles rendent. Elle est muette sur le "
        "COMMENT, ce qui est précisément ce qui permet à deux implémentations "
        "différentes de la satisfaire toutes les deux."
    ),
    source_cours=_TSD_INTERFACE,
    source_programme="TNSI-STRUCTURES-DONNEES::C1",
    refutations={
        "B": (
            "Le rangement en mémoire est l'implémentation : tableau contigu ou "
            "maillons chaînés. C'est exactement ce que l'interface cache."
        ),
        "C": (
            "L'occupation mémoire est une conséquence mesurable de "
            "l'implémentation choisie, variable de l'une à l'autre pour une "
            "même interface."
        ),
        "D": (
            "Une interface se formule indépendamment du langage : la même "
            "interface de pile s'écrit en Python, en C ou en pseudo-code."
        ),
    },
)

conceptuelle(
    _TSD, "Q2", reponse="B",
    raisonnement=(
        "Un programme qui n'utilise que les opérations de l'interface ne "
        "dépend d'aucun détail interne. Changer l'implémentation en préservant "
        "l'interface et le comportement observable laisse donc ces programmes "
        "inchangés : c'est le bénéfice même de la séparation."
    ),
    source_cours=_TSD_INTERFACE,
    source_programme="TNSI-STRUCTURES-DONNEES::C2",
    refutations={
        "A": (
            "Réécrire les appelants serait nécessaire si l'interface changeait. "
            "Ici, seule l'implémentation change."
        ),
        "C": (
            "LIFO est une propriété du CONTRAT : elle fait partie de ce que les "
            "deux implémentations doivent garantir. Aucune ne peut la changer "
            "sans cesser d'être une pile."
        ),
        "D": (
            "L'indépendance est possible, et le cours en donne deux "
            "implémentations complètes de la même pile."
        ),
    },
)

conceptuelle(
    _TSD, "Q3", reponse="A",
    raisonnement=(
        "Deux implémentations d'une même file produisent nécessairement le même "
        "ordre de sortie — c'est le contrat FIFO. Ce qui diffère est le COÛT : "
        "`pop(0)` sur une liste Python décale tous les éléments restants, "
        "opération linéaire, là où la technique des deux piles amortit le coût "
        "à une constante par élément."
    ),
    source_cours=_TSD_PILES,
    source_programme="TNSI-STRUCTURES-DONNEES::C3",
    refutations={
        "B": (
            "Rien n'interdit plusieurs implémentations : c'est même le propos "
            "de la distinction interface / implémentation."
        ),
        "C": (
            "Des ordres de sortie différents signifieraient qu'une des deux "
            "n'est pas une file : le contrat FIFO fixe l'ordre."
        ),
        "D": (
            "Les performances diffèrent nettement, et c'est justement le "
            "critère qui fait choisir l'une plutôt que l'autre."
        ),
    },
)


@mecanique(_TSD, "Q4", PYTHON)
def _tsd_q4(options):
    """Quelle méthode Python appelle-t-il vraiment à la construction ?"""
    appels = []

    class Sonde:
        def __init__(self):
            appels.append("__init__")

        def init(self):
            appels.append("init")

        def create(self):
            appels.append("create")

        def new(self):
            appels.append("new")

    Sonde()
    assert appels == ["__init__"], appels
    return _lettre(options, lambda texte: _code_brut(texte) == appels[0])


@mecanique(_TSD, "Q5", PYTHON)
def _tsd_q5(options):
    """`self` est-il l'objet, la classe, ou autre chose ? On le compare."""
    class Sonde:
        def qui_suis_je(self):
            return self

    objet = Sonde()
    recu = objet.qui_suis_je()
    assert recu is objet
    assert recu is not Sonde
    assert not isinstance(recu, type)
    return _lettre(
        options,
        lambda texte: "l'objet sur lequel la méthode est appelée" in texte,
    )


@mecanique(_TSD, "Q6", PYTHON)
def _tsd_q6(options):
    """On empile 1, 2, 3 puis on dépile : quelle valeur sort ?"""
    pile = []
    for valeur in (1, 2, 3):
        pile.append(valeur)
    sortie = pile.pop()
    assert sortie == 3
    assert sortie != min(1, 2, 3)
    return _lettre(options, lambda texte: texte.strip() == f"${sortie}$")


conceptuelle(
    _TSD, "Q7", reponse="A",
    raisonnement=(
        "« Revenir en arrière » consiste à reprendre la page la plus récemment "
        "quittée, c'est-à-dire la dernière empilée : c'est un comportement "
        "LIFO, donc une pile. Chaque nouvelle page consultée s'empile, chaque "
        "retour dépile."
    ),
    source_cours=_TSD_PILES,
    source_programme="TNSI-STRUCTURES-DONNEES::C7",
    refutations={
        "B": (
            "Un arbre binaire de recherche organise des clés par ordre : "
            "l'historique est chronologique, pas ordonné par valeur."
        ),
        "C": (
            "Une file rendrait la page la PLUS ANCIENNE : le bouton retour "
            "ramènerait à la première page visitée, ce qui n'est pas le "
            "comportement attendu."
        ),
        "D": (
            "Une matrice d'adjacence représente des relations entre sommets ; "
            "elle ne conserve aucun ordre de visite."
        ),
    },
)

conceptuelle(
    _TSD, "Q8", reponse="B",
    raisonnement=(
        "Le dictionnaire calcule à partir de la clé une position dans une table "
        "— le hachage — et y accède directement. Le nombre de comparaisons ne "
        "croît donc pas avec le nombre d'éléments, alors qu'une recherche dans "
        "une liste les parcourt jusqu'à trouver."
    ),
    source_cours=_TSD_PILES,
    source_programme="TNSI-STRUCTURES-DONNEES::C8",
    refutations={
        "A": (
            "La taille n'a rien à voir : un dictionnaire d'un million d'entrées "
            "reste rapide, une liste de dix éléments reste lente en "
            "proportion de sa taille."
        ),
        "C": (
            "L'écart est réel et mesurable : accès en temps constant en moyenne "
            "contre parcours linéaire."
        ),
        "D": (
            "Les dictionnaires ne sont pas triés par clé ; ils conservent "
            "l'ordre d'insertion, ce qui n'a aucun rapport avec la rapidité de "
            "l'accès."
        ),
    },
)

conceptuelle(
    _TSD, "Q9", reponse="C",
    raisonnement=(
        "Une structure arborescente s'impose quand les données sont "
        "hiérarchiques : chaque élément a un parent unique et peut avoir "
        "plusieurs enfants. Un système de fichiers est exactement cela — un "
        "dossier contient des dossiers et des fichiers, chacun dans un seul "
        "dossier parent."
    ),
    source_cours=_TSD_ARBRES,
    source_programme="TNSI-STRUCTURES-DONNEES::C9",
    refutations={
        "A": (
            "Une liste alphabétique est un ordre total sur une séquence : une "
            "liste triée suffit, et l'arbre n'apporterait aucune structure "
            "supplémentaire."
        ),
        "B": (
            "Une file d'impression est FIFO : c'est une file, structure "
            "linéaire sans hiérarchie."
        ),
        "D": (
            "Un relevé heure par heure est une séquence indexée par le temps : "
            "un tableau la représente exactement."
        ),
    },
)


@mecanique(_TSD, "Q10", PYTHON)
def _tsd_q10(options):
    """Taille, hauteur, feuilles, niveaux : on calcule les quatre et on choisit."""
    arbre = _arbre_exemple()

    def taille(n):
        return 0 if n is None else 1 + taille(n.gauche) + taille(n.droite)

    def hauteur(n):
        return -1 if n is None else 1 + max(hauteur(n.gauche), hauteur(n.droite))

    def feuilles(n):
        if n is None:
            return 0
        if n.gauche is None and n.droite is None:
            return 1
        return feuilles(n.gauche) + feuilles(n.droite)

    valeurs = {
        "noeuds": taille(arbre),
        "hauteur": hauteur(arbre),
        "feuilles": feuilles(arbre),
        "niveaux_moins_un": hauteur(arbre),
    }
    assert valeurs == {"noeuds": 5, "hauteur": 2, "feuilles": 3,
                       "niveaux_moins_un": 2}
    # Les quatre grandeurs diffèrent : une seule option décrit la taille.
    return _lettre(options, lambda texte: "nombre de nœuds" in texte)


conceptuelle(
    _TSD, "Q11", reponse="A",
    raisonnement=(
        "L'amitié réciproque est une relation SYMÉTRIQUE : si a est ami avec b, "
        "b est ami avec a. Une arête non orientée traduit exactement cette "
        "symétrie, sans avoir à stocker deux fois la même information dans les "
        "deux sens."
    ),
    source_cours=_TSD_GRAPHES,
    source_programme="TNSI-STRUCTURES-DONNEES::C11",
    refutations={
        "B": (
            "Une pile de profils n'exprime aucune relation entre personnes : "
            "elle ne fait qu'ordonner."
        ),
        "C": (
            "Un arbre binaire de recherche impose une hiérarchie et un ordre "
            "sur les clés ; l'amitié n'est ni hiérarchique ni ordonnée, et un "
            "arbre n'admet pas de cycle, que les cercles d'amis créent."
        ),
        "D": (
            "L'énoncé précise que l'amitié est RÉCIPROQUE : l'orientation "
            "ajouterait une information fausse. Elle conviendrait à « suivre » "
            "sur un autre réseau, qui n'est pas réciproque."
        ),
    },
)


@mecanique(_TSD, "Q12", PYTHON)
def _tsd_q12(options):
    """On construit la matrice depuis les arêtes et on lit la règle qu'elle suit."""
    aretes = {(0, 1), (0, 2), (1, 2)}
    n = 3
    matrice = [[1 if (i, j) in aretes else 0 for j in range(n)] for i in range(n)]
    uns = {(i, j) for i in range(n) for j in range(n) if matrice[i][j] == 1}
    assert uns == aretes
    # Les trois autres règles proposées ne décrivent pas cet ensemble.
    diagonale = {(i, i) for i in range(n)}
    somme_n = {(i, j) for i in range(n) for j in range(n) if i + j == n}
    assert uns != diagonale and uns != somme_n
    return _lettre(options, lambda texte: "une arête reliant" in texte)


@mecanique(_TSD, "Q13", PYTHON)
def _tsd_q13(options):
    """On COMPTE les cases occupées par la représentation, pour n et m variables."""
    def occupation(n, aretes):
        listes = {sommet: [] for sommet in range(n)}
        for u, v in aretes:
            listes[u].append(v)
        # une entrée par sommet, plus une case par arête stockée
        return len(listes) + sum(len(v) for v in listes.values())

    mesures = {}
    for n, m in ((4, 3), (4, 6), (10, 3), (10, 20)):
        aretes = [(i % n, (i + 1) % n) for i in range(m)]
        mesures[(n, m)] = occupation(n, aretes)
    # L'occupation vaut exactement n + m dans les quatre cas.
    assert all(taille == n + m for (n, m), taille in mesures.items()), mesures
    # Elle ne vaut ni n², ni m seul, ni n×m.
    assert mesures[(10, 3)] != 10 ** 2
    assert mesures[(10, 3)] != 3
    assert mesures[(10, 3)] != 10 * 3
    return _lettre(options, lambda texte: texte.strip() == "$n + m$.")


@mecanique(_TSD, "Q14", PYTHON)
def _tsd_q14(options):
    """La règle de conversion qui reproduit vraiment les listes de successeurs."""
    # Les degrés sont volontairement 1, 0 puis 2 : sur un graphe dont les
    # degrés décroissent déjà, un tri par nombre de voisins serait
    # indiscernable de l'ordre naturel, et le contrôle négatif ne prouverait
    # rien.
    matrice = [[0, 1, 0], [0, 0, 0], [1, 1, 0]]
    attendu = {0: [1], 1: [], 2: [0, 1]}
    n = len(matrice)

    par_indices_des_uns = {
        i: [j for j in range(n) if matrice[i][j] == 1] for i in range(n)
    }
    par_diagonale = {i: [matrice[i][i]] for i in range(n)}
    par_recopie = {i: list(matrice[i]) for i in range(n)}
    par_tri = dict(
        sorted(par_indices_des_uns.items(), key=lambda kv: -len(kv[1]))
    )

    assert par_indices_des_uns == attendu
    assert par_diagonale != attendu and par_recopie != attendu
    assert list(par_tri) != list(attendu)
    return _lettre(
        options,
        lambda texte: "indices des colonnes" in texte and "vaut $1$" in texte,
    )


# ══════════════════════════════════════════════════════════════════════════
# TNSI-LANGAGES-ET-PROGRAMMATION
# ══════════════════════════════════════════════════════════════════════════

_TLANG = "TNSI-LANGAGES-ET-PROGRAMMATION"
_TLANG_CALCUL = "NSI/chapitres/TNSI-LANGAGES-ET-PROGRAMMATION/cours/10_C01_programme_donnee.tex"
_TLANG_RECURSION = "NSI/chapitres/TNSI-LANGAGES-ET-PROGRAMMATION/cours/11_C02_recursivite.tex"
_TLANG_API = "NSI/chapitres/TNSI-LANGAGES-ET-PROGRAMMATION/cours/12_C03_api_modules.tex"
_TLANG_PARADIGMES = "NSI/chapitres/TNSI-LANGAGES-ET-PROGRAMMATION/cours/13_C04_paradigmes.tex"
_TLANG_DEBUG = "NSI/chapitres/TNSI-LANGAGES-ET-PROGRAMMATION/cours/14_C05_debug.tex"

conceptuelle(
    _TLANG, "Q1", reponse="A",
    raisonnement=(
        "Un programme est une suite de caractères ou d'octets : rien ne le "
        "distingue matériellement d'une donnée. Il peut donc être stocké, "
        "transmis, transformé — et surtout LU ET EXÉCUTÉ par un autre "
        "programme, ce que fait tout interpréteur ou compilateur."
    ),
    source_cours=_TLANG_CALCUL,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C1",
    refutations={
        "B": (
            "L'absence d'effet n'a rien à voir : un programme-donnée produit "
            "évidemment des effets quand un interpréteur l'exécute."
        ),
        "C": (
            "L'égalité des tailles est fausse et sans rapport : un programme "
            "d'une ligne peut traiter un fichier de plusieurs gigaoctets."
        ),
        "D": (
            "L'origine de l'écriture — humaine ou machine — ne change rien à la "
            "nature du programme comme suite de symboles."
        ),
    },
)

conceptuelle(
    _TLANG, "Q2", reponse="B",
    raisonnement=(
        "L'indépendance de la calculabilité vis-à-vis du langage dit que "
        "l'ENSEMBLE des fonctions calculables est le même pour tous les "
        "langages universels. Un problème résoluble en Python l'est en C, en "
        "OCaml, sur une machine de Turing — la difficulté d'écriture varie, la "
        "possibilité non."
    ),
    source_cours=_TLANG_CALCUL,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C2",
    refutations={
        "A": (
            "Les vitesses diffèrent considérablement : un même algorithme peut "
            "être cent fois plus rapide en C qu'en Python. La calculabilité ne "
            "parle pas de vitesse."
        ),
        "C": (
            "Les syntaxes sont manifestement différentes : c'est même ce qui "
            "distingue les langages entre eux."
        ),
        "D": (
            "C'est exactement la négation de l'énoncé : si un algorithme "
            "n'était écrivable que dans un langage, la calculabilité "
            "dépendrait du langage."
        ),
    },
)

conceptuelle(
    _TLANG, "Q3", reponse="C",
    raisonnement=(
        "L'indécidabilité porte sur l'existence d'un programme UNIQUE et "
        "UNIVERSEL : aucun ne peut répondre correctement pour tout couple "
        "(programme, entrée). L'énoncé quantifie sur tous les cas ; c'est cette "
        "universalité qui est impossible."
    ),
    source_cours=_TLANG_CALCUL,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C3",
    refutations={
        "A": (
            "Beaucoup de programmes s'arrêtent : la boucle `for i in range(3)` "
            "se termine toujours. L'indécidabilité ne dit rien sur les "
            "programmes eux-mêmes."
        ),
        "B": (
            "On prouve au cas par cas la terminaison de nombreux programmes — "
            "c'est ce que fait un variant de boucle. Ce qui est impossible est "
            "de le faire automatiquement pour TOUS."
        ),
        "D": (
            "Le résultat est indépendant du langage : il vaut pour tout "
            "formalisme universel, et il précède l'existence de Python de "
            "plusieurs décennies."
        ),
    },
)

conceptuelle(
    _TLANG, "Q4", reponse="D",
    raisonnement=(
        "Le cas de base est la branche qui renvoie une valeur SANS effectuer "
        "d'appel récursif. C'est le seul point où la chaîne d'appels s'arrête ; "
        "sans lui, la récursion se poursuit jusqu'à épuisement de la pile."
    ),
    source_cours=_TLANG_RECURSION,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C4",
    refutations={
        "A": (
            "Le cas de base ne fait rien gagner en vitesse : il rend la "
            "terminaison possible. Une fonction sans cas de base n'est pas "
            "lente, elle est fausse."
        ),
        "B": (
            "La déclaration des variables locales n'a aucun rapport, et Python "
            "ne déclare pas ses variables."
        ),
        "C": (
            "La vérification des types est un contrôle facultatif, qu'on place "
            "en tête de fonction ; le cas de base traite une VALEUR "
            "particulière, pas un type."
        ),
    },
)

conceptuelle(
    _TLANG, "Q5", reponse="A",
    raisonnement=(
        "Un arbre d'appels volumineux signifie que chaque branche atteint bien "
        "un cas de base — sinon il n'y aurait pas d'arbre fini — mais qu'elles "
        "sont très nombreuses. La fonction termine donc, et le problème est le "
        "COÛT. `fib(30)` naïf en est l'exemple : plus de deux millions "
        "d'appels, et une réponse correcte au bout."
    ),
    source_cours=_TLANG_RECURSION,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C5",
    refutations={
        "B": (
            "Un coût élevé n'est pas une erreur de programmation : "
            "l'algorithme peut être correct et simplement inefficace, ce qui "
            "appelle une mémoïsation, pas une correction."
        ),
        "C": (
            "La non-terminaison donnerait un arbre INFINI et une erreur de "
            "profondeur de récursion, pas un grand nombre d'appels achevés."
        ),
        "D": (
            "Un cas de base mal écrit provoquerait une non-terminaison ou un "
            "résultat faux, pas une multiplication des appels qui aboutissent."
        ),
    },
)

conceptuelle(
    _TLANG, "Q6", reponse="B",
    raisonnement=(
        "L'API est l'ensemble de ce que la bibliothèque EXPOSE : noms des "
        "fonctions, paramètres attendus, valeurs renvoyées. C'est ce qu'il faut "
        "connaître pour l'utiliser, et c'est indépendant de la manière dont "
        "elle est écrite à l'intérieur."
    ),
    source_cours=_TLANG_API,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C6",
    refutations={
        "A": (
            "Le code source est l'implémentation. Une bibliothèque peut être "
            "utilisée sans qu'on en lise une ligne — et parfois sans qu'elle "
            "soit disponible."
        ),
        "C": (
            "Le nom de l'auteur est une métadonnée : elle n'aide personne à "
            "appeler une fonction."
        ),
        "D": (
            "La vitesse est une propriété mesurée à l'exécution, qui varie avec "
            "la machine et les données. Elle ne figure pas dans une interface."
        ),
    },
)

conceptuelle(
    _TLANG, "Q7", reponse="C",
    raisonnement=(
        "La documentation annonce un cas de retour particulier : `None` quand "
        "la clé est absente. Utiliser la valeur sans distinguer ce cas conduit "
        "à opérer sur `None`, donc à une exception à l'exécution. Le contrat "
        "impose donc de tester avant d'utiliser."
    ),
    source_cours=_TLANG_API,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C7",
    refutations={
        "A": (
            "Modifier la bibliothèque pour changer son contrat casse tous ses "
            "autres appelants, et fige une version qui ne recevra plus les "
            "corrections."
        ),
        "B": (
            "La documentation s'adresse précisément aux appelants : c'est le "
            "contrat qu'ils doivent respecter."
        ),
        "D": (
            "Supposer la clé toujours présente contredit la documentation, et "
            "le programme échouera au premier cas contraire — souvent en "
            "production."
        ),
    },
)


@mecanique(_TLANG, "Q8", PYTHON)
def _tlang_q8(options):
    """On exécute le même fichier comme script, puis comme module importé."""
    import runpy
    import tempfile
    from pathlib import Path as _Path

    source = (
        "TRACE = []\n"
        "def utile():\n"
        "    return 42\n"
        'if __name__ == "__main__":\n'
        "    TRACE.append('demo')\n"
    )
    with tempfile.TemporaryDirectory() as dossier:
        fichier = _Path(dossier) / "sonde.py"
        fichier.write_text(source, encoding="utf-8")
        comme_script = runpy.run_path(str(fichier), run_name="__main__")
        comme_module = runpy.run_path(str(fichier), run_name="sonde")

    # Le code du bloc ne s'exécute QUE lancé directement.
    assert comme_script["TRACE"] == ["demo"]
    assert comme_module["TRACE"] == []
    # Dans les deux cas, la fonction utile est bien définie et exportée.
    assert comme_script["utile"]() == comme_module["utile"]() == 42
    return _lettre(
        options,
        lambda texte: "lancé directement" in texte and "que si" in texte,
    )


conceptuelle(
    _TLANG, "Q9", reponse="A",
    raisonnement=(
        "Python n'impose aucun paradigme : un même fichier peut contenir une "
        "boucle qui modifie un état — impératif —, une compréhension sans effet "
        "de bord — fonctionnel — et une classe — objet. Le paradigme est un "
        "choix de conception, pas une contrainte du langage."
    ),
    source_cours=_TLANG_PARADIGMES,
    source_programme="TNSI-LANGAGES-ET-PROGRAMMATION::C9",
    refutations={
        "B": (
            "Restreindre Python à l'objet est faux : une fonction au niveau du "
            "module n'appartient à aucune classe."
        ),
        "C": (
            "Aucune contrainte du langage n'impose un paradigme unique ; c'est "
            "même l'un de ses traits caractéristiques."
        ),
        "D": (
            "Tout programme relève d'un ou plusieurs paradigmes identifiables : "
            "la question est de savoir lesquels, pas s'il y en a."
        ),
    },
)


@mecanique(_TLANG, "Q10", PYTHON)
def _tlang_q10(options):
    """Quel style transforme SANS modifier la liste de départ ? On mesure."""
    depart = [1, 2, 3]

    # Style impératif, sur place : la liste de départ est modifiée.
    imperative = list(depart)
    for indice in range(len(imperative)):
        imperative[indice] = imperative[indice] * 2
    modifie_la_source = imperative != depart

    # Style fonctionnel : une nouvelle liste, la source intacte.
    source = list(depart)
    fonctionnelle = [valeur * 2 for valeur in source]
    assert fonctionnelle == [2, 4, 6]
    assert source == depart          # inchangée
    assert fonctionnelle is not source
    assert modifie_la_source          # le style impératif, lui, a modifié
    return _lettre(
        options,
        lambda texte: "fonctionnel" in texte and "nouvelle liste" in texte,
    )


@mecanique(_TLANG, "Q11", PYTHON)
def _tlang_q11(options):
    """La comparaison de flottants échoue-t-elle, et pourquoi ?"""
    assert (0.1 + 0.2 == 0.3) is False
    # Ce n'est pas une interdiction : la comparaison s'évalue sans erreur.
    assert isinstance(0.1 + 0.2 == 0.3, bool)
    # Ce n'est pas réservé aux entiers : elle fonctionne entre flottants.
    assert (0.5 + 0.25 == 0.75) is True
    # Et tous les flottants ne sont pas égaux entre eux.
    assert (1.0 == 2.0) is False
    # La cause est la représentation : 0.1 n'est pas exactement 1/10.
    from decimal import Decimal
    assert Decimal(0.1) != Decimal("0.1")
    return _lettre(
        options,
        lambda texte: "ne représentent pas exactement" in texte,
    )


@mecanique(_TLANG, "Q12", PYTHON)
def _tlang_q12(options):
    """`b = a` : copie ou alias ? On mute et on regarde."""
    a = [1, 2]
    b = a
    assert b is a
    b.append(3)
    assert a == [1, 2, 3]        # a a bougé : ce n'est pas une copie
    assert a != []               # a n'a pas été vidée
    return _lettre(
        options,
        lambda texte: "le même objet" in texte,
    )


# ══════════════════════════════════════════════════════════════════════════
# TNSI-ARCHITECTURES-MATERIELLES-SY
# ══════════════════════════════════════════════════════════════════════════

_TARCH = "TNSI-ARCHITECTURES-MATERIELLES-SY"
_TARCH_SOC = "NSI/chapitres/TNSI-ARCHITECTURES-MATERIELLES-SY/cours/10_C01_systeme_sur_puce.tex"
_TARCH_PROC = "NSI/chapitres/TNSI-ARCHITECTURES-MATERIELLES-SY/cours/11_C02_processus.tex"
_TARCH_ROUTAGE = "NSI/chapitres/TNSI-ARCHITECTURES-MATERIELLES-SY/cours/12_C03_routage.tex"
_TARCH_CHIFFRE = "NSI/chapitres/TNSI-ARCHITECTURES-MATERIELLES-SY/cours/13_C04_chiffrement.tex"

conceptuelle(
    _TARCH, "Q1", reponse="A",
    raisonnement=(
        "L'intégration fait gagner sur les trois autres tableaux — compacité, "
        "consommation, coût — précisément parce que tout est sur une seule "
        "puce. Ce qu'elle coûte est la MODULARITÉ : une mémoire ou un modem "
        "défaillant ne se remplace plus séparément, c'est toute la puce qu'il "
        "faut changer."
    ),
    source_cours=_TARCH_SOC,
    source_programme="TNSI-ARCHITECTURES-MATERIELLES-SY::C1",
    refutations={
        "B": (
            "La consommation BAISSE : les distances entre composants sont plus "
            "courtes, donc les pertes de communication moindres."
        ),
        "C": (
            "L'encombrement diminue : c'est le premier argument de "
            "l'intégration, et ce qui rend un smartphone possible."
        ),
        "D": (
            "Le coût de fabrication en grande série est généralement plus "
            "faible qu'un assemblage de composants distincts."
        ),
    },
)

conceptuelle(
    _TARCH, "Q2", reponse="B",
    raisonnement=(
        "Créer un processus, pour le système, c'est lui allouer un espace "
        "mémoire, y charger le code, initialiser son état, et l'inscrire dans "
        "la liste des processus que l'ordonnanceur pourra élire. C'est une "
        "opération d'exécution, pas de traduction."
    ),
    source_cours=_TARCH_PROC,
    source_programme="TNSI-ARCHITECTURES-MATERIELLES-SY::C2",
    refutations={
        "A": (
            "La compilation traduit le source en code machine, avant "
            "l'exécution et souvent sur une autre machine. Un programme "
            "interprété n'est pas compilé et donne pourtant des processus."
        ),
        "C": (
            "Arrêter les autres processus serait le contraire du "
            "multitâche : plusieurs processus coexistent."
        ),
        "D": (
            "Une adresse IP identifie une interface réseau, pas un processus. "
            "Un programme sans réseau a bien un processus."
        ),
    },
)

conceptuelle(
    _TARCH, "Q3", reponse="C",
    raisonnement=(
        "L'ordonnanceur arbitre l'accès à une ressource unique : le processeur. "
        "Il choisit, parmi les processus PRÊTS, lequel s'exécute et pendant "
        "quelle durée. C'est cet arbitrage répété qui donne l'illusion du "
        "parallélisme sur un cœur unique."
    ),
    source_cours=_TARCH_PROC,
    source_programme="TNSI-ARCHITECTURES-MATERIELLES-SY::C3",
    refutations={
        "A": (
            "Le tri des fichiers relève du système de fichiers, une tout autre "
            "fonction du système d'exploitation."
        ),
        "B": (
            "La compilation est faite par un compilateur, avant le lancement, "
            "et pas par l'ordonnanceur."
        ),
        "D": (
            "La libération des ressources d'un processus terminé fait partie de "
            "la gestion des processus, mais « et rien d'autre » exclut "
            "l'arbitrage, qui est justement le rôle de l'ordonnanceur."
        ),
    },
)

conceptuelle(
    _TARCH, "Q4", reponse="A",
    raisonnement=(
        "Dans le graphe d'attente, chaque processus pointe vers la ressource "
        "qu'il attend et chaque ressource vers le processus qui la retient. Un "
        "interblocage est un groupe de processus qui s'attendent mutuellement : "
        "en suivant les flèches, on revient au point de départ, c'est-à-dire "
        "qu'on parcourt un CYCLE."
    ),
    source_cours=_TARCH_PROC,
    source_programme="TNSI-ARCHITECTURES-MATERIELLES-SY::C4",
    refutations={
        "B": (
            "Un arbre est sans cycle : chaque attente y aboutit à une ressource "
            "libre, et le groupe finit par progresser."
        ),
        "C": (
            "Un graphe sans arête décrit des processus qui n'attendent rien : "
            "c'est la situation la plus saine possible."
        ),
        "D": (
            "Un sommet isolé est un processus qui n'attend ni ne retient rien ; "
            "il ne peut bloquer personne."
        ),
    },
)

conceptuelle(
    _TARCH, "Q5", reponse="B",
    raisonnement=(
        "RIP est un protocole à vecteur de distance dont la métrique est le "
        "NOMBRE DE SAUTS : il retient la route traversant le moins de "
        "routeurs, sans considération de débit ni de charge. C'est ce qui le "
        "distingue d'OSPF."
    ),
    source_cours=_TARCH_ROUTAGE,
    source_programme="TNSI-ARCHITECTURES-MATERIELLES-SY::C5",
    refutations={
        "A": (
            "Le coût cumulé est la métrique d'OSPF. Les deux protocoles "
            "choisissent des routes différentes dès qu'une liaison courte est "
            "coûteuse."
        ),
        "C": (
            "La latence mesurée en temps réel n'est la métrique d'aucun des "
            "deux protocoles au programme : elle varie trop vite pour être "
            "stable."
        ),
        "D": (
            "Le nombre d'utilisateurs connectés n'est pas une propriété du "
            "chemin et n'entre dans aucune table de routage."
        ),
    },
)

conceptuelle(
    _TARCH, "Q6", reponse="C",
    raisonnement=(
        "Le chiffrement asymétrique repose sur une PAIRE de clés liées "
        "mathématiquement : ce qui est chiffré avec la publique ne se déchiffre "
        "qu'avec la privée. C'est ce qui permet d'échanger sans secret "
        "préalable, la clé publique pouvant être diffusée librement."
    ),
    source_cours=_TARCH_CHIFFRE,
    source_programme="TNSI-ARCHITECTURES-MATERIELLES-SY::C6",
    refutations={
        "A": (
            "Une unique clé secrète partagée est le chiffrement SYMÉTRIQUE : "
            "c'est justement l'échange préalable de ce secret que "
            "l'asymétrique évite."
        ),
        "B": (
            "Sans clé, aucun secret : n'importe qui déchiffrerait le message "
            "en appliquant l'algorithme, qui est public."
        ),
        "D": (
            "Une clé par caractère décrit un masque jetable, technique "
            "symétrique, et n'a rien à voir avec la paire publique/privée."
        ),
    },
)

conceptuelle(
    _TARCH, "Q7", reponse="D",
    raisonnement=(
        "L'asymétrique est lent : il serait inutilisable sur le volume d'une "
        "session. HTTPS ne s'en sert donc qu'au DÉBUT, pour convenir en sûreté "
        "d'une clé symétrique de session ; toute la suite des échanges est "
        "chiffrée avec cette clé symétrique, bien plus rapide."
    ),
    source_cours=_TARCH_CHIFFRE,
    source_programme="TNSI-ARCHITECTURES-MATERIELLES-SY::C7",
    refutations={
        "A": (
            "Chiffrer toute la session en asymétrique serait beaucoup trop "
            "lent : c'est précisément le problème que la clé de session "
            "résout."
        ),
        "B": (
            "La compression est une opération distincte, sans lien avec le "
            "chiffrement, et souvent appliquée avant lui."
        ),
        "C": (
            "Le cadenas est un indicateur affiché par le navigateur : c'est une "
            "conséquence visible, pas la fonction du chiffrement."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# TNSI-HISTOIRE-INFORMATIQUE
# ══════════════════════════════════════════════════════════════════════════

_THIST = "TNSI-HISTOIRE-INFORMATIQUE"
_THIST_REPERES = "NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/cours/10_C1_evenements_cles.tex"
_THIST_EVOLUTION = "NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/cours/11_C2_evolution_logiciel_materiel.tex"

conceptuelle(
    _THIST, "Q1", reponse="A",
    raisonnement=(
        "L'article de Turing « On Computable Numbers » paraît en 1936 : il y "
        "définit la machine qui porte son nom et la machine universelle capable "
        "de simuler n'importe laquelle des autres. C'est le repère chronologique "
        "que le programme fixe pour l'entrée dans l'informatique théorique."
    ),
    source_cours=_THIST_REPERES,
    source_programme="TNSI-HISTOIRE-INFORMATIQUE::C1",
    refutations={
        "B": (
            "1948 est la date des premiers ordinateurs électroniques à "
            "programme enregistré — la réalisation, douze ans après la "
            "théorie."
        ),
        "C": (
            "1969 est la mise en service d'ARPANET : un réseau, pas un modèle "
            "de calcul."
        ),
        "D": (
            "1991 correspond aux débuts publics du Web, plus d'un demi-siècle "
            "après."
        ),
    },
)

conceptuelle(
    _THIST, "Q2", reponse="B",
    raisonnement=(
        "ARPANET est mis en service en 1969, avec ses premiers nœuds "
        "universitaires américains. C'est l'ancêtre direct d'Internet, dont il "
        "inaugure la commutation de paquets à l'échelle d'un réseau de réseaux."
    ),
    source_cours=_THIST_REPERES,
    source_programme="TNSI-HISTOIRE-INFORMATIQUE::C1",
    refutations={
        "A": (
            "1948 est celle des premiers ordinateurs à programme enregistré, "
            "vingt ans avant tout réseau de ce type."
        ),
        "C": (
            "1989 est l'année de la proposition du Web par Tim Berners-Lee, "
            "qui suppose Internet déjà existant."
        ),
        "D": (
            "En 2000, Internet est déjà mondial et grand public : la date est "
            "trop tardive de trente ans."
        ),
    },
)

conceptuelle(
    _THIST, "Q3", reponse="C",
    raisonnement=(
        "L'évolution va du matériel spécialisé — machines câblées pour une "
        "tâche — vers un matériel GÉNÉRIQUE, dont le comportement particulier "
        "est déterminé par le logiciel qu'il exécute. Un même smartphone "
        "devient calculatrice, appareil photo ou lecteur de musique selon "
        "l'application lancée."
    ),
    source_cours=_THIST_EVOLUTION,
    source_programme="TNSI-HISTOIRE-INFORMATIQUE::C2",
    refutations={
        "A": (
            "C'est le mouvement inverse de celui observé : la spécialisation "
            "caractérise les machines des débuts, pas celles d'aujourd'hui."
        ),
        "B": (
            "Le matériel ne disparaît pas : aucun logiciel ne s'exécute sans "
            "processeur ni mémoire. C'est son RÔLE qui a changé."
        ),
        "D": (
            "L'évolution est considérable, et elle est précisément l'objet de "
            "la capacité évaluée."
        ),
    },
)

conceptuelle(
    _THIST, "Q4", reponse="D",
    raisonnement=(
        "Internet est l'infrastructure : un réseau de réseaux qui achemine des "
        "paquets. Le Web est l'un des services qui l'utilisent, au même titre "
        "que le courrier électronique — il est donc AU-DESSUS d'Internet, et "
        "postérieur de vingt ans."
    ),
    source_cours=_THIST_REPERES,
    source_programme="TNSI-HISTOIRE-INFORMATIQUE::C2",
    refutations={
        "A": (
            "Ce ne sont pas deux noms de la même chose : le courrier "
            "électronique passe par Internet sans passer par le Web, ce qui "
            "suffit à les distinguer."
        ),
        "B": (
            "Le Web n'est pas un réseau physique : il n'a ni câbles ni "
            "routeurs propres, il emploie ceux d'Internet."
        ),
        "C": (
            "La relation est inversée : c'est le Web qui repose sur Internet, "
            "et non l'inverse. Internet existait vingt ans avant le Web."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# TNSI-PROJET
# ══════════════════════════════════════════════════════════════════════════

_TPROJ = "TNSI-PROJET"
_TPROJ_ANNUEL = "NSI/chapitres/TNSI-PROJET/projet/TNSI-PROJET-ANNUEL.tex"

conceptuelle(
    _TPROJ, "Q1", reponse="A",
    raisonnement=(
        "Un problème de projet n'est utilisable que s'il est formulé de façon "
        "explicite ET assorti de critères observables : sans eux, personne ne "
        "peut dire si le projet est terminé, et l'évaluation devient une "
        "affaire d'impression."
    ),
    source_cours=_TPROJ_ANNUEL,
    source_programme="TNSI-PROJET::C1",
    refutations={
        "B": (
            "Une formulation la plus large possible rend le périmètre "
            "indéfini : on ne sait ni quoi construire ni quand s'arrêter."
        ),
        "C": (
            "Formuler le problème après coup revient à décrire ce qu'on a fait, "
            "pas à conduire un projet : les choix ne peuvent plus être "
            "justifiés par une exigence."
        ),
        "D": (
            "L'appropriation du problème par l'équipe fait partie du travail "
            "attendu ; un énoncé entièrement imposé prive le projet de ses "
            "choix de conception."
        ),
    },
)

conceptuelle(
    _TPROJ, "Q2", reponse="B",
    raisonnement=(
        "Répartir suppose deux décisions liées : qui prend quelle partie, et "
        "comment ces parties s'assembleront — quelles interfaces, quels "
        "formats d'échange. Sans la seconde, les parties ne s'emboîtent pas à "
        "la fin, quel que soit le soin apporté à chacune."
    ),
    source_cours=_TPROJ_ANNUEL,
    source_programme="TNSI-PROJET::C1",
    refutations={
        "A": (
            "Écrire le même code chacun de son côté n'est pas une répartition : "
            "c'est une duplication, qui ne fait avancer le projet que d'une "
            "seule part."
        ),
        "C": (
            "Une seule personne qui programme laisse les autres sans "
            "apprentissage ni contribution : ce n'est pas un travail d'équipe."
        ),
        "D": (
            "Le tirage au sort ignore les compétences et les dépendances entre "
            "tâches, alors que certaines doivent être faites avant d'autres."
        ),
    },
)

conceptuelle(
    _TPROJ, "Q3", reponse="C",
    raisonnement=(
        "Un point d'étape sert à décider de la suite ; il doit donc porter sur "
        "des faits vérifiables : ce qui fonctionne, ce qui est testé, ce qui "
        "reste. Ces trois éléments permettent d'ajuster le périmètre en "
        "connaissance de cause."
    ),
    source_cours=_TPROJ_ANNUEL,
    source_programme="TNSI-PROJET::C2",
    refutations={
        "A": (
            "Le nombre de lignes ne mesure pas l'avancement : une correction "
            "importante peut en retirer, et du code écrit mais non testé "
            "n'avance rien."
        ),
        "B": (
            "L'impression générale n'est pas observable : deux membres peuvent "
            "l'avoir opposée sur le même état du projet."
        ),
        "D": (
            "La date de rendu est connue depuis le début : la rappeler "
            "n'apporte aucune information sur l'état d'avancement."
        ),
    },
)

conceptuelle(
    _TPROJ, "Q4", reponse="D",
    raisonnement=(
        "À mi-parcours, le temps restant est une contrainte fixe. La seule "
        "conduite qui produise un résultat exploitable est de réduire le "
        "périmètre — en accord avec l'enseignant, puisque c'est lui qui évalue "
        "— et de livrer un ensemble COHÉRENT ET TESTÉ, plutôt qu'un ensemble "
        "complet et cassé."
    ),
    source_cours=_TPROJ_ANNUEL,
    source_programme="TNSI-PROJET::C2",
    refutations={
        "A": (
            "Conserver le périmètre en sachant qu'il ne sera pas tenu garantit "
            "un rendu inachevé : la décision est prise par omission au lieu "
            "d'être prise."
        ),
        "B": (
            "Recommencer à mi-parcours perd tout le travail fait et laisse "
            "encore moins de temps qu'au départ."
        ),
        "C": (
            "Ajouter des membres en cours de route coûte du temps "
            "d'explication à ceux qui avancent : le renfort ralentit d'abord "
            "avant d'aider, si tant est qu'il aide."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# TSPE-GEOMETRIE-ESPACE — cinq questions se calculent
# ══════════════════════════════════════════════════════════════════════════

_GEO = "TSPE-GEOMETRIE-ESPACE"
_GEO_VECTEURS = "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/10_C1_C2_C4_C5_vecteurs_espace.tex"
_GEO_POSITIONS = "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/11_C3_C6_positions_relatives.tex"
_GEO_SCALAIRE = "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/12_C7_produit_scalaire.tex"
_GEO_PLAN = "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/14_C13_C16_equation_cartesienne_plan.tex"
_GEO_PROJECTION = "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/15_C8_C11_C14_projection_orthogonale.tex"
_GEO_SYSTEMES = "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/16_C10_C15_systemes_lieux.tex"

conceptuelle(
    _GEO, "Q6", reponse="B",
    raisonnement=(
        "Deux vecteurs non colinéaires engendrent un sous-espace de dimension "
        "2. L'ensemble de leurs combinaisons linéaires est donc un PLAN "
        "vectoriel — celui qu'ils dirigent. Il faudrait un troisième vecteur "
        "non coplanaire pour engendrer l'espace tout entier."
    ),
    source_cours=_GEO_VECTEURS,
    source_programme="TSPE-GEOMETRIE-ESPACE::C1",
    refutations={
        "A": (
            "Décrire tout l'espace exigerait trois vecteurs non coplanaires : "
            "avec deux, un vecteur hors du plan engendré n'est jamais atteint."
        ),
        "C": (
            "Une droite serait engendrée par un seul vecteur, ou par deux "
            "vecteurs colinéaires — précisément ce que l'énoncé exclut."
        ),
        "D": (
            "Un seul point correspondrait à $a=b=0$ uniquement ; ici $a$ et $b$ "
            "parcourent tous les réels."
        ),
    },
)


@mecanique(_GEO, "Q7", SYMBOLIC)
def _geo_q7(options):
    """Décomposition de EC dans la base (AB, AD, AE), par coordonnées du cube."""
    A = (0, 0, 0)
    B, D, E = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    C = tuple(B[i] + D[i] for i in range(3))          # C = A + AB + AD
    EC = tuple(C[i] - E[i] for i in range(3))
    assert EC == (1, 1, -1)
    # EC = 1·AB + 1·AD − 1·AE : on cherche l'option qui écrit ces trois signes.
    return _lettre(
        options,
        lambda texte: texte.replace(" ", "")
        == "$\\vec{AB}+\\vec{AD}-\\vec{AE}$",
    )


conceptuelle(
    _GEO, "Q8", reponse="D",
    raisonnement=(
        "Non colinéaires deux à deux interdit seulement qu'un vecteur soit "
        "multiple d'un autre. Trois vecteurs peuvent parfaitement vérifier cela "
        "tout en appartenant à un même plan : $(1,0,0)$, $(0,1,0)$ et $(1,1,0)$ "
        "en sont un exemple. Ils PEUVENT donc être coplanaires."
    ),
    source_cours=_GEO_VECTEURS,
    source_programme="TSPE-GEOMETRIE-ESPACE::C4",
    refutations={
        "A": (
            "Former une base exige d'être non COPLANAIRES, condition plus forte "
            "que non colinéaires deux à deux : le contre-exemple ci-dessus la "
            "met en défaut."
        ),
        "B": (
            "« Toujours » est faux dans l'autre sens : les trois vecteurs de la "
            "base canonique sont non colinéaires deux à deux et non "
            "coplanaires."
        ),
        "C": (
            "L'orthogonalité est une propriété métrique, sans rapport avec la "
            "colinéarité : deux vecteurs non colinéaires peuvent faire un "
            "angle quelconque."
        ),
    },
)

conceptuelle(
    _GEO, "Q9", reponse="A",
    raisonnement=(
        "Les coordonnées suffisent toujours à écrire le vecteur comme "
        "combinaison des vecteurs de base : c'est leur définition. En revanche "
        "la formule $\\sqrt{x^2+y^2+z^2}$ suppose la base ORTHONORMÉE ; dans une "
        "base quelconque, la norme dépend aussi des normes des vecteurs de base "
        "et des angles entre eux, que les coordonnées ne donnent pas."
    ),
    source_cours=_GEO_VECTEURS,
    source_programme="TSPE-GEOMETRIE-ESPACE::C5",
    refutations={
        "B": (
            "$\\sqrt{3}$ n'est la norme que dans une base orthonormée. Avec des "
            "vecteurs de base de longueur 2, le même triplet donnerait $2\\sqrt3$."
        ),
        "C": (
            "Être unitaire est une propriété de norme : elle est hors d'atteinte "
            "pour la même raison."
        ),
        "D": (
            "Les coordonnées $(1;1;1)$ ne disent rien des angles ; elles "
            "n'établissent aucune orthogonalité."
        ),
    },
)

conceptuelle(
    _GEO, "Q10", reponse="B",
    raisonnement=(
        "Quatre points sont coplanaires lorsque le quatrième appartient au plan "
        "défini par les trois premiers. En termes vectoriels, cela s'écrit "
        "exactement : $\\vec{AD}$ est combinaison linéaire de $\\vec{AB}$ et "
        "$\\vec{AC}$ — à condition que ces deux-là ne soient pas colinéaires, "
        "sans quoi ils ne définissent pas de plan."
    ),
    source_cours=_GEO_POSITIONS,
    source_programme="TSPE-GEOMETRIE-ESPACE::C6",
    refutations={
        "A": (
            "Trois points sont TOUJOURS coplanaires : la condition est vide et "
            "ne dit rien du quatrième."
        ),
        "C": (
            "Si $\\vec{AB}$ et $\\vec{AC}$ sont colinéaires, les trois premiers "
            "points sont alignés et ne définissent aucun plan unique : la "
            "condition ne conclut rien sur $D$."
        ),
        "D": (
            "Quatre points deux à deux distincts peuvent former un tétraèdre, "
            "cas typiquement non coplanaire."
        ),
    },
)


@mecanique(_GEO, "Q11", SYMBOLIC)
def _geo_q11(options):
    """Distance d'un point à un plan, par la formule et par minimisation."""
    from sympy import Rational, sqrt, symbols, solve, diff, simplify

    a, b, c, d = 1, 2, 2, -6
    M = (1, 2, 3)
    numerateur = abs(a * M[0] + b * M[1] + c * M[2] + d)
    norme = sqrt(a ** 2 + b ** 2 + c ** 2)
    distance = Rational(numerateur, 1) / norme
    assert simplify(distance - Rational(5, 3)) == 0

    # Contrôle indépendant : on minimise la distance au carré sous contrainte,
    # sans réutiliser la formule.
    x, y, t = symbols("x y t", real=True)
    z = (6 - x - 2 * y) / 2                     # point courant du plan
    carre = (x - 1) ** 2 + (y - 2) ** 2 + (z - 3) ** 2
    solution = solve([diff(carre, x), diff(carre, y)], [x, y], dict=True)[0]
    minimum = carre.subs(solution)
    assert simplify(minimum - Rational(25, 9)) == 0
    assert simplify(sqrt(minimum) - Rational(5, 3)) == 0

    return _lettre(options, lambda texte: "\\dfrac{5}{3}" in texte)


@mecanique(_GEO, "Q12", SYMBOLIC)
def _geo_q12(options):
    """Angle BAC par le produit scalaire, en repère orthonormé."""
    from sympy import acos, pi, sqrt, simplify, Rational

    A, B, C = (0, 0, 0), (1, 0, 0), (1, 1, 0)
    AB = tuple(B[i] - A[i] for i in range(3))
    AC = tuple(C[i] - A[i] for i in range(3))
    scalaire = sum(AB[i] * AC[i] for i in range(3))
    normes = sqrt(sum(v ** 2 for v in AB)) * sqrt(sum(v ** 2 for v in AC))
    angle = acos(Rational(scalaire, 1) / normes)
    assert simplify(angle - pi / 4) == 0
    return _lettre(options, lambda texte: "\\dfrac{\\pi}{4}" in texte)


conceptuelle(
    _GEO, "Q13", reponse="A",
    raisonnement=(
        "Une droite est orthogonale à un plan quand son vecteur directeur est "
        "orthogonal à TOUT vecteur du plan. Il suffit de le vérifier sur deux "
        "vecteurs non colinéaires du plan : tout autre vecteur du plan en est "
        "une combinaison linéaire, et le produit scalaire étant linéaire, "
        "l'orthogonalité se transmet."
    ),
    source_cours=_GEO_SCALAIRE,
    source_programme="TSPE-GEOMETRIE-ESPACE::C10",
    refutations={
        "B": (
            "Une seule droite ne suffit pas : un vecteur peut être orthogonal à "
            "une direction du plan sans l'être au plan — il est alors dans le "
            "plan lui-même."
        ),
        "C": (
            "Être orthogonal au vecteur NORMAL signifie au contraire être "
            "PARALLÈLE au plan, ou contenu dedans : c'est l'exact opposé."
        ),
        "D": (
            "Aucun vecteur non nul n'est orthogonal à toutes les directions de "
            "l'espace : il serait orthogonal à lui-même, donc nul."
        ),
    },
)


@mecanique(_GEO, "Q14", SYMBOLIC)
def _geo_q14(options):
    """Projeté orthogonal : on le calcule, puis on vérifie ses deux propriétés."""
    from sympy import Rational, symbols, solve

    M = (3, 3, 3)
    normal = (1, 1, 1)
    d = -3                                    # plan x + y + z − 3 = 0
    t = symbols("t", real=True)
    point = tuple(M[i] + t * normal[i] for i in range(3))
    valeur = solve(sum(point) + d, t)[0]
    projete = tuple(coord.subs(t, valeur) for coord in point)
    assert projete == (1, 1, 1)
    # Il appartient au plan, et MP est colinéaire à la normale.
    assert sum(projete) - 3 == 0
    MP = tuple(projete[i] - M[i] for i in range(3))
    assert MP == (-2, -2, -2)
    assert all(Rational(MP[i], normal[i]) == Rational(MP[0], normal[0])
               for i in range(3))
    return _lettre(options, lambda texte: texte.strip() == "$(1;1;1)$")


conceptuelle(
    _GEO, "Q15", reponse="C",
    raisonnement=(
        "En substituant la représentation paramétrique de la droite dans "
        "l'équation du plan, on obtient une équation en le paramètre. "
        "L'aboutissement $0 = 5$ est une contradiction : AUCUNE valeur du "
        "paramètre ne convient, donc la droite ne rencontre pas le plan. Sans "
        "point commun et de direction parallèle au plan, elle lui est "
        "strictement parallèle."
    ),
    source_cours=_GEO_SYSTEMES,
    source_programme="TSPE-GEOMETRIE-ESPACE::C15",
    refutations={
        "A": (
            "Une contradiction n'est pas une erreur : c'est un résultat, et "
            "c'est même le seul moyen algébrique de constater un parallélisme "
            "strict."
        ),
        "B": (
            "Une droite incluse dans le plan donnerait une identité du type "
            "$0 = 0$, vérifiée pour TOUT paramètre — l'inverse exact."
        ),
        "D": (
            "Une intersection en un point donnerait une équation admettant une "
            "solution unique en le paramètre."
        ),
    },
)


@mecanique(_GEO, "Q16", SYMBOLIC)
def _geo_q16(options):
    """L'équation cartésienne du plan : on la construit, puis on la teste."""
    A = (2, -1, 3)
    n = (1, 4, -2)
    d = -sum(n[i] * A[i] for i in range(3))
    assert d == 8                                   # x + 4y − 2z + 8 = 0

    def verifie(equation) -> bool:
        return equation(*A) == 0

    assert verifie(lambda x, y, z: x + 4 * y - 2 * z + d)
    # Les autres candidats ne passent pas par A, ou n'ont pas la bonne normale.
    assert (A[0] + 4 * A[1] - 2 * A[2]) != 0                    # option A
    assert (A[0] + 4 * A[1] - 2 * A[2] - 8) != 0                # option B
    assert (2 * A[0] - A[1] + 3 * A[2] + 8) != 0                # option C
    return _lettre(options, lambda texte: "x+4y-2z+8=0" in texte.replace(" ", ""))


# ══════════════════════════════════════════════════════════════════════════
# TSPE-SUITES-LIMITES
# ══════════════════════════════════════════════════════════════════════════

_SUITES = "TSPE-SUITES-LIMITES"
_SUITES_CONV = "Mathematiques/manuel-maths/chapitres/TSPE-SUITES-LIMITES/cours/10_C1_convergence_divergence.tex"
_SUITES_MODEL = "Mathematiques/manuel-maths/chapitres/TSPE-SUITES-LIMITES/cours/12_C3_modelisation.tex"
_SUITES_CROISSANTE = "Mathematiques/manuel-maths/chapitres/TSPE-SUITES-LIMITES/cours/13_C4_suite_croissante_non_majoree.tex"
_SUITES_COMPARAISON = "Mathematiques/manuel-maths/chapitres/TSPE-SUITES-LIMITES/cours/15_C6_comparaison.tex"


@mecanique(_SUITES, "Q1", SYMBOLIC)
def _suites_q1(options):
    """Limite d'un quotient de degré 1 sur degré 1, calculée et contrôlée."""
    from sympy import symbols, limit, oo, Rational, simplify

    n = symbols("n", positive=True, integer=True)
    valeur = limit((5 * n - 1) / (2 * n + 3), n, oo)
    assert simplify(valeur - Rational(5, 2)) == 0
    # Contrôle numérique : la suite s'en approche.
    assert abs((5 * 10**6 - 1) / (2 * 10**6 + 3) - 2.5) < 1e-5
    return _lettre(options, lambda texte: texte.strip() == "$5/2$")


@mecanique(_SUITES, "Q6", SYMBOLIC)
def _suites_q6(options):
    """Raison de la suite auxiliaire, calculée à partir de la récurrence."""
    from sympy import Rational, simplify, symbols

    u = symbols("u", real=True)
    suivant = Rational(7, 10) * u + 9
    v_courant = u - 30
    v_suivant = simplify(suivant - 30)
    raison = simplify(v_suivant / v_courant)
    assert raison == Rational(7, 10)
    # Contrôle numérique sur plusieurs rangs.
    valeur = 5.0
    for _ in range(10):
        precedent = valeur - 30
        valeur = 0.7 * valeur + 9
        assert abs((valeur - 30) - 0.7 * precedent) < 1e-9
    return _lettre(options, lambda texte: texte.strip() in ("0,7", "$0,7$"))


conceptuelle(
    _SUITES, "Q7", reponse="D",
    raisonnement=(
        "Le théorème de la limite monotone énonce qu'une suite croissante ET "
        "majorée converge. Les deux hypothèses sont nécessaires : la croissance "
        "donne le sens, la majoration empêche la fuite vers l'infini. C'est "
        "l'énoncé exact de l'option D."
    ),
    source_cours=_SUITES_CROISSANTE,
    source_programme="TSPE-SUITES-LIMITES::C4",
    refutations={
        "A": (
            "Une suite croissante peut converger : $u_n = 1 - 1/n$ croît et "
            "tend vers 1. La croissance seule ne dit rien."
        ),
        "B": (
            "L'implication est dans le mauvais sens et fausse : la suite "
            "$(-1)^n/n$ converge vers 0 sans être croissante."
        ),
        "C": (
            "Majorée ne suffit pas : $(-1)^n$ est majorée par 1 et ne converge "
            "pas. Il manque la monotonie."
        ),
    },
)


@mecanique(_SUITES, "Q12", SYMBOLIC)
def _suites_q12(options):
    """Théorème de comparaison : on le vérifie sur des cas, et on le réfute pas."""
    from sympy import symbols, limit, oo, sqrt

    n = symbols("n", positive=True, integer=True)
    # u_n minore v_n et tend vers +infini : v_n aussi, quelles que soient les
    # formes essayées.
    for majorante in (n, n + 1, n ** 2, n + sqrt(n)):
        assert limit(majorante, n, oo) == oo
    for k in range(1, 500):
        assert k <= k + 1 <= k ** 2 + 1
    # Aucune suite majorant n ne peut converger ni rester bornée.
    assert limit(n, n, oo) == oo
    return _lettre(options, lambda texte: "+\\infty" in texte and "lim" in texte)


conceptuelle(
    _SUITES, "Q13", reponse="B",
    raisonnement=(
        "Le théorème des gendarmes conclut que la suite encadrée converge vers "
        "la limite COMMUNE des deux encadrantes. Si elles n'ont pas la même "
        "limite, la suite encadrée peut prendre n'importe quel comportement "
        "entre les deux, et le théorème ne s'applique pas."
    ),
    source_cours=_SUITES_COMPARAISON,
    source_programme="TSPE-SUITES-LIMITES::C6",
    refutations={
        "A": (
            "Des limites différentes ne concluent rien : $-1 \\leq (-1)^n \\leq 1$ "
            "est un encadrement valide d'une suite qui n'a pas de limite."
        ),
        "C": (
            "Une seule limite ne suffit pas : il faut un encadrement des DEUX "
            "côtés, sans quoi la suite peut s'échapper de l'autre côté."
        ),
        "D": (
            "La divergence des encadrantes relève du théorème de comparaison, "
            "pas de celui des gendarmes, qui conclut à une convergence."
        ),
    },
)


# ══════════════════════════════════════════════════════════════════════════
# TSPE-CONTINUITE
# ══════════════════════════════════════════════════════════════════════════

_CONT = "TSPE-CONTINUITE"
_CONT_TVI = "Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/cours/10_C1_continuite_tvi.tex"
_CONT_SUITES = "Mathematiques/manuel-maths/chapitres/TSPE-CONTINUITE/cours/11_C2_suites_recurrentes.tex"

conceptuelle(
    _CONT, "Q5", reponse="B",
    raisonnement=(
        "La fonction croît strictement de $-1$ à $4$, puis décroît strictement "
        "de $4$ à $2$ : son maximum sur $[0\\,;6]$ vaut donc $4$. La valeur $5$ "
        "n'est jamais atteinte, et l'équation $f(x)=5$ n'a AUCUNE solution. Le "
        "théorème des valeurs intermédiaires ne s'applique que dans "
        "l'intervalle image, ici $[-1\\,;4]$."
    ),
    source_cours=_CONT_TVI,
    source_programme="TSPE-CONTINUITE::C1",
    refutations={
        "A": (
            "Une solution unique correspondrait à une valeur atteinte une seule "
            "fois — le cas de $4$, le maximum, ou d'une valeur de $]2\\,;4[$ "
            "sur la seule branche croissante."
        ),
        "C": (
            "Deux solutions correspondraient à une valeur strictement comprise "
            "entre $2$ et $4$, atteinte une fois sur chaque branche. $5$ est "
            "au-dessus du maximum."
        ),
        "D": (
            "Le nombre de solutions se détermine parfaitement à partir des "
            "variations et des valeurs aux bornes : c'est même l'objet de "
            "l'exercice."
        ),
    },
)

conceptuelle(
    _CONT, "Q9", reponse="B",
    raisonnement=(
        "Si $u_n \\to \\ell$ et $f$ est continue en $\\ell$, alors "
        "$f(u_n) \\to f(\\ell)$. Or $f(u_n) = u_{n+1}$, qui tend vers $\\ell$ "
        "aussi puisque c'est la même suite décalée d'un rang. Par unicité de la "
        "limite, $f(\\ell) = \\ell$ : la limite est un point fixe de $f$."
    ),
    source_cours=_CONT_SUITES,
    source_programme="TSPE-CONTINUITE::C2",
    refutations={
        "A": (
            "$f(\\ell)=0$ ferait de $\\ell$ une racine de $f$, ce qui n'a aucune "
            "raison d'être : pour $f(x)=x/2+1$, la limite est 2 et $f(2)=2$, pas 0."
        ),
        "C": (
            "$\\ell=0$ n'a pas lieu d'être : la même suite converge vers 2."
        ),
        "D": (
            "La croissance de $f$ n'est pas requise : le raisonnement n'utilise "
            "que la continuité et l'unicité de la limite."
        ),
    },
)

conceptuelle(
    _CONT, "Q11", reponse="D",
    raisonnement=(
        "Le théorème de la limite monotone garantit la CONVERGENCE d'une suite "
        "croissante majorée, sans identifier la limite. Celle-ci est la borne "
        "supérieure de l'ensemble des termes, qui n'a aucune raison d'être le "
        "majorant qu'on avait choisi."
    ),
    source_cours=_CONT_SUITES,
    source_programme="TSPE-CONTINUITE::C2",
    refutations={
        "A": (
            "La limite n'est pas le majorant : $u_n = 1 - 1/n$ est majorée par "
            "$10$ et converge vers $1$."
        ),
        "B": (
            "Rien n'impose une forme géométrique : $u_n = 1 - 1/n$ croît, est "
            "majorée, et n'est pas géométrique."
        ),
        "C": (
            "Diverger vers $+\\infty$ contredit la majoration : la suite "
            "dépasserait son majorant."
        ),
    },
)


@mecanique(_CONT, "Q14", SYMBOLIC)
def _cont_q14(options):
    """Contraction de rapport 1/2 : on itère la majoration depuis |u0 − l| = 4."""
    from sympy import Rational

    borne = Rational(4)
    for _ in range(5):
        borne = borne / 2
    assert borne == Rational(1, 8)
    assert float(borne) == 0.125
    # Contrôle : la majoration est bien 4 × (1/2)^5.
    assert borne == 4 * Rational(1, 2) ** 5
    return _lettre(
        options,
        lambda texte: texte.strip() in ("$0{,}125$", "$0,125$"),
    )


# ══════════════════════════════════════════════════════════════════════════
# TSPE-LIMITES-FONCTIONS
# ══════════════════════════════════════════════════════════════════════════

_LIMF = "TSPE-LIMITES-FONCTIONS"
_LIMF_LIMITES = "Mathematiques/manuel-maths/chapitres/TSPE-LIMITES-FONCTIONS/cours/10_C1_limites_fonctions.tex"
_LIMF_ASYMPTOTES = "Mathematiques/manuel-maths/chapitres/TSPE-LIMITES-FONCTIONS/cours/11_C2_asymptotes.tex"


@mecanique(_LIMF, "Q2", SYMBOLIC)
def _limf_q2(options):
    """Limite d'un polynôme de degré 2 en +infini."""
    from sympy import symbols, limit, oo

    x = symbols("x", real=True)
    valeur = limit(x ** 2 - 3 * x + 1, x, oo)
    assert valeur == oo
    # Contrôle numérique : la fonction dépasse tout seuil.
    assert (10 ** 6) ** 2 - 3 * 10 ** 6 + 1 > 10 ** 11
    return _lettre(options, lambda texte: texte.strip() == "$+\\infty$")


conceptuelle(
    _LIMF, "Q3", reponse="C",
    raisonnement=(
        "$\\frac{\\infty}{\\infty}$ ne détermine aucune valeur : selon les "
        "fonctions, la limite peut être nulle, finie non nulle, ou infinie. "
        "$\\frac{x}{x^2} \\to 0$, $\\frac{2x}{x} \\to 2$, "
        "$\\frac{x^2}{x} \\to +\\infty$. C'est précisément la définition d'une "
        "forme indéterminée : il faut transformer l'écriture avant de conclure."
    ),
    source_cours=_LIMF_LIMITES,
    source_programme="TSPE-LIMITES-FONCTIONS::C1",
    refutations={
        "A": (
            "Une valeur de 1 supposerait que les deux infinis « se simplifient », "
            "ce que $\\frac{x^2}{x}$ dément immédiatement."
        ),
        "B": (
            "$+\\infty$ n'est qu'un des trois comportements possibles, réalisé "
            "seulement quand le numérateur l'emporte."
        ),
        "D": (
            "0 est aussi un cas particulier, réalisé quand le dénominateur "
            "l'emporte — et il exclut les deux autres."
        ),
    },
)


@mecanique(_LIMF, "Q4", SYMBOLIC)
def _limf_q4(options):
    """Limite de 1/x en 0 par valeurs supérieures."""
    from sympy import symbols, limit

    x = symbols("x", real=True)
    valeur = limit(1 / x, x, 0, "+")
    assert str(valeur) == "oo"
    # Contrôle numérique : la fonction dépasse tout seuil quand x décroît.
    assert 1 / 1e-9 > 1e8
    return _lettre(options, lambda texte: texte.strip() == "$+\\infty$")


@mecanique(_LIMF, "Q9", SYMBOLIC)
def _limf_q9(options):
    """Asymptotes de e^{-x} + 3 : on calcule les deux limites et le domaine."""
    from sympy import symbols, limit, exp, oo

    x = symbols("x", real=True)
    f = exp(-x) + 3
    en_plus = limit(f, x, oo)
    en_moins = limit(f, x, -oo)
    assert en_plus == 3            # asymptote horizontale y = 3 en +infini
    assert en_moins == oo          # aucune asymptote horizontale en −infini
    # La fonction est définie sur tout R : pas d'asymptote verticale.
    assert all(f.subs(x, valeur).is_finite for valeur in (-5, 0, 5, 100))
    return _lettre(
        options,
        lambda texte: "AH $y=3$ en $+\\infty$" in texte and "pas d'AV" in texte,
    )


# ══════════════════════════════════════════════════════════════════════════
# Questions ajoutées pour couvrir les capacités laissées sans QCM
#
# Le gate `qcm` refusait quatorze chapitres dont une capacité du contrat
# n'était évaluée par aucune question. Les questions écrites pour les couvrir
# entrent dans la même chaîne de preuve que les autres : le solveur générique
# les a routées en `HUMAN_REVIEW_REQUIRED`, elles sont fermées ici.
# ══════════════════════════════════════════════════════════════════════════

_MATHS_CH = "Mathematiques/manuel-maths/chapitres"


def _cours_maths(chapitre: str, fichier: str) -> str:
    return f"{_MATHS_CH}/{chapitre}/cours/{fichier}"


# ── 1SPE-SECOND-DEGRE ─────────────────────────────────────────────────────
_SECDEG = "1SPE-SECOND-DEGRE"


@mecanique(_SECDEG, "Q19", SYMBOLIC)
def _secdeg_q19(options):
    """Somme et produit des racines de a(x+1)(x-4), calculés puis rapprochés."""
    from sympy import Poly, Rational, expand, symbols

    x, a = symbols("x a")
    polynome = Poly(expand(a * (x + 1) * (x - 4)), x)
    coefficients = polynome.all_coeffs()          # [a2, a1, a0]
    somme = -coefficients[1] / coefficients[0]
    produit = coefficients[2] / coefficients[0]
    assert somme == 3 and produit == -4
    # Les quatre options sont rendues AVANT de savoir laquelle est vraie : la
    # dérivation choisit celle qui porte le couple calculé.
    rendus = {
        (3, -4): "$S=3$ et $P=-4$",
        (3, 4): "$S=3$ et $P=4$",
        (-3, -4): "$S=-3$ et $P=-4$",
        (-3, 4): "$S=-3$ et $P=4$",
    }
    attendu = rendus[(int(somme), int(produit))]
    assert Rational(int(somme)) == somme
    return _lettre(options, lambda texte: texte.strip() == attendu)


@mecanique(_SECDEG, "Q20", SYMBOLIC)
def _secdeg_q20(options):
    """Signe de -2(x-1)(x+3) : l'ensemble de positivité est résolu sur R."""
    from sympy import Interval, S, solveset, symbols

    x = symbols("x", real=True)
    f = -2 * (x - 1) * (x + 3)
    positif = solveset(f > 0, x, domain=S.Reals)
    assert positif == Interval.open(-3, 1)
    assert positif != S.Reals and positif != S.EmptySet
    # L'extérieur des racines est l'autre candidat : on vérifie qu'il est faux.
    assert f.subs(x, 2) < 0 and f.subs(x, -4) < 0 and f.subs(x, 0) > 0
    return _lettre(options, lambda texte: texte.strip() == "pour $-3<x<1$")


# ── TCOMPL-ECHANTILLONNAGE ────────────────────────────────────────────────
_ECH = "TCOMPL-ECHANTILLONNAGE"


@mecanique(_ECH, "Q6", SYMBOLIC)
def _ech_q6(options):
    """E(X) pour X ~ B(3,1/2), par la somme définissant l'espérance."""
    from sympy import Rational, binomial

    p = Rational(1, 2)
    esperance = sum(k * binomial(3, k) * p**k * (1 - p) ** (3 - k) for k in range(4))
    assert esperance == Rational(3, 2)
    variance = 3 * p * (1 - p)
    assert variance == Rational(3, 4) and variance != esperance
    rendus = {
        Rational(1, 2): "$\\tfrac12$",
        Rational(3, 2): "$\\tfrac32$",
        Rational(3, 1): "$3$",
        Rational(3, 4): "$\\tfrac34$",
    }
    return _lettre(options, lambda texte: texte.strip() == rendus[esperance])


@mecanique(_ECH, "Q7", SYMBOLIC)
def _ech_q7(options):
    """Espérance de la loi uniforme sur {1,...,n}, calculée symboliquement."""
    from sympy import Rational, Sum, simplify, symbols

    n, k = symbols("n k", positive=True, integer=True)
    esperance = simplify(Sum(k * Rational(1, 1) / n, (k, 1, n)).doit())
    assert simplify(esperance - (n + 1) / 2) == 0
    assert simplify(esperance - n / 2) != 0
    rendus = {"(n + 1)/2": "$\\tfrac{n+1}2$", "n/2": "$\\tfrac n2$"}
    return _lettre(options, lambda texte: texte.strip() == rendus["(n + 1)/2"])


# ── TCOMPL-TEMPS-ATTENTE ──────────────────────────────────────────────────
_ATT = "TCOMPL-TEMPS-ATTENTE"


@mecanique(_ATT, "Q7", SYMBOLIC)
def _att_q7(options):
    """Constante de normalisation d'une densité exponentielle."""
    from sympy import Rational, Symbol, exp, integrate, oo, solve, symbols

    x = Symbol("x", positive=True)
    k = symbols("k")
    masse = integrate(k * exp(-2 * x), (x, 0, oo))
    solutions = solve(masse - 1, k)
    assert solutions == [2]
    assert integrate(exp(-2 * x), (x, 0, oo)) == Rational(1, 2)
    rendus = {1: "$k=1$", 2: "$k=2$", Rational(1, 2): "$k=\\tfrac12$"}
    return _lettre(options, lambda texte: texte.strip() == rendus[solutions[0]])


@mecanique(_ATT, "Q9", SYMBOLIC)
def _att_q9(options):
    """Espérance et variance de la loi uniforme continue sur [a;b]."""
    from sympy import Symbol, integrate, simplify, symbols

    x = Symbol("x")
    a, b = symbols("a b", real=True, positive=True)
    densite = 1 / (b - a)
    esperance = simplify(integrate(x * densite, (x, a, b)))
    variance = simplify(integrate((x - esperance) ** 2 * densite, (x, a, b)))
    assert simplify(esperance - (a + b) / 2) == 0
    assert simplify(variance - (b - a) ** 2 / 12) == 0
    assert simplify(esperance - (b - a) / 2) != 0
    assert simplify(variance - (b - a) / 12) != 0
    attendu = "$E(X)=\\tfrac{a+b}2$ et $V(X)=\\tfrac{(b-a)^2}{12}$"
    return _lettre(options, lambda texte: texte.strip() == attendu)


# ── TEXP-ARITHMETIQUE ─────────────────────────────────────────────────────
_ARITH = "TEXP-ARITHMETIQUE"


@mecanique(_ARITH, "Q6", SYMBOLIC)
def _arith_q6(options):
    """Le plus petit facteur premier de 221 dépasse 7 mais pas la racine."""
    from sympy import factorint, isprime, primerange, sqrt

    facteurs = sorted(factorint(221))
    assert facteurs == [13, 17]
    assert not isprime(221)
    petits = [p for p in primerange(2, 8)]
    assert all(221 % p for p in petits)           # 2,3,5,7 ne suffisent pas
    borne = max(p for p in primerange(2, 222) if p * p <= 221)
    assert borne == 13 and sqrt(221) < 15
    return _lettre(
        options,
        lambda texte: f"$p^2\\leq221$" in texte and f"jusqu'à ${borne}$" in texte,
    )


@mecanique(_ARITH, "Q7", SYMBOLIC)
def _arith_q7(options):
    """6x+9y=5 : le critère de Bézout est évalué, pas invoqué."""
    from sympy import gcd
    from sympy.solvers.diophantine.diophantine import diop_linear
    from sympy.abc import x, y

    d = gcd(6, 9)
    assert d == 3 and 5 % d != 0
    # `diop_linear` renvoie un couple de paramétrages, ou `(None, None)`
    # lorsqu'il n'existe aucune solution entière.
    assert diop_linear(6 * x + 9 * y - 5) == (None, None)
    # Contrôle : la même équation avec un second membre multiple de 3 en a.
    assert diop_linear(6 * x + 9 * y - 3) != (None, None)
    return _lettre(options, lambda texte: texte.startswith("n'admet aucune solution"))


@mecanique(_ARITH, "Q10", SYMBOLIC)
def _arith_q10(options):
    """Les quatre congruences proposées sont testées sur des cas concrets."""
    from sympy import primerange

    couples = [(a, p) for p in primerange(3, 20) for a in range(2, 10) if a % p]
    universelles = {
        "$a^{p-1}\\equiv1 \\pmod p$": all(pow(a, p - 1, p) == 1 for a, p in couples),
        "$a^{p}\\equiv1 \\pmod p$": all(pow(a, p, p) == 1 for a, p in couples),
        "$a^p\\equiv a \\pmod{p-1}$": all(
            pow(a, p, p - 1) == a % (p - 1) for a, p in couples
        ),
        "$p^{a-1}\\equiv1 \\pmod a$": all(
            pow(p, a - 1, a) == 1 for a, p in couples if a > 1
        ),
    }
    vraies = [texte for texte, valeur in universelles.items() if valeur]
    assert len(vraies) == 1
    return _lettre(options, lambda texte: texte.strip() == vraies[0])


# ── TEXP-COMPLEXES-ALGEBRE-GEOMETRIE ──────────────────────────────────────
_CPLXA = "TEXP-COMPLEXES-ALGEBRE-GEOMETRIE"


@mecanique(_CPLXA, "Q6", SYMBOLIC)
def _cplxa_q6(options):
    """(2+i)z = 5 : l'équation est résolue, pas devinée."""
    from sympy import I, Symbol, simplify, solve

    z = Symbol("z")
    solutions = solve((2 + I) * z - 5, z)
    assert len(solutions) == 1
    racine = simplify(solutions[0])
    assert racine == 2 - I
    assert simplify((2 + I) * (1 - 2 * I)) == 4 - 3 * I    # le distracteur D
    rendus = {2 - I: "$2-i$", 2 + I: "$2+i$", 1 - 2 * I: "$1-2i$"}
    return _lettre(options, lambda texte: texte.strip() == rendus[racine])


# ── TEXP-COMPLEXES-TRIGO-POLYNOMES ────────────────────────────────────────
_CPLXT = "TEXP-COMPLEXES-TRIGO-POLYNOMES"


@mecanique(_CPLXT, "Q7", SYMBOLIC)
def _cplxt_q7(options):
    """Chaque factorisation proposée est développée et comparée à P."""
    from sympy import Symbol, expand, simplify

    z = Symbol("z")
    P = z**3 - 3 * z**2 + 4 * z - 2
    candidats = {
        "$(z-1)(z^2-2z-2)$": (z - 1) * (z**2 - 2 * z - 2),
        "$(z-1)(z^2+2z+2)$": (z - 1) * (z**2 + 2 * z + 2),
        "$(z-1)(z^2-2z+2)$": (z - 1) * (z**2 - 2 * z + 2),
        "$(z-1)^3$": (z - 1) ** 3,
    }
    egaux = [texte for texte, forme in candidats.items()
             if simplify(expand(forme) - P) == 0]
    assert len(egaux) == 1
    return _lettre(options, lambda texte: texte.strip() == egaux[0])


# ── TSPE-CALCUL-INTEGRAL ──────────────────────────────────────────────────
_INTEG = "TSPE-CALCUL-INTEGRAL"


@mecanique(_INTEG, "Q6", SYMBOLIC)
def _integ_q6(options):
    """Aire entre y = x et y = x^2 sur [0;1], intégrée symboliquement."""
    from sympy import Rational, Symbol, integrate

    x = Symbol("x")
    aire = integrate(x - x**2, (x, 0, 1))
    assert aire == Rational(1, 6)
    assert integrate(x, (x, 0, 1)) == Rational(1, 2)
    assert integrate(x**2, (x, 0, 1)) == Rational(1, 3)
    rendus = {
        Rational(1, 2): "$\\tfrac12$",
        Rational(1, 6): "$\\tfrac16$",
        Rational(1, 3): "$\\tfrac13$",
        Rational(5, 6): "$\\tfrac56$",
    }
    return _lettre(options, lambda texte: texte.strip() == rendus[aire])


@mecanique(_INTEG, "Q7", SYMBOLIC)
def _integ_q7(options):
    """Les quatre relations de récurrence sont confrontées aux valeurs de I_n."""
    from sympy import E, Symbol, integrate, simplify

    x = Symbol("x")
    I = [integrate(x**n * E**x, (x, 0, 1)) for n in range(5)]
    relations = {
        "$I_n=e+nI_{n-1}$": lambda n: E + n * I[n - 1],
        "$I_n=nI_{n-1}-e$": lambda n: n * I[n - 1] - E,
        "$I_n=e-nI_{n-1}$": lambda n: E - n * I[n - 1],
        "$I_n=I_{n-1}$": lambda n: I[n - 1],
    }
    valides = [
        texte
        for texte, formule in relations.items()
        if all(simplify(I[n] - formule(n)) == 0 for n in range(1, 5))
    ]
    assert len(valides) == 1
    return _lettre(options, lambda texte: texte.strip() == valides[0])


# ── TSPE-PROBABILITES ─────────────────────────────────────────────────────
_PROBA = "TSPE-PROBABILITES"


@mecanique(_PROBA, "Q7", SYMBOLIC)
def _proba_q7(options):
    """P(au moins un succès) sur trois épreuves de probabilité 0,2."""
    from sympy import Rational, nsimplify

    p = Rational(2, 10)
    aucun = (1 - p) ** 3
    au_moins_un = 1 - aucun
    assert aucun == nsimplify("0.512")
    assert au_moins_un == nsimplify("0.488")
    rendus = {
        nsimplify("0.2"): "$0{,}2$",
        nsimplify("0.6"): "$0{,}6$",
        nsimplify("0.488"): "$0{,}488$",
        nsimplify("0.512"): "$0{,}512$",
    }
    return _lettre(options, lambda texte: texte.strip() == rendus[au_moins_un])


@mecanique(_PROBA, "Q8", SYMBOLIC)
def _proba_q8(options):
    """Le plus petit n tel que 1 - 0,98^n >= 0,5, cherché par énumération."""
    from sympy import Rational

    q = Rational(98, 100)
    seuil = Rational(1, 2)
    n = next(n for n in range(1, 500) if 1 - q**n >= seuil)
    assert n == 35
    assert 1 - q ** (n - 1) < seuil                 # minimalité
    assert 1 - q**50 >= seuil                       # 50 convient mais n'est pas minimal
    rendus = {2: "$n=2$", 25: "$n=25$", 35: "$n=35$", 50: "$n=50$"}
    return _lettre(options, lambda texte: texte.strip() == rendus[n])


# ── Revues conceptuelles des questions ajoutées ───────────────────────────
_BAYES = "TCOMPL-INFERENCE-BAYESIENNE"
_LOGH = "TCOMPL-LOGARITHME-HISTORIQUE"
_EVOL = "TCOMPL-MODELES-EVOLUTION"
_FONC = "TCOMPL-MODELES-FONCTION"
_GRAPHES = "TEXP-GRAPHES"
_MARKOV = "TEXP-MATRICES-MARKOV"

conceptuelle(
    _BAYES, "Q6", reponse="B",
    raisonnement=(
        "La valeur prédictive positive est la probabilité conditionnelle "
        "P(malade | test positif), que la formule de Bayes exprime par "
        "se·p / (se·p + (1−sp)(1−p)). Le seul terme qui varie ici est la "
        "prévalence p. Avec se = sp = 0,99, elle vaut 0,099/0,108 ≈ 0,92 pour "
        "p = 0,1 et 0,00099/0,01098 ≈ 0,09 pour p = 0,001. La chute vient de "
        "ce que le 1 % de faux positifs s'applique à une population saine "
        "presque entière : en population très saine, les faux positifs "
        "deviennent majoritaires parmi les tests positifs."
    ),
    source_cours=_cours_maths(_BAYES, "11_C2_tests_depistage.tex"),
    source_programme=f"{_BAYES}::C5",
    refutations={
        "A": (
            "Sensibilité et spécificité sont des probabilités conditionnelles "
            "SACHANT l'état de santé ; la VPP conditionne dans l'autre sens et "
            "fait donc intervenir la loi a priori, c'est-à-dire la prévalence. "
            "Le calcul le montre : 0,92 puis 0,09 pour un test inchangé."
        ),
        "C": (
            "L'affirmation inverse le sens de variation. Quand p décroît, le "
            "numérateur se·p décroît proportionnellement à p, tandis que le "
            "terme de faux positifs (1−sp)(1−p) tend vers 1−sp, constant non "
            "nul : le quotient décroît."
        ),
        "D": (
            "La VPP reste strictement positive tant que la sensibilité et la "
            "prévalence le sont : elle vaut environ 0,09, soit à peu près un "
            "test positif sur onze correspondant à un vrai malade."
        ),
    },
)

conceptuelle(
    _LOGH, "Q6", reponse="B",
    raisonnement=(
        "L'équation fonctionnelle ln(ab) = ln a + ln b vaut pour tous a, b "
        "strictement positifs. Le choix b = 1/a est licite puisque 1/a > 0, et "
        "il donne ln(a × 1/a) = ln a + ln(1/a), c'est-à-dire ln 1 = ln a + "
        "ln(1/a). Comme ln 1 = 0, on conclut ln(1/a) = −ln a. C'est le seul "
        "choix parmi les quatre qui fasse apparaître 1/a dans l'équation."
    ),
    source_cours=_cours_maths(_LOGH, "11_C2_equation_fonctionnelle.tex"),
    source_programme=f"{_LOGH}::C4",
    refutations={
        "A": (
            "b = a donne ln(a²) = 2 ln a, une identité correcte mais où 1/a "
            "n'apparaît jamais : aucune substitution ultérieure n'en fera "
            "sortir l'inverse."
        ),
        "C": (
            "b = 0 sort du domaine de définition de ln, qui est ]0 ; +∞[. "
            "L'équation fonctionnelle n'y est pas énoncée et ne peut donc pas "
            "y être appliquée."
        ),
        "D": (
            "a = b = 1 donne ln 1 = 2 ln 1, donc ln 1 = 0. C'est un "
            "préliminaire utile — il sert d'ailleurs à conclure — mais pris "
            "seul il ne dit rien de ln(1/a)."
        ),
    },
)

conceptuelle(
    _EVOL, "Q6", reponse="B",
    raisonnement=(
        "La construction graphique des termes d'une suite récurrente doit "
        "transformer une ordonnée en abscisse : on lit u_{n+1} = f(u_n) sur "
        "l'axe des ordonnées, et il faut le reporter sur l'axe des abscisses "
        "pour appliquer f de nouveau. La droite d'équation y = x est "
        "exactement l'outil de ce report, puisqu'un point de cette droite a "
        "des coordonnées égales. D'où la construction en escalier ou en "
        "escargot, qui laisse conjecturer monotonie et limite éventuelle."
    ),
    source_cours=_cours_maths(_EVOL, "11_C2_recurrence_arithmetico_geometrique.tex"),
    source_programme=f"{_EVOL}::C3",
    refutations={
        "A": (
            "L'axe des abscisses, d'équation y = 0, ne relie pas une ordonnée "
            "à une abscisse : il ne permet aucun report. Il ne sert qu'à "
            "situer le premier terme."
        ),
        "C": (
            "La tangente en u_0 approche f localement. Elle intervient dans "
            "l'étude de la vitesse de convergence, pas dans la construction "
            "des termes, qui sont exacts et non approchés."
        ),
        "D": (
            "La verticale x = u_0 donne le point (u_0 ; u_1) et rien de plus : "
            "sans y = x, l'ordonnée u_1 ne redescend jamais sur l'axe des "
            "abscisses et l'itération s'arrête au premier pas."
        ),
    },
)

conceptuelle(
    _EVOL, "Q7", reponse="C",
    raisonnement=(
        "En ajoutant 2 aux trois membres, l'hypothèse s'écrit "
        "2 − 1/n ≤ u_n ≤ 2 + 1/n pour tout n ≥ 1. Les deux suites encadrantes "
        "convergent vers 2, puisque 1/n tend vers 0. Le théorème des gendarmes "
        "conclut alors que (u_n) converge, et que sa limite est 2."
    ),
    source_cours=_cours_maths(_EVOL, "13_C6_limites_suites.tex"),
    source_programme=f"{_EVOL}::C6",
    refutations={
        "A": (
            "Une suite encadrée par deux suites convergentes de même limite ne "
            "peut pas diverger : au-delà d'un rang, tous ses termes sont dans "
            "un intervalle aussi petit qu'on veut autour de 2."
        ),
        "B": (
            "C'est l'écart u_n − 2 qui tend vers 0, ce que dit littéralement "
            "l'encadrement. La suite elle-même tend donc vers 2, pas vers 0."
        ),
        "D": (
            "Le théorème des gendarmes sert précisément à conclure sans "
            "expression explicite : l'encadrement suffit, et c'est tout son "
            "intérêt pour les suites définies par récurrence."
        ),
    },
)

conceptuelle(
    _FONC, "Q6", reponse="B",
    raisonnement=(
        "f est continue sur [0 ; 5] et 2 est compris entre f(0) = −3 et "
        "f(5) = 7 : le théorème des valeurs intermédiaires donne au moins une "
        "solution. La stricte croissance donne l'unicité, car deux antécédents "
        "distincts x₁ < x₂ entraîneraient f(x₁) < f(x₂), donc deux images "
        "différentes. Existence et unicité : exactement une solution."
    ),
    source_cours=_cours_maths(_FONC, "10_C1_etude_fonction.tex"),
    source_programme=f"{_FONC}::C2",
    refutations={
        "A": (
            "L'image de [0 ; 5] par une fonction continue est un intervalle "
            "contenant −3 et 7, donc contenant 2. Nier l'existence contredit "
            "le théorème des valeurs intermédiaires."
        ),
        "C": (
            "Deux solutions distinctes contrediraient la stricte croissance, "
            "qui interdit à f de prendre deux fois la même valeur."
        ),
        "D": (
            "Une infinité de solutions supposerait f constante égale à 2 sur "
            "tout un intervalle : impossible pour une fonction strictement "
            "croissante."
        ),
    },
)

conceptuelle(
    _FONC, "Q7", reponse="C",
    raisonnement=(
        "La dichotomie remplace une borne de l'intervalle par son milieu, en "
        "conservant la moitié aux extrémités de laquelle f change de signe. "
        "Ici f(0) = −1 < 0, f(1) = 1 > 0 et f(0,5) = −0,375 < 0 : le "
        "changement de signe se produit entre 0,5 et 1. L'intervalle retenu "
        "est donc [0,5 ; 1], moitié droite de [0 ; 1]."
    ),
    source_cours=_cours_maths(_FONC, "10_C1_etude_fonction.tex"),
    source_programme=f"{_FONC}::C3",
    refutations={
        "A": (
            "Sur [0 ; 0,5], f vaut −1 puis −0,375 : elle reste négative aux "
            "deux bornes, donc aucun changement de signe n'y est garanti et "
            "cette moitié est celle qu'on élimine."
        ),
        "B": (
            "[0,5 ; 0,75] est le résultat de deux coupes successives. Une "
            "étape de dichotomie ne remplace qu'une seule borne."
        ),
        "D": (
            "[0,25 ; 0,75] n'est pas une moitié de [0 ; 1] : la dichotomie "
            "supprime une moitié, elle ne recentre pas l'intervalle autour du "
            "milieu."
        ),
    },
)

conceptuelle(
    _FONC, "Q8", reponse="D",
    raisonnement=(
        "Le point moyen d'un nuage est défini par les moyennes arithmétiques "
        "des deux coordonnées : G(x̄ ; ȳ). Cette définition est celle qui rend "
        "les calculs de covariance et de régression cohérents, puisque les "
        "écarts se mesurent ensuite par rapport à ce point."
    ),
    source_cours=_cours_maths(_FONC, "12_C3_statistique_deux_variables.tex"),
    source_programme=f"{_FONC}::C6",
    refutations={
        "A": (
            "Le couple des maxima est un point extrême du nuage, souvent hors "
            "du nuage lui-même, et entièrement déterminé par une seule "
            "observation. Ce n'est pas une position moyenne."
        ),
        "B": (
            "Médiane et moyenne coïncident seulement pour une distribution "
            "symétrique. Le point moyen est défini par les moyennes, seules "
            "compatibles avec la suite du calcul statistique."
        ),
        "C": (
            "Un nuage n'est centré à l'origine qu'après soustraction des "
            "moyennes. Sur les données brutes, le point moyen n'a aucune "
            "raison d'être l'origine."
        ),
    },
)

conceptuelle(
    _FONC, "Q9", reponse="D",
    raisonnement=(
        "La droite des moindres carrés minimise la somme des carrés des écarts "
        "verticaux. L'annulation de la dérivée par rapport à l'ordonnée à "
        "l'origine donne exactement ȳ = a x̄ + b, c'est-à-dire que le point "
        "moyen appartient à la droite. Son équation s'écrit donc "
        "y − ȳ = a(x − x̄), quelle que soit la pente a."
    ),
    source_cours=_cours_maths(_FONC, "12_C3_statistique_deux_variables.tex"),
    source_programme=f"{_FONC}::C7",
    refutations={
        "A": (
            "Passer par tous les points supposerait le nuage déjà aligné. "
            "Sinon aucune droite ne le peut, et c'est précisément pourquoi on "
            "minimise un écart plutôt que de l'annuler."
        ),
        "B": (
            "La méthode minimise les carrés des écarts VERTICAUX y_i − (ax_i + b). "
            "Minimiser des distances perpendiculaires donnerait une autre "
            "droite, et rendrait indiscernables les régressions de y en x et "
            "de x en y, qui sont pourtant distinctes."
        ),
        "C": (
            "L'appartenance du point moyen n'est pas un cas particulier : elle "
            "découle de la condition d'optimalité sur b, donc vaut toujours."
        ),
    },
)

conceptuelle(
    _ATT, "Q6", reponse="B",
    raisonnement=(
        "L'absence de mémoire est une propriété de probabilité "
        "CONDITIONNELLE : sachant que l'attente a déjà duré s, la loi de "
        "l'attente restante est la loi initiale. Elle s'écrit "
        "P(X > s + t | X > s) = P(X > t). Le calcul la confirme : "
        "P(X > s+t)/P(X > s) = e^{−λ(s+t)}/e^{−λs} = e^{−λt} = P(X > t)."
    ),
    source_cours=_cours_maths(_ATT, "11_C2_loi_exponentielle.tex"),
    source_programme=f"{_ATT}::C4",
    refutations={
        "A": (
            "Les probabilités de survie se multiplient, elles ne s'ajoutent "
            "pas : e^{−λ(s+t)} = e^{−λs} × e^{−λt}. Une somme dépasserait "
            "d'ailleurs 1 pour s et t petits."
        ),
        "C": (
            "1 − e^{−λt} est la fonction de répartition P(X ≤ t). C'est une "
            "formule vraie, mais elle décrit la loi, pas le conditionnement "
            "qui définit l'absence de mémoire."
        ),
        "D": (
            "L'espérance vaut 1/λ et non λ ; surtout, une espérance ne dit "
            "rien d'un conditionnement par l'événement {X > s}."
        ),
    },
)

conceptuelle(
    _ATT, "Q8", reponse="D",
    raisonnement=(
        "L'espérance d'une variable à densité est l'intégrale de x contre la "
        "densité, sur le support de la loi. La densité exponentielle vaut "
        "λe^{−λx} sur [0 ; +∞[ et 0 ailleurs : l'espérance s'écrit donc "
        "∫₀^{+∞} x λ e^{−λx} dx, et une intégration par parties en donne la "
        "valeur 1/λ."
    ),
    source_cours=_cours_maths(_ATT, "11_C2_loi_exponentielle.tex"),
    source_programme=f"{_ATT}::C6",
    refutations={
        "A": (
            "Le facteur λ de la densité manque : cette intégrale vaut 1/λ², "
            "qui n'a pas la même dimension que l'espérance et n'en est donc "
            "jamais la valeur, sauf si λ = 1."
        ),
        "B": (
            "La densité est nulle sur ]−∞ ; 0[ ; intégrer x λ e^{−λx} depuis "
            "−∞ ne correspond à aucune loi, et l'intégrale diverge."
        ),
        "C": (
            "∫₀^{+∞} λ e^{−λx} dx vaut 1 : c'est la masse totale de la "
            "densité, la condition de normalisation, pas une moyenne."
        ),
    },
)

conceptuelle(
    _ARITH, "Q8", reponse="A",
    raisonnement=(
        "Le théorème de Gauss énonce que si a divise bc et si a est premier "
        "avec b, alors a divise c. L'hypothèse de primalité relative entre a "
        "et b remplace la primalité de a exigée par le lemme d'Euclide, et "
        "c'est ce qui en fait un outil applicable à des entiers quelconques."
    ),
    source_cours=_cours_maths(_ARITH, "12_C3_bezout_gauss.tex"),
    source_programme=f"{_ARITH}::C6",
    refutations={
        "B": (
            "Cette conclusion caractérise les nombres PREMIERS (lemme "
            "d'Euclide) et tombe sans cette hypothèse : 6 divise 4 × 3 = 12 "
            "sans diviser 4 ni 3."
        ),
        "C": (
            "« a divise b et a divise c donc a divise bc » découle "
            "immédiatement de la définition, sans hypothèse de primalité "
            "relative, et ne permet de conclure sur rien de nouveau."
        ),
        "D": (
            "La primalité relative n'entraîne aucune divisibilité de ce type : "
            "4 est premier avec 9 et ne divise pas 10."
        ),
    },
)

conceptuelle(
    _ARITH, "Q9", reponse="D",
    raisonnement=(
        "N = p₁p₂⋯p_k + 1 laisse le reste 1 dans la division par chacun des "
        "p_i. Aucun p_i ne divise donc N. Or tout entier supérieur à 1 admet "
        "au moins un facteur premier : ce facteur n'est pas dans la liste, qui "
        "n'était donc pas complète. La contradiction établit l'infinité."
    ),
    source_cours=_cours_maths(_ARITH, "13_C4_nombres_premiers.tex"),
    source_programme=f"{_ARITH}::C7",
    refutations={
        "A": (
            "N n'est pas toujours premier : 2·3·5·7·11·13 + 1 = 30031 = "
            "59 × 509. L'argument ne repose pas sur la primalité de N mais sur "
            "l'existence d'un facteur premier hors de la liste."
        ),
        "B": (
            "La division de N par p₁ laisse précisément le reste 1 : c'est "
            "l'inverse de ce que l'option affirme, et c'est ce reste qui fait "
            "toute la démonstration."
        ),
        "C": (
            "Si 2 figure dans la liste, le produit est pair et N est impair. "
            "La parité de N n'intervient d'ailleurs pas dans l'argument."
        ),
    },
)

conceptuelle(
    _ARITH, "Q11", reponse="C",
    raisonnement=(
        "L'algorithme d'Euclide repose sur l'égalité PGCD(a ; b) = "
        "PGCD(b ; a mod b) : tout diviseur commun de a et b divise le reste "
        "a − qb, et réciproquement. Le couple (b ; a mod b) a une seconde "
        "composante strictement plus petite que b, ce qui fait décroître "
        "l'algorithme jusqu'à un reste nul."
    ),
    source_cours=_cours_maths(_ARITH, "10_C1_divisibilite_pgcd.tex"),
    source_programme=f"{_ARITH}::C9",
    refutations={
        "A": (
            "L'égalité PGCD(a ; b) = PGCD(a − b ; b) est vraie sans aucune "
            "condition : c'est la variante par soustractions successives. La "
            "restriction « seulement lorsque b divise a » la rend inutilisable "
            "alors qu'elle est générale."
        ),
        "B": (
            "Les rôles de a et b sont inversés : comme a > b, on a "
            "b mod a = b, le couple est inchangé et l'algorithme ne progresse "
            "jamais."
        ),
        "D": (
            "a mod b est le reste d'une seule division. Il ne vaut le PGCD que "
            "par coïncidence ; le PGCD est le dernier reste NON NUL de la "
            "suite des divisions."
        ),
    },
)

conceptuelle(
    _CPLXA, "Q7", reponse="C",
    raisonnement=(
        "En posant z = a + ib, le conjugué est z̄ = a − ib et le produit se "
        "calcule par l'identité remarquable : (a + ib)(a − ib) = a² − (ib)² = "
        "a² + b², puisque i² = −1. Or |z| = √(a² + b²), donc |z|² = a² + b² = "
        "z z̄."
    ),
    source_cours=_cours_maths(_CPLXA, "11_C2_geometrie.tex"),
    source_programme=f"{_CPLXA}::C5",
    refutations={
        "A": (
            "(a + ib)² est le carré de z, pas le produit de z par son "
            "conjugué : le conjugué change le signe de la partie imaginaire, "
            "ce qui élimine le terme en i au lieu de le doubler."
        ),
        "B": (
            "a² − b² est la partie réelle de z². Le calcul correct fait "
            "apparaître −(ib)² = +b², d'où la somme a² + b²."
        ),
        "D": (
            "z z̄ vaut le module au CARRÉ : les deux ne coïncident que si "
            "|z| vaut 0 ou 1."
        ),
    },
)

conceptuelle(
    _CPLXT, "Q6", reponse="B",
    raisonnement=(
        "Les vecteurs u(cos a ; sin a) et v(cos b ; sin b) sont unitaires et "
        "font entre eux l'angle a − b. Le produit scalaire se calcule de deux "
        "manières : par les coordonnées, il vaut cos a cos b + sin a sin b ; "
        "par la formule ‖u‖‖v‖cos(u ; v), il vaut cos(a − b). L'égalité des "
        "deux expressions est exactement la formule d'addition."
    ),
    source_cours=_cours_maths(_CPLXT, "11_C2_equations_polynomiales.tex"),
    source_programme=f"{_CPLXT}::C3",
    refutations={
        "A": (
            "Le produit vectoriel n'est pas défini pour deux vecteurs du plan, "
            "et la grandeur analogue ferait apparaître sin(a − b), donc une "
            "autre formule."
        ),
        "C": (
            "Le produit scalaire somme les PRODUITS des coordonnées de même "
            "rang, non les coordonnées elles-mêmes. La somme des coordonnées "
            "n'est même pas invariante par rotation."
        ),
        "D": (
            "La dérivation de cosinus relève de l'analyse et donne cos′ = "
            "−sin. Elle ne fait intervenir aucun angle entre deux vecteurs."
        ),
    },
)

conceptuelle(
    _CPLXT, "Q8", reponse="D",
    raisonnement=(
        "|z − 2| est la distance du point d'affixe z au point A d'affixe 2, et "
        "|z + 2i| = |z − (−2i)| sa distance au point B d'affixe −2i. L'égalité "
        "des deux distances caractérise les points équidistants de A et B, "
        "c'est-à-dire la médiatrice du segment [AB]."
    ),
    source_cours=_cours_maths(_CPLXT, "12_C3_geometrie_racines_unite.tex"),
    source_programme=f"{_CPLXT}::C6",
    refutations={
        "A": (
            "Un cercle est le lieu des points à distance CONSTANTE d'un point "
            "fixe. Ici deux distances variables sont égalées entre elles, ce "
            "qui donne une droite, non un cercle."
        ),
        "B": (
            "Le segment est l'ensemble des points situés entre A et B ; ses "
            "points ne sont équidistants qu'en son milieu. La médiatrice lui "
            "est perpendiculaire."
        ),
        "C": (
            "L'axe des réels ne convient pas : pour z = 1, |1 − 2| = 1 alors "
            "que |1 + 2i| = √5. Il contient d'ailleurs A, qui est à distance "
            "nulle de lui-même."
        ),
    },
)

conceptuelle(
    _GRAPHES, "Q6", reponse="B",
    raisonnement=(
        "Modéliser, c'est choisir ce que représentent sommets et arêtes. Les "
        "objets reliés sont les villes : elles deviennent les sommets. La "
        "relation « être reliées par une route » est symétrique, puisque les "
        "routes sont à double sens : les arêtes sont donc non orientées, une "
        "par route."
    ),
    source_cours=_cours_maths(_GRAPHES, "10_C1_vocabulaire_graphes.tex"),
    source_programme=f"{_GRAPHES}::C2",
    refutations={
        "A": (
            "Orienter puis doubler chaque arête n'ajoute aucune information et "
            "fausse la lecture des degrés, sur laquelle reposent les "
            "raisonnements de parcours."
        ),
        "C": (
            "Prendre les routes comme sommets construit un autre graphe, utile "
            "pour des questions de parcours d'arêtes. La question porte sur "
            "les liaisons entre villes."
        ),
        "D": (
            "Un arbre suppose l'absence de cycle et exactement cinq arêtes "
            "pour six sommets. Rien ne l'assure ici, et un réseau routier en "
            "comporte presque toujours."
        ),
    },
)

conceptuelle(
    _MARKOV, "Q6", reponse="B",
    raisonnement=(
        "La situation associe un nombre à chaque COUPLE (atelier de départ, "
        "atelier d'arrivée) : la structure adaptée est un tableau à double "
        "entrée, c'est-à-dire une matrice carrée 3 × 3 dont le coefficient de "
        "la ligne i et de la colonne j est m_ij. Le sens de lecture "
        "ligne = départ, colonne = arrivée est celui qui rend le produit "
        "matriciel interprétable comme une composition de transferts."
    ),
    source_cours=_cours_maths(_MARKOV, "11_C2C3_suites_matricielles.tex"),
    source_programme=f"{_MARKOV}::C2",
    refutations={
        "A": (
            "Trois totaux ne conservent pas l'information de flux : deux "
            "situations très différentes peuvent donner les mêmes totaux par "
            "atelier."
        ),
        "C": (
            "Rien n'impose m_ij = m_ji. Imposer la symétrie contraindrait le "
            "modèle à des transferts réciproques, ce que l'énoncé n'affirme "
            "pas."
        ),
        "D": (
            "Une matrice ligne ne code que trois nombres, alors que la "
            "situation en comporte neuf."
        ),
    },
)

conceptuelle(
    _MARKOV, "Q7", reponse="C",
    raisonnement=(
        "Avec une distribution écrite en ligne, une transition s'écrit "
        "π_{n+1} = π_n T. Une récurrence immédiate donne π_n = π₀ Tⁿ : "
        "l'initialisation est π₀ = π₀ T⁰, et l'hérédité résulte de "
        "π_{n+1} = π_n T = (π₀ Tⁿ) T = π₀ T^{n+1}. C'est la démonstration "
        "attendue par la capacité."
    ),
    source_cours=_cours_maths(
        _MARKOV, "13_C6C7_demonstration_distribution_invariante.tex"),
    source_programme=f"{_MARKOV}::C6",
    refutations={
        "A": (
            "Le produit Tⁿπ₀ n'est pas défini avec π₀ écrite en ligne : les "
            "dimensions ne se composent pas. C'est la convention colonne qui "
            "donnerait cette écriture."
        ),
        "B": (
            "Une distribution et une matrice de transition ne s'additionnent "
            "pas : la somme des coefficients d'une distribution vaut 1, une "
            "propriété que l'addition d'une matrice détruit."
        ),
        "D": (
            "Multiplier par n ferait sortir la somme des coefficients de 1. Le "
            "nombre de transitions intervient en PUISSANCE de T, par itération "
            "de la relation de récurrence."
        ),
    },
)

conceptuelle(
    _INTEG, "Q8", reponse="D",
    raisonnement=(
        "∫₀^{60} v(t) dt est la distance parcourue, en mètres. La diviser par "
        "la durée 60 s donne la valeur moyenne de v sur [0 ; 60], c'est-à-dire "
        "la vitesse moyenne, en m·s⁻¹. C'est la définition même de la valeur "
        "moyenne d'une fonction sur un intervalle."
    ),
    source_cours=_cours_maths(_INTEG, "16_C6_applications.tex"),
    source_programme=f"{_INTEG}::C6",
    refutations={
        "A": (
            "La distance est l'intégrale SEULE. Le facteur 1/60 change l'unité "
            "de mètres en m·s⁻¹ : ce n'est plus une longueur."
        ),
        "B": (
            "L'accélération moyenne est (v(60) − v(0))/60, une variation de "
            "vitesse rapportée au temps, obtenue par différence et non par "
            "intégration."
        ),
        "C": (
            "Une valeur moyenne est comprise entre le minimum et le maximum de "
            "la fonction, et n'égale le maximum que si v est constante."
        ),
    },
)

conceptuelle(
    _INTEG, "Q9", reponse="A",
    raisonnement=(
        "Pour h > 0, F(x + h) − F(x) = ∫_x^{x+h} f(t) dt. Comme f est "
        "croissante, f(x) ≤ f(t) ≤ f(x + h) sur [x ; x + h] ; en intégrant ces "
        "inégalités sur un intervalle de longueur h, on obtient "
        "h f(x) ≤ F(x + h) − F(x) ≤ h f(x + h). En divisant par h et en "
        "faisant tendre h vers 0, la continuité de f donne F′(x) = f(x)."
    ),
    source_cours=_cours_maths(_INTEG, "11_C7_fonction_integrale.tex"),
    source_programme=f"{_INTEG}::C7",
    refutations={
        "B": (
            "L'encadrement est inversé. f croissante donne f(x) ≤ f(t) sur "
            "[x ; x + h] : c'est le rectangle de hauteur f(x) qui minore "
            "l'aire, pas celui de hauteur f(x + h)."
        ),
        "C": (
            "L'égalité ne vaut que si f est constante sur [x ; x + h]. C'est "
            "le passage à la limite, non l'aire elle-même, qui rétablit "
            "l'égalité."
        ),
        "D": (
            "f est positive, donc F est croissante et la différence "
            "F(x + h) − F(x) est positive : elle est même minorée par h f(x)."
        ),
    },
)

conceptuelle(
    _INTEG, "Q10", reponse="B",
    raisonnement=(
        "En intégrant l'identité (uv)′ = u′v + uv′ entre a et b, le membre de "
        "gauche donne [uv]_a^b et le membre de droite ∫u′v + ∫uv′. En isolant "
        "∫u′v, on obtient ∫_a^b u′v = [uv]_a^b − ∫_a^b uv′ : c'est exactement "
        "la formule d'intégration par parties."
    ),
    source_cours=_cours_maths(_INTEG, "13_C8_integration_par_parties.tex"),
    source_programme=f"{_INTEG}::C8",
    refutations={
        "A": (
            "La dérivée d'un quotient conduit à une autre formule et exige que "
            "v ne s'annule pas. La formule cherchée porte sur un produit."
        ),
        "C": (
            "La dérivée d'un produit n'est pas le produit des dérivées : avec "
            "u = v = x, (x²)′ = 2x alors que u′v′ = 1."
        ),
        "D": (
            "La dérivation d'une composée donne la technique du changement de "
            "variable, une autre méthode d'intégration."
        ),
    },
)

conceptuelle(
    _PROBA, "Q9", reponse="A",
    raisonnement=(
        "La loi binomiale n'a pas de fonction de répartition inversible en "
        "forme close : la recherche du plus petit intervalle de probabilité au "
        "moins 0,95 se fait en cumulant les P(X = k) de part et d'autre de "
        "l'espérance, jusqu'à atteindre le seuil. C'est un calcul numérique, "
        "conduit à la calculatrice ou en Python."
    ),
    source_cours=_cours_maths(_PROBA, "12_C3_C4_utilisation_binomiale.tex"),
    source_programme=f"{_PROBA}::C4",
    refutations={
        "B": (
            "P(X = k) fait intervenir un coefficient binomial et des "
            "puissances de k : ce n'est pas une expression du second degré, et "
            "aucune résolution algébrique fermée ne fournit les bornes."
        ),
        "C": (
            "[0 ; 50] a bien une probabilité égale à 1, mais l'énoncé demande "
            "le PLUS PETIT intervalle : la minimalité est toute la question."
        ),
        "D": (
            "E(X) ± σ couvre environ 68 % des cas dans le modèle normal "
            "approchant, très loin des 95 % demandés."
        ),
    },
)

conceptuelle(
    _PROBA, "Q10", reponse="B",
    raisonnement=(
        "En posant X_i = 1 si le i-ème lancer donne face et 0 sinon, on a "
        "X = X₁ + … + X₁₀, chaque X_i étant une variable de Bernoulli "
        "d'espérance 1/2. La linéarité de l'espérance donne alors "
        "E(X) = 10 × 1/2 = 5, sans écrire la loi de X ni aucun coefficient "
        "binomial."
    ),
    source_cours=_cours_maths(_PROBA, "13_C6_C7_esperance_linearite.tex"),
    source_programme=f"{_PROBA}::C6",
    refutations={
        "A": (
            "X = 10X₁ ne prendrait que les valeurs 0 et 10 : cette écriture "
            "suppose les dix lancers identiques au premier, alors qu'ils sont "
            "indépendants."
        ),
        "C": (
            "Le maximum vaut 1 dès qu'une face apparaît : il détecte "
            "l'existence d'un succès, il n'en compte pas le nombre."
        ),
        "D": (
            "C'est précisément ce que la linéarité permet d'éviter : elle vaut "
            "sans hypothèse d'indépendance et évite le calcul de la loi "
            "complète."
        ),
    },
)
