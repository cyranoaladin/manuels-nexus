---
title: "TD - Structures de données"
level: "terminale"
sequence_id: "s01_structures_donnees_interfaces_implementations"
document_type: "td"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°8 du 25 juillet 2019"
theme: "Structures de données"
notion: "exercices structures"
duration: "2 h"
difficulty: "standard"
private_data: false
official_program:
  level: "terminale"
  rubrique: "Structures de données"
  content: "TD"
  capacities:
    - id: "T-STRUCT-01A"
      label: "Interface et implémentation."
      evidence: [{section: "Exercices", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/td.md", anchor: "#exercices", type: "td"}]
    - id: "T-STRUCT-02A"
      label: "Classes."
      evidence: [{section: "Écriture de code", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/td.md", anchor: "#écriture-de-code", type: "td"}]
    - id: "T-STRUCT-03B"
      label: "Structures linéaires et dictionnaires."
      evidence: [{section: "Exercices", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/td.md", anchor: "#exercices", type: "td"}]
    - id: "T-STRUCT-05A"
      label: "Graphes."
      evidence: [{section: "Exercices", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/td.md", anchor: "#exercices", type: "td"}]
    - id: "T-LANG-03A"
      label: "Modules."
      evidence: [{section: "Analyse de code", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/td.md", anchor: "#analyse-de-code", type: "td"}]
    - id: "T-LANG-05"
      label: "Bugs."
      evidence: [{section: "Analyse de code", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/td.md", anchor: "#analyse-de-code", type: "td"}]
    - id: "T-ALGO-02A"
      label: "Parcours graphes."
      evidence: [{section: "Exercices", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/td.md", anchor: "#exercices", type: "td"}]
prerequisites: ["Cours S01"]
learning_objectives: ["S'entraîner sur interfaces, structures et graphes."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# TD - Structures de données

## Situation-problème

Une plateforme doit gérer annulations, files d'attente, clients et routes.
Chaque exercice impose de choisir une structure et de justifier ce choix.

## Objectifs

- Distinguer interface et implémentation.
- Manipuler LIFO et FIFO.
- Justifier un dictionnaire.
- Construire deux représentations de graphe.
- Analyser du code de structure.

## Exercices

### Exercice 1 - Socle - Interface

Donner trois opérations de l'interface d'une pile.
Dire si `_items` appartient à l'interface ou à l'implémentation.
Expliquer pourquoi le programme utilisateur ne doit pas dépendre de `_items`.

### Exercice 2 - Socle - LIFO

On empile `A`, puis `B`, puis `C`.
Donner l'ordre de sortie.
Donner un exemple d'usage naturel d'une pile.
Dire quel bug apparaît si on retire le premier élément au lieu du dernier.

### Exercice 3 - Socle - FIFO

On enfile `A`, puis `B`, puis `C`.
Donner l'ordre de sortie.
Donner un exemple d'usage naturel d'une file.
Comparer avec l'exercice 2.

### Exercice 4 - Standard - Dictionnaire

On stocke des fiches par identifiant fictif.
Proposer une structure.
Ecrire un exemple de dictionnaire.
Expliquer pourquoi une liste de fiches serait moins adaptée pour une recherche fréquente.

### Exercice 5 - Standard - Graphe

Sommets : `A`, `B`, `C`, `D`.
Liens non orientés : `A-B`, `A-C`, `B-D`.
Construire la liste d'adjacence.
Construire la matrice avec l'ordre `A, B, C, D`.
Dire quelle représentation est la plus lisible ici.

### Exercice 6 - Standard - Coût

Un graphe de 1000 sommets contient 1200 liens.
Comparer qualitativement matrice et liste d'adjacence.
Calculer le nombre de cases de la matrice.
Expliquer pourquoi beaucoup de cases valent zéro.

### Exercice 7 - Expert - BFS

On veut trouver un chemin avec le plus petit nombre d'arêtes dans un graphe non pondéré.
Dire pourquoi une file est pertinente.
Décrire les informations stockées dans la file.
Donner un cas limite : départ égal à arrivée.

### Exercice 8 - Expert - Interface stable

Une file est d'abord codée avec une liste.
Puis elle est recodée avec `deque`.
Expliquer ce qui doit rester identique pour le reste du programme.
Ecrire deux tests qui protègent cette stabilité.

### Exercice 9 - Analyse de code

Lire :
```python
class Pile:
    def __init__(self):
        self.items = []
    def push(self, x):
        self.items.append(x)
    def pop(self):
        return self.items.pop(0)
```
Identifier l'intention annoncée.
Identifier le problème.
Proposer la correction.
Proposer un test qui révèle l'erreur.

### Exercice 10 - Écriture de code

Ecrire une classe `FileSimple` avec `enqueue`, `dequeue`, `is_empty`.
Utiliser une liste ou `deque`.
Prévoir le cas de file vide.
Ecrire trois tests.

## Analyse de code

L'exercice 9 vérifie que le nom d'une méthode ne suffit pas.
Le comportement doit respecter l'invariant annoncé.

## Écriture de code

L'exercice 10 impose d'écrire une interface minimale.
Le corrigé associé donne une solution commentée.

## Justification

Chaque réponse doit relier structure et opération.
Une réponse sans opération dominante n'est pas assez argumentée.

## Aides progressives

- Socle : écrire LIFO ou FIFO en toutes lettres.
- Standard : dessiner les entrées et sorties.
- Expert : écrire un test avant le code.

## Erreurs fréquentes

- Inverser pile et file.
- Confondre sommet et arête.
- Oublier les sommets sans voisin.
- Confondre interface et attribut interne.

## Auto-évaluation

- Je sais justifier une structure.
- Je sais construire une liste d'adjacence.
- Je sais construire une matrice.
- Je sais écrire un test d'invariant.

## Corrigé associé

Voir `corrige.md`, section `Réponse attendue - TD`.
