---
title: "P04 - TD - Types construits complément"
level: "premiere"
sequence_id: "P04"
document_type: "td"
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

# P04 - Travaux dirigés - Types construits complément

## Capacités officielles atomiques
- P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs
- P-DATA-CONSTR-02B : Construire un tableau par compréhension
- P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices
- P-DATA-CONSTR-03A : Construire une entrée de dictionnaire
- P-DATA-CONSTR-03B : Itérer sur les éléments d’un dictionnaire
- P-DATA-CONSTR-03C : Utiliser les méthodes keys, values et items

---

## Exercice 1 - Fonction renvoyant un p-uplet (P-DATA-CONSTR-01)

On considère la fonction suivante :

```python
def analyser_notes(notes):
    mini = notes[0]
    maxi = notes[0]
    somme = 0
    for n in notes:
        if n < mini:
            mini = n
        if n > maxi:
            maxi = n
        somme = somme + n
    moyenne = somme / len(notes)
    return mini, maxi, moyenne
```

**Question 1a.** Donner le type de la valeur renvoyée par `analyser_notes([12, 8, 15, 10])`.

**Question 1b.** Déterminer les valeurs de `a`, `b` et `c` après l’exécution de :

```python
a, b, c = analyser_notes([12, 8, 15, 10])
```

**Question 1c.** Écrire sur papier une fonction `extremes(a, b)` qui renvoie le tuple `(plus_petit, plus_grand)` de deux nombres `a` et `b`.

**Question 1d.** Que se passe-t-il si on appelle `analyser_notes([])` ? Quelle précondition faudrait-il vérifier ?

---

## Exercice 2 - Tableau par compréhension (P-DATA-CONSTR-02B)

**Question 2a.** Déterminer le contenu de chaque liste :

```python
L1 = [x ** 2 for x in range(10)]
L2 = [k * 3 for k in range(1, 6)]
L3 = [c.upper() for c in "python"]
```

**Question 2b.** Déterminer le contenu de la liste avec filtre :

```python
L4 = [n for n in range(1, 21) if n % 3 == 0]
```

**Question 2c.** Écrire sur papier une compréhension qui produit la liste des cubes des entiers de 1 à 8, soit `[1, 8, 27, 64, 125, 216, 343, 512]`.

**Question 2d.** On donne `temperatures = [15.5, 22.0, 18.3, -1.0, 30.2]`. Écrire une compréhension qui ne garde que les températures strictement positives.

**Question 2e.** Que produit `[0 for _ in range(0)]` ? Justifier.

---

## Exercice 3 - Matrices comme tableaux de tableaux (P-DATA-CONSTR-02C)

On donne la matrice suivante :

```python
M = [
    [5, 3, 8],
    [1, 7, 4],
    [9, 2, 6],
]
```

**Question 3a.** Donner la valeur de `M[0][2]`, `M[1][1]` et `M[2][0]`.

**Question 3b.** Combien de lignes et de colonnes possède `M` ? Écrire les expressions Python qui donnent ces valeurs.

**Question 3c.** Écrire sur papier la trace d'exécution (valeurs de `i`, `j` et `total`) de la fonction suivante appliquée à `M` :

```python
def somme_diagonale(matrice):
    total = 0
    for i in range(len(matrice)):
        total = total + matrice[i][i]
    return total
```

**Question 3d.** On exécute le code suivant. Expliquer pourquoi le résultat est incorrect et proposer une correction.

```python
grille = [[0] * 3] * 3
grille[0][0] = 1
print(grille)
```

---

## Exercice 4 - Construire une entrée de dictionnaire (P-DATA-CONSTR-03A)

On souhaite stocker les métadonnées EXIF fictives d’une photographie.

**Question 4a.** Compléter le code pour construire le dictionnaire `photo` contenant les entrées suivantes : `"marque"` associée à `"Sony"`, `"modele"` associée à `"A7III"`, `"date_prise"` associée à `"2025-07-01"`, `"taille"` associée au tuple `(6000, 4000)`.

