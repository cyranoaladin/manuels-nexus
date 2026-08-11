---
title: "Guide professeur - structures de données, interfaces et implémentations"
niveau: terminale
source: "BO spécial n°8 du 25 juillet 2019 - NSI Terminale"
status: needs_review
version: "0.2.0"
notion: "structures abstraites, pile, file, dictionnaire, graphe"
objectifs:
  - "Installer le vocabulaire interface, implémentation, coût."
  - "Éviter une entrée prématurée par BFS ou DFS."
  - "Préparer les séquences ultérieures sur arbres, graphes et algorithmes."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
---

# Guide professeur - structures de données, interfaces et implémentations

## Objectifs

Faire distinguer une structure abstraite de son implémentation.

Faire manipuler pile, file, dictionnaire et graphe avec des exemples courts.

Faire comparer liste d'adjacence et matrice d'adjacence.

Faire justifier un choix de structure selon un problème.

Limiter BFS à un exemple d'utilisation de file.

Signaler l'ABR comme aperçu hors évaluation dans cette séquence.

## Durée

Durée indicative : 4 semaines.

Séance 1 : situation-problème et vocabulaire.

Séance 2 : pile, file et dictionnaire.

Séance 3 : graphe comme structure relationnelle.

Séance 4 : représentations de graphe et coût comparé.

Séance 5 : TD progressif.

Séance 6 : TP réseau local.

Séance 7 : correction, remédiation, synthèse.

Séance 8 : évaluation.

## Scénario séance par séance

Séance 1 : partir de trois problèmes concrets.

Demander aux élèves de nommer les opérations sans citer Python.

Introduire interface et implémentation.

Institutionnaliser l'idée : une même interface peut avoir plusieurs implémentations.

Séance 2 : manipuler pile et file avec cartes papier.

Faire écrire les opérations `empiler`, `depiler`, `enfiler`, `defiler`.

Comparer une liste Python et `deque` pour la file.

Introduire le dictionnaire comme association clé-valeur.

Séance 3 : représenter des relations entre lieux par un graphe.

Distinguer sommet, arête, voisin.

Construire une liste d'adjacence à partir d'un tableau d'arêtes.

Séance 4 : construire une matrice d'adjacence du même graphe.

Comparer la place mémoire de façon qualitative.

Comparer le coût du test d'arête.

Séance 5 : TD en trois niveaux.

Faire expliciter les justifications avant la correction.

Séance 6 : TP en binômes.

Un élève tient le rôle de concepteur d'interface.

Un élève tient le rôle d'implémenteur.

Les rôles changent à mi-parcours.

Séance 7 : mise en commun.

Reprendre les erreurs de structure vide, clé absente et voisin absent.

Séance 8 : évaluation individuelle.

## Difficultés prévisibles

Les élèves peuvent réduire une structure de données à un type Python.

Ils peuvent confondre l'ordre d'entrée et l'ordre de sortie.

Ils peuvent mélanger graphe et dessin de graphe.

Ils peuvent croire qu'une matrice est plus scientifique qu'une liste.

Ils peuvent appliquer BFS sans comprendre pourquoi une file intervient.

Ils peuvent traiter l'ABR comme un objectif central alors qu'il relève d'une séquence ultérieure.

## Remédiation

Utiliser trois jetons A, B, C pour faire sortir les éléments physiquement.

Faire verbaliser : je retire le dernier ou je retire le premier.

Donner un graphe de quatre sommets avant un graphe plus grand.

Demander une justification en une phrase avant le code.

Comparer deux programmes qui donnent le même résultat mais n'ont pas les mêmes coûts.

Faire écrire un test sur structure vide.

Faire écrire un test sur clé absente.

## Différenciation

Pour les élèves fragiles, fournir un tableau opérations vers structures.

Pour les élèves fragiles, limiter le graphe à quatre sommets.

Pour les élèves fragiles, donner le squelette de tests.

Pour les élèves à l'aise, demander une comparaison qualitative de complexité.

Pour les élèves à l'aise, demander une deuxième implémentation de file.

Pour les élèves à l'aise, proposer une courte extension BFS.

## Questions orales

Quelle opération définit le besoin principal ?

Qu'est-ce qui change entre interface et implémentation ?

Pourquoi `pop(0)` n'est-il pas le meilleur réflexe pour une file ?

Dans quel cas une matrice d'adjacence est-elle intéressante ?

Que se passe-t-il si la pile est vide ?

Pourquoi un dictionnaire impose-t-il de réfléchir aux clés ?

## Critères d'évaluation

Le vocabulaire est correctement utilisé.

Le choix de structure est justifié par les opérations.

Le code traite les cas limites demandés.

La représentation de graphe est cohérente avec le problème.

Les tests montrent le comportement attendu.

La comparaison des coûts reste qualitative mais exacte.

## Prolongements

Séquence ultérieure sur arbres binaires et arbres binaires de recherche.

Séquence ultérieure sur parcours de graphes.

Séquence ultérieure sur modularité et tests.

Lien possible avec les bases de données : dictionnaire, clé, index.

Lien possible avec les systèmes : file de processus et ordonnanceur.
