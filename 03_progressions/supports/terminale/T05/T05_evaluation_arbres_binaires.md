---
title: "T05 - Evaluation - Arbres binaires"
level: "terminale"
sequence_id: "T05"
document_type: "evaluation"
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


# T05 - Évaluation courte - Arbres binaires

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

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : T-STRUCT-04A.
- Énoncé : résoudre arbre feuille avec `7`.
- Réponse attendue : hauteur 0.
- Critère de réussite : méthode visible, résultat correct et contrôle « arbre vide ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : T-STRUCT-04A.
- Énoncé : expliquer hauteur à partir de racine avec deux feuilles.
- Réponse attendue : hauteur 1.
- Critère de réussite : méthode visible, résultat correct et contrôle « un seul fils ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : T-STRUCT-04A.
- Énoncé : comparer parcours préfixe avec `+ 2 3`.
- Réponse attendue : `+, 2, 3`.
- Critère de réussite : méthode visible, résultat correct et contrôle « nœud feuille ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : T-STRUCT-04A.
- Énoncé : corriger évaluation pour `(2 + 3) * 4`.
- Réponse attendue : `20`.
- Critère de réussite : méthode visible, résultat correct et contrôle « division par zéro si opérateur `/` ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à arbre vide.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à un seul fils.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à nœud feuille.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à division par zéro si opérateur `/`.
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

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour T05.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour T05.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour T05.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour T05.

## Corrigé
### Corrigé question 1
- Résultat attendu : hauteur 0.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « arbre vide ».
### Corrigé question 2
- Résultat attendu : hauteur 1.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « un seul fils ».
### Corrigé question 3
- Résultat attendu : `+, 2, 3`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « nœud feuille ».
### Corrigé question 4
- Résultat attendu : `20`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « division par zéro si opérateur `/` ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche arbres binaires, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- T-STRUCT-04A

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence T05, statut `needs_review`.
- Séance liée : `T05-S1`, avec question centrée sur noeuds, feuilles et parcours.
- Version aménagée : données noeuds, feuilles et parcours surlignées et tableau réponse en trois zones.
- Remédiation : reprendre un parcours infixe sur un arbre à trois noeuds, puis verbaliser la méthode en binôme.

