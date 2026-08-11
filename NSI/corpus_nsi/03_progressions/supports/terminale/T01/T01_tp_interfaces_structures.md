---
title: "T01 - Tp - Interfaces et structures"
level: "terminale"
sequence_id: "T01"
document_type: "tp"
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


# T01 - TP - Interfaces et structures

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

## Consigne technique détaillée
- Problème à programmer : Implémenter une pile avec une interface stable et des tests indépendants de la représentation.
- Starter code : `code/T01_starter_interfaces_structures.py`.
- Tests attendus : `code/T01_tests_attendus_interfaces_structures.py`.
- Corrigé professeur séparé : `code/T01_corrige_professeur_interfaces_structures.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : dépilement vide.
## Étapes de réalisation
- Étape 1 : coder ou tester interface pile à partir de `push`, `pop`, `is_empty`, puis contrôler dépilement vide.
- Étape 2 : coder ou tester invariant à partir de taille après deux empilements, puis contrôler opération refusée.
- Étape 3 : coder ou tester file à partir de arrivées A puis B, puis contrôler file vide.
- Étape 4 : coder ou tester encapsulation à partir de liste interne `_items`, puis contrôler changement de représentation.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
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

## Complément TP - conformité d’un TAD
### Consigne technique détaillée
Écrire deux classes ou modules respectant les interfaces suivantes :

```python
class Pile:
    def empiler(self, x): ...
    def depiler(self): ...
    def sommet(self): ...
    def est_vide(self): ...

class File:
    def enfiler(self, x): ...
    def defiler(self): ...
    def premier(self): ...
    def est_vide(self): ...
```

### Tests attendus
- Pile : après `empiler("A")`, `empiler("B")`, `sommet()` renvoie `"B"`, puis deux appels à `depiler()` renvoient `"B"`, puis `"A"`.
- File : après `enfiler("A")`, `enfiler("B")`, `premier()` renvoie `"A"`, puis deux appels à `defiler()` renvoient `"A"`, puis `"B"`.
- File : après `enfiler("A")`, `enfiler("B")`, deux appels à `defiler()` renvoient `"A"`, puis `"B"`.
- Cas vide : `depiler()` ou `defiler()` sur structure vide lève une exception documentée.
- Complexité attendue : expliquer pourquoi une file avec `pop(0)` peut coûter `O(n)`.

### Livrable vérifiable
Le rendu contient le code, les tests de conformité, l’invariant choisi et une comparaison de deux implémentations de file.

## Validation opérationnelle du TP
- Vérification T01-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification T01-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification T01-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification T01-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification T01-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification T01-6 : comparer l’algorithme écrit avec la capacité officielle citée.
