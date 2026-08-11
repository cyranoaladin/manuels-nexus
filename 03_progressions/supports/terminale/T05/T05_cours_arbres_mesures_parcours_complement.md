---
title: "T05 - Cours - Mesures et parcours d'arbres complément"
level: "terminale"
sequence_id: "T05"
document_type: "cours"
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

# T05 - Cours - Mesures et parcours d'arbres complément

## Objectifs spécifiques

- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques

- T-STRUCT-04B : Évaluer quelques mesures des arbres binaires (taille, hauteur, feuilles). « Taille, hauteur et feuilles. »
- T-ALGO-01A : Calculer la taille d’un arbre. « Structure récursive adaptée. »
- T-ALGO-01B : Calculer la hauteur d’un arbre. « Cas arbre vide : hauteur conventionnelle -1 (ou 0 selon la convention). »
- T-ALGO-01D : Parcourir un arbre en largeur d'abord. « Lien avec file. »

## Prérequis

- Connaître la définition d’un arbre binaire (racine, noeud, feuille, sous-arbre gauche/droit).
- Maîtriser la récursivité (appel récursif, cas de base).
- Connaître la structure de file (FIFO).

## Définitions

Un arbre binaire est une structure récursive. Les mesures fondamentales sont la taille (nombre de noeuds), la hauteur (longueur du plus long chemin racine-feuille) et le nombre de feuilles (noeuds terminaux sans enfant).

## Arbre de référence

Tous les exemples de ce cours utilisent l'arbre binaire suivant :

```
        8
       / \
      3   10
     / \    \
    1   6    14
       / \   /
      4   7 13
```

Propriétés attendues : taille = 9, hauteur = 3, feuilles = {1, 4, 7, 13}, BFS = [8, 3, 10, 1, 6, 14, 4, 7, 13].

---

## Section 1 — Mesures sur papier (T-STRUCT-04B)

### 1.1 Définitions

**Taille** : nombre total de noeuds dans l'arbre.

**Hauteur** : longueur du plus long chemin de la racine à une feuille, mesurée en nombre d'arêtes.
Convention adoptée : la hauteur d’un arbre vide vaut -1 ; la hauteur d’un arbre réduit à une feuille vaut 0.

**Feuille** : noeud sans fils gauche ni fils droit.

### Exemple corrigé 1 — Mesures sur l'arbre de référence

**Taille** : on dénombre chaque noeud : 8, 3, 10, 1, 6, 14, 4, 7, 13. Total = 9.

**Hauteur** : le plus long chemin est 8 → 3 → 6 → 4 (ou 8 → 3 → 6 → 7), soit 3 arêtes. Hauteur = 3.

**Feuilles** : les noeuds sans enfant sont 1, 4, 7 et 13. Ensemble des feuilles = {1, 4, 7, 13}.

### Exemple corrigé 5 — Cas limites des mesures

- Arbre vide : taille = 0, hauteur = -1, feuilles = {} (ensemble vide).
- Arbre réduit à une feuille : taille = 1, hauteur = 0, feuilles = {racine}.

### Question 1 — Vérification des cas limites

Pour un arbre réduit au seul noeud 42, vérifier que taille = 1, hauteur = 0 et feuilles = {42}.

---

## Section 2 — Calculer la taille d’un arbre récursivement (T-ALGO-01A)

### 2.1 Principe récursif

La taille d’un arbre se décompose récursivement :

```
taille(arbre) =
    0                                           si arbre est vide
    1 + taille(gauche) + taille(droite)         sinon
```

### 2.2 Algorithme en Python

```python
def taille(noeud):
    """Renvoie le nombre de noeuds de l'arbre enraciné en noeud."""
    if noeud is None:
        return 0
    return 1 + taille(noeud.gauche) + taille(noeud.droite)
```

### Exemple corrigé 2 — Trace d'exécution de taille

