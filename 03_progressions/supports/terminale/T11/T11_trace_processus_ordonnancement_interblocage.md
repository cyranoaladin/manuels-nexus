---
title: "T11 - trace - SoC, processus, ordonnancement et interblocage"
level: "terminale"
sequence_id: "T11"
document_type: "trace"
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

# T11 - Trace - SoC, processus, ordonnancement et interblocage

## Trace courte
- Donnée : `P1 verrouille camera puis journal ; P2 verrouille journal puis camera ; quantum=20 ms`.
- Vocabulaire : système sur puce, processus, état prêt, état bloqué, ordonnancement.
- Étape 1 : identifier CPU mémoire interfaces.
- Étape 2 : décrire création de processus.
- Résultat de référence : P1 20 ms, P2 20 ms, P1 20 ms.

## Cas limites à mémoriser
- un seul processus prêt.
- ressource libérée avant attente.
- processus bloqué.

## Erreurs fréquentes
- programme confondu avec processus.
- bloqué confondu avec terminé.
- ordre des verrous oublié.

## Critères de réussite observables
- Capacité : T-ARCH-01.
- Résultat final : P1 attend journal et P2 attend camera.
- Cas limite : un seul processus prêt.
