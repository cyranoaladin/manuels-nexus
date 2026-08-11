---
title: "T05 - Corrige - Arbres binaires"
level: "terminale"
sequence_id: "T05"
document_type: "corrige"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Arbres et algorithmes"
notion: "arbre binaire, racine, feuille, parcours"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-04A"
---


# T05 - Corrigé professeur - Arbres binaires

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-04A

## Prérequis
- Reconnaître une consigne liée à arbre binaire.
- Distinguer donnée, méthode et conclusion dans le thème Arbres et algorithmes.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T05-S1 à T05-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une expression arithmétique est représentée par un arbre dont les feuilles sont des valeurs et les nœuds internes des opérateurs.

## Activité d’entrée
1. Repérer racine, fils gauche et fils droit.
2. Calculer la hauteur d’un arbre réduit à une feuille.
3. Lister un parcours préfixe.
4. Évaluer une expression simple.

## Méthode générale de correction
- Point 1 : pour arbre feuille, exiger la donnée `7`, la méthode « reconnaître l’absence de fils » et le contrôle « arbre vide ».
- Point 2 : pour hauteur, exiger la donnée racine avec deux feuilles, la méthode « prendre 1 plus le maximum des hauteurs des sous-arbres » et le contrôle « un seul fils ».
- Point 3 : pour parcours préfixe, exiger la donnée `+ 2 3`, la méthode « visiter racine puis gauche puis droite » et le contrôle « nœud feuille ».
- Point 4 : pour évaluation, exiger la donnée `(2 + 3) * 4`, la méthode « évaluer les sous-arbres avant l’opérateur parent » et le contrôle « division par zéro si opérateur `/` ».
## Exercices numérotés
- Exercice 1 : résoudre arbre feuille avec `7` ; attendu : hauteur 0.
- Exercice 2 : expliquer hauteur à partir de racine avec deux feuilles ; attendu : hauteur 1.
- Exercice 3 : comparer parcours préfixe avec `+ 2 3` ; attendu : `+, 2, 3`.
- Exercice 4 : corriger évaluation pour `(2 + 3) * 4` ; attendu : `20`.
- Exercice 5 : tester un cas limite lié à arbre vide ; attendu : le comportement de arbre feuille est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour hauteur ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise parcours préfixe avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur évaluation ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `7`, appliquer la méthode « reconnaître l’absence de fils », puis écrire hauteur 0.
- Résultat : hauteur 0.
- Contrôle : faire apparaître le contrôle « arbre vide ».
- Erreur traitée : EF1 - Confondre hauteur et nombre de nœuds.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de prendre 1 plus le maximum des hauteurs des sous-arbres avant de conclure par hauteur 1.
- Résultat : hauteur 1.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Oublier le cas arbre vide.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « nœud feuille » et valider `+, 2, 3`.
- Résultat : `+, 2, 3`.
- Contrôle : comparer avec le cas « nœud feuille ».
- Erreur traitée : EF3 - Mélanger parcours préfixe et infixe.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Évaluer un opérateur avant ses opérandes. » puis reprendre la procédure correcte.
- Résultat : `20`.
- Contrôle : corriger l’erreur « Évaluer un opérateur avant ses opérandes. ».
- Erreur traitée : EF4 - Évaluer un opérateur avant ses opérandes.
### Corrigé exercice 5
- Méthode : identifier `7`, appliquer la méthode « reconnaître l’absence de fils », puis écrire hauteur 0.
- Résultat : le comportement de arbre feuille est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Confondre hauteur et nombre de nœuds.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de prendre 1 plus le maximum des hauteurs des sous-arbres avant de conclure par hauteur 1.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Oublier le cas arbre vide. » est une erreur.
- Erreur traitée : EF2 - Oublier le cas arbre vide.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « nœud feuille » et valider `+, 2, 3`.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Mélanger parcours préfixe et infixe.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Évaluer un opérateur avant ses opérandes. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Remonter les valeurs depuis les feuilles vers la racine. ».
- Erreur traitée : EF4 - Évaluer un opérateur avant ses opérandes.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « arbre vide » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « nœud feuille » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Évaluer un opérateur avant ses opérandes. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Oublier le cas arbre vide. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Remonter les valeurs depuis les feuilles vers la racine. » ».
## Erreurs fréquentes
- Erreur fréquente EF1 - Confondre hauteur et nombre de nœuds.
- Erreur fréquente EF2 - Oublier le cas arbre vide.
- Erreur fréquente EF3 - Mélanger parcours préfixe et infixe.
- Erreur fréquente EF4 - Évaluer un opérateur avant ses opérandes.

## Remédiation ciblée
- Activité corrective EF1 : Calculer séparément hauteur gauche et droite.
- Activité corrective EF2 : Décider une convention pour l’arbre vide puis l’appliquer partout.
- Activité corrective EF3 : Écrire l’ordre de visite au-dessus de chaque nœud.
- Activité corrective EF4 : Remonter les valeurs depuis les feuilles vers la racine.

## Différenciation
- Socle : traiter `7` avec une fiche méthode fournie.
- Standard : traiter racine avec deux feuilles en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « nœud feuille » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
