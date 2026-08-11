---
title: "T16 - corrige - diviser pour régner et tri fusion"
level: "terminale"
sequence_id: "T16"
document_type: "corrige"
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

# T16 - Corrigé - diviser pour régner et tri fusion

## Corrigé du TD
### Exercice 1
- Réponse attendue : division -> [38,12,27] et [12,5,44].
- Méthode : couper en deux sous-listes.
- Cas limite : liste vide.
### Exercice 2
- Réponse attendue : fusion -> [5,12,12,27,38,44].
- Méthode : trier récursivement.
- Cas limite : liste taille 1.
### Exercice 3
- Réponse attendue : cas taille 1 renvoie la liste.
- Méthode : fusionner deux listes triées.
- Cas limite : doublons 12.
### Exercice 4
- Réponse attendue : coût environ n log n.
- Méthode : compter niveaux et comparaisons.
- Cas limite : liste vide.
### Exercice 5
- Réponse attendue : division -> [38,12,27] et [12,5,44].
- Méthode : couper en deux sous-listes.
- Cas limite : liste taille 1.
### Exercice 6
- Réponse attendue : fusion -> [5,12,12,27,38,44].
- Méthode : trier récursivement.
- Cas limite : doublons 12.
### Exercice 7
- Réponse attendue : cas taille 1 renvoie la liste.
- Méthode : fusionner deux listes triées.
- Cas limite : liste vide.
### Exercice 8
- Réponse attendue : coût environ n log n.
- Méthode : compter niveaux et comparaisons.
- Cas limite : liste taille 1.

## Corrigé du TP
- Donnée : `valeurs=[38,12,27,12,5,44]`.
- Résultat principal : division -> [38,12,27] et [12,5,44].
- Résultat secondaire : fusion -> [5,12,12,27,38,44].

## Corrigé de l évaluation
- Question 1 : division -> [38,12,27] et [12,5,44].
- Question 2 : fusion -> [5,12,12,27,38,44].
- Question 3 : cas taille 1 renvoie la liste.
- Question 4 : coût environ n log n.
