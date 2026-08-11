---
title: "P02 - Corrigé - Tables de vérité booléennes"
level: "premiere"
sequence_id: "P02"
document_type: "corrige"
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

# P02 - Corrigé - Tables de vérité booléennes

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-04 : Dresser la table d’une expression booléenne.

## Prérequis
- Ce corrigé correspond à l'évaluation P02 sur les tables de vérité booléennes.

---

## Corrigé de la Question 1 - Table de vérité à 2 variables (5 points)

Expression : `E = (a OU b) ET (NON b)`

**a)** (1 pt) L'expression comporte 2 variables (`a` et `b`). La table doit contenir `2^2 = 4` lignes.

**b)** (3 pts) Pour dresser la table d’une expression booléenne, on évalue les sous-expressions ligne par ligne.

| a | b | a OU b | NON b | E = (a OU b) ET (NON b) | Justification |
|---|---|--------|-------|------------------------|---------------|
| 0 | 0 |   0    |   1   |           0            | OU faux, donc ET donne faux |
| 0 | 1 |   1    |   0   |           0            | NON b faux, donc ET donne faux |
| 1 | 0 |   1    |   1   |           1            | Les deux termes du ET sont vrais |
| 1 | 1 |   1    |   0   |           0            | NON b faux, donc ET donne faux |

Détail du calcul pour chaque ligne :
- Cas a=0, b=0 : `a OU b = 0 OU 0 = 0`. `NON b = NON 0 = 1`. `E = 0 ET 1 = 0`. Le OU est faux.
- Cas a=0, b=1 : `a OU b = 0 OU 1 = 1`. `NON b = NON 1 = 0`. `E = 1 ET 0 = 0`. NON b annule le ET.
- Cas a=1, b=0 : `a OU b = 1 OU 0 = 1`. `NON b = NON 0 = 1`. `E = 1 ET 1 = 1`. Seul cas ou E vaut vrai.
- Cas a=1, b=1 : `a OU b = 1 OU 1 = 1`. `NON b = NON 1 = 0`. `E = 1 ET 0 = 0`. Le NON b bloque le résultat.

**c)** (1 pt) La colonne `E` donne les valeurs `0, 0, 1, 0`. Cela correspond exactement à la colonne `a ET NON b` :

| a | b | a ET NON b | Commentaire |
|---|---|-----------|-------------|
| 0 | 0 |     0     | a est faux |
| 0 | 1 |     0     | a est faux |
| 1 | 0 |     1     | a vrai et b faux |
| 1 | 1 |     0     | b est vrai donc NON b faux |

Donc `E = (a OU b) ET (NON b)` est équivalente à `a ET (NON b)`. L'expression se simplifie : le `OU b` est neutralisé par le `ET NON b`, seul `a` détermine le résultat quand `b = 0`.

---

## Corrigé de la Question 2 - Table de vérité à 3 variables (6 points)

Expression : `F = (a ET NON b) OU (b ET c)`

**a)** (1 pt) L'expression comporte 3 variables (`a`, `b`, `c`). La table doit contenir `2^3 = 8` lignes, car il y a 8 combinaisons possibles pour 3 variables binaires.

**b)** (4 pts) On dresse la table en calculant les sous-expressions intermédiaires pour chaque ligne.

| a | b | c | NON b | a ET NON b | b ET c | F | Justification |
|---|---|---|-------|-----------|--------|---|---------------|
| 0 | 0 | 0 |   1   |     0     |   0    | 0 | a faux, b faux et c faux |
| 0 | 0 | 1 |   1   |     0     |   0    | 0 | a faux annule le premier ET, b faux annule le second |
| 0 | 1 | 0 |   0   |     0     |   0    | 0 | NON b faux et c faux |
| 0 | 1 | 1 |   0   |     0     |   1    | 1 | b ET c suffit pour le OU |
| 1 | 0 | 0 |   1   |     1     |   0    | 1 | a ET NON b suffit pour le OU |
| 1 | 0 | 1 |   1   |     1     |   0    | 1 | Le premier terme du OU est vrai |
| 1 | 1 | 0 |   0   |     0     |   0    | 0 | NON b faux et c faux annulent tout |
| 1 | 1 | 1 |   0   |     0     |   1    | 1 | Seul b ET c est vrai |

