---
title: "P04 - Td - Types construits"
level: "premiere"
sequence_id: "P04"
document_type: "td"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Tuples, listes, dictionnaires"
notion: "tuple, liste, dictionnaire, mutabilité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-CONSTR-02A"
    - "P-DATA-CONSTR-02D"
---

# P04 - TD - Types construits

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-CONSTR-02A
- P-DATA-CONSTR-02D

## Prérequis
- Reconnaître une consigne liée à tuple.
- Distinguer donnée, méthode et conclusion dans le thème Tuples, listes, dictionnaires.
- Rédiger une justification courte en utilisant le vocabulaire du programme.
- Contrôler une réponse par un cas limite ou un contre-exemple explicite.

## Séance(s) correspondante(s)
- P04-S1 à P04-S7 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Une station météo stocke des coordonnées fixes, des relevés horaires modifiables et des mesures accessibles par nom.

## Activité d’entrée
1. Identifier ce qui doit rester immuable dans un tuple.
2. Modifier une liste de températures.
3. Lire une clé dans un dictionnaire de station.
4. Décrire ce qui se passe avec une liste vide.

## Exemples corrigés précis
### Exemple corrigé 1 - tuple de coordonnées
- Donnée étudiée : `(36.8, 10.2)`.
- Méthode : lire sans modifier et nommer latitude puis longitude.
- Résultat obtenu : coordonnées conservées.
- Contrôle : le cas limite « tentative de modification interdite » est vérifié séparément.
### Exemple corrigé 2 - liste de relevés
- Donnée étudiée : `[18, 20, 19]`.
- Méthode : parcourir les valeurs et calculer une moyenne.
- Résultat obtenu : `19`.
- Contrôle : le cas limite « liste vide » est vérifié séparément.
### Exemple corrigé 3 - dictionnaire
- Donnée étudiée : `{"temperature": 21, "vent": 12}`.
- Méthode : tester la présence de la clé avant lecture.
- Résultat obtenu : `21` pour `temperature`.
- Contrôle : le cas limite « clé absente » est vérifié séparément.
### Exemple corrigé 4 - copie de liste
- Donnée étudiée : `[[1], [2]]`.
- Méthode : distinguer copie superficielle et copie indépendante.
- Résultat obtenu : modification locale contrôlée.
- Contrôle : le cas limite « liste imbriquée » est vérifié séparément.
## Exercices numérotés
### Exercice 1
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé disciplinaire : résoudre tuple de coordonnées avec `(36.8, 10.2)`.
- Production attendue : coordonnées conservées.
- Contrainte de contrôle : faire apparaître le contrôle « tentative de modification interdite ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 2
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-CONSTR-02A, P-DATA-CONSTR-02D.
- Énoncé disciplinaire : on dispose de la liste `releves = [18, 20, 19]`. Écrire une boucle `for` qui parcourt les éléments de `releves` et calcule leur moyenne. Donner la trace d'exécution : à chaque tour de boucle, indiquer la valeur de l'élément courant et le cumul partiel.
- Production attendue : `19` (moyenne = (18 + 20 + 19) / 3).
- Contrainte de contrôle : utiliser `for valeur in releves` (itération sur les valeurs, pas sur les indices) ; traiter le cas `releves = []`.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 3
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé disciplinaire : comparer dictionnaire avec `{"temperature": 21, "vent": 12}`.
- Production attendue : `21` pour `temperature`.
- Contrainte de contrôle : comparer avec le cas « clé absente ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 4
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé disciplinaire : corriger copie de liste pour `[[1], [2]]`.
- Production attendue : modification locale contrôlée.
- Contrainte de contrôle : corriger l’erreur « Copier une liste imbriquée seulement au premier niveau. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 5
- Objectif travaillé : O1.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé disciplinaire : tester un cas limite lié à tentative de modification interdite.
- Production attendue : le comportement de tuple de coordonnées est contrôlé.
- Contrainte de contrôle : nommer la donnée minimale et la conclusion.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 6
- Objectif travaillé : O2.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé disciplinaire : classer deux méthodes possibles pour liste de relevés.
- Production attendue : la méthode robuste est choisie et justifiée.
- Contrainte de contrôle : identifier pourquoi « Parcourir les indices quand les valeurs suffisent. » est une erreur.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 7
- Objectif travaillé : O3.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé disciplinaire : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle.
- Production attendue : la justification reste valable sur le nouveau cas.
- Contrainte de contrôle : inclure une étape calculable par un pair.
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
### Exercice 8
- Objectif travaillé : O4.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé disciplinaire : étendre un énoncé volontairement erroné sur copie de liste.
- Production attendue : l’erreur est localisée puis réparée.
- Contrainte de contrôle : proposer une activité corrective inspirée de « Modifier une sous-liste et observer l’effet sur la copie. ».
- Critère local : la réponse contient une donnée, une méthode, un résultat et une vérification.
## Corrigé
### Corrigé exercice 1
- Résultat : coordonnées conservées.
- Contrôle : faire apparaître le contrôle « tentative de modification interdite ».
- Erreur traitée : EF1 - Modifier un tuple comme une liste.
- Donnée utilisée alpha dans P04 td types construits : cas alpha de l exercice 1 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P04 td types construits : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P04 td types construits : sortie vérifiable de l exercice 1, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 2
- Résultat : `19`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Parcourir les indices quand les valeurs suffisent.
- Donnée utilisée beta dans P04 td types construits : cas beta de l exercice 2 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P04 td types construits : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P04 td types construits : sortie vérifiable de l exercice 2, reliée à la capacité officielle du bloc.
- Contrôle beta dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 3
- Résultat : `21` pour `temperature`.
- Contrôle : comparer avec le cas « clé absente ».
- Erreur traitée : EF3 - Accéder à une clé sans vérifier sa présence.
- Donnée utilisée gamma dans P04 td types construits : cas gamma de l exercice 3 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P04 td types construits : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P04 td types construits : sortie vérifiable de l exercice 3, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 4
- Résultat : modification locale contrôlée.
- Contrôle : corriger l’erreur « Copier une liste imbriquée seulement au premier niveau. ».
- Erreur traitée : EF4 - Copier une liste imbriquée seulement au premier niveau.
- Donnée utilisée delta dans P04 td types construits : cas delta de l exercice 4 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P04 td types construits : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P04 td types construits : sortie vérifiable de l exercice 4, reliée à la capacité officielle du bloc.
- Contrôle delta dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 5
- Résultat : le comportement de tuple de coordonnées est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Modifier un tuple comme une liste.
- Donnée utilisée epsilon dans P04 td types construits : cas epsilon de l exercice 5 avec les valeurs indiquées dans l énoncé.
- Méthode epsilon dans P04 td types construits : trace courte, pseudo-code local `if cas_epsilon: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat epsilon dans P04 td types construits : sortie vérifiable de l exercice 5, reliée à la capacité officielle du bloc.
- Contrôle epsilon dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 6
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Parcourir les indices quand les valeurs suffisent. » est une erreur.
- Erreur traitée : EF2 - Parcourir les indices quand les valeurs suffisent.
- Donnée utilisée zeta dans P04 td types construits : cas zeta de l exercice 6 avec les valeurs indiquées dans l énoncé.
- Méthode zeta dans P04 td types construits : trace courte, pseudo-code local `if cas_zeta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat zeta dans P04 td types construits : sortie vérifiable de l exercice 6, reliée à la capacité officielle du bloc.
- Contrôle zeta dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 7
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Accéder à une clé sans vérifier sa présence.
- Donnée utilisée eta dans P04 td types construits : cas eta de l exercice 7 avec les valeurs indiquées dans l énoncé.
- Méthode eta dans P04 td types construits : trace courte, pseudo-code local `if cas_eta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat eta dans P04 td types construits : sortie vérifiable de l exercice 7, reliée à la capacité officielle du bloc.
- Contrôle eta dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 8
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Modifier une sous-liste et observer l’effet sur la copie. ».
- Erreur traitée : EF4 - Copier une liste imbriquée seulement au premier niveau.
- Donnée utilisée theta dans P04 td types construits : cas theta de l exercice 8 avec les valeurs indiquées dans l énoncé.
- Méthode theta dans P04 td types construits : trace courte, pseudo-code local `if cas_theta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat theta dans P04 td types construits : sortie vérifiable de l exercice 8, reliée à la capacité officielle du bloc.
- Contrôle theta dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.

