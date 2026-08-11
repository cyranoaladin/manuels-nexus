---
title: "P02 - TD - Tables de vérité booléennes"
level: "premiere"
sequence_id: "P02"
document_type: "td"
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

# P02 - TD - Tables de vérité booléennes

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-04 : Dresser la table d’une expression booléenne.

## Prérequis
- Connaître les opérateurs ET, OU, NON, XOR et leurs tables de vérité.
- Savoir construire une table de vérité pour une expression à 2 variables.
- Connaître la méthode systématique en 6 étapes vue en cours.

---

## Exercice 1 - Expressions à 2 variables (niveau fondamental)

L'objectif est de dresser la table d’une expression booléenne pour chacune des expressions suivantes.

**1.a)** Dresser la table de vérité de l'expression `E1 = a ET (NON b)`.

Compléter le tableau :

| a | b | NON b | a ET (NON b) | Justification |
|---|---|-------|-------------|---------------|
| 0 | 0 |       |             | Deux entrées fausses |
| 0 | 1 |       |             | Seul b est vrai |
| 1 | 0 |       |             | Seul a est vrai |
| 1 | 1 |       |             | Les deux entrées sont vraies |

**1.b)** Dresser la table de vérité de l'expression `E2 = (NON a) OU b`.

| a | b | NON a | (NON a) OU b | Justification |
|---|---|-------|-------------|---------------|
| 0 | 0 |       |             | NON a est vrai, b est faux |
| 0 | 1 |       |             | NON a et b sont vrais |
| 1 | 0 |       |             | NON a est faux, b est faux |
| 1 | 1 |       |             | NON a est faux mais b est vrai |

**1.c)** Comparer les tables de `E1` et `NON(E2)`. Que constate-t-on ? Justifier à l'aide des lois de De Morgan.

**1.d)** Dresser la table de vérité de `E3 = a XOR b`. Vérifier que `E3 = (a OU b) ET NON(a ET b)` en dressant la table de cette seconde expression.

---

## Exercice 2 - Expression à 3 variables (niveau intermédiaire)

On considère l'expression `F = (a ET b) OU (NON a ET c)`.

**2.a)** Combien de lignes comporte la table de vérité de `F` ? Justifier.

**2.b)** Dresser la table de vérité complète de `F` en faisant apparaître les colonnes intermédiaires `a ET b`, `NON a`, `NON a ET c`.

| a | b | c | a ET b | NON a | NON a ET c | F | Justification |
|---|---|---|--------|-------|-----------|---|---------------|
| 0 | 0 | 0 |        |       |           |   | Toutes les entrées sont fausses |
| 0 | 0 | 1 |        |       |           |   | Seul c est vrai |
| 0 | 1 | 0 |        |       |           |   | Seul b est vrai |
| 0 | 1 | 1 |        |       |           |   | b et c sont vrais, a est faux |
| 1 | 0 | 0 |        |       |           |   | Seul a est vrai |
| 1 | 0 | 1 |        |       |           |   | a et c vrais, b faux |
| 1 | 1 | 0 |        |       |           |   | a et b vrais, c faux |
| 1 | 1 | 1 |        |       |           |   | Toutes les entrées sont vraies |

**2.c)** Pour quelles combinaisons de `(a, b, c)` l'expression `F` vaut-elle 1 ?

**2.d)** Contrôle : vérifier le résultat pour le cas `a = 0, b = 0, c = 0` et pour le cas `a = 1, b = 1, c = 1` en substituant directement dans l'expression.

---

## Exercice 3 - Simplification par tables de vérité (niveau avancé)

**3.a)** Dresser la table de vérité de l'expression `G = (a ET b) OU (a ET NON b)`.

| a | b | a ET b | NON b | a ET NON b | G | Justification |
|---|---|--------|-------|-----------|---|---------------|
| 0 | 0 |        |       |           |   | Les deux entrées sont fausses |
| 0 | 1 |        |       |           |   | Seul b est vrai |
| 1 | 0 |        |       |           |   | Seul a est vrai |
| 1 | 1 |        |       |           |   | Les deux entrées sont vraies |

