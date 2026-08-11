---
title: "P04 - Evaluation - Types construits complément"
level: "premiere"
sequence_id: "P04"
document_type: "evaluation"
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

# P04 - Évaluation - Types construits complément

**Durée : 20 minutes | Sans ordinateur | Documents interdits**

## Capacités officielles atomiques
- P-DATA-CONSTR-01 : Écrire une fonction renvoyant un p-uplet de valeurs
- P-DATA-CONSTR-02B : Construire un tableau par compréhension
- P-DATA-CONSTR-02C : Utiliser des tableaux de tableaux pour représenter des matrices
- P-DATA-CONSTR-03A : Construire une entrée de dictionnaire
- P-DATA-CONSTR-03B : Itérer sur les éléments d’un dictionnaire
- P-DATA-CONSTR-03C : Utiliser les méthodes keys, values et items

---

## Question 1 - P-DATA-CONSTR-01 (4 points)

On considère la fonction suivante :

```python
def encadrer(n):
    return n - 1, n + 1
```

**1a.** (1 pt) Quel est le type de la valeur renvoyée par `encadrer(5)` ?

**1b.** (1 pt) Donner les valeurs de `a` et `b` après l’exécution de :

```python
a, b = encadrer(10)
```

**1c.** (2 pts) Écrire une fonction `aire_perimetre(longueur, largeur)` qui renvoie un tuple contenant l'aire et le périmètre d’un rectangle. Donner le résultat pour `longueur = 5` et `largeur = 3`.

---

## Question 2 - P-DATA-CONSTR-02B (4 points)

**2a.** (2 pts) Déterminer le contenu des listes suivantes :

```python
L1 = [x ** 2 for x in range(10)]
L2 = [n for n in range(1, 16) if n % 5 == 0]
```

**2b.** (2 pts) Écrire une compréhension de liste qui, a partir d’une liste `notes`, produit la liste des notes supérieures ou égales a 10. Appliquer avec `notes = [8, 12, 5, 16, 10, 3]`.

---

## Question 3 - P-DATA-CONSTR-02C (4 points)

On donne :

```python
grille = [
    [2, 7, 1],
    [8, 3, 5],
    [4, 9, 6],
]
```

**3a.** (1 pt) Donner la valeur de `grille[1][2]` et `grille[2][0]`.

**3b.** (1 pt) Écrire les expressions Python qui donnent le nombre de lignes et le nombre de colonnes.

**3c.** (2 pts) Écrire une fonction `somme_ligne(matrice, i)` qui renvoie la somme des éléments de la ligne `i`. Donner le résultat pour la ligne 0 de `grille`.

---

## Question 4 - P-DATA-CONSTR-03A (4 points)

**4a.** (2 pts) Compléter le code suivant pour construire un dictionnaire `eleve` avec les entrées `"nom"` (valeur `"Martin"`), `"prenom"` (valeur `"Léa"`), `"age"` (valeur `16`) et `"classe"` (valeur `"1NSI"`).

```python
eleve = {}
eleve[_____] = _____
eleve[_____] = _____
eleve[_____] = _____
eleve[_____] = _____
```

**4b.** (1 pt) Que se passe-t-il si on exécute ensuite `eleve["age"] = 17` ? Quelle est la nouvelle valeur de `eleve["age"]` ?

**4c.** (1 pt) Pourquoi l'instruction `d[[1, 2]] = "valeur"` provoque-t-elle une erreur ?

---

## Question 5 - P-DATA-CONSTR-03B, P-DATA-CONSTR-03C (4 points)

On donne :

```python
scores = {"Alice": 85, "Bob": 72, "Clara": 91}
```

**5a.** (1 pt) Écrire ce qu'affiche le code suivant :

```python
for nom in scores:
    print(nom)
```

**5b.** (1 pt) Écrire une boucle qui affiche chaque entrée sous la forme `"Alice a obtenu 85"`, en utilisant `.items()`.

**5c.** (2 pts) Écrire une fonction `meilleur_score(d)` qui prend un dictionnaire `{nom: score}` et renvoie le tuple `(nom, score)` correspondant au score le plus élevé.


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


## Barème

| Question | Points |
|---|---|
| Question 1 | 4 |
| Question 2 | 4 |
| Question 3 | 4 |
| Question 4 | 4 |
| Question 5 | 4 |
| **Total** | **20** |

## Critères de réussite

Fonction renvoyant un tuple vérifiée. Compréhension de liste correcte. Matrice accessible par double index. Dictionnaire itéré avec keys/values/items.

## Séance(s) correspondante(s)

Séance dédiée.

Cas limite : tuple vide renvoyé. Cas limite : compréhension sur une liste vide. Cas limite : dictionnaire vide itéré. Cas limite : clé absente dans le dictionnaire.

Critère de validation : chaque réponse est vérifiable par un contrôle explicite.
