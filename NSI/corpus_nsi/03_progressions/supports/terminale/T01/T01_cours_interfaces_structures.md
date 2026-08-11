---
title: "T01 - Cours - Interfaces et structures"
level: "terminale"
sequence_id: "T01"
document_type: "cours"
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

# T01 - Cours - Interfaces et structures

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

## Définitions et formalisation
- Définition D1 : interface est utilisé dans Structures de données abstraites avec une donnée, une règle et un contrôle.
- Définition D2 : invariant est utilisé dans Structures de données abstraites avec une donnée, une règle et un contrôle.
- Définition D3 : pile est utilisé dans Structures de données abstraites avec une donnée, une règle et un contrôle.
- Définition D4 : file est utilisé dans Structures de données abstraites avec une donnée, une règle et un contrôle.
- Cas limite principal : dépilement vide.

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
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : T-STRUCT-01A.
- Point de départ : `push`, `pop`, `is_empty`.
- Angle disciplinaire : repérage initial autour de interface pile.
- Démarche attendue : décrire contrat d’entrée et résultat de chaque opération.
- Exemple associé : interface indépendante du stockage.
- Point de vigilance : Confondre interface et implémentation.
- Activité de reprise associée : Écrire le contrat avant le choix de représentation.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : T-STRUCT-01A.
- Point de départ : taille après deux empilements.
- Angle disciplinaire : méthode guidée autour de invariant.
- Démarche attendue : relier nombre d’éléments et opérations réalisées.
- Exemple associé : taille augmentée de 2.
- Point de vigilance : Tester un attribut interne au lieu de l’opération publique.
- Activité de reprise associée : Réécrire les tests en utilisant seulement les méthodes publiques.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : T-STRUCT-01A.
- Point de départ : arrivées A puis B.
- Angle disciplinaire : transfert argumenté autour de file.
- Démarche attendue : sortir dans l’ordre FIFO.
- Exemple associé : A sort avant B.
- Point de vigilance : Oublier l’état vide.
- Activité de reprise associée : Faire une trace d’opérations depuis la structure vide.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : T-STRUCT-01A.
- Point de départ : liste interne `_items`.
- Angle disciplinaire : vérification critique autour de encapsulation.
- Démarche attendue : ne jamais dépendre du détail privé.
- Exemple associé : tests écrits sur méthodes publiques.
- Point de vigilance : Mélanger ordre LIFO et ordre FIFO.
- Activité de reprise associée : Comparer une pile et une file avec la même suite d’entrées.
- Mini-production : produire une correction d’erreur avec un nouveau test.
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre interface pile avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « dépilement vide » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre invariant avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « opération refusée » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre file avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « file vide » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre encapsulation avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « changement de représentation » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier interface pile à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier invariant à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier file à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier encapsulation à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- interface : terme à employer dans une justification écrite de la séquence.
- invariant : terme à employer dans une justification écrite de la séquence.
- pile : terme à employer dans une justification écrite de la séquence.
- file : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante T01-A : modifier la donnée du premier exemple de T01 - Cours - Interfaces et structures et conserver exactement la même méthode.
- Variante T01-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante T01-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante T01-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante T01-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante T01-F : construire une donnée minimale qui force une décision de méthode.
- Variante T01-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante T01-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante T01-I : relier une erreur fréquente à une activité corrective précise.
- Variante T01-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante T01-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante T01-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante T01-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante T01-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante T01-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante T01-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
