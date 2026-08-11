---
title: "T18 - corrige - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "corrige"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Boyer-Moore"
notion: "Boyer-Moore"
private_data: false
official_program:
  capacities:
    - "T-ALGO-05"
---

# T18 - Corrigé - Boyer-Moore

## Corrigé du TD
### Exercice 1
- Réponse attendue : table : A->2, N->1.
- Méthode : prétraiter dernière position de chaque caractère.
- Cas limite : motif absent.
### Exercice 2
- Réponse attendue : alignement 0 : N comparé à A -> décalage 1.
- Méthode : comparer depuis la droite.
- Cas limite : motif plus long que texte.
### Exercice 3
- Réponse attendue : alignement 1 : ANA trouvé à l'indice 1.
- Méthode : calculer max(1, j - dernière_position).
- Cas limite : caractère absent du motif.
### Exercice 4
- Réponse attendue : motif XYZ absent.
- Méthode : comparer avec recherche naïve.
- Cas limite : motif absent.
### Exercice 5
- Réponse attendue : table : A->2, N->1.
- Méthode : prétraiter dernière position de chaque caractère.
- Cas limite : motif plus long que texte.
### Exercice 6
- Réponse attendue : alignement 0 : N comparé à A -> décalage 1.
- Méthode : comparer depuis la droite.
- Cas limite : caractère absent du motif.
### Exercice 7
- Réponse attendue : alignement 1 : ANA trouvé à l'indice 1.
- Méthode : calculer max(1, j - dernière_position).
- Cas limite : motif absent.
### Exercice 8
- Réponse attendue : motif XYZ absent.
- Méthode : comparer avec recherche naïve.
- Cas limite : motif plus long que texte.

## Corrigé du TP
- Donnée : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`.
- Résultat principal : table : A->2, N->1.
- Résultat secondaire : alignement 0 : N comparé à A -> décalage 1.

## Corrigé de l évaluation
- Question 1 : table : A->2, N->1.
- Question 2 : alignement 0 : N comparé à A -> décalage 1.
- Question 3 : alignement 1 : ANA trouvé à l'indice 1.
- Question 4 : motif XYZ absent.
