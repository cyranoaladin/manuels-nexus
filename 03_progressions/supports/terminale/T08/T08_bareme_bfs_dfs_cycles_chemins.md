---
title: "T08 - bareme - BFS, DFS, cycles et chemins"
level: "terminale"
sequence_id: "T08"
document_type: "bareme"
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

# T08 - Barème - BFS, DFS, cycles et chemins

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `adj={A:[B,C], B:[D], C:[E], D:[C], E:[]}`.
- 3 points tâche `BFS file A puis B,C puis D,E`.
- 3 points résultat `BFS -> A,B,C,D,E`.
- 2 points cas limite `sommet isolé F`.

## Évaluation question par question
- Question 1 : 4 points sur T-ALGO-02A avec résultat `BFS -> A,B,C,D,E`.
- Question 2 : 4 points sur T-ALGO-02B avec résultat `prédécesseurs E<-C<-A donc chemin A-C-E`.
- Question 3 : 4 points sur T-ALGO-02C avec résultat `F isolé -> aucun chemin`.
- Question 4 : 4 points sur T-ALGO-02D avec résultat `complexité O(V+E)`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
