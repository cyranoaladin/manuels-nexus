---
title: "T02 - Evaluation - Classes et objets"
level: "terminale"
sequence_id: "T02"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Programmation orientée objet"
notion: "classe, attribut, méthode, invariant"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-02A"
    - "T-STRUCT-02B"
---


# T02 - Évaluation courte - Classes et objets

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-02A
- T-STRUCT-02B

## Prérequis
- Reconnaître une consigne liée à classe.
- Distinguer donnée, méthode et conclusion dans le thème Programmation orientée objet.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T02-S1 à T02-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une application de gestion de comptes doit garantir qu’aucune opération ne crée un solde incohérent.

## Activité d’entrée
1. Identifier attributs et méthodes d’un compte.
2. Écrire l’invariant `solde >= 0`.
3. Prévoir un dépôt puis un retrait.
4. Décider quoi faire si le retrait dépasse le solde.

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : T-STRUCT-02A.
- Énoncé : résoudre constructeur avec `Compte("Ada", 20)`.
- Réponse attendue : propriétaire Ada, solde 20.
- Critère de réussite : méthode visible, résultat correct et contrôle « solde initial négatif ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : T-STRUCT-02A, T-STRUCT-02B.
- Énoncé : expliquer méthode dépôt à partir de dépôt de 15.
- Réponse attendue : solde augmenté de 15.
- Critère de réussite : méthode visible, résultat correct et contrôle « montant nul ou négatif ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : T-STRUCT-02A.
- Énoncé : comparer méthode retrait avec retrait de 7 sur solde 20.
- Réponse attendue : solde 13.
- Critère de réussite : méthode visible, résultat correct et contrôle « retrait supérieur au solde ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : T-STRUCT-02A.
- Énoncé : corriger représentation pour `repr(compte)`.
- Réponse attendue : résumé lisible.
- Critère de réussite : méthode visible, résultat correct et contrôle « nom vide ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à solde initial négatif.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à montant nul ou négatif.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à retrait supérieur au solde.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à nom vide.
## Erreurs fréquentes
- Erreur fréquente EF1 - Modifier directement un attribut sans passer par la méthode.
- Erreur fréquente EF2 - Oublier de maintenir l’invariant.
- Erreur fréquente EF3 - Utiliser une variable globale pour l’état de l’objet.
- Erreur fréquente EF4 - Confondre classe et instance.

## Remédiation ciblée
- Activité corrective EF1 : Tracer l’état avant et après chaque méthode.
- Activité corrective EF2 : Écrire l’invariant en marge de chaque opération.
- Activité corrective EF3 : Créer deux comptes pour vérifier l’indépendance des états.
- Activité corrective EF4 : Colorer définition de classe, constructeur et instance.

## Différenciation
- Socle : traiter `Compte("Ada", 20)` avec une fiche méthode fournie.
- Standard : traiter dépôt de 15 en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « retrait supérieur au solde » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour T02.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour T02.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour T02.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour T02.

## Corrigé
### Corrigé question 1
- Résultat attendu : propriétaire Ada, solde 20.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « solde initial négatif ».
### Corrigé question 2
- Résultat attendu : solde augmenté de 15.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « montant nul ou négatif ».
### Corrigé question 3
- Résultat attendu : solde 13.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « retrait supérieur au solde ».
### Corrigé question 4
- Résultat attendu : résumé lisible.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « nom vide ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche classes et objets, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- T-STRUCT-02A
- T-STRUCT-02B

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence T02, statut `needs_review`.
- Séance liée : `T02-S1`, avec question centrée sur attributs, méthodes et invariants.
- Version aménagée : données attributs, méthodes et invariants surlignées et tableau réponse en trois zones.
- Remédiation : instancier un objet minimal puis lire un attribut, puis verbaliser la méthode en binôme.