```python
photo = {}
photo[______] = ______
photo[______] = ______
photo[______] = ______
photo[______] = ______
```

**Question 4b.** Qu'affiche `photo["taille"]` ? De quel type est cette valeur ?

**Question 4c.** On exécute `photo["iso"] = 100` puis `photo["iso"] = 200`. Que contient `photo["iso"]` ? Expliquer.

**Question 4d.** Expliquer pourquoi le code suivant provoque une erreur :

```python
d = {}
d[[1, 2]] = "coordonnees"
```

---

## Exercice 5 - Itérer sur un dictionnaire (P-DATA-CONSTR-03B, P-DATA-CONSTR-03C)

On donne le dictionnaire suivant :

```python
meteo = {
    "temperature": 22,
    "humidite": 65,
    "vent": 15,
    "pression": 1013,
}
```

**Question 5a.** Écrire ce qu'affiche chacun des trois blocs :

```python
# Bloc A
for cle in meteo:
    print(cle)

# Bloc B
for val in meteo.values():
    print(val)

# Bloc C
for cle, val in meteo.items():
    print(f"{cle} = {val}")
```

**Question 5b.** Écrire sur papier une boucle qui calcule la somme de toutes les valeurs du dictionnaire `meteo`.

**Question 5c.** Écrire sur papier une fonction `cles_superieures(d, seuil)` qui renvoie la liste des clés dont la valeur associée est strictement supérieure à `seuil`.

**Question 5d.** Que se passe-t-il si on itère sur un dictionnaire vide `{}` ? Justifier.


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

### Exercice 1 — Retour de tuple

**Donnée** : On dispose d'une liste de températures relevées sur une journée, par exemple `temps = [12.5, 14.0, 18.3, 21.7, 19.2, 15.8]`.
**Consigne** : Écrire une fonction `resume_temperatures(temps)` qui renvoie un tuple `(moyenne, amplitude)` où `moyenne` est la moyenne des températures et `amplitude` est l'écart entre la température maximale et minimale. Utiliser la déstructuration `moy, amp = resume_temperatures(temps)` pour vérifier le résultat.
**Livrable** : Le code de la fonction, un appel avec déstructuration et l'affichage des deux valeurs.
**Corrigé** : Le corrigé détaillé se trouve dans le fichier corrigé complément, exercice 1.

### Exercice 2 — Compréhension de liste

**Donnée** : On dispose d'une liste de mots `mots = ["Python", "est", "un", "langage", "puissant", "et", "élégant"]`.
**Consigne** : En une seule compréhension de liste, construire une nouvelle liste contenant uniquement les mots dont la longueur est strictement supérieure à 3, convertis en majuscules. Puis, en une seconde compréhension, construire la liste des longueurs de tous les mots originaux.
**Livrable** : Les deux compréhensions de liste et leur résultat affiché.
**Corrigé** : Voir la correction complète dans le corrigé complément (exercice 2).

### Exercice 3 — Matrice 2D

**Donnée** : On modélise une grille de jeu de morpion par une matrice 3×3 initialisée à `" "` (espace). Après quelques coups, la grille est : `grille = [["X", "O", "X"], [" ", "X", "O"], ["O", " ", "X"]]`.
**Consigne** : Écrire une fonction `compter_symbole(grille, symbole)` qui parcourt la matrice et renvoie le nombre d'occurrences du symbole donné. Puis écrire une fonction `diagonale_principale(grille)` qui renvoie la liste des éléments sur la diagonale principale (indices `[0][0]`, `[1][1]`, `[2][2]`).
**Livrable** : Le code des deux fonctions, les appels de test et les résultats attendus.
**Corrigé** : Corrigé avec justification : fichier corrigé complément, exercice 3.

### Exercice 4 — Construction d'un dictionnaire

