#!/usr/bin/env python3
"""Revues mathématiques des objets qu'aucun oracle ne peut trancher.

Un bloc `% BEGIN-VERIFY` prouve ce qui se calcule. Quatre cent dix-sept objets
du corpus n'en portent pas et ne peuvent pas en porter : un coup de pouce
reformule une étape, une fiche méthode décrit une démarche, une version
aménagée allège un énoncé. Leur exactitude mathématique existe pourtant, et
personne ne l'a établie.

Ce fichier la déclare, objet par objet. Chaque revue dit quatre choses, et le
producteur vérifie que les quatre sont là :

  `science`     ce qui est mathématiquement affirmé, et pourquoi c'est vrai ;
  `programme`   la capacité du contrat que l'objet sert ;
  `pedagogy`    ce que l'objet fait pour l'élève, et pourquoi c'est adapté ;
  `editorial`   ce qui a été vérifié dans la forme — notations, renvois.

Une revue qui se contente de paraphraser le titre n'est pas une revue : le
producteur refuse les champs trop courts, et refuse une revue qui ne nomme
aucune source. Ce qui reste sans revue reste `PENDING` et compte.

AUCUNE REVUE ICI N'APPROUVE. Elle établit `VALIDATED_BY_EVIDENCE` ; le
sign-off humain porte sur le corpus gelé, et lui seul.
"""

from __future__ import annotations

from typing import Any

#: chemin relatif de l'objet -> revue.
REVIEWS: dict[str, dict[str, Any]] = {}

#: Longueur en dessous de laquelle un champ ne dit rien d'utile.
MINIMUM = 60


def revue(
    chemin: str,
    *,
    science: str,
    programme: str,
    pedagogy: str,
    editorial: str,
    defect: str | None = None,
) -> None:
    """Déclare la revue d'un objet non formalisable.

    `defect` nomme un défaut trouvé pendant la revue. Une revue qui trouve un
    défaut et le tait ne vaut rien : le champ existe pour que la correction
    soit tracée à côté du constat.
    """
    if chemin in REVIEWS:
        raise ValueError(f"revue déjà déclarée : {chemin}")
    for nom, valeur in (
        ("science", science), ("programme", programme),
        ("pedagogy", pedagogy), ("editorial", editorial),
    ):
        if len(valeur.strip()) < MINIMUM:
            raise ValueError(f"{chemin}: champ {nom} trop court pour être une revue")
    REVIEWS[chemin] = {
        "science": science.strip(),
        "programme": programme.strip(),
        "pedagogy": pedagogy.strip(),
        "editorial": editorial.strip(),
        "defect": defect,
    }


# ===========================================================================
# 1SPE-DERIVATION-GLOBAL — cinq fiches méthode
# ===========================================================================

_D = "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL/methodes"

revue(
    f"{_D}/1SPE-DERGLOBAL-ME-001.tex",
    science="Les trois formules données sont exactes sur leur domaine propre : "
    "(x^n)' = n x^(n-1) vaut sur R pour n entier positif, (1/x)' = -1/x^2 sur "
    "R*, et (racine x)' = 1/(2 racine x) sur ]0 ; +inf[ seulement — la fiche "
    "exclut bien 0, où la racine n'est pas dérivable.",
    programme="Sert C1, « dériver une fonction de référence ». Les trois "
    "fonctions citées — puissance, inverse, racine — sont exactement celles que "
    "le programme de Première spécialité déclare comme fonctions de référence.",
    pedagogy="La fiche fait précéder l'application de la formule par "
    "l'identification du type de fonction. C'est le geste que l'élève oublie le "
    "plus souvent : il applique la formule des puissances à un quotient.",
    editorial="Notations conformes au reste du chapitre : f' pour la dérivée, "
    "dfrac pour les quotients affichés. Les domaines de validité sont écrits à "
    "côté de chaque formule et non renvoyés en note.",
)

revue(
    f"{_D}/1SPE-DERGLOBAL-ME-002.tex",
    science="Les trois règles sont exactes : (u+v)' = u'+v', (uv)' = u'v+uv', "
    "et (u/v)' = (u'v-uv')/v^2 sous la condition v non nul. L'ordre des termes "
    "du numérateur du quotient est le bon — c'est u'v moins uv', et l'inverse "
    "serait faux d'un signe.",
    programme="Sert C2, « calculer la dérivée d'une expression ». Les trois "
    "opérations couvrent ce que le programme exige à ce niveau ; la dérivée "
    "d'une composée n'y figure pas et la fiche ne la revendique pas.",
    pedagogy="La fiche demande d'identifier la structure GLOBALE avant de "
    "choisir la règle. C'est ce qui évite l'erreur classique consistant à "
    "dériver un produit en dérivant chaque facteur séparément.",
    editorial="Les lettres u et v sont introduites avant d'être employées, et "
    "la condition de non-annulation du dénominateur accompagne la règle du "
    "quotient au lieu d'être supposée connue.",
)

