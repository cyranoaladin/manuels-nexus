---
title: "T07 - bareme - graphes, listes et matrices"
level: "terminale"
sequence_id: "T07"
document_type: "bareme"
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

# T07 - Barème - graphes, listes et matrices

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `arcs=[(A,B),(A,C),(B,D),(C,D),(D,B)]`.
- 3 points tâche `lister voisins sortants`.
- 3 points résultat `A -> [B,C], B -> [D], C -> [D], D -> [B]`.
- 2 points cas limite `sommet isolé E`.

## Évaluation question par question
- Question 1 : 4 points sur T-STRUCT-05A avec résultat `A -> [B,C], B -> [D], C -> [D], D -> [B]`.
- Question 2 : 4 points sur T-STRUCT-05B avec résultat `ligne A : colonnes B et C valent 1`.
- Question 3 : 4 points sur T-STRUCT-05C avec résultat `matrice 4x4 -> 16 cases`.
- Question 4 : 4 points sur T-STRUCT-05D avec résultat `sommet E isolé -> liste vide`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