Détail du calcul pour les lignes clés :
- Cas (a=0, b=1, c=1) : `NON b = 0`, donc `a ET NON b = 0 ET 0 = 0`. `b ET c = 1 ET 1 = 1`. `F = 0 OU 1 = 1`. Ici seul le second terme du OU est vrai.
- Cas (a=1, b=0, c=0) : `NON b = 1`, donc `a ET NON b = 1 ET 1 = 1`. `b ET c = 0 ET 0 = 0`. `F = 1 OU 0 = 1`. Ici seul le premier terme du OU est vrai.
- Cas (a=1, b=1, c=0) : `NON b = 0`, donc `a ET NON b = 1 ET 0 = 0`. `b ET c = 1 ET 0 = 0`. `F = 0 OU 0 = 0`. Aucun terme du OU n'est satisfait.

Barème pour les 4 points :
- 1 pt pour les colonnes intermédiaires correctement remplies.
- 2 pts pour la colonne `F` entièrement correcte (8 lignes).
- 1 pt pour les combinaisons listées en binaire dans le bon ordre.

**c)** (1 pt) Contrôle pour `a = 1, b = 0, c = 1` :
- `a ET NON b = 1 ET NON 0 = 1 ET 1 = 1`.
- `b ET c = 0 ET 1 = 0`.
- `F = 1 OU 0 = 1`.

Le résultat par substitution directe est 1, ce qui correspond bien à la ligne 6 de la table. Le contrôle est concluant.

---

## Corrigé de la Question 3 - Analyse et cas limites (4 points)

Expression : `G = (a ET b) OU (NON a ET NON b)`

**a)** (2 pts)

| a | b | a ET b | NON a | NON b | NON a ET NON b | G | Justification |
|---|---|--------|-------|-------|----------------|---|---------------|
| 0 | 0 |   0    |   1   |   1   |       1        | 1 | Les deux sont faux donc NON a ET NON b est vrai |
| 0 | 1 |   0    |   1   |   0   |       0        | 0 | Ni a ET b ni NON a ET NON b n'est vrai |
| 1 | 0 |   0    |   0   |   1   |       0        | 0 | Cas symétrique : valeurs différentes |
| 1 | 1 |   1    |   0   |   0   |       0        | 1 | a ET b est vrai car les deux sont vrais |

Détail :
- Pour a=0, b=0 : `a ET b = 0`. `NON a ET NON b = 1 ET 1 = 1`. `G = 0 OU 1 = 1`. Les deux sont faux, G vaut vrai.
- Pour a=0, b=1 : `a ET b = 0`. `NON a ET NON b = 1 ET 0 = 0`. `G = 0 OU 0 = 0`. Valeurs différentes, G vaut faux.
- Pour a=1, b=0 : `a ET b = 0`. `NON a ET NON b = 0 ET 1 = 0`. `G = 0 OU 0 = 0`. Cas symétrique du précédent.
- Pour a=1, b=1 : `a ET b = 1`. `NON a ET NON b = 0 ET 0 = 0`. `G = 1 OU 0 = 1`. Les deux sont vrais, G vaut vrai.

**b)** (1 pt) La table de `a XOR b` donne les valeurs `0, 1, 1, 0`. La table de `G` donne les valeurs `1, 0, 0, 1`. On constate que `G` est l'inverse exact de `a XOR b` :

| a | b | a XOR b | G | Relation |
|---|---|---------|---|----------|
| 0 | 0 |    0    | 1 | G = NON(XOR) car les deux valent la même chose |
| 0 | 1 |    1    | 0 | XOR vrai quand les valeurs diffèrent |
| 1 | 0 |    1    | 0 | Cas symétrique : valeurs différentes |
| 1 | 1 |    0    | 1 | G vrai quand a et b sont identiques |

