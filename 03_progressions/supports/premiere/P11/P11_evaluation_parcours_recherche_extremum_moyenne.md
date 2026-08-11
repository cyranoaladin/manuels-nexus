---
title: "P11 - evaluation - parcours, recherche, extremum et moyenne"
level: "premiere"
sequence_id: "P11"
document_type: "evaluation"
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

# P11 - Évaluation - parcours, recherche, extremum et moyenne

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : P-ALGO-01A, P-ALGO-01B.

## Questions
### Question 1
- Capacité officielle : P-ALGO-01A.
- Énoncé : à partir de `mesures=[18,21,17,24,21], cible=21, seuil=22`, parcourir avec indice.
- Réponse attendue : première occurrence de 21 -> indice 1.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.
### Question 2
- Capacité officielle : P-ALGO-01B.
- Énoncé : à partir de `mesures=[18,21,17,24,21], cible=21, seuil=22`, mémoriser le premier indice de 21.
- Réponse attendue : maximum -> 24.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `cible absente`.
### Question 3
- Capacité officielle : P-ALGO-01A.
- Énoncé : à partir de `mesures=[18,21,17,24,21], cible=21, seuil=22`, initialiser maximum à la première valeur.
- Réponse attendue : somme=101, len=5, moyenne=20.2.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `doublon de 21`.
### Question 4
- Capacité officielle : P-ALGO-01B.
- Énoncé : à partir de `mesures=[18,21,17,24,21], cible=21, seuil=22`, tester liste vide avant moyenne.
- Réponse attendue : liste vide -> ValueError.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : première occurrence de 21 -> indice 1.
- Critère spécifique : parcourir avec indice et éviter `maximum initialisé à 0`.
### Corrigé question 2
- Résultat attendu : maximum -> 24.
- Critère spécifique : mémoriser le premier indice de 21 et éviter `division par len sans test`.
### Corrigé question 3
- Résultat attendu : somme=101, len=5, moyenne=20.2.
- Critère spécifique : initialiser maximum à la première valeur et éviter `indice changé après première occurrence`.
### Corrigé question 4
- Résultat attendu : liste vide -> ValueError.
- Critère spécifique : tester liste vide avant moyenne et éviter `maximum initialisé à 0`.

## Erreurs fréquentes et remédiation
- maximum initialisé à 0.
- division par len sans test.
- indice changé après première occurrence.

## Cas limites travaillés
- liste vide.
- cible absente.
- doublon de 21.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `première occurrence de 21 -> indice 1`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours P11 sur `parcours_recherche_extremum_moyenne`.

## Aménagement
- Version aménagée : `P11_version_amenagee_parcours_recherche_extremum_moyenne.md` ; consignes découpées et barème conservé.
