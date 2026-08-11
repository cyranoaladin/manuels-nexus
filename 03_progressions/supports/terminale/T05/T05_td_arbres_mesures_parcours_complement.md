---
title: "T05 - TD - Mesures et parcours d'arbres complément"
level: "terminale"
sequence_id: "T05"
document_type: "td"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Arbres et algorithmes"
notion: "arbre binaire, taille, hauteur, feuilles, parcours en largeur, file"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-04B"
    - "T-ALGO-01A"
    - "T-ALGO-01B"
    - "T-ALGO-01D"
---

# T05 - TD - Mesures et parcours d'arbres complément

## Capacités officielles atomiques

- T-STRUCT-04B : Évaluer quelques mesures des arbres binaires (taille, hauteur, feuilles). « Taille, hauteur et feuilles. »
- T-ALGO-01A : Calculer la taille d’un arbre. « Structure récursive adaptée. »
- T-ALGO-01B : Calculer la hauteur d’un arbre. « Cas arbre vide : hauteur conventionnelle -1 (ou 0 selon la convention). »
- T-ALGO-01D : Parcourir un arbre en largeur d'abord. « Lien avec file. »

## Arbre de référence (rappel)

```
        8
       / \
      3   10
     / \    \
    1   6    14
       / \   /
      4   7 13
```

Taille = 9, hauteur = 3, feuilles = {1, 4, 7, 13}, BFS = [8, 3, 10, 1, 6, 14, 4, 7, 13].

---

## Exercice 1 — Mesures sur papier (T-STRUCT-04B)

Soit l'arbre binaire A1 suivant :

```
        20
       /  \
      15    25
     / \   /
    12  18 22
   /      \
  9       23
```

**1.a)** Déterminer la taille de A1.

**1.b)** Déterminer la hauteur de A1. Préciser le plus long chemin.

**1.c)** Lister toutes les feuilles de A1.

**1.d)** Cas limite : donner la taille, la hauteur et les feuilles d’un arbre vide. Donner la taille, la hauteur et les feuilles d’un arbre réduit à une seule feuille de valeur 42.

---

## Exercice 2 — Calcul récursif de la taille (T-ALGO-01A)

Soit l'arbre binaire A2 suivant :

```
      5
     / \
    2   7
   /   / \
  1   6   9
         /
        8
```

**2.a)** Écrire la formule récursive de la taille. Préciser le cas de base.

**2.b)** Dérouler l’exécution de `taille(5)` sur A2. Montrer l'arbre des appels récursifs et le résultat de chaque appel.

**2.c)** Quel est le variant utilisé pour prouver la terminaison de l'algorithme ? Justifier que ce variant décroît strictement et atteint le cas de base.

**2.d)** On considère un arbre A3 réduit au seul noeud 42. Vérifier que `taille(42)` renvoie 1 en déroulant l'algorithme.

---

## Exercice 3 — Calcul récursif de la hauteur (T-ALGO-01B)

Soit l'arbre binaire A4 suivant :

```
        30
       /
      20
     /  \
    10   25
   /
  5
```

**3.a)** Quelle convention adopte-t-on pour la hauteur d’un arbre vide ? Justifier ce choix.

**3.b)** Écrire la formule récursive de la hauteur. Préciser le cas de base.

**3.c)** Dérouler l’exécution de `hauteur(30)` sur A4. Détailler chaque appel récursif.

**3.d)** Vérifier le résultat en identifiant le plus long chemin dans A4 et en comptant les arêtes.

**3.e)** Donner un arbre de hauteur 0 et un arbre de hauteur 1. Vérifier avec la formule récursive.

---

## Exercice 4 — Parcours en largeur d'abord (T-ALGO-01D)

Soit l'arbre binaire A5 suivant :

```
         1
        / \
       2   3
      / \   \
     4   5   6
    /       / \
   7       8   9
```

**4.a)** Expliquer pourquoi le parcours BFS nécessite une file et non une pile.

**4.b)** Dérouler le parcours BFS de A5. Compléter le tableau :

| Étape | File (avant défilement) | Noeud traité | Résultat partiel |
|-------|------------------------|--------------|-----------------|
| 1 | | | |
| 2 | | | |
| ... | | | |

**4.c)** Donner le résultat final du parcours BFS de A5.

**4.d)** On suppose que l'on remplace la file par une pile (LIFO : on dépile au lieu de défiler). Dérouler le parcours obtenu sur A5. Est-ce un parcours en largeur ? Quel type de parcours obtient-on ?

**4.e)** Quel est le résultat du parcours BFS d’un arbre vide ? D'un arbre à un seul noeud ?


## Objectifs


## Prérequis


## Situation-problème

