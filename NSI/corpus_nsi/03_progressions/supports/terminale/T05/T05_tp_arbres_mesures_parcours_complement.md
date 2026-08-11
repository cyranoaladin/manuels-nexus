---
title: "T05 - TP - Mesures et parcours d'arbres complément"
level: "terminale"
sequence_id: "T05"
document_type: "tp"
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

# T05 - TP - Mesures et parcours d'arbres complément

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

Taille = 9, hauteur = 3, feuilles = {1, 4, 7, 13}, BFS = [8, 3, 10, 1, 6, 14, 4, 7, 13].

---

## Partie 0 — Classe Noeud et construction de l'arbre

Le code suivant définit la classe `Noeud` et construit l'arbre de référence. Recopier ce code dans un fichier `tp_arbres.py`.

```python
from collections import deque


class Noeud:
    """Représente un noeud d’un arbre binaire."""

    def __init__(self, valeur, gauche=None, droite=None):
        self.valeur = valeur
        self.gauche = gauche
        self.droite = droite

    def __repr__(self):
        return f"Noeud({self.valeur})"


# Construction de l'arbre de référence
arbre_ref = Noeud(8,
    Noeud(3,
        Noeud(1),
        Noeud(6,
            Noeud(4),
            Noeud(7)
        )
    ),
    Noeud(10,
        None,
        Noeud(14,
            Noeud(13),
            None
        )
    )
)
```

---

## Partie 1 — Calcul de la taille (T-ALGO-01A)

### Question 1.1

Compléter la fonction `taille` ci-dessous pour qu'elle renvoie le nombre de noeuds de l'arbre.

```python
def taille(noeud):
    """Renvoie le nombre de noeuds de l'arbre enraciné en noeud.
    Renvoie 0 si noeud est None (arbre vide)."""
    if noeud is None:
        return ...  # cas de base
    return ...  # appel récursif
```

### Question 1.2

Tester la fonction sur l'arbre de référence :

```python
assert taille(arbre_ref) == 9
assert taille(None) == 0
assert taille(Noeud(42)) == 1
print("taille : tous les tests passent")
```

### Question 1.3

En commentaire dans le code, expliquer en 2-3 lignes pourquoi cet algorithme termine toujours (variant de terminaison).

---

## Partie 2 — Calcul de la hauteur (T-ALGO-01B)

### Question 2.1

Compléter la fonction `hauteur` ci-dessous. Convention : la hauteur d’un arbre vide vaut -1.

```python
def hauteur(noeud):
    """Renvoie la hauteur de l'arbre enraciné en noeud.
    Convention : hauteur d’un arbre vide = -1."""
    if noeud is None:
        return ...  # cas de base
    return ...  # appel récursif
```

### Question 2.2

Tester la fonction :

```python
assert hauteur(arbre_ref) == 3
assert hauteur(None) == -1
assert hauteur(Noeud(42)) == 0
assert hauteur(Noeud(1, Noeud(2), None)) == 1
print("hauteur : tous les tests passent")
```

### Question 2.3

Pourquoi choisit-on -1 pour l'arbre vide et non 0 ? Expliquer en commentaire.

---

## Partie 3 — Liste des feuilles (T-STRUCT-04B)

### Question 3.1

Écrire une fonction `feuilles(noeud)` qui renvoie la liste des valeurs des feuilles de l'arbre (dans l'ordre d’un parcours en profondeur gauche-droite).

```python
def feuilles(noeud):
    """Renvoie la liste des valeurs des feuilles."""
    # À compléter
    pass
```

### Question 3.2

Tester la fonction :

```python
assert set(feuilles(arbre_ref)) == {1, 4, 7, 13}
assert feuilles(None) == []
assert feuilles(Noeud(42)) == [42]
print("feuilles : tous les tests passent")
```

---

## Partie 4 — Parcours en largeur d'abord (T-ALGO-01D)

### Question 4.1

Compléter la fonction `bfs` ci-dessous. Utiliser `collections.deque` comme file.

```python
def bfs(racine):
    """Renvoie la liste des valeurs en parcours largeur (BFS).
    Utilise une file (collections.deque)."""
    if racine is None:
        return []
    resultat = []
    file = deque()
    file.append(racine)
    while ...:  # condition d'arrêt
        noeud = ...  # défiler
        resultat.append(...)
        if ...:  # fils gauche existe
            file.append(...)
        if ...:  # fils droit existe
            file.append(...)
    return resultat
```

### Question 4.2

Tester la fonction :

```python
assert bfs(arbre_ref) == [8, 3, 10, 1, 6, 14, 4, 7, 13]
assert bfs(None) == []
assert bfs(Noeud(42)) == [42]
print("bfs : tous les tests passent")
```

### Question 4.3

Modifier la fonction pour afficher le contenu de la file à chaque étape de la boucle. Vérifier que la trace correspond au tableau du cours.

---

### Question 4.4 — Trace manuelle

Reproduire la trace du BFS sur l'arbre de référence en notant le contenu de la file à chaque étape. Comparer avec le tableau du cours.

---

## Partie 5 — Pour aller plus loin

### Question 5.1

Écrire une fonction `nombre_feuilles(noeud)` qui renvoie le nombre de feuilles de l'arbre **sans** construire la liste des feuilles (directement par récursion).

### Question 5.2

Écrire une fonction `bfs_par_niveau(racine)` qui renvoie une liste de listes, chaque sous-liste contenant les valeurs d’un niveau.

Exemple sur l'arbre de référence :
```python
assert bfs_par_niveau(arbre_ref) == [[8], [3, 10], [1, 6, 14], [4, 7, 13]]
```


## Objectifs


## Prérequis


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

- Critère de réussite : taille() et hauteur() retournent les valeurs correctes sur l'arbre exemple.
- Critère de validation : le parcours en largeur utilise une file et produit l'ordre attendu.
- Observable : la preuve de terminaison identifie le variant de boucle.


## Séance(s) correspondante(s)

Séance dédiée.

## Tests attendus

Vérifier le résultat avec les jeux de tests fournis.

## Exemple d’exécution

Exécuter taille(), hauteur() et bfs() sur l'arbre exemple et comparer avec les résultats calculés à la main.

## Livrable vérifiable

Module Python implémentant les fonctions taille(), hauteur() et bfs() sur des arbres binaires.

## Consigne technique détaillée

Utiliser la classe Noeud fournie et implémenter les fonctions récursives demandées.

## Cas limite

Tester avec des entrées vides et des cas extrêmes.

