---
title: "P04 - Trace - Types construits complément"
level: "premiere"
sequence_id: "P04"
document_type: "trace"
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

# P04 - Trace écrite - Types construits complément

## Capacités officielles atomiques
- P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs
- P-DATA-CONSTR-02B : Construire un tableau par compréhension
- P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices
- P-DATA-CONSTR-03A : Construire une entrée de dictionnaire
- P-DATA-CONSTR-03B : Itérer sur les éléments d’un dictionnaire

---

## Méthode 1 - Écrire une fonction renvoyant un p-uplet (P-DATA-CONSTR-01)

**Principe** : une fonction peut renvoyer plusieurs valeurs en les séparant par des virgules après `return`. Python crée automatiquement un tuple.

**Modèle** :

```python
def statistiques(tableau):
    somme = sum(tableau)
    moyenne = somme / len(tableau)
    return somme, moyenne
```

**Déballage du résultat** :

```python
s, m = statistiques([10, 20, 30])
# s vaut 60, m vaut 20.0
```

**Exemple clé** :

```python
def division_euclidienne(a, b):
    return a // b, a % b

q, r = division_euclidienne(17, 5)
# q vaut 3, r vaut 2
```

**A retenir** : `return a, b` est identique a `return (a, b)`. Le tuple est immuable.

---

## Méthode 2 - Construire un tableau par compréhension (P-DATA-CONSTR-02B)

**Principe** : une liste par compréhension construit un nouveau tableau en une ligne lisible.

**Modèle** :

```python
resultat = [expression for variable in iterable]
resultat = [expression for variable in iterable if condition]
```

**Exemples clés** :

```python
carres = [x ** 2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

mots = ["nsi", "python", "algo"]
majuscules = [m.upper() for m in mots]
# ["NSI", "PYTHON", "ALGO"]

positifs = [x for x in [-3, 5, -1, 8] if x > 0]
# [5, 8]
```

**A retenir** : rester sur des formes simples et lisibles. Si l'expression est complexe, utiliser une boucle classique.

---

## Méthode 3 - Utiliser des tableaux de tableaux pour les matrices (P-DATA-CONSTR-02C)

**Principe** : une matrice est une liste de listes. Pas de NumPy. Accès par `matrice[i][j]` (ligne i, colonne j).

**Modèle** :

```python
matrice = [
    [1, 2, 3],
    [4, 5, 6],
]
# matrice[0][2] vaut 3 (ligne 0, colonne 2)
# len(matrice) donne le nombre de lignes : 2
# len(matrice[0]) donne le nombre de colonnes : 3
```

**Initialisation correcte** :

```python
zeros = [[0 for j in range(colonnes)] for i in range(lignes)]
```

**Erreur a eviter** : `[[0]*p]*n` partage les memes lignes en memoire.

**Exemple clé - parcours** :

```python
for i in range(len(matrice)):
    for j in range(len(matrice[i])):
        print(matrice[i][j], end=" ")
    print()
```

---

## Méthode 4 - Construire une entrée de dictionnaire (P-DATA-CONSTR-03A)

**Principe** : un dictionnaire associe des clés (immuables) a des valeurs. On ajoute ou modifie une entrée avec `d[cle] = valeur`.

**Modèle** :

```python
d = {}
d["nom"] = "valeur"     # ajout
d["nom"] = "autre"      # modification (la clé existait déjà)
```

**Exemple clé - métadonnées EXIF fictives** :

```python
exif = {}
exif["appareil"] = "Canon EOS"
exif["date"] = "2025-03-20"
exif["resolution"] = (4000, 3000)
exif["iso"] = 200
```

**Exemple clé - comptage** :

```python
def compter(texte):
    freq = {}
    for c in texte:
        if c in freq:
            freq[c] = freq[c] + 1
        else:
            freq[c] = 1
    return freq
```

**A retenir** : les clés doivent etre immuables (str, int, tuple). Les listes ne sont pas des clés valides.

---

## Méthode 5 - Itérer sur les éléments d’un dictionnaire (P-DATA-CONSTR-03B)

**Principe** : on peut parcourir les clés, les valeurs ou les couples (clé, valeur).

**Modèle** :

| Code | Parcourt |
|------|----------|
| `for k in d` | les clés |
| `for k in d.keys()` | les clés (explicite) |
| `for v in d.values()` | les valeurs |
| `for k, v in d.items()` | les couples (clé, valeur) |

**Exemple clé** :

```python
exif = {"appareil": "Canon EOS", "date": "2025-03-20", "iso": 200}

for cle, valeur in exif.items():
    print(f"{cle} -> {valeur}")
```

**A retenir** : ne pas modifier un dictionnaire pendant qu'on itère dessus. Itération sur dictionnaire vide : la boucle ne s'exécute pas.

---

## Tableau récapitulatif

| Capacité | Structure | Syntaxe essentielle |
|----------|-----------|-------------------|
| P-DATA-CONSTR-01 | Tuple | `return a, b` |
| P-DATA-CONSTR-02B | Liste | `[expr for x in iterable]` |
| P-DATA-CONSTR-02C | Liste de listes | `m[i][j]` |
| P-DATA-CONSTR-03A | Dictionnaire | `d[cle] = valeur` |
| P-DATA-CONSTR-03B | Dictionnaire | `for k, v in d.items()` |


## Objectifs


## Prérequis


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

- Critère de réussite : la fonction renvoie un tuple vérifiable par déstructuration.
- Critère de validation : la compréhension de liste produit le résultat attendu.
- Observable : le dictionnaire est itéré avec keys(), values() et items() correctement.


## Séance(s) correspondante(s)

Séance dédiée.
