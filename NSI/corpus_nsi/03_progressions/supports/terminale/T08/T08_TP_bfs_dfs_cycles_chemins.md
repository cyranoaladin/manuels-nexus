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

## Objectif opérationnel
Programmer un parcours BFS avec file, un parcours DFS avec pile ou récursion, puis reconstruire un chemin à partir des prédécesseurs.

Le TP vérifie explicitement quatre idées :
- un sommet est marqué dès son entrée dans la file ou la pile ;
- BFS explore par distance croissante depuis la source ;
- DFS suit une branche avant de revenir ;
- le dictionnaire des prédécesseurs permet de reconstruire un chemin réel.

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

## Trace attendue détaillée
BFS depuis `A` sur `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}` :
1. file initiale `[A]`, marqués `{A}` ;
2. sortir `A`, enfiler `B` puis `C`, prédécesseurs `B:A`, `C:A` ;
3. sortir `B`, enfiler `D`, prédécesseur `D:B` ;
4. sortir `C`, enfiler `E`, prédécesseur `E:C` ;
5. sortir `D`, le voisin `C` est déjà marqué ;
6. sortir `E`, aucun voisin.

Ordre BFS attendu : `[A, B, C, D, E]`.
Prédécesseurs attendus : `{"B": "A", "C": "A", "D": "B", "E": "C"}`.
Chemin reconstruit de `A` à `E` : `A -> C -> E`.

DFS possible depuis `A` en parcourant les voisins dans l'ordre donné :
1. visiter `A` ;
2. suivre `B`, puis `D` ;
3. depuis `D`, le voisin `C` n'est pas encore visité, visiter `C` ;
4. depuis `C`, visiter `E` ;
5. revenir car `E` n'a pas de voisin.

Ordre DFS accepté : `[A, B, D, C, E]`.

## Cas de cycle contrôlé
Sur le graphe `A:[B], B:[C], C:[A]`, le cycle annoncé est `A -> B -> C -> A`.
Le programme doit détecter que `A` est rencontré alors qu'il est déjà dans la pile active.
Le même sommet déjà marqué mais hors pile active ne suffit pas à conclure à un cycle orienté.

## Exigences sur le code
- `bfs(adj, "A")` retourne l'ordre et les prédécesseurs, pas seulement une impression.
- `reconstruire_chemin(pred, "A", "E")` retourne `["A", "C", "E"]`.
- Une destination absente retourne une liste vide ou déclenche une erreur documentée.
- Un sommet isolé `F` produit l'ordre `[F]` si `F` existe dans le graphe.
- La complexité est expliquée comme proportionnelle à `|S| + |A|`.



## Protocole de validation complémentaire
1. Préparer un jeu nominal propre à T08 et noter la sortie attendue avant exécution.
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
- Starter élève : `code/T08_starter_bfs_dfs_cycles_chemins.py`.
- Tests attendus : `code/T08_tests_attendus_bfs_dfs_cycles_chemins.py`.
- Corrigé professeur : `code/T08_corrige_professeur_bfs_dfs_cycles_chemins.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.


## Précision DFS
- DFS avec pile explicite ou récursion : le parcours empile les voisins non marqués, ou bien appelle récursivement chaque voisin non visité.
- La trace indique pour chaque sommet son prédécesseur et l’ordre de dépilement ou de retour récursif.
