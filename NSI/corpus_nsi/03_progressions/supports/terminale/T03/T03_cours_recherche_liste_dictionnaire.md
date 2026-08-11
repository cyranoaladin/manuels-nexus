---
title: "T03 - Cours - Recherche liste vs dictionnaire"
level: "terminale"
sequence_id: "T03"
document_type: "cours"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures linéaires et tables associatives"
notion: "recherche, liste, dictionnaire, index, clé, complexité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-03C"
---

# Cours — Recherche dans une liste vs dans un dictionnaire

## Capacité visée

> Distinguer la recherche d’une valeur dans une liste et dans un dictionnaire.

---

**Définition** : la recherche dans une structure de données consiste a determiner si un element donne est present dans cette structure, et le cas echeant a y acceder. La complexite de cette operation depend du type de structure utilisee.

**A savoir** : en Python, l'operateur `in` effectue une recherche dont le cout depend de la structure sous-jacente : parcours sequentiel en O(n) pour une liste, acces par hachage en O(1) moyen pour un dictionnaire.

## 1. Rappels sur les structures

### 1.1 La liste Python

Une **liste** est une séquence ordonnée d'éléments, repérés par leur **index** (position entière, commençant à 0).

```python
eleves = ["Alice", "Bob", "Charlie", "Diana"]
#           0        1        2          3
```

L'accès par index est en O(1), mais la **recherche d’une valeur** impose de parcourir la liste.

### 1.2 Le dictionnaire Python

Un **dictionnaire** est une table associative qui relie des **clés** à des **valeurs**. Chaque clé est unique et permet un accès direct grâce à une fonction de hachage interne.

```python
notes = {"Alice": 15, "Bob": 12, "Charlie": 17, "Diana": 14}
```

La **clé** joue le rôle d'identifiant ; elle remplace la notion de position.

---

## 2. Recherche d’une valeur dans une liste — parcours séquentiel

Pour savoir si une valeur `x` appartient à une liste, Python réalise un **parcours séquentiel** (linéaire) :

```python
def recherche_liste(lst, x):
    """Renvoie True si x est dans lst, False sinon."""
    for element in lst:
        if element == x:
            return True
    return False
```

L'opérateur `in` fait exactement ce parcours :

```python
x in liste   # parcours séquentiel, O(n)
```

### Complexité

| Cas | Nombre de comparaisons | Complexité |
|-----|------------------------|------------|
| Meilleur cas (élément en tête) | 1 | O(1) |
| Pire cas (élément absent ou en fin) | n | O(n) |
| Cas moyen | n/2 | O(n) |

**La recherche dans une liste est en O(n)** : le temps croît linéairement avec la taille de la liste.

---

## 3. Recherche d’une clé dans un dictionnaire — accès direct

Pour savoir si une clé `cle` existe dans un dictionnaire, Python utilise une **table de hachage** qui calcule directement la position en mémoire :

```python
cle in dico   # accès direct par clé, O(1) en moyenne
```

### Mécanisme simplifié

1. Python calcule `hash(cle)`, un entier.
2. Cet entier détermine un emplacement dans la table interne.
3. Python vérifie directement cet emplacement.

Il n'y a **pas de parcours** de l'ensemble des entrées.

### Complexité

| Cas | Complexité |
|-----|------------|
| Cas moyen (attendu) | O(1) |
| Pire cas théorique (collisions extrêmes) | O(n) |

**La recherche dans un dictionnaire est en O(1) en moyenne** : le temps est quasi constant quelle que soit la taille du dictionnaire.

---

## 4. Comparaison synthétique

| Critère | Liste | Dictionnaire |
|---------|-------|--------------|
| Repérage des éléments | par **index** (position) | par **clé** (identifiant) |
| Opération testée | `x in liste` | `cle in dico` |
| Méthode interne | parcours séquentiel | hachage + accès direct |
| Complexité moyenne | **O(n)** | **O(1)** |
| Adapté quand… | l'ordre compte, peu de recherches | beaucoup de recherches, accès par identifiant |

---

## 5. Mesure expérimentale du temps

On peut vérifier la différence de complexité avec le module `time` :

```python
import time

n = 1_000_000
liste = list(range(n))
dico = {i: True for i in range(n)}
cible = n - 1  # pire cas pour la liste

# Recherche dans la liste
debut = time.perf_counter()
resultat_liste = cible in liste
duree_liste = time.perf_counter() - debut

# Recherche dans le dictionnaire
debut = time.perf_counter()
resultat_dico = cible in dico
duree_dico = time.perf_counter() - debut

print(f"Liste  : {duree_liste:.6f} s")
print(f"Dico   : {duree_dico:.6f} s")
print(f"Ratio  : x{duree_liste / duree_dico:.0f}")
```

**Résultat typique** (ordre de grandeur) :

```
Liste  : 0.012000 s
Dico   : 0.000001 s
Ratio  : x12000
```

Plus `n` augmente, plus l'écart se creuse : c'est la manifestation concrète de O(n) vs O(1).

---

## 6. Lien entre index et clé

| Concept | Liste | Dictionnaire |
|---------|-------|--------------|
| Accès direct | `liste[i]` — par **index** (entier) | `dico[cle]` — par **clé** (tout type hachable) |
| Recherche de valeur | parcours nécessaire | non applicable (on cherche par clé) |

