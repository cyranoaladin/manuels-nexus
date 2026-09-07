#!/usr/bin/env python3
"""Table de decision : quelles fiches methode 1NSI sont justifiees.

CE QUE CE FICHIER N'EST PAS. Une premiere version de cet audit classait les
capacites par une liste fermee de verbes : « derouler » procedural, «
identifier » declaratif. Elle a declare TNSI-ALGORITHMIQUE — treize capacites
dont « parcourir un arbre en ordre infixe » — entierement declaratif, donc
exempt de fiche methode. C'etait faux, et faux dans le sens dangereux : une
exemption fabriquee par un mot manquant dans une liste.

Ce classement est un JUGEMENT EDITORIAL. Le laisser sortir d'une expression
reguliere revient a resoudre par ressemblance, ce que le depot interdit
partout ailleurs. Il est donc ecrit ici, capacite par capacite, avec sa
raison — et le producteur verifie que la table couvre exactement les
capacites du contrat, ni plus ni moins.

PORTEE. Seul `1NSI::livret_methodes` est en defaut parmi les 24 livrables :
`1SPE` et `TSPE_2026_2027` sont complets, et TNSI n'a pas de livret methodes
au perimetre. La table couvre donc les dix chapitres de 1NSI.

TROIS VERDICTS PAR CAPACITE.

`PROCEDURAL_UNCOVERED`  suite d'etapes reproductible, ecrite nulle part.
`DECLARATIVE`           savoir a enoncer, pas de resultat a construire.
`PROCEDURAL_COVERED`    la suite d'etapes est deja ecrite, et l'objet qui la
                        porte est nomme.

Une fiche ne nait que d'une ou plusieurs capacites `PROCEDURAL_UNCOVERED`.
Regrouper est permis quand une seule demarche les sert toutes ; inventer une
fiche par capacite pour remplir un compteur ne l'est pas.
"""

from __future__ import annotations

PROCEDURAL_UNCOVERED = "PROCEDURAL_UNCOVERED"
DECLARATIVE = "DECLARATIVE"
PROCEDURAL_COVERED = "PROCEDURAL_COVERED"

