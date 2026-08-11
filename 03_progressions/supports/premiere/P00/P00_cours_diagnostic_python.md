---
title: "P00 - Cours - Diagnostic Python"
level: "premiere"
sequence_id: "P00"
document_type: "cours"
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

# P00 - Cours - Diagnostic Python

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

## Définitions et formalisation
- Définition D1 : affectation est utilisé dans Rentrée et méthode avec une donnée, une règle et un contrôle.
- Définition D2 : type est utilisé dans Rentrée et méthode avec une donnée, une règle et un contrôle.
- Définition D3 : condition est utilisé dans Rentrée et méthode avec une donnée, une règle et un contrôle.
- Définition D4 : trace d’exécution est utilisé dans Rentrée et méthode avec une donnée, une règle et un contrôle.
- Cas limite principal : variable réaffectée deux fois.

## Exemples corrigés précis
### Exemple corrigé 1 - trace d’affectation
- Donnée étudiée : `x = 4 ; x = x + 3 ; print(x)`.
- Méthode : dresser une table instruction, expression calculée, nouvelle valeur.
- Résultat obtenu : `7` affiché.
- Contrôle : le cas limite « variable réaffectée deux fois » est vérifié séparément.
### Exemple corrigé 2 - concaténation de chaînes
- Donnée étudiée : `mot = "NS" ; mot = mot + "I"`.
- Méthode : identifier le type chaîne puis appliquer `+` comme concaténation.
- Résultat obtenu : `"NSI"`.
- Contrôle : le cas limite « addition impossible entre chaîne et entier » est vérifié séparément.
### Exemple corrigé 3 - test conditionnel
- Donnée étudiée : `n = 6 ; n % 2 == 0`.
- Méthode : calculer le reste puis évaluer le booléen.
- Résultat obtenu : `True`.
- Contrôle : le cas limite « reste nul » est vérifié séparément.
### Exemple corrigé 4 - fonction courte
- Donnée étudiée : `def f(a): return 2*a + 1` avec `a = 5`.
- Méthode : substituer l’argument et distinguer retour et affichage.
- Résultat obtenu : `11` retourné.
- Contrôle : le cas limite « aucun affichage sans `print` » est vérifié séparément.
## Objectif O1 - Identifier précisément la représentation ou la structure en jeu
- Capacité mobilisée : P-LANG-01.
- Point de départ : `x = 4 ; x = x + 3 ; print(x)`.
- Angle disciplinaire : repérage initial autour de trace d’affectation.
- Démarche attendue : dresser une table instruction, expression calculée, nouvelle valeur.
- Exemple associé : `7` affiché.
- Point de vigilance : Lire le signe égal comme une égalité mathématique permanente.
- Activité de reprise associée : Construire un tableau mémoire avec une ligne par instruction.
- Mini-production : produire un court diagnostic de la donnée et du vocabulaire.
## Objectif O2 - Appliquer une méthode disciplinaire complète
- Capacité mobilisée : P-LANG-01.
- Point de départ : `mot = "NS" ; mot = mot + "I"`.
- Angle disciplinaire : méthode guidée autour de concaténation de chaînes.
- Démarche attendue : identifier le type chaîne puis appliquer `+` comme concaténation.
- Exemple associé : `"NSI"`.
- Point de vigilance : Confondre affichage et valeur retournée par une fonction.
- Activité de reprise associée : Colorer `print`, `return` et expression évaluée dans trois colonnes.
- Mini-production : produire une procédure numérotée avec contrôle intermédiaire.
## Objectif O3 - Justifier le résultat sur un cas différent
- Capacité mobilisée : P-LANG-01.
- Point de départ : `n = 6 ; n % 2 == 0`.
- Angle disciplinaire : transfert argumenté autour de test conditionnel.
- Démarche attendue : calculer le reste puis évaluer le booléen.
- Exemple associé : `True`.
- Point de vigilance : Oublier de tester la valeur zéro dans une fonction numérique.
- Activité de reprise associée : Ajouter les tests `0`, `1` et `-1` avant les cas ordinaires.
- Mini-production : produire une justification qui compare deux cas distincts.
## Objectif O4 - Contrôler un cas limite et corriger une erreur observée
- Capacité mobilisée : P-LANG-01.
- Point de départ : `def f(a): return 2*a + 1` avec `a = 5`.
- Angle disciplinaire : vérification critique autour de fonction courte.
- Démarche attendue : substituer l’argument et distinguer retour et affichage.
- Exemple associé : `11` retourné.
- Point de vigilance : Donner une sortie sans trace intermédiaire.
- Activité de reprise associée : Écrire une justification en deux phrases : état avant, état après.
- Mini-production : produire une correction d’erreur avec un nouveau test.
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
## Banque de situations complémentaires
- Situation complémentaire 1 : reprendre trace d’affectation avec une donnée construite par un binôme.
- Question orale 1 : expliquer pourquoi le cas limite « variable réaffectée deux fois » change ou ne change pas la méthode.
- Trace attendue 1 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 2 : reprendre concaténation de chaînes avec une donnée construite par un binôme.
- Question orale 2 : expliquer pourquoi le cas limite « addition impossible entre chaîne et entier » change ou ne change pas la méthode.
- Trace attendue 2 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 3 : reprendre test conditionnel avec une donnée construite par un binôme.
- Question orale 3 : expliquer pourquoi le cas limite « reste nul » change ou ne change pas la méthode.
- Trace attendue 3 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
- Situation complémentaire 4 : reprendre fonction courte avec une donnée construite par un binôme.
- Question orale 4 : expliquer pourquoi le cas limite « aucun affichage sans `print` » change ou ne change pas la méthode.
- Trace attendue 4 : une phrase de méthode, une ligne de calcul et une vérification indépendante.
## Atelier de synthèse
- Synthèse 1 : relier trace d’affectation à une erreur fréquente et à une remédiation ciblée.
- Synthèse 2 : relier concaténation de chaînes à une erreur fréquente et à une remédiation ciblée.
- Synthèse 3 : relier test conditionnel à une erreur fréquente et à une remédiation ciblée.
- Synthèse 4 : relier fonction courte à une erreur fréquente et à une remédiation ciblée.
## Lexique actif
- affectation : terme à employer dans une justification écrite de la séquence.
- type : terme à employer dans une justification écrite de la séquence.
- condition : terme à employer dans une justification écrite de la séquence.
- trace d’exécution : terme à employer dans une justification écrite de la séquence.