Un biologiste modélise un arbre phylogénétique et doit calculer le nombre d'espèces (taille), la profondeur maximale (hauteur) et lister les espèces terminales (feuilles). Comment parcourir l'arbre ?

## Activité d’entrée

Dessiner un arbre binaire de 7 noeuds, compter ses feuilles et mesurer sa hauteur à la main avant de programmer.

## Exemple

Construction collective d'un arbre binaire de 5 noeuds et calcul de sa taille, hauteur et parcours en largeur.

## Exercices

Exercices de calcul de mesures et de parcours sur des arbres binaires variés.

## Corrigé

Les corrigés détaillés sont dans T05_corrige_arbres_mesures_parcours_complement.md.

## Erreurs fréquentes

- EF1 : oublier le cas de l'arbre vide dans la fonction récursive (retourner 0 ou -1).
- EF2 : confondre hauteur et profondeur d'un noeud dans l'arbre.
- EF3 : utiliser une liste au lieu d'une file (deque) pour le parcours en largeur.


## Remédiation

Exercice de remédiation : tracer l'exécution de taille() sur un arbre de 3 noeuds en notant chaque appel récursif.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.

## Critères de réussite

- Critère de réussite : taille() et hauteur() retournent les valeurs correctes sur l'arbre exemple.
- Critère de validation : le parcours en largeur utilise une file et produit l'ordre attendu.
- Observable : la preuve de terminaison identifie le variant de boucle.


## Séance(s) correspondante(s)

Séance dédiée.

### Exercice 1 — Mesures d'un arbre sur papier

**Donnée** : Soit l'arbre binaire B1 suivant :
```
        50
       /  \
      30    70
     / \      \
    20  40     80
       /      /
      35    75
```
**Consigne** : (a) Déterminer la taille de B1. (b) Déterminer la hauteur de B1 en précisant le plus long chemin depuis la racine. (c) Lister toutes les feuilles de B1. (d) Indiquer le nombre de noeuds internes (noeuds qui ne sont pas des feuilles). Vérifier que taille = feuilles + noeuds internes.
**Livrable** : La taille, la hauteur avec le chemin le plus long, la liste des feuilles et le nombre de noeuds internes.
**Corrigé** : Le corrigé détaillé se trouve dans le fichier corrigé complément, exercice 1.

### Exercice 2 — Taille récursive

**Donnée** : Soit l'arbre binaire B2 suivant :
```
      10
     /  \
    5    15
   /    /  \
  3    12   20
```
**Consigne** : (a) Rappeler la formule récursive de la taille : `taille(noeud) = 1 + taille(gauche) + taille(droite)` avec `taille(None) = 0`. (b) Dérouler l'exécution de `taille(10)` sur B2 en dessinant l'arbre des appels récursifs. Pour chaque appel, indiquer la valeur renvoyée. (c) Vérifier que le résultat final correspond au nombre de noeuds comptés visuellement. (d) Quel est le variant de l'algorithme ? Justifier la terminaison.
**Livrable** : L'arbre des appels récursifs avec les valeurs de retour et la justification de terminaison.
**Corrigé** : Voir la correction complète dans le corrigé complément (exercice 2).

### Exercice 3 — Hauteur récursive

**Donnée** : Soit l'arbre binaire B3, un arbre « peigne gauche » :
```
    100
   /
  80
 /
60
 \
  65
```
**Consigne** : (a) Rappeler la formule récursive de la hauteur : `hauteur(noeud) = 1 + max(hauteur(gauche), hauteur(droite))` avec `hauteur(None) = -1`. (b) Dérouler l'exécution de `hauteur(100)` sur B3 en détaillant chaque appel récursif et les comparaisons `max`. (c) Vérifier le résultat en comptant les arêtes du plus long chemin. (d) Comparer la hauteur de B3 avec celle d'un arbre complet de même nombre de noeuds. Quel type d'arbre a la hauteur minimale pour un nombre de noeuds donné ?
**Livrable** : Le déroulement complet des appels, le résultat vérifié et la comparaison.
**Corrigé** : Corrigé avec justification : fichier corrigé complément, exercice 3.

### Exercice 4 — Parcours BFS avec file

**Donnée** : Soit l'arbre binaire B4 suivant :
```
       A
      / \
     B   C
    / \   \
   D   E   F
  /
 G
```
**Consigne** : (a) Dérouler le parcours en largeur (BFS) de B4 en complétant un tableau avec les colonnes : étape, contenu de la file avant défilement, noeud traité, noeuds ajoutés, résultat partiel. (b) Donner le résultat final du parcours BFS. (c) Expliquer pourquoi la propriété FIFO de la file garantit un traitement niveau par niveau. (d) Écrire le pseudo-code du BFS utilisant `from collections import deque`.
**Livrable** : Le tableau de trace complet, le résultat BFS, l'explication et le pseudo-code.
**Corrigé** : Solution détaillée : exercice 4 du corrigé complément associé.