# chapitre -> code local -> (verdict, raison, objet couvrant eventuel)
CAPACITY_VERDICTS: dict[str, dict[str, tuple[str, str, str | None]]] = {
    "1NSI-TYPES-CONSTRUITS": {
        code: (PROCEDURAL_COVERED, "Chapitre deja pourvu de cinq fiches methode.", "NSI/chapitres/1NSI-TYPES-CONSTRUITS/methodes")
        for code in ("C1", "C2", "C3", "C4", "C5")
    },
    "1NSI-ALGO-PARCOURS-TRIS": {
        code: (PROCEDURAL_COVERED, "Chapitre deja pourvu de six fiches methode.", "NSI/chapitres/1NSI-ALGO-PARCOURS-TRIS/methodes")
        for code in ("C1", "C2", "C3", "C4", "C5", "C6")
    },
    "1NSI-ALGO-DICHO-GLOUTON-KNN": {
        code: (PROCEDURAL_COVERED, "Chapitre deja pourvu de trois fiches methode.", "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/methodes")
        for code in ("C1", "C2", "C3")
    },
    "1NSI-TYPES-BASE": {
        "C1": (PROCEDURAL_UNCOVERED, "Convertir entre bases 2, 10 et 16 se fait par divisions successives ou par regroupement de bits : une suite d'etapes que l'eleve execute. Le cours enonce les deux proprietes de conversion sans les derouler.", None),
        "C2": (PROCEDURAL_UNCOVERED, "Compter les bits necessaires et ecrire un entier en complement a deux sont deux calculs poses, avec un piege de signe a chaque etape.", None),
        "C3": (DECLARATIVE, "Expliquer pourquoi les flottants sont approximatifs est un savoir a enoncer ; il n'y a pas de resultat a construire.", None),
        "C4": (PROCEDURAL_UNCOVERED, "Dresser une table de verite se fait ligne par ligne, dans un ordre precis. Le cours donne les tables de `and` et `or` mais pas la demarche de construction.", None),
        "C5": (DECLARATIVE, "Identifier l'interet de differents encodages est comparatif : rien a executer.", None),
    },
    "1NSI-TABLES": {
        "C1": (PROCEDURAL_UNCOVERED, "Importer un CSV suit un enchainement fixe : ouvrir, lire l'en-tete, construire les dictionnaires, refermer. Chaque etape a son piege.", None),
        "C2": (PROCEDURAL_UNCOVERED, "Rechercher des lignes selon un critere en logique propositionnelle se pose : ecrire le predicat, le tester, le composer.", None),
        "C3": (PROCEDURAL_UNCOVERED, "Trier suivant une colonne demande de choisir une cle, un sens, et de decider entre `sort` et `sorted`.", None),
        "C4": (PROCEDURAL_UNCOVERED, "Fusionner deux tables par cle commune est une demarche en trois temps : indexer, apparier, projeter.", None),
    },
    "1NSI-LANGAGE": {
        "C1": (DECLARATIVE, "Identifier les constructions elementaires communes aux langages est un savoir de reconnaissance.", None),
        "C2": (DECLARATIVE, "Reperer traits communs et particuliers d'un nouveau langage est une lecture comparative.", None),
        "C3": (PROCEDURAL_UNCOVERED, "Prototyper une fonction, avec ses preconditions et postconditions, se fait dans un ordre : signature, ce qu'on exige, ce qu'on garantit. Sert C3, C6 et C7 ensemble.", None),
        "C4": (PROCEDURAL_UNCOVERED, "Construire un jeu de tests suit une methode : cas nominal, bornes, cas d'erreur. Le cours enonce ce qu'est un bon jeu de tests sans dire comment l'obtenir.", None),
        "C5": (PROCEDURAL_UNCOVERED, "Trouver une fonction dans une documentation est une recherche guidee : module, signature, valeur de retour, exemple.", None),
        "C6": (PROCEDURAL_UNCOVERED, "Decrire les preconditions : meme demarche que C3, servie par la meme fiche.", None),
        "C7": (PROCEDURAL_UNCOVERED, "Decrire les postconditions : meme demarche que C3, servie par la meme fiche.", None),
    },
    "1NSI-ARCHITECTURE-OS": {
        "C1": (DECLARATIVE, "Distinguer les roles des constituants d'une machine est un savoir de structure.", None),
        "C2": (PROCEDURAL_UNCOVERED, "Derouler une sequence d'instructions machine se fait dans un tableau de trace, registre par registre, cycle par cycle. Le cours enonce le principe sans donner le tableau.", None),
        "C3": (DECLARATIVE, "Identifier les fonctions d'un systeme d'exploitation est un savoir a enoncer.", None),
        "C4": (PROCEDURAL_UNCOVERED, "Se reperer et agir en ligne de commande suit toujours le meme ordre : ou suis-je, que contient ce dossier, comment m'y deplacer, comment agir sans casser.", None),
        "C5": (PROCEDURAL_UNCOVERED, "Lire et poser des droits en notation octale est un calcul : trois triplets, une somme par triplet.", None),
    },
    "1NSI-RESEAUX": {
        "C1": (DECLARATIVE, "Expliquer l'interet du decoupage en paquets est un savoir a enoncer.", None),
        "C2": (PROCEDURAL_UNCOVERED, "Derouler le protocole du bit alterne se fait par un tableau d'echanges, avec les pertes simulees a chaque tour.", None),
        "C3": (PROCEDURAL_UNCOVERED, "Determiner si deux machines communiquent est un calcul : masque, adresse reseau des deux cotes, comparaison.", None),
        "C4": (DECLARATIVE, "Identifier le role des capteurs et actionneurs est un savoir de reconnaissance.", None),
        "C5": (PROCEDURAL_UNCOVERED, "Realiser une IHM repondant a un cahier des charges suit une demarche : lire l'exigence, poser les composants, brancher les evenements, verifier point par point.", None),
    },
    "1NSI-WEB-IHM": {
        "C1": (DECLARATIVE, "Identifier les composants graphiques est un savoir de reconnaissance.", None),
        "C2": (DECLARATIVE, "Identifier les evenements traitables est un savoir de reconnaissance.", None),
        "C3": (PROCEDURAL_UNCOVERED, "Analyser puis modifier le gestionnaire d'un clic suit un chemin fixe : trouver le composant, trouver l'ecouteur, lire la fonction, modifier, reverifier.", None),
        "C4": (DECLARATIVE, "Distinguer ce qui s'execute cote client ou serveur est un savoir de structure.", None),
        "C5": (DECLARATIVE, "Distinguer ce qui est memorise et retransmis est un savoir de structure.", None),
        "C6": (DECLARATIVE, "Reconnaitre quand une transmission est chiffree est un savoir de reconnaissance.", None),
        "C7": (PROCEDURAL_UNCOVERED, "Analyser un formulaire se fait champ par champ : nom, methode, destination, puis ce qui arrive cote serveur. La meme lecture decide GET ou POST, donc sert C7, C8 et C9.", None),
        "C8": (PROCEDURAL_UNCOVERED, "Distinguer POST et GET dans un formulaire reel : meme lecture que C7, servie par la meme fiche.", None),
        "C9": (PROCEDURAL_UNCOVERED, "Choisir le type de requete selon la confidentialite : meme lecture que C7, servie par la meme fiche.", None),
    },
    "1NSI-PROJET-METHODES": {
        "C1": (DECLARATIVE, "Situer les evenements de l'histoire de l'informatique est un savoir de reperes.", None),
        "C2": (PROCEDURAL_UNCOVERED, "Decouper un projet en jalons se fait dans un ordre : besoin, livrables, jalons dates, repartition. Le cours enonce le principe du decoupage sans le derouler.", None),
        "C3": (PROCEDURAL_COVERED, "La demarche methodique de debogage est deja ecrite pas a pas, en liste numerotee, dans le cours du chapitre. Une fiche la recopierait.", "NSI/chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C3.tex"),
        "C4": (PROCEDURAL_UNCOVERED, "Documenter son code puis preparer l'oral suit une demarche : ce qu'on ecrit dans le code, ce qu'on ecrit a cote, ce qu'on dit et dans quel ordre.", None),
    },
}

