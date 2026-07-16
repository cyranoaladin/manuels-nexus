---
title: "P04 - Cours - Types construits complément"
level: "premiere"
sequence_id: "P04"
document_type: "cours"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Tuples, listes, dictionnaires"
notion: "p-uplet, compréhension, matrice, dictionnaire, itération"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-CONSTR-01"
    - "P-DATA-CONSTR-02B"
    - "P-DATA-CONSTR-02C"
    - "P-DATA-CONSTR-03A"
    - "P-DATA-CONSTR-03B"
    - "P-DATA-CONSTR-03C"
---

# P04 - Cours - Types construits complément

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs
- P-DATA-CONSTR-02B : Construire un tableau par compréhension
- P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices
- P-DATA-CONSTR-03A : Construire une entrée de dictionnaire
- P-DATA-CONSTR-03B : Itérer sur les éléments d’un dictionnaire
- P-DATA-CONSTR-03C : Utiliser les méthodes keys, values et items

## Prérequis
- Connaître les types de base en Python (int, float, str, bool).
- Savoir définir et appeler une fonction avec `def` et `return`.
- Connaître la syntaxe de base des tuples, listes et dictionnaires (séquence P04 initiale).
- Maîtriser les boucles `for` et `while`.

## Séance(s) correspondante(s)
- P04-S1 à P04-S7 : support rattaché aux séances prêtes de la progression.

---

## 1. P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs

### Définition

Un **p-uplet** (tuple) est une collection ordonnée et **immuable** de valeurs. Une fonction peut renvoyer plusieurs valeurs simultanément en les regroupant dans un p-uplet grâce à l'instruction `return`.

La syntaxe `return a, b` est équivalente à `return (a, b)`. Python construit automatiquement un tuple.

### Formalisation

```python
def nom_fonction(parametres):
    # calculs
    return valeur1, valeur2  # renvoie un tuple (valeur1, valeur2)
```

Le tuple renvoyé peut être déballé lors de l'appel :

```python
x, y = nom_fonction(arguments)
```

### Exemple corrigé 1 - Fonction renvoyant min et max

```python
def min_max(tableau):
    """Renvoie le minimum et le maximum d’un tableau non vide."""
    mini = tableau[0]
    maxi = tableau[0]
    for val in tableau:
        if val < mini:
            mini = val
        if val > maxi:
            maxi = val
    return mini, maxi
```

- Donnée étudiée : `[7, 2, 9, 4, 1]`.
- Méthode : parcours complet pour trouver les deux extrema.
- Résultat obtenu : `(1, 9)`.
- Déballage : `plus_petit, plus_grand = min_max([7, 2, 9, 4, 1])`.

### Exemple corrigé 2 - Coordonnées d’un point milieu

```python
def milieu(xa, ya, xb, yb):
    """Renvoie les coordonnées du milieu de [AB]."""
    mx = (xa + xb) / 2
    my = (ya + yb) / 2
    return mx, my
```

- Donnée étudiée : `A(0, 0)` et `B(6, 4)`.
- Résultat obtenu : `(3.0, 2.0)`.

### Cas limites

- Tableau d’un seul élément pour `min_max` : renvoie `(e, e)` avec le même élément en min et max.
- Tableau vide : provoque une erreur `IndexError` car `tableau[0]` est impossible. Il convient de documenter la précondition ou de lever une exception explicite.

---

## 2. P-DATA-CONSTR-02B : Construire un tableau par compréhension

### Définition

Un **tableau par compréhension** (list comprehension) permet de construire une liste en une seule expression lisible. On se limite aux formes simples et lisibles.

### Formalisation

```python
nouveau_tableau = [expression for variable in iterable]
```

Avec filtre optionnel :

```python
nouveau_tableau = [expression for variable in iterable if condition]
```

### Exemple corrigé 1 - Carrés des entiers

```python
carres = [x ** 2 for x in range(10)]
# Résultat : [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

- Donnée étudiée : les entiers de 0 à 9.
- Méthode : appliquer l'opération `x ** 2` à chaque entier.
- Résultat obtenu : liste de 10 carrés parfaits.

### Exemple corrigé 2 - Filtrer les valeurs paires

```python
pairs = [n for n in range(20) if n % 2 == 0]
# Résultat : [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Exemple corrigé 3 - Conversion de températures