### Exercice 5 — Nombre de feuilles

**Donnée** : On reprend l'arbre B2 de l'exercice 2 :
```
      10
     /  \
    5    15
   /    /  \
  3    12   20
```
**Consigne** : (a) Écrire la formule récursive du nombre de feuilles : si le noeud est une feuille (pas d'enfants), renvoyer 1 ; sinon renvoyer `feuilles(gauche) + feuilles(droite)`. Quel est le cas de base pour un arbre vide ? (b) Dérouler l'exécution de `nb_feuilles(10)` sur B2. (c) Vérifier le résultat visuellement. (d) Écrire la fonction Python correspondante et la tester.
**Livrable** : La formule récursive, le déroulement, la vérification et le code Python.
**Corrigé** : Consulter le corrigé complément pour la solution de l'exercice 5.

### Exercice 6 — Cas arbre vide

**Donnée** : On considère les fonctions `taille(noeud)`, `hauteur(noeud)` et `bfs(noeud)` programmées dans les exercices précédents.
**Consigne** : (a) Appeler chaque fonction sur un arbre vide (`None`). Indiquer la valeur attendue : `taille(None) = 0`, `hauteur(None) = -1`, `bfs(None) = []`. (b) Vérifier que chaque fonction gère correctement ce cas de base sans erreur. (c) Appeler chaque fonction sur un arbre réduit à un seul noeud de valeur 42. Vérifier : `taille = 1`, `hauteur = 0`, `bfs = [42]`. (d) Expliquer pourquoi le cas de base de l'arbre vide est indispensable pour la terminaison de la récursion.
**Livrable** : Les résultats des appels, les vérifications et l'explication sur la terminaison.
**Corrigé** : La réponse attendue et sa justification sont dans le corrigé complément, exercice 6.

### Exercice 7 — BFS par niveau

**Donnée** : On reprend l'arbre B4 de l'exercice 4 :
```
       A
      / \
     B   C
    / \   \
   D   E   F
  /
 G
```
**Consigne** : (a) Modifier l'algorithme BFS classique pour produire une liste de listes, où chaque sous-liste contient les noeuds d'un même niveau. Le résultat attendu est `[["A"], ["B", "C"], ["D", "E", "F"], ["G"]]`. (b) Indication : utiliser une boucle imbriquée qui traite tous les noeuds du niveau courant avant de passer au niveau suivant (en mémorisant la taille de la file au début de chaque niveau). (c) Dérouler l'algorithme sur B4 en montrant l'état de la file et de la liste de résultats à chaque étape. (d) Quel est l'intérêt de ce parcours par niveau dans un arbre de décision ?
**Livrable** : Le pseudo-code ou code Python, le déroulement et l'explication de l'intérêt.
**Corrigé** : Exercice 7 : solution dans le corrigé complément (avec trace d'exécution).

### Exercice 8 — Comparaison pile vs file dans les parcours

**Donnée** : On reprend l'arbre B4. On dispose de deux variantes d'un même algorithme de parcours : l'une utilise une file (FIFO), l'autre utilise une pile (LIFO). Le reste du code est identique.
**Consigne** : (a) Dérouler le parcours avec une file (BFS) sur B4. Noter l'ordre de visite. (b) Dérouler le parcours avec une pile (en ajoutant d'abord le fils droit puis le fils gauche) sur B4. Noter l'ordre de visite. (c) Identifier le type de parcours obtenu avec la pile (préfixe / DFS). (d) Expliquer en quoi la structure de données (file vs pile) détermine l'ordre de parcours. (e) Dans quel cas pratique préfère-t-on le BFS au DFS, et inversement ? Donner un exemple pour chaque.
**Livrable** : Les deux traces de parcours, l'identification des types, l'explication et les exemples d'usage.
**Corrigé** : Pour la correction : voir exercice 8 dans le document corrigé complément.


### Question de synthèse — Choisir la mesure adaptée

**Donnée** : Un développeur modélise un arbre binaire représentant un organigramme d'entreprise. La racine est le PDG, chaque noeud interne est un manager et chaque feuille est un employé sans subordonnés.
**Consigne** : (a) Quelle mesure (taille, hauteur, nombre de feuilles) répond à la question « combien de personnes travaillent dans l'entreprise » ? (b) Quelle mesure répond à « combien de niveaux hiérarchiques séparent le PDG du plus bas employé » ? (c) Proposer une requête concrète de l'entreprise à laquelle le parcours en largeur (BFS) apporterait une réponse utile.
**Livrable** : Les trois réponses justifiées avec le nom de la mesure ou du parcours utilisé.
