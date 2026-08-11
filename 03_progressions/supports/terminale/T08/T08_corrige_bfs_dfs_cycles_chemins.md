---
title: "T08 - corrige - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "corrige"
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

# T08 - Corrigé - BFS, DFS, cycles et chemins

## Corrigé du TD
### Exercice 1
- Réponse attendue : BFS -> A,B,C,D,E.
- Méthode : BFS file A puis B,C puis D,E.
- Cas limite : sommet isolé F.
### Exercice 2
- Réponse attendue : prédécesseurs E<-C<-A donc chemin A-C-E.
- Méthode : mémoriser prédécesseurs.
- Cas limite : destination absente.
### Exercice 3
- Réponse attendue : F isolé -> aucun chemin.
- Méthode : DFS explore un chemin avant retour.
- Cas limite : cycle D-C-D.
### Exercice 4
- Réponse attendue : complexité O(V+E).
- Méthode : détecter cycle par sommet gris.
- Cas limite : sommet isolé F.
### Exercice 5
- Réponse attendue : BFS -> A,B,C,D,E.
- Méthode : BFS file A puis B,C puis D,E.
- Cas limite : destination absente.
### Exercice 6
- Réponse attendue : prédécesseurs E<-C<-A donc chemin A-C-E.
- Méthode : mémoriser prédécesseurs.
- Cas limite : cycle D-C-D.
### Exercice 7
- Réponse attendue : F isolé -> aucun chemin.
- Méthode : DFS explore un chemin avant retour.
- Cas limite : sommet isolé F.
### Exercice 8
- Réponse attendue : complexité O(V+E).
- Méthode : détecter cycle par sommet gris.
- Cas limite : destination absente.

## Corrigé du TP
- Donnée : `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- Résultat principal : BFS -> A,B,C,D,E.
- Résultat secondaire : prédécesseurs E<-C<-A donc chemin A-C-E.

## Corrigé de l évaluation
- Question 1 : BFS -> A,B,C,D,E.
- Question 2 : prédécesseurs E<-C<-A donc chemin A-C-E.
- Question 3 : F isolé -> aucun chemin.
- Question 4 : complexité O(V+E).
