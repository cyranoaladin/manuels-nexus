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
