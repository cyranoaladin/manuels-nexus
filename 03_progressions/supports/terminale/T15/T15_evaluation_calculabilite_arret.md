---
title: "T15 - evaluation - calculabilité, programme comme donnée et arrêt"
level: "terminale"
sequence_id: "T15"
document_type: "evaluation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "calculabilité, programme comme donnée et arrêt"
notion: "calculabilité, programme comme donnée et arrêt"
private_data: false
official_program:
  capacities:
    - "T-LANG-01A"
    - "T-LANG-01B"
    - "T-LANG-01C"
---

# T15 - Évaluation - calculabilité, programme comme donnée et arrêt

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-LANG-01A, T-LANG-01B, T-LANG-01C.

## Questions
### Question 1
- Capacité officielle : T-LANG-01A.
- Énoncé : à partir de `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`, encoder un programme comme texte.
- Réponse attendue : source="print(1)" est une donnée.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `programme très long mais fini`.
### Question 2
- Capacité officielle : T-LANG-01B.
- Énoncé : à partir de `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`, raisonner indépendamment de Python.
- Réponse attendue : arrete(P,x) renvoie True ou False.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `langage différent`.
### Question 3
- Capacité officielle : T-LANG-01C.
- Énoncé : à partir de `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`, poser un oracle hypothétique.
- Réponse attendue : Q boucle si arrete(Q,Q) dit True.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `entrée absente`.
### Question 4
- Capacité officielle : T-LANG-01A.
- Énoncé : à partir de `arrete(P,x) prétend répondre True si P(x) termine ; Q appelle arrete(Q,Q)`, construire un programme contradictoire.
- Réponse attendue : contradiction donc oracle impossible.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `programme très long mais fini`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : source="print(1)" est une donnée.
- Critère spécifique : encoder un programme comme texte et éviter `non connu confondu avec impossible`.
### Corrigé question 2
- Résultat attendu : arrete(P,x) renvoie True ou False.
- Critère spécifique : raisonner indépendamment de Python et éviter `tests finis comme preuve`.
### Corrigé question 3
- Résultat attendu : Q boucle si arrete(Q,Q) dit True.
- Critère spécifique : poser un oracle hypothétique et éviter `contradiction oubliée`.
### Corrigé question 4
- Résultat attendu : contradiction donc oracle impossible.
- Critère spécifique : construire un programme contradictoire et éviter `non connu confondu avec impossible`.

## Erreurs fréquentes et remédiation
- non connu confondu avec impossible.
- tests finis comme preuve.
- contradiction oubliée.

## Cas limites travaillés
- programme très long mais fini.
- langage différent.
- entrée absente.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `source="print(1)" est une donnée`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T15 sur `calculabilite_arret`.

## Aménagement
- Version aménagée : `T15_version_amenagee_calculabilite_arret.md` ; consignes découpées et barème conservé.
