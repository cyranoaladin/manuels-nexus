---
title: "T08 - evaluation - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "evaluation"
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

# T08 - Évaluation - BFS, DFS, cycles et chemins

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-ALGO-02A, T-ALGO-02B, T-ALGO-02C, T-ALGO-02D.

## Questions
### Question 1
- Capacité officielle : T-ALGO-02A.
- Énoncé : à partir de `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`, BFS file A puis B,C puis D,E.
- Réponse attendue : BFS -> A,B,C,D,E.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `sommet isolé F`.
### Question 2
- Capacité officielle : T-ALGO-02B.
- Énoncé : à partir de `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`, mémoriser prédécesseurs.
- Réponse attendue : prédécesseurs E<-C<-A donc chemin A-C-E.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `destination absente`.
### Question 3
- Capacité officielle : T-ALGO-02C.
- Énoncé : à partir de `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`, DFS explore un chemin avant retour.
- Réponse attendue : F isolé -> aucun chemin.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `cycle D-C-D`.
### Question 4
- Capacité officielle : T-ALGO-02D.
- Énoncé : à partir de `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`, détecter cycle par sommet gris.
- Réponse attendue : complexité O(V+E).
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `sommet isolé F`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : BFS -> A,B,C,D,E.
- Critère spécifique : BFS file A puis B,C puis D,E et éviter `marquage trop tardif`.
### Corrigé question 2
- Résultat attendu : prédécesseurs E<-C<-A donc chemin A-C-E.
- Critère spécifique : mémoriser prédécesseurs et éviter `BFS confondu avec DFS`.
### Corrigé question 3
- Résultat attendu : F isolé -> aucun chemin.
- Critère spécifique : DFS explore un chemin avant retour et éviter `prédécesseurs oubliés`.
### Corrigé question 4
- Résultat attendu : complexité O(V+E).
- Critère spécifique : détecter cycle par sommet gris et éviter `marquage trop tardif`.

## Erreurs fréquentes et remédiation
- marquage trop tardif.
- BFS confondu avec DFS.
- prédécesseurs oubliés.

## Cas limites travaillés
- sommet isolé F.
- destination absente.
- cycle D-C-D.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `BFS -> A,B,C,D,E`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T08 sur `bfs_dfs_cycles_chemins`.

## Aménagement
- Version aménagée : `T08_version_amenagee_bfs_dfs_cycles_chemins.md` ; consignes découpées et barème conservé.