## Erreurs fréquentes
- Erreur fréquente EF1 - Modifier un tuple comme une liste.
- Erreur fréquente EF2 - Parcourir les indices quand les valeurs suffisent.
- Erreur fréquente EF3 - Accéder à une clé sans vérifier sa présence.
- Erreur fréquente EF4 - Copier une liste imbriquée seulement au premier niveau.

## Remédiation ciblée
- Activité corrective EF1 : Identifier mutabilité et usage avant d’écrire une affectation.
- Activité corrective EF2 : Écrire deux boucles, avec indices puis avec valeurs, et comparer.
- Activité corrective EF3 : Tester `cle in dictionnaire` avant la lecture.
- Activité corrective EF4 : Modifier une sous-liste et observer l’effet sur la copie.

## Différenciation
- Socle : traiter `(36.8, 10.2)` avec une fiche méthode fournie.
- Standard : traiter `[18, 20, 19]` en rédigeant la justification complète.
- Expert : inventer un cas limite lié à « clé absente » et expliquer le comportement attendu.

## Critères de réussite
- La capacité officielle est citée dans la copie.
- La méthode contient au moins une étape vérifiable par un pair.
- Le cas limite est discuté avec une donnée concrète.
- La correction explique quelle erreur fréquente est évitée.

## Complément d’exercices corrigés - types construits
### Exercice 9 - Milieu de deux coordonnées
- Données : `A = (0, 4)`, `B = (6, 10)`. ; jeu_exercice=alpha
- Consigne : écrire la formule du milieu et préciser pourquoi un tuple convient.