revue(
    f"{_D}/1SPE-DERGLOBAL-ME-003.tex",
    science="L'enchaînement est mathématiquement correct : le signe de f' sur "
    "un intervalle détermine le sens de variation de f sur cet intervalle, et "
    "les racines de f' délimitent les sous-intervalles où ce signe est "
    "constant. La fiche ne confond pas l'annulation de f' avec un changement "
    "de variation.",
    programme="Sert C3, « dresser le tableau de variations ». Le programme "
    "demande précisément cette chaîne : dérivée, signe, variations.",
    pedagogy="Les quatre étapes séparent le calcul du signe de la lecture des "
    "variations. L'élève qui saute l'étude de signe conclut sur la seule "
    "annulation de f' et se trompe dès qu'il y a un point d'inflexion.",
    editorial="Le tableau de signes et le tableau de variations sont nommés "
    "distinctement, ce qui évite la confusion des deux objets dans la copie.",
)

revue(
    f"{_D}/1SPE-DERGLOBAL-ME-004.tex",
    science="Le critère énoncé est le bon : f'(a) = 0 est nécessaire mais non "
    "suffisant, et la fiche exige le CHANGEMENT DE SIGNE de f' de part et "
    "d'autre du candidat. C'est ce qui distingue un extremum d'un point "
    "d'inflexion à tangente horizontale, comme x^3 en 0.",
    programme="Sert C4, « déterminer les extremums ». Le programme attend "
    "explicitement que l'élève ne conclue pas de la seule annulation de la "
    "dérivée.",
    pedagogy="L'ordre des étapes met le candidat avant la validation, ce qui "
    "installe le vocabulaire correct : on cherche des candidats, on ne trouve "
    "pas directement des extremums.",
    editorial="Le mot « candidat » est employé de façon constante, et la "
    "distinction local/global est portée par l'intervalle d'étude, pas laissée "
    "implicite.",
)

revue(
    f"{_D}/1SPE-DERGLOBAL-ME-005.tex",
    science="La démarche est correcte et complète : ramener la grandeur à une "
    "fonction d'UNE variable, déterminer le domaine imposé par la contrainte "
    "géométrique ou physique, puis appliquer l'étude des variations. Sans la "
    "réduction à une variable, la dérivation n'a pas de sens.",
    programme="Sert C5, « résoudre un problème d'optimisation ». Le programme "
    "situe l'optimisation comme aboutissement de l'étude des variations, ce que "
    "l'ordre des étapes respecte.",
    pedagogy="La fiche nomme la modélisation comme première étape, alors que "
    "l'élève commence souvent par dériver une expression à deux variables. Le "
    "domaine d'étude est demandé avant le calcul, pas après.",
    editorial="Les exemples de grandeurs — aire, volume, coût, bénéfice — "
    "couvrent les contextes géométriques et économiques attendus, sans en "
    "privilégier un seul.",
)

# ===========================================================================
# 1SPE-DERIVATION-LOCAL — cinq fiches méthode
# ===========================================================================

_L = "Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-LOCAL/methodes"

revue(
    f"{_L}/1SPE-DERLOCAL-ME-001.tex",
    science="Le taux de variation entre a et b est (f(b)-f(a))/(b-a), et la "
    "fiche exige a différent de b — sans quoi le quotient n'existe pas. Elle "
    "identifie correctement ce nombre à la pente de la sécante joignant les "
    "deux points de la courbe.",
    programme="Sert C1. Le programme introduit le nombre dérivé comme limite "
    "du taux de variation : cette fiche établit l'objet dont on prendra la "
    "limite.",
    pedagogy="Le calcul séparé de f(a) et f(b) avant le quotient évite "
    "l'erreur d'écriture la plus fréquente, qui est de soustraire les abscisses "
    "au numérateur.",
    editorial="Les mots « variation moyenne », « pente de sécante » et "
    "« vitesse moyenne » sont donnés comme synonymes de contexte, ce qui aide "
    "à reconnaître la demande sous ses différentes formulations.",
)

