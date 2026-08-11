---
title: "T01 - Corrige - Interfaces et structures"
level: "terminale"
sequence_id: "T01"
document_type: "corrige"
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


# T01 - Corrigé professeur - Interfaces et structures

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

## Méthode générale de correction
- Point 1 : pour interface pile, exiger la donnée `push`, `pop`, `is_empty`, la méthode « décrire contrat d’entrée et résultat de chaque opération » et le contrôle « dépilement vide ».
- Point 2 : pour invariant, exiger la donnée taille après deux empilements, la méthode « relier nombre d’éléments et opérations réalisées » et le contrôle « opération refusée ».
- Point 3 : pour file, exiger la donnée arrivées A puis B, la méthode « sortir dans l’ordre FIFO » et le contrôle « file vide ».
- Point 4 : pour encapsulation, exiger la donnée liste interne `_items`, la méthode « ne jamais dépendre du détail privé » et le contrôle « changement de représentation ».
## Exercices numérotés
- Exercice 1 : résoudre interface pile avec `push`, `pop`, `is_empty` ; attendu : interface indépendante du stockage.
- Exercice 2 : expliquer invariant à partir de taille après deux empilements ; attendu : taille augmentée de 2.
- Exercice 3 : comparer file avec arrivées A puis B ; attendu : A sort avant B.
- Exercice 4 : corriger encapsulation pour liste interne `_items` ; attendu : tests écrits sur méthodes publiques.
- Exercice 5 : tester un cas limite lié à dépilement vide ; attendu : le comportement de interface pile est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour invariant ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise file avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur encapsulation ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `push`, `pop`, `is_empty`, appliquer la méthode « décrire contrat d’entrée et résultat de chaque opération », puis écrire interface indépendante du stockage.
- Résultat : interface indépendante du stockage.
- Contrôle : faire apparaître le contrôle « dépilement vide ».
- Erreur traitée : EF1 - Confondre interface et implémentation.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de relier nombre d’éléments et opérations réalisées avant de conclure par taille augmentée de 2.
- Résultat : taille augmentée de 2.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Tester un attribut interne au lieu de l’opération publique.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « file vide » et valider A sort avant B.
- Résultat : A sort avant B.
- Contrôle : comparer avec le cas « file vide ».
- Erreur traitée : EF3 - Oublier l’état vide.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Mélanger ordre LIFO et ordre FIFO. » puis reprendre la procédure correcte.
- Résultat : tests écrits sur méthodes publiques.
- Contrôle : corriger l’erreur « Mélanger ordre LIFO et ordre FIFO. ».
- Erreur traitée : EF4 - Mélanger ordre LIFO et ordre FIFO.
### Corrigé exercice 5
- Méthode : identifier `push`, `pop`, `is_empty`, appliquer la méthode « décrire contrat d’entrée et résultat de chaque opération », puis écrire interface indépendante du stockage.
- Résultat : le comportement de interface pile est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Confondre interface et implémentation.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de relier nombre d’éléments et opérations réalisées avant de conclure par taille augmentée de 2.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Tester un attribut interne au lieu de l’opération publique. » est une erreur.
- Erreur traitée : EF2 - Tester un attribut interne au lieu de l’opération publique.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « file vide » et valider A sort avant B.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Oublier l’état vide.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Mélanger ordre LIFO et ordre FIFO. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Comparer une pile et une file avec la même suite d’entrées. ».
- Erreur traitée : EF4 - Mélanger ordre LIFO et ordre FIFO.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « dépilement vide » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « file vide » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Mélanger ordre LIFO et ordre FIFO. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Tester un attribut interne au lieu de l’opération publique. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Comparer une pile et une file avec la même suite d’entrées. » ».
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

## Corrigés complémentaires TAD
### Corrigé exercice 9
- Résultat visible : `"B"`, puis `"B"`, puis `"A"`.
- Justification : une pile respecte LIFO ; l’implémentation par liste ou par maillons ne change pas l’interface.
- Contrôle : dépiler une troisième fois doit être refusé.

### Corrigé exercice 10
- Résultat visible : `"A"`, puis `"A"`, puis `"B"`.
- Justification : une file respecte FIFO.
- Contrôle : `defiler()` sur file vide lève une erreur documentée.

### Corrigé exercice 11
- Résultat attendu : liste naïve `pop(0)` en `O(n)`, file à deux listes en coût amorti `O(1)`.
- Justification : la deuxième implémentation reporte le coût du renversement sur plusieurs opérations.
- Contrôle : les deux implémentations doivent passer la même suite de tests d’interface.
