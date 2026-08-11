---
title: "T03 - Tp - Piles, files et dictionnaires"
level: "terminale"
sequence_id: "T03"
document_type: "tp"
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


# T03 - TP - Piles, files et dictionnaires

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

## Consigne technique détaillée
- Problème à programmer : Choisir et implémenter la structure adaptée pour gérer une file de tâches et un accès par identifiant.
- Starter code : `code/T03_starter_piles_files_dictionnaires.py`.
- Tests attendus : `code/T03_tests_attendus_piles_files_dictionnaires.py`.
- Corrigé professeur séparé : `code/T03_corrige_professeur_piles_files_dictionnaires.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : pile vide.
## Étapes de réalisation
- Étape 1 : coder ou tester pile à partir de empiler A puis B, dépiler, puis contrôler pile vide.
- Étape 2 : coder ou tester file à partir de enfiler A puis B, défiler, puis contrôler file vide.
- Étape 3 : coder ou tester dictionnaire à partir de `{"id7": "ok"}`, puis contrôler clé absente.
- Étape 4 : coder ou tester complexité à partir de accès par identifiant, puis contrôler collision abstraite hors programme.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
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

## Validation opérationnelle du TP
- Vérification T03-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification T03-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification T03-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification T03-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification T03-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification T03-6 : comparer l’algorithme écrit avec la capacité officielle citée.
