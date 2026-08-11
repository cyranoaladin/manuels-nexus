---
title: "Fiche méthode - choisir une structure de données"
niveau: terminale
source: "BO spécial n°8 du 25 juillet 2019 - NSI Terminale"
status: needs_review
version: "0.2.0"
notion: "structures abstraites, interfaces, implémentations"
objectifs:
  - "Identifier l'interface utile avant l'implémentation."
  - "Comparer pile, file, dictionnaire, liste d'adjacence et matrice."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
---

# Fiche méthode - choisir une structure de données

## Situation-problème

Une application doit gérer des demandes arrivant dans un réseau.

Certaines demandes doivent être traitées dans l'ordre d'arrivée.

D'autres doivent être annulées en revenant à la dernière action.

D'autres encore doivent permettre une recherche rapide par identifiant.

La question n'est pas seulement : quel code Python écrire ?

La question prioritaire est : quelle structure abstraite répond au besoin ?

## Méthode

1. Nommer les données manipulées.

2. Lister les opérations nécessaires.

3. Repérer l'ordre attendu : dernier entré, premier entré, accès par clé, voisinage.

4. Choisir une interface.

5. Choisir ensuite une implémentation.

6. Justifier le coût attendu des opérations importantes.

7. Prévoir un test sur un cas limite.

8. Vérifier que le choix reste lisible pour une autre personne.

## Questions de décision

- Ai-je besoin de retirer le dernier élément ajouté ?

- Ai-je besoin de retirer le premier élément ajouté ?

- Ai-je besoin d'associer une clé à une valeur ?

- Ai-je besoin de connaître les voisins d'un sommet ?

- Ai-je besoin de tester rapidement l'existence d'une arête ?

- Ai-je besoin de parcourir souvent tous les voisins ?

- La taille de la structure est-elle connue à l'avance ?

- Les données changent-elles souvent ?

## Exemple

On veut modéliser une file d'attente de tickets de support.

Les tickets doivent être traités dans l'ordre d'arrivée.

L'opération principale est `defiler`.

La structure abstraite adaptée est une file.

Une implémentation possible en Python est `collections.deque`.

Une liste Python avec `pop(0)` fonctionne sur de petits cas, mais son coût augmente car les éléments doivent être décalés.

Le choix doit donc être justifié par l'usage prévu.

## Exemple comparatif

On veut représenter un graphe social de 1 000 personnes.

Chaque personne connaît peu d'autres personnes.

Une liste d'adjacence stocke seulement les relations existantes.

Une matrice d'adjacence stocke toutes les paires possibles.

La liste d'adjacence est plus adaptée pour parcourir les voisins.

La matrice est plus adaptée pour tester immédiatement si deux sommets sont reliés.

## Erreurs fréquentes

Erreur fréquente 1 : choisir une liste parce que c'est le type Python le plus connu.

Correction : partir des opérations, pas de l'habitude.

Erreur fréquente 2 : confondre pile et file.

Correction : écrire un exemple avec trois ajouts puis deux retraits.

Erreur fréquente 3 : croire qu'un dictionnaire est toujours plus adapté.

Correction : un dictionnaire est pertinent pour l'accès par clé, pas pour conserver un ordre de traitement.

Erreur fréquente 4 : représenter tout graphe par une matrice.

Correction : comparer le nombre de sommets au nombre d'arêtes.

Erreur fréquente 5 : discuter d'un algorithme de parcours sans préciser la représentation du graphe.

Correction : l'algorithme dépend de l'accès aux voisins.

## Mini-application

Pour chaque situation, choisir une structure et justifier.

- Historique d'annulation dans un éditeur.

- Impression de documents dans une salle de classe.

- Carnet d'adresses indexé par nom.

- Carte de lignes de bus.

- Test rapide de liaison directe entre deux routeurs.

## Auto-évaluation

Je sais séparer interface et implémentation.

Je sais reconnaître une pile à partir d'un scénario.

Je sais reconnaître une file à partir d'un scénario.

Je sais expliquer l'intérêt d'un dictionnaire.

Je sais comparer liste d'adjacence et matrice d'adjacence.

Je sais citer un cas limite à tester.

## Lien avec la séquence

Cette méthode est mobilisée dans le TD pour justifier les choix.

Elle est mobilisée dans le TP pour choisir la représentation d'un petit réseau.

Elle est mobilisée dans l'évaluation pour analyser un code court.
