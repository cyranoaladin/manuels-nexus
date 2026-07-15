---
title: "P04 - Corrige - Types construits complément"
level: "premiere"
sequence_id: "P04"
document_type: "corrige"
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

# P04 - Corrigé - Types construits complément

## Capacités officielles atomiques
- P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs
- P-DATA-CONSTR-02B : Construire un tableau par compréhension
- P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices
- P-DATA-CONSTR-03A : Construire une entrée de dictionnaire
- P-DATA-CONSTR-03B : Itérer sur les éléments d’un dictionnaire

---

## Corrigé du TD

### Exercice 1 - Fonction renvoyant un p-uplet (P-DATA-CONSTR-01)

**1a.** La valeur renvoyée est de type `tuple`. Plus précisément, c'est un tuple de trois éléments : `(8, 15, 11.25)`.

**1b.**

- `a = 8` (minimum)
- `b = 15` (maximum)
- `c = 11.25` (moyenne : (12 + 8 + 15 + 10) / 4 = 45 / 4 = 11.25)

**1c.**

```python
def extremes(a, b):
    if a <= b:
        return a, b
    else:
        return b, a
```

**1d.** L'appel `analyser_notes([])` provoque une erreur `IndexError` sur la ligne `mini = notes[0]` car le tableau est vide et l'indice 0 n'existe pas. De plus, `len(notes)` vaut 0, ce qui provoquerait une division par zéro. La précondition est : le tableau doit être non vide.

---

### Exercice 2 - Tableau par compréhension (P-DATA-CONSTR-02B)

**2a.**

- `L1 = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]`
- `L2 = [3, 6, 9, 12, 15]`
- `L3 = ['P', 'Y', 'T', 'H', 'O', 'N']`

**2b.**

`L4 = [3, 6, 9, 12, 15, 18]` (les multiples de 3 entre 1 et 20).

**2c.**

```python
cubes = [x ** 3 for x in range(1, 9)]
```

**2d.**

```python
positives = [t for t in temperatures if t > 0]
# Résultat : [15.5, 22.0, 18.3, 30.2]
```

**2e.** `[0 for _ in range(0)]` produit `[]` (liste vide). `range(0)` génère une séquence vide, donc la compréhension n'itère sur aucun élément.

---

### Exercice 3 - Matrices (P-DATA-CONSTR-02C)

**3a.**

- `M[0][2] = 8` (ligne 0, colonne 2)
- `M[1][1] = 7` (ligne 1, colonne 1)
- `M[2][0] = 9` (ligne 2, colonne 0)

**3b.** `M` possède 3 lignes et 3 colonnes.

- Nombre de lignes : `len(M)` qui vaut `3`.
- Nombre de colonnes : `len(M[0])` qui vaut `3`.

**3c.** Trace d'exécution de `somme_diagonale(M)` :

| Étape | `i` | `matrice[i][i]` | `total` |
|-------|-----|-----------------|---------|
| Init  | -   | -               | 0       |
| 1     | 0   | 5               | 5       |
| 2     | 1   | 7               | 12      |
| 3     | 2   | 6               | 18      |

Résultat renvoyé : `18`.

**3d.** Le code `grille = [[0] * 3] * 3` crée une liste contenant 3 fois la **même** sous-liste (même objet en mémoire). Modifier `grille[0][0]` modifie donc les trois lignes simultanément.

Affichage : `[[1, 0, 0], [1, 0, 0], [1, 0, 0]]`.

Correction :

```python
grille = [[0 for j in range(3)] for i in range(3)]
grille[0][0] = 1
# Résultat correct : [[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

---

### Exercice 4 - Construire une entrée de dictionnaire (P-DATA-CONSTR-03A)

**4a.**

```python
photo = {}
photo["marque"] = "Sony"
photo["modele"] = "A7III"
photo["date_prise"] = "2025-07-01"
photo["taille"] = (6000, 4000)
```

**4b.** `photo["taille"]` affiche `(6000, 4000)`. C'est un `tuple` de deux entiers.

**4c.** Après `photo["iso"] = 100` puis `photo["iso"] = 200`, la clé `"iso"` est associée à `200`. La seconde affectation remplace la valeur précédente. Un dictionnaire ne peut pas contenir deux entrées avec la même clé.

**4d.** L'instruction `d[[1, 2]] = "coordonnees"` provoque `TypeError: unhashable type: 'list'`. Les clés d’un dictionnaire doivent être de type immuable (hashable). Une liste est mutable et ne peut donc pas servir de clé. On pourrait utiliser un tuple a la place : `d[(1, 2)] = "coordonnees"`.

---

### Exercice 5 - Itérer sur un dictionnaire (P-DATA-CONSTR-03B)

**5a.**

Bloc A affiche (une par ligne) :
```
temperature
humidite
vent
pression
```

Bloc B affiche :
```
22
65
15
1013
```

Bloc C affiche :
```
temperature = 22
humidite = 65
vent = 15
pression = 1013
```

**5b.**

```python
total = 0
for val in meteo.values():
    total = total + val
