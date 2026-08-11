---
title: "P02 - Cours - Tables de vérité booléennes"
level: "premiere"
sequence_id: "P02"
document_type: "cours"
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

# P02 - Cours - Tables de vérité booléennes

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-04 : Dresser la table d’une expression booléenne.

## Prérequis
- Connaître les valeurs booléennes Vrai (1) et Faux (0).
- Savoir évaluer une expression logique simple.
- Distinguer donnée, méthode et conclusion dans le thème Représentation machine.
- Rédiger une justification courte en utilisant le vocabulaire du programme.

## Séance(s) correspondante(s)
- P02-S1 à P02-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un circuit logique reçoit deux signaux d'entrée et produit un signal de sortie. Pour vérifier son comportement dans tous les cas possibles, il faut dresser la table d’une expression booléenne décrivant ce circuit.

## Activité d’entrée
1. Évaluer `a ET b` pour les quatre combinaisons possibles de `a` et `b`.
2. Comparer les résultats de `a OU b` et `a XOR b` : dans quel cas diffèrent-ils ?
3. Construire la table de `NON(a ET b)` et comparer avec `(NON a) OU (NON b)`.
4. Identifier si l'expression `a OU (NON a)` donne toujours le même résultat.

---

## Définitions et formalisation

### Définition D1 : Variable booléenne
Une variable booléenne est une variable qui ne peut prendre que deux valeurs : Vrai (noté 1) ou Faux (noté 0). En informatique, ces valeurs correspondent aux états logiques des bits.

### Définition D2 : Expression booléenne
Une expression booléenne est une combinaison de variables booléennes reliées par des opérateurs logiques (ET, OU, NON, XOR). Elle produit un résultat booléen (0 ou 1).

### Définition D3 : Table de vérité
Une table de vérité est un tableau qui liste toutes les combinaisons possibles des valeurs d'entrée d’une expression booléenne et le résultat correspondant. Pour `n` variables, la table comporte `2^n` lignes.

### Définition D4 : Opérateur ET (conjonction)
L'opérateur ET (AND) vaut 1 si et seulement si les deux opérandes valent 1.

| a | b | a ET b | Justification |
|---|---|--------|---------------|
| 0 | 0 |   0    | Les deux opérandes sont faux |
| 0 | 1 |   0    | Le premier opérande est faux |
| 1 | 0 |   0    | Le second opérande est faux |
| 1 | 1 |   1    | Les deux opérandes sont vrais |

### Définition D5 : Opérateur OU (disjonction)
L'opérateur OU (OR) vaut 1 si au moins un des deux opérandes vaut 1.

| a | b | a OU b | Justification |
|---|---|--------|---------------|
| 0 | 0 |   0    | Aucun opérande vrai |
| 0 | 1 |   1    | Le second est vrai |
| 1 | 0 |   1    | Le premier est vrai |
| 1 | 1 |   1    | Les deux sont vrais |

### Définition D6 : Opérateur NON (négation)
L'opérateur NON (NOT) inverse la valeur de son opérande.

| a | NON a |
|---|-------|
| 0 |   1   |
| 1 |   0   |

### Définition D7 : Opérateur XOR (ou exclusif)
L'opérateur XOR vaut 1 si exactement un des deux opérandes vaut 1.

| a | b | a XOR b | Justification |
|---|---|---------|---------------|
| 0 | 0 |    0    | Aucun opérande exclusif |
| 0 | 1 |    1    | Exactement un opérande vrai (b) |
| 1 | 0 |    1    | Exactement un opérande vrai (a) |
| 1 | 1 |    0    | Les deux sont vrais, pas d'exclusivité |

Remarque importante : le XOR est lié à l'addition binaire. En effet, `a XOR b` donne le bit de somme de `a + b` (sans retenue). La retenue, quant à elle, est donnée par `a ET b`. Cette propriété est à la base du demi-additionneur en architecture des ordinateurs.

---

## Méthode systématique pour dresser la table d’une expression booléenne

Pour dresser la table d’une expression booléenne, on applique la méthode suivante :

**Étape 1 : Identifier les variables.**
Repérer toutes les variables présentes dans l'expression.

**Étape 2 : Calculer le nombre de lignes.**
Pour `n` variables, la table comporte `2^n` lignes. Avec 2 variables : 4 lignes. Avec 3 variables : 8 lignes.

**Étape 3 : Lister toutes les combinaisons.**
Écrire toutes les combinaisons en comptant en binaire de `00...0` à `11...1`.

**Étape 4 : Décomposer l'expression.**
Identifier les sous-expressions intermédiaires et créer une colonne pour chacune.

**Étape 5 : Évaluer ligne par ligne.**
Pour chaque combinaison, calculer les sous-expressions de l'intérieur vers l'extérieur, puis le résultat final.

**Étape 6 : Contrôler.**
Vérifier le résultat sur au moins un cas limite (toutes les entrées à 0, toutes à 1).

---

## Exemples corrigés précis

### Exemple corrigé 1 - Expression à 2 variables : `(a ET b) OU (NON a)`
- Donnée étudiée : expression `(a ET b) OU (NON a)` avec deux variables `a` et `b`.
- Méthode : dresser la table d’une expression booléenne en décomposant en sous-expressions.

| a | b | a ET b | NON a | (a ET b) OU (NON a) | Commentaire |
|---|---|--------|-------|---------------------|-------------|
| 0 | 0 |   0    |   1   |         1           | NON a suffit a rendre le OU vrai |
| 0 | 1 |   0    |   1   |         1           | Idem, NON a est vrai |
| 1 | 0 |   0    |   0   |         0           | Aucun des deux termes du OU n'est vrai |
| 1 | 1 |   1    |   0   |         1           | a ET b suffit a rendre le OU vrai |

