---
title: "T18 - tp - Boyer-Moore"
level: "terminale"
sequence_id: "T18"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Boyer-Moore"
notion: "Boyer-Moore"
private_data: false
official_program:
  capacities:
    - "T-ALGO-05"
---

# T18 - TP - Boyer-Moore

## Statut du TP
TP exécutable : le livrable élève est un fichier Python de recherche Boyer-Moore simplifiée vérifié par tests.

## Donnée fournie
`texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : prétraiter dernière position de chaque caractère.
3. Réaliser : comparer depuis la droite.
4. Tester le cas limite `motif absent`.
5. Produire le livrable : table : A->2, N->1 et indice trouvé 1 pour `texte="BANANAS"`, `motif="ANA"`.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `table : A->2, N->1` et indice trouvé `1`.
- 2 points : cas limite `motif absent`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `texte="BANANAS", motif="ANA", table mauvais caractère A->2, N->1`.
### Corrigé question 2
Résultat attendu : table : A->2, N->1.
### Corrigé question 3
Résultat attendu : alignement 0 : N comparé à A -> décalage 1.
### Corrigé question 4
Résultat attendu : alignement 1 : `ANA` correspond, motif trouvé à l indice 1 ; motif absent renvoie -1.

## Liens
- TD lié : `T18_TD_boyer_moore.md`.
- Évaluation liée : `T18_evaluation_boyer_moore.md`.

## Cas limites travaillés
- motif absent.
- motif plus long que texte.
- caractère absent du motif.

## Erreurs fréquentes
- comparaison gauche à droite.
- décalage nul.
- caractère absent oublié.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `table : A->2, N->1` et à l indice trouvé `1`.
- Au moins un cas limite de la section précédente est décidé.

## Assets Python
- Starter élève : `code/T18_starter_boyer_moore.py`.
- Tests attendus : `code/T18_tests_attendus_boyer_moore.py`.
- Corrigé professeur : `code/T18_corrige_professeur_boyer_moore.py`.
- Fonctions à compléter : `table_mauvais_caractere`, `boyer_moore`, `trace_decalages`.
- Cas testés : motif trouvé dans `BANANAS`, motif absent, motif plus long que le texte.
