---
title: "T06 - corrige - arbres binaires de recherche"
level: "terminale"
sequence_id: "T06"
document_type: "corrige"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "arbres binaires de recherche"
notion: "arbres binaires de recherche"
private_data: false
official_program:
  capacities:
    - "T-ALGO-01A"
    - "T-ALGO-01B"
    - "T-ALGO-01C"
    - "T-ALGO-01E"
    - "T-ALGO-01F"
---

# T06 - Corrigé - arbres binaires de recherche

## Corrigé du TD
### Exercice 1
- Réponse attendue : chercher 6 : 8 -> 3 -> 6.
- Méthode : comparer à la racine.
- Cas limite : arbre vide.
### Exercice 2
- Réponse attendue : insérer 7 : 8 -> 3 -> 6 -> droite.
- Méthode : descendre gauche ou droite.
- Cas limite : doublon 6.
### Exercice 3
- Réponse attendue : infixe -> 1,3,6,8,10,14.
- Méthode : parcours infixe (gauche, racine, droite) — T-ALGO-01C.
- Cas limite : arbre dégénéré.
### Exercice 4
- Réponse attendue : arbre vide -> nouvelle racine.
- Méthode : parcours infixe pour clés triées.
- Cas limite : arbre vide.
### Exercice 5
- Réponse attendue : chercher 6 : 8 -> 3 -> 6.
- Méthode : comparer à la racine.
- Cas limite : doublon 6.
### Exercice 6
- Réponse attendue : insérer 7 : 8 -> 3 -> 6 -> droite.
- Méthode : descendre gauche ou droite.
- Cas limite : arbre dégénéré.
### Exercice 7
- Réponse attendue : infixe -> 1,3,6,8,10,14.
- Méthode : insérer une feuille.
- Cas limite : arbre vide.
### Exercice 8
- Réponse attendue : arbre vide -> nouvelle racine.
- Méthode : parcours infixe pour clés triées.
- Cas limite : doublon 6.

## Corrigé du TP
- Donnée : `ABR racine=8, gauche=3 avec 1 et 6, droite=10 avec 14`.
- Résultat principal : chercher 6 : 8 -> 3 -> 6.
- Résultat secondaire : insérer 7 : 8 -> 3 -> 6 -> droite.

## Corrigé de l évaluation
- Question 1 : chercher 6 : 8 -> 3 -> 6.
- Question 2 : insérer 7 : 8 -> 3 -> 6 -> droite.
- Question 3 : infixe -> 1,3,6,8,10,14.
- Question 4 : arbre vide -> nouvelle racine.
- Question 5 : taille = 6 (T-ALGO-01A), hauteur = 2 (T-ALGO-01B).
