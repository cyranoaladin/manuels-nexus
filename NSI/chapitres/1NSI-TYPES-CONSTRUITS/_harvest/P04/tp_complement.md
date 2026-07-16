---
title: "P04 - TP - Types construits complément"
level: "premiere"
sequence_id: "P04"
document_type: "tp"
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

# P04 - Travaux pratiques - Types construits complément

## Capacités officielles atomiques
- P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs
- P-DATA-CONSTR-02B : Construire un tableau par compréhension
- P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices
- P-DATA-CONSTR-03A : Construire une entrée de dictionnaire
- P-DATA-CONSTR-03B : Itérer sur les éléments d’un dictionnaire

## Consignes générales
- Tester chaque fonction avec les exemples fournis.
- Ajouter au moins un test supplémentaire de votre choix.
- Tester les cas limites mentionnés.

---

## Exercice 1 - Fonction renvoyant un p-uplet (P-DATA-CONSTR-01)

### 1a. Statistiques de base

Écrire une fonction `statistiques(tableau)` qui prend un tableau non vide d'entiers et renvoie le tuple `(minimum, maximum, moyenne)`.

```python
def statistiques(tableau):
    # A compléter
    pass

# Tests attendus :
assert statistiques([10, 20, 30]) == (10, 30, 20.0)
assert statistiques([5]) == (5, 5, 5.0)
assert statistiques([-3, 0, 3]) == (-3, 3, 0.0)
```

### 1b. Conversion de durée

Écrire une fonction `secondes_vers_hms(total_secondes)` qui convertit un nombre de secondes en un tuple `(heures, minutes, secondes)`.

```python
def secondes_vers_hms(total_secondes):
    # A compléter
    pass

# Tests attendus :
assert secondes_vers_hms(3661) == (1, 1, 1)
assert secondes_vers_hms(0) == (0, 0, 0)
assert secondes_vers_hms(59) == (0, 0, 59)
assert secondes_vers_hms(3600) == (1, 0, 0)
```

### Question 1c - Cas limite

Que se passe-t-il si on appelle `statistiques([])` ? Ajouter un commentaire dans votre code pour expliquer.

---

## Exercice 2 - Tableau par compréhension (P-DATA-CONSTR-02B)

### 2a. Compréhensions simples

Écrire chacune des listes suivantes sous forme de compréhension :

```python
# Liste des carrés de 0 à 9
carres = # A compléter

# Liste des multiples de 7 entre 0 et 50 (inclus)
multiples_7 = # A compléter

# Liste des longueurs des mots
mots = ["bonjour", "nsi", "python", "ok"]
longueurs = # A compléter
```

Tests attendus :

```python
assert carres == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
assert multiples_7 == [0, 7, 14, 21, 28, 35, 42, 49]
assert longueurs == [7, 3, 6, 2]
```

### Question 2b - Compréhension avec filtre

Écrire une compréhension qui, a partir d’une liste de nombres, ne conserve que les nombres pairs et les met au carré.

```python
nombres = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
pairs_carres = # A compléter

assert pairs_carres == [4, 16, 36, 64, 100]
```

### Question 2c - Application

Écrire une fonction `initiales(prenoms)` qui prend une liste de prénoms et renvoie la liste de leurs initiales (première lettre en majuscule), en utilisant une compréhension.

```python
def initiales(prenoms):
    # A compléter avec une compréhension
    pass

assert initiales(["alice", "bob", "charlie"]) == ["A", "B", "C"]
assert initiales([]) == []
```

---

## Exercice 3 - Matrices (P-DATA-CONSTR-02C)

### 3a. Création et accès

Créer une matrice `identite` de taille 3x3 (matrice identité : des 1 sur la diagonale, des 0 ailleurs) en utilisant une compréhension de listes imbriquée.

```python
identite = # A compléter avec une compréhension

# Vérifications :
assert identite[0][0] == 1
assert identite[0][1] == 0
assert identite[1][1] == 1
assert identite[2][2] == 1
assert len(identite) == 3
assert len(identite[0]) == 3
```

### Question 3b - Transposition

Écrire une fonction `transposer(matrice)` qui renvoie la transposée d’une matrice (les lignes deviennent les colonnes).

```python
def transposer(matrice):
    # A compléter
    pass

M = [[1, 2, 3], [4, 5, 6]]
T = transposer(M)
assert T == [[1, 4], [2, 5], [3, 6]]
```

### Question 3c - Recherche dans une matrice

Écrire une fonction `rechercher(matrice, valeur)` qui renvoie le tuple `(ligne, colonne)` de la première occurrence de `valeur` dans la matrice, ou `None` si la valeur est absente.