# total vaut 22 + 65 + 15 + 1013 = 1115
```

**5c.**

```python
def cles_superieures(d, seuil):
    resultat = []
    for cle, valeur in d.items():
        if valeur > seuil:
            resultat.append(cle)
    return resultat
```

Exemple : `cles_superieures(meteo, 20)` renvoie `["temperature", "humidite", "pression"]`.

**5d.** Itérer sur un dictionnaire vide `{}` ne provoque pas d'erreur. La boucle `for` ne s'exécute simplement pas car il n'y a aucun élément à parcourir.

---

## Corrigé de l'évaluation

### Question 1 - P-DATA-CONSTR-01 (4 points)

**1a.** (1 pt) La valeur renvoyée par `encadrer(5)` est de type `tuple`. C'est le tuple `(4, 6)`.

**1b.** (1 pt) `a = 9`, `b = 11`.

**1c.** (2 pts)

```python
def aire_perimetre(longueur, largeur):
    aire = longueur * largeur
    perimetre = 2 * (longueur + largeur)
    return aire, perimetre
```

Pour `longueur = 5` et `largeur = 3` : `aire_perimetre(5, 3)` renvoie `(15, 16)`.

---

### Question 2 - P-DATA-CONSTR-02B (4 points)

**2a.** (2 pts)

- `L1 = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]`
- `L2 = [5, 10, 15]`

**2b.** (2 pts)

```python
notes = [8, 12, 5, 16, 10, 3]
reussies = [n for n in notes if n >= 10]
# Résultat : [12, 16, 10]
```

---

### Question 3 - P-DATA-CONSTR-02C (4 points)

**3a.** (1 pt) `grille[1][2] = 5`, `grille[2][0] = 4`.

**3b.** (1 pt) Nombre de lignes : `len(grille)` (vaut 3). Nombre de colonnes : `len(grille[0])` (vaut 3).

**3c.** (2 pts)

```python
def somme_ligne(matrice, i):
    total = 0
    for j in range(len(matrice[i])):
        total = total + matrice[i][j]
    return total
```

Pour la ligne 0 de `grille` : `somme_ligne(grille, 0)` renvoie `2 + 7 + 1 = 10`.

---

### Question 4 - P-DATA-CONSTR-03A (4 points)

**4a.** (2 pts)

```python
eleve = {}
eleve["nom"] = "Martin"
eleve["prenom"] = "Léa"
eleve["age"] = 16
eleve["classe"] = "1NSI"
```

**4b.** (1 pt) L'instruction `eleve["age"] = 17` remplace la valeur 16 par 17. La nouvelle valeur de `eleve["age"]` est `17`.

**4c.** (1 pt) Une liste est un type mutable et ne peut pas être utilisée comme clé de dictionnaire. Python exige des clés hashables (immuables). L'erreur levée est `TypeError: unhashable type: 'list'`.

---

### Question 5 - P-DATA-CONSTR-03B (4 points)

**5a.** (1 pt) Le code affiche :

```
Alice
Bob
Clara
```

**5b.** (1 pt)

```python
for nom, score in scores.items():
    print(f"{nom} a obtenu {score}")
```

**5c.** (2 pts)

```python
def meilleur_score(d):
    meilleur_nom = None
    meilleur_val = None
    for nom, score in d.items():
        if meilleur_val is None or score > meilleur_val:
            meilleur_nom = nom
            meilleur_val = score
    return meilleur_nom, meilleur_val
```

Avec `scores` : `meilleur_score(scores)` renvoie `("Clara", 91)`.

---

## Corrigé du TP

### Exercice 1

**1a.**

```python
def statistiques(tableau):
    mini = tableau[0]
    maxi = tableau[0]
    somme = 0
    for val in tableau:
        if val < mini:
            mini = val
        if val > maxi:
            maxi = val
        somme = somme + val
    moyenne = somme / len(tableau)
    return mini, maxi, moyenne
```

**1b.**

```python
def secondes_vers_hms(total_secondes):
    heures = total_secondes // 3600
    reste = total_secondes % 3600
    minutes = reste // 60
    secondes = reste % 60
    return heures, minutes, secondes