- Résultat obtenu : l'expression vaut 0 uniquement quand `a = 1` et `b = 0`.
- Contrôle : le cas limite `a = 0, b = 0` est vérifié : `NON a = 1` donc le OU donne 1, ce qui est cohérent.

### Exemple corrigé 2 - Expression à 2 variables : `a XOR b`
- Donnée étudiée : expression `a XOR b`.
- Méthode : dresser la table et comparer avec `(a OU b) ET NON(a ET b)`.

| a | b | a XOR b | a OU b | a ET b | NON(a ET b) | (a OU b) ET NON(a ET b) | Commentaire |
|---|---|---------|--------|--------|-------------|------------------------|-------------|
| 0 | 0 |    0    |   0    |   0    |      1      |           0            | OU faux, donc le ET final donne faux |
| 0 | 1 |    1    |   1    |   0    |      1      |           1            | OU vrai et ET faux, NON donne vrai |
| 1 | 0 |    1    |   1    |   0    |      1      |           1            | Cas symétrique du précédent |
| 1 | 1 |    0    |   1    |   1    |      0      |           0            | ET vrai, NON donne faux |

- Résultat obtenu : les deux expressions donnent les mêmes résultats. On a l'identité `a XOR b = (a OU b) ET NON(a ET b)`.
- Contrôle : le cas `a = 1, b = 1` confirme que XOR donne 0 (les deux sont identiques, pas d'exclusivité).

### Exemple corrigé 3 - Expression à 3 variables : `(a ET b) OU (b ET c)`
- Donnée étudiée : expression `(a ET b) OU (b ET c)` avec trois variables `a`, `b`, `c`.
- Méthode : dresser la table avec `2^3 = 8` lignes et décomposer en sous-expressions.

| a | b | c | a ET b | b ET c | (a ET b) OU (b ET c) | Commentaire |
|---|---|---|--------|--------|----------------------|-------------|
| 0 | 0 | 0 |   0    |   0    |          0           | Toutes les entrées sont fausses |
| 0 | 0 | 1 |   0    |   0    |          0           | b est faux, les deux ET donnent faux |
| 0 | 1 | 0 |   0    |   0    |          0           | a et c sont faux, b seul ne suffit pas |
| 0 | 1 | 1 |   0    |   1    |          1           | b ET c est vrai, le OU donne vrai |
| 1 | 0 | 0 |   0    |   0    |          0           | b est faux, aucun ET n'est satisfait |
| 1 | 0 | 1 |   0    |   0    |          0           | b est faux malgré a et c vrais |
| 1 | 1 | 0 |   1    |   0    |          1           | a ET b est vrai, le OU donne vrai |
| 1 | 1 | 1 |   1    |   1    |          1           | Les deux sous-expressions sont vraies |

- Résultat obtenu : l'expression vaut 1 quand `b = 1` et au moins l'un de `a` ou `c` vaut 1. On peut simplifier en `b ET (a OU c)`.
- Contrôle : le cas `a = 0, b = 0, c = 0` donne bien 0 ; le cas `a = 1, b = 1, c = 1` donne bien 1.

---

## Cas limites et propriétés remarquables

### Tautologie
Une expression est une tautologie si elle vaut toujours 1, quelles que soient les valeurs des variables.

Exemple : `a OU (NON a)` est une tautologie.

| a | NON a | a OU (NON a) |
|---|-------|-------------|
| 0 |   1   |      1      |
| 1 |   0   |      1      |

### Contradiction
Une expression est une contradiction si elle vaut toujours 0, quelles que soient les valeurs des variables.

Exemple : `a ET (NON a)` est une contradiction.

| a | NON a | a ET (NON a) |
|---|-------|-------------|
| 0 |   1   |      0      |
| 1 |   0   |      0      |

### Lien entre XOR et addition binaire
Le XOR joue un role fondamental en arithmétique binaire. Pour additionner deux bits `a` et `b` :
- Le bit de somme est `a XOR b`.
- Le bit de retenue est `a ET b`.

| a | b | Somme (a XOR b) | Retenue (a ET b) | Valeur décimale a+b | Commentaire |
|---|---|-----------------|------------------|---------------------|-------------|
| 0 | 0 |        0        |        0         | 0+0 = 0             | Aucune retenue, somme nulle |
| 0 | 1 |        1        |        0         | 0+1 = 1             | Somme directe sans retenue |
| 1 | 0 |        1        |        0         | 1+0 = 1             | Cas symétrique du précédent |
| 1 | 1 |        0        |        1         | 1+1 = 10 en binaire | Retenue générée vers le bit supérieur |

On retrouve les résultats de l'addition : `0+0=0`, `0+1=1`, `1+0=1`, `1+1=10` (soit 0 avec une retenue de 1).

---

## Lois de De Morgan

Deux identités fondamentales permettent de transformer des expressions :

- `NON(a ET b) = (NON a) OU (NON b)`
- `NON(a OU b) = (NON a) ET (NON b)`

Ces lois se vérifient en dressant les tables de vérité des deux membres et en constatant qu'elles sont identiques ligne par ligne.

---

## Synthèse du cours
- Une table de vérité permet de décrire exhaustivement le comportement d’une expression booléenne.
- Les quatre opérateurs fondamentaux sont ET, OU, NON et XOR.
- Pour `n` variables, la table contient `2^n` lignes.
- La méthode systématique (identifier, lister, décomposer, évaluer, contrôler) garantit l'exactitude.
- Le XOR est le bit de somme de l'addition binaire ; le ET est le bit de retenue.
- Les tautologies (toujours 1) et contradictions (toujours 0) sont des cas limites à reconnaître.


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