### Exercice 10 - Liste mutable
- Données : `notes = [8, 12, 10]`. ; jeu_exercice=beta
- Consigne : remplacer la deuxième note par `14`, puis donner la liste.

### Exercice 11 - Liste de dictionnaires
- Données : `stations = [{"nom": "A", "temperature": 21}, {"nom": "B", "temperature": 18}, {"nom": "C", "temperature": 23}]`. ; jeu_exercice=gamma
- Consigne : extraire les noms des stations dont la température est au moins `20`.

### Exercice 12 - Cas limites
- Données : `point = (2,)`, `station = {"temperature": 21}`, `notes = []`. ; jeu_exercice=delta
- Consigne : associer chaque donnée à l’erreur possible.

### Corrigé exercice 9
- Résultat attendu : le milieu vaut `((0+6)/2, (4+10)/2) = (3.0, 7.0)`.
- Contrôle : le résultat est un tuple de taille 2, adapté à une coordonnée fixe.
- Donnée utilisée alpha dans P04 td types construits : cas alpha de l exercice 9 avec les valeurs indiquées dans l énoncé.
- Méthode alpha dans P04 td types construits : trace courte, pseudo-code local `if cas_alpha: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat alpha dans P04 td types construits : sortie vérifiable de l exercice 9, reliée à la capacité officielle du bloc.
- Contrôle alpha dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 10
- Résultat attendu : après `notes[1] = 14`, la liste vaut `[8, 14, 10]`.
- Contrôle : la longueur reste `3`, seule la valeur de rang 2 change.
- Donnée utilisée beta dans P04 td types construits : cas beta de l exercice 10 avec les valeurs indiquées dans l énoncé.
- Méthode beta dans P04 td types construits : trace courte, pseudo-code local `if cas_beta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat beta dans P04 td types construits : sortie vérifiable de l exercice 10, reliée à la capacité officielle du bloc.
- Contrôle beta dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 11
- Résultat attendu : les noms extraits sont `["A", "C"]`.
- Contrôle : la station `"B"` est exclue car `18 < 20`.
- Donnée utilisée gamma dans P04 td types construits : cas gamma de l exercice 11 avec les valeurs indiquées dans l énoncé.
- Méthode gamma dans P04 td types construits : trace courte, pseudo-code local `if cas_gamma: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat gamma dans P04 td types construits : sortie vérifiable de l exercice 11, reliée à la capacité officielle du bloc.
- Contrôle gamma dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
### Corrigé exercice 12
- Résultat attendu : `point` a une mauvaise taille pour une coordonnée 2D ; `station["pression"]` provoquerait une clé absente ; `notes` ne permet pas de moyenne sans convention.
- Contrôle : chaque erreur est liée à un type différent : tuple, dictionnaire, liste.
- Donnée utilisée delta dans P04 td types construits : cas delta de l exercice 12 avec les valeurs indiquées dans l énoncé.
- Méthode delta dans P04 td types construits : trace courte, pseudo-code local `if cas_delta: décider else: calculer`, invariant nommé et complexité `O(n)`.
- Résultat delta dans P04 td types construits : sortie vérifiable de l exercice 12, reliée à la capacité officielle du bloc.
- Contrôle delta dans P04 td types construits : le cas limite annoncé est décidé explicitement et une réponse sans trace est refusée.