**3.b)** Comparer la colonne `G` avec la colonne `a`. Quelle simplification peut-on en déduire ?

**3.c)** Justifier cette simplification en factorisant algébriquement : `G = a ET (b OU NON b)`. Pourquoi `b OU NON b` vaut-il toujours 1 ?

**3.d)** Dresser la table de vérité de `H = (a OU b) ET (a OU NON b)`. Simplifier `H` de la même manière.

---

## Exercice 4 - Application : vote majoritaire (niveau avancé)

Un système de vote électronique repose sur trois capteurs `a`, `b` et `c`. Le résultat `V` vaut 1 si et seulement si au moins deux capteurs sur trois valent 1 (vote majoritaire).

**4.a)** Écrire l'expression booléenne de `V` en fonction de `a`, `b` et `c`.

Indication : `V = (a ET b) OU (a ET c) OU (b ET c)`.

**4.b)** Dresser la table de vérité complète de `V` avec les 8 lignes.

| a | b | c | a ET b | a ET c | b ET c | V | Justification |
|---|---|---|--------|--------|--------|---|---------------|
| 0 | 0 | 0 |        |        |        |   | Aucun capteur actif |
| 0 | 0 | 1 |        |        |        |   | Un seul capteur actif (c) |
| 0 | 1 | 0 |        |        |        |   | Un seul capteur actif (b) |
| 0 | 1 | 1 |        |        |        |   | Deux capteurs actifs (b et c) |
| 1 | 0 | 0 |        |        |        |   | Un seul capteur actif (a) |
| 1 | 0 | 1 |        |        |        |   | Deux capteurs actifs (a et c) |
| 1 | 1 | 0 |        |        |        |   | Deux capteurs actifs (a et b) |
| 1 | 1 | 1 |        |        |        |   | Trois capteurs actifs |

**4.c)** Vérifier que `V` vaut bien 1 exactement lorsque 2 ou 3 capteurs sont actifs.

**4.d)** Cas limite : que se passe-t-il si les trois capteurs sont en panne (tous à 0) ? Et si les trois fonctionnent (tous à 1) ? Vérifier la cohérence du système.


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

### Exercice 1 — Table ET à 2 variables

**Donnée** : Soit l'expression booléenne `E = a ET b`.
**Consigne** : Dresser la table de vérité complète de `E` en listant les 4 combinaisons possibles de `a` et `b`. Pour chaque ligne, justifier le résultat en rappelant la règle : « ET ne vaut 1 que si les deux opérandes valent 1 ». Identifier les lignes où `E` vaut 1 et celles où `E` vaut 0.
**Livrable** : La table de vérité à 4 lignes avec colonnes `a`, `b`, `a ET b` et `Justification`.
**Corrigé** : Le corrigé détaillé se trouve dans le fichier corrigé complément, exercice 1.

### Exercice 2 — Table OU à 2 variables

**Donnée** : L'expression suivante est `E = a OU b`.
**Consigne** : Dresser la table de vérité complète de `E` pour les 4 combinaisons de `a` et `b`. Pour chaque ligne, justifier le résultat en rappelant la règle : « OU vaut 0 uniquement si les deux opérandes valent 0 ». Comparer avec la table de ET de l'exercice 1 : pour quelles combinaisons les résultats diffèrent-ils ?
**Livrable** : La table de vérité à 4 lignes avec colonnes `a`, `b`, `a OU b` et `Justification`, plus la comparaison.
**Corrigé** : Voir la correction complète dans le corrigé complément (exercice 2).

### Exercice 3 — Table NON + ET à 2 variables

**Donnée** : On étudie l'expression `E = (NON a) ET b`.
**Consigne** : Dresser la table de vérité de `E` en faisant apparaître la colonne intermédiaire `NON a`. Pour chaque ligne, détailler le calcul en deux étapes : d'abord évaluer `NON a`, puis appliquer `ET` avec `b`. Indiquer pour quelles valeurs de `(a, b)` cette expression vaut 1.
**Livrable** : La table de vérité à 4 lignes avec colonnes `a`, `b`, `NON a`, `(NON a) ET b` et `Justification`.
**Corrigé** : Corrigé avec justification : fichier corrigé complément, exercice 3.

