---
title: "T14 - tp_papier - modularité, API, paradigmes et bugs"
level: "terminale"
sequence_id: "T14"
document_type: "tp_papier"
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

# T14 - TP - modularité, API, paradigmes et bugs

## Statut du TP
TP papier : ce support n attend aucune ressource Python ; le livrable est une trace écrite vérifiable.

## Donnée fournie
`meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : définir fonction publique documentée.
3. Réaliser : séparer module et script principal.
4. Tester le cas limite `liste vide`.
5. Produire le livrable : moyenne_temperature(releves) -> 30.0.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `moyenne_temperature(releves) -> 30.0`.
- 2 points : cas limite `liste vide`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `meteo.py expose moyenne_temperature(releves) ; releves=[{ville:Sfax,temperature:31},{ville:Tunis,temperature:29}]`.
### Corrigé question 2
Résultat attendu : moyenne_temperature(releves) -> 30.0.
### Corrigé question 3
Résultat attendu : from meteo import moyenne_temperature.
### Corrigé question 4
Résultat attendu : `liste vide` traité sans ambiguïté.

## Liens
- TD lié : `T14_TD_modularite_api_paradigmes_bugs.md`.
- Évaluation liée : `T14_evaluation_modularite_api_paradigmes_bugs.md`.

## Cas limites travaillés
- liste vide.
- clé temperature absente.
- type chaîne.

## Erreurs fréquentes
- import avec effet de bord.
- API sans docstring.
- bug corrigé sans test.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `moyenne_temperature(releves) -> 30.0`.
- Au moins un cas limite de la section précédente est décidé.