```python
celsius = [0, 10, 20, 30, 40]
fahrenheit = [c * 9 / 5 + 32 for c in celsius]
# Résultat : [32.0, 50.0, 68.0, 86.0, 104.0]
```

### Cas limites

- Compréhension sur un itérable vide : `[x for x in []]` produit `[]`.
- Expression constante : `[0 for _ in range(5)]` produit `[0, 0, 0, 0, 0]`, utile pour initialiser un tableau.

### Remarque importante

On ne demande pas d'écrire des compréhensions imbriquées complexes. La lisibilité prime : si l'expression devient difficile à lire, on préfère une boucle classique.

---

## 3. P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices

### Définition

Une **matrice** est représentée en Python par une **liste de listes** (tableau de tableaux). Chaque sous-liste représente une ligne. L'accès à l'élément en ligne `i`, colonne `j` se fait par `matrice[i][j]`. On n'utilise pas de bibliothèque externe (pas de NumPy).

### Formalisation

Une matrice de `n` lignes et `p` colonnes :

```python
matrice = [
    [a00, a01, a02],  # ligne 0
    [a10, a11, a12],  # ligne 1
    [a20, a21, a22],  # ligne 2
]
```

- `matrice[i]` donne la ligne `i` (une liste).
- `matrice[i][j]` donne l'élément en ligne `i`, colonne `j`.
- `len(matrice)` donne le nombre de lignes.
- `len(matrice[0])` donne le nombre de colonnes.

### Exemple corrigé 1 - Création et accès

```python
notes = [
    [12, 15, 8],
    [14, 10, 16],
    [9, 11, 13],
]
```

- `notes[0][1]` vaut `15` (ligne 0, colonne 1).
- `notes[2][2]` vaut `13` (ligne 2, colonne 2).

### Exemple corrigé 2 - Parcours complet d’une matrice

```python
def somme_matrice(matrice):
    """Renvoie la somme de tous les éléments de la matrice."""
    total = 0
    for i in range(len(matrice)):
        for j in range(len(matrice[i])):
            total = total + matrice[i][j]
    return total
```

- Donnée étudiée : la matrice `notes` ci-dessus.
- Résultat obtenu : `12 + 15 + 8 + 14 + 10 + 16 + 9 + 11 + 13 = 108`.

### Exemple corrigé 3 - Initialisation par compréhension

```python
zeros = [[0 for j in range(4)] for i in range(3)]
# Résultat : [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
```

### Cas limites et erreur fréquente

**Erreur classique** : initialiser avec la multiplication.

```python
# INCORRECT : les 3 lignes partagent le même objet en mémoire
mauvais = [[0] * 4] * 3
mauvais[0][0] = 1
# mauvais vaut [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]]
```

La bonne méthode est d'utiliser la compréhension `[[0]*4 for _ in range(3)]`.

- Matrice 1x1 : `[[5]]`, accès `matrice[0][0]`.
- Indice hors limites : `matrice[3][0]` sur une matrice 3x3 lève `IndexError`.

---

## 4. P-DATA-CONSTR-03A : Construire une entrée de dictionnaire

### Définition

Un **dictionnaire** associe des **clés** à des **valeurs**. Construire une entrée consiste à ajouter ou modifier une association `clé: valeur` dans un dictionnaire existant, avec la syntaxe `d[cle] = valeur`.

### Formalisation

```python
d = {}              # dictionnaire vide
d[cle] = valeur     # ajoute ou met à jour l'entrée
```

Les clés doivent être de type immuable (str, int, tuple). Les valeurs peuvent être de tout type.

### Exemple corrigé 1 - Métadonnées EXIF d’une photo

```python
exif = {}
exif["appareil"] = "Nikon D3500"
exif["date"] = "2025-06-15"
exif["resolution"] = (6000, 4000)
exif["iso"] = 400
exif["flash"] = False
```

