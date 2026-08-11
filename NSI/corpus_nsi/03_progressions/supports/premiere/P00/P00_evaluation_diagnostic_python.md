---
title: "P00 - Evaluation - Diagnostic Python"
level: "premiere"
sequence_id: "P00"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Rentrée et méthode"
notion: "affectation, type, condition, trace d’exécution"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-LANG-01"
---


# P00 - Évaluation courte - Diagnostic Python

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-LANG-01

## Prérequis
- Reconnaître une consigne liée à affectation.
- Distinguer donnée, méthode et conclusion dans le thème Rentrée et méthode.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P00-S1 à P00-S4 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un groupe reçoit quatre fragments Python issus de copies anonymisées et doit prédire les valeurs affichées avant d’exécuter le programme.

## Activité d’entrée
1. Repérer les variables modifiées dans `x = 4 ; x = x + 3 ; print(x)`.
2. Séparer valeur stockée, expression évaluée et affichage produit.
3. Comparer une prédiction papier avec une exécution Python.
4. Identifier la première instruction qui explique une divergence.

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : P-LANG-01.
- Énoncé : résoudre trace d’affectation avec `x = 4 ; x = x + 3 ; print(x)`.
- Réponse attendue : `7` affiché.
- Critère de réussite : méthode visible, résultat correct et contrôle « variable réaffectée deux fois ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : P-LANG-01.
- Énoncé : expliquer concaténation de chaînes à partir de `mot = "NS" ; mot = mot + "I"`.
- Réponse attendue : `"NSI"`.
- Critère de réussite : méthode visible, résultat correct et contrôle « addition impossible entre chaîne et entier ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : P-LANG-01.
- Énoncé : comparer test conditionnel avec `n = 6 ; n % 2 == 0`.
- Réponse attendue : `True`.
- Critère de réussite : méthode visible, résultat correct et contrôle « reste nul ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : P-LANG-01.
- Énoncé : corriger fonction courte pour `def f(a): return 2*a + 1` avec `a = 5`.
- Réponse attendue : `11` retourné.
- Critère de réussite : méthode visible, résultat correct et contrôle « aucun affichage sans `print` ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à variable réaffectée deux fois.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à addition impossible entre chaîne et entier.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à reste nul.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à aucun affichage sans `print`.
## Erreurs fréquentes
- Erreur fréquente EF1 - Lire le signe égal comme une égalité mathématique permanente.
- Erreur fréquente EF2 - Confondre affichage et valeur retournée par une fonction.
- Erreur fréquente EF3 - Oublier de tester la valeur zéro dans une fonction numérique.
- Erreur fréquente EF4 - Donner une sortie sans trace intermédiaire.

## Remédiation ciblée
- Activité corrective EF1 : Construire un tableau mémoire avec une ligne par instruction.
- Activité corrective EF2 : Colorer `print`, `return` et expression évaluée dans trois colonnes.
- Activité corrective EF3 : Ajouter les tests `0`, `1` et `-1` avant les cas ordinaires.
- Activité corrective EF4 : Écrire une justification en deux phrases : état avant, état après.

## Différenciation
- Socle : traiter `x = 4 ; x = x + 3 ; print(x)` avec une fiche méthode fournie.
- Standard : traiter `mot = "NS" ; mot = mot + "I"` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « reste nul » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour P00.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour P00.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour P00.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour P00.

## Corrigé
### Corrigé question 1
- Résultat attendu : `7` affiché.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « variable réaffectée deux fois ».
### Corrigé question 2
- Résultat attendu : `"NSI"`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « addition impossible entre chaîne et entier ».
### Corrigé question 3
- Résultat attendu : `True`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « reste nul ».
### Corrigé question 4
- Résultat attendu : `11` retourné.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « aucun affichage sans `print` ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche diagnostic Python annotée, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- P-LANG-01

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence P00, statut `needs_review`.
- Séance liée : `P00-S1`, avec question centrée sur variables, types et trace.
- Version aménagée : données variables, types et trace surlignées et tableau réponse en trois zones.
- Remédiation : reprendre la trace mémoire avec deux instructions seulement, puis verbaliser la méthode en binôme.