L'**index** est une position numérique imposée par l'ordre d'insertion. La **clé** est un identifiant choisi par le programmeur, qui permet un accès en temps constant.

---

## 7. Ce qu'il faut retenir

1. `x in liste` effectue un **parcours séquentiel** en **O(n)**.
2. `cle in dico` effectue un **accès direct par hachage** en **O(1)** (cas moyen).
3. Quand on a besoin de recherches fréquentes, un dictionnaire est bien plus efficace qu'une liste.
4. La clé d’un dictionnaire joue un rôle analogue à l'index d’une liste, mais avec un accès direct à la valeur associée.


## Objectifs


## Capacités officielles


## Prérequis


## Situation-problème

Un programme de correcteur orthographique doit vérifier si un mot appartient au dictionnaire français (300 000 mots). La recherche séquentielle prend trop de temps. Comment accélérer ?

## Activité d’entrée

Mesurer le temps de recherche de 10 000 mots dans une liste de 100 000 éléments, puis dans un dictionnaire de 100 000 clés. Comparer.



## Définitions et formalisation

La recherche dans une liste parcourt les éléments un par un (accès séquentiel). La recherche dans un dictionnaire accède directement par clé (accès associatif). Cette différence fondamentale détermine la complexité algorithmique de chaque opération.

### Exemple 1 — Recherche sequentielle dans une liste

On dispose de la liste `prenoms = ["Alice", "Bob", "Charlie", "Diana"]`. Pour chercher si `"Charlie"` est present, Python parcourt les elements un par un : il compare `"Alice"`, puis `"Bob"`, puis `"Charlie"` et renvoie `True` apres 3 comparaisons. Si l'on cherche `"Eve"` (element absent), Python parcourt les 4 elements sans trouver de correspondance et renvoie `False` apres n comparaisons. La complexite est O(n).

### Exemple 2 — Recherche par cle dans un dictionnaire

On dispose du dictionnaire `notes = {"Alice": 15, "Bob": 12, "Charlie": 17}`. Pour verifier si la cle `"Charlie"` existe, Python calcule `hash("Charlie")`, accede directement a l'emplacement correspondant dans la table de hachage et renvoie `True` en temps constant O(1). Il n'y a pas de parcours sequentiel des autres cles.

### Exemple 3 — Comparaison experimentale des temps de recherche

On construit une liste et un dictionnaire de 100 000 elements. On cherche l'element `99999` (pire cas pour la liste). La recherche dans la liste prend environ 0.003 s (parcours sequentiel de 100 000 elements), tandis que la recherche dans le dictionnaire prend environ 0.000001 s (acces direct par hachage). Le ratio est de l'ordre de 3000, ce qui illustre concretement la difference entre O(n) et O(1).

## Exercices

Exercices de recherche dans des listes et dictionnaires avec analyse de complexité.

## Corrigé

Les corrigés détaillés sont dans T03_corrige_recherche_liste_dictionnaire.md.

## Erreurs fréquentes

- EF1 : confondre la complexité de recherche dans une liste (O(n)) et dans un dictionnaire (O(1)).
- EF2 : oublier que `val in dico.values()` est en O(n) et non O(1).
- EF3 : mélanger index de position (liste) et clé d'accès (dictionnaire).


## Cas limites

- Recherche dans une liste vide : `x in []` renvoie toujours `False` sans aucune comparaison.
- Recherche dans un dictionnaire vide : `cle in {}` renvoie toujours `False` en temps constant.
- Recherche d'un element absent : dans une liste, le parcours sequentiel examine tous les elements avant de conclure a l'absence ; dans un dictionnaire, le hachage detecte l'absence en O(1).
- Recherche avec une cle invalide (type non hachable) : `[1, 2] in dico` leve une exception `TypeError` car les listes ne sont pas hachables.
- Doublon dans une liste : si un element apparait plusieurs fois, la recherche `x in liste` s'arrete au premier doublon trouve.

## Remédiation

Exercice de remediation : chronometrer manuellement 100 recherches dans une liste puis dans un dictionnaire et expliquer l'ecart.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.

## Savoir-faire et méthodes opérationnelles

- Chercher un element dans une liste par parcours sequentiel avec l'operateur `in` ou une boucle `for`.
- Tester si une cle existe dans un dictionnaire avec `cle in dico` avant d'y acceder.
- Vérifier qu'une structure est vide avant d'y effectuer une recherche.
- Parcourir les cles d'un dictionnaire avec `for cle in dico` pour filtrer les entrees selon un critere.
- Convertir une liste en dictionnaire pour accelerer les recherches repetees.
- Trier une liste avant d'appliquer une recherche dichotomique pour reduire la complexite a O(log n).
- Calculer le temps d'execution d'une recherche avec `time.perf_counter()` pour comparer experimentalement les performances.

## Critères de réussite

- Critère de réussite : les mesures de temps confirment O(n) pour la liste et O(1) pour le dictionnaire.
- Critère de validation : l'élève justifie la différence de complexité par le mécanisme d'accès.
- Observable : le code de benchmark est correct et les résultats cohérents.


## Séance(s) correspondante(s)

Séance dédiée.

### Exercice 1
Rechercher la valeur 42 dans la liste [10, 20, 30, 42, 50]. Combien de comparaisons ?

### Exercice 2
Rechercher la clé 'Alice' dans le dictionnaire {'Alice': 15, 'Bob': 12}. Combien de comparaisons ?