- Donnée étudiée : les métadonnées fictives d’un fichier photo.
- Méthode : chaque affectation `exif[cle] = valeur` crée une entrée.
- Résultat obtenu : `{"appareil": "Nikon D3500", "date": "2025-06-15", "resolution": (6000, 4000), "iso": 400, "flash": False}`.

### Exemple corrigé 2 - Mise à jour d’une entrée existante

```python
exif["iso"] = 800  # modification de la valeur associée à la clé "iso"
```

Si la clé existe déjà, la valeur est remplacée. Il n'y a pas de doublon de clé dans un dictionnaire.

### Exemple corrigé 3 - Construction à partir de données

```python
def compter_occurrences(texte):
    """Construit un dictionnaire des occurrences de chaque caractère."""
    compteur = {}
    for c in texte:
        if c in compteur:
            compteur[c] = compteur[c] + 1
        else:
            compteur[c] = 1
    return compteur
```

- Donnée étudiée : `"abracadabra"`.
- Résultat obtenu : `{'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}`.

### Cas limites

- Clé de type mutable (liste) : `d[[1, 2]] = "x"` lève `TypeError: unhashable type: 'list'`.
- Dictionnaire vide : `len({})` vaut `0`, aucune clé n'existe.

---

## 5. P-DATA-CONSTR-03B : Itérer sur les éléments d’un dictionnaire

### Définition

Itérer sur un dictionnaire signifie parcourir ses éléments à l'aide d’une boucle `for`. Python offre plusieurs méthodes pour choisir ce que l'on parcourt.

### Formalisation

| Syntaxe | Ce qui est parcouru |
|---------|-------------------|
| `for k in d` | les clés |
| `for k in d.keys()` | les clés (explicite) |
| `for v in d.values()` | les valeurs |
| `for k, v in d.items()` | les couples (clé, valeur) |

### Exemple corrigé 1 - Parcours des clés

```python
exif = {"appareil": "Nikon D3500", "date": "2025-06-15", "iso": 400}

for cle in exif:
    print(cle)
# Affiche : appareil, date, iso (un par ligne)
```

### Exemple corrigé 2 - Parcours des valeurs

```python
for valeur in exif.values():
    print(valeur)
# Affiche : Nikon D3500, 2025-06-15, 400
```

### Exemple corrigé 3 - Parcours des couples (clé, valeur)

```python
for cle, valeur in exif.items():
    print(f"{cle} : {valeur}")
# Affiche :
# appareil : Nikon D3500
# date : 2025-06-15
# iso : 400
```

### Exemple corrigé 4 - Recherche d’une valeur

```python
def trouver_cle(d, valeur_cherchee):
    """Renvoie la première clé associée à la valeur cherchée, ou None."""
    for cle, valeur in d.items():
        if valeur == valeur_cherchee:
            return cle
    return None
```

- Donnée étudiée : `exif`, recherche de `400`.
- Résultat obtenu : `"iso"`.

### Cas limites

- Itération sur un dictionnaire vide : la boucle ne s'exécute pas.
- Modification du dictionnaire pendant l'itération : provoque une erreur `RuntimeError`. Il faut itérer sur une copie des clés si on veut modifier le dictionnaire.

---

## 6. P-DATA-CONSTR-03C : Utiliser les méthodes keys, values et items

### Définition

Les méthodes `keys()`, `values()` et `items()` d'un dictionnaire renvoient des objets vue (*view objects*) qui reflètent dynamiquement le contenu du dictionnaire. Contrairement à une liste, une vue n'est pas une copie : elle se met à jour automatiquement si le dictionnaire est modifié en dehors d'une itération.

### Formalisation

| Méthode | Type renvoyé | Contenu |
|---------|-------------|---------|
| `d.keys()` | `dict_keys` | toutes les clés |
| `d.values()` | `dict_values` | toutes les valeurs |
| `d.items()` | `dict_items` | tous les couples `(clé, valeur)` |

Ces objets sont itérables et supportent le test d'appartenance avec `in`, mais ne sont **pas indexables** : `d.keys()[0]` provoque une `TypeError`. Pour obtenir une liste, on écrit `list(d.keys())`.

