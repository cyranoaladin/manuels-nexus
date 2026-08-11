---
titre: Evaluation corrigee professeur - S01 structures de donnees, interfaces et implementations
niveau: terminale
type: evaluation_corrigee
statut: needs_review
status: needs_review
sequence: S01 structures de donnees interfaces implementations
notion: interface, implementation, piles, files, dictionnaires, graphes
objectifs:
  - Corriger les distinctions interface implementation.
  - Corriger les piles, files, dictionnaires et representations de graphes.
version: 0.3.0
public: professeur
source: generated
private_data: false
official_program:
  level: terminale
  rubrique: Structures de donnees
  content: Interface, implementation, piles, files, dictionnaires, graphes
  capacities:
    - id: T-STRUCT-01A
      label: Distinguer interface et implementation
    - id: T-STRUCT-02A
      label: Utiliser une pile
    - id: T-STRUCT-02B
      label: Utiliser une file
    - id: T-STRUCT-05A
      label: Representer un graphe par liste d'adjacence
    - id: T-STRUCT-05B
      label: Representer un graphe par matrice d'adjacence
---

# Evaluation corrigee professeur - S01 structures de donnees, interfaces et implementations

Statut : document professeur non publiable, a relire pedagogiquement et scientifiquement.

## Conditions d'utilisation professeur

- Status : needs_review.
- Durée standard : 1 h.
- Matériel : ordinateur avec Python local ou sujet papier selon modalite.
- Correction complète : toutes les questions de l'evaluation sont corrigees ci-dessous avec justification, bareme, variante acceptable, erreur frequente et remediation.
- Erreur fréquente : les erreurs signalees servent a preparer la remediation, pas a valider la publication.

## Barème global

- Question 1 : 2 points.
- Question 2 : 2 points.
- Question 3 : 2 points.
- Question 4 : 2 points.
- Question 5 : 2 points.
- Question 6 : 3 points.
- Question 7 : 3 points.
- Question 8 : 4 points.
- Total : 20 points.

## Question 1 - Interface et implementation

- Capacité officielle : T-STRUCT-01A.
- Reponse attendue : l'interface decrit les operations disponibles et leur contrat ; l'implementation decrit comment ces operations sont realisees en memoire et en code.
- Justification : deux implementations differentes peuvent respecter la meme interface si elles produisent les memes effets observables.
- Barème : 1 point pour la definition d'interface ; 0,5 point pour l'implementation ; 0,5 point pour l'exemple.
- Variante acceptable : citer une pile implementee par liste Python ou par liste chainee.
- Erreurs fréquentes : confondre classe Python et interface abstraite ; juger une structure seulement par son nom.
- Remédiation : faire comparer deux codes de pile ayant les memes methodes `push`, `pop`, `is_empty`.
- Critere de reussite : l'eleve separe contrat utilisateur et choix technique interne.

## Question 2 - Pile

- Capacité officielle : T-STRUCT-02A.
- Reponse attendue : une pile suit le principe LIFO ; apres `push(3)`, `push(7)`, `pop()`, la valeur retiree est `7` et la pile contient encore `3`.
- Justification : le dernier element ajoute est le premier retire.
- Barème : 1 point pour LIFO ; 0,5 point pour la valeur retiree ; 0,5 point pour l'etat final.
- Variante acceptable : representer la pile verticalement si le sommet est clairement indique.
- Erreurs fréquentes : appliquer FIFO ; oublier de retirer l'element apres `pop`; ne pas traiter la pile vide.
- Remédiation : faire simuler quatre operations avec une colonne `sommet`.
- Critere de reussite : chaque operation modifie correctement l'etat de la pile.

## Question 3 - File

- Capacité officielle : T-STRUCT-02B.
- Reponse attendue : une file suit FIFO ; apres `enqueue("A")`, `enqueue("B")`, `dequeue()`, la valeur retiree est `A` et `B` reste en tete.
- Justification : le premier element entre est le premier servi.
- Barème : 1 point pour FIFO ; 0,5 point pour la valeur retiree ; 0,5 point pour l'etat final.
- Variante acceptable : utiliser les termes `enfiler` et `defiler`.
- Erreurs fréquentes : retirer le dernier element ; confondre tete et queue ; oublier le cas file vide.
- Remédiation : simuler une file d'attente physique puis traduire en operations.
- Critere de reussite : le comportement attendu ne depend pas de l'implementation choisie.

## Question 4 - Dictionnaire et choix de structure

