---
title: "P04 - Evaluation - Types construits"
level: "premiere"
sequence_id: "P04"
document_type: "evaluation"
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


# P04 - Évaluation courte - Types construits

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

## Questions
### Question 1
- Objectif évalué : O1.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé : résoudre tuple de coordonnées avec `(36.8, 10.2)`.
- Réponse attendue : coordonnées conservées.
- Critère de réussite : méthode visible, résultat correct et contrôle « tentative de modification interdite ».
### Question 2
- Objectif évalué : O2.
- Capacité officielle : P-DATA-CONSTR-02A, P-DATA-CONSTR-02D.
- Énoncé : on dispose de `releves = [18, 20, 19]`. Écrire une boucle `for valeur in releves` qui calcule la moyenne des relevés. Donner la trace (élément courant et cumul à chaque tour).
- Réponse attendue : `19` (moyenne = (18 + 20 + 19) / 3).
- Critère de réussite : boucle `for` sur les valeurs (pas les indices), résultat correct et contrôle « liste vide ».
### Question 3
- Objectif évalué : O3.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé : comparer dictionnaire avec `{"temperature": 21, "vent": 12}`.
- Réponse attendue : `21` pour `temperature`.
- Critère de réussite : méthode visible, résultat correct et contrôle « clé absente ».
### Question 4
- Objectif évalué : O4.
- Capacité officielle : P-DATA-CONSTR-02A.
- Énoncé : corriger copie de liste pour `[[1], [2]]`.
- Réponse attendue : modification locale contrôlée.
- Critère de réussite : méthode visible, résultat correct et contrôle « liste imbriquée ».
## Barème
- Question 1 : 2 points méthode, 1 point résultat, 1 point justification liée à tentative de modification interdite.
- Question 2 : 2 points méthode, 1 point résultat, 1 point justification liée à liste vide.
- Question 3 : 2 points méthode, 1 point résultat, 1 point justification liée à clé absente.
- Question 4 : 2 points méthode, 1 point résultat, 1 point justification liée à liste imbriquée.
- Question 5 : 1 point rôle du tuple, 1 point rôle du dictionnaire, 1 point rôle de la liste, 1 point calcul du milieu `(3.0, 7.0)`.
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

## Question complémentaire - structures combinées
### Question 5
- Données : `stations = [{"nom": "A", "coord": (0, 4), "temperature": 21}, {"nom": "B", "coord": (6, 10), "temperature": 18}]`.
- Travail : expliquer le rôle du tuple, de la liste et du dictionnaire dans cette donnée, puis calculer le milieu des deux coordonnées.

### Corrigé question 5
- Tuple : chaque `coord` est un couple immuable.
- Dictionnaire : chaque station associe les clés `nom`, `coord`, `temperature` à des valeurs.
- Liste : `stations` rassemble plusieurs dictionnaires et se parcourt.
- Résultat attendu : le milieu est `((0+6)/2, (4+10)/2) = (3.0, 7.0)`.
- Contrôle : le résultat est un tuple numérique de deux coordonnées.

## Exercices numérotés
- Exercice 1 : reprendre question 1 en explicitant donnée, méthode, résultat et contrôle pour P04.
- Exercice 2 : reprendre question 2 en explicitant donnée, méthode, résultat et contrôle pour P04.
- Exercice 3 : reprendre question 3 en explicitant donnée, méthode, résultat et contrôle pour P04.
- Exercice 4 : reprendre question 4 en explicitant donnée, méthode, résultat et contrôle pour P04.

## Corrigé
### Corrigé question 1
- Résultat attendu : coordonnées conservées.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 1.
- Critère de validation : méthode visible, résultat correct et contrôle « tentative de modification interdite ».
### Corrigé question 2
- Résultat attendu : `19`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 2.
- Critère de validation : méthode visible, résultat correct et contrôle « liste vide ».
### Corrigé question 3
- Résultat attendu : `21` pour `temperature`.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 3.
- Critère de validation : méthode visible, résultat correct et contrôle « clé absente ».
### Corrigé question 4
- Résultat attendu : modification locale contrôlée.
- Méthode exigée : reprendre la démarche du cours puis vérifier le cas limite de la question 4.
- Critère de validation : méthode visible, résultat correct et contrôle « liste imbriquée ».

## Modalités de passation
- Durée : 25 minutes.
- Matériel autorisé : fiche types construits, sans corrigé distribué ni navigation externe.
- Capacités évaluées :
- P-DATA-CONSTR-02A
- P-DATA-CONSTR-02D

## Fiche liée et aménagement
- Fiche liée : fiche de cours opérationnelle de la séquence P04, statut `needs_review`.
- Séance liée : `P04-S1`, avec question centrée sur tuples, listes et dictionnaires.
- Version aménagée : données tuples, listes et dictionnaires surlignées et tableau réponse en trois zones.
- Remédiation : corriger une mutation de liste sur un exemple à trois éléments, puis verbaliser la méthode en binôme.
