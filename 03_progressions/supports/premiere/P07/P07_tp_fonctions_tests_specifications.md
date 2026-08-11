---
title: "P07 - tp - fonctions, tests et spécifications"
level: "premiere"
sequence_id: "P07"
document_type: "tp"
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

# P07 - TP - fonctions, tests et spécifications

## Statut du TP
TP exécutable : le livrable élève est un fichier Python complété et vérifié par tests.

## Donnée fournie
`prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : écrire def prix_ttc(prix_ht: float, taux: float) -> float.
3. Réaliser : poser prix_ht >= 0 et taux >= 0.
4. Tester le cas limite `prix_ht=0`.
5. Produire le livrable : signature complète de prix_ttc.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `signature complète de prix_ttc`.
- 2 points : cas limite `prix_ht=0`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`.
### Corrigé question 2
Résultat attendu : `def prix_ttc(prix_ht: float, taux: float) -> float` ; `prix_ttc(80.0, 0.20) -> 96.0` et `prix_ht < 0 -> ValueError`.
### Corrigé question 3
Résultat attendu : prix_ttc(80,0.20) -> 96.0.
### Corrigé question 4
Résultat attendu : `prix_ht=0` traité sans ambiguïté.

## Liens
- TD lié : `P07_TD_fonctions_tests_specifications.md`.
- Évaluation liée : `P07_evaluation_fonctions_tests_specifications.md`.

## Cas limites travaillés
- prix_ht=0.
- taux=0.
- type chaîne "80".

## Erreurs fréquentes
- test unique non suffisant.
- précondition absente.
- effet de bord global.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `signature complète de prix_ttc`.
- Au moins un cas limite de la section précédente est décidé.

## Assets Python
- Starter élève : `code/P07_starter_fonctions_tests_specifications.py`.
- Tests attendus : `code/P07_tests_attendus_fonctions_tests_specifications.py`.
- Corrigé professeur : `code/P07_corrige_professeur_fonctions_tests_specifications.py`.
- Fonctions à compléter : `prix_ttc`, `est_pair`, `normaliser_nom`.
- Cas testés : prix HT nominal, prix négatif refusé, parité, nom vide refusé.
