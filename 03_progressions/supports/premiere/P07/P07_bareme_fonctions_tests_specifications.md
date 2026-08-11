---
title: "P07 - bareme - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "fonctions, tests et spécifications"
notion: "fonctions, tests et spécifications"
private_data: false
official_program:
  capacities:
    - "P-LANG-01"
    - "P-LANG-02"
    - "P-LANG-03A"
    - "P-LANG-03B"
    - "P-LANG-03C"
    - "P-LANG-04"
    - "P-LANG-05"
---

# P07 - Barème - fonctions, tests et spécifications

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- 3 points tâche `écrire def prix_ttc(prix_ht: float, taux: float) -> float`.
- 3 points résultat `signature complète de prix_ttc`.
- 2 points cas limite `prix_ht=0`.

## Évaluation question par question
- Question 1 : 4 points sur P-LANG-01 avec résultat `signature complète de prix_ttc`.
- Question 2 : 4 points sur P-LANG-02 avec résultat `prix_ttc(80,0.20) -> 96.0`.
- Question 3 : 4 points sur P-LANG-03A avec résultat `prix_ttc(-5,0.20) -> ValueError`.
- Question 4 : 4 points sur P-LANG-03B avec résultat `taux=0 -> résultat 80.0`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
