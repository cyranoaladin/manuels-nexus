---
title: "P11 - tp - parcours, recherche, extremum et moyenne"
level: "premiere"
sequence_id: "P11"
document_type: "tp"
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

# P11 - TP - parcours, recherche, extremum et moyenne

## Statut du TP
TP exécutable : le livrable élève est un fichier Python de parcours de listes vérifié par tests.

## Donnée fournie
`mesures=[18,21,17,24,21], cible=21, seuil=22`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : parcourir avec indice.
3. Réaliser : mémoriser le premier indice de 21.
4. Tester le cas limite `liste vide`.
5. Produire le livrable : première occurrence de 21 -> indice 1.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `première occurrence de 21 -> indice 1`.
- 2 points : cas limite `liste vide`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `mesures=[18,21,17,24,21], cible=21, seuil=22`.
### Corrigé question 2
Résultat attendu : première occurrence de 21 -> indice 1.
### Corrigé question 3
Résultat attendu : maximum -> 24.
### Corrigé question 4
Résultat attendu : `liste vide` traité sans ambiguïté.

## Liens
- TD lié : `P11_TD_parcours_recherche_extremum_moyenne.md`.
- Évaluation liée : `P11_evaluation_parcours_recherche_extremum_moyenne.md`.

## Cas limites travaillés
- liste vide.
- cible absente.
- doublon de 21.

## Erreurs fréquentes
- maximum initialisé à 0.
- division par len sans test.
- indice changé après première occurrence.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `première occurrence de 21 -> indice 1`.
- Au moins un cas limite de la section précédente est décidé.

## Assets Python
- Starter élève : `code/P11_starter_parcours_recherche_extremum_moyenne.py`.
- Tests attendus : `code/P11_tests_attendus_parcours_recherche_extremum_moyenne.py`.
- Corrigé professeur : `code/P11_corrige_professeur_parcours_recherche_extremum_moyenne.py`.
- Fonctions à compléter : `maximum`, `indices_de`, `moyenne`.
- Cas testés : maximum positif/négatif, cible doublée ou absente, liste vide refusée.
