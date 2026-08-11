---
title: "P07 - remediation - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "remediation"
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

# P07 - Remédiation - fonctions, tests et spécifications

## Diagnostic
- test unique non suffisant.
- précondition absente.
- effet de bord global.

## Activités correctives
1. Annoter `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
2. Refaire la tâche `écrire def prix_ttc(prix_ht: float, taux: float) -> float` et comparer avec `signature complète de prix_ttc`.
3. Traiter le cas limite `prix_ht=0`.
4. Relier la réponse à P-LANG-01.

## Critères de sortie
- Donnée exacte.
- Résultat final explicite.
- Cas limite décidé.
