---
title: "Aides progressives - structures abstraites et implémentations"
niveau: terminale
source: "BO spécial n°8 du 25 juillet 2019 - NSI Terminale"
status: needs_review
version: "0.2.0"
notion: "pile, file, dictionnaire, graphe"
objectifs:
  - "Débloquer les exercices sans donner immédiatement la réponse."
  - "Faire verbaliser l'interface avant le code."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
---

# Aides progressives - structures abstraites et implémentations

## Situation-problème

Un élève sait coder avec des listes, mais ne sait pas choisir entre pile, file, dictionnaire et graphe.

L'aide doit guider le raisonnement sans remplacer la recherche.

## Aides progressives

Utiliser les niveaux dans l'ordre.

Ne donner le niveau suivant que si le blocage persiste.

Demander à l'élève de reformuler ce qu'il a compris avant de passer à l'aide suivante.

## Niveau 1

Repère les verbes de l'énoncé.

Ajouter, retirer, chercher, relier, parcourir ne désignent pas la même opération.

Écris les opérations attendues avec des mots simples.

Exemple : ajouter un ticket, retirer le plus ancien ticket, savoir si une clé existe.

Si l'ordre des retraits est important, écris trois entrées fictives.

Observe ensuite quel élément sort en premier.

## Niveau 2

Associe chaque opération à une interface.

Dernier élément retiré : pile.

Premier élément retiré : file.

Accès par clé : dictionnaire.

Relations entre objets : graphe.

Voisins d'un sommet : liste d'adjacence.

Test rapide d'une arête : matrice d'adjacence.

Si deux choix semblent possibles, note l'opération la plus fréquente.

## Niveau 3

Passe au code seulement après le choix d'interface.

Pour une pile, une liste Python avec `append` et `pop` est suffisante dans cette séquence.

Pour une file, `collections.deque` évite le coût de `pop(0)`.

Pour un dictionnaire, vérifie que la clé est stable et unique.

Pour un graphe, choisis entre liste d'adjacence et matrice selon la densité.

Ajoute un test sur structure vide.

Ajoute un test sur un élément absent.

Ajoute un test sur une relation inexistante.

## Erreurs fréquentes

Erreur fréquente 1 : coder avant d'avoir choisi l'interface.

Question de relance : quelles opérations ton programme doit-il garantir ?

Erreur fréquente 2 : employer une file quand l'annulation demande une pile.

Question de relance : après trois actions A, B, C, laquelle doit être annulée d'abord ?

Erreur fréquente 3 : oublier le cas de la structure vide.

Question de relance : que doit faire le programme si aucune donnée n'est présente ?

Erreur fréquente 4 : confondre sommet et arête.

Question de relance : dans ton exemple, quels sont les objets et quelles sont les relations ?

## Extension

Comparer deux implémentations d'une file : liste Python et `deque`.

Mesurer qualitativement la différence sur 10 éléments, puis sur 10 000 éléments.

Expliquer pourquoi l'interface reste la même alors que l'implémentation change.

## Auto-évaluation

Je sais demander une aide de niveau adapté.

Je sais identifier l'opération principale.

Je sais faire un test de structure vide.

Je sais expliquer mon choix sans réciter un nom de structure.

Je sais reprendre une erreur comme information sur mon modèle mental.
