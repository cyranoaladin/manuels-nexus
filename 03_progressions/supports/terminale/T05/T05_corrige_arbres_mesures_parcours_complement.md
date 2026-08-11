---
title: "T05 - Corrigé - Mesures et parcours d'arbres complément"
level: "terminale"
sequence_id: "T05"
document_type: "corrige"
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

# T05 - Corrigé - Mesures et parcours d'arbres complément

## Capacités officielles atomiques

- T-STRUCT-04B : Évaluer quelques mesures des arbres binaires (taille, hauteur, feuilles). « Taille, hauteur et feuilles. »
- T-ALGO-01A : Calculer la taille d’un arbre. « Structure récursive adaptée. »
- T-ALGO-01B : Calculer la hauteur d’un arbre. « Cas arbre vide : hauteur conventionnelle -1 (ou 0 selon la convention). »
- T-ALGO-01D : Parcourir un arbre en largeur d'abord. « Lien avec file. »

---

## Corrigé de l'évaluation

### Arbre B (rappel)

```
        50
       /  \
      30    70
     / \      \
    20  40     80
   /   /  \
  10  35  45
```

---

### Question 1 — Mesures sur papier (T-STRUCT-04B)

Exercice fondamental sur le dénombrement des noeuds, la mesure de hauteur et l'identification des feuilles.

**1.a)** Taille et hauteur de B.

Taille : on dénombre tous les noeuds : 50, 30, 70, 20, 40, 80, 10, 35, 45. **Taille = 9.**

Hauteur : le plus long chemin est 50 → 30 → 40 → 35 (ou 50 → 30 → 40 → 45), soit 3 arêtes. **Hauteur = 3.**

**1.b)** Feuilles de B.

Les noeuds sans fils gauche ni fils droit sont : 10, 35, 45, 80. **Feuilles = {10, 35, 45, 80}.**

**1.c)** Arbre réduit au seul noeud 99.

- Taille = 1
- Hauteur = 0 (0 arête)
- Feuilles = {99}

---

### Question 2 — Calcul récursif de la taille (T-ALGO-01A)

Exercice de traçage de la récursion pour le calcul de la taille.

**2.a)** Trace de `taille(50)` :

```
taille(50)
  = 1 + taille(30) + taille(70)

  taille(30)
    = 1 + taille(20) + taille(40)

    taille(20)
      = 1 + taille(10) + taille(None)
      taille(10) = 1 + taille(None) + taille(None) = 1 + 0 + 0 = 1
      taille(20) = 1 + 1 + 0 = 2

    taille(40)
      = 1 + taille(35) + taille(45)
      taille(35) = 1 + 0 + 0 = 1
      taille(45) = 1 + 0 + 0 = 1
      taille(40) = 1 + 1 + 1 = 3

    taille(30) = 1 + 2 + 3 = 6

  taille(70)
    = 1 + taille(None) + taille(80)
    taille(80) = 1 + 0 + 0 = 1
    taille(70) = 1 + 0 + 1 = 2

taille(50) = 1 + 6 + 2 = 9
```

**Résultat : taille(50) = 9.**

**2.b)** Variant de terminaison.

Le variant est le **nombre de noeuds du sous-arbre** passé en argument. À chaque appel récursif, on passe un sous-arbre strict (gauche ou droit), qui contient strictement moins de noeuds. Ce variant est un entier naturel qui décroît strictement et atteint 0 (arbre vide) au cas de base. L'algorithme termine donc toujours.

---

### Question 3 — Calcul récursif de la hauteur (T-ALGO-01B)

Exercice de traçage de la récursion pour le calcul de la hauteur.

**3.a)** Trace de `hauteur(50)` :

```
hauteur(50)
  = 1 + max(hauteur(30), hauteur(70))

  hauteur(30)
    = 1 + max(hauteur(20), hauteur(40))

    hauteur(20)
      = 1 + max(hauteur(10), hauteur(None))
      hauteur(10) = 1 + max(-1, -1) = 0
      hauteur(20) = 1 + max(0, -1) = 1

    hauteur(40)
      = 1 + max(hauteur(35), hauteur(45))
      hauteur(35) = 1 + max(-1, -1) = 0
      hauteur(45) = 1 + max(-1, -1) = 0
      hauteur(40) = 1 + max(0, 0) = 1

    hauteur(30) = 1 + max(1, 1) = 2

  hauteur(70)
    = 1 + max(hauteur(None), hauteur(80))
    hauteur(80) = 1 + max(-1, -1) = 0
    hauteur(70) = 1 + max(-1, 0) = 1

hauteur(50) = 1 + max(2, 1) = 3
```

