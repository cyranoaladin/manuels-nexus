---
title: "T05 - Trace - Mesures et parcours d'arbres complément"
level: "terminale"
sequence_id: "T05"
document_type: "trace"
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

# T05 - Trace écrite - Mesures et parcours d'arbres complément

## Capacités officielles atomiques

- T-STRUCT-04B : Évaluer quelques mesures des arbres binaires (taille, hauteur, feuilles). « Taille, hauteur et feuilles. »
- T-ALGO-01A : Calculer la taille d’un arbre. « Structure récursive adaptée. »
- T-ALGO-01B : Calculer la hauteur d’un arbre. « Cas arbre vide : hauteur conventionnelle -1 (ou 0 selon la convention). »
- T-ALGO-01D : Parcourir un arbre en largeur d'abord. « Lien avec file. »

## Arbre de référence

```
        8
       / \
      3   10
     / \    \
    1   6    14
       / \   /
      4   7 13
```

---

## 1. Mesures d’un arbre binaire (T-STRUCT-04B)

### Définitions à retenir

| Mesure | Définition | Cas limite (arbre vide) |
|--------|-----------|------------------------|
| **Taille** | Nombre total de noeuds | 0 |
| **Hauteur** | Plus long chemin racine → feuille (en arêtes) | -1 (convention) |
| **Feuilles** | Noeuds sans fils gauche ni fils droit | {} (ensemble vide) |

### Résultats sur l'arbre de référence

- Taille = 9
- Hauteur = 3 (chemin : 8 → 3 → 6 → 4)
- Feuilles = {1, 4, 7, 13}

---

## 2. Algorithme récursif de taille (T-ALGO-01A)

### Formule récursive

```
taille(A) = 0                                   si A est vide
taille(A) = 1 + taille(A.gauche) + taille(A.droite)   sinon
```

### Code Python

```python
def taille(noeud):
    if noeud is None:
        return 0
    return 1 + taille(noeud.gauche) + taille(noeud.droite)
```

### Preuve de terminaison

Variant : nombre de noeuds du sous-arbre. Décroît strictement à chaque appel. Cas de base : arbre vide (0 noeud) → renvoie 0.

### Trace sur l'arbre de référence

taille(8) = 1 + taille(3) + taille(10) = 1 + 5 + 3 = **9**

---

## 3. Algorithme récursif de hauteur (T-ALGO-01B)

### Convention

Hauteur de l'arbre vide = **-1**.

### Formule récursive

```
hauteur(A) = -1                                              si A est vide
hauteur(A) = 1 + max(hauteur(A.gauche), hauteur(A.droite))  sinon
```

### Code Python

```python
def hauteur(noeud):
    if noeud is None:
        return -1
    return 1 + max(hauteur(noeud.gauche), hauteur(noeud.droite))
```

### Preuve de terminaison

Même variant que pour `taille` : nombre de noeuds du sous-arbre. Décroît strictement, atteint 0 au cas de base.

### Trace sur l'arbre de référence

hauteur(8) = 1 + max(hauteur(3), hauteur(10)) = 1 + max(2, 2) = **3**

---

## 4. Parcours en largeur d'abord — BFS (T-ALGO-01D)

### Principe

Visiter les noeuds **niveau par niveau**, de gauche à droite, en utilisant une **file** (FIFO).

### Algorithme

```
BFS(racine) :
    F ← file vide
    enfiler(racine, F)
    tant que F non vide :
        n ← défiler(F)
        traiter(n)
        si n.gauche existe : enfiler(n.gauche, F)
        si n.droite existe : enfiler(n.droite, F)
```

### Code Python

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

### Trace sur l'arbre de référence

| Étape | File | Traité | Résultat |
|-------|------|--------|----------|
| 1 | [8] | 8 | [8] |
| 2 | [3, 10] | 3 | [8, 3] |
| 3 | [10, 1, 6] | 10 | [8, 3, 10] |
| 4 | [1, 6, 14] | 1 | [8, 3, 10, 1] |
| 5 | [6, 14] | 6 | [8, 3, 10, 1, 6] |
| 6 | [14, 4, 7] | 14 | [8, 3, 10, 1, 6, 14] |
| 7 | [4, 7, 13] | 4 | [8, 3, 10, 1, 6, 14, 4] |
| 8 | [7, 13] | 7 | [8, 3, 10, 1, 6, 14, 4, 7] |
| 9 | [13] | 13 | [8, 3, 10, 1, 6, 14, 4, 7, 13] |

**Résultat BFS = [8, 3, 10, 1, 6, 14, 4, 7, 13]**

### Pourquoi une file ?

La file garantit l'ordre FIFO : les noeuds du niveau k sont tous traités avant ceux du niveau k+1. Une pile donnerait un parcours en profondeur, pas en largeur.

---

## Formules essentielles à retenir

| Mesure | Formule récursive | Cas de base |
|--------|-------------------|-------------|
| Taille | 1 + taille(g) + taille(d) | 0 si vide |
| Hauteur | 1 + max(h(g), h(d)) | -1 si vide |
| BFS | File : enfiler / défiler | [] si vide |


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