```

**1c.** `statistiques([])` provoque `IndexError` car `tableau[0]` est inaccessible sur un tableau vide.

---

### Exercice 2

**2a.**

```python
carres = [x ** 2 for x in range(10)]
multiples_7 = [k for k in range(0, 51) if k % 7 == 0]
longueurs = [len(m) for m in mots]
```

**2b.**

```python
pairs_carres = [n ** 2 for n in nombres if n % 2 == 0]
```

**2c.**

```python
def initiales(prenoms):
    return [p[0].upper() for p in prenoms]
```

---

### Exercice 3

**3a.**

```python
identite = [[1 if i == j else 0 for j in range(3)] for i in range(3)]
```

**3b.**

```python
def transposer(matrice):
    nb_lignes = len(matrice)
    nb_colonnes = len(matrice[0])
    resultat = [[0 for j in range(nb_lignes)] for i in range(nb_colonnes)]
    for i in range(nb_lignes):
        for j in range(nb_colonnes):
            resultat[j][i] = matrice[i][j]
    return resultat
```

**3c.**

```python
def rechercher(matrice, valeur):
    for i in range(len(matrice)):
        for j in range(len(matrice[i])):
            if matrice[i][j] == valeur:
                return (i, j)
    return None
```

---

### Exercice 4

**4a.**

```python
film = {}
film["titre"] = "Interstellar"
film["realisateur"] = "Christopher Nolan"
film["annee"] = 2014
film["duree_min"] = 169
film["genres"] = ["science-fiction", "drame"]
```

**4b.**

```python
def compter_mots(phrase):
    mots = phrase.split()
    compteur = {}
    for mot in mots:
        if mot in compteur:
            compteur[mot] = compteur[mot] + 1
        else:
            compteur[mot] = 1
    return compteur
```

**4c.**

```python
def creer_exif(appareil, date, largeur, hauteur, iso):
    exif = {}
    exif["appareil"] = appareil
    exif["date"] = date
    exif["resolution"] = (largeur, hauteur)
    exif["iso"] = iso
    return exif
```

---

### Exercice 5

**5a.**

```python
def afficher_fiche(d):
    for cle, valeur in d.items():
        print(f"{cle} : {valeur}")
```

**5b.**

```python
def filtrer_valeurs(d, seuil):
    resultat = {}
    for cle, valeur in d.items():
        if valeur >= seuil:
            resultat[cle] = valeur
    return resultat
```

**5c.**

```python
def inverser_dict(d):
    resultat = {}
    for cle, valeur in d.items():
        resultat[valeur] = cle
    return resultat
```


## Objectifs


## Prérequis


## Situation-problème

Un programme de gestion de notes doit stocker, pour chaque élève, son nom et ses notes dans différentes matières. Quelle structure de données choisir et comment organiser les accès ?

## Activité d’entrée

Écrire une fonction Python qui reçoit deux nombres et renvoie à la fois leur somme et leur produit. Tester avec print(resultat[0], resultat[1]).

## Exercices

Exercices de manipulation de tuples, listes en compréhension, matrices et dictionnaires.

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

- Critère de réussite : la fonction renvoie un tuple vérifiable par déstructuration.
- Critère de validation : la compréhension de liste produit le résultat attendu.
- Observable : le dictionnaire est itéré avec keys(), values() et items() correctement.


## Séance(s) correspondante(s)

Séance dédiée.

### Corrigé exercice 1

**Méthode** : on écrit une fonction qui renvoie un tuple contenant les deux valeurs calculées.
La fonction `min_max(lst)` renvoie `(1, 9)` pour la liste `[3, 1, 9, 5]`. Le résultat vaut `(min, max)` sous forme de tuple Python.

















### Corrigé exercice 2

Réponse détaillée avec justification.

La compréhension donne `[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]` pour les carrés de 0 à 9.

### Corrigé exercice 3

Réponse détaillée avec justification.

L'élément `matrice[1][2]` vaut `5` et `somme_diagonale` renvoie `18`.

### Corrigé exercice 4

Réponse détaillée avec justification.

Le dictionnaire donne `{'titre': 'Interstellar', 'realisateur': 'Christopher Nolan', 'annee': 2014}`.

### Corrigé exercice 5

Réponse détaillée avec justification.

`d.keys()` renvoie `dict_keys(['temperature', 'humidite', 'vent', 'pression'])` (une vue, pas une liste) pour le dictionnaire météo.

### Corrigé exercice 6

Réponse détaillée avec justification.

La fonction renvoie `(8, 15, 11.25)` pour la liste `[12, 8, 15, 10]`.

### Corrigé exercice 7

Réponse détaillée avec justification.

La compréhension filtrée donne `[12, 16, 10]` pour les notes supérieures ou égales à 10.

### Corrigé exercice 8

Réponse détaillée avec justification.

La fonction `inverser_dict` renvoie `{'a': 1, 'b': 2}` pour l'entrée `{1: 'a', 2: 'b'}`.

