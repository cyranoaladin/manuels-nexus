---
title: "T04 - Corrige - Récursivité"
level: "terminale"
sequence_id: "T04"
document_type: "corrige"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Langage et preuve de terminaison"
notion: "appel récursif, cas de base, terminaison, pile d’appels"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-LANG-02A"
    - "T-LANG-02B"
---


# T04 - Corrigé professeur - Récursivité

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-LANG-02A
- T-LANG-02B
- T-LANG-04A

## Prérequis
- Reconnaître une consigne liée à appel récursif.
- Distinguer donnée, méthode et conclusion dans le thème Langage et preuve de terminaison.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T04-S1 à T04-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un algorithme de parcours doit traiter une structure définie en se ramenant à un sous-problème plus petit.

## Activité d’entrée
1. Identifier le cas de base d’une factorielle.
2. Suivre les appels de `somme([4, 1, 3])`.
3. Comparer récursif et itératif.
4. Prévoir ce qui se passe sans décroissance.

## Méthode générale de correction
- Point 1 : pour factorielle, exiger la donnée `4!`, la méthode « appliquer `n * fact(n-1)` jusqu’au cas `0!` » et le contrôle « entier négatif refusé ».
- Point 2 : pour somme de liste, exiger la donnée `[4, 1, 3]`, la méthode « séparer tête et reste » et le contrôle « liste vide ».
- Point 3 : pour longueur, exiger la donnée `["a", "b"]`, la méthode « ajouter 1 à la longueur du reste » et le contrôle « reste vide ».
- Point 4 : pour terminaison, exiger la donnée `n` décroît vers 0, la méthode « montrer une mesure entière strictement décroissante » et le contrôle « appel avec même argument ».
## Exercices numérotés
- Exercice 1 : résoudre factorielle avec `4!` ; attendu : `24`.
- Exercice 2 : expliquer somme de liste à partir de `[4, 1, 3]` ; attendu : `8`.
- Exercice 3 : comparer longueur avec `["a", "b"]` ; attendu : `2`.
- Exercice 4 : corriger terminaison pour `n` décroît vers 0 ; attendu : preuve de terminaison.
- Exercice 5 : tester un cas limite lié à entier négatif refusé ; attendu : le comportement de factorielle est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour somme de liste ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise longueur avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur terminaison ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `4!`, appliquer la méthode « appliquer `n * fact(n-1)` jusqu’au cas `0!` », puis écrire `24`.
- Résultat : `24`.
- Contrôle : faire apparaître le contrôle « entier négatif refusé ».
- Erreur traitée : EF1 - Oublier le cas de base.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de séparer tête et reste avant de conclure par `8`.
- Résultat : `8`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Faire un appel récursif qui ne rapproche pas du cas de base.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « reste vide » et valider `2`.
- Résultat : `2`.
- Contrôle : comparer avec le cas « reste vide ».
- Erreur traitée : EF3 - Confondre valeur retournée et affichage des appels.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Ne pas traiter l’entrée vide. » puis reprendre la procédure correcte.
- Résultat : preuve de terminaison.
- Contrôle : corriger l’erreur « Ne pas traiter l’entrée vide. ».
- Erreur traitée : EF4 - Ne pas traiter l’entrée vide.
### Corrigé exercice 5
- Méthode : identifier `4!`, appliquer la méthode « appliquer `n * fact(n-1)` jusqu’au cas `0!` », puis écrire `24`.
- Résultat : le comportement de factorielle est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Oublier le cas de base.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de séparer tête et reste avant de conclure par `8`.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Faire un appel récursif qui ne rapproche pas du cas de base. » est une erreur.
- Erreur traitée : EF2 - Faire un appel récursif qui ne rapproche pas du cas de base.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « reste vide » et valider `2`.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Confondre valeur retournée et affichage des appels.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Ne pas traiter l’entrée vide. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Tester d’abord la liste vide ou `n = 0`. ».
- Erreur traitée : EF4 - Ne pas traiter l’entrée vide.

### Corrigé exercice 9
- Méthode : identifier le paradigme de chaque implémentation par ses traits distinctifs.
- Résultat : impératif (boucle for, variable mutable), fonctionnel (récursion), objet (classe).
- Contrôle : la version récursive risque RecursionError pour n=10000 car l'addition `lst[0] + …` reste en attente sur la pile à chaque appel (appel non terminal — Python ne pratique pas l'élimination d'appel terminal).
- Erreur traitée : confondre récursion et itération comme paradigmes interchangeables.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « entier négatif refusé » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « reste vide » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Ne pas traiter l’entrée vide. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Faire un appel récursif qui ne rapproche pas du cas de base. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Tester d’abord la liste vide ou `n = 0`. » ».
## Erreurs fréquentes
- Erreur fréquente EF1 - Oublier le cas de base.
- Erreur fréquente EF2 - Faire un appel récursif qui ne rapproche pas du cas de base.
- Erreur fréquente EF3 - Confondre valeur retournée et affichage des appels.
- Erreur fréquente EF4 - Ne pas traiter l’entrée vide.

## Remédiation ciblée
- Activité corrective EF1 : Encadrer le cas de base avant d’écrire l’appel récursif.
- Activité corrective EF2 : Tracer la valeur de l’argument à chaque appel.
- Activité corrective EF3 : Dessiner la pile d’appels avec valeurs de retour.
- Activité corrective EF4 : Tester d’abord la liste vide ou `n = 0`.

## Différenciation
- Socle : traiter `4!` avec une fiche méthode fournie.
- Standard : traiter `[4, 1, 3]` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « reste vide » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