# Fiches planifiees : une demarche, les capacites qu'elle sert.
# Regrouper est permis quand une seule demarche les sert toutes.
PLANNED_SHEETS: dict[str, list[tuple[str, str, tuple[str, ...]]]] = {
    "1NSI-TYPES-BASE": [
        ("M1", "Convertir un entier entre les bases 2, 10 et 16", ("C1",)),
        ("M2", "Compter les bits et ecrire en complement a deux", ("C2",)),
        ("M3", "Dresser la table de verite d'une expression booleenne", ("C4",)),
    ],
    "1NSI-TABLES": [
        ("M1", "Importer une table depuis un fichier CSV", ("C1",)),
        ("M2", "Selectionner les lignes qui verifient un critere", ("C2",)),
        ("M3", "Trier une table suivant une colonne", ("C3",)),
        ("M4", "Fusionner deux tables par une cle commune", ("C4",)),
    ],
    "1NSI-LANGAGE": [
        ("M1", "Specifier une fonction : prototype, preconditions, postconditions", ("C3", "C6", "C7")),
        ("M2", "Construire un jeu de tests qui trouve les bugs", ("C4",)),
        ("M3", "Trouver une fonction dans la documentation d'une bibliotheque", ("C5",)),
    ],
    "1NSI-ARCHITECTURE-OS": [
        ("M1", "Derouler une sequence d'instructions machine dans un tableau de trace", ("C2",)),
        ("M2", "Se reperer et agir en ligne de commande", ("C4",)),
        ("M3", "Lire et poser des droits en notation octale", ("C5",)),
    ],
    "1NSI-RESEAUX": [
        ("M1", "Derouler le protocole du bit alterne", ("C2",)),
        ("M2", "Determiner si deux machines peuvent communiquer", ("C3",)),
        ("M3", "Realiser une IHM a partir d'un cahier des charges", ("C5",)),
    ],
    "1NSI-WEB-IHM": [
        ("M1", "Analyser et modifier ce qui s'execute au clic d'un bouton", ("C3",)),
        ("M2", "Lire un formulaire et choisir entre GET et POST", ("C7", "C8", "C9")),
    ],
    "1NSI-PROJET-METHODES": [
        ("M1", "Decouper un projet en jalons", ("C2",)),
        ("M2", "Documenter son code et preparer l'oral", ("C4",)),
    ],
}


# ══════════════════════════════════════════════════════════════════════════
# LES CINQ AUTRES MANUELS
#
# Le triage `PEDAGOGICAL_ROLE_APPLICABILITY_AUDIT` a laisse 82 cellules
# (capacite, `methodes`) sans verdict editorial, dans seize chapitres de
# TNSI, TSPE, TCOMPL et 1SPE. C'etait exactement l'etat de 1NSI avant son
# audit : une lacune tant que l'absence n'est pas justifiee.
#
# Le critere applique, capacite par capacite, est le meme qu'au-dessus, et
# c'est celui de la decision humaine §5 : une fiche methode n'est due que
# lorsqu'il existe une DEMARCHE REUTILISABLE, applicable a des instances que
# le cours ne traite pas, et qui n'est ecrite nulle part. Trois consequences
# qui reviennent souvent ci-dessous :
#
#   * une DEMONSTRATION EXIGIBLE n'appelle pas de fiche. Elle est ecrite en
#     entier dans le cours, souvent par deux voies (calcul et denombrement) ;
#     une fiche la recopierait mot pour mot. C'est le cas de TSPE-COMBI C3 et
#     C4, TSPE-PRIMEQ C4 et C5, TSPE-INTEG C7 et C8, TSPE-PROBA C5 et C9 ;
#   * une SYNTAXE n'est pas une demarche. Ecrire `class`, `__init__`, `self`,
#     ou `INSERT INTO ... VALUES` se lit dans le cours et son exemple ;
#   * une REGLE DE DECISION deja ecrite comme telle — « le choix depend des
#     operations dominantes », « un interblocage se traduit par un cycle dans
#     le graphe d'attente » — couvre la capacite : la demarche est la, ecrite.
#
# Chaque verdict `PROCEDURAL_COVERED` nomme le fichier qui couvre, et le
# producteur verifie que ce fichier existe.
# ══════════════════════════════════════════════════════════════════════════

_NSI = "NSI/chapitres"
_MATHS = "Mathematiques/manuel-maths/chapitres"


def _cours(racine: str, chapitre: str, fichier: str) -> str:
    return f"{racine}/{chapitre}/cours/{fichier}"


def _fiche(racine: str, chapitre: str, fichier: str) -> str:
    return f"{racine}/{chapitre}/methodes/{fichier}"


_ALGO = "TNSI-ALGORITHMIQUE"
_ARBRES = _cours(_NSI, _ALGO, "10_C01_arbres_parcours.tex")
_ABR = _cours(_NSI, _ALGO, "11_C02_arbres_recherche.tex")
_GRAPHES_CC = _cours(_NSI, _ALGO, "13_C04_graphes_cycle_chemin.tex")

