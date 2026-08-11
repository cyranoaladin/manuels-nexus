---
title: "T08 - tp - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "BFS, DFS, cycles et chemins"
notion: "BFS, DFS, cycles et chemins"
private_data: false
official_program:
  capacities:
    - "T-ALGO-02A"
    - "T-ALGO-02B"
    - "T-ALGO-02C"
    - "T-ALGO-02D"
---

# T08 - TP - BFS, DFS, cycles et chemins

## Statut du TP
TP exécutable : utiliser les fichiers du dossier `code/` (T08_starter_bfs_dfs_cycles_chemins.py, T08_tests_attendus_bfs_dfs_cycles_chemins.py, T08_corrige_professeur_bfs_dfs_cycles_chemins.py).

## Donnée fournie
`adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : BFS file A puis B,C puis D,E.
3. Réaliser : mémoriser prédécesseurs.
4. Tester le cas limite `sommet isolé F`.
5. Produire le livrable : BFS -> A,B,C,D,E.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `BFS -> A,B,C,D,E`.
- 2 points : cas limite `sommet isolé F`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
### Corrigé question 2
Résultat attendu : BFS -> A,B,C,D,E.
### Corrigé question 3
Résultat attendu : `pred = {"B":"A", "C":"A", "D":"B", "E":"C"}` donc chemin reconstruit `A -> C -> E`.
### Corrigé question 4
Résultat attendu : `sommet isolé F` traité sans ambiguïté.

## Liens
- TD lié : `T08_TD_bfs_dfs_cycles_chemins.md`.
- Évaluation liée : `T08_evaluation_bfs_dfs_cycles_chemins.md`.

## Cas limites travaillés
- sommet isolé F.
- destination absente.
- cycle D-C-D.

## Erreurs fréquentes
- marquage trop tardif.
- BFS confondu avec DFS.
- prédécesseurs oubliés.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `BFS -> A,B,C,D,E`.
- Au moins un cas limite de la section précédente est décidé.



## Assets Python
- Starter élève : `code/T08_starter_bfs_dfs_cycles_chemins.py`.
- Tests attendus : `code/T08_tests_attendus_bfs_dfs_cycles_chemins.py`.
- Corrigé professeur : `code/T08_corrige_professeur_bfs_dfs_cycles_chemins.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.


## Précision DFS
- DFS avec pile explicite ou récursion : le parcours empile les voisins non marqués, ou bien appelle récursivement chaque voisin non visité.
- La trace indique pour chaque sommet son prédécesseur et l’ordre de dépilement ou de retour récursif.
