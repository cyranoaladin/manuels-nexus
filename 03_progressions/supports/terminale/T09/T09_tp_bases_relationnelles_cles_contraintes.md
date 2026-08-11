---
title: "T09 - tp - bases relationnelles, clés et contraintes"
level: "terminale"
sequence_id: "T09"
document_type: "tp"
status: "needs_review"
version: "0.6.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "bases relationnelles, clés et contraintes"
notion: "bases relationnelles, clés et contraintes"
private_data: false
official_program:
  capacities:
    - "T-BDD-01A"
    - "T-BDD-01B"
    - "T-BDD-01C"
    - "T-BDD-02"
---

# T09 - TP - bases relationnelles, clés et contraintes

## Statut du TP
TP exécutable : le livrable élève est un fichier Python de vérification de contraintes relationnelles.

## Donnée fournie
`Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`

## Travail demandé
1. Préparer la donnée et nommer les champs utiles.
2. Réaliser : identifier schéma et instance.
3. Réaliser : vérifier unicité id_livre.
4. Tester le cas limite `clé primaire nulle`.
5. Produire le livrable : Livre.id_livre identifie chaque livre.

## Barème associé
- 2 points : donnée préparée.
- 3 points : méthode principale.
- 3 points : résultat `Livre.id_livre identifie chaque livre`.
- 2 points : cas limite `clé primaire nulle`.

## Corrigé question par question
### Corrigé question 1
Résultat attendu : `Livre(1,Dune), Livre(2,Fondation) ; Emprunt(10,1,Nora), Emprunt(11,9,Sam) invalide`.
### Corrigé question 2
Résultat attendu : clé primaire `Livre.id_livre` ; valeurs `1` et `2` sont uniques et non nulles.
### Corrigé question 3
Résultat attendu : clé étrangère `Emprunt.id_livre -> Livre.id_livre` ; `id_livre=9` est refusé car absent de `Livre`.
### Corrigé question 4
Résultat attendu : `clé primaire nulle` traité sans ambiguïté.

## Liens
- TD lié : `T09_TD_bases_relationnelles_cles_contraintes.md`.
- Évaluation liée : `T09_evaluation_bases_relationnelles_cles_contraintes.md`.

## Cas limites travaillés
- clé primaire nulle.
- doublon id_livre=1.
- suppression référencée.

## Erreurs fréquentes
- attribut confondu avec valeur.
- clé étrangère supposée unique.
- domaine ignoré.

## Critères de réussite observables
- La donnée de départ est recopiée exactement.
- La trace ou le pseudo-code conduit à `Livre.id_livre identifie chaque livre`.
- Au moins un cas limite de la section précédente est décidé.

## Assets Python
- Starter élève : `code/T09_starter_bases_relationnelles_cles_contraintes.py`.
- Tests attendus : `code/T09_tests_attendus_bases_relationnelles_cles_contraintes.py`.
- Corrigé professeur : `code/T09_corrige_professeur_bases_relationnelles_cles_contraintes.py`.
- Fonctions à compléter : `cles_primaires_uniques`, `references_valides`, `violations_domaine`.
- Cas testés : clé primaire dupliquée, clé étrangère absente, domaine de note invalide.
