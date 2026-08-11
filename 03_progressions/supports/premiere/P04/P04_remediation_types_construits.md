---
title: "P04 - Remediation - Types construits"
level: "premiere"
sequence_id: "P04"
document_type: "remediation"
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


# P04 - Remédiation - Types construits

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

### Remédiation EF1
- Erreur fréquente EF1 - Modifier un tuple comme une liste.
- Diagnostic : refaire tuple de coordonnées avec `(36.8, 10.2)` et repérer l’étape fautive.
- Activité corrective EF1 : Identifier mutabilité et usage avant d’écrire une affectation.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « tentative de modification interdite ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF2
- Erreur fréquente EF2 - Parcourir les indices quand les valeurs suffisent.
- Diagnostic : refaire liste de relevés avec `[18, 20, 19]` et repérer l’étape fautive.
- Activité corrective EF2 : Écrire deux boucles, avec indices puis avec valeurs, et comparer.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « liste vide ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF3
- Erreur fréquente EF3 - Accéder à une clé sans vérifier sa présence.
- Diagnostic : refaire dictionnaire avec `{"temperature": 21, "vent": 12}` et repérer l’étape fautive.
- Activité corrective EF3 : Tester `cle in dictionnaire` avant la lecture.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « clé absente ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
### Remédiation EF4
- Erreur fréquente EF4 - Copier une liste imbriquée seulement au premier niveau.
- Diagnostic : refaire copie de liste avec `[[1], [2]]` et repérer l’étape fautive.
- Activité corrective EF4 : Modifier une sous-liste et observer l’effet sur la copie.
- Nouvelle tâche : produire une réponse sur un cas voisin qui vérifie « liste imbriquée ».
- Critère de sortie : l’élève explique la correction sans reprendre la phrase du cours.
## Exercices numérotés
- Exercice 1 : résoudre tuple de coordonnées avec `(36.8, 10.2)` ; attendu : coordonnées conservées.
- Exercice 2 : expliquer liste de relevés à partir de `[18, 20, 19]` ; attendu : `19`.
- Exercice 3 : comparer dictionnaire avec `{"temperature": 21, "vent": 12}` ; attendu : `21` pour `temperature`.
- Exercice 4 : corriger copie de liste pour `[[1], [2]]` ; attendu : modification locale contrôlée.
- Exercice 5 : tester un cas limite lié à tentative de modification interdite ; attendu : le comportement de tuple de coordonnées est contrôlé.
- Exercice 6 : classer deux méthodes possibles pour liste de relevés ; attendu : la méthode robuste est choisie et justifiée.
- Exercice 7 : justifier un transfert qui utilise dictionnaire avec une donnée nouvelle ; attendu : la justification reste valable sur le nouveau cas.
- Exercice 8 : étendre un énoncé volontairement erroné sur copie de liste ; attendu : l’erreur est localisée puis réparée.

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
