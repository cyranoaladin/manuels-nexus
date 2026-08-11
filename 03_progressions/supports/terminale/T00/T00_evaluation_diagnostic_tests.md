---
title: "T00 - Evaluation - Diagnostic tests"
level: "terminale"
sequence_id: "T00"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Reprise Python et tests"
notion: "fonction, assertion, cas limite, spécification"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-LANG-03A"
---


# T00 - Évaluation courte - Diagnostic tests

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-LANG-03A

## Prérequis
- Reconnaître une consigne liée à fonction.
- Distinguer donnée, méthode et conclusion dans le thème Reprise Python et tests.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T00-S1 à T00-S4 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une équipe reprend une bibliothèque Python de Première et doit écrire des tests avant de modifier le code.

## Activité d’entrée
1. Écrire le résultat attendu pour une fonction `maximum`.
2. Choisir un cas nominal, un cas limite et un cas invalide.
3. Distinguer spécification et implémentation.
4. Lire un message d’assertion échouée.

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : T-LANG-03A.
- Énoncé : résoudre maximum nominal avec `[3, 7, 2]`.
- Réponse attendue : `7`.
- Critère de réussite : méthode visible, résultat correct et contrôle « liste d’un élément ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : T-LANG-03A.
- Énoncé : expliquer liste vide à partir de `[]`.
- Réponse attendue : exception documentée.
- Critère de réussite : méthode visible, résultat correct et contrôle « aucune valeur initiale ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : T-LANG-03A.
- Énoncé : comparer assertion avec `assert maximum([1]) == 1`.
- Réponse attendue : test passant.
- Critère de réussite : méthode visible, résultat correct et contrôle « message utile en cas d’échec ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : T-LANG-03A.
- Énoncé : corriger entrée invalide pour `[1, "x"]`.
- Réponse attendue : erreur contrôlée.
- Critère de réussite : méthode visible, résultat correct et contrôle « comparaison impossible ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à liste d’un élément.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à aucune valeur initiale.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à message utile en cas d’échec.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à comparaison impossible.
## Erreurs fréquentes
- Erreur fréquente EF1 - Tester seulement le cas donné en exemple.
- Erreur fréquente EF2 - Écrire un test qui reproduit le code au lieu de la spécification.
- Erreur fréquente EF3 - Oublier le cas vide.
- Erreur fréquente EF4 - Ne pas lire le message d’échec.

## Remédiation ciblée
- Activité corrective EF1 : Construire un tableau cas nominal, limite, invalide.
- Activité corrective EF2 : Formuler le résultat attendu en français avant le code du test.
- Activité corrective EF3 : Ajouter systématiquement une entrée minimale.
- Activité corrective EF4 : Réécrire le message d’échec comme diagnostic.

## Différenciation
- Socle : traiter `[3, 7, 2]` avec une fiche méthode fournie.
- Standard : traiter `[]` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « message utile en cas d’échec » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour T00.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour T00.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour T00.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour T00.

## Corrigé
### Corrigé question 1
- Résultat attendu : `7`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « liste d’un élément ».
### Corrigé question 2
- Résultat attendu : exception documentée.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « aucune valeur initiale ».
### Corrigé question 3
- Résultat attendu : test passant.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « message utile en cas d’échec ».
### Corrigé question 4
- Résultat attendu : erreur contrôlée.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « comparaison impossible ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche reprise Python et tests, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- T-LANG-03A

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence T00, statut `needs_review`.
- Séance liée : `T00-S1`, avec question centrée sur tests et complexité simple.
- Version aménagée : données tests et complexité simple surlignées et tableau réponse en trois zones.
- Remédiation : reprendre un test nominal puis un test limite, puis verbaliser la méthode en binôme.

