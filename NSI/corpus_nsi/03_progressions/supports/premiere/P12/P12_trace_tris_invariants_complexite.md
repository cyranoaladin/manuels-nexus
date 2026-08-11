---
title: "P12 - trace - tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "trace"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "tris, invariants et complexité"
notion: "tris, invariants et complexité"
private_data: false
official_program:
  capacities:
    - "P-ALGO-02A"
    - "P-ALGO-02B"
    - "P-ALGO-02C"
    - "P-ALGO-02D"
---

# P12 - Trace - tris, invariants et complexité

## Trace courte
- Donnée : `temps=[42,17,23,17,9]`.
- Vocabulaire : tri par insertion, tri par sélection, invariant, variant, coût quadratique.
- Étape 1 : insérer la clé dans la partie gauche triée.
- Étape 2 : chercher le minimum du suffixe.
- À compléter : écrire l'état après la première insertion et entourer les valeurs décalées.

## Cas limites à mémoriser
- liste vide.
- liste déjà triée.
- doublons 17.

## Erreurs fréquentes
- invariant confondu avec résultat.
- décalage oublié.
- coût linéaire annoncé.

## Critères de réussite observables
- Capacité : P-ALGO-02A.
- Vérification : citer le minimum retenu au premier tour de sélection et justifier son choix.

## Repères enseignant — trace de référence
- Première insertion : `insertion après i=1 -> [17,42,23,17,9]`.
- Premier tour de sélection sur la liste du cours : le minimum est placé en tête après exploration du suffixe.
- Cas limite : liste vide.
