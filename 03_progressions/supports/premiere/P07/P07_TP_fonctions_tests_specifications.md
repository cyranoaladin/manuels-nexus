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

## Objectifs opérationnels
- Objectif 1 : écrire une fonction pure `prix_ttc` avec signature, précondition numérique et résultat arrondi à deux décimales.
- Objectif 2 : distinguer test nominal, test limite et test invalide dans un fichier de tests attendu.
- Objectif 3 : refuser explicitement une donnée incohérente plutôt que renvoyer une valeur arbitraire.
- Objectif 4 : comparer le starter, le corrigé et les tests pour comprendre ce qui reste à programmer.

## Donnée fournie
`prix_ht=80.0, taux=0.20 -> 96.0 ; prix_ht=-5.0 -> ValueError`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : écrire def prix_ttc(prix_ht: float, taux: float) -> float.
3. Réaliser : poser prix_ht >= 0 et taux >= 0.
4. Tester le cas limite `prix_ht=0`.
5. Produire le livrable : signature complète de prix_ttc.

## Déroulé en classe
1. Ouvrir le starter et repérer les trois fonctions incomplètes avant toute modification.
2. Écrire d'abord la signature de `prix_ttc` sans coder le calcul.
3. Noter les préconditions : prix hors taxe positif ou nul, taux positif ou nul.
4. Ajouter le calcul `prix_ht * (1 + taux)` puis l'arrondi à deux décimales.
5. Vérifier à la main `80.0 * 1.20 = 96.0` avant de lancer les tests.
6. Compléter `est_pair` avec le reste de la division par 2.
7. Compléter `normaliser_nom` en supprimant les espaces extérieurs et en mettant le nom en capitale initiale.
8. Lancer les tests attendus avec le module starter pour constater l'échec initial.
9. Corriger une fonction à la fois et relancer les tests après chaque correction.
10. Expliquer dans la trace pourquoi `prix_ht=-5.0` et nom vide doivent lever `ValueError`.

## Tests attendus à interpréter
- Test nominal : `prix_ttc(80.0, 0.20)` doit renvoyer `96.0`.
- Test limite : `prix_ttc(0.0, 0.20)` doit renvoyer `0.0`.
- Test invalide : `prix_ttc(-5.0, 0.20)` doit lever `ValueError`.
- Test de parité : `est_pair(18)` vaut `True` et `est_pair(17)` vaut `False`.
- Test de texte : `normaliser_nom("  ada  ")` doit renvoyer `"Ada"`.

## Remédiation immédiate
- Si le calcul donne `80.2`, reprendre la priorité entre addition et multiplication.
- Si le prix négatif passe, relire la précondition avant le calcul.
- Si le nom vide renvoie une chaîne, tester la longueur après `strip`.

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



## Protocole de validation complémentaire
1. Préparer un jeu nominal propre à P07 et noter la sortie attendue avant exécution.
2. Préparer un cas limite distinct et expliquer pourquoi il doit être accepté ou refusé.
3. Exécuter le starter : il doit échouer sur au moins un test complet, ce qui confirme que le travail élève reste à produire.
4. Exécuter le corrigé professeur : il doit produire exactement les valeurs attendues dans les tests.
5. Comparer la trace obtenue avec la consigne : chaque étape doit être justifiée par une donnée du sujet.
6. Noter l'erreur fréquente observée et choisir la remédiation ciblée dans le support associé.

## Livrable vérifiable complémentaire
- Fichier élève complété avec les fonctions demandées dans le TP.
- Trace courte indiquant entrée, traitement, sortie et cas limite.
- Capture textuelle des tests attendus : nominal OK, cas limite OK, entrée invalide traitée.
- Commentaire final indiquant la capacité officielle réellement travaillée.

## Assets Python
- Starter élève : `code/P07_starter_fonctions_tests_specifications.py`.
- Tests attendus : `code/P07_tests_attendus_fonctions_tests_specifications.py`.
- Corrigé professeur : `code/P07_corrige_professeur_fonctions_tests_specifications.py`.
- Fonctions à compléter : `prix_ttc`, `est_pair`, `normaliser_nom`.
- Cas testés : prix HT nominal, prix négatif refusé, parité, nom vide refusé.
