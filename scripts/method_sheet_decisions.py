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