### Exemple corrigé 1 — Extraire les clés d'un dictionnaire

```python
notes = {"Alice": 16, "Bob": 12, "Clara": 18}
cles = notes.keys()
print(cles)          # dict_keys(['Alice', 'Bob', 'Clara'])
print("Alice" in cles)  # True
```

- Donnée étudiée : `notes`, trois entrées.
- Résultat obtenu : un objet `dict_keys` contenant les trois prénoms.

### Exemple corrigé 2 — Calculer une moyenne avec values

```python
notes = {"Alice": 16, "Bob": 12, "Clara": 18}
total = sum(notes.values())
moyenne = total / len(notes)
print(moyenne)  # 15.333333333333334
```

- Donnée étudiée : `notes.values()` renvoie `dict_values([16, 12, 18])`.
- Résultat obtenu : la somme vaut 46, la moyenne vaut environ 15.33.

### Exemple corrigé 3 — Trouver le maximum avec items

```python
notes = {"Alice": 16, "Bob": 12, "Clara": 18}
meilleur_nom = ""
meilleure_note = -1
for nom, note in notes.items():
    if note > meilleure_note:
        meilleure_note = note
        meilleur_nom = nom
print(f"{meilleur_nom} : {meilleure_note}")  # Clara : 18
```

- Donnée étudiée : les couples `(nom, note)` via `items()`.
- Résultat obtenu : Clara avec 18.

### Exemple corrigé 4 — Vue dynamique

```python
d = {"x": 1, "y": 2}
vue = d.keys()
print(list(vue))  # ['x', 'y']
d["z"] = 3
print(list(vue))  # ['x', 'y', 'z']  — la vue reflète l'ajout
```

- Point clé : `vue` n'est pas une copie figée ; elle suit le dictionnaire.

### Cas limites

- Sur un dictionnaire vide, `d.keys()`, `d.values()` et `d.items()` renvoient des vues vides (itérables, longueur 0).
- Modifier le dictionnaire **pendant** une itération sur une vue provoque `RuntimeError`. Solution : itérer sur `list(d.keys())` si des modifications sont nécessaires.

---

## Synthèse

| Capacité | Structure | Opération clé |
|----------|-----------|---------------|
| P-DATA-CONSTR-01 | Tuple | `return a, b` |
| P-DATA-CONSTR-02B | Liste | `[expr for var in iterable]` |
| P-DATA-CONSTR-02C | Liste de listes | `matrice[i][j]` |
| P-DATA-CONSTR-03A | Dictionnaire | `d[cle] = valeur` |
| P-DATA-CONSTR-03B | Dictionnaire | `for k, v in d.items()` |
| P-DATA-CONSTR-03C | Dictionnaire | `d.keys()`, `d.values()`, `d.items()` |


## Situation-problème

Un programme de gestion de notes doit stocker, pour chaque élève, son nom et ses notes dans différentes matières. Quelle structure de données choisir et comment organiser les accès ?

## Activité d’entrée

Écrire une fonction Python qui reçoit deux nombres et renvoie à la fois leur somme et leur produit. Tester avec print(resultat[0], resultat[1]).

## Exercices

Exercices de manipulation de tuples, listes en compréhension, matrices et dictionnaires.

## Corrigé

Les corrigés détaillés sont dans P04_corrige_types_construits_complement.md.

## Erreurs fréquentes

- EF1 : confondre tuple (immutable) et liste (mutable) lors du retour de fonction.
- EF2 : oublier les crochets dans une compréhension de liste.
- EF3 : accéder à une clé inexistante d'un dictionnaire sans utiliser get().


## Remédiation

Exercice de remédiation : écrire une fonction min_max qui renvoie le minimum et le maximum d'une liste sous forme de tuple.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.

## Critères de réussite

Fonction renvoyant un tuple vérifiée. Compréhension de liste correcte. Matrice accessible par double index. Dictionnaire itéré avec keys/values/items.

Critère de validation : chaque réponse est vérifiable par un contrôle explicite.