### Exercice 4 — Table à 3 variables

**Donnée** : L'expression booléenne à analyser est `E = (a OU b) ET c`.
**Consigne** : Déterminer le nombre de lignes de la table (justifier avec la formule 2^n). Dresser la table de vérité complète en faisant apparaître la colonne intermédiaire `a OU b`. Pour les 8 combinaisons, évaluer d'abord `a OU b`, puis appliquer `ET c`. Lister toutes les combinaisons pour lesquelles `E` vaut 1.
**Livrable** : La table de vérité à 8 lignes avec colonnes `a`, `b`, `c`, `a OU b`, `(a OU b) ET c` et `Justification`.
**Corrigé** : Solution détaillée : exercice 4 du corrigé complément associé.

### Exercice 5 — XOR par combinaison d'opérateurs

**Donnée** : L'opérateur XOR (ou exclusif) peut s'exprimer comme `a XOR b = (a OU b) ET NON(a ET b)`.
**Consigne** : Dresser la table de vérité de `a XOR b` en faisant apparaître toutes les colonnes intermédiaires : `a OU b`, `a ET b`, `NON(a ET b)` et le résultat final. Vérifier que le XOR vaut 1 exactement lorsque les deux variables ont des valeurs différentes. Proposer une seconde décomposition équivalente utilisant `(a ET NON b) OU (NON a ET b)` et vérifier par table de vérité.
**Livrable** : Les deux tables de vérité complètes et la vérification d'équivalence.
**Corrigé** : Consulter le corrigé complément pour la solution de l'exercice 5.

### Exercice 6 — Vérification par substitution

**Donnée** : Soit l'expression booléenne `E = (a ET b) OU (NON a ET NON b)`. On affirme que `E` est équivalente à `NON(a XOR b)`.
**Consigne** : (a) Dresser la table de vérité de `E` avec les colonnes intermédiaires `a ET b`, `NON a`, `NON b`, `NON a ET NON b`. (b) Dresser la table de vérité de `a XOR b` puis de `NON(a XOR b)`. (c) Vérifier par substitution directe pour le cas `a = 1, b = 0` que les deux expressions donnent le même résultat. (d) Conclure sur l'équivalence.
**Livrable** : Les deux tables de vérité, la vérification par substitution et la conclusion.
**Corrigé** : La réponse attendue et sa justification sont dans le corrigé complément, exercice 6.

### Exercice 7 — Simplification booléenne

**Donnée** : L'expression suivante est `E = (a OU b) ET (a OU NON b)`.
**Consigne** : (a) Dresser la table de vérité de `E` avec les colonnes intermédiaires `NON b`, `a OU b`, `a OU NON b`. (b) Comparer la colonne de `E` avec la colonne de `a`. Quelle simplification en déduit-on ? (c) Justifier algébriquement en factorisant : `E = a OU (b ET NON b)`. Expliquer pourquoi `b ET NON b = 0` et donc `E = a OU 0 = a`. (d) Appliquer la même méthode pour simplifier `F = (a ET b) OU (a ET NON b)`.
**Livrable** : La table de vérité, la simplification identifiée, la preuve algébrique et la simplification de `F`.
**Corrigé** : Exercice 7 : solution dans le corrigé complément (avec trace d'exécution).

### Exercice 8 — Tautologie et contradiction

**Donnée** : On considère les deux expressions `T = a OU NON a` et `C = a ET NON a`.
**Consigne** : (a) Dresser la table de vérité de `T` et de `C`. (b) Constater que `T` vaut toujours 1 : c'est une tautologie. Constater que `C` vaut toujours 0 : c'est une contradiction. (c) Dresser la table de vérité de `E = (a ET b) OU NON(a ET b)`. Est-ce une tautologie, une contradiction ou ni l'un ni l'autre ? Justifier. (d) Dresser la table de vérité de `F = (a ET NON a) OU (b ET NON b)`. Conclure.
**Livrable** : Les quatre tables de vérité et la classification de chaque expression (tautologie, contradiction ou contingente).
**Corrigé** : Pour la correction : voir exercice 8 dans le document corrigé complément.

