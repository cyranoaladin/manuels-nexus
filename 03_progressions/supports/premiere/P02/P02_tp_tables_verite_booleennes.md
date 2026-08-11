---
title: "P02 - TP - Tables de vérité booléennes"
level: "premiere"
sequence_id: "P02"
document_type: "tp"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Représentation machine"
notion: "expression booléenne, table de vérité, opérateurs logiques"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-04"
---

# P02 - TP - Tables de vérité booléennes

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-04 : Dresser la table d’une expression booléenne.

## Prérequis
- Connaître les opérateurs ET, OU, NON, XOR et leurs tables de vérité.
- Connaître les opérateurs Python `and`, `or`, `not` et `^` (XOR sur entiers).
- Savoir utiliser les boucles `for` et la fonction `print`.

---

## Partie 1 - Opérateurs booléens en Python

### Exercice 1.1 - Découverte des opérateurs

En Python, les opérateurs booléens sont `and`, `or`, `not`. Le XOR sur les booléens s'obtient avec `!=` ou avec `^` sur des entiers 0/1.

**a)** Dans la console Python, tester les expressions suivantes et noter les résultats :

```python
True and False
True or False
not True
True != True    # XOR
True != False   # XOR
```

**b)** Vérifier que `1 ^ 0` donne bien 1 et que `1 ^ 1` donne bien 0. Expliquer pourquoi `^` sur les entiers 0 et 1 se comporte comme le XOR booléen.

### Exercice 1.2 - Évaluation d'expressions

**a)** Prévoir le résultat de chaque expression, puis vérifier en Python :

```python
(True and False) or True
not (True or False)
(True or False) and not True
True and not False
```

**b)** Traduire l'expression booléenne `(a ET b) OU (NON a)` en Python et l'évaluer pour `a = True, b = False`.

```python
a = True
b = False
resultat = (a and b) or (not a)
print(resultat)
```

---

### Exercice 1.3 - Analyse des résultats

**a)** Quelle différence observe-t-on entre `and` et `or` quand les deux opérandes sont faux ?

**b)** Vérifier que `not (True and False)` donne le même résultat que `(not True) or (not False)`. Quelle loi cela illustre-t-il ?

---

## Partie 2 - Générer des tables de vérité en Python

L’objectif de cette partie est de dresser la table d’une expression booléenne de manière automatique avec Python.

### Exercice 2.1 - Table de vérité à 2 variables

**a)** Compléter le programme suivant pour afficher la table de vérité de `a ET b` :

```python
print("a | b | a ET b")
print("--+---+-------")
for a in [0, 1]:
    for b in [0, 1]:
        resultat = ...  # Compléter avec l'opération ET
        print(f"{a} | {b} |   {resultat}")
```

Indication : en Python, avec des entiers 0 et 1, on peut utiliser `a and b` ou `a * b` pour le ET logique.

**b)** Modifier le programme pour afficher les tables de OU (`a or b`), NON a (`1 - a` ou `int(not a)`) et XOR (`a ^ b`).

**c)** Écrire un programme qui affiche la table de vérité de l'expression `(a or b) and (not a)` avec les colonnes intermédiaires :

```python
print("a | b | a OU b | NON a | (a OU b) ET (NON a)")
print("--+---+--------+-------+--------------------")
for a in [0, 1]:
    for b in [0, 1]:
        ou = int(a or b)
        non_a = int(not a)
        resultat = int((a or b) and (not a))
        print(f"{a} | {b} |   {ou}    |   {non_a}   |         {resultat}")
```

Exécuter ce programme et vérifier que la table obtenue correspond à celle dressée à la main en TD.

### Exercice 2.2 - Table de vérité à 3 variables

**a)** Écrire un programme qui génère la table de vérité de `(a ET b) OU (b ET c)` avec les 8 combinaisons :

```python
print("a | b | c | a ET b | b ET c | (a ET b) OU (b ET c)")
print("--+---+---+--------+--------+---------------------")
for a in [0, 1]:
    for b in [0, 1]:
        for c in [0, 1]:
            ab = int(a and b)
            bc = int(b and c)
            resultat = int((a and b) or (b and c))
            print(f"{a} | {b} | {c} |   {ab}    |   {bc}    |          {resultat}")
```

**b)** Vérifier que le résultat est identique à la table dressée à la main dans le cours (exemple corrigé 3).

**c)** Modifier le programme pour afficher aussi la colonne `b ET (a OU c)` et vérifier que cette expression simplifiée donne les mêmes résultats.

---

## Partie 3 - Fonction générique de table de vérité

### Exercice 3.1 - Fonction pour 2 variables

**a)** Écrire une fonction `table_2var(expression, nom)` qui prend en paramètre une fonction booléenne à 2 arguments et un nom (chaîne), et affiche sa table de vérité :

```python
def table_2var(expression, nom):
    """Affiche la table de vérité d’une expression à 2 variables."""
    print(f"a | b | {nom}")
    print(f"--+---+{'--' * len(nom)}")
    for a in [0, 1]:
        for b in [0, 1]:
            r = int(expression(bool(a), bool(b)))
            print(f"{a} | {b} |  {r}")
```

**b)** Tester cette fonction avec les quatre opérateurs de base :

```python
table_2var(lambda a, b: a and b, "a ET b")
print()
table_2var(lambda a, b: a or b, "a OU b")
print()
table_2var(lambda a, b: a and not b, "a ET NON b")
print()
table_2var(lambda a, b: a != b, "a XOR b")
```