CAPACITY_VERDICTS[_ALGO] = {
    "C1": (PROCEDURAL_COVERED, "Le cours enonce le schema recursif lui-meme — cas de base l'arbre vide, cas general combinant les deux sous-arbres — puis le deroule sur la taille. La demarche est ecrite, pas seulement son resultat.", _ARBRES),
    "C2": (PROCEDURAL_COVERED, "Meme schema recursif, ecrit dans le meme appui de marge et applique a la hauteur avec sa convention $-1$ pour l'arbre vide.", _ARBRES),
    "C3": (PROCEDURAL_UNCOVERED, "Donner les trois ordres d'un arbre DESSINE se fait a la main, en marquant chaque noeud a son passage. Le cours definit les trois ordres et ne montre le code que de l'infixe : le trace pas a pas, celui que l'epreuve demande, n'est ecrit nulle part.", None),
    "C4": (PROCEDURAL_UNCOVERED, "Le parcours en largeur se deroule a la main en tenant l'etat de la file a chaque tour. Meme demarche de trace que C3, servie par la meme fiche.", None),
    "C5": (PROCEDURAL_COVERED, "Le cours ecrit la descente comparaison par comparaison, et son cout en fonction de la hauteur. Rien a formaliser de plus.", _ABR),
    "C6": (PROCEDURAL_COVERED, "L'insertion est enoncee comme une procedure — descendre comme pour une recherche jusqu'a un sous-arbre vide, y placer une feuille — avec le piege de la reaffectation nomme.", _ABR),
    "C7": (PROCEDURAL_UNCOVERED, "Sur un graphe, le parcours en largeur demande de tenir DEUX etats a la main : la file et l'ensemble des sommets deja vus. L'ordre de visite depend de l'ordre des voisins ; le cours donne le code, pas le tableau de trace.", None),
    "C8": (PROCEDURAL_UNCOVERED, "Le parcours en profondeur se deroule avec la pile d'appels. Meme demarche de trace que C7, servie par la meme fiche.", None),
    "C9": (PROCEDURAL_COVERED, "Le critere est ecrit exactement : un sommet deja visite qui n'est pas le parent direct. Le cours nomme aussi le faux positif — revenir sur ses pas n'est pas un cycle.", _GRAPHES_CC),
    "C10": (PROCEDURAL_COVERED, "La definition EST la demarche : memoriser le predecesseur de chaque sommet atteint, puis remonter la chaine depuis l'arrivee, en traitant explicitement l'absence de chemin.", _GRAPHES_CC),
    "C11": (PROCEDURAL_UNCOVERED, "Le cours enonce les trois mots — diviser, regner, combiner — et les illustre sur le tri fusion. Passer d'un probleme NEUF a sa structure diviser pour regner (que divise-t-on, quel est le cas de base, comment recoller) reste a formaliser.", None),
    "C12": (PROCEDURAL_UNCOVERED, "Le cours montre une version naive puis une version memoisee du rendu de monnaie. La transformation elle-meme — reperer le recoupement, choisir la cle du dictionnaire, ou lire et ou ecrire — s'applique a tout autre probleme et n'est ecrite nulle part.", None),
    "C13": (DECLARATIVE, "La capacite demande d'EXPLIQUER le principe de Boyer-Moore, pas de le derouler ni de l'ecrire. Le cours expose la comparaison de droite a gauche et la regle du mauvais caractere : c'est un savoir a enoncer.", None),
}

_STRUCT = "TNSI-STRUCTURES-DONNEES"
_INTERFACE = _cours(_NSI, _STRUCT, "10_C01_interface_implementation.tex")
_CLASSES = _cours(_NSI, _STRUCT, "11_C02_classes.tex")
_PILES = _cours(_NSI, _STRUCT, "12_C03_piles_files_choix.tex")
_ARBRES_SD = _cours(_NSI, _STRUCT, "13_C04_arbres_binaires.tex")
_GRAPHES_SD = _cours(_NSI, _STRUCT, "14_C05_graphes.tex")

CAPACITY_VERDICTS[_STRUCT] = {
    "C1": (PROCEDURAL_UNCOVERED, "Le cours DEFINIT ce qu'est une interface et en montre une, celle de la pile. Produire l'interface d'une structure qu'on decouvre — lister les operations, dire ce que chacune exige et ce qu'elle garantit, decider des cas limites — est une demarche a part entiere, et elle n'est pas ecrite.", None),
    "C2": (DECLARATIVE, "Distinguer interface et implementation est un savoir a enoncer ; il n'y a pas de resultat a construire.", None),
    "C3": (PROCEDURAL_COVERED, "Le cours ecrit DEUX implementations completes de la meme pile — par liste Python et par liste chainee — et enonce la discipline qui les relie : tester le comportement observable, pas les details internes.", _INTERFACE),
    "C4": (PROCEDURAL_COVERED, "Ecrire une classe est une syntaxe, pas une demarche : le cours en donne le modele complet (constructeur, attributs, methodes) et nomme le piege de `self`. Une fiche recopierait le squelette.", _CLASSES),
    "C5": (PROCEDURAL_COVERED, "L'acces `objet.attribut` et l'appel `objet.methode(...)` sont montres sur l'exemple file, avec le vocabulaire attribut/methode/instance pose a cote.", _CLASSES),
    "C6": (DECLARATIVE, "Distinguer FIFO et LIFO par le jeu des methodes est un savoir de reconnaissance.", None),
    "C7": (PROCEDURAL_COVERED, "La regle de decision est ecrite comme telle : identifier les operations dominantes de la situation, puis lire la correspondance operation -> structure que le cours dresse.", _PILES),
    "C8": (DECLARATIVE, "Comparer la recherche dans une liste et dans un dictionnaire est un savoir de cout, enonce en marge du cours.", None),
    "C9": (DECLARATIVE, "Identifier une situation arborescente est une reconnaissance : hierarchie, ou processus recursif par nature.", None),
    "C10": (PROCEDURAL_COVERED, "Taille, hauteur et nombre de feuilles sont calcules dans le cours, en code puis a la main sur un arbre nomme, avec les trois valeurs justifiees.", _ARBRES_SD),
    "C11": (PROCEDURAL_UNCOVERED, "Modeliser demande de choisir ce que sont les sommets, ce que sont les aretes, et si le graphe est oriente ou pondere. Le cours donne trois modelisations deja faites ; il ne dit pas comment on arrive a en produire une.", None),
    "C12": (PROCEDURAL_COVERED, "La regle de remplissage est ecrite — la case $(i,j)$ vaut 1 s'il existe une arete de $i$ vers $j$ — et appliquee sur un graphe nomme.", _GRAPHES_SD),
    "C13": (PROCEDURAL_COVERED, "Le cours donne la representation par listes de successeurs du meme graphe, et nomme le piege du sommet sans successeur qui doit rester present avec une liste vide.", _GRAPHES_SD),
    "C14": (PROCEDURAL_UNCOVERED, "Le cours convertit dans UN sens, matrice vers listes, par une comprehension. Le sens inverse, et surtout la conversion a la main sur un graphe non oriente ou la symetrie se perd facilement, ne sont pas traites.", None),
}

_BDD = "TNSI-BASES-DE-DONNEES"
_MODIF_SQL = _cours(_NSI, _BDD, "14_C05_insert_update_delete.tex")

