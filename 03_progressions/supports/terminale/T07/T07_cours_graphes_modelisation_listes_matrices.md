---
title: "T07 - cours - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "cours"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "graphes, listes et matrices"
notion: "graphes, listes et matrices"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-05A"
    - "T-STRUCT-05B"
    - "T-STRUCT-05C"
    - "T-STRUCT-05D"
---

# T07 - Cours - graphes, listes et matrices

## Objectifs spécifiques
- Identifier les données utiles de la situation : arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)].
- Employer le vocabulaire : graphe orienté, graphe non orienté, liste d adjacence, matrice d adjacence, degré, voisinage.
- Produire une trace, une table, une valeur ou un pseudo-code vérifiable.

## Capacités officielles
- T-STRUCT-05A.
- T-STRUCT-05B.
- T-STRUCT-05C.
- T-STRUCT-05D.

## Situation-problème
arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]

## À savoir
- graphe orienté.
- graphe non orienté.
- liste d adjacence.
- matrice d adjacence.
- degré.
- voisinage.
- coût mémoire.

## Méthodes
- lister voisins sortants.
- remplir matrice 0/1.
- calculer degré sortant.
- choisir liste pour graphe peu dense.

## Exemples corrigés
### Exemple corrigé 1
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Méthode : lister voisins sortants.
- Résultat attendu : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Contrôle : capacité T-STRUCT-05A et cas limite `sommet isolé E`.
### Exemple corrigé 2
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Méthode : remplir matrice 0/1.
- Résultat attendu : ligne A : colonnes B et C valent 1.
- Contrôle : capacité T-STRUCT-05B et cas limite `boucle A->A`.
### Exemple corrigé 3
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Méthode : écrire l'implémentation par listes de successeurs (T-STRUCT-05C).
- Résultat attendu : `graphe = {"A": ["B","C"], "B": ["D"], "C": ["D"], "D": ["B"], "E": []}`. On crée un dictionnaire où chaque sommet pointe vers la liste de ses successeurs. L'exercice 3bis du TD sert de point de départ.
- Contrôle : capacité T-STRUCT-05C et cas limite `sommet isolé E → liste vide`.
### Exemple corrigé 4
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Méthode : passer d'une représentation à une autre (T-STRUCT-05D).
- Résultat attendu : convertir la liste de successeurs en matrice d'adjacence 5×5 (A,B,C,D,E). Ligne A : colonnes B et C valent 1. Ligne D : colonne B vaut 1. Ligne E : toutes les colonnes valent 0. Inversement, depuis la matrice, reconstruire les listes de successeurs.
- Contrôle : capacité T-STRUCT-05D et cas limite `sommet isolé E → ligne de zéros dans la matrice et liste vide dans le dictionnaire`.

## Cas limites
- sommet isolé E.
- boucle A->A.
- arête non orientée.

## Erreurs fréquentes
- voisin entrant confondu.
- sommet isolé oublié.
- coût mémoire ignoré.

## Exercices intégrés
1. Identifier les données utiles dans `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
2. Appliquer : lister voisins sortants.
3. Appliquer : remplir matrice 0/1.
4. Décider le cas limite `sommet isolé E`.

## Critères de réussite observables
- Une capacité parmi T-STRUCT-05A, T-STRUCT-05B, T-STRUCT-05C, T-STRUCT-05D est citée et utilisée.
- Le résultat attendu est explicite : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Le cas limite `boucle A->A` est tranché.

## Lien avec la progression
- Séance : T07-S1 à T07-S4.
- TD : `T07_TD_graphes_modelisation_listes_matrices.md`.
- TP : `T07_tp_graphes_modelisation_listes_matrices.md`.
- Évaluation : `T07_evaluation_graphes_modelisation_listes_matrices.md`.

## Renforcement explicatif ciblé

Ce cours doit être lu comme une progression sur graphes et représentations. La notion ne se réduit pas à une liste de mots : on part d'une situation observable, on nomme les objets manipulés, puis on applique une méthode vérifiable sur un cas limité avant de généraliser.

### Savoir disciplinaire
- Vocabulaire à maîtriser : sommet, arête, graphe orienté, liste d’adjacence, matrice d’adjacence, degré.
- Capacités reliées : T-STRUCT-05A, T-STRUCT-05B, T-STRUCT-05C, T-STRUCT-05D.
- Le savoir attendu consiste à expliquer le rôle de chaque objet avant de l'utiliser dans un exercice.

### Savoir-faire et méthodes opérationnelles
- traduire une situation en sommets et arêtes.
- passer de la liste d’adjacence à la matrice.
- comparer le coût mémoire des deux représentations.

### Erreurs fréquentes spécifiques
- Un élève peut oublier la symétrie d’un graphe non orienté ; la correction consiste à reprendre la définition puis à refaire la trace sur un exemple minimal.
- Un élève peut confondre voisin et successeur ; la correction consiste à isoler le cas limite avant de recommencer le calcul ou le raisonnement.
- Un élève peut compter deux fois une arête ; la correction consiste à vérifier le résultat avec une donnée différente.

### Cas limites à contrôler
- Cas minimal : une donnée vide, un seul élément, une route absente ou une structure sans enfant selon la notion.
- Cas ambigu : doublon, égalité, absence de correspondance ou choix local non optimal.

### Synthèse savoir / savoir-faire / méthode
- Savoir : définir précisément les objets de graphes et représentations.
- Savoir-faire : appliquer une méthode contrôlable à une donnée explicite.
- Méthode : annoncer la donnée, exécuter les étapes dans l'ordre, puis vérifier le résultat par un cas limite.
