---
title: "T03 - Td - Piles, files et dictionnaires"
level: "terminale"
sequence_id: "T03"
document_type: "td"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures linéaires et tables associatives"
notion: "pile, file, dictionnaire, complexité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-03A"
    - "T-STRUCT-03B"
---

# T03 - TD - Piles, files et dictionnaires

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- T-STRUCT-03A
- T-STRUCT-03B

## Prérequis
- Reconnaître une consigne liée à pile.
- Distinguer donnée, méthode et conclusion dans le thème Structures linéaires et tables associatives.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- T03-S1 à T03-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un serveur journalise des tâches en attente et doit choisir entre pile, file et dictionnaire selon l’usage.

## Activité d’entrée
1. Simuler une pile sur trois opérations.
2. Simuler une file sur trois clients.
3. Utiliser un dictionnaire pour retrouver une tâche par identifiant.
4. Comparer coût de recherche et d’accès direct.

## Exemples corrigés précis
### Exemple corrigé 1 - pile
- Donnée étudiée : empiler A puis B, dépiler.
- Méthode : appliquer LIFO.
- Résultat obtenu : B sort en premier.
- Contrôle : le cas limite « pile vide » est vérifié séparément.
### Exemple corrigé 2 - file
- Donnée étudiée : enfiler A puis B, défiler.
- Méthode : appliquer FIFO.
- Résultat obtenu : A sort en premier.
- Contrôle : le cas limite « file vide » est vérifié séparément.
### Exemple corrigé 3 - dictionnaire
- Donnée étudiée : `{"id7": "ok"}`.
- Méthode : tester la clé puis accéder.
- Résultat obtenu : `ok`.
- Contrôle : le cas limite « clé absente » est vérifié séparément.
### Exemple corrigé 4 - complexité
- Donnée étudiée : accès par identifiant.
- Méthode : choisir dictionnaire plutôt que parcours linéaire.
- Résultat obtenu : accès attendu constant.
- Contrôle : le cas limite « collision abstraite hors programme » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : T-STRUCT-03A.
- Énoncé disciplinaire : résoudre pile avec empiler A puis B, dépiler.
- Production attendue : B sort en premier.
- Contrainte de contrôle : faire apparaître le contrôle « pile vide ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : T-STRUCT-03A.
- Énoncé disciplinaire : expliquer file à partir de enfiler A puis B, défiler.
- Production attendue : A sort en premier.
- Contrainte de contrôle : rédiger la méthode avant le résultat.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : T-STRUCT-03A.
- Énoncé disciplinaire : comparer dictionnaire avec `{"id7": "ok"}`.
- Production attendue : `ok`.
- Contrainte de contrôle : comparer avec le cas « clé absente ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : T-STRUCT-03A, T-STRUCT-03B.
- Énoncé disciplinaire : corriger complexité pour accès par identifiant.
- Production attendue : accès attendu constant.
- Contrainte de contrôle : corriger l’erreur « Confondre clé et valeur. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : T-STRUCT-03A.
- Énoncé disciplinaire : tester un cas limite lié à pile vide.
- Production attendue : le comportement de pile est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : T-STRUCT-03A.
- Énoncé disciplinaire : classer deux méthodes possibles pour file.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Retirer dans une structure vide sans test. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : T-STRUCT-03A.
- Énoncé disciplinaire : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : T-STRUCT-03A.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur complexité.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Surligner clés et valeurs de couleurs différentes. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : B sort en premier.
- Contrôle : faire apparaître le contrôle « pile vide ».
- Erreur traitée : EF1 - Inverser LIFO et FIFO.
- Donnée utilisée alpha dans T03 td piles files dictionnaires : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : A sort en premier.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Retirer dans une structure vide sans test.
- Donnée utilisée beta dans T03 td piles files dictionnaires : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : `ok`.
- Contrôle : comparer avec le cas « clé absente ».
- Erreur traitée : EF3 - Parcourir tout un dictionnaire pour une clé connue.
- Donnée utilisée gamma dans T03 td piles files dictionnaires : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : accès attendu constant.
- Contrôle : corriger l’erreur « Confondre clé et valeur. ».
- Erreur traitée : EF4 - Confondre clé et valeur.
- Donnée utilisée delta dans T03 td piles files dictionnaires : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de pile est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Inverser LIFO et FIFO.
- Donnée utilisée epsilon dans T03 td piles files dictionnaires : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Retirer dans une structure vide sans test. » est une erreur.
- Erreur traitée : EF2 - Retirer dans une structure vide sans test.
- Donnée utilisée zeta dans T03 td piles files dictionnaires : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Parcourir tout un dictionnaire pour une clé connue.
- Donnée utilisée eta dans T03 td piles files dictionnaires : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Surligner clés et valeurs de couleurs différentes. ».
- Erreur traitée : EF4 - Confondre clé et valeur.
- Donnée utilisée theta dans T03 td piles files dictionnaires : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans T03 td piles files dictionnaires : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans T03 td piles files dictionnaires : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans T03 td piles files dictionnaires : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- Erreur fréquente EF1 - Inverser LIFO et FIFO.
- Erreur fréquente EF2 - Retirer dans une structure vide sans test.
- Erreur fréquente EF3 - Parcourir tout un dictionnaire pour une clé connue.
- Erreur fréquente EF4 - Confondre clé et valeur.

## Remédiation ciblée
- Activité corrective EF1 : Jouer les opérations avec des cartes empilées puis alignées.
- Activité corrective EF2 : Écrire le test `est_vide` avant chaque retrait.
- Activité corrective EF3 : Remplacer une boucle de recherche par un accès par clé.
- Activité corrective EF4 : Surligner clés et valeurs de couleurs différentes.

## Différenciation
- Socle : traiter empiler A puis B, dépiler avec une fiche méthode fournie.
- Standard : traiter enfiler A puis B, défiler en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « clé absente » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.