CAPACITY_VERDICTS[_BDD] = {
    "C1": (DECLARATIVE, "Nommer relation, attribut, domaine, schema, cle primaire et cle etrangere est un savoir de vocabulaire.", None),
    "C2": (DECLARATIVE, "Distinguer la structure, stable, du contenu, qui evolue, est un savoir enonce comme propriete dans le cours.", None),
    "C3": (PROCEDURAL_UNCOVERED, "Reperer les anomalies d'un schema est une lecture methodique : chercher l'information stockee deux fois, verifier que chaque relation a une cle primaire, verifier que chaque reference est une cle etrangere. Le cours montre UNE anomalie dans un encadre d'erreur frequente ; il ne donne pas la grille de lecture.", None),
    "C4": (DECLARATIVE, "Enumerer les quatre services d'un SGBD — persistance, concurrence, efficacite, securisation — est un savoir a enoncer.", None),
    "C5": (DECLARATIVE, "Identifier les clauses d'une requete est de la reconnaissance : SELECT, FROM, WHERE sont nommees et definies.", None),
    "C6": (PROCEDURAL_UNCOVERED, "Le cours donne la syntaxe de chaque clause separement. Traduire une question posee en francais — quelles colonnes, quelles tables, faut-il croiser et sur quelle egalite de cles, quelle condition, quel tri — est la demarche que l'epreuve demande, et elle traverse les quatre clauses a la fois.", None),
    "C7": (PROCEDURAL_UNCOVERED, "La clause WHERE fait partie de la meme traduction : elle est servie par la meme fiche que C6.", None),
    "C8": (PROCEDURAL_UNCOVERED, "Decider qu'il faut un JOIN, et sur quelle egalite cle etrangere = cle primaire, est l'etape la plus difficile de cette traduction : meme fiche que C6.", None),
    "C9": (PROCEDURAL_UNCOVERED, "Le tri ORDER BY ferme la meme requete, et sa place apres WHERE fait partie de la demarche : meme fiche que C6.", None),
    "C10": (PROCEDURAL_COVERED, "INSERT INTO ... VALUES est une syntaxe, donnee avec son exemple.", _MODIF_SQL),
    "C11": (PROCEDURAL_COVERED, "Le cours donne la syntaxe d'UPDATE et, surtout, la precaution qui en fait une demarche : executer d'abord le SELECT portant la meme clause WHERE pour voir quels tuples seront touches.", _MODIF_SQL),
    "C12": (PROCEDURAL_COVERED, "Meme chose pour DELETE, avec l'avertissement sur l'absence de WHERE ecrit noir sur blanc.", _MODIF_SQL),
}

_LANG = "TNSI-LANGAGES-ET-PROGRAMMATION"
_API = _cours(_NSI, _LANG, "12_C03_api_modules.tex")
_PARADIGMES = _cours(_NSI, _LANG, "13_C04_paradigmes.tex")
_DEBUG = _cours(_NSI, _LANG, "14_C05_debug.tex")

CAPACITY_VERDICTS[_LANG] = {
    "C1": (DECLARATIVE, "Comprendre qu'un programme est une donnee est une idee a enoncer, illustree par l'interpreteur du cours.", None),
    "C2": (DECLARATIVE, "L'independance de la calculabilite vis-a-vis du langage est enoncee comme propriete.", None),
    "C3": (DECLARATIVE, "Expliquer l'indecidabilite de l'arret sans formalisme est un raisonnement a restituer ; l'argument par le programme paradoxal est ecrit en entier.", None),
    "C4": (PROCEDURAL_UNCOVERED, "Ecrire une fonction recursive NEUVE demande de choisir le cas de base, de verifier que le cas general se ramene strictement a une instance plus petite, et de s'assurer de la terminaison. Le cours donne la definition et deux exemples ; la demarche de construction n'est pas ecrite.", None),
    "C5": (PROCEDURAL_UNCOVERED, "Analyser demande de dessiner l'arbre d'appels et de compter. Le cours LIT un arbre d'appels deja decrit ; le construire soi-meme, appel apres retour, est la meme demarche que C4 vue dans l'autre sens, et la meme fiche les sert.", None),
    "C6": (PROCEDURAL_COVERED, "Le cours importe une bibliotheque standard et appelle trois de ses fonctions : l'usage est montre.", _API),
    "C7": (PROCEDURAL_COVERED, "La propriete « Exploiter la documentation » EST la demarche : nom et ordre des parametres, types attendus, valeur renvoyee, exemples, et `help` pour l'obtenir.", _API),
    "C8": (PROCEDURAL_COVERED, "Le cours ecrit un module complet avec ses docstrings et enonce la regle qui les gouverne : documenter ce que fait la fonction, pas comment elle le fait.", _API),
    "C9": (DECLARATIVE, "Distinguer les trois paradigmes sur des exemples est une reconnaissance ; le cours donne le meme calcul ecrit trois fois.", None),
    "C10": (PROCEDURAL_COVERED, "La propriete « Choisir un paradigme selon le contexte » est une regle de decision ecrite, suivie de l'avertissement qu'un projet reel les combine.", _PARADIGMES),
    "C11": (DECLARATIVE, "Identifier les causes typiques de bugs est de la reconnaissance : le cours enumere les quatre familles — flottants, effets de bord, inegalites, nommage — chacune avec son exemple.", _DEBUG),
}

_ARCH = "TNSI-ARCHITECTURES-MATERIELLES-SY"
_PROCESSUS = _cours(_NSI, _ARCH, "11_C02_processus.tex")
_CHIFFREMENT = _cours(_NSI, _ARCH, "13_C04_chiffrement.tex")

