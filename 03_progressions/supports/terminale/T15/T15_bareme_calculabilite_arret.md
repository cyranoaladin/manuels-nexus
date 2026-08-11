---
title: "T15 - bareme - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "calculabilité, programme comme donnée et arrêt"
notion: "calculabilité, programme comme donnée et arrêt"
private_data: false
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
---

# T15 - Barème - calculabilité, programme comme donnée et arrêt

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- 3 points tâche `encoder un programme comme texte`.
- 3 points résultat `source="print(1)" est une donnée`.
- 2 points cas limite `programme très long mais fini`.

## Évaluation question par question
- Question 1 : 4 points sur T-LANG-01A avec résultat `source="print(1)" est une donnée`.
- Question 2 : 4 points sur T-LANG-01B avec résultat `arrete(P,x) renvoie True ou False`.
- Question 3 : 4 points sur T-LANG-01C avec résultat `Q boucle si arrete(Q,Q) dit True`.
- Question 4 : 4 points sur T-LANG-01A avec résultat `contradiction donc oracle impossible`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
