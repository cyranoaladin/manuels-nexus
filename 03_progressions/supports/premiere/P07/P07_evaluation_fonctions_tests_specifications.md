---
title: "P07 - evaluation - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "evaluation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "fonctions, tests et spécifications"
notion: "fonctions, tests et spécifications"
private_data: false
official_program:
  capacities:
    - "P-LANG-01"
    - "P-LANG-02"
    - "P-LANG-03A"
    - "P-LANG-03B"
    - "P-LANG-03C"
    - "P-LANG-04"
    - "P-LANG-05"
---

# P07 - Évaluation - fonctions, tests et spécifications

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : P-LANG-01, P-LANG-02, P-LANG-03A, P-LANG-03B, P-LANG-03C, P-LANG-04, P-LANG-05.

## Questions
### Question 1
- Capacité officielle : P-LANG-01.
- Énoncé : à partir de `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`, écrire def prix_ttc(prix_ht: float, taux: float) -> float.
- Réponse attendue : signature complète de prix_ttc.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `prix_ht=0`.
### Question 2
- Capacité officielle : P-LANG-02.
- Énoncé : à partir de `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`, poser prix_ht >= 0 et taux >= 0.
- Réponse attendue : prix_ttc(80,0.20) -> 96.0.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `taux=0`.
### Question 3
- Capacité officielle : P-LANG-03A.
- Énoncé : à partir de `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`, vérifier résultat >= prix_ht.
- Réponse attendue : prix_ttc(-5,0.20) -> ValueError.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `type chaîne "80"`.
### Question 4
- Capacité officielle : P-LANG-03B.
- Énoncé : à partir de `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`, écrire tests nominal, limite et invalide.
- Réponse attendue : taux=0 -> résultat 80.0.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `prix_ht=0`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : signature complète de prix_ttc.
- Critère spécifique : écrire def prix_ttc(prix_ht: float, taux: float) -> float et éviter `test unique non suffisant`.
### Corrigé question 2
- Résultat attendu : prix_ttc(80,0.20) -> 96.0.
- Critère spécifique : poser prix_ht >= 0 et taux >= 0 et éviter `précondition absente`.
### Corrigé question 3
- Résultat attendu : prix_ttc(-5,0.20) -> ValueError.
- Critère spécifique : vérifier résultat >= prix_ht et éviter `effet de bord global`.
### Corrigé question 4
- Résultat attendu : taux=0 -> résultat 80.0.
- Critère spécifique : écrire tests nominal, limite et invalide et éviter `test unique non suffisant`.

## Erreurs fréquentes et remédiation
- test unique non suffisant.
- précondition absente.
- effet de bord global.

## Cas limites travaillés
- prix_ht=0.
- taux=0.
- type chaîne "80".

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `signature complète de prix_ttc`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours P07 sur `fonctions_tests_specifications`.

## Aménagement
- Version aménagée : `P07_version_amenagee_fonctions_tests_specifications.md` ; consignes découpées et barème conservé.
