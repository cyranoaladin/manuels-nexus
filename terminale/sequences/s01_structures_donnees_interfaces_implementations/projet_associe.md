---
title: "Projet associé - choisir les structures d'un mini-réseau"
niveau: terminale
source: "BO spécial n°8 du 25 juillet 2019 - NSI Terminale"
status: needs_review
version: "0.2.0"
notion: "graphe, file, dictionnaire"
objectifs:
  - "Concevoir un mini-outil de représentation de réseau."
  - "Justifier les structures choisies."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
---

# Projet associé - choisir les structures d'un mini-réseau

## Cahier des charges

Le projet consiste à représenter un petit réseau de salles ou de routeurs.

Le réseau contient entre 5 et 12 sommets.

Chaque sommet possède un identifiant unique.

Les liaisons sont non orientées.

Le programme doit stocker les voisins de chaque sommet.

Le programme doit afficher les voisins d'un sommet choisi.

Le programme doit tester si deux sommets sont reliés directement.

Le programme doit expliquer la structure choisie.

Le projet ne demande pas d'interface graphique.

## Jalons

Jalon 1 : décrire le problème et les opérations nécessaires.

Jalon 2 : choisir la représentation principale.

Jalon 3 : écrire les fonctions de construction.

Jalon 4 : écrire les fonctions de consultation.

Jalon 5 : ajouter les tests.

Jalon 6 : préparer une courte soutenance.

## Livrables

Un fichier Python documenté.

Un fichier de tests ou une section de tests exécutables.

Une courte note de conception.

Un schéma du réseau sous forme textuelle.

Une justification du choix liste d'adjacence ou matrice.

## Critères d'évaluation

Les opérations attendues sont identifiées.

La structure choisie est adaptée au problème.

Les fonctions sont courtes et lisibles.

Les cas limites sont testés.

La soutenance emploie le vocabulaire de la séquence.

La comparaison entre deux représentations est argumentée.

## Grille de soutenance

Présentation du problème : 4 points.

Choix de structure : 5 points.

Démonstration du code : 5 points.

Tests et cas limites : 3 points.

Qualité de l'explication orale : 3 points.

## Version minimale

Représenter le réseau par liste d'adjacence.

Afficher les voisins d'un sommet existant.

Tester le cas d'un sommet absent.

Fournir deux tests simples.

## Version standard

Ajouter une fonction `sont_relies(graphe, a, b)`.

Ajouter une fonction de conversion vers matrice d'adjacence.

Comparer les deux représentations sur un paragraphe.

Fournir au moins cinq tests.

## Version experte

Ajouter une recherche d'un chemin court avec une file.

Séparer clairement l'interface et l'implémentation.

Proposer une deuxième implémentation sans changer les tests utilisateurs.

Expliquer le coût qualitatif de chaque opération.

## Contraintes de rendu

Le code doit s'exécuter sans dépendance externe.

Les noms de fonctions doivent être explicites.

Les erreurs doivent être signalées par des valeurs ou exceptions documentées.

Aucune donnée personnelle ne doit apparaître dans les exemples.