**Résultat : hauteur(50) = 3.**

**3.b)** Avec la convention hauteur(vide) = 0 :

La hauteur d’une feuille serait : 1 + max(0, 0) = 1. Or une feuille n'a aucune arête en dessous d'elle ; sa hauteur devrait logiquement valoir 0. La convention hauteur(vide) = -1 donne : 1 + max(-1, -1) = 0, ce qui est cohérent avec le comptage en arêtes. C'est pourquoi la convention -1 est préférable.

---

### Question 4 — Parcours en largeur (T-ALGO-01D)

Exercice de traçage du parcours BFS avec une file.

**4.a)** Trace du parcours BFS de B :

| Étape | File (avant défilement) | Noeud traité | Résultat partiel |
|-------|------------------------|--------------|-----------------|
| 1 | [50] | 50 | [50] |
| 2 | [30, 70] | 30 | [50, 30] |
| 3 | [70, 20, 40] | 70 | [50, 30, 70] |
| 4 | [20, 40, 80] | 20 | [50, 30, 70, 20] |
| 5 | [40, 80, 10] | 40 | [50, 30, 70, 20, 40] |
| 6 | [80, 10, 35, 45] | 80 | [50, 30, 70, 20, 40, 80] |
| 7 | [10, 35, 45] | 10 | [50, 30, 70, 20, 40, 80, 10] |
| 8 | [35, 45] | 35 | [50, 30, 70, 20, 40, 80, 10, 35] |
| 9 | [45] | 45 | [50, 30, 70, 20, 40, 80, 10, 35, 45] |

**Résultat BFS = [50, 30, 70, 20, 40, 80, 10, 35, 45].**

**4.b)** Le BFS utilise une **file** (FIFO). La file garantit que les noeuds du niveau k sont tous traités avant ceux du niveau k+1 : les noeuds enfilés en premier (ceux du niveau courant) sont défilés en premier. Une pile (LIFO) traiterait en priorité les noeuds les plus récemment ajoutés, ce qui donnerait un parcours en profondeur, pas en largeur.

**4.c)** Le parcours BFS d’un arbre vide renvoie une **liste vide** : `[]`.

---

## Corrigé du TD

### Exercice 1 — Mesures sur papier (T-STRUCT-04B)

Question préliminaire : rappeler les définitions de taille, hauteur et feuille d'un arbre binaire.

Arbre A1 :

```
        20
       /  \
      15    25
     / \   /
    12  18 22
   /      \
  9       23
```

**1.a)** Taille de A1 : noeuds = {20, 15, 25, 12, 18, 22, 9, 23}. **Taille = 8.**

**1.b)** Hauteur de A1 : plus long chemin = 20 → 15 → 12 → 9, soit 3 arêtes. **Hauteur = 3.**

**1.c)** Feuilles de A1 : noeuds sans fils = 9, 18, 23. **Feuilles = {9, 18, 23}.**

**1.d)** Cas limites :
- Arbre vide : taille = 0, hauteur = -1, feuilles = {}.
- Arbre {42} : taille = 1, hauteur = 0, feuilles = {42}.

---

### Exercice 2 — Calcul récursif de la taille (T-ALGO-01A)

Arbre A2 :

```
      5
     / \
    2   7
   /   / \
  1   6   9
         /
        8
```

**2.a)** Formule récursive :
- Cas de base : taille(None) = 0.
- Cas récursif : taille(n) = 1 + taille(n.gauche) + taille(n.droite).

**2.b)** Trace de `taille(5)` :

```
taille(5)
  = 1 + taille(2) + taille(7)

  taille(2) = 1 + taille(1) + taille(None)
    taille(1) = 1 + 0 + 0 = 1
  taille(2) = 1 + 1 + 0 = 2

  taille(7) = 1 + taille(6) + taille(9)
    taille(6) = 1 + 0 + 0 = 1
    taille(9) = 1 + taille(8) + taille(None)
      taille(8) = 1 + 0 + 0 = 1
    taille(9) = 1 + 1 + 0 = 2
  taille(7) = 1 + 1 + 2 = 4

taille(5) = 1 + 2 + 4 = 7
```

