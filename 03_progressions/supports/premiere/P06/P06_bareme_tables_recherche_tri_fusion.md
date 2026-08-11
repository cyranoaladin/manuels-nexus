---
title: "P06 - bareme - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "recherche, tri et fusion de tables"
notion: "recherche, tri et fusion de tables"
private_data: false
official_program:
  capacities:
    - "P-TABLE-03"
    - "P-TABLE-04"
---

# P06 - Barème - recherche, tri et fusion de tables

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`.
- 3 points tâche `chercher la première ligne id=17`.
- 3 points résultat `première ligne id=17 -> Ada/robot`.
- 2 points cas limite `table vide`.

## Évaluation question par question
- Question 1 : 4 points sur P-TABLE-03 avec résultat `première ligne id=17 -> Ada/robot`.
- Question 2 : 4 points sur P-TABLE-04 avec résultat `doublon id=17 -> Ada/python signalé`.
- Question 3 : 4 points sur P-TABLE-03 avec résultat `tri -> Ada/python, Ada/robot, Linus/web`.
- Question 4 : 4 points sur P-TABLE-04 avec résultat `fusion -> erreur id_absent=9`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
