---
title: "T11 - remediation - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "remediation"
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

# T11 - Remédiation - SoC, processus, ordonnancement et interblocage

## Diagnostic
- programme confondu avec processus.
- bloqué confondu avec terminé.
- ordre des verrous oublié.

## Activités correctives
1. Annoter `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
2. Refaire la tâche `identifier CPU mémoire interfaces` et comparer avec `P1 20 ms, P2 20 ms, P1 20 ms`.
3. Traiter le cas limite `un seul processus prêt`.
4. Relier la réponse à T-ARCH-01.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