**Résultat : taille(5) = 7.**

**2.c)** Variant : nombre de noeuds du sous-arbre. Décroît strictement (chaque sous-arbre est strictement plus petit) et atteint 0 au cas de base (arbre vide).

**2.d)** taille(42) = 1 + taille(None) + taille(None) = 1 + 0 + 0 = **1**.

---

### Exercice 3 — Calcul récursif de la hauteur (T-ALGO-01B)

Arbre A4 :

```
        30
       /
      20
     /  \
    10   25
   /
  5
```

**3.a)** Convention : hauteur(vide) = -1. Cela permet que la hauteur d’une feuille vaille 0 (cohérent avec le comptage en arêtes).

**3.b)** Formule :
- Cas de base : hauteur(None) = -1.
- Cas récursif : hauteur(n) = 1 + max(hauteur(n.gauche), hauteur(n.droite)).

**3.c)** Trace de `hauteur(30)` :

```
hauteur(30)
  = 1 + max(hauteur(20), hauteur(None))
  = 1 + max(hauteur(20), -1)

  hauteur(20) = 1 + max(hauteur(10), hauteur(25))
    hauteur(10) = 1 + max(hauteur(5), hauteur(None))
      hauteur(5) = 1 + max(-1, -1) = 0
    hauteur(10) = 1 + max(0, -1) = 1
    hauteur(25) = 1 + max(-1, -1) = 0
  hauteur(20) = 1 + max(1, 0) = 2

hauteur(30) = 1 + max(2, -1) = 3
```

**Résultat : hauteur(30) = 3.**

**3.d)** Plus long chemin : 30 → 20 → 10 → 5, soit 3 arêtes. Cohérent avec hauteur = 3.

**3.e)**
- Arbre de hauteur 0 : un seul noeud (feuille). hauteur = 1 + max(-1, -1) = 0.
- Arbre de hauteur 1 : racine avec un fils. hauteur = 1 + max(0, -1) = 1.

---

### Exercice 4 — Parcours en largeur d'abord (T-ALGO-01D)

Question préliminaire : pourquoi une file est-elle nécessaire pour un parcours en largeur ?

Arbre A5 :

```
         1
        / \
       2   3
      / \   \
     4   5   6
    /       / \
   7       8   9
```

**4.a)** La file (FIFO) garantit que les noeuds sont traités dans l'ordre de leur découverte : les noeuds du niveau k sont tous enfilés avant ceux du niveau k+1, et donc défilés (traités) en premier. Une pile (LIFO) traiterait les noeuds les plus récents en premier, donnant un parcours en profondeur.

**4.b)** et **4.c)** Trace du parcours BFS de A5 :

| Étape | File (avant défilement) | Noeud traité | Résultat partiel |
|-------|------------------------|--------------|-----------------|
| 1 | [1] | 1 | [1] |
| 2 | [2, 3] | 2 | [1, 2] |
| 3 | [3, 4, 5] | 3 | [1, 2, 3] |
| 4 | [4, 5, 6] | 4 | [1, 2, 3, 4] |
| 5 | [5, 6, 7] | 5 | [1, 2, 3, 4, 5] |
| 6 | [6, 7] | 6 | [1, 2, 3, 4, 5, 6] |
| 7 | [7, 8, 9] | 7 | [1, 2, 3, 4, 5, 6, 7] |
| 8 | [8, 9] | 8 | [1, 2, 3, 4, 5, 6, 7, 8] |
| 9 | [9] | 9 | [1, 2, 3, 4, 5, 6, 7, 8, 9] |

**Résultat BFS = [1, 2, 3, 4, 5, 6, 7, 8, 9].**

**4.d)** Avec une pile (LIFO), en dépilant au lieu de défiler :

| Étape | Pile | Noeud traité | Résultat |
|-------|------|--------------|----------|
| 1 | [1] | 1 | [1] |
| 2 | [2, 3] | 3 (sommet) | [1, 3] |
| 3 | [2, 6] | 6 | [1, 3, 6] |
| 4 | [2, 8, 9] | 9 | [1, 3, 6, 9] |
| 5 | [2, 8] | 8 | [1, 3, 6, 9, 8] |
| 6 | [2] | 2 | [1, 3, 6, 9, 8, 2] |
| 7 | [4, 5] | 5 | [1, 3, 6, 9, 8, 2, 5] |
| 8 | [4] | 4 | [1, 3, 6, 9, 8, 2, 5, 4] |
| 9 | [7] | 7 | [1, 3, 6, 9, 8, 2, 5, 4, 7] |