CAPACITY_VERDICTS[_ARCH] = {
    "C1": (DECLARATIVE, "Identifier les composants d'un systeme sur puce et les avantages de l'integration est un savoir a enoncer.", None),
    "C2": (DECLARATIVE, "Decrire la creation d'un processus — allouer, charger, inscrire, puis `fork` et `exec` — est un savoir a restituer.", None),
    "C3": (PROCEDURAL_UNCOVERED, "L'epreuve demande le CHRONOGRAMME : qui occupe le processeur, pendant combien de temps, dans quel ordre, avec quel temps restant. Le cours donne le code du tourniquet ; derouler l'ordonnancement a la main, tableau en main, n'est pas ecrit.", None),
    "C4": (PROCEDURAL_COVERED, "La demarche est ecrite comme propriete : construire le graphe d'attente — chaque processus pointe vers la ressource attendue, chaque ressource vers le processus qui la retient — et y chercher un cycle.", _PROCESSUS),
    "C5": (PROCEDURAL_UNCOVERED, "Determiner la route empruntee demande d'enumerer les chemins, de calculer la metrique du protocole considere — nombre de sauts pour RIP, somme des couts pour OSPF — puis de comparer. Le cours compare sur un exemple ; la marche a suivre, transposable a un autre reseau, n'est pas posee.", None),
    "C6": (DECLARATIVE, "Decrire les deux familles de chiffrement, leurs cles et leurs couts, est un savoir a enoncer.", None),
    "C7": (DECLARATIVE, "Decrire l'echange d'une cle symetrique par un protocole asymetrique est un savoir a restituer ; le cours precise que le detail de TLS n'est pas exigible.", _CHIFFREMENT),
}

CAPACITY_VERDICTS["TNSI-HISTOIRE-INFORMATIQUE"] = {
    "C1": (DECLARATIVE, "Situer les evenements de l'histoire de l'informatique est un savoir de reperes chronologiques.", None),
    "C2": (DECLARATIVE, "Identifier l'evolution des roles du logiciel et du materiel est une lecture historique, pas une demarche a executer.", None),
}

# ── Mathématiques ────────────────────────────────────────────────────────
# Les chapitres de maths portent déjà un livret méthodes : leurs fiches
# existent, `ME-001` à `ME-00n`, et couvrent les capacités du cœur du
# chapitre. Ce qui restait sans verdict, ce sont les capacités ajoutées
# ensuite — souvent des DÉMONSTRATIONS EXIGIBLES, écrites en entier dans le
# cours — et les démarches longues que le cours illustre sans les poser.

_SECDEG = "1SPE-SECOND-DEGRE"
_SECDEG_C7 = _cours(_MATHS, _SECDEG, "16_C7_somme_produit_racines.tex")
_SECDEG_SIGNE = _fiche(_MATHS, _SECDEG, "1SPE-SECDEG-ME-004.tex")
_SECDEG_METHODES = f"{_MATHS}/{_SECDEG}/methodes"

CAPACITY_VERDICTS[_SECDEG] = {
    code: (PROCEDURAL_COVERED, f"Fiche méthode ME-00{code[1:]} du chapitre.", _SECDEG_METHODES)
    for code in ("C1", "C2", "C3", "C4", "C5", "C6")
}
CAPACITY_VERDICTS[_SECDEG]["C7"] = (
    PROCEDURAL_COVERED,
    "Le cours pose le théorème — les fonctions s'annulant en deux réels "
    "distincts sont exactement les $a(x-x_1)(x-x_2)$ — le démontre dans les "
    "deux sens, et le déroule sur un exemple chiffré. Une fiche recopierait "
    "ce passage.",
    _SECDEG_C7,
)
CAPACITY_VERDICTS[_SECDEG]["C8"] = (
    PROCEDURAL_COVERED,
    "Étudier le signe d'un trinôme DÉJÀ factorisé est l'étape 3 de la fiche "
    "M4, qui dresse le tableau de signes à partir des racines et de la règle "
    "du signe de $a$. Le cas factorisé est le même travail, sans le calcul "
    "du discriminant.",
    _SECDEG_SIGNE,
)

_ECH = "TCOMPL-ECHANTILLONNAGE"
_ECH_UNIFORME = _cours(_MATHS, _ECH, "13_C7_loi_uniforme_discrete.tex")
CAPACITY_VERDICTS[_ECH] = {
    code: (PROCEDURAL_COVERED, "Fiche méthode du chapitre.", f"{_MATHS}/{_ECH}/methodes")
    for code in ("C1", "C2", "C3", "C4", "C5", "C6")
}
CAPACITY_VERDICTS[_ECH]["C7"] = (
    PROCEDURAL_COVERED,
    "La loi uniforme sur un ensemble fini tient en une définition et un "
    "calcul d'espérance, tous deux écrits dans le cours neuf avec leur "
    "démonstration par la somme des $n$ premiers entiers. Il n'y a pas de "
    "démarche transposable au-delà de ce calcul.",
    _ECH_UNIFORME,
)

_ATT = "TCOMPL-TEMPS-ATTENTE"
CAPACITY_VERDICTS[_ATT] = {
    code: (PROCEDURAL_COVERED, "Fiche méthode du chapitre.", f"{_MATHS}/{_ATT}/methodes")
    for code in ("C1", "C2", "C3", "C4", "C5", "C6")
}
CAPACITY_VERDICTS[_ATT]["C7"] = (
    PROCEDURAL_UNCOVERED,
    "Le chapitre traite chaque loi continue par une fiche qui enchaîne "
    "densité, fonction de répartition, espérance — c'est ce que fait M4 pour "
    "l'exponentielle. La loi uniforme continue demande le même enchaînement, "
    "variance comprise, et il ne se déduit pas de celui de l'exponentielle : "
    "la primitive et l'intégrale ne sont pas les mêmes.",
    None,
)

