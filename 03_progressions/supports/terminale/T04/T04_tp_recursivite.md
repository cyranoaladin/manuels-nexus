---
title: "T04 - Tp - Récursivité"
level: "terminale"
sequence_id: "T04"
document_type: "tp"
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


# T04 - TP - Récursivité

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-LANG-02A
- T-LANG-02B

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

## Consigne technique détaillée
- Problème à programmer : Écrire trois fonctions récursives avec cas de base, mesure décroissante et tests de terminaison.
- Starter code : `code/T04_starter_recursivite.py`.
- Tests attendus : `code/T04_tests_attendus_recursivite.py`.
- Corrigé professeur séparé : `code/T04_corrige_professeur_recursivite.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : entier négatif refusé.
## Étapes de réalisation
- Étape 1 : coder ou tester factorielle à partir de `4!`, puis contrôler entier négatif refusé.
- Étape 2 : coder ou tester somme de liste à partir de `[4, 1, 3]`, puis contrôler liste vide.
- Étape 3 : coder ou tester longueur à partir de `["a", "b"]`, puis contrôler reste vide.
- Étape 4 : coder ou tester terminaison à partir de `n` décroît vers 0, puis contrôler appel avec même argument.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
## Exercices numérotés
- Exercice 1 : résoudre factorielle avec `4!` ; attendu : `24`.
- Exercice 2 : expliquer somme de liste à partir de `[4, 1, 3]` ; attendu : `8`.
- Exercice 3 : comparer longueur avec `["a", "b"]` ; attendu : `2`.
- Exercice 4 : corriger terminaison pour `n` décroît vers 0 ; attendu : preuve de terminaison.
- Exercice 5 : tester un cas limite lié à entier négatif refusé ; attendu : le comportement de factorielle est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour somme de liste ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise longueur avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur terminaison ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `4!`, appliquer la méthode « appliquer `n * fact(n-1)` jusqu’au cas `0!` », puis écrire `24` ; résultat : `24` ; contrôle : faire apparaître le contrôle « entier négatif refusé ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de séparer tête et reste avant de conclure par `8` ; résultat : `8` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « reste vide » et valider `2` ; résultat : `2` ; contrôle : comparer avec le cas « reste vide ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Ne pas traiter l’entrée vide. » puis reprendre la procédure correcte ; résultat : preuve de terminaison ; contrôle : corriger l’erreur « Ne pas traiter l’entrée vide. ».
- Corrigé exercice 5 : méthode : identifier `4!`, appliquer la méthode « appliquer `n * fact(n-1)` jusqu’au cas `0!` », puis écrire `24` ; résultat : le comportement de factorielle est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de séparer tête et reste avant de conclure par `8` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Faire un appel récursif qui ne rapproche pas du cas de base. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « reste vide » et valider `2` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Ne pas traiter l’entrée vide. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Tester d’abord la liste vide ou `n = 0`. ».

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

## Validation opérationnelle du TP
- Vérification T04-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification T04-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification T04-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification T04-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification T04-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification T04-6 : comparer l’algorithme écrit avec la capacité officielle citée.