## Analyse de variantes disciplinaires
- Variante P00-A : modifier la donnée du premier exemple de P00 - Cours - Diagnostic Python et conserver exactement la même méthode.
- Variante P00-B : changer le cas limite et expliquer quelle étape de contrôle devient obligatoire.
- Variante P00-C : demander à un pair de retrouver l’erreur fréquente avant de lire la correction.
- Variante P00-D : produire une trace écrite qui sépare définition, calcul et justification.
- Variante P00-E : comparer deux solutions d’élèves et isoler celle qui cite la capacité officielle.
- Variante P00-F : construire une donnée minimale qui force une décision de méthode.
- Variante P00-G : transformer un exemple corrigé en question d’évaluation courte.
- Variante P00-H : écrire un contre-exemple qui invalide une réponse seulement déclarative.
- Variante P00-I : relier une erreur fréquente à une activité corrective précise.
- Variante P00-J : rédiger un critère de réussite observable pour une copie réelle.
- Variante P00-K : vérifier que le vocabulaire utilisé correspond au thème de la séquence.
- Variante P00-L : préparer une question orale de trente secondes avec réponse vérifiable.
- Variante P00-M : isoler la donnée, l’algorithme mental et le résultat final dans trois lignes.
- Variante P00-N : expliquer ce que le TP apporte que le TD ne permet pas de tester.
- Variante P00-O : compléter la trace écrite par une mise en garde liée au cas limite.
- Variante P00-P : vérifier la cohérence entre exercice, corrigé, barème et remédiation.
