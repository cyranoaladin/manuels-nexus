---
title: "P04 - Version amenagee - Types construits"
level: "premiere"
sequence_id: "P04"
document_type: "version_amenagee"
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
---


# P04 - Version aménagée - Types construits

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-CONSTR-02A

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

## Version aménagée - Énoncé élève
### Question aménagée 1
- Énoncé élève : traiter tuple de coordonnées avec la donnée `(36.8, 10.2)`.
- Aide intégrée : commencer par lire sans modifier et nommer latitude puis longitude.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Modifier un tuple comme une liste.
### Question aménagée 2
- Énoncé élève : traiter liste de relevés avec la donnée `[18, 20, 19]`.
- Aide intégrée : commencer par parcourir les valeurs et calculer une moyenne.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Parcourir les indices quand les valeurs suffisent.
### Question aménagée 3
- Énoncé élève : traiter dictionnaire avec la donnée `{"temperature": 21, "vent": 12}`.
- Aide intégrée : commencer par tester la présence de la clé avant lecture.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Accéder à une clé sans vérifier sa présence.
### Question aménagée 4
- Énoncé élève : traiter copie de liste avec la donnée `[[1], [2]]`.
- Aide intégrée : commencer par distinguer copie superficielle et copie indépendante.
- Espace de réponse : méthode : ______ ; résultat : ______ ; contrôle : ______.
- Point de vigilance : Copier une liste imbriquée seulement au premier niveau.
## Exercices numérotés
- Exercice 1 : résoudre tuple de coordonnées avec `(36.8, 10.2)` avec aide possible sur la méthode.
- Exercice 2 : expliquer liste de relevés à partir de `[18, 20, 19]` avec aide possible sur la méthode.
- Exercice 3 : comparer dictionnaire avec `{"temperature": 21, "vent": 12}` avec aide possible sur la méthode.
- Exercice 4 : corriger copie de liste pour `[[1], [2]]` avec aide possible sur la méthode.
- Exercice 5 : tester un cas limite lié à tentative de modification interdite avec aide possible sur la méthode.
- Exercice 6 : classer deux méthodes possibles pour liste de relevés avec aide possible sur la méthode.
- Exercice 7 : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle avec aide possible sur la méthode.
- Exercice 8 : étendre un énoncé volontairement erroné sur copie de liste avec aide possible sur la méthode.
## Corrigés complets des exercices du cours
- Corrigé exercice 1 : méthode : identifier `(36.8, 10.2)`, appliquer la méthode « lire sans modifier et nommer latitude puis longitude », puis écrire coordonnées conservées ; résultat : coordonnées conservées ; contrôle : faire apparaître le contrôle « tentative de modification interdite ».
- Corrigé exercice 2 : méthode : expliciter chaque étape de parcourir les valeurs et calculer une moyenne avant de conclure par `19` ; résultat : `19` ; contrôle : rédiger la méthode avant le résultat.
- Corrigé exercice 3 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `21` pour `temperature` ; résultat : `21` pour `temperature` ; contrôle : comparer avec le cas « clé absente ».
- Corrigé exercice 4 : méthode : isoler l’erreur fréquente « Copier une liste imbriquée seulement au premier niveau. » puis reprendre la procédure correcte ; résultat : modification locale contrôlée ; contrôle : corriger l’erreur « Copier une liste imbriquée seulement au premier niveau. ».
- Corrigé exercice 5 : méthode : identifier `(36.8, 10.2)`, appliquer la méthode « lire sans modifier et nommer latitude puis longitude », puis écrire coordonnées conservées ; résultat : le comportement de tuple de coordonnées est contrôlé ; contrôle : nommer la donnée minimale et la conclusion.
- Corrigé exercice 6 : méthode : expliciter chaque étape de parcourir les valeurs et calculer une moyenne avant de conclure par `19` ; résultat : la méthode robuste est choisie et justifiée ; contrôle : identifier pourquoi « Parcourir les indices quand les valeurs suffisent. » est une erreur.
- Corrigé exercice 7 : méthode : comparer la donnée avec le cas limite « clé absente » et valider `21` pour `temperature` ; résultat : la justification reste valable sur le nouveau cas ; contrôle : inclure une étape calculable par un pair.
- Corrigé exercice 8 : méthode : isoler l’erreur fréquente « Copier une liste imbriquée seulement au premier niveau. » puis reprendre la procédure correcte ; résultat : l’erreur est localisée puis réparée ; contrôle : proposer une activité corrective inspirée de « Modifier une sous-liste et observer l’effet sur la copie. ».

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