- Capacité officielle : T-STRUCT-03A.
- Reponse attendue : un dictionnaire convient lorsque l'on associe une cle unique a une valeur, par exemple `distance[sommet]`; il est moins adapte si l'on doit conserver plusieurs valeurs ordonnees sans cle.
- Justification : l'acces par cle exprime directement la relation recherchee.
- Barème : 1 point pour le cas pertinent ; 0,5 point pour le contre-exemple ; 0,5 point pour l'explication.
- Variante acceptable : citer un index d'enregistrements par identifiant.
- Erreurs fréquentes : utiliser une liste de couples sans justifier la recherche ; prendre une valeur modifiable comme cle ; confondre cle et position.
- Remédiation : faire choisir entre liste, pile, file et dictionnaire pour trois besoins.
- Critere de reussite : le choix est relie a une operation dominante.

## Question 5 - Graphe en liste d'adjacence

- Capacité officielle : T-STRUCT-05A.
- Reponse attendue : pour les aretes `A-B`, `A-C`, `B-C`, une liste d'adjacence non orientee possible est `{"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}`.
- Justification : dans un graphe non oriente, chaque arete apparait dans les deux listes de voisins.
- Barème : 1 point pour les trois sommets ; 0,5 point pour la symetrie ; 0,5 point pour l'absence de voisin invente.
- Variante acceptable : utiliser des ensembles au lieu de listes si l'ordre n'est pas exige.
- Erreurs fréquentes : oublier la symetrie ; oublier un sommet isole ; confondre voisin et chemin.
- Remédiation : faire construire d'abord le tableau des aretes, puis remplir chaque liste de voisins.
- Critere de reussite : tous les sommets et seulement les aretes donnees sont representes.

## Question 6 - Matrice d'adjacence

- Capacité officielle : T-STRUCT-05B.
- Reponse attendue : avec l'ordre `A, B, C`, la matrice du graphe precedent est `[[0,1,1],[1,0,1],[1,1,0]]` si aucune boucle n'est presente.
- Justification : la case `(i, j)` vaut `1` si une arete relie les sommets d'indices `i` et `j`, sinon `0`.
- Barème : 1 point pour la taille 3x3 ; 1 point pour les valeurs correctes ; 1 point pour la justification de la diagonale.
- Variante acceptable : matrice equivalente avec un autre ordre de sommets si l'ordre est annonce.
- Erreurs fréquentes : matrice non carree ; valeur autre que 0/1 sans ponderation annoncee ; diagonale mal interpretee.
- Remédiation : verifier d'abord l'ordre des sommets puis completer ligne par ligne.
- Critere de reussite : chaque ligne correspond au voisinage du sommet annonce.

## Question 7 - Cout compare

- Capacité officielle : T-STRUCT-05C.
- Reponse attendue : une matrice facilite le test d'adjacence en temps constant pour deux indices, mais coute plus de memoire pour un graphe peu dense ; une liste d'adjacence est plus compacte pour un graphe peu dense et facilite le parcours des voisins.
- Justification : le choix depend des operations dominantes et de la densite du graphe.
- Barème : 1 point pour matrice ; 1 point pour liste ; 1 point pour critere de choix.
- Variante acceptable : formuler en ordre de grandeur sans notation asymptotique si le raisonnement est correct.
- Erreurs fréquentes : affirmer qu'une representation est toujours meilleure ; oublier le cout de stockage ; confondre voisins et sommets.
- Remédiation : comparer deux graphes de 5 sommets, l'un dense et l'autre avec 4 aretes.
- Critere de reussite : l'argument cite une operation et un contexte.

## Question 8 - Application courte : parcours guide

- Capacité officielle : T-STRUCT-05A, T-ALGO-02A.
- Reponse attendue : sur une liste d'adjacence donnee, un parcours en largeur utilise une file ; l'ordre exact peut varier selon l'ordre des voisins, mais chaque sommet atteignable est visite une seule fois si l'ensemble `vus` est tenu a jour.
- Justification : la file impose de traiter d'abord les sommets decouverts le plus tot.
- Barème : 1 point pour la structure file ; 1 point pour `vus`; 1 point pour l'ordre de visite coherent ; 1 point pour le cas absence de chemin.
- Variante acceptable : proposer un parcours en profondeur si la question accepte explicitement DFS, mais il faut alors utiliser une pile ou la recursion.
- Erreurs fréquentes : revisiter les sommets en cycle ; confondre BFS et DFS ; oublier un sommet absent ou isole.
- Remédiation : tracer la file et l'ensemble `vus` sur trois etapes, sans coder d'abord.
- Critere de reussite : le parcours reste une application, non une validation complete de T-ALGO-02.