```python
def rechercher(matrice, valeur):
    # A compléter
    pass

M = [[5, 3, 8], [1, 7, 4], [9, 2, 6]]
assert rechercher(M, 7) == (1, 1)
assert rechercher(M, 9) == (2, 0)
assert rechercher(M, 10) is None
```

---

## Exercice 4 - Construire des entrées de dictionnaire (P-DATA-CONSTR-03A)

### 4a. Construction pas à pas

Construire un dictionnaire `film` contenant les métadonnées fictives d’un film : `"titre"`, `"realisateur"`, `"annee"`, `"duree_min"`, `"genres"` (liste de genres).

```python
film = {}
# A compléter : ajouter les 5 entrées

assert film["titre"] == "Interstellar"
assert film["annee"] == 2014
assert "science-fiction" in film["genres"]
```

### Question 4b - Compteur d'occurrences

Écrire une fonction `compter_mots(phrase)` qui prend une phrase (chaîne de caractères) et renvoie un dictionnaire associant chaque mot à son nombre d'occurrences.

```python
def compter_mots(phrase):
    # A compléter
    pass

resultat = compter_mots("le chat et le chien et le poisson")
assert resultat["le"] == 3
assert resultat["et"] == 2
assert resultat["chat"] == 1
```

### 4c. Métadonnées EXIF

Écrire une fonction `creer_exif(appareil, date, largeur, hauteur, iso)` qui renvoie un dictionnaire avec les clés `"appareil"`, `"date"`, `"resolution"` (tuple largeur, hauteur) et `"iso"`.

```python
def creer_exif(appareil, date, largeur, hauteur, iso):
    # A compléter
    pass

e = creer_exif("Nikon", "2025-06-15", 6000, 4000, 400)
assert e["resolution"] == (6000, 4000)
assert e["iso"] == 400
```

---

## Exercice 5 - Itérer sur un dictionnaire (P-DATA-CONSTR-03B)

### 5a. Affichage formaté

Écrire une fonction `afficher_fiche(d)` qui prend un dictionnaire et affiche chaque entrée sous la forme `cle : valeur`, une par ligne, en utilisant `d.items()`.

```python
def afficher_fiche(d):
    # A compléter
    pass

# Test visuel :
afficher_fiche({"nom": "Dupont", "age": 17, "classe": "1NSI"})
# Doit afficher :
# nom : Dupont
# age : 17
# classe : 1NSI
```

### Question 5b - Filtrage par valeur

Écrire une fonction `filtrer_valeurs(d, seuil)` qui renvoie un nouveau dictionnaire ne contenant que les entrées dont la valeur est supérieure ou égale à `seuil`.

```python
def filtrer_valeurs(d, seuil):
    # A compléter
    pass

notes = {"maths": 14, "nsi": 18, "anglais": 9, "svt": 12}
resultat = filtrer_valeurs(notes, 12)
assert resultat == {"maths": 14, "nsi": 18, "svt": 12}
assert filtrer_valeurs({}, 10) == {}
```

### Question 5c - Inversion clé-valeur

Écrire une fonction `inverser_dict(d)` qui renvoie un nouveau dictionnaire ou les clés et valeurs sont inversées.

```python
def inverser_dict(d):
    # A compléter
    pass

assert inverser_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
assert inverser_dict({}) == {}
```


## Objectifs


## Prérequis


## Situation-problème

Un programme de gestion de notes doit stocker, pour chaque élève, son nom et ses notes dans différentes matières. Quelle structure de données choisir et comment organiser les accès ?

## Activité d’entrée

Écrire une fonction Python qui reçoit deux nombres et renvoie à la fois leur somme et leur produit. Tester avec print(resultat[0], resultat[1]).

## Exemple

Écriture collective d'une fonction coordonnees() renvoyant un tuple (x, y) et d'une compréhension [i**2 for i in range(5)].

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

- Critère de réussite : la fonction renvoie un tuple vérifiable par déstructuration.
- Critère de validation : la compréhension de liste produit le résultat attendu.
- Observable : le dictionnaire est itéré avec keys(), values() et items() correctement.


## Séance(s) correspondante(s)

Séance dédiée.

## Exemple d’exécution

Exécuter chaque fonction et vérifier que le type de retour est correct (tuple, liste, dictionnaire).

## Livrable vérifiable

Module Python contenant les fonctions de manipulation de tuples, listes en compréhension, matrices et dictionnaires.

## Consigne technique détaillée

Utiliser les constructions Python appropriées : return (a, b), [x for x in ...], tab[i][j], d[cle] = val.

