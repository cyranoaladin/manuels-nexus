---
title: "T14 - bareme - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "modularité, API, paradigmes et bugs"
notion: "modularité, API, paradigmes et bugs"
private_data: false
official_program:
  capacities:
    - "T-LANG-03A"
    - "T-LANG-03B"
    - "T-LANG-03C"
    - "T-LANG-04A"
    - "T-LANG-04B"
    - "T-LANG-05"
---

# T14 - Barème - modularité, API, paradigmes et bugs

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
- 3 points tâche `définir fonction publique documentée`.
- 3 points résultat `moyenne_temperature(releves) -> 30.0`.
- 2 points cas limite `liste vide`.

## Évaluation question par question
- Question 1 : 4 points sur T-LANG-03A avec résultat `moyenne_temperature(releves) -> 30.0`.
- Question 2 : 4 points sur T-LANG-03B avec résultat `from meteo import moyenne_temperature`.
- Question 3 : 4 points sur T-LANG-03C avec résultat `temperature="31" refusée ou convertie`.
- Question 4 : 4 points sur T-LANG-04A avec résultat `liste vide -> ValueError`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
