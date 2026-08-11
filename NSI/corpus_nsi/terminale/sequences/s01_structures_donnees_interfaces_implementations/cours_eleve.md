---
title: "S01 - Structures de données : interfaces et implémentations"
level: "terminale"
sequence_id: "s01_structures_donnees_interfaces_implementations"
document_type: "cours"
status: "needs_review"
version: "0.2.0"
authors: ["NSI"]
source: "BO spécial n°8 du 25 juillet 2019"
theme: "Structures de données"
notion: "interface, implémentation, pile, file, dictionnaire, graphe"
duration: "5 séances"
difficulty: "standard"
private_data: false
official_program:
  level: "terminale"
  rubrique: "Structures de données"
  content: "Interfaces, implémentations, structures linéaires, dictionnaires, graphes"
  capacities:
    - id: "T-STRUCT-01A"
      label: "Spécifier une structure par son interface et distinguer interface et implémentation."
      evidence:
        - section: "Structure abstraite, interface, implémentation"
          file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/cours_eleve.md"
          anchor: "#structure-abstraite-interface-implémentation"
          type: "cours"
    - id: "T-STRUCT-02A"
      label: "Écrire une classe et accéder aux attributs et méthodes."
      evidence:
        - section: "Classes, attributs et méthodes"
          file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/cours_eleve.md"
          anchor: "#classes-attributs-et-méthodes"
          type: "cours"
    - id: "T-STRUCT-03B"
      label: "Distinguer listes, piles, files, dictionnaires et choisir une structure."
      evidence:
        - section: "Piles, files et dictionnaires"
          file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/cours_eleve.md"
          anchor: "#piles-files-et-dictionnaires"
          type: "cours"
    - id: "T-STRUCT-05A"
      label: "Modéliser un graphe et passer d'une représentation à une autre."
      evidence:
        - section: "Graphes comme structures relationnelles"
          file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/cours_eleve.md"
          anchor: "#graphes-comme-structures-relationnelles"
          type: "cours"
    - id: "T-LANG-03A"
      label: "Utiliser des API ou bibliothèques et créer des modules simples documentés."
      evidence:
        - section: "Modularité et API"
          file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/cours_eleve.md"
          anchor: "#modularité-et-api"
          type: "cours"
    - id: "T-LANG-05"
      label: "Répondre aux causes typiques de bugs."
      evidence:
        - section: "Tests, bugs et cas limites"
          file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/cours_eleve.md"
          anchor: "#tests-bugs-et-cas-limites"
          type: "cours"
    - id: "T-ALGO-02A"
      label: "Parcourir un graphe en profondeur ou largeur, repérer un cycle, chercher un chemin."
      evidence:
        - section: "BFS et DFS comme activité d'application"
          file: "terminale/sequences/s01_structures_donnees_interfaces_implementations/cours_eleve.md"
          anchor: "#bfs-et-dfs-comme-activité-dapplication"
          type: "cours"
prerequisites:
  - "Listes et dictionnaires Python."
  - "Fonctions et tests simples."
learning_objectives:
  - "Distinguer interface et implémentation."
  - "Comparer pile, file, dictionnaire et graphe selon les opérations."
  - "Représenter un graphe par liste d'adjacence ou matrice."
  - "Justifier un coût simple en mémoire ou en temps."
assessment:
  formative: true
  summative: false
last_review:
  pedagogy: ""
  science: ""
  technical: ""
---

# S01 - Structures de données : interfaces et implémentations

## Situation-problème

Une application de livraison doit gérer des colis en attente.
Elle doit aussi gérer des tickets de support.
Elle doit chercher rapidement un client par identifiant.
Elle doit représenter un réseau de dépôts reliés par des routes.
Une seule structure Python ne suffit pas à tout faire proprement.
Une liste peut stocker une suite.
Une pile peut gérer le dernier élément arrivé.
Une file peut gérer le premier élément arrivé.
Un dictionnaire peut donner un accès par clé.
Un graphe peut représenter des relations.
La question de la séquence est donc la suivante.
Comment séparer ce qu'une structure promet de faire de la façon dont elle est codée ?

