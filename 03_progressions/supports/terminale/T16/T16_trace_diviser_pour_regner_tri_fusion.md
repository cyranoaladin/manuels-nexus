---
title: "T16 - trace - diviser pour régner et tri fusion"
level: "terminale"
sequence_id: "T16"
document_type: "trace"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "diviser pour régner et tri fusion"
notion: "diviser pour régner et tri fusion"
private_data: false
official_program:
  capacities:
    - "T-ALGO-03"
---

# T16 - Trace - diviser pour régner et tri fusion

## Trace courte
- Donnée : `valeurs=[38,12,27,12,5,44]`.
- Vocabulaire : diviser pour régner, cas de base, division, récursion, fusion.
- Étape 1 : couper en deux sous-listes.
- Étape 2 : trier récursivement.
- Résultat de référence : division -> [38,12,27] et [12,5,44].

## Cas limites à mémoriser
- liste vide.
- liste taille 1.
- doublons 12.

## Erreurs fréquentes
- cas de base oublié.
- concaténation sans fusion.
- coût quadratique annoncé.

## Critères de réussite observables
- Capacité : T-ALGO-03.
- Résultat final : fusion -> [5,12,12,27,38,44].
- Cas limite : liste vide.
