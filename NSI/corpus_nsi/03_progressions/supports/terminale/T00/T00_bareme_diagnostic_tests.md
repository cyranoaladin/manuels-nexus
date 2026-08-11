---
title: "T00 - Bareme - Diagnostic tests"
level: "terminale"
sequence_id: "T00"
document_type: "bareme"
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


# T00 - Barème - Diagnostic tests

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

### Barème question 1
- 1 point : identifier correctement maximum nominal et la donnée `[3, 7, 2]`.
- 1 point : appliquer la méthode « parcourir la liste en conservant le meilleur élément ».
- 1 point : obtenir `7`.
- 1 point : contrôler le cas limite « liste d’un élément » ou expliquer pourquoi il ne s’applique pas.
- Retrait possible : confusion avec l’erreur fréquente EF1 - Tester seulement le cas donné en exemple.
### Barème question 2
- 1 point : identifier correctement liste vide et la donnée `[]`.
- 1 point : appliquer la méthode « refuser l’entrée avant le parcours ».
- 1 point : obtenir exception documentée.
- 1 point : contrôler le cas limite « aucune valeur initiale » ou expliquer pourquoi il ne s’applique pas.
- Retrait possible : confusion avec l’erreur fréquente EF2 - Écrire un test qui reproduit le code au lieu de la spécification.
### Barème question 3
- 1 point : identifier correctement assertion et la donnée `assert maximum([1]) == 1`.
- 1 point : appliquer la méthode « traduire une exigence en test exécutable ».
- 1 point : obtenir test passant.
- 1 point : contrôler le cas limite « message utile en cas d’échec » ou expliquer pourquoi il ne s’applique pas.
- Retrait possible : confusion avec l’erreur fréquente EF3 - Oublier le cas vide.
### Barème question 4
- 1 point : identifier correctement entrée invalide et la donnée `[1, "x"]`.
- 1 point : appliquer la méthode « définir si le mélange de types est autorisé ».
- 1 point : obtenir erreur contrôlée.
- 1 point : contrôler le cas limite « comparaison impossible » ou expliquer pourquoi il ne s’applique pas.
- Retrait possible : confusion avec l’erreur fréquente EF4 - Ne pas lire le message d’échec.
## Exercices numérotés
- Exercice 1 : résoudre maximum nominal avec `[3, 7, 2]` ; attendu : `7`.
- Exercice 2 : expliquer liste vide à partir de `[]` ; attendu : exception documentée.
- Exercice 3 : comparer assertion avec `assert maximum([1]) == 1` ; attendu : test passant.
- Exercice 4 : corriger entrée invalide pour `[1, "x"]` ; attendu : erreur contrôlée.
- Exercice 5 : tester un cas limite lié à liste d’un élément ; attendu : le comportement de maximum nominal est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour liste vide ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise assertion avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur entrée invalide ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `[3, 7, 2]`, appliquer la méthode « parcourir la liste en conservant le meilleur élément », puis écrire `7` ; résultat : `7` ; contrôle : faire apparaître le contrôle « liste d’un élément ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de refuser l’entrée avant le parcours avant de conclure par exception documentée ; résultat : exception documentée ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « message utile en cas d’échec » et valider test passant ; résultat : test passant ; contrôle : comparer avec le cas « message utile en cas d’échec ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Ne pas lire le message d’échec. » puis reprendre la procédure correcte ; résultat : erreur contrôlée ; contrôle : corriger l’erreur « Ne pas lire le message d’échec. ».
- Corrigé exercice 5 : méthode : identifier `[3, 7, 2]`, appliquer la méthode « parcourir la liste en conservant le meilleur élément », puis écrire `7` ; résultat : le comportement de maximum nominal est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de refuser l’entrée avant le parcours avant de conclure par exception documentée ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Écrire un test qui reproduit le code au lieu de la spécification. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « message utile en cas d’échec » et valider test passant ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Ne pas lire le message d’échec. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Réécrire le message d’échec comme diagnostic. ».

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
