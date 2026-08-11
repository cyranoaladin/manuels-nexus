---
title: "T11 - bareme - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "bareme"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "SoC, processus, ordonnancement et interblocage"
notion: "SoC, processus, ordonnancement et interblocage"
private_data: false
official_program:
  capacities:
    - "T-ARCH-01"
    - "T-ARCH-02A"
    - "T-ARCH-02B"
    - "T-ARCH-02C"
---

# T11 - Barème - SoC, processus, ordonnancement et interblocage

## TD
- 8 exercices : 1 point donnée, 1 point méthode, 1 point résultat, 1 point cas limite.

## TP
- 2 points donnée `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- 3 points tâche `identifier CPU mémoire interfaces`.
- 3 points résultat `P1 20 ms, P2 20 ms, P1 20 ms`.
- 2 points cas limite `un seul processus prêt`.

## Évaluation question par question
- Question 1 : 4 points sur T-ARCH-01 avec résultat `P1 20 ms, P2 20 ms, P1 20 ms`.
- Question 2 : 4 points sur T-ARCH-02A avec résultat `P1 attend journal et P2 attend camera`.
- Question 3 : 4 points sur T-ARCH-02B avec résultat `CPU + mémoire + contrôleur caméra intégrés`.
- Question 4 : 4 points sur T-ARCH-02C avec résultat `processus bloqué ne consomme pas CPU`.

## Critères observables
- Trace, table, valeur ou pseudo-code présent.
- Cas limite et erreur fréquente explicités.
