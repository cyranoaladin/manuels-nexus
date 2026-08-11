---
title: "T14 - evaluation - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "evaluation"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "modularité, API, paradigmes et bugs"
notion: "modularité, API, paradigmes et bugs"
private_data: false
official_program:
  capacities:
    - "T-LANG-03A"
    - "T-LANG-03B"
    - "T-LANG-03C"
    - "T-LANG-04A"
    - "T-LANG-04B"
    - "T-LANG-05"
---

# T14 - Évaluation - modularité, API, paradigmes et bugs

## Modalités
- Durée : 30 minutes.
- Matériel autorisé : fiche de cours.
- Capacités évaluées : T-LANG-03A, T-LANG-03B, T-LANG-03C, T-LANG-04A, T-LANG-04B, T-LANG-05.

## Questions
### Question 1
- Capacité officielle : T-LANG-03A.
- Énoncé : à partir de `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`, définir fonction publique documentée.
- Réponse attendue : moyenne_temperature(releves) -> 30.0.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.
### Question 2
- Capacité officielle : T-LANG-03B.
- Énoncé : à partir de `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`, séparer module et script principal.
- Réponse attendue : from meteo import moyenne_temperature.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `clé temperature absente`.
### Question 3
- Capacité officielle : T-LANG-03C.
- Énoncé : à partir de `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`, choisir paradigme selon tâche.
- Réponse attendue : temperature="31" refusée ou convertie.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `type chaîne`.
### Question 4
- Capacité officielle : T-LANG-04A.
- Énoncé : à partir de `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`, écrire un test révélant un bug.
- Réponse attendue : liste vide -> ValueError.
- Barème : 1 point donnée, 1 point méthode, 1 point résultat, 1 point justification sur `liste vide`.

## Corrigé question par question
### Corrigé question 1
- Résultat attendu : moyenne_temperature(releves) -> 30.0.
- Critère spécifique : définir fonction publique documentée et éviter `import avec effet de bord`.
### Corrigé question 2
- Résultat attendu : from meteo import moyenne_temperature.
- Critère spécifique : séparer module et script principal et éviter `API sans docstring`.
### Corrigé question 3
- Résultat attendu : temperature="31" refusée ou convertie.
- Critère spécifique : choisir paradigme selon tâche et éviter `bug corrigé sans test`.
### Corrigé question 4
- Résultat attendu : liste vide -> ValueError.
- Critère spécifique : écrire un test révélant un bug et éviter `import avec effet de bord`.

## Erreurs fréquentes et remédiation
- import avec effet de bord.
- API sans docstring.
- bug corrigé sans test.

## Cas limites travaillés
- liste vide.
- clé temperature absente.
- type chaîne.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `moyenne_temperature(releves) -> 30.0`.
- Au moins un cas limite de la section précédente est décidé.



## Barème question par question
- question 1: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 2: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 3: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.
- question 4: 1 point donnée exacte, 1 point méthode liée à la capacité, 1 point résultat vérifiable, 1 point justification du cas limite.

## Fiche liée
- Fiche liée : fiche de cours T14 sur `modularite_api_paradigmes_bugs`.

## Aménagement
- Version aménagée : `T14_version_amenagee_modularite_api_paradigmes_bugs.md` ; consignes découpées et barème conservé.
