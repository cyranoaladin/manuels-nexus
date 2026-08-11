---
title: "Évaluation - structures abstraites et implémentations"
niveau: terminale
source: "BO spécial n°8 du 25 juillet 2019 - NSI Terminale"
status: needs_review
version: "0.2.0"
notion: "pile, file, dictionnaire, graphe"
objectifs:
  - "Évaluer le choix argumenté d'une structure de données."
  - "Évaluer la lecture et l'écriture de code court."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
official_program:
  level: terminale
  rubrique: "Structures de données"
  content: "Structures abstraites et implémentations"
  capacities:
    - id: T-STRUCT-01A
      label: "Distinguer interface et implémentation d'une structure de données"
      evidence: [{section: "Compétences évaluées", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/evaluation.md", anchor: "#compétences-évaluées", type: "evaluation"}]
    - id: T-STRUCT-02A
      label: "Spécifier et utiliser listes, piles et files"
      evidence: [{section: "Questions progressives", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/evaluation.md", anchor: "#questions-progressives", type: "evaluation"}]
    - id: T-STRUCT-05A
      label: "Représenter un graphe par liste d'adjacence ou matrice d'adjacence"
      evidence: [{section: "Analyse de code", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/evaluation.md", anchor: "#analyse-de-code", type: "evaluation"}]
---

# Évaluation - structures abstraites et implémentations

## Durée

Durée : 55 minutes.

Lecture : 5 minutes.

Questions de cours : 10 minutes.

Analyse de code : 15 minutes.

Programmation : 15 minutes.

Justification écrite : 10 minutes.

## Matériel autorisé

Une feuille de synthèse personnelle manuscrite est autorisée.

Aucun accès réseau n'est autorisé.

L'environnement Python local est autorisé pour la partie programmation si l'évaluation est organisée sur machine.

Le corrigé n'est pas fourni pendant l'épreuve.

## Compétences évaluées

Distinguer interface et implémentation.

Choisir pile, file, dictionnaire ou graphe selon un besoin.

Construire une liste d'adjacence.

Construire ou lire une matrice d'adjacence.

Analyser un coût d'accès de manière qualitative.

Écrire un code court avec tests de cas limites.

Justifier une décision technique en français précis.

## Barème

Total : 20 points.

Question 1 : 3 points.

Question 2 : 3 points.

Question 3 : 4 points.

Question 4 : 5 points.

Question 5 : 3 points.

Présentation, vocabulaire et rigueur : 2 points.

Un raisonnement exact avec une erreur mineure de syntaxe peut recevoir une partie des points.

Un résultat sans justification ne reçoit pas tous les points.

## Questions progressives

### Question 1 - Interface ou implémentation

On considère une structure qui offre les opérations `ajouter`, `retirer`, `est_vide`.

1. Cette description relève-t-elle plutôt de l'interface ou de l'implémentation ?

2. Donner deux implémentations Python possibles pour une file.

3. Expliquer pourquoi l'utilisateur de l'interface ne devrait pas dépendre du choix interne.

### Question 2 - Pile et file

On ajoute successivement A, B, C dans une structure.

1. Quel élément sort d'abord si la structure est une pile ?

2. Quel élément sort d'abord si la structure est une file ?

3. Donner un exemple d'application réelle de chaque structure.

### Question 3 - Choix de structure

Une application gère des messages reçus par ordre chronologique.

Chaque message possède un identifiant unique.

On doit traiter les messages dans l'ordre d'arrivée et pouvoir retrouver rapidement un message par son identifiant.

1. Quelle structure utiliser pour l'ordre de traitement ?

2. Quelle structure utiliser pour l'accès par identifiant ?

3. Expliquer pourquoi une seule liste n'est pas le choix le plus robuste.

## Analyse de code

### Question 4 - Graphe

On donne le code suivant.

```python
reseau = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A"],
    "D": ["B"],
}
```

1. Quelle représentation de graphe est utilisée ?

2. Citer les voisins de `A`.

3. L'arête entre `C` et `D` existe-t-elle ? Justifier.

4. Proposer une matrice d'adjacence avec l'ordre `A, B, C, D`.

5. Comparer l'intérêt de la liste et de la matrice pour tester une arête.

## Programmation

### Question 5 - File de traitement

Écrire une fonction `traiter_file(demandes)` qui reçoit une liste de chaînes.

La fonction doit retourner une liste contenant les demandes dans le même ordre.

La fonction doit utiliser une file explicite.

La fonction doit traiter le cas d'une liste vide.

Un test minimal est attendu.

Exemple attendu :

```python
traiter_file(["A", "B", "C"]) == ["A", "B", "C"]
traiter_file([]) == []
```

## Justification

Rédiger cinq lignes pour expliquer pourquoi une file est adaptée à la question 5.

La justification doit employer les mots interface, implémentation et ordre d'arrivée.

## Corrigé lié

Le corrigé est dans [corrige.md](./corrige.md).

Le barème détaillé est repris dans le corrigé.

Le code de référence s'appuie sur `collections.deque`.