## Objectifs

- Définir structure abstraite, interface et implémentation.
- Lire une interface comme un contrat d'utilisation.
- Implémenter une pile et une file.
- Expliquer LIFO et FIFO.
- Choisir entre liste, pile, file et dictionnaire.
- Modéliser une situation par un graphe.
- Représenter un graphe par liste d'adjacence.
- Représenter un graphe par matrice d'adjacence.
- Comparer grossièrement les coûts des représentations.
- Utiliser des tests pour repérer les cas limites.

## Prérequis

- Savoir écrire une fonction Python.
- Savoir lire une liste Python.
- Savoir utiliser un dictionnaire Python.
- Savoir lire une boucle `for`.
- Savoir utiliser un test unitaire simple.
- Savoir expliquer une condition.

## Limites de la séquence

Cette séquence ne commence pas par BFS ou DFS.
BFS et DFS apparaissent comme applications sur graphes.
Les arbres binaires ne sont pas étudiés ici.
Les arbres binaires de recherche sont seulement signalés comme aperçu non évalué.
Les parcours d'arbres et l'insertion dans un ABR relèvent d'une autre séquence.
La programmation objet est utilisée de façon limitée.
L'héritage et le polymorphisme ne sont pas attendus ici.

## Activité d'introduction

On distribue quatre cartes de contraintes.
Carte A : le dernier ticket ouvert doit être traité en premier.
Carte B : le premier colis arrivé doit partir en premier.
Carte C : un client doit être retrouvé par identifiant.
Carte D : les dépôts sont reliés par des routes.
Question 1 : quelle opération est centrale dans chaque carte ?
Question 2 : quelle structure semble naturelle ?
Question 3 : peut-on changer le code interne sans changer les opérations promises ?
Question 4 : pourquoi une liste brute ne suffit-elle pas à expliquer l'intention ?

## Formalisation

Une structure de données organise des valeurs pour permettre certaines opérations.
Elle n'est pas seulement un conteneur.
Elle exprime une manière d'accéder aux données.
Elle exprime aussi les opérations considérées comme normales.
Une pile promet `push`, `pop`, `is_empty`.
Une file promet `enqueue`, `dequeue`, `is_empty`.
Un dictionnaire promet l'accès par clé.
Un graphe promet l'accès aux voisins ou aux relations.
L'interface décrit les opérations offertes.
L'implémentation décrit comment ces opérations sont codées.
Deux implémentations peuvent respecter la même interface.
Cette séparation permet de changer le code interne sans changer le reste du programme.

## Définitions

Définition 1 : une structure abstraite de données décrit des opérations sans imposer le code interne.
Définition 2 : une interface est l'ensemble des opérations visibles et leur contrat d'utilisation.
Définition 3 : une implémentation est une réalisation concrète de l'interface.
Définition 4 : une pile est une structure LIFO où le dernier élément ajouté sort en premier.
Définition 5 : une file est une structure FIFO où le premier élément ajouté sort en premier.
Définition 6 : un dictionnaire associe des clés à des valeurs pour accéder par clé.
Définition 7 : un graphe est une structure relationnelle composée de sommets et de liens.
Définition 8 : une liste d'adjacence associe à chaque sommet la liste de ses voisins.
Définition 9 : une matrice d'adjacence indique par un tableau carré si deux sommets sont reliés.

## Structure abstraite, interface, implémentation

Une structure abstraite répond à la question "que peut-on faire ?".
Une implémentation répond à la question "comment est-ce codé ?".
Exemple : une file peut être implémentée avec une liste.
Exemple : une file peut être implémentée avec deux piles.
Dans les deux cas, l'utilisateur veut seulement `enqueue` et `dequeue`.
Le reste du programme ne devrait pas dépendre du détail interne.
Cette idée limite les effets de bord lors d'un changement.
Elle rend les tests plus ciblés.
Elle rend le code plus lisible.
Elle aide à comparer plusieurs solutions.

### Exemple corrigé 1

