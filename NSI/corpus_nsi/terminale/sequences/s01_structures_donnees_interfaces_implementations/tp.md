---
title: "TP - Interfaces de structures"
level: "terminale"
sequence_id: "s01_structures_donnees_interfaces_implementations"
document_type: "tp"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°8 du 25 juillet 2019"
theme: "Structures de données"
notion: "pile, file, graphe"
duration: "2 h"
difficulty: "standard"
private_data: false
official_program:
  level: "terminale"
  rubrique: "Structures de données"
  content: "TP"
  capacities:
    - id: "T-STRUCT-01A"
      label: "Interface et implémentation."
      evidence: [{section: "Étapes", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/tp.md", anchor: "#étapes", type: "tp"}]
    - id: "T-STRUCT-02A"
      label: "Classes."
      evidence: [{section: "Travail demandé", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/tp.md", anchor: "#travail-demandé", type: "tp"}]
    - id: "T-STRUCT-03B"
      label: "Piles, files, dictionnaires."
      evidence: [{section: "Travail demandé", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/tp.md", anchor: "#travail-demandé", type: "tp"}]
    - id: "T-STRUCT-05A"
      label: "Graphes."
      evidence: [{section: "Étapes", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/tp.md", anchor: "#étapes", type: "tp"}]
    - id: "T-LANG-03A"
      label: "Modules."
      evidence: [{section: "Fichiers fournis", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/tp.md", anchor: "#fichiers-fournis", type: "tp"}]
    - id: "T-LANG-05"
      label: "Tests et bugs."
      evidence: [{section: "Tests", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/tp.md", anchor: "#tests", type: "tp"}]
    - id: "T-ALGO-02A"
      label: "BFS comme application."
      evidence: [{section: "Extension experte", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/tp.md", anchor: "#extension-experte", type: "tp"}]
prerequisites: ["Cours et TD S01"]
learning_objectives: ["Utiliser et tester une mini-API de structures."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# TP - Interfaces de structures

## Contexte

Le fichier `python/structures_tools.py` propose une pile, une file et des fonctions de graphe.
Le TP demande d'utiliser cette API et de vérifier ses invariants.

## Objectif

Comprendre comment une interface peut rester stable même si l'implémentation change.

## Fichiers fournis

- `python/structures_tools.py`
- `tests/test_structures_tools.py`

## Travail demandé

Lire la classe `Stack`.
Identifier son attribut interne.
Utiliser seulement `push`, `pop`, `is_empty`, `size`.
Lire la classe `Queue`.
Utiliser seulement `enqueue`, `dequeue`, `is_empty`, `size`.
Construire un graphe à partir d'arêtes.
Produire sa matrice d'adjacence.
Reconstruire la liste d'adjacence depuis la matrice.
Expliquer quel code relève de l'interface.
Expliquer quel code relève de l'implémentation.

## Étapes

Étape 1 : exécuter les tests fournis.
Étape 2 : ajouter mentalement `1`, puis `2` dans une pile.
Étape 3 : vérifier que la sortie respecte LIFO.
Étape 4 : ajouter `A`, puis `B` dans une file.
Étape 5 : vérifier que la sortie respecte FIFO.
Étape 6 : construire le graphe `A-B`, `A-C`.
Étape 7 : obtenir la matrice selon l'ordre `A, B, C`.
Étape 8 : reconstruire la liste depuis la matrice.
Étape 9 : comparer les deux représentations.
Étape 10 : écrire une phrase sur le coût mémoire.
Étape 11 : écrire une phrase sur le test de relation directe.

## Tests

Commande : `python scripts/run_python_tests.py`.
Test de pile : deux entrées, deux sorties en ordre inverse.
Test de file : deux entrées, deux sorties dans le même ordre.
Test de matrice : vérifier la ligne du sommet `A`.
Test de reconstruction : vérifier que le graphe final égale le graphe initial.
Test d'erreur : matrice non carrée.

## Livrable

Rendre :
- les résultats de tests ;
- un schéma de graphe ;
- la liste d'adjacence ;
- la matrice d'adjacence ;
- deux phrases de comparaison.

## Critères de réussite

- L'interface est identifiée.
- Les invariants LIFO et FIFO sont testés.
- Les représentations de graphe concordent.
- Les limites sont mentionnées.

## Aides progressives

- Niveau 1 : dessiner les entrées et sorties.
- Niveau 2 : écrire la structure après chaque opération.
- Niveau 3 : expliquer la règle conservée.

## Erreurs fréquentes

- Lire l'attribut interne au lieu d'utiliser l'interface.
- Inverser LIFO et FIFO.
- Changer l'ordre des sommets entre liste et matrice.
- Tester seulement un graphe sans arête.

## Auto-évaluation

- Je sais exécuter les tests.
- Je sais expliquer une interface.
- Je sais vérifier une matrice.
- Je sais citer un cas limite.

## Extension experte

Utiliser `bfs_path` pour chercher un chemin.
Expliquer pourquoi la fonction utilise une file.
Tester le cas où aucun chemin n'existe.

## Point de fermeture

Chaque binôme termine en écrivant la structure choisie et la raison principale de ce choix.
