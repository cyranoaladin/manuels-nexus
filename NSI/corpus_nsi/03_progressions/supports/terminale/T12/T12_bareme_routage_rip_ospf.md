---
title: "T12 - bareme - routage RIP et OSPF"
level: "terminale"
sequence_id: "T12"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "routage RIP et OSPF"
notion: "routage RIP et OSPF"
private_data: false
official_program:
  capacities:
    - "T-ARCH-03"
---

# T12 - Barème - routage RIP et OSPF

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `RIP A-B-D=2 sauts, A-C-D=2 sauts ; OSPF A-B=5, B-D=5, A-C=2, C-D=9`.
- 3 points tâche `compter sauts RIP`.
- 3 points résultat `RIP : A-B-D et A-C-D ont 2 sauts`.
- 2 points cas limite `égalité exacte`.

## Évaluation question par question
- Question 1 : 4 points sur T-ARCH-03 avec résultat `RIP : A-B-D et A-C-D ont 2 sauts`.
- Question 2 : 4 points sur T-ARCH-03 avec résultat `OSPF : A-B-D coût 10, A-C-D coût 11`.
- Question 3 : 4 points sur T-ARCH-03 avec résultat `panne B-D -> A-C-D coût 11`.
- Question 4 : 4 points sur T-ARCH-03 avec résultat `route inconnue -> rejet ou défaut`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