Ce n'est pas un parcours en largeur. C'est un parcours en profondeur (similaire à un parcours préfixe, mais en visitant le fils droit avant le fils gauche).

**4.e)**
- Arbre vide : BFS = [].
- Arbre à un seul noeud (valeur v) : BFS = [v].

---

## Corrigé du TP

### Partie 1 — taille

```python
def taille(noeud):
    if noeud is None:
        return 0
    return 1 + taille(noeud.gauche) + taille(noeud.droite)
```

Terminaison : le variant est le nombre de noeuds du sous-arbre. Il décroît strictement à chaque appel récursif et atteint 0 au cas de base.

### Partie 2 — hauteur

```python
def hauteur(noeud):
    if noeud is None:
        return -1
    return 1 + max(hauteur(noeud.gauche), hauteur(noeud.droite))
```

Convention -1 : avec hauteur(vide) = 0, une feuille aurait hauteur 1 (= 1 + max(0,0)), ce qui ne correspond pas au nombre d'arêtes (0 pour une feuille). La convention -1 corrige cela.

### Partie 3 — feuilles

```python
def feuilles(noeud):
    if noeud is None:
        return []
    if noeud.gauche is None and noeud.droite is None:
        return [noeud.valeur]
    return feuilles(noeud.gauche) + feuilles(noeud.droite)
```

### Partie 4 — bfs

```python
from collections import deque

def bfs(racine):
    if racine is None:
        return []
    resultat = []
    file = deque()
    file.append(racine)
    while file:
        noeud = file.popleft()
        resultat.append(noeud.valeur)
        if noeud.gauche is not None:
            file.append(noeud.gauche)
        if noeud.droite is not None:
            file.append(noeud.droite)
    return resultat
```

### Partie 5 — Pour aller plus loin

**5.1 — nombre_feuilles**

```python
def nombre_feuilles(noeud):
    if noeud is None:
        return 0
    if noeud.gauche is None and noeud.droite is None:
        return 1
    return nombre_feuilles(noeud.gauche) + nombre_feuilles(noeud.droite)
```

**5.2 — bfs_par_niveau**

```python
def bfs_par_niveau(racine):
    if racine is None:
        return []
    resultat = []
    file = deque()
    file.append(racine)
    while file:
        niveau = []
        for _ in range(len(file)):
            noeud = file.popleft()
            niveau.append(noeud.valeur)
            if noeud.gauche is not None:
                file.append(noeud.gauche)
            if noeud.droite is not None:
                file.append(noeud.droite)
        resultat.append(niveau)
    return resultat
```


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

### Corrigé exercice 1

**Méthode** : on compte les noeuds de l'arbre de référence et on mesure le plus long chemin racine-feuille.
La taille vaut `9` (nombre total de noeuds). La hauteur vaut `3` (chemin 8→3→6→7). Les feuilles sont `{1, 4, 7, 13}`, soit `4` feuilles. Le résultat du parcours en largeur donne `[8, 3, 10, 1, 6, 14, 4, 7, 13]`.

















### Corrigé exercice 2

Réponse détaillée avec justification.

La fonction `taille(arbre)` renvoie `7` pour l'arbre A2.

### Corrigé exercice 3

Réponse détaillée avec justification.

La fonction `hauteur(arbre)` renvoie `3` pour l'arbre A4.

### Corrigé exercice 4

Réponse détaillée avec justification.

Le parcours en largeur donne `[1, 2, 3, 4, 5, 6, 7, 8, 9]` pour l'arbre A5.

### Corrigé exercice 5

Réponse détaillée avec justification.

`hauteur(None)` renvoie `-1` (arbre vide).

### Corrigé exercice 6

Réponse détaillée avec justification.

Le nombre de feuilles vaut `3` pour l'arbre A1.

### Corrigé exercice 7

Réponse détaillée avec justification.

La fonction `bfs_par_niveau(arbre)` renvoie `[[1], [2, 3], [4, 5, 6], [7, 8, 9]]` pour l'arbre A5.

### Corrigé exercice 8

Réponse détaillée avec justification.

La fonction `nombre_feuilles(arbre)` renvoie `4` pour l'arbre B.

