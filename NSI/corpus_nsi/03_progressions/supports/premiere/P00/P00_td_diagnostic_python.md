---
title: "P00 - Td - Diagnostic Python"
level: "premiere"
sequence_id: "P00"
document_type: "td"
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

# P00 - TD - Diagnostic Python

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
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : résoudre trace d’affectation avec `x = 4 ; x = x + 3 ; print(x)`.
- Production attendue : `7` affiché.
- Contrainte de contrôle : faire apparaître le contrôle « variable réaffectée deux fois ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : expliquer concaténation de chaînes à partir de `mot = "NS" ; mot = mot + "I"`.
- Production attendue : `"NSI"`.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : comparer test conditionnel avec `n = 6 ; n % 2 == 0`.
- Production attendue : `True`.
- Contrainte de contrôle : comparer avec le cas « reste nul ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : corriger fonction courte pour `def f(a): return 2*a + 1` avec `a = 5`.
- Production attendue : `11` retourné.
- Contrainte de contrôle : corriger l’erreur « Donner une sortie sans trace intermédiaire. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : tester un cas limite lié à variable réaffectée deux fois.
- Production attendue : le comportement de trace d’affectation est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : classer deux méthodes possibles pour concaténation de chaînes.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Confondre affichage et valeur retournée par une fonction. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : justifier un transfert qui utilise test conditionnel avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : P-LANG-01.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur fonction courte.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Écrire une justification en deux phrases : état avant, état après. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : `7` affiché.
- Contrôle : faire apparaître le contrôle « variable réaffectée deux fois ».
- Erreur traitée : EF1 - Lire le signe égal comme une égalité mathématique permanente.
- Donnée utilisée alpha dans P00 td diagnostic python : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P00 td diagnostic python : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : `"NSI"`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Confondre affichage et valeur retournée par une fonction.
- Donnée utilisée beta dans P00 td diagnostic python : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P00 td diagnostic python : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : `True`.
- Contrôle : comparer avec le cas « reste nul ».
- Erreur traitée : EF3 - Oublier de tester la valeur zéro dans une fonction numérique.
- Donnée utilisée gamma dans P00 td diagnostic python : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P00 td diagnostic python : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : `11` retourné.
- Contrôle : corriger l’erreur « Donner une sortie sans trace intermédiaire. ».
- Erreur traitée : EF4 - Donner une sortie sans trace intermédiaire.
- Donnée utilisée delta dans P00 td diagnostic python : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P00 td diagnostic python : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de trace d’affectation est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Lire le signe égal comme une égalité mathématique permanente.
- Donnée utilisée epsilon dans P00 td diagnostic python : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P00 td diagnostic python : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Confondre affichage et valeur retournée par une fonction. » est une erreur.
- Erreur traitée : EF2 - Confondre affichage et valeur retournée par une fonction.
- Donnée utilisée zeta dans P00 td diagnostic python : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P00 td diagnostic python : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Oublier de tester la valeur zéro dans une fonction numérique.
- Donnée utilisée eta dans P00 td diagnostic python : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P00 td diagnostic python : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Écrire une justification en deux phrases : état avant, état après. ».
- Erreur traitée : EF4 - Donner une sortie sans trace intermédiaire.
- Donnée utilisée theta dans P00 td diagnostic python : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P00 td diagnostic python : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P00 td diagnostic python : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P00 td diagnostic python : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

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
