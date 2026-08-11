---
title: "T07 - corrige - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "corrige"
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

# T07 - Corrigé - graphes, listes et matrices

## Corrigé du TD
### Exercice 1
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Méthode : lister voisins sortants.
- Cas limite : sommet isolé E.
### Exercice 2
- Réponse attendue : ligne A : colonnes B et C valent 1.
- Méthode : remplir matrice 0/1.
- Cas limite : boucle A->A.
### Exercice 3
- Réponse attendue : matrice 4x4 -> 16 cases.
- Méthode : calculer degré sortant.
- Cas limite : arête non orientée.
### Exercice 3bis
- Capacité mobilisée : T-STRUCT-05C.
- Réponse attendue : `{A: [B, C], B: [D], C: [D], D: [B]}`.
- Méthode : pour chaque arc (u, v) dans arcs, ajouter v à la liste graphe[u] ; initialiser chaque sommet avec une liste vide avant parcours.
- Cas limite : sommet isolé (pas d'arc sortant) → sa clé existe dans le dictionnaire avec une liste vide.
### Exercice 4
- Réponse attendue : sommet E isolé -> liste vide.
- Méthode : choisir liste pour graphe peu dense.
- Cas limite : sommet isolé E.
### Exercice 5
- Réponse attendue : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Méthode : lister voisins sortants.
- Cas limite : boucle A->A.
### Exercice 6
- Réponse attendue : ligne A : colonnes B et C valent 1.
- Méthode : remplir matrice 0/1.
- Cas limite : arête non orientée.
### Exercice 7
- Réponse attendue : matrice 4x4 -> 16 cases.
- Méthode : calculer degré sortant.
- Cas limite : sommet isolé E.
### Exercice 8
- Réponse attendue : sommet E isolé -> liste vide.
- Méthode : choisir liste pour graphe peu dense.
- Cas limite : boucle A->A.

## Corrigé du TP
- Donnée : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- Résultat principal : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Résultat secondaire : ligne A : colonnes B et C valent 1.

## Corrigé de l évaluation
- Question 1 : A -> [B,C], B -> [D], C -> [D], D -> [B].
- Question 2 : ligne A : colonnes B et C valent 1.
- Question 3 : matrice 4x4 -> 16 cases.
- Question 4 : sommet E isolé -> liste vide.
