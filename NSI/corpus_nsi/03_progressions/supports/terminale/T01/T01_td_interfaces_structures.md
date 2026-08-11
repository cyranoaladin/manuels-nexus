---
title: "T01 - Td - Interfaces et structures"
level: "terminale"
sequence_id: "T01"
document_type: "td"
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

# T01 - TD - Interfaces et structures

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

## Exemples corrigés précis
### Exemple corrigé 1 - interface pile
- Donnée étudiée : `push`, `pop`, `is_empty`.
- Méthode : décrire contrat d’entrée et résultat de chaque opération.
- Résultat obtenu : interface indépendante du stockage.
- Contrôle : le cas limite « dépilement vide » est vérifié séparément.
### Exemple corrigé 2 - invariant
- Donnée étudiée : taille après deux empilements.
- Méthode : relier nombre d’éléments et opérations réalisées.
- Résultat obtenu : taille augmentée de 2.
- Contrôle : le cas limite « opération refusée » est vérifié séparément.
### Exemple corrigé 3 - file
- Donnée étudiée : arrivées A puis B.
- Méthode : sortir dans l’ordre FIFO.
- Résultat obtenu : A sort avant B.
- Contrôle : le cas limite « file vide » est vérifié séparément.
### Exemple corrigé 4 - encapsulation
- Donnée étudiée : liste interne `_items`.
- Méthode : ne jamais dépendre du détail privé.
- Résultat obtenu : tests écrits sur méthodes publiques.
- Contrôle : le cas limite « changement de représentation » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : résoudre interface pile avec `push`, `pop`, `is_empty`.
- Production attendue : interface indépendante du stockage.
- Contrainte de contrôle : faire apparaître le contrôle « dépilement vide ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : expliquer invariant à partir de taille après deux empilements.
- Production attendue : taille augmentée de 2.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : comparer file avec arrivées A puis B.
- Production attendue : A sort avant B.
- Contrainte de contrôle : comparer avec le cas « file vide ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : corriger encapsulation pour liste interne `_items`.
- Production attendue : tests écrits sur méthodes publiques.
- Contrainte de contrôle : corriger l’erreur « Mélanger ordre LIFO et ordre FIFO. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : tester un cas limite lié à dépilement vide.
- Production attendue : le comportement de interface pile est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : classer deux méthodes possibles pour invariant.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Tester un attribut interne au lieu de l’opération publique. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : justifier un transfert qui utilise file avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : T-STRUCT-01A.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur encapsulation.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Comparer une pile et une file avec la même suite d’entrées. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : interface indépendante du stockage.
- Contrôle : faire apparaître le contrôle « dépilement vide ».
- Erreur traitée : EF1 - Confondre interface et implémentation.
- Donnée utilisée alpha dans T01 td interfaces structures : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T01 td interfaces structures : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : taille augmentée de 2.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Tester un attribut interne au lieu de l’opération publique.
- Donnée utilisée beta dans T01 td interfaces structures : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T01 td interfaces structures : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : A sort avant B.
- Contrôle : comparer avec le cas « file vide ».
- Erreur traitée : EF3 - Oublier l’état vide.
- Donnée utilisée gamma dans T01 td interfaces structures : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T01 td interfaces structures : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : tests écrits sur méthodes publiques.
- Contrôle : corriger l’erreur « Mélanger ordre LIFO et ordre FIFO. ».
- Erreur traitée : EF4 - Mélanger ordre LIFO et ordre FIFO.
- Donnée utilisée delta dans T01 td interfaces structures : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T01 td interfaces structures : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de interface pile est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Confondre interface et implémentation.
- Donnée utilisée epsilon dans T01 td interfaces structures : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T01 td interfaces structures : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Tester un attribut interne au lieu de l’opération publique. » est une erreur.
- Erreur traitée : EF2 - Tester un attribut interne au lieu de l’opération publique.
- Donnée utilisée zeta dans T01 td interfaces structures : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T01 td interfaces structures : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Oublier l’état vide.
- Donnée utilisée eta dans T01 td interfaces structures : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T01 td interfaces structures : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Comparer une pile et une file avec la même suite d’entrées. ».
- Erreur traitée : EF4 - Mélanger ordre LIFO et ordre FIFO.
- Donnée utilisée theta dans T01 td interfaces structures : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T01 td interfaces structures : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

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

## Complément TAD - conformité pile et file
### Exercice 9 - Interface pile
- Données : opérations `empiler("A")`, `empiler("B")`, `sommet()`, `depiler()`, `depiler()`. ; jeu_exercice=alpha
- Consigne : donner les résultats visibles sans supposer l’implémentation.

### Exercice 10 - Interface file
- Données : opérations `enfiler("A")`, `enfiler("B")`, `premier()`, `defiler()`, `defiler()`. ; jeu_exercice=beta
- Consigne : donner les résultats visibles et le cas limite suivant.

### Exercice 11 - Implémentation et complexité
- Données : file par liste Python avec `pop(0)` et file à deux listes. ; jeu_exercice=gamma
- Consigne : comparer les coûts.

### Corrigé exercice 9
- Résultat attendu : `sommet()` vaut `"B"` ; le premier `depiler()` renvoie `"B"` ; le second renvoie `"A"`.
- Contrôle : les valeurs sortent dans l’ordre inverse des entrées, donc l’interface pile est respectée.
- Donnée utilisée alpha dans T01 td interfaces structures : cas alpha de l exercice 9 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T01 td interfaces structures : sortie vérifiable de l exercice 9, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 10
- Résultat attendu : `premier()` vaut `"A"` ; les deux sorties sont `"A"` puis `"B"`.
- Contrôle : un troisième `defiler()` doit lever une erreur de file vide documentée.
- Donnée utilisée beta dans T01 td interfaces structures : cas beta de l exercice 10 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T01 td interfaces structures : sortie vérifiable de l exercice 10, reliée à la capacité officielle du bloc.
- Contrôle beta dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 11
- Résultat attendu : `pop(0)` coûte `O(n)` par décalage ; la file à deux listes donne un coût amorti `O(1)` pour enfiler et défiler.
- Contrôle : la comparaison porte sur l’implémentation, pas sur l’interface abstraite commune.
- Donnée utilisée gamma dans T01 td interfaces structures : cas gamma de l exercice 11 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T01 td interfaces structures : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T01 td interfaces structures : sortie vérifiable de l exercice 11, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T01 td interfaces structures : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