_ME = "TCOMPL-MODELES-EVOLUTION"
CAPACITY_VERDICTS[_ME] = {
    code: (PROCEDURAL_COVERED, "Fiche méthode du chapitre.", f"{_MATHS}/{_ME}/methodes")
    for code in ("C1", "C2", "C3", "C4", "C5")
}
CAPACITY_VERDICTS[_ME]["C6"] = (
    PROCEDURAL_UNCOVERED,
    "Déterminer une limite est la démarche la plus réutilisée de la classe : "
    "reconnaître la forme indéterminée, factoriser par le terme dominant, ou "
    "encadrer et invoquer les gendarmes. Le cours neuf pose les règles et "
    "trois exemples ; l'ordre des gestes, lui, mérite d'être écrit une fois "
    "pour toutes.",
    None,
)

_INTEG = "TSPE-CALCUL-INTEGRAL"
_INTEG_C6 = _cours(_MATHS, _INTEG, "16_C6_applications.tex")
_INTEG_C7 = _cours(_MATHS, _INTEG, "11_C7_fonction_integrale.tex")
_INTEG_C8 = _cours(_MATHS, _INTEG, "13_C8_integration_par_parties.tex")
CAPACITY_VERDICTS[_INTEG] = {
    "C1": (PROCEDURAL_UNCOVERED, "Encadrer une intégrale sans la calculer demande d'abord d'étudier les variations pour obtenir le minimum et le maximum EXACTS, puis d'appliquer $m(b-a) \\leq I \\leq M(b-a)$. Le cours donne la propriété et un exemple où l'encadrement est fourni ; l'étape qui coûte — trouver $m$ et $M$ — n'est nommée que dans un encadré d'erreur fréquente.", None),
    "C2": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _fiche(_MATHS, _INTEG, "TSPE-INTEG-ME-001.tex")),
    "C3": (PROCEDURAL_UNCOVERED, "Majorer ou minorer par comparaison des fonctions intégrées est la même démarche que C1 vue par l'autre bout : établir l'inégalité entre fonctions sur l'intervalle, puis l'intégrer. Une seule fiche les sert.", None),
    "C4": (PROCEDURAL_COVERED, "Fiche méthode ME-002 du chapitre.", _fiche(_MATHS, _INTEG, "TSPE-INTEG-ME-002.tex")),
    "C5": (PROCEDURAL_UNCOVERED, "Une suite d'intégrales s'étudie toujours dans le même ordre : signe, monotonie en comparant les intégrandes, relation de récurrence par parties, puis limite par encadrement. Le cours déroule le signe et la récurrence sur un exemple ; la monotonie et la limite, que l'épreuve demande, n'y sont pas.", None),
    "C6": (PROCEDURAL_COVERED, "Le cours interprète l'intégrale d'une vitesse en distance et la valeur moyenne en vitesse moyenne, puis généralise en marge : débit vers volume, puissance vers énergie, densité vers masse. L'interprétation est un savoir, pas un calcul à conduire.", _INTEG_C6),
    "C7": (PROCEDURAL_COVERED, "Démonstration exigible, écrite en entier dans le cours.", _INTEG_C7),
    "C8": (PROCEDURAL_COVERED, "Démonstration exigible de la formule d'intégration par parties, écrite en entier dans le cours.", _INTEG_C8),
}

_COMBI = "TSPE-COMBINATOIRE"
CAPACITY_VERDICTS[_COMBI] = {
    "C1": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _fiche(_MATHS, _COMBI, "TSPE-COMBI-ME-001.tex")),
    "C2": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _fiche(_MATHS, _COMBI, "TSPE-COMBI-ME-001.tex")),
    "C3": (PROCEDURAL_COVERED, "Démonstration exigible. Le cours compte les parties d'un ensemble de deux façons, nomme la technique — preuve par double dénombrement — et avertit contre le réflexe de calculer chaque coefficient.", _cours(_MATHS, _COMBI, "12_C3_somme_coefficients_binomiaux.tex")),
    "C4": (PROCEDURAL_COVERED, "Démonstration exigible, écrite DEUX fois dans le cours comme le programme le demande : par le calcul factoriel, puis par le dénombrement selon l'appartenance d'un élément fixé.", _cours(_MATHS, _COMBI, "13_C4_relation_pascal.tex")),
}

_LOG = "TSPE-LOGARITHME"
CAPACITY_VERDICTS[_LOG] = {
    "C1": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _fiche(_MATHS, _LOG, "TSPE-LOG-ME-001.tex")),
    "C2": (PROCEDURAL_COVERED, "Résoudre un problème contextuel revient à isoler le terme exponentiel puis à appliquer $\\ln$ — la démarche que la fiche M1 pose en cinq étapes, domaine compris. Le cours l'applique à la demi-vie et au seuil de 10 %.", _fiche(_MATHS, _LOG, "TSPE-LOG-ME-001.tex")),
    "C3": (PROCEDURAL_COVERED, "Fiche méthode ME-002 du chapitre.", _fiche(_MATHS, _LOG, "TSPE-LOG-ME-002.tex")),
    "C4": (PROCEDURAL_COVERED, "Fiche méthode ME-002 du chapitre.", _fiche(_MATHS, _LOG, "TSPE-LOG-ME-002.tex")),
}