### Exercice 3.1b - Test de la fonction avec expressions complexes

Vérifier que `table_2var` produit les résultats attendus pour `(a and b) or (not a)` en comparant chaque ligne avec le calcul manuel.

### Exercice 3.2 - Fonction pour 3 variables

**a)** Écrire une fonction `table_3var(expression, nom)` sur le même modèle, avec trois boucles imbriquées.

**b)** Utiliser cette fonction pour dresser la table du vote majoritaire : `(a and b) or (a and c) or (b and c)`.

**c)** Vérifier que le résultat vaut 1 si et seulement si au moins 2 des 3 variables valent 1.

---

## Partie 4 - Vérification et cas limites

### Exercice 4.1 - Vérifier les lois de De Morgan

**a)** Écrire un programme qui vérifie automatiquement la première loi de De Morgan `NON(a ET b) = (NON a) OU (NON b)` en comparant les deux expressions pour toutes les combinaisons :

```python
def verifier_de_morgan_1():
    for a in [False, True]:
        for b in [False, True]:
            gauche = not (a and b)
            droite = (not a) or (not b)
            if gauche != droite:
                print(f"Echec pour a={a}, b={b}")
                return False
    print("Loi de De Morgan 1 vérifiée pour toutes les combinaisons.")
    return True

verifier_de_morgan_1()
```

**b)** Écrire un programme similaire pour la seconde loi : `NON(a OU b) = (NON a) ET (NON b)`.

### Exercice 4.1b - Test avec la seconde loi de De Morgan

Modifier la fonction pour vérifier `NON(a OU b) = (NON a) ET (NON b)` et confirmer que toutes les combinaisons sont valides.

### Exercice 4.2 - Détecter tautologies et contradictions

**a)** Écrire une fonction `est_tautologie_2var(expression)` qui retourne `True` si l'expression vaut toujours `True` pour toutes les combinaisons de 2 variables :

```python
def est_tautologie_2var(expression):
    """Retourne True si l'expression est une tautologie."""
    for a in [False, True]:
        for b in [False, True]:
            if not expression(a, b):
                return False
    return True
```

**b)** Tester avec :
```python
print(est_tautologie_2var(lambda a, b: a or (not a)))      # True
print(est_tautologie_2var(lambda a, b: a or b))             # False
print(est_tautologie_2var(lambda a, b: (a and b) or (a and not b) or (not a and b) or (not a and not b)))  # True
```

**c)** Écrire une fonction `est_contradiction_2var(expression)` et tester avec `a ET (NON a)`.

### Exercice 4.3 - XOR et addition binaire

**a)** Écrire un programme qui affiche le demi-additionneur binaire : pour chaque paire `(a, b)`, afficher le bit de somme (`a XOR b`) et le bit de retenue (`a ET b`) :

```python
print("a | b | Somme (XOR) | Retenue (ET)")
print("--+---+-------------+-------------")
for a in [0, 1]:
    for b in [0, 1]:
        somme = a ^ b
        retenue = a and b
        print(f"{a} | {b} |      {somme}      |      {int(retenue)}")
```

**b)** Vérifier que pour chaque ligne, la valeur décimale `retenue * 2 + somme` correspond bien à `a + b`.

### Exercice 4.4 - Comparer XOR et différence

Écrire un programme qui vérifie que `a ^ b` produit le même résultat que `(a or b) and not (a and b)` pour toutes les combinaisons possibles de `a` et `b` (avec `a` et `b` dans `[0, 1]`).


## Situation-problème

Un ingénieur réseau reçoit un paquet de 8 bits et doit déterminer si les données représentent un entier positif ou négatif. Comment distinguer les deux cas sans information supplémentaire ?

## Activité d’entrée

Compléter la table de vérité de l'expression A ET (NON B) pour toutes les combinaisons possibles de A et B.

## Exemple

Construction collective de la table de vérité de (A ET B) OU (NON C) avec 8 lignes.

## Exercices

Exercices de construction de tables de vérité avec expressions booléennes de complexité croissante.

## Corrigé

Les corrigés détaillés sont dans P02_corrige_tables_verite_booleennes.md.

## Erreurs fréquentes

- EF1 : confondre ET et OU dans une expression composée.
- EF2 : oublier une ligne dans la table de vérité (nombre de combinaisons = 2^n).
- EF3 : inverser Vrai et Faux pour l'opérateur NON.


## Remédiation

Exercice de remédiation : construire pas à pas la table de vérité de A OU (NON A) en vérifiant chaque cellule.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.

## Critères de réussite

Table de vérité correcte avec toutes les combinaisons. Identification des tautologies et contradictions justifiée.

## Séance(s) correspondante(s)

Séance dédiée.

## Tests attendus

Vérifier le résultat avec les jeux de tests fournis.

## Exemple d’exécution

Exécuter le script de génération de tables et vérifier que chaque ligne correspond aux valeurs attendues.

## Livrable vérifiable

Script Python générant automatiquement la table de vérité d'une expression booléenne donnée.

## Consigne technique détaillée

Implémenter les fonctions demandées en utilisant les opérateurs booléens Python (and, or, not).

## Cas limite

Tester avec des entrées vides et des cas extrêmes.

Critère de validation : chaque réponse est vérifiable par un contrôle explicite.
