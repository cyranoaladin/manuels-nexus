#!/usr/bin/env python3
"""Plan des deux banques d'epreuve TNSI, ecrit AVANT le moindre sujet.

POURQUOI UN PLAN D'ABORD. Une banque ecrite sans plan produit dix-huit
exercices qui portent tous sur les arbres et le SQL, parce que ce sont les
sujets les plus faciles a ecrire. Le plan fixe ce que la banque doit couvrir,
et l'audit verifie ensuite que ce qui a ete ecrit correspond — pas l'inverse.

AUTORITE. Note de service MENE2516123N, BO n°31 du 21 aout 2025, epreuve de
specialite NSI a compter de la session 2026.

  ecrit     3 h 30, TROIS exercices independants, note /20, poids 0,75
  pratique  1 h, resolution de problemes et programmation sur machine,
            note /20, poids 0,25

Les deux notes forment une moyenne ponderee. Le « 15 + 5 » qu'on lit parfois
est une explication pedagogique de la contribution, pas une echelle : ne pas
l'inscrire comme bareme.

CE QUE LE PLAN N'AUTORISE PAS. Aucun sujet officiel n'est reproduit ni
paraphrase de pres. Tout le contenu est original, marque
NEXUS_ORIGINAL_AUTHORING, et porte la mention
ORIGINAL_NEXUS_TRAINING_MATERIAL_NOT_OFFICIAL_EXAM_CONTENT.

STRUCTURE DE LA BANQUE ECRITE. Six sujets de trois exercices independants,
soit dix-huit exercices. « Independants » est une contrainte forte et
verifiee : dans un meme sujet, aucun exercice ne peut dependre d'un resultat,
d'une definition ou d'une structure introduite par un autre. Un candidat qui
echoue au premier doit pouvoir traiter les deux suivants.

Chaque sujet couvre trois DOMAINES distincts, pour qu'un candidat fort sur un
seul domaine ne puisse pas obtenir toute la note.

STRUCTURE DE LA BANQUE PRATIQUE. Huit situations d'une heure, chacune
faisable sur machine a partir d'un document fourni. Chaque situation porte son
propre jeu de tests, executable depuis un repertoire quelconque : une banque
pratique qui ne tourne que dans l'arborescence du depot n'est pas utilisable
en salle d'examen.
"""

from __future__ import annotations

AUTHORITY = {
    "official_ref": "MENE2516123N",
    "bo": "BO n°31 du 21 août 2025",
    "note_date": "2025-07-04",
    "applicable_from_session": 2026,
    "ecrit": {"duree_h": 3.5, "exercices": 3, "raw_scale": 20, "weight": 0.75},
    "pratique": {"duree_h": 1.0, "raw_scale": 20, "weight": 0.25},
}

DOMAINS = {
    "STRUCTURES": "TNSI-STRUCTURES-DONNEES",
    "ALGORITHMIQUE": "TNSI-ALGORITHMIQUE",
    "BASES_DE_DONNEES": "TNSI-BASES-DE-DONNEES",
    "LANGAGES": "TNSI-LANGAGES-ET-PROGRAMMATION",
    "ARCHITECTURE": "TNSI-ARCHITECTURES-MATERIELLES-SY",
    "HISTOIRE": "TNSI-HISTOIRE-INFORMATIQUE",
}

# `TNSI-PROJET` n'apparait dans aucun sujet, et ce n'est pas un oubli. Sa
# decision d'evaluation est PROJECT_ASSESSMENT : le chapitre porte le projet
# annuel, evalue par sa grille criteriee. L'epreuve ecrite de specialite ne
# demande a personne de « conduire un projet » sur copie. Y placer un exercice
# serait fabriquer du contenu pour un compteur.
ASSESSED_ELSEWHERE = {
    "TNSI-PROJET": (
        "ASSESSMENT_MODE = PROJECT_ASSESSMENT, décision humaine du "
        "2026-09-06 : le chapitre est évalué par le projet annuel et sa "
        "grille critériée, pas par une épreuve sur copie."
    ),
}

