---
title: "T16 - tp - diviser pour régner et tri fusion"
level: "terminale"
sequence_id: "T16"
document_type: "tp"
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

# T16 - TP - diviser pour régner et tri fusion

## Statut du TP
TP exécutable : utiliser les fichiers du dossier `code/` (T16_starter_diviser_pour_regner_tri_fusion.py, T16_tests_attendus_diviser_pour_regner_tri_fusion.py, T16_corrige_professeur_diviser_pour_regner_tri_fusion.py).

## Donnée fournie
`valeurs=[38,12,27,12,5,44]`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : couper en deux sous-listes.
3. Réaliser : trier récursivement.
4. Tester le cas limite `liste vide`.
5. Produire le livrable : division -> [38,12,27] et [12,5,44].

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `division -> [38,12,27] et [12,5,44]`.
- 2 points : cas limite `liste vide`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `valeurs=[38,12,27,12,5,44]`.
### Corrigé question 2
Résultat attendu : division -> [38,12,27] et [12,5,44].
### Corrigé question 3
Résultat attendu : fusion -> [5,12,12,27,38,44].
### Corrigé question 4
Résultat attendu : `liste vide` traité sans ambiguïté.

## Liens
- TD lié : `T16_TD_diviser_pour_regner_tri_fusion.md`.
- Évaluation liée : `T16_evaluation_diviser_pour_regner_tri_fusion.md`.

## Cas limites travaillés
- liste vide.
- liste taille 1.
- doublons 12.

## Erreurs fréquentes
- cas de base oublié.
- concaténation sans fusion.
- coût quadratique annoncé.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `division -> [38,12,27] et [12,5,44]`.
- Au moins un cas limite de la section précédente est décidé.



## Assets Python
- Starter élève : `code/T16_starter_diviser_pour_regner_tri_fusion.py`.
- Tests attendus : `code/T16_tests_attendus_diviser_pour_regner_tri_fusion.py`.
- Corrigé professeur : `code/T16_corrige_professeur_diviser_pour_regner_tri_fusion.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.