revue(
    f"{_L}/1SPE-DERLOCAL-ME-002.tex",
    science="Les deux interprétations données de f'(a) sont exactes et "
    "équivalentes : pente de la tangente au point d'abscisse a, et taux de "
    "variation instantané de la grandeur modélisée par f. La fiche demande "
    "d'ajouter l'unité, ce qui est nécessaire dès que f modélise une grandeur "
    "physique ou économique.",
    programme="Sert C2, l'interprétation du nombre dérivé. Le programme lie "
    "explicitement lecture graphique et interprétation contextuelle.",
    pedagogy="La fiche part des mots-clés de l'énoncé — vitesse instantanée, "
    "coût marginal — plutôt que de la notation, ce qui correspond à la "
    "difficulté réelle : reconnaître qu'une question porte sur f'(a).",
    editorial="L'exigence d'unité est isolée comme une étape à part entière, "
    "et non ajoutée en remarque finale où elle serait oubliée.",
)

revue(
    f"{_L}/1SPE-DERLOCAL-ME-003.tex",
    science="La lecture de la pente par deux points de la tangente est exacte, "
    "et la construction par déplacement horizontal de 1 puis vertical de f'(a) "
    "est la traduction correcte de la définition de la pente. Elle suppose un "
    "repère orthonormé, ce que la fiche indique.",
    programme="Sert C3, lecture et construction graphiques de la tangente, que "
    "le programme demande avant le calcul de son équation.",
    pedagogy="Le geste « +1 horizontalement, puis f'(a) verticalement » donne "
    "à l'élève une construction reproductible, là où la lecture de deux points "
    "quelconques introduit des erreurs de lecture d'échelle.",
    editorial="Le point A(a ; f(a)) est nommé et placé avant toute lecture, ce "
    "qui ancre la construction sur la courbe et non dans le vide.",
)

revue(
    f"{_L}/1SPE-DERLOCAL-ME-004.tex",
    science="L'équation y = f(a) + f'(a)(x - a) est exacte : c'est la droite "
    "passant par (a ; f(a)) de coefficient directeur f'(a). La fiche ne "
    "développe pas systématiquement, ce qui est le bon choix — la forme donnée "
    "porte le point et la pente, la forme développée les cache.",
    programme="Sert C4, l'équation de la tangente, écrite au programme sous "
    "exactement cette forme.",
    pedagogy="L'ordre f(a) puis f'(a) puis substitution empêche l'inversion "
    "des deux quantités, qui est l'erreur dominante sur cette question.",
    editorial="Le développement est présenté comme facultatif et conditionné à "
    "la demande de l'énoncé, ce qui évite un calcul inutile source d'erreurs.",
)

revue(
    f"{_L}/1SPE-DERLOCAL-ME-005.tex",
    science="L'approximation f(a+h) proche de f(a) + f'(a)h est exacte au "
    "premier ordre, et la fiche la conditionne à h petit — sans cette réserve "
    "l'égalité serait fausse. Elle présente le résultat comme une valeur "
    "approchée, jamais comme une égalité.",
    programme="Sert C5, l'approximation affine locale, que le programme "
    "présente comme conséquence directe de la tangente.",
    pedagogy="L'écriture préalable du nombre cherché sous la forme a+h est "
    "l'étape que l'élève omet : sans elle, il ne sait pas quel a choisir.",
    editorial="Le mot « approchée » figure dans la conclusion attendue, ce qui "
    "empêche l'élève d'écrire un signe égal là où il faut un signe environ.",
)


# ===========================================================================
# 1SPE-EXPONENTIELLE — six fiches méthode
# ===========================================================================

_E = "Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/methodes"

revue(
    f"{_E}/1SPE-EXPO-ME-001.tex",
    science="Les trois règles employées sont exactes et valent pour TOUS les "
    "réels a et b : e^a e^b = e^(a+b), e^a/e^b = e^(a-b), (e^a)^n = e^(na). "
    "Aucune condition de signe n'est requise, contrairement aux règles "
    "correspondantes sur les puissances de réels quelconques.",
    programme="Sert C2, la simplification d'expressions exponentielles. Ces "
    "trois relations sont celles que le programme énonce comme propriétés "
    "algébriques de l'exponentielle.",
    pedagogy="La fiche fait reconnaître la forme du produit ou du quotient "
    "avant d'appliquer la règle, ce qui évite l'erreur consistant à additionner "
    "les exponentielles au lieu de leurs exposants.",
    editorial="L'exponentielle est notée mathrm{e} en romain conformément à la "
    "charte du corpus, et les exposants composés sont parenthésés.",
)

