---
title: "P06 - evaluation - recherche, tri et fusion de tables"
level: "premiere"
sequence_id: "P06"
document_type: "evaluation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "recherche, tri et fusion de tables"
notion: "recherche, tri et fusion de tables"
private_data: false
official_program:
  capacities:
    - "P-TABLE-03"
    - "P-TABLE-04"
---

# P06 - Évaluation - recherche, tri et fusion de tables

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : P-TABLE-03, P-TABLE-04.

## Questions
### Question 1
- Capacité officielle : P-TABLE-03.
- Énoncé : à partir de `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`, chercher la première ligne id=17.
- Réponse attendue : première ligne id=17 -> Ada/robot.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `table vide`.
### Question 2
- Capacité officielle : P-TABLE-04.
- Énoncé : à partir de `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`, détecter le doublon id=17.
- Réponse attendue : doublon id=17 -> Ada/python signalé.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `clé id=9 absente`.
### Question 3
- Capacité officielle : P-TABLE-03.
- Énoncé : à partir de `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`, trier par (nom, atelier).
- Réponse attendue : tri -> Ada/python, Ada/robot, Linus/web.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `conflit de clé id=17`.
### Question 4
- Capacité officielle : P-TABLE-04.
- Énoncé : à partir de `inscriptions=[{id:17,nom:Ada,atelier:robot},{id:4,nom:Linus,atelier:web},{id:17,nom:Ada,atelier:python}], presences=[{id:17,present:true},{id:9,present:true}]`, fusionner inscriptions et présences.
- Réponse attendue : fusion -> erreur id_absent=9.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `table vide`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : première ligne id=17 -> Ada/robot.
- Critère spécifique : chercher la première ligne id=17 et éviter `écraser un doublon`.
### Corrigé question 2
- Résultat attendu : doublon id=17 -> Ada/python signalé.
- Critère spécifique : détecter le doublon id=17 et éviter `utiliser un indice comme clé`.
### Corrigé question 3
- Résultat attendu : tri -> Ada/python, Ada/robot, Linus/web.
- Critère spécifique : trier par (nom, atelier) et éviter `oublier une clé absente`.
### Corrigé question 4
- Résultat attendu : fusion -> erreur id_absent=9.
- Critère spécifique : fusionner inscriptions et présences et éviter `écraser un doublon`.

## Erreurs fréquentes et remédiation
- écraser un doublon.
- utiliser un indice comme clé.
- oublier une clé absente.

## Cas limites travaillés
- table vide.
- clé id=9 absente.
- conflit de clé id=17.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `première ligne id=17 -> Ada/robot`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours P06 sur `tables_recherche_tri_fusion`.

## Aménagement
- Version aménagée : `P06_version_amenagee_tables_recherche_tri_fusion.md` ; consignes découpées et barème conservé.