Interface d'une pile :
`push(x)` ajoute `x`.
`pop()` retire et renvoie le dernier élément ajouté.
`is_empty()` indique si la pile est vide.
Implémentation possible : une liste Python.
`push(x)` utilise `append`.
`pop()` utilise `pop`.
Le code interne peut changer.
L'interface doit rester stable pour l'utilisateur.

### Contre-exemple 1

Utiliser directement `ma_liste.append` partout dans un programme ne dit pas si l'on modélise une pile.
Le code peut fonctionner.
Mais l'intention est moins claire.
Une fonction `push` exprime mieux le contrat.

### Exercice intégré 1

Donner l'interface minimale d'une pile.
Donner l'interface minimale d'une file.
Dire ce qui relève de l'interface et ce qui relève de l'implémentation.

## Classes, attributs et méthodes

Une classe Python peut regrouper données et opérations.
Un attribut stocke une donnée interne.
Une méthode décrit une opération associée à l'objet.
Dans une pile, l'attribut interne peut être une liste.
La méthode `push` ajoute dans cette liste.
La méthode `pop` retire depuis cette liste.
Le caractère interne de la liste doit rester un détail.
Le programme utilisateur doit appeler les méthodes prévues.

### Exemple corrigé 2

Une classe `Stack` peut contenir `_items`.
`_items` est une liste interne.
`push` ajoute un élément.
`pop` retire un élément.
`size` donne la taille.
Si `_items` est remplacée par une autre structure, l'utilisateur de `Stack` ne change pas son code.

### Erreur fréquente 1

Accéder directement à l'attribut interne depuis l'extérieur.
Cela casse l'abstraction.
Cela rend un changement d'implémentation risqué.
Une interface est utile seulement si on l'utilise vraiment.

## Piles, files et dictionnaires

Une pile suit la règle LIFO.
LIFO signifie "last in, first out".
Le dernier élément ajouté est le premier retiré.
Exemples : pile d'assiettes, retour arrière, appels récursifs.
Une file suit la règle FIFO.
FIFO signifie "first in, first out".
Le premier élément ajouté est le premier retiré.
Exemples : file d'attente, impression, tickets traités dans l'ordre.
Un dictionnaire organise l'accès par clé.
La clé peut être un identifiant.
La valeur peut être une fiche ou un objet.
Une liste cherche souvent par parcours.
Un dictionnaire est adapté quand la clé est centrale.
La question n'est pas "quelle structure est meilleure ?".
La question est "quelle structure sert l'opération dominante ?".

### Exemple corrigé 3

Tickets à traiter dans l'ordre d'arrivée.
Structure : file.
Opération principale : retirer le ticket arrivé le plus tôt.
Interface : `enqueue(ticket)`, `dequeue()`.
Utiliser une pile serait contraire à la règle métier.

### Exemple corrigé 4

Clients indexés par identifiant.
Structure : dictionnaire.
Opération principale : retrouver vite une fiche par identifiant.
Interface : `clients[id_client]`.
Une liste de fiches obligerait un parcours.

### Exercice intégré 2

Choisir une structure pour un historique de navigation.
Choisir une structure pour une salle d'attente.
Choisir une structure pour un annuaire par identifiant.
Justifier par l'opération dominante.

## Modularité et API

Une API expose les opérations à utiliser.
Une bibliothèque fournit souvent plusieurs structures.
Utiliser une API impose de lire sa documentation.
Créer un module simple impose de documenter ses fonctions.
Le fichier `python/structures_tools.py` sert de mini-API pédagogique.
Il expose `Stack`, `Queue`, `adjacency_list_from_edges`, `adjacency_matrix`.
Les tests vérifient l'interface, pas seulement le détail interne.
Un module de structures doit rester lisible.
Un module de structures doit annoncer ses erreurs.
Un module de structures doit éviter les dépendances inutiles.

## Graphes comme structures relationnelles

Un graphe représente des relations.
Les sommets représentent les objets.
Les arêtes ou arcs représentent les liens.
Un graphe non orienté a des liens symétriques.
Un graphe orienté a des liens avec un sens.
Un réseau routier simple peut être non orienté.
Un réseau de dépendances peut être orienté.
Un graphe peut se représenter par liste d'adjacence.
Un graphe peut se représenter par matrice d'adjacence.
La liste d'adjacence est compacte si le graphe a peu d'arêtes.
La matrice d'adjacence permet de tester rapidement si deux sommets sont reliés.
Le choix dépend du traitement.

