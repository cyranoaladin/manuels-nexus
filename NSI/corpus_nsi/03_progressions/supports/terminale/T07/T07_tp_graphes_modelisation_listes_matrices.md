---
title: "T07 - tp - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "tp"
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

# T07 - TP - graphes, listes et matrices

## Statut du TP
TP exécutable : utiliser les fichiers du dossier `code/` (T07_starter_graphes_modelisation_listes_matrices.py, T07_tests_attendus_graphes_modelisation_listes_matrices.py, T07_corrige_professeur_graphes_modelisation_listes_matrices.py).

## Donnée fournie
`arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : lister voisins sortants.
3. Réaliser : remplir matrice 0/1.
4. Tester le cas limite `sommet isolé E`.
5. Produire le livrable : A -> [B,C], B -> [D], C -> [D], D -> [B].

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `A -> [B,C], B -> [D], C -> [D], D -> [B]`.
- 2 points : cas limite `sommet isolé E`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
### Corrigé question 2
Résultat attendu : A -> [B,C], B -> [D], C -> [D], D -> [B].
### Corrigé question 3
Résultat attendu : ligne A : colonnes B et C valent 1.
### Corrigé question 4
Résultat attendu : `sommet isolé E` traité sans ambiguïté.

## Liens
- TD lié : `T07_TD_graphes_modelisation_listes_matrices.md`.
- Évaluation liée : `T07_evaluation_graphes_modelisation_listes_matrices.md`.

## Cas limites travaillés
- sommet isolé E.
- boucle A->A.
- arête non orientée.

## Erreurs fréquentes
- voisin entrant confondu.
- sommet isolé oublié.
- coût mémoire ignoré.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `A -> [B,C], B -> [D], C -> [D], D -> [B]`.
- Au moins un cas limite de la section précédente est décidé.



## Assets Python
- Starter élève : `code/T07_starter_graphes_modelisation_listes_matrices.py`.
- Tests attendus : `code/T07_tests_attendus_graphes_modelisation_listes_matrices.py`.
- Corrigé professeur : `code/T07_corrige_professeur_graphes_modelisation_listes_matrices.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.
