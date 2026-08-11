---
title: "P07 - trace - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "trace"
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

# P07 - Trace - fonctions, tests et spécifications

## Trace courte
- Donnée : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
- Vocabulaire : signature, précondition, postcondition, assertion, test unitaire.
- Étape 1 : écrire def prix_ttc(prix_ht: float, taux: float) -> float.
- Étape 2 : poser prix_ht >= 0 et taux >= 0.
- Résultat de référence : signature complète de prix_ttc.

## Cas limites à mémoriser
- prix_ht=0.
- taux=0.
- type chaîne "80".

## Erreurs fréquentes
- test unique non suffisant.
- précondition absente.
- effet de bord global.

## Critères de réussite observables
- Capacité : P-LANG-01.
- Résultat final : prix_ttc(80,0.20) -> 96.0.
- Cas limite : prix_ht=0.