### Exemple corrigé 5

Sommets : `A`, `B`, `C`.
Arêtes : `A-B`, `A-C`.
Liste d'adjacence :
`A: [B, C]`.
`B: [A]`.
`C: [A]`.
Matrice avec ordre `A, B, C` :
ligne `A` : `0 1 1`.
ligne `B` : `1 0 0`.
ligne `C` : `1 0 0`.
Les deux représentations décrivent le même graphe.

### Contre-exemple 2

Dire qu'une matrice est toujours meilleure est faux.
Si un graphe a 1000 sommets et très peu d'arêtes, la matrice contient beaucoup de zéros.
Une liste d'adjacence peut être plus économique en mémoire.
Dire qu'une liste d'adjacence est toujours meilleure est faux aussi.
Si on demande sans cesse "A est-il relié à B ?", la matrice peut être plus directe.

### Exercice intégré 3

Construire la liste d'adjacence d'un graphe à quatre sommets.
Construire la matrice correspondante.
Identifier une question où la matrice est pratique.
Identifier une question où la liste d'adjacence est pratique.

## Coût comparé

Le coût en temps mesure le nombre d'opérations significatives.
Le coût en mémoire mesure l'espace utilisé.
Une pile par liste Python donne un ajout en fin pratique.
Une file par liste avec retrait au début peut être coûteuse.
Une file par `deque` est plus adaptée.
Une matrice d'adjacence pour `n` sommets utilise `n*n` cases.
Une liste d'adjacence utilise de l'espace lié au nombre de sommets et de liens.
Pour un graphe dense, la matrice peut être acceptable.
Pour un graphe creux, la liste d'adjacence est souvent plus sobre.
Le coût doit être relié au besoin.

## BFS et DFS comme activité d'application

Un parcours de graphe utilise une structure auxiliaire.
BFS signifie parcours en largeur.
BFS utilise naturellement une file.
DFS signifie parcours en profondeur.
DFS utilise naturellement une pile ou la récursivité.
Dans cette séquence, BFS et DFS servent à illustrer le choix de structure.
L'objectif principal reste interface, implémentation et représentation.
La maîtrise approfondie des algorithmes de graphes pourra être reprise ensuite.

### Exemple corrigé 6

Pour chercher un plus court nombre d'arêtes dans un graphe non pondéré, BFS est pertinent.
Il explore d'abord les voisins proches.
Il utilise une file.
Le choix de file correspond à l'ordre de traitement.
Ce lien montre que l'algorithme dépend de la structure auxiliaire.

### Erreur fréquente 2

Apprendre BFS comme une recette sans comprendre la file.
Si on remplace la file par une pile, le comportement change.
Le parcours obtenu n'est plus le même.

## Aperçu non évalué : ABR

Un arbre binaire de recherche est une structure ordonnée.
Il permet des recherches efficaces quand l'arbre reste équilibré.
Cette notion n'est pas évaluée dans cette séquence.
Elle sera traitée dans une séquence dédiée.
Ici, l'ABR sert seulement à montrer que le choix d'une structure dépend aussi d'un invariant.

## Tests, bugs et cas limites

Une pile vide ne peut pas dépiler.
Une file vide ne peut pas défiler.
Une matrice doit être carrée.
Une liste d'adjacence ne doit pas mentionner de sommet absent sans décision explicite.
Un graphe orienté ne se traite pas comme un graphe non orienté.
Un test doit vérifier le comportement normal.
Un test doit vérifier le comportement limite.
Un test doit vérifier une erreur attendue.
Les bugs typiques viennent souvent d'un mauvais invariant.
Un invariant de pile : les éléments sortent dans l'ordre inverse d'entrée.
Un invariant de file : les éléments sortent dans l'ordre d'entrée.
Un invariant de matrice : toutes les lignes ont la même longueur.

### Exemple corrigé 7