Donc `G = NON(a XOR b)`, ce qui s'appelle parfois XNOR ou opérateur d'équivalence. `G` vaut 1 quand `a` et `b` ont la même valeur.

**c)** (1 pt) `G` n'est ni une tautologie ni une contradiction :
- Ce n'est pas une tautologie car `G` vaut 0 pour `a = 0, b = 1` (et pour `a = 1, b = 0`).
- Ce n'est pas une contradiction car `G` vaut 1 pour `a = 0, b = 0` (et pour `a = 1, b = 1`).

`G` est une expression qui dépend effectivement des valeurs de `a` et `b`. Elle vaut 1 exactement lorsque `a = b` (les deux variables ont la même valeur).

---

## Barème récapitulatif

| Question | Points | Critères principaux |
|----------|--------|-------------------|
| Q1.a     | 1      | Nombre de variables et de lignes correct |
| Q1.b     | 3      | Table correcte avec colonnes intermédiaires |
| Q1.c     | 1      | Simplification correcte avec justification |
| Q2.a     | 1      | Nombre de lignes correct avec justification |
| Q2.b     | 4      | Table à 8 lignes correcte avec intermédiaires |
| Q2.c     | 1      | Contrôle par substitution correct |
| Q3.a     | 2      | Table correcte avec toutes les colonnes |
| Q3.b     | 1      | Relation avec XOR identifiée |
| Q3.c     | 1      | Ni tautologie ni contradiction, justifié |
| **Total**| **15** | |


## Situation-problème

Un ingénieur réseau reçoit un paquet de 8 bits et doit déterminer si les données représentent un entier positif ou négatif. Comment distinguer les deux cas sans information supplémentaire ?

## Activité d’entrée

Compléter la table de vérité de l'expression A ET (NON B) pour toutes les combinaisons possibles de A et B.

## Exemple

Construction collective de la table de vérité de (A ET B) OU (NON C) avec 8 lignes.

## Exercices

Exercices de construction de tables de vérité avec expressions booléennes de complexité croissante.

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

### Corrigé exercice 1

**Méthode** : on applique la définition de l'opérateur ET ligne par ligne.
Pour A=0, B=0 : A ET B vaut `0`. Pour A=0, B=1 : A ET B vaut `0`. Pour A=1, B=0 : A ET B vaut `0`. Pour A=1, B=1 : A ET B vaut `1`.
**Résultat** : la table complète donne `[0, 0, 0, 1]` pour les 4 combinaisons.

















### Corrigé exercice 2

Réponse détaillée avec justification.

La table donne `[0, 1, 1, 0]` pour les 4 combinaisons de A et B.

### Corrigé exercice 3

Réponse détaillée avec justification.

Le résultat attendu est `1` (Vrai) lorsque A=1 et B=0, la table complète donne `[0, 0, 1, 0]`.

### Corrigé exercice 4

Réponse détaillée avec justification.

L'expression vaut `1` pour les combinaisons où A ET B sont vrais, la table donne `[0, 0, 0, 1]`.

### Corrigé exercice 5

Réponse détaillée avec justification.

Le résultat attendu est `[1, 1, 1, 0]` car l'expression A OU B vaut `0` uniquement quand A=0 et B=0.

### Corrigé exercice 6

Réponse détaillée avec justification.

La table donne `[1, 0, 0, 0]` et le résultat attendu est `1` uniquement pour A=0, B=0.

### Corrigé exercice 7

Réponse détaillée avec justification.

Le résultat attendu est `[1, 1, 1, 1]` car l'expression est une tautologie qui vaut `1` pour toutes les combinaisons.

### Corrigé exercice 8

Réponse détaillée avec justification.

La table donne `[0, 1, 1, 0]` et le résultat attendu est `1` quand les variables A et B diffèrent (XOR).

