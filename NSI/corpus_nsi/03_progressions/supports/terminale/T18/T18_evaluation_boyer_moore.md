---
title: "T18 - evaluation - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "evaluation"
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

# T18 - Évaluation - Boyer-Moore

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-ALGO-05.

## Questions
### Question 1
- Capacité officielle : T-ALGO-05.
- Énoncé : à partir de `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`, prétraiter dernière position de chaque caractère.
- Réponse attendue : table : A->2, N->1.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `motif absent`.
### Question 2
- Capacité officielle : T-ALGO-05.
- Énoncé : à partir de `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`, comparer depuis la droite.
- Réponse attendue : alignement 0 : N comparé à A -> décalage 1.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `motif plus long que texte`.
### Question 3
- Capacité officielle : T-ALGO-05.
- Énoncé : à partir de `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`, calculer max(1, j - dernière_position).
- Réponse attendue : alignement 1 : ANA trouvé à l'indice 1.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `caractère absent du motif`.
### Question 4
- Capacité officielle : T-ALGO-05.
- Énoncé : à partir de `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`, comparer avec recherche naïve.
- Réponse attendue : motif XYZ absent.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `motif absent`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : table : A->2, N->1.
- Critère spécifique : prétraiter dernière position de chaque caractère et éviter `comparaison gauche à droite`.
### Corrigé question 2
- Résultat attendu : alignement 0 : N comparé à A -> décalage 1.
- Critère spécifique : comparer depuis la droite et éviter `décalage nul`.
### Corrigé question 3
- Résultat attendu : alignement 1 : ANA trouvé à l'indice 1.
- Critère spécifique : calculer max(1, j - dernière_position) et éviter `caractère absent oublié`.
### Corrigé question 4
- Résultat attendu : motif XYZ absent.
- Critère spécifique : comparer avec recherche naïve et éviter `comparaison gauche à droite`.

## Erreurs fréquentes et remédiation
- comparaison gauche à droite.
- décalage nul.
- caractère absent oublié.

## Cas limites travaillés
- motif absent.
- motif plus long que texte.
- caractère absent du motif.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `table : A->2, N->1`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T18 sur `boyer_moore`.

## Aménagement
- Version aménagée : `T18_version_amenagee_boyer_moore.md` ; consignes découpées et barème conservé.
