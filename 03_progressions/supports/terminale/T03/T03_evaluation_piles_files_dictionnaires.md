---
title: "T03 - Evaluation - Piles, files et dictionnaires"
level: "terminale"
sequence_id: "T03"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures linéaires et tables associatives"
notion: "pile, file, dictionnaire, complexité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-03A"
    - "T-STRUCT-03B"
---


# T03 - Évaluation courte - Piles, files et dictionnaires

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-03A
- T-STRUCT-03B

## Prérequis
- Reconnaître une consigne liée à pile.
- Distinguer donnée, méthode et conclusion dans le thème Structures linéaires et tables associatives.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T03-S1 à T03-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un serveur journalise des tâches en attente et doit choisir entre pile, file et dictionnaire selon l’usage.

## Activité d’entrée
1. Simuler une pile sur trois opérations.
2. Simuler une file sur trois clients.
3. Utiliser un dictionnaire pour retrouver une tâche par identifiant.
4. Comparer coût de recherche et d’accès direct.

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : T-STRUCT-03A.
- Énoncé : résoudre pile avec empiler A puis B, dépiler.
- Réponse attendue : B sort en premier.
- Critère de réussite : méthode visible, résultat correct et contrôle « pile vide ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : T-STRUCT-03A.
- Énoncé : expliquer file à partir de enfiler A puis B, défiler.
- Réponse attendue : A sort en premier.
- Critère de réussite : méthode visible, résultat correct et contrôle « file vide ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : T-STRUCT-03A.
- Énoncé : comparer dictionnaire avec `{"id7": "ok"}`.
- Réponse attendue : `ok`.
- Critère de réussite : méthode visible, résultat correct et contrôle « clé absente ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : T-STRUCT-03A, T-STRUCT-03B.
- Énoncé : corriger complexité pour accès par identifiant.
- Réponse attendue : accès attendu constant.
- Critère de réussite : méthode visible, résultat correct et contrôle « collision abstraite hors programme ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à pile vide.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à file vide.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à clé absente.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à collision abstraite hors programme.
## Erreurs fréquentes
- Erreur fréquente EF1 - Inverser LIFO et FIFO.
- Erreur fréquente EF2 - Retirer dans une structure vide sans test.
- Erreur fréquente EF3 - Parcourir tout un dictionnaire pour une clé connue.
- Erreur fréquente EF4 - Confondre clé et valeur.

## Remédiation ciblée
- Activité corrective EF1 : Jouer les opérations avec des cartes empilées puis alignées.
- Activité corrective EF2 : Écrire le test `est_vide` avant chaque retrait.
- Activité corrective EF3 : Remplacer une boucle de recherche par un accès par clé.
- Activité corrective EF4 : Surligner clés et valeurs de couleurs différentes.

## Différenciation
- Socle : traiter empiler A puis B, dépiler avec une fiche méthode fournie.
- Standard : traiter enfiler A puis B, défiler en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « clé absente » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour T03.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour T03.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour T03.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour T03.

## Corrigé
### Corrigé question 1
- Résultat attendu : B sort en premier.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « pile vide ».
### Corrigé question 2
- Résultat attendu : A sort en premier.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « file vide ».
### Corrigé question 3
- Résultat attendu : `ok`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « clé absente ».
### Corrigé question 4
- Résultat attendu : accès attendu constant.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « collision abstraite hors programme ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche piles, files, dictionnaires, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- T-STRUCT-03A
- T-STRUCT-03B

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence T03, statut `needs_review`.
- Séance liée : `T03-S1`, avec question centrée sur structures linéaires.
- Version aménagée : données structures linéaires surlignées et tableau réponse en trois zones.
- Remédiation : simuler trois opérations push/pop ou enfiler/defiler, puis verbaliser la méthode en binôme.

