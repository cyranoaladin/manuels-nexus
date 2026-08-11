---
title: "Corrigé - Structures de données"
level: "terminale"
sequence_id: "s01_structures_donnees_interfaces_implementations"
document_type: "corrige"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°8 du 25 juillet 2019"
theme: "Structures de données"
notion: "corrections"
duration: "1 h"
difficulty: "standard"
private_data: false
official_program:
  level: "terminale"
  rubrique: "Structures de données"
  content: "Corrigé"
  capacities:
    - id: "T-STRUCT-01A"
      label: "Interface et implémentation."
      evidence: [{section: "Réponse attendue - TD", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/corrige.md", anchor: "#réponse-attendue-td", type: "corrige"}]
    - id: "T-STRUCT-02A"
      label: "Classes."
      evidence: [{section: "Réponse attendue - TD", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/corrige.md", anchor: "#réponse-attendue-td", type: "corrige"}]
    - id: "T-STRUCT-03B"
      label: "Structures linéaires."
      evidence: [{section: "Réponse attendue - TD", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/corrige.md", anchor: "#réponse-attendue-td", type: "corrige"}]
    - id: "T-STRUCT-05A"
      label: "Graphes."
      evidence: [{section: "Réponse attendue - TD", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/corrige.md", anchor: "#réponse-attendue-td", type: "corrige"}]
    - id: "T-LANG-03A"
      label: "Modules."
      evidence: [{section: "Code testé", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/corrige.md", anchor: "#code-testé", type: "corrige"}]
    - id: "T-LANG-05"
      label: "Bugs."
      evidence: [{section: "Erreurs fréquentes", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/corrige.md", anchor: "#erreurs-fréquentes", type: "corrige"}]
    - id: "T-ALGO-02A"
      label: "Parcours graphes."
      evidence: [{section: "Variante acceptable", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/corrige.md", anchor: "#variante-acceptable", type: "corrige"}]
prerequisites: ["TD, TP"]
learning_objectives: ["Corriger avec justification."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Corrigé - Structures de données

## Réponse attendue - TD

### Exercice 1

Interface d'une pile : `push`, `pop`, `is_empty`.
`_items` relève de l'implémentation.
Le programme utilisateur ne doit pas dépendre de `_items`.
Sinon un changement interne casse le code utilisateur.

### Exercice 2

Sortie : `C`, puis `B`, puis `A`.
Usage naturel : historique de navigation ou pile d'appels.
Si on retire le premier élément, on obtient FIFO et non LIFO.

### Exercice 3

Sortie : `A`, puis `B`, puis `C`.
Usage naturel : file d'attente.
La file conserve l'ordre d'arrivée.
La pile inverse l'ordre d'arrivée.

### Exercice 4

Structure attendue : dictionnaire.
Exemple : `clients = {"c01": {"statut": "actif"}}`.
Une liste impose de parcourir les fiches pour retrouver l'identifiant.

### Exercice 5

Liste d'adjacence :
`A: [B, C]`.
`B: [A, D]`.
`C: [A]`.
`D: [B]`.
Matrice ordre `A, B, C, D` :
`A: 0 1 1 0`.
`B: 1 0 0 1`.
`C: 1 0 0 0`.
`D: 0 1 0 0`.
La liste est lisible car le graphe a peu de liens.

### Exercice 6

La matrice contient `1000 * 1000 = 1 000 000` cases.
Avec seulement 1200 liens, beaucoup de cases valent zéro.
La liste d'adjacence est plus économique en mémoire dans ce cas.

### Exercice 7

BFS utilise une file pour traiter d'abord les sommets à distance 1, puis 2, etc.
La file peut stocker des chemins ou des couples sommet-prédécesseur.
Si départ égale arrivée, le chemin est immédiatement trouvé.

### Exercice 8

L'interface doit rester `enqueue`, `dequeue`, `is_empty`.
Test 1 : ajouter `A`, puis `B`, retirer `A`.
Test 2 : la file vide signale une erreur ou un état vide selon contrat.

### Exercice 9

L'intention annoncée est une pile.
Le problème est `pop(0)`, qui retire le premier élément.
La correction est `pop()`.
Test révélateur : empiler `A`, puis `B`, dépiler doit donner `B`.

### Exercice 10

Solution possible :
```python
from collections import deque

class FileSimple:
    def __init__(self):
        self.items = deque()
    def enqueue(self, x):
        self.items.append(x)
    def dequeue(self):
        if not self.items:
            raise IndexError("file vide")
        return self.items.popleft()
    def is_empty(self):
        return len(self.items) == 0
```

## Justification

Une correction acceptable cite l'invariant.
Pour une pile, l'invariant vérifié est LIFO.
Pour une file, l'invariant vérifié est FIFO.
Pour un graphe, la représentation doit conserver les mêmes relations.
Pour une API, le code utilisateur doit dépendre des méthodes publiques.

## Variante acceptable

Une pile peut être codée avec une liste Python.
Une file peut être codée avec `deque`.
Une file peut aussi être codée avec deux piles dans une extension.
BFS peut stocker les sommets seuls ou des chemins entiers selon le besoin.

## Erreurs fréquentes

- Appeler une structure "pile" mais appliquer FIFO.
- Changer l'ordre des sommets entre matrice et liste.
- Oublier le cas de structure vide.
- Tester seulement une opération.
- Confondre graphe orienté et non orienté.

## Barème

- Interface et vocabulaire : 4 points.
- Pile/file/dictionnaire : 5 points.
- Graphe et représentations : 5 points.
- Analyse de code : 3 points.
- Tests et justification : 3 points.

## Code testé

Le module support est `python/structures_tools.py`.
Les tests sont dans `tests/test_structures_tools.py`.
La commande de référence est `python scripts/run_python_tests.py`.
Les tests vérifient LIFO, FIFO, conversion graphe-matrice et BFS simple.
