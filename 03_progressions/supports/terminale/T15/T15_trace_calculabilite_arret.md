---
title: "T15 - trace - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "trace"
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

# T15 - Trace - calculabilité, programme comme donnée et arrêt

## Trace courte
- Donnée : `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`.
- Vocabulaire : programme comme donnée, interpréteur, calculabilité, langage indépendant, problème de l arrêt.
- Étape 1 : encoder un programme comme texte.
- Étape 2 : raisonner indépendamment de Python.
- Résultat de référence : source="print(1)" est une donnée.

## Cas limites à mémoriser
- programme très long mais fini.
- langage différent.
- entrée absente.

## Erreurs fréquentes
- non connu confondu avec impossible.
- tests finis comme preuve.
- contradiction oubliée.

## Critères de réussite observables
- Capacité : T-LANG-01A.
- Résultat final : arrete(P,x) renvoie True ou False.
- Cas limite : programme très long mais fini.
