---
title: "P12 - tp - tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "tris, invariants et complexité"
notion: "tris, invariants et complexité"
private_data: false
official_program:
  capacities:
    - "P-ALGO-02A"
    - "P-ALGO-02B"
    - "P-ALGO-02C"
    - "P-ALGO-02D"
---

# P12 - TP - tris, invariants et complexité

## Statut du TP
TP exécutable : utiliser les fichiers du dossier `code/` (P12_starter_tris_invariants_complexite.py, P12_tests_attendus_tris_invariants_complexite.py, P12_corrige_professeur_tris_invariants_complexite.py).

## Donnée fournie
`temps=[42,17,23,17,9]`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : insérer la clé dans la partie gauche triée.
3. Réaliser : chercher le minimum du suffixe.
4. Tester le cas limite `liste vide`.
5. Produire un livrable comprenant la trace du premier passage d'insertion, une trace de sélection et un essai sur `liste vide`.

## Repères enseignant — barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `insertion après i=1 -> [17,42,23,17,9]`.
- 2 points : cas limite `liste vide`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `temps=[42,17,23,17,9]`.
### Corrigé question 2
Résultat attendu : insertion après i=1 -> [17,42,23,17,9].
### Corrigé question 3
Résultat attendu : sélection place 9 en tête.
### Corrigé question 4
Résultat attendu : `liste vide` traité sans ambiguïté.

## Liens
- TD lié : `P12_TD_tris_invariants_complexite.md`.
- Évaluation liée : `P12_evaluation_tris_invariants_complexite.md`.

## Cas limites travaillés
- liste vide.
- liste déjà triée.
- doublons 17.

## Erreurs fréquentes
- invariant confondu avec résultat.
- décalage oublié.
- coût linéaire annoncé.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code rend vérifiable le placement de la première clé.
- Au moins un cas limite de la section précédente est décidé.



## Assets Python
- Starter élève : `code/P12_starter_tris_invariants_complexite.py`.
- Tests attendus : `code/P12_tests_attendus_tris_invariants_complexite.py`.
- Corrigé professeur : `code/P12_corrige_professeur_tris_invariants_complexite.py`.
- Le starter doit échouer aux tests complets ; le corrigé professeur doit passer.
