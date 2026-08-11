---
title: "P13 - bareme - dichotomie, glouton et k-NN"
level: "premiere"
sequence_id: "P13"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "dichotomie, glouton et k-NN"
notion: "dichotomie, glouton et k-NN"
private_data: false
official_program:
  capacities:
    - "P-ALGO-03"
    - "P-ALGO-04"
    - "P-ALGO-05"
---

# P13 - Barème - dichotomie, glouton et k-NN

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `tableau=[4,9,18,23,37,41], cible=37 ; pièces=[10,5,2,1], montant=28 ; voisins=[rouge:1.2, bleu:2.0, rouge:2.4]`.
- 3 points tâche `calculer milieu puis réduire intervalle`.
- 3 points résultat `milieux 18 puis 37 -> trouvé indice 4`.
- 2 points cas limite `cible absente`.

## Évaluation question par question
- Question 1 : 4 points sur P-ALGO-04 avec résultat `milieux 18 puis 37 -> trouvé indice 4`.
- Question 2 : 4 points sur P-ALGO-04 avec résultat `variant V = droite − gauche + 1 décroît, terminaison prouvée`.
- Question 3 : 4 points sur P-ALGO-05 avec résultat `28 = 10+10+5+2+1 (5 pièces, glouton)`.
- Question 4 : 4 points sur P-ALGO-03 avec résultat `rouge (2 voix) vs bleu (1 voix) → classe rouge`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