```
taille(8)
  = 1 + taille(3) + taille(10)
  = 1 + (1 + taille(1) + taille(6)) + (1 + taille(None) + taille(14))
  = 1 + (1 + 1 + (1 + taille(4) + taille(7))) + (1 + 0 + (1 + taille(13) + taille(None)))
  = 1 + (1 + 1 + (1 + 1 + 1)) + (1 + 0 + (1 + 1 + 0))
  = 1 + (1 + 1 + 3) + (1 + 0 + 2)
  = 1 + 5 + 3
  = 9
```

### Question 2 — Appliquer la formule récursive

Calculer `taille(noeud)` pour un arbre contenant uniquement une racine et un fils gauche (2 noeuds). Vérifier que le résultat est bien 2.

### 2.4 Preuve de terminaison

**Variant de boucle** : le nombre de noeuds dans le sous-arbre passé en argument.

- À chaque appel récursif, on passe un sous-arbre strict (gauche ou droit), qui contient strictement moins de noeuds que l'arbre courant.
- Le variant est un entier naturel qui décroît strictement à chaque appel.
- Le cas de base est atteint quand le sous-arbre est vide (0 noeud), et l'algorithme renvoie 0.
- Donc l'algorithme termine toujours.

---

## Section 3 — Calculer la hauteur d’un arbre récursivement (T-ALGO-01B)

### 3.1 Convention pour l'arbre vide

**Convention choisie** : la hauteur d’un arbre vide vaut **-1**.

Justification : ainsi, la hauteur d’une feuille vaut max(-1, -1) + 1 = 0, ce qui correspond bien à un chemin de 0 arête.

### 3.2 Principe récursif

```
hauteur(arbre) =
    -1                                                  si arbre est vide
    1 + max(hauteur(gauche), hauteur(droite))           sinon
```

### 3.3 Algorithme en Python

```python
def hauteur(noeud):
    """Renvoie la hauteur de l'arbre enraciné en noeud.
    Convention : hauteur d’un arbre vide = -1."""
    if noeud is None:
        return -1
    return 1 + max(hauteur(noeud.gauche), hauteur(noeud.droite))
```

### Exemple corrigé 3 — Trace d'exécution de hauteur

```
hauteur(8)
  = 1 + max(hauteur(3), hauteur(10))
  hauteur(3) = 1 + max(hauteur(1), hauteur(6))
    hauteur(1) = 1 + max(-1, -1) = 0
    hauteur(6) = 1 + max(hauteur(4), hauteur(7))
      hauteur(4) = 0
      hauteur(7) = 0
    hauteur(6) = 1 + max(0, 0) = 1
  hauteur(3) = 1 + max(0, 1) = 2
  hauteur(10) = 1 + max(-1, hauteur(14))
    hauteur(14) = 1 + max(hauteur(13), -1)
      hauteur(13) = 0
    hauteur(14) = 1 + max(0, -1) = 1
  hauteur(10) = 1 + max(-1, 1) = 2
hauteur(8) = 1 + max(2, 2) = 3
```

### Question 3 — Convention hauteur de l'arbre vide

Expliquer pourquoi la convention hauteur(vide) = -1 est préférable à hauteur(vide) = 0 en calculant la hauteur d'une feuille dans chaque cas.

### 3.5 Preuve de terminaison

Le raisonnement est identique à celui de `taille` : le variant est le nombre de noeuds du sous-arbre, qui décroît strictement à chaque appel récursif et atteint 0 (arbre vide) au cas de base. L'algorithme termine donc toujours.

---

## Section 4 — Parcours en largeur d'abord (BFS) avec file (T-ALGO-01D)

### 4.1 Principe

Le parcours en largeur d'abord (BFS — Breadth-First Search) visite les noeuds niveau par niveau, de gauche à droite. Il utilise une **file** (structure FIFO) pour mémoriser les noeuds à visiter.

### 4.2 Algorithme

```
BFS(racine) :
    créer une file vide F
    enfiler racine dans F
    tant que F n'est pas vide :
        noeud ← défiler F
        traiter noeud
        si noeud.gauche existe : enfiler noeud.gauche
        si noeud.droite existe : enfiler noeud.droite
```

