---
title: "Trace écrite - Structures de données"
level: "terminale"
sequence_id: "s01_structures_donnees_interfaces_implementations"
document_type: "trace"
status: "needs_review"
version: "0.2.0"
source: "BO spécial n°8 du 25 juillet 2019"
theme: "Structures de données"
notion: "interface, implémentation, pile, file, graphe"
duration: "30 min"
difficulty: "standard"
private_data: false
official_program:
  level: "terminale"
  rubrique: "Structures de données"
  content: "Synthèse"
  capacities:
    - id: "T-STRUCT-01A"
      label: "Interface et implémentation."
      evidence: [{section: "Notions essentielles", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/trace_ecrite.md", anchor: "#notions-essentielles", type: "trace"}]
    - id: "T-STRUCT-02A"
      label: "Classes, attributs, méthodes."
      evidence: [{section: "Définitions", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/trace_ecrite.md", anchor: "#définitions", type: "trace"}]
    - id: "T-STRUCT-03B"
      label: "Listes, piles, files, dictionnaires."
      evidence: [{section: "Méthodes", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/trace_ecrite.md", anchor: "#méthodes", type: "trace"}]
    - id: "T-STRUCT-05A"
      label: "Graphes."
      evidence: [{section: "Exemples minimaux", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/trace_ecrite.md", anchor: "#exemples-minimaux", type: "trace"}]
    - id: "T-LANG-03A"
      label: "API et modules."
      evidence: [{section: "À savoir refaire", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/trace_ecrite.md", anchor: "#à-savoir-refaire", type: "trace"}]
    - id: "T-LANG-05"
      label: "Gestion des bugs."
      evidence: [{section: "Points de vigilance", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/trace_ecrite.md", anchor: "#points-de-vigilance", type: "trace"}]
    - id: "T-ALGO-02A"
      label: "Parcours de graphes."
      evidence: [{section: "À savoir refaire", file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/trace_ecrite.md", anchor: "#à-savoir-refaire", type: "trace"}]
prerequisites: ["Cours Terminale S01"]
learning_objectives: ["Mémoriser les choix de structure et leurs invariants."]
assessment: {formative: true, summative: false}
last_review: {pedagogy: "", science: "", technical: ""}
---

# Trace écrite - Structures de données

## Notions essentielles

- Une interface décrit les opérations visibles.
- Une implémentation décrit la réalisation concrète.
- Une pile suit LIFO.
- Une file suit FIFO.
- Un dictionnaire donne un accès par clé.
- Un graphe représente des relations entre sommets.
- Une liste d'adjacence associe chaque sommet à ses voisins.
- Une matrice d'adjacence est un tableau carré de relations.
- BFS utilise une file.
- DFS utilise une pile ou la récursivité.

## Définitions

- Structure abstraite : description des opérations sans code imposé.
- Interface : contrat d'utilisation.
- Implémentation : code qui réalise le contrat.
- Attribut : donnée portée par un objet.
- Méthode : fonction associée à un objet.
- Invariant : propriété que la structure doit conserver.

## Méthodes

- Pour choisir une structure, nommer l'opération dominante.
- Dernier entré, premier sorti : pile.
- Premier entré, premier sorti : file.
- Recherche par identifiant : dictionnaire.
- Relations entre objets : graphe.
- Graphe peu dense : liste d'adjacence souvent adaptée.
- Test direct de relation : matrice d'adjacence souvent pratique.

## Exemples minimaux

- Pile : historique de retour arrière.
- File : tickets traités par ordre d'arrivée.
- Dictionnaire : fiche par identifiant.
- Graphe : réseau de stations.
- Liste d'adjacence : `A: [B, C]`.
- Matrice d'adjacence : ligne `A = 0 1 1`.

## Points de vigilance

- Ne pas confondre interface et implémentation.
- Ne pas inverser LIFO et FIFO.
- Ne pas exposer inutilement les attributs internes.
- Ne pas oublier les sommets isolés.
- Ne pas traiter un graphe orienté comme non orienté.

## À savoir refaire

- Ecrire l'interface d'une pile.
- Ecrire l'interface d'une file.
- Implémenter une pile simple.
- Implémenter une file simple.
- Construire une liste d'adjacence.
- Construire une matrice d'adjacence.
- Expliquer pourquoi BFS utilise une file.
- Donner un test d'invariant.

## Auto-positionnement

- Je définis interface et implémentation.
- Je distingue pile et file.
- Je justifie un dictionnaire.
- Je représente un graphe de deux façons.
- Je cite un cas limite.
