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

## Objectif opérationnel
Transformer une liste d'arcs en liste d'adjacence et en matrice d'adjacence, puis interpréter les voisins selon l'orientation du graphe.

Le TP sépare volontairement trois représentations :
- les arcs d'entrée, qui sont des couples ordonnés ;
- la liste d'adjacence, qui donne les voisins sortants ;
- la matrice d'adjacence, qui indique `1` quand un arc existe.

Un sommet isolé doit être conservé avec une liste vide et une ligne de matrice remplie de zéros.

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

## Trace attendue détaillée
Sommets retenus : `A`, `B`, `C`, `D`, `E`.

Construction de la liste d'adjacence :
1. avec `(A,B)`, ajouter `B` aux voisins sortants de `A` ;
2. avec `(A,C)`, ajouter `C` aux voisins sortants de `A` ;
3. avec `(B,D)`, ajouter `D` aux voisins sortants de `B` ;
4. avec `(C,D)`, ajouter `D` aux voisins sortants de `C` ;
5. avec `(D,B)`, ajouter `B` aux voisins sortants de `D` ;
6. le sommet `E` reste présent avec `[]`.

Résultat attendu :
- `A -> [B, C]`
- `B -> [D]`
- `C -> [D]`
- `D -> [B]`
- `E -> []`

Construction de la matrice avec l'ordre `A, B, C, D, E` :
- ligne `A` : `[0, 1, 1, 0, 0]` ;
- ligne `B` : `[0, 0, 0, 1, 0]` ;
- ligne `C` : `[0, 0, 0, 1, 0]` ;
- ligne `D` : `[0, 1, 0, 0, 0]` ;
- ligne `E` : `[0, 0, 0, 0, 0]`.

## Exigences sur le code
- La fonction `liste_adjacence` doit créer une entrée pour chaque sommet annoncé, même isolé.
- La fonction `matrice_adjacence` doit respecter l'ordre des sommets fourni.
- Un arc `(D,B)` ne doit pas créer automatiquement `(B,D)` : le graphe est orienté.
- Le degré sortant de `A` vaut `2`.
- Le degré sortant de `E` vaut `0`.

## Vérifications manuelles avant tests
- `voisins["A"] == ["B", "C"]`.
- `voisins["E"] == []`.
- `matrice[0] == [0, 1, 1, 0, 0]`.
- `matrice[4] == [0, 0, 0, 0, 0]`.
- Le coût mémoire de la matrice est expliqué comme proportionnel à `n^2`.



## Protocole de validation complémentaire
1. Préparer un jeu nominal propre à T07 et noter la sortie attendue avant exécution.
2. Préparer un cas limite distinct et expliquer pourquoi il doit être accepté ou refusé.
3. Exécuter le starter : il doit échouer sur au moins un test complet, ce qui confirme que le travail élève reste à produire.
4. Exécuter le corrigé professeur : il doit produire exactement les valeurs attendues dans les tests.
5. Comparer la trace obtenue avec la consigne : chaque étape doit être justifiée par une donnée du sujet.
6. Noter l'erreur fréquente observée et choisir la remédiation ciblée dans le support associé.

## Livrable vérifiable complémentaire
- Fichier élève complété avec les fonctions demandées dans le TP.
- Trace courte indiquant entrée, traitement, sortie et cas limite.
- Capture textuelle des tests attendus : nominal OK, cas limite OK, entrée invalide traitée.
- Commentaire final indiquant la capacité officielle réellement travaillée.


## Assets Python
- Starter élève : `code/T07_starter_graphes_modelisation_listes_matrices.py`.
- Tests attendus : `code/T07_tests_attendus_graphes_modelisation_listes_matrices.py`.
- Corrigé professeur : `code/T07_corrige_professeur_graphes_modelisation_listes_matrices.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.