### 4.3 Algorithme en Python

```python
from collections import deque

def bfs(racine):
    """Renvoie la liste des valeurs en parcours largeur."""
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

### Exemple corrigé 4 — Trace d'exécution du parcours BFS

| Étape | File (avant défilement) | Noeud traité | Résultat partiel |
|-------|------------------------|--------------|-----------------|
| 1 | [8] | 8 | [8] |
| 2 | [3, 10] | 3 | [8, 3] |
| 3 | [10, 1, 6] | 10 | [8, 3, 10] |
| 4 | [1, 6, 14] | 1 | [8, 3, 10, 1] |
| 5 | [6, 14] | 6 | [8, 3, 10, 1, 6] |
| 6 | [14, 4, 7] | 14 | [8, 3, 10, 1, 6, 14] |
| 7 | [4, 7, 13] | 4 | [8, 3, 10, 1, 6, 14, 4] |
| 8 | [7, 13] | 7 | [8, 3, 10, 1, 6, 14, 4, 7] |
| 9 | [13] | 13 | [8, 3, 10, 1, 6, 14, 4, 7, 13] |

Résultat final : [8, 3, 10, 1, 6, 14, 4, 7, 13].

### Question 4 — Comparer BFS et parcours en profondeur

Sur l'arbre de référence, donner l'ordre de visite en parcours en profondeur préfixe et comparer avec le résultat du BFS. Expliquer la différence.

### Question 5 — BFS sur un arbre vide

Quel est le résultat du parcours BFS sur un arbre vide ? Quel est le résultat sur un arbre à un seul noeud ?

### 4.5 Lien avec la structure de file

Le parcours BFS **ne peut pas** être implémenté par un simple appel récursif (contrairement aux parcours en profondeur). La file garantit l'ordre FIFO : les noeuds découverts en premier sont traités en premier, ce qui assure le traitement niveau par niveau.

En Python, `collections.deque` offre des opérations `append` (enfiler) et `popleft` (défiler) en O(1).

---

### Question 6 — Relation entre taille et hauteur

Pour un arbre binaire de hauteur h, quelle est la taille maximale possible ? Justifier par un exemple.

### Question 7 — Compter les feuilles

Sur l'arbre de référence, vérifier que le nombre de feuilles est bien 4. Proposer une formule récursive pour compter les feuilles.

### Exemple corrigé 6 — BFS par niveau

Sur l'arbre de référence, le parcours BFS par niveau donne : [[8], [3, 10], [1, 6, 14], [4, 7, 13]]. Chaque sous-liste correspond à un niveau de l'arbre.

---

## Synthèse

| Mesure / Parcours | Méthode | Complexité temporelle |
|---|---|---|
| Taille | Récursion : 1 + taille(g) + taille(d) | O(n) |
| Hauteur | Récursion : 1 + max(h(g), h(d)) | O(n) |
| Feuilles | Récursion ou parcours : tester absence de fils | O(n) |
| BFS | File (deque) : enfiler/défiler | O(n) |

Cas limites à retenir : arbre vide (taille=0, hauteur=-1, BFS=[]).

### Question 8 — Résumé des cas limites

Dresser un tableau récapitulatif des résultats attendus pour taille, hauteur, feuilles et BFS sur un arbre vide et un arbre à un seul noeud.


## Situation-problème

Un biologiste modélise un arbre phylogénétique et doit calculer le nombre d'espèces (taille), la profondeur maximale (hauteur) et lister les espèces terminales (feuilles). Comment parcourir l'arbre ?

## Activité d’entrée

Dessiner un arbre binaire de 7 noeuds, compter ses feuilles et mesurer sa hauteur à la main avant de programmer.

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

Taille et hauteur calculées correctement par récursion. Parcours en largeur produit le bon ordre avec une file.

## Séance(s) correspondante(s)

Séance dédiée.

Critère de validation : taille et hauteur calculées correctement par récursion.
Observable : le parcours en largeur utilise une file et produit le bon ordre.