_PRIMEQ = "TSPE-PRIMITIVES-EQDIFF"
CAPACITY_VERDICTS[_PRIMEQ] = {
    "C1": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _fiche(_MATHS, _PRIMEQ, "TSPE-PRIMEQ-ME-001.tex")),
    "C2": (PROCEDURAL_COVERED, "Fiche méthode ME-002 du chapitre.", _fiche(_MATHS, _PRIMEQ, "TSPE-PRIMEQ-ME-002.tex")),
    "C3": (PROCEDURAL_COVERED, "Fiche méthode ME-002 du chapitre.", _fiche(_MATHS, _PRIMEQ, "TSPE-PRIMEQ-ME-002.tex")),
    "C4": (PROCEDURAL_COVERED, "Démonstration exigible : le cours pose $g = G - F$, montre $g' = 0$, invoque la propriété admise et traite la réciproque. Il avertit même que le résultat suppose un intervalle.", _cours(_MATHS, _PRIMEQ, "10_C4_primitives_constante.tex")),
    "C5": (PROCEDURAL_COVERED, "Démonstration exigible de la résolution complète de $y'=ay$, écrite dans les deux sens, avec la technique — multiplier par $\\mathrm{e}^{-ax}$ — nommée en marge comme transposable à $y'=ay+b$.", _cours(_MATHS, _PRIMEQ, "12_C5_equation_yprime_ay.tex")),
}

_PROBA = "TSPE-PROBABILITES"
_PROBA_ME1 = _fiche(_MATHS, _PROBA, "TSPE-PROBA-ME-001.tex")
CAPACITY_VERDICTS[_PROBA] = {
    "C1": (PROCEDURAL_UNCOVERED, "Modéliser une succession d'épreuves demande de décider ce qu'est une épreuve, si les tirages sont avec ou sans remise, puis de construire l'arbre et d'y appliquer les trois règles. Le cours énonce les règles et traite une urne ; la fiche M1 du chapitre commence à la loi binomiale, en aval. L'arbre lui-même n'a pas sa démarche.", None),
    "C2": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _PROBA_ME1),
    "C3": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _PROBA_ME1),
    "C4": (PROCEDURAL_COVERED, "Fiche méthode ME-001 du chapitre.", _PROBA_ME1),
    "C5": (PROCEDURAL_COVERED, "Démonstration exigible de $P(X=k)$ dans le schéma de Bernoulli, écrite dans le cours.", _cours(_MATHS, _PROBA, "11_C2_C5_schema_bernoulli_binomiale.tex")),
    "C6": (PROCEDURAL_COVERED, "Le cours écrit la décomposition en somme de variables de Bernoulli comme propriété, puis la déroule sur trois dés : décomposer, calculer chaque espérance, sommer.", _cours(_MATHS, _PROBA, "13_C6_C7_esperance_linearite.tex")),
    "C7": (PROCEDURAL_COVERED, "Même passage : la linéarité est appliquée pas à pas sur l'exemple, avec l'avertissement qu'elle ne demande aucune indépendance.", _cours(_MATHS, _PROBA, "13_C6_C7_esperance_linearite.tex")),
    "C8": (PROCEDURAL_COVERED, "Le cours donne l'additivité, la variance d'une Bernoulli, un exemple chiffré, et le contre-exemple $X$ et $-X$ qui montre pourquoi l'indépendance est requise.", _cours(_MATHS, _PROBA, "14_C8_variance.tex")),
    "C9": (PROCEDURAL_COVERED, "Démonstration exigible des formules de l'espérance et de la variance de la loi binomiale, écrite dans le cours.", _cours(_MATHS, _PROBA, "15_C9_esperance_variance_binomiale.tex")),
    "C10": (PROCEDURAL_COVERED, "Le cours applique Bienaymé-Tchebychev à l'échantillonnage, majore $p(1-p)$ par $1/4$ pour s'affranchir d'un $p$ inconnu, et déroule le calcul complet d'une taille d'échantillon jusqu'au nombre.", _cours(_MATHS, _PROBA, "16_CONCLGN_bienayme_tchebychev.tex")),
}


# ── Fiches planifiées hors 1NSI ──────────────────────────────────────────
PLANNED_SHEETS.update({
    _ALGO: [
        ("M1", "Dérouler à la main les parcours d'un arbre binaire", ("C3", "C4")),
        ("M2", "Dérouler à la main un parcours de graphe", ("C7", "C8")),
        ("M3", "Structurer un algorithme diviser pour régner", ("C11",)),
        ("M4", "Passer d'une récursion naïve à une version mémoïsée", ("C12",)),
    ],
    _STRUCT: [
        ("M1", "Spécifier une structure de données par son interface", ("C1",)),
        ("M2", "Modéliser une situation par un graphe", ("C11",)),
        ("M3", "Passer d'une représentation de graphe à l'autre", ("C14",)),
    ],
    _BDD: [
        ("M1", "Repérer les anomalies d'un schéma relationnel", ("C3",)),
        ("M2", "Traduire une question en requête SQL", ("C6", "C7", "C8", "C9")),
    ],
    _LANG: [
        ("M1", "Écrire une fonction récursive et dérouler son arbre d'appels", ("C4", "C5")),
    ],
    _ARCH: [
        ("M1", "Dérouler un ordonnancement de processus", ("C3",)),
        ("M2", "Déterminer la route empruntée selon la métrique du protocole", ("C5",)),
    ],
    _ATT: [
        ("ME-007", "Étudier la loi uniforme continue : densité, répartition, espérance, variance", ("C7",)),
    ],
    _ME: [
        ("ME-006", "Déterminer la limite d'une suite", ("C6",)),
    ],
    _INTEG: [
        ("ME-003", "Encadrer ou comparer une intégrale sans la calculer", ("C1", "C3")),
        ("ME-004", "Étudier une suite d'intégrales", ("C5",)),
    ],
    _PROBA: [
        ("ME-002", "Modéliser par un arbre pondéré et calculer une probabilité", ("C1",)),
    ],
})