# Six sujets, trois exercices chacun, trois domaines distincts par sujet.
# `capacites` cite les references officielles du contrat de chapitre.
WRITTEN_SUBJECTS: list[dict] = [
    {
        "subject_id": "TNSI-ECRIT-S1",
        "titre": "Arbres, files de priorité et journal d'événements",
        "exercices": [
            {"id": "TNSI-ECRIT-S1-EX1", "domain": "STRUCTURES",
             "titre": "Un arbre binaire de recherche de mesures",
             "capacites": ["T-STRUCT-04A", "T-STRUCT-04B"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S1-EX2", "domain": "ALGORITHMIQUE",
             "titre": "Parcours en largeur d'un réseau de capteurs",
             "capacites": ["T-ALGO-02A", "T-ALGO-02D"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S1-EX3", "domain": "BASES_DE_DONNEES",
             "titre": "Journal d'événements et requêtes d'agrégat",
             "capacites": ["T-BDD-03A", "T-BDD-03F"], "duree_min": 70},
        ],
    },
    {
        "subject_id": "TNSI-ECRIT-S2",
        "titre": "Piles, récursivité et ordonnancement",
        "exercices": [
            {"id": "TNSI-ECRIT-S2-EX1", "domain": "STRUCTURES",
             "titre": "Une pile pour évaluer une expression postfixée",
             "capacites": ["T-STRUCT-03A", "T-STRUCT-03B"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S2-EX2", "domain": "LANGAGES",
             "titre": "Récursivité et coût d'un calcul répété",
             "capacites": ["T-LANG-02A", "T-LANG-02B"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S2-EX3", "domain": "ARCHITECTURE",
             "titre": "Ordonnancement de trois processus",
             "capacites": ["T-ARCH-02A", "T-ARCH-02B"], "duree_min": 70},
        ],
    },
    {
        "subject_id": "TNSI-ECRIT-S3",
        "titre": "Graphes, jointures et effets de bord",
        "exercices": [
            {"id": "TNSI-ECRIT-S3-EX1", "domain": "ALGORITHMIQUE",
             "titre": "Détecter un cycle dans un graphe de dépendances",
             "capacites": ["T-ALGO-02B", "T-ALGO-02C"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S3-EX2", "domain": "BASES_DE_DONNEES",
             "titre": "Deux tables, une jointure, une contrainte",
             "capacites": ["T-BDD-01B", "T-BDD-03D"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S3-EX3", "domain": "LANGAGES",
             "titre": "Un effet de bord qui fausse un résultat",
             "capacites": ["T-LANG-05", "T-LANG-04A"], "duree_min": 70},
        ],
    },
    {
        "subject_id": "TNSI-ECRIT-S4",
        "titre": "Files, diviser pour régner et adressage",
        "exercices": [
            {"id": "TNSI-ECRIT-S4-EX1", "domain": "STRUCTURES",
             "titre": "Une file d'attente à deux piles",
             "capacites": ["T-STRUCT-03C", "T-STRUCT-02A"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S4-EX2", "domain": "ALGORITHMIQUE",
             "titre": "Diviser pour régner sur un tableau trié",
             "capacites": ["T-ALGO-03", "T-ALGO-04"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S4-EX3", "domain": "ARCHITECTURE",
             "titre": "Routage, coût d'un chemin et confidentialité",
             "capacites": ["T-ARCH-03", "T-ARCH-04A", "T-ARCH-04B"],
             "duree_min": 70},
        ],
    },
    {
        "subject_id": "TNSI-ECRIT-S5",
        "titre": "Classes, arbres de recherche et agrégats",
        "exercices": [
            {"id": "TNSI-ECRIT-S5-EX1", "domain": "STRUCTURES",
             "titre": "Une classe pour un stock, interface et implémentation",
             "capacites": ["T-STRUCT-01A", "T-STRUCT-02B"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S5-EX2", "domain": "ALGORITHMIQUE",
             "titre": "Insertion et recherche dans un arbre binaire de recherche",
             "capacites": ["T-ALGO-01E", "T-ALGO-01F"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S5-EX3", "domain": "BASES_DE_DONNEES",
             "titre": "Agrégats et regroupements sur un catalogue",
             "capacites": ["T-BDD-03E", "T-BDD-03G"], "duree_min": 70},
        ],
    },
    {
        "subject_id": "TNSI-ECRIT-S6",
        "titre": "Matrices d'adjacence, tests et repères historiques",
        "exercices": [
            {"id": "TNSI-ECRIT-S6-EX1", "domain": "STRUCTURES",
             "titre": "Deux représentations d'un même graphe",
             "capacites": ["T-STRUCT-05B", "T-STRUCT-05D"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S6-EX2", "domain": "LANGAGES",
             "titre": "Spécifier puis tester une fonction de fusion",
             "capacites": ["T-LANG-03A", "T-LANG-03C"], "duree_min": 70},
            {"id": "TNSI-ECRIT-S6-EX3", "domain": "HISTOIRE",
             "titre": "Situer une évolution technique et ses conséquences",
             "capacites": ["T-HIST-01A", "T-HIST-01B"], "duree_min": 70},
        ],
    },
]

# Huit situations pratiques d'une heure, chacune sur machine, a partir d'un
# document fourni. `fichiers_fournis` est le document remis au candidat.
PRACTICAL_SITUATIONS: list[dict] = [
    {"id": "TNSI-PRATIQUE-P1", "domain": "ARCHITECTURE",
     "titre": "Simuler un ordonnancement par tourniquet",
     "capacites": ["T-ARCH-02A", "T-ARCH-02B"], "duree_min": 60},
    {"id": "TNSI-PRATIQUE-P2", "domain": "ALGORITHMIQUE",
     "titre": "Parcours en profondeur d'un graphe fourni",
     "capacites": ["T-ALGO-02B"], "duree_min": 60},
    {"id": "TNSI-PRATIQUE-P3", "domain": "ALGORITHMIQUE",
     "titre": "Taille et hauteur d'un arbre binaire",
     "capacites": ["T-ALGO-01A", "T-ALGO-01B"], "duree_min": 60},
    {"id": "TNSI-PRATIQUE-P4", "domain": "BASES_DE_DONNEES",
     "titre": "Trois requêtes sur une base fournie",
     "capacites": ["T-BDD-03B", "T-BDD-03C"], "duree_min": 60},
    {"id": "TNSI-PRATIQUE-P5", "domain": "LANGAGES",
     "titre": "Corriger une fonction récursive et la tester",
     "capacites": ["T-LANG-02A", "T-LANG-03B"], "duree_min": 60},
    {"id": "TNSI-PRATIQUE-P6", "domain": "STRUCTURES",
     "titre": "Implémenter une file à partir de son interface",
     "capacites": ["T-STRUCT-03C"], "duree_min": 60},
    {"id": "TNSI-PRATIQUE-P7", "domain": "ALGORITHMIQUE",
     "titre": "Un algorithme glouton et son contre-exemple",
     "capacites": ["T-ALGO-05"], "duree_min": 60},
    {"id": "TNSI-PRATIQUE-P8", "domain": "STRUCTURES",
     "titre": "Passer d'une matrice d'adjacence aux listes de successeurs",
     "capacites": ["T-STRUCT-05C", "T-STRUCT-05D"], "duree_min": 60},
]

# Les cinq etapes exigees pour chaque exercice ecrit. Un exercice qui n'a pas
# franchi les cinq n'est pas terminé, meme s'il est lisible.
# La banque pratique n'attend rien de deux chapitres, et la raison est
# ecrite : elle sera verifiee, pas crue.
PRACTICAL_NOT_APPLICABLE = {
    "TNSI-PROJET": (
        "ASSESSMENT_MODE = PROJECT_ASSESSMENT : le chapitre est évalué par le "
        "projet annuel et sa grille critériée."
    ),
    "TNSI-HISTOIRE-INFORMATIQUE": (
        "L'épreuve pratique est définie par MENE2516123N comme « résolution "
        "de problèmes et programmation sur machine ». Les deux capacités du "
        "chapitre — situer une évolution dans le temps, en expliquer les "
        "conséquences — ne se programment pas. Elles sont évaluées à l'écrit, "
        "par TNSI-ECRIT-S6-EX3."
    ),
}

AUTHORING_STEPS = (
    "REDACTION",        # l'enonce, original
    "ORACLE",           # un bloc executable qui verifie les reponses
    "CORRECTION",       # le corrige, avec le bareme
    "CRITIQUE",         # les pieges, ce qui peut etre mal compris
    "PEDAGOGIE",        # ce que l'exercice enseigne, et a qui il s'adresse
)
