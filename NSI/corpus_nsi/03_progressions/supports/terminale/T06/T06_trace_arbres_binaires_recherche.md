---
title: "T06 - trace - arbres binaires de recherche"
level: "terminale"
sequence_id: "T06"
document_type: "trace"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "arbres binaires de recherche"
notion: "arbres binaires de recherche"
private_data: false
official_program:
  capacities:
    - "T-ALGO-01E"
    - "T-ALGO-01F"
---

# T06 - Trace - arbres binaires de recherche

## Trace courte
- Donnée : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
- Vocabulaire : invariant ABR, recherche, insertion, parcours infixe, arbre vide.
- Étape 1 : comparer à la racine.
- Étape 2 : descendre gauche ou droite.
- Résultat de référence : chercher 6 : 8 -> 3 -> 6.

## Cas limites à mémoriser
- arbre vide.
- doublon 6.
- arbre dégénéré.

## Erreurs fréquentes
- gauche et droite inversées.
- logarithmique sans équilibre.
- racine vide oubliée.

## Critères de réussite observables
- Capacité : T-ALGO-01E.
- Résultat final : insérer 7 : 8 -> 3 -> 6 -> droite.
- Cas limite : arbre vide.