revue(
    f"{_E}/1SPE-EXPO-ME-002.tex",
    science="L'argument est exact : la fonction exponentielle étant "
    "strictement croissante sur R, e^a < e^b équivaut à a < b. La comparaison "
    "des exposants est donc une équivalence, et non une simple implication.",
    programme="Sert C3, comparer des valeurs de l'exponentielle. Le programme "
    "attend que la comparaison s'appuie sur le sens de variation, sans "
    "calculatrice.",
    pedagogy="Comparer les exposants avant les images est le geste économique "
    "et exact ; il dispense d'un calcul numérique que l'élève ne peut de toute "
    "façon pas mener à la main.",
    editorial="La stricte croissance est nommée explicitement comme "
    "justification, et non supposée évidente.",
)

revue(
    f"{_E}/1SPE-EXPO-ME-003.tex",
    science="La formule (e^(at))' = a e^(at) est exacte pour tout réel "
    "constant a. Elle est le cas particulier de la dérivée d'une composée que "
    "le programme de Première admet, et la fiche l'applique sans la démontrer, "
    "ce qui est le régime attendu à ce niveau.",
    programme="Sert C4, la dérivation de t ↦ e^(at). C'est la seule forme "
    "composée que le programme de Première spécialité fait dériver.",
    pedagogy="L'identification préalable du coefficient a évite l'erreur "
    "dominante, qui est d'écrire la dérivée sans le facteur a.",
    editorial="La variable est notée t et non x, ce qui prépare l'usage en "
    "modélisation temporelle traité par les fiches suivantes.",
)

revue(
    f"{_E}/1SPE-EXPO-ME-004.tex",
    science="Le modèle Q(t) = Q_0 e^(at) est exact pour une évolution à taux "
    "de variation relatif constant, et la fiche relie correctement le signe de "
    "a au sens de l'évolution : croissance si a > 0, décroissance si a < 0. "
    "La valeur initiale est bien identifiée comme Q(0).",
    programme="Sert C5, la construction d'un modèle exponentiel continu, que "
    "le programme relie aux situations d'évolution.",
    pedagogy="Déterminer Q_0 puis a dans cet ordre suit la lecture naturelle "
    "d'un énoncé, où la valeur initiale est donnée avant le taux.",
    editorial="Les paramètres Q_0 et a sont nommés une fois pour toutes et "
    "réemployés sans changement de lettre dans les fiches voisines.",
)

revue(
    f"{_E}/1SPE-EXPO-ME-005.tex",
    science="Les trois faits énoncés sont exacts : toutes les courbes "
    "t ↦ e^(kt) passent par (0 ; 1) puisque e^0 = 1 ; l'exposant kt avec k > 0 "
    "donne une fonction croissante ; l'exposant -kt une fonction décroissante. "
    "La fiche restreint bien l'énoncé au cas k > 0.",
    programme="Sert C5, la reconnaissance graphique d'un modèle exponentiel.",
    pedagogy="Le point commun (0 ; 1) donne un repère fixe à partir duquel "
    "distinguer les courbes, plutôt qu'une comparaison d'allures qui dépend de "
    "l'échelle du graphique.",
    editorial="Le paramètre k est déclaré strictement positif avant d'être "
    "employé, ce qui rend les deux cas exhaustifs et disjoints.",
)

revue(
    f"{_E}/1SPE-EXPO-ME-006.tex",
    science="La caractérisation est exacte et complète : l'exponentielle est "
    "l'unique fonction dérivable sur R vérifiant f' = f et f(0) = 1. Les deux "
    "conditions sont nécessaires — f = 0 vérifie la première seule, et une "
    "fonction affine valant 1 en 0 vérifie la seconde seule. La fiche insiste "
    "sur « deux conditions, et deux seulement ».",
    programme="Sert C1, la reconnaissance de l'exponentielle par sa "
    "caractérisation, qui est la définition retenue par le programme.",
    pedagogy="Faire vérifier les deux conditions séparément, et fournir le "
    "contre-exemple de la fonction nulle, empêche l'élève de conclure sur la "
    "seule équation différentielle.",
    editorial="L'énoncé de la caractérisation est isolé du mode d'emploi, ce "
    "qui permet de le citer tel quel dans une copie.",
)
