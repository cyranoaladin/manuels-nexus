---
title: "T00 - Corrige - Diagnostic tests"
level: "terminale"
sequence_id: "T00"
document_type: "corrige"
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


# T00 - Corrigé professeur - Diagnostic tests

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

## Méthode générale de correction
- Point 1 : pour maximum nominal, exiger la donnée `[3, 7, 2]`, la méthode « parcourir la liste en conservant le meilleur élément » et le contrôle « liste d’un élément ».
- Point 2 : pour liste vide, exiger la donnée `[]`, la méthode « refuser l’entrée avant le parcours » et le contrôle « aucune valeur initiale ».
- Point 3 : pour assertion, exiger la donnée `assert maximum([1]) == 1`, la méthode « traduire une exigence en test exécutable » et le contrôle « message utile en cas d’échec ».
- Point 4 : pour entrée invalide, exiger la donnée `[1, "x"]`, la méthode « définir si le mélange de types est autorisé » et le contrôle « comparaison impossible ».
## Exercices numérotés
- Exercice 1 : résoudre maximum nominal avec `[3, 7, 2]` ; attendu : `7`.
- Exercice 2 : expliquer liste vide à partir de `[]` ; attendu : exception documentée.
- Exercice 3 : comparer assertion avec `assert maximum([1]) == 1` ; attendu : test passant.
- Exercice 4 : corriger entrée invalide pour `[1, "x"]` ; attendu : erreur contrôlée.
- Exercice 5 : tester un cas limite lié à liste d’un élément ; attendu : le comportement de maximum nominal est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour liste vide ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise assertion avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur entrée invalide ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `[3, 7, 2]`, appliquer la méthode « parcourir la liste en conservant le meilleur élément », puis écrire `7`.
- Résultat : `7`.
- Contrôle : faire apparaître le contrôle « liste d’un élément ».
- Erreur traitée : EF1 - Tester seulement le cas donné en exemple.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de refuser l’entrée avant le parcours avant de conclure par exception documentée.
- Résultat : exception documentée.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Écrire un test qui reproduit le code au lieu de la spécification.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « message utile en cas d’échec » et valider test passant.
- Résultat : test passant.
- Contrôle : comparer avec le cas « message utile en cas d’échec ».
- Erreur traitée : EF3 - Oublier le cas vide.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Ne pas lire le message d’échec. » puis reprendre la procédure correcte.
- Résultat : erreur contrôlée.
- Contrôle : corriger l’erreur « Ne pas lire le message d’échec. ».
- Erreur traitée : EF4 - Ne pas lire le message d’échec.
### Corrigé exercice 5
- Méthode : identifier `[3, 7, 2]`, appliquer la méthode « parcourir la liste en conservant le meilleur élément », puis écrire `7`.
- Résultat : le comportement de maximum nominal est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Tester seulement le cas donné en exemple.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de refuser l’entrée avant le parcours avant de conclure par exception documentée.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Écrire un test qui reproduit le code au lieu de la spécification. » est une erreur.
- Erreur traitée : EF2 - Écrire un test qui reproduit le code au lieu de la spécification.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « message utile en cas d’échec » et valider test passant.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Oublier le cas vide.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Ne pas lire le message d’échec. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Réécrire le message d’échec comme diagnostic. ».
- Erreur traitée : EF4 - Ne pas lire le message d’échec.

### Corrigé exercice 9
- Méthode : import json, appel dumps/loads, lecture fichier avec gestion FileNotFoundError, test chaîne malformée.
- Résultat : sérialisation/désérialisation vérifiée, exception JSONDecodeError identifiée.
- Contrôle : cas d'erreur (fichier absent, JSON malformé) traités explicitement.
- Erreur traitée : utiliser une API sans gérer les exceptions documentées (FileNotFoundError, JSONDecodeError).

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « liste d’un élément » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « message utile en cas d’échec » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Ne pas lire le message d’échec. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Écrire un test qui reproduit le code au lieu de la spécification. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Réécrire le message d’échec comme diagnostic. » ».
- Exercice 9 : 1 point méthode (import + appel API), 0,5 point résultat (sérialisation/désérialisation vérifiée), 0,5 point contrôle sur « gérer FileNotFoundError et JSONDecodeError ».
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
