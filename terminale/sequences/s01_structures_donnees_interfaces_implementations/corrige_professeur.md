---
title: "Corrigé professeur - structures de données"
niveau: terminale
source: "Prototype interne"
status: needs_review
version: "0.5.0"
notion: "corrigé professeur"
objectifs: "Document professeur exploitable en prototype, à relire avant usage."
sequence: s01_structures_donnees_interfaces_implementations
private_data: false
---

# Corrigé professeur - structures de données

**Document professeur uniquement. Statut : `needs_review`.**

## Question 1 - Interface

- Capacité officielle associée : T-STRUCT-01A.
- Réponse attendue : créer, enfiler, défiler, est_vide, éventuellement premier..
- Justification : L’interface liste les opérations visibles..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : noms anglais acceptés..
- Erreurs fréquentes : décrire la liste interne.
- Remédiation associée : cacher l’implémentation et ne garder que les opérations.
- Critère de réussite : FIFO est mentionné.

## Question 2 - Implémentation

- Capacité officielle associée : T-STRUCT-01B.
- Réponse attendue : L’interface décrit quoi faire ; l’implémentation décrit comment c’est stocké..
- Justification : Deux implémentations peuvent partager la même interface..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : exemple pile accepté..
- Erreurs fréquentes : assimiler interface à classe Python.
- Remédiation associée : comparer deux codes avec mêmes méthodes.
- Critère de réussite : les deux niveaux sont séparés.

## Question 3 - Classe

- Capacité officielle associée : T-STRUCT-02A.
- Réponse attendue : `__init__` initialise un attribut, puis méthodes empiler/depiler..
- Justification : La classe regroupe état et opérations..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : deque accepté..
- Erreurs fréquentes : utiliser une variable globale.
- Remédiation associée : créer deux piles et tracer les états.
- Critère de réussite : deux objets indépendants fonctionnent.

## Question 4 - Choix structure

- Capacité officielle associée : T-STRUCT-03B.
- Réponse attendue : Un dictionnaire convient..
- Justification : La recherche se fait par clé..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : index auxiliaire accepté..
- Erreurs fréquentes : choisir une file par ordre d’arrivée.
- Remédiation associée : lister les opérations dominantes.
- Critère de réussite : le choix répond au besoin.

## Question 5 - Dictionnaire

- Capacité officielle associée : T-STRUCT-03C.
- Réponse attendue : Liste : parcours ; dictionnaire : accès par clé..
- Justification : Les opérations caractéristiques diffèrent..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : réponse avec complexité intuitive acceptée..
- Erreurs fréquentes : chercher une valeur comme une clé.
- Remédiation associée : faire écrire clé -> valeur.
- Critère de réussite : clé et valeur sont distinguées.

## Question 6 - Graphe

- Capacité officielle associée : T-STRUCT-05A.
- Réponse attendue : Villes = sommets, routes = arêtes..
- Justification : Le graphe représente des relations..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : orientation acceptée si justifiée..
- Erreurs fréquentes : confondre sommet et arête.
- Remédiation associée : dessiner puis convertir.
- Critère de réussite : les voisins sont retrouvables.

## Question 7 - Matrice

- Capacité officielle associée : T-STRUCT-05B.
- Réponse attendue : Case i,j indique présence d’une arête..
- Justification : La matrice encode toutes les paires de sommets..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : 0/1 ou booléens acceptés..
- Erreurs fréquentes : matrice non carrée.
- Remédiation associée : repartir de la liste des sommets.
- Critère de réussite : dimension n x n citée.

## Question 8 - BFS

- Capacité officielle associée : T-ALGO-02A.
- Réponse attendue : La file traite les sommets découverts en FIFO..
- Justification : Cela visite par couches de distance..
- Barème question par question : 2.5 points, dont 0,5 compréhension, 1 méthode, 0,5 résultat, 0,5 justification.
- Variante acceptable : trace dessinée acceptée..
- Erreurs fréquentes : utiliser une pile et décrire DFS.
- Remédiation associée : comparer pile et file sur le même graphe.
- Critère de réussite : ordre de visite justifié.