Test de pile :
On ajoute `1`, puis `2`.
On retire une fois.
Le résultat attendu est `2`.
On retire encore.
Le résultat attendu est `1`.
Ce test vérifie LIFO.

### Exemple corrigé 8

Test de file :
On ajoute `A`, puis `B`.
On retire une fois.
Le résultat attendu est `A`.
On retire encore.
Le résultat attendu est `B`.
Ce test vérifie FIFO.

## Aides progressives

Aide niveau 1 : nommer l'opération principale.
Aide niveau 2 : écrire l'interface avant le code.
Aide niveau 3 : choisir l'implémentation seulement après l'interface.
Aide niveau 1 : pour un graphe, lister les sommets.
Aide niveau 2 : lister les liens.
Aide niveau 3 : choisir liste d'adjacence ou matrice selon la question.

## Différenciation

Parcours socle : distinguer LIFO, FIFO et accès par clé.
Parcours socle : lire une liste d'adjacence.
Parcours standard : écrire une pile et une file testées.
Parcours standard : convertir liste d'adjacence en matrice.
Parcours expert : comparer coût mémoire et coût de requête.
Parcours expert : expliquer pourquoi BFS utilise une file.

## Erreurs fréquentes

Erreur fréquente 1 : confondre interface et implémentation.
Erreur fréquente 2 : utiliser une liste brute sans contrat.
Erreur fréquente 3 : inverser LIFO et FIFO.
Erreur fréquente 4 : oublier les sommets isolés d'un graphe.
Erreur fréquente 5 : confondre matrice d'adjacence et tableau de distances.
Erreur fréquente 6 : tester seulement un graphe à deux sommets.

## À retenir

Une interface décrit ce que l'on peut faire.
Une implémentation décrit comment c'est fait.
Une pile suit LIFO.
Une file suit FIFO.
Un dictionnaire sert l'accès par clé.
Un graphe représente des relations.
Une liste d'adjacence favorise souvent les graphes peu denses.
Une matrice d'adjacence donne un test direct de relation.
Le choix de structure dépend des opérations attendues.
Les tests doivent vérifier les invariants.

## Auto-évaluation

- Je sais définir interface et implémentation.
- Je sais donner l'interface d'une pile.
- Je sais donner l'interface d'une file.
- Je sais expliquer LIFO et FIFO.
- Je sais choisir un dictionnaire quand l'accès par clé domine.
- Je sais représenter un graphe par liste d'adjacence.
- Je sais représenter un graphe par matrice d'adjacence.
- Je sais citer un coût mémoire comparé.
- Je sais expliquer pourquoi BFS utilise une file.
- Je sais proposer un test d'invariant.

## Extension

Approfondissement 1 : implémenter une file avec deux piles.
Approfondissement 2 : mesurer la taille d'une matrice pour 100 sommets.
Approfondissement 3 : écrire une fonction qui détecte les sommets isolés.
Approfondissement 4 : comparer BFS et DFS sur le même graphe.
Approfondissement 5 : préparer une question pour la future séquence sur ABR.

## Exemples corrigés

Cette section récapitule les exemples corrigés de la séquence.

Exemple corrigé récapitulatif 1 : une pile modélise l'annulation de la dernière action.

Exemple corrigé récapitulatif 2 : une file modélise une imprimante qui traite dans l'ordre d'arrivée.

Exemple corrigé récapitulatif 3 : un dictionnaire associe un identifiant stable à une valeur.

Exemple corrigé récapitulatif 4 : une liste d'adjacence donne directement les voisins d'un sommet.

Exemple corrigé récapitulatif 5 : une matrice d'adjacence permet de tester directement une arête par deux indices.

## Exercices intégrés

Cette section rassemble les exercices intégrés à refaire après le cours.

Exercice intégré récapitulatif 1 : expliquer la différence entre interface et implémentation sur l'exemple d'une file.

Exercice intégré récapitulatif 2 : choisir une structure pour un historique d'annulation.

Exercice intégré récapitulatif 3 : représenter le graphe `A-B`, `A-C`, `C-D` par liste d'adjacence et matrice.
