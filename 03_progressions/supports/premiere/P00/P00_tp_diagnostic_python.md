---
title: "P00 - Tp - Diagnostic Python"
level: "premiere"
sequence_id: "P00"
document_type: "tp"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Rentrée et méthode"
notion: "affectation, type, condition, trace d’exécution"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-LANG-01"
---


# P00 - TP - Diagnostic Python

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-LANG-01

## Prérequis
- Reconnaître une consigne liée à affectation.
- Distinguer donnée, méthode et conclusion dans le thème Rentrée et méthode.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P00-S1 à P00-S4 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un groupe reçoit quatre fragments Python issus de copies anonymisées et doit prédire les valeurs affichées avant d’exécuter le programme.

## Activité d’entrée
1. Repérer les variables modifiées dans `x = 4 ; x = x + 3 ; print(x)`.
2. Séparer valeur stockée, expression évaluée et affichage produit.
3. Comparer une prédiction papier avec une exécution Python.
4. Identifier la première instruction qui explique une divergence.

## Consigne technique détaillée
- Problème à programmer : Compléter une fonction qui simule une trace mémoire simple sans exécuter le code reçu.
- Starter code : `code/P00_starter_diagnostic_python.py`.
- Tests attendus : `code/P00_tests_attendus_diagnostic_python.py`.
- Corrigé professeur séparé : `code/P00_corrige_professeur_diagnostic_python.py`.
- Livrable vérifiable : fichier Python complété, sortie de tests nominal, limite et invalide, puis commentaire de deux lignes sur le cas limite.
- Exemple d’exécution : lancer les tests avec `TP_MODULE` pointant vers le module à contrôler.
- Cas limite principal : variable réaffectée deux fois.
## Étapes de réalisation
- Étape 1 : coder ou tester trace d’affectation à partir de `x = 4 ; x = x + 3 ; print(x)`, puis contrôler variable réaffectée deux fois.
- Étape 2 : coder ou tester concaténation de chaînes à partir de `mot = "NS" ; mot = mot + "I"`, puis contrôler addition impossible entre chaîne et entier.
- Étape 3 : coder ou tester test conditionnel à partir de `n = 6 ; n % 2 == 0`, puis contrôler reste nul.
- Étape 4 : coder ou tester fonction courte à partir de `def f(a): return 2*a + 1` avec `a = 5`, puis contrôler aucun affichage sans `print`.
## Tests attendus
- Test nominal : donnée ordinaire issue du premier exemple.
- Test limite : entrée minimale, vide ou borne de représentation.
- Test invalide : type ou valeur explicitement refusé par la spécification.
## Exercices numérotés
- Exercice 1 : résoudre trace d’affectation avec `x = 4 ; x = x + 3 ; print(x)` ; attendu : `7` affiché.
- Exercice 2 : expliquer concaténation de chaînes à partir de `mot = "NS" ; mot = mot + "I"` ; attendu : `"NSI"`.
- Exercice 3 : comparer test conditionnel avec `n = 6 ; n % 2 == 0` ; attendu : `True`.
- Exercice 4 : corriger fonction courte pour `def f(a): return 2*a + 1` avec `a = 5` ; attendu : `11` retourné.
- Exercice 5 : tester un cas limite lié à variable réaffectée deux fois ; attendu : le comportement de trace d’affectation est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour concaténation de chaînes ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise test conditionnel avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur fonction courte ; attendu : l’erreur est localisée puis réparée.

## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `x = 4 ; x = x + 3 ; print(x)`, appliquer la méthode « dresser une table instruction, expression calculée, nouvelle valeur », puis écrire `7` affiché ; résultat : `7` affiché ; contrôle : faire apparaître le contrôle « variable réaffectée deux fois ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de identifier le type chaîne puis appliquer `+` comme concaténation avant de conclure par `"NSI"` ; résultat : `"NSI"` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « reste nul » et valider `True` ; résultat : `True` ; contrôle : comparer avec le cas « reste nul ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Donner une sortie sans trace intermédiaire. » puis reprendre la procédure correcte ; résultat : `11` retourné ; contrôle : corriger l’erreur « Donner une sortie sans trace intermédiaire. ».
- Corrigé exercice 5 : méthode : identifier `x = 4 ; x = x + 3 ; print(x)`, appliquer la méthode « dresser une table instruction, expression calculée, nouvelle valeur », puis écrire `7` affiché ; résultat : le comportement de trace d’affectation est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de identifier le type chaîne puis appliquer `+` comme concaténation avant de conclure par `"NSI"` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Confondre affichage et valeur retournée par une fonction. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « reste nul » et valider `True` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Donner une sortie sans trace intermédiaire. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Écrire une justification en deux phrases : état avant, état après. ».

## Erreurs fréquentes
- Erreur fréquente EF1 - Lire le signe égal comme une égalité mathématique permanente.
- Erreur fréquente EF2 - Confondre affichage et valeur retournée par une fonction.
- Erreur fréquente EF3 - Oublier de tester la valeur zéro dans une fonction numérique.
- Erreur fréquente EF4 - Donner une sortie sans trace intermédiaire.

## Remédiation ciblée
- Activité corrective EF1 : Construire un tableau mémoire avec une ligne par instruction.
- Activité corrective EF2 : Colorer `print`, `return` et expression évaluée dans trois colonnes.
- Activité corrective EF3 : Ajouter les tests `0`, `1` et `-1` avant les cas ordinaires.
- Activité corrective EF4 : Écrire une justification en deux phrases : état avant, état après.

## Différenciation
- Socle : traiter `x = 4 ; x = x + 3 ; print(x)` avec une fiche méthode fournie.
- Standard : traiter `mot = "NS" ; mot = mot + "I"` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « reste nul » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Validation opérationnelle du TP
- Vérification P00-1 : exécuter le starter et constater au moins un échec de test nominal.
- Vérification P00-2 : exécuter le corrigé professeur et obtenir les trois catégories de tests au vert.
- Vérification P00-3 : modifier une entrée limite et expliquer pourquoi le résultat reste contrôlable.
- Vérification P00-4 : refuser explicitement une entrée invalide au lieu de produire une valeur arbitraire.
- Vérification P00-5 : joindre au livrable la commande exécutée et la sortie courte des tests.
- Vérification P00-6 : comparer l’algorithme écrit avec la capacité officielle citée.
