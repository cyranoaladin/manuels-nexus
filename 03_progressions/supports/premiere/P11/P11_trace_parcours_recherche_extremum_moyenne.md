---
title: "P11 - trace - parcours, recherche, extremum et moyenne"
level: "premiere"
sequence_id: "P11"
document_type: "trace"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "parcours, recherche, extremum et moyenne"
notion: "parcours, recherche, extremum et moyenne"
private_data: false
official_program:
  capacities:
    - "P-ALGO-01A"
    - "P-ALGO-01B"
---

# P11 - Trace - parcours, recherche, extremum et moyenne

## Trace courte
- Donnée : `mesures=[18,21,17,24,21], cible=21, seuil=22`.
- Vocabulaire : parcours linéaire, recherche occurrence, premier indice, maximum, minimum.
- Étape 1 : parcourir avec indice.
- Étape 2 : mémoriser le premier indice de 21.
- Résultat de référence : première occurrence de 21 -> indice 1.

## Cas limites à mémoriser
- liste vide.
- cible absente.
- doublon de 21.

## Erreurs fréquentes
- maximum initialisé à 0.
- division par len sans test.
- indice changé après première occurrence.

## Critères de réussite observables
- Capacité : P-ALGO-01A.
- Résultat final : maximum -> 24.
- Cas limite : liste vide.
