---
title: "T01 - Remediation - Interfaces et structures"
level: "terminale"
sequence_id: "T01"
document_type: "remediation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures de données abstraites"
notion: "interface, invariant, pile, file"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-01A"
---


# T01 - Remédiation - Interfaces et structures

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-01A

## Prérequis
- Reconnaître une consigne liée à interface.
- Distinguer donnée, méthode et conclusion dans le thème Structures de données abstraites.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T01-S1 à T01-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un module doit exposer une pile sans révéler si elle est stockée par liste Python ou par maillons.

## Activité d’entrée
1. Lister les opérations d’une pile.
2. Écrire un invariant après empilement.
3. Comparer interface et représentation.
4. Prévoir le comportement sur structure vide.

### Remédiation EF1
- Erreur fréquente EF1 - Confondre interface et implémentation.
- Diagnostic : refaire interface pile avec `push`, `pop`, `is_empty` et repérer l’étape fautive.
- Activité corrective EF1 : Écrire le contrat avant le choix de représentation.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « dépilement vide ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF2
- Erreur fréquente EF2 - Tester un attribut interne au lieu de l’opération publique.
- Diagnostic : refaire invariant avec taille après deux empilements et repérer l’étape fautive.
- Activité corrective EF2 : Réécrire les tests en utilisant seulement les méthodes publiques.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « opération refusée ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF3
- Erreur fréquente EF3 - Oublier l’état vide.
- Diagnostic : refaire file avec arrivées A puis B et repérer l’étape fautive.
- Activité corrective EF3 : Faire une trace d’opérations depuis la structure vide.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « file vide ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF4
- Erreur fréquente EF4 - Mélanger ordre LIFO et ordre FIFO.
- Diagnostic : refaire encapsulation avec liste interne `_items` et repérer l’étape fautive.
- Activité corrective EF4 : Comparer une pile et une file avec la même suite d’entrées.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « changement de représentation ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
## Exercices numérotés
- Exercice 1 : résoudre interface pile avec `push`, `pop`, `is_empty` ; attendu : interface indépendante du stockage.
- Exercice 2 : expliquer invariant à partir de taille après deux empilements ; attendu : taille augmentée de 2.
- Exercice 3 : comparer file avec arrivées A puis B ; attendu : A sort avant B.
- Exercice 4 : corriger encapsulation pour liste interne `_items` ; attendu : tests écrits sur méthodes publiques.
- Exercice 5 : tester un cas limite lié à dépilement vide ; attendu : le comportement de interface pile est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour invariant ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise file avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur encapsulation ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `push`, `pop`, `is_empty`, appliquer la méthode « décrire contrat d’entrée et résultat de chaque opération », puis écrire interface indépendante du stockage ; résultat : interface indépendante du stockage ; contrôle : faire apparaître le contrôle « dépilement vide ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de relier nombre d’éléments et opérations réalisées avant de conclure par taille augmentée de 2 ; résultat : taille augmentée de 2 ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « file vide » et valider A sort avant B ; résultat : A sort avant B ; contrôle : comparer avec le cas « file vide ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Mélanger ordre LIFO et ordre FIFO. » puis reprendre la procédure correcte ; résultat : tests écrits sur méthodes publiques ; contrôle : corriger l’erreur « Mélanger ordre LIFO et ordre FIFO. ».
- Corrigé exercice 5 : méthode : identifier `push`, `pop`, `is_empty`, appliquer la méthode « décrire contrat d’entrée et résultat de chaque opération », puis écrire interface indépendante du stockage ; résultat : le comportement de interface pile est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de relier nombre d’éléments et opérations réalisées avant de conclure par taille augmentée de 2 ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Tester un attribut interne au lieu de l’opération publique. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « file vide » et valider A sort avant B ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Mélanger ordre LIFO et ordre FIFO. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Comparer une pile et une file avec la même suite d’entrées. ».

## Erreurs fréquentes
- Erreur fréquente EF1 - Confondre interface et implémentation.
- Erreur fréquente EF2 - Tester un attribut interne au lieu de l’opération publique.
- Erreur fréquente EF3 - Oublier l’état vide.
- Erreur fréquente EF4 - Mélanger ordre LIFO et ordre FIFO.

## Remédiation ciblée
- Activité corrective EF1 : Écrire le contrat avant le choix de représentation.
- Activité corrective EF2 : Réécrire les tests en utilisant seulement les méthodes publiques.
- Activité corrective EF3 : Faire une trace d’opérations depuis la structure vide.
- Activité corrective EF4 : Comparer une pile et une file avec la même suite d’entrées.

## Différenciation
- Socle : traiter `push`, `pop`, `is_empty` avec une fiche méthode fournie.
- Standard : traiter taille après deux empilements en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « file vide » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
