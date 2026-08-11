---
title: "T16 - evaluation - diviser pour régner et tri fusion"
level: "terminale"
sequence_id: "T16"
document_type: "evaluation"
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

# T16 - Évaluation - diviser pour régner et tri fusion

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-ALGO-03.

## Questions
### Question 1
- Capacité officielle : T-ALGO-03.
- Énoncé : à partir de `valeurs=[38,12,27,12,5,44]`, couper en deux sous-listes.
- Réponse attendue : division -> [38,12,27] et [12,5,44].
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.
### Question 2
- Capacité officielle : T-ALGO-03.
- Énoncé : à partir de `valeurs=[38,12,27,12,5,44]`, trier récursivement.
- Réponse attendue : fusion -> [5,12,12,27,38,44].
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste taille 1`.
### Question 3
- Capacité officielle : T-ALGO-03.
- Énoncé : à partir de `valeurs=[38,12,27,12,5,44]`, fusionner deux listes triées.
- Réponse attendue : cas taille 1 renvoie la liste.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `doublons 12`.
### Question 4
- Capacité officielle : T-ALGO-03.
- Énoncé : à partir de `valeurs=[38,12,27,12,5,44]`, compter niveaux et comparaisons.
- Réponse attendue : coût environ n log n.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : division -> [38,12,27] et [12,5,44].
- Critère spécifique : couper en deux sous-listes et éviter `cas de base oublié`.
### Corrigé question 2
- Résultat attendu : fusion -> [5,12,12,27,38,44].
- Critère spécifique : trier récursivement et éviter `concaténation sans fusion`.
### Corrigé question 3
- Résultat attendu : cas taille 1 renvoie la liste.
- Critère spécifique : fusionner deux listes triées et éviter `coût quadratique annoncé`.
### Corrigé question 4
- Résultat attendu : coût environ n log n.
- Critère spécifique : compter niveaux et comparaisons et éviter `cas de base oublié`.

## Erreurs fréquentes et remédiation
- cas de base oublié.
- concaténation sans fusion.
- coût quadratique annoncé.

## Cas limites travaillés
- liste vide.
- liste taille 1.
- doublons 12.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `division -> [38,12,27] et [12,5,44]`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T16 sur `diviser_pour_regner_tri_fusion`.

## Aménagement
- Version aménagée : `T16_version_amenagee_diviser_pour_regner_tri_fusion.md` ; consignes découpées et barème conservé.
