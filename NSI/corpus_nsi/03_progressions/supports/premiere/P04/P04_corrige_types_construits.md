---
title: "P04 - Corrige - Types construits"
level: "premiere"
sequence_id: "P04"
document_type: "corrige"
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


# P04 - Corrigé professeur - Types construits

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

## Méthode générale de correction
- Point 1 : pour tuple de coordonnées, exiger la donnée `(36.8, 10.2)`, la méthode « lire sans modifier et nommer latitude puis longitude » et le contrôle « tentative de modification interdite ».
- Point 2 : pour liste de relevés, exiger la donnée `[18, 20, 19]`, la méthode « parcourir les valeurs et calculer une moyenne » et le contrôle « liste vide ».
- Point 3 : pour dictionnaire, exiger la donnée `{"temperature": 21, "vent": 12}`, la méthode « tester la présence de la clé avant lecture » et le contrôle « clé absente ».
- Point 4 : pour copie de liste, exiger la donnée `[[1], [2]]`, la méthode « distinguer copie superficielle et copie indépendante » et le contrôle « liste imbriquée ».
## Exercices numérotés
- Exercice 1 : résoudre tuple de coordonnées avec `(36.8, 10.2)` ; attendu : coordonnées conservées.
- Exercice 2 : expliquer liste de relevés à partir de `[18, 20, 19]` ; attendu : `19`.
- Exercice 3 : comparer dictionnaire avec `{"temperature": 21, "vent": 12}` ; attendu : `21` pour `temperature`.
- Exercice 4 : corriger copie de liste pour `[[1], [2]]` ; attendu : modification locale contrôlée.
- Exercice 5 : tester un cas limite lié à tentative de modification interdite ; attendu : le comportement de tuple de coordonnées est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour liste de relevés ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur copie de liste ; attendu : l’erreur est localisée puis réparée.

## Corrigé
### Corrigé exercice 1
- Méthode : identifier `(36.8, 10.2)`, appliquer la méthode « lire sans modifier et nommer latitude puis longitude », puis écrire coordonnées conservées.
- Résultat : coordonnées conservées.
- Contrôle : faire apparaître le contrôle « tentative de modification interdite ».
- Erreur traitée : EF1 - Modifier un tuple comme une liste.
### Corrigé exercice 2
- Méthode : expliciter chaque étape de parcourir les valeurs et calculer une moyenne avant de conclure par `19`.
- Résultat : `19`.
- Contrôle : rédiger la méthode avant le résultat.
- Erreur traitée : EF2 - Parcourir les indices quand les valeurs suffisent.
### Corrigé exercice 3
- Méthode : comparer la donnée avec le cas limite « clé absente » et valider `21` pour `temperature`.
- Résultat : `21` pour `temperature`.
- Contrôle : comparer avec le cas « clé absente ».
- Erreur traitée : EF3 - Accéder à une clé sans vérifier sa présence.
### Corrigé exercice 4
- Méthode : isoler l’erreur fréquente « Copier une liste imbriquée seulement au premier niveau. » puis reprendre la procédure correcte.
- Résultat : modification locale contrôlée.
- Contrôle : corriger l’erreur « Copier une liste imbriquée seulement au premier niveau. ».
- Erreur traitée : EF4 - Copier une liste imbriquée seulement au premier niveau.
### Corrigé exercice 5
- Méthode : identifier `(36.8, 10.2)`, appliquer la méthode « lire sans modifier et nommer latitude puis longitude », puis écrire coordonnées conservées.
- Résultat : le comportement de tuple de coordonnées est contrôlé.
- Contrôle : nommer la donnée minimale et la conclusion.
- Erreur traitée : EF1 - Modifier un tuple comme une liste.
### Corrigé exercice 6
- Méthode : expliciter chaque étape de parcourir les valeurs et calculer une moyenne avant de conclure par `19`.
- Résultat : la méthode robuste est choisie et justifiée.
- Contrôle : identifier pourquoi « Parcourir les indices quand les valeurs suffisent. » est une erreur.
- Erreur traitée : EF2 - Parcourir les indices quand les valeurs suffisent.
### Corrigé exercice 7
- Méthode : comparer la donnée avec le cas limite « clé absente » et valider `21` pour `temperature`.
- Résultat : la justification reste valable sur le nouveau cas.
- Contrôle : inclure une étape calculable par un pair.
- Erreur traitée : EF3 - Accéder à une clé sans vérifier sa présence.
### Corrigé exercice 8
- Méthode : isoler l’erreur fréquente « Copier une liste imbriquée seulement au premier niveau. » puis reprendre la procédure correcte.
- Résultat : l’erreur est localisée puis réparée.
- Contrôle : proposer une activité corrective inspirée de « Modifier une sous-liste et observer l’effet sur la copie. ».
- Erreur traitée : EF4 - Copier une liste imbriquée seulement au premier niveau.

## Barème de correction rapide
- Exercice 1 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « faire apparaître le contrôle « tentative de modification interdite » ».
- Exercice 2 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « rédiger la méthode avant le résultat ».
- Exercice 3 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « comparer avec le cas « clé absente » ».
- Exercice 4 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « corriger l’erreur « Copier une liste imbriquée seulement au premier niveau. » ».
- Exercice 5 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « nommer la donnée minimale et la conclusion ».
- Exercice 6 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « identifier pourquoi « Parcourir les indices quand les valeurs suffisent. » est une erreur ».
- Exercice 7 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « inclure une étape calculable par un pair ».
- Exercice 8 : 1 point méthode, 0,5 point résultat, 0,5 point contrôle sur « proposer une activité corrective inspirée de « Modifier une sous-liste et observer l’effet sur la copie. » ».
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

## Corrigés complémentaires - types construits
### Corrigé exercice 9
- Valeur attendue : `A=(0,4)`, `B=(6,10)`, milieu `(3.0, 7.0)`.
- Justification : la formule moyenne les abscisses et les ordonnées séparément.
- Contrôle : le résultat est encore un tuple de taille 2.

### Corrigé exercice 10
- Valeur attendue : `[8, 14, 10]`.
- Justification : une liste est mutable ; l’affectation `notes[1] = 14` modifie la liste en place.
- Contrôle : l’indice `1` désigne la deuxième valeur, pas la première.

### Corrigé exercice 11
- Valeur attendue : `["A", "C"]`.
- Justification : les dictionnaires des stations A et C ont `temperature >= 20`.
- Contrôle : le filtre lit la clé `temperature` et ne compare pas le dictionnaire complet.

### Corrigé exercice 12
- Valeurs attendues : mauvaise taille pour `(2,)`, clé absente pour `"pression"`, liste vide pour `[]`.
- Justification : chaque structure impose une vérification différente avant traitement.
- Contrôle : le corrigé cite l’erreur et la garde à ajouter.
