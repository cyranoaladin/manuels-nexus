---
title: "T18 - bareme - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Boyer-Moore"
notion: "Boyer-Moore"
private_data: false
official_program:
  capacities:
    - "T-ALGO-05"
---

# T18 - Barème - Boyer-Moore

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`.
- 3 points tâche `prétraiter dernière position de chaque caractère`.
- 3 points résultat `table : A->2, N->1`.
- 2 points trace de comparaison depuis la droite : `N` du texte comparé à `A` du motif, puis décalage `1`.
- 2 points cas limite `motif absent`.

## Évaluation question par question
- Question 1 : 4 points sur T-ALGO-05 avec résultat `table : A->2, N->1`.
- Question 2 : 4 points sur T-ALGO-05 avec résultat `alignement 0 : N comparé à A -> décalage 1`.
- Question 3 : 4 points sur T-ALGO-05 avec résultat `alignement 1 : ANA trouvé à l'indice 1`.
- Question 4 : 4 points sur T-ALGO-05 avec résultat `motif XYZ absent`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
