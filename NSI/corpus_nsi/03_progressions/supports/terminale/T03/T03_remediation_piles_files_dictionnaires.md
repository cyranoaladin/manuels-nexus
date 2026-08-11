---
title: "T03 - Remediation - Piles, files et dictionnaires"
level: "terminale"
sequence_id: "T03"
document_type: "remediation"
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
---


# T03 - Remédiation - Piles, files et dictionnaires

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-03A

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

### Remédiation EF1
- Erreur fréquente EF1 - Inverser LIFO et FIFO.
- Diagnostic : refaire pile avec empiler A puis B, dépiler et repérer l’étape fautive.
- Activité corrective EF1 : Jouer les opérations avec des cartes empilées puis alignées.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « pile vide ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF2
- Erreur fréquente EF2 - Retirer dans une structure vide sans test.
- Diagnostic : refaire file avec enfiler A puis B, défiler et repérer l’étape fautive.
- Activité corrective EF2 : Écrire le test `est_vide` avant chaque retrait.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « file vide ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF3
- Erreur fréquente EF3 - Parcourir tout un dictionnaire pour une clé connue.
- Diagnostic : refaire dictionnaire avec `{"id7": "ok"}` et repérer l’étape fautive.
- Activité corrective EF3 : Remplacer une boucle de recherche par un accès par clé.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « clé absente ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF4
- Erreur fréquente EF4 - Confondre clé et valeur.
- Diagnostic : refaire complexité avec accès par identifiant et repérer l’étape fautive.
- Activité corrective EF4 : Surligner clés et valeurs de couleurs différentes.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « collision abstraite hors programme ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
## Exercices numérotés
- Exercice 1 : résoudre pile avec empiler A puis B, dépiler ; attendu : B sort en premier.
- Exercice 2 : expliquer file à partir de enfiler A puis B, défiler ; attendu : A sort en premier.
- Exercice 3 : comparer dictionnaire avec `{"id7": "ok"}` ; attendu : `ok`.
- Exercice 4 : corriger complexité pour accès par identifiant ; attendu : accès attendu constant.
- Exercice 5 : tester un cas limite lié à pile vide ; attendu : le comportement de pile est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour file ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur complexité ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier empiler A puis B, dépiler, appliquer la méthode « appliquer LIFO », puis écrire B sort en premier ; résultat : B sort en premier ; contrôle : faire apparaître le contrôle « pile vide ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de appliquer FIFO avant de conclure par A sort en premier ; résultat : A sort en premier ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `ok` ; résultat : `ok` ; contrôle : comparer avec le cas « clé absente ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Confondre clé et valeur. » puis reprendre la procédure correcte ; résultat : accès attendu constant ; contrôle : corriger l’erreur « Confondre clé et valeur. ».
- Corrigé exercice 5 : méthode : identifier empiler A puis B, dépiler, appliquer la méthode « appliquer LIFO », puis écrire B sort en premier ; résultat : le comportement de pile est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de appliquer FIFO avant de conclure par A sort en premier ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Retirer dans une structure vide sans test. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `ok` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Confondre clé et valeur. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Surligner clés et valeurs de couleurs différentes. ».

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