**Donnée** : On dispose de deux listes parallèles : `pays = ["France", "Allemagne", "Espagne", "Italie"]` et `capitales = ["Paris", "Berlin", "Madrid", "Rome"]`.
**Consigne** : Construire un dictionnaire `atlas` associant chaque pays à sa capitale en utilisant `zip()`. Puis ajouter manuellement l'entrée `"Portugal": "Lisbonne"`. Enfin, construire un dictionnaire inversé `atlas_inv` associant chaque capitale à son pays, en utilisant une compréhension de dictionnaire.
**Livrable** : Le dictionnaire `atlas`, l'ajout, le dictionnaire `atlas_inv` et l'affichage des deux.
**Corrigé** : Solution détaillée : exercice 4 du corrigé complément associé.

### Exercice 5 — Parcours avec keys(), values() et items()

**Donnée** : On dispose du dictionnaire `stock = {"pommes": 45, "bananes": 12, "cerises": 0, "dattes": 30, "figues": 7}`.
**Consigne** : (a) Afficher toutes les clés du dictionnaire en utilisant `.keys()`. (b) Calculer le stock total en sommant les valeurs obtenues via `.values()`. (c) En utilisant `.items()`, afficher uniquement les fruits dont le stock est strictement positif sous la forme `"fruit : quantité unités"`. (d) Construire une liste `rupture` contenant les noms des fruits dont le stock vaut 0.
**Livrable** : Le code de chaque parcours et les résultats affichés.
**Corrigé** : Consulter le corrigé complément pour la solution de l'exercice 5.

### Exercice 6 — Débogage type mutable

**Donnée** : Le code suivant contient un bug lié à la mutabilité des listes :
```python
def creer_grille(n, valeur=[]):
    grille = []
    for i in range(n):
        grille.append(valeur)
    return grille

g = creer_grille(3)
g[0].append("X")
print(g)  # Résultat surprenant !
```
**Consigne** : (a) Exécuter mentalement le code et prédire le résultat de `print(g)`. (b) Expliquer pourquoi toutes les lignes sont modifiées simultanément. (c) Corriger le code pour que chaque ligne soit une liste indépendante. Tester la version corrigée.
**Livrable** : La prédiction, l'explication du bug (aliasing de référence) et le code corrigé.
**Corrigé** : La réponse attendue et sa justification sont dans le corrigé complément, exercice 6.

### Exercice 7 — Cas limites : liste vide et clé absente

**Donnée** : On dispose de la fonction suivante et du dictionnaire `notes = {"Alice": 15, "Bob": 12}` :
```python
def moyenne_liste(lst):
    return sum(lst) / len(lst)
```
**Consigne** : (a) Appeler `moyenne_liste([])` et constater l'erreur. Modifier la fonction pour qu'elle renvoie `None` si la liste est vide. (b) Accéder à `notes["Charlie"]` et constater l'erreur. Réécrire l'accès en utilisant `.get("Charlie", "inconnu")`. (c) Écrire un test avec `if cle in dico` avant d'accéder à la valeur. Expliquer la différence entre les trois approches.
**Livrable** : La fonction corrigée, les trois méthodes d'accès sécurisé et une phrase comparative.
**Corrigé** : Exercice 7 : solution dans le corrigé complément (avec trace d'exécution).

### Exercice 8 — Transfert liste vers dictionnaire et inversement

**Donnée** : On dispose d'une liste d'élèves avec leurs notes : `resultats = [("Alice", 15), ("Bob", 12), ("Charlie", 18), ("Alice", 14), ("Bob", 16)]`. Certains élèves apparaissent plusieurs fois.
**Consigne** : (a) Construire un dictionnaire `notes_par_eleve` où chaque clé est un nom d'élève et la valeur est la liste de toutes ses notes. (b) À partir de ce dictionnaire, construire une liste de tuples `(nom, moyenne)` triée par moyenne décroissante. (c) Vérifier que le nombre total de notes dans le dictionnaire correspond bien à la longueur de la liste initiale.
**Livrable** : Le dictionnaire construit, la liste triée et la vérification du total.
**Corrigé** : Pour la correction : voir exercice 8 dans le document corrigé complément.


Cas limite : liste vide passée en argument. Cas limite : clé absente du dictionnaire.

