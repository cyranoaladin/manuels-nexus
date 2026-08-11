---
title: "P02 - Evaluation - Tables de vérité booléennes"
level: "premiere"
sequence_id: "P02"
document_type: "evaluation"
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

# P02 - Evaluation - Tables de vérité booléennes

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-04 : Dresser la table d’une expression booléenne.

## Prérequis
- Connaître les opérateurs ET, OU, NON, XOR et leurs tables de vérité.
- Savoir appliquer la méthode systématique pour construire une table de vérité.
- Connaître les notions de tautologie et de contradiction.

---

**Durée : 15 minutes | Sans documents | Sans calculatrice**

---

## Question 1 - Dresser une table de vérité à 2 variables (5 points)

Dresser la table de vérité de l'expression `E = (a OU b) ET (NON b)`.

**a)** (1 pt) Combien de variables comporte cette expression ? Combien de lignes la table doit-elle contenir ?

**b)** (3 pts) Compléter la table de vérité ci-dessous en faisant apparaître les colonnes intermédiaires `a OU b` et `NON b`.

| a | b | a OU b | NON b | E = (a OU b) ET (NON b) | Justification |
|---|---|--------|-------|------------------------|---------------|
| 0 | 0 |        |       |                        | Deux entrées fausses |
| 0 | 1 |        |       |                        | Seul b est vrai |
| 1 | 0 |        |       |                        | Seul a est vrai |
| 1 | 1 |        |       |                        | Les deux entrées sont vraies |

**c)** (1 pt) L'expression `E` est-elle équivalente à une expression plus simple ? Si oui, laquelle ? Justifier en comparant les colonnes.

---

## Question 2 - Dresser une table de vérité à 3 variables (6 points)

On considère l'expression `F = (a ET NON b) OU (b ET c)`.

**a)** (1 pt) Combien de lignes comporte la table de vérité de `F` ? Justifier.

**b)** (4 pts) Dresser la table de vérité complète de `F` en faisant apparaître les colonnes intermédiaires `NON b`, `a ET NON b`, `b ET c`.

| a | b | c | NON b | a ET NON b | b ET c | F | Justification |
|---|---|---|-------|-----------|--------|---|---------------|
| 0 | 0 | 0 |       |           |        |   | Toutes les entrées sont fausses |
| 0 | 0 | 1 |       |           |        |   | Seul c est vrai |
| 0 | 1 | 0 |       |           |        |   | Seul b est vrai |
| 0 | 1 | 1 |       |           |        |   | b et c sont vrais, a est faux |
| 1 | 0 | 0 |       |           |        |   | Seul a est vrai |
| 1 | 0 | 1 |       |           |        |   | a et c vrais, b faux |
| 1 | 1 | 0 |       |           |        |   | a et b vrais, c faux |
| 1 | 1 | 1 |       |           |        |   | Toutes les entrées sont vraies |

**c)** (1 pt) Contrôle : vérifier par substitution directe dans l'expression que le résultat est correct pour le cas `a = 1, b = 0, c = 1`.

---

## Question 3 - Analyse et cas limites (4 points)

**a)** (2 pts) Dresser la table de vérité de l'expression `G = (a ET b) OU (NON a ET NON b)`.

| a | b | a ET b | NON a | NON b | NON a ET NON b | G | Justification |
|---|---|--------|-------|-------|----------------|---|---------------|
| 0 | 0 |        |       |       |                |   | Les deux entrées sont fausses |
| 0 | 1 |        |       |       |                |   | Seul b est vrai |
| 1 | 0 |        |       |       |                |   | Seul a est vrai |
| 1 | 1 |        |       |       |                |   | Les deux entrées sont vraies |

**b)** (1 pt) Comparer la table de `G` avec celle de `a XOR b`. Quelle relation lie `G` et `a XOR b` ?

**c)** (1 pt) L'expression `G` est-elle une tautologie, une contradiction, ou ni l'une ni l'autre ? Justifier.


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


## Barème

| Question | Points |
|---|---|
| Question 1 | 5 |
| Question 2 | 6 |
| Question 3 | 4 |
| **Total** | **15** |

## Critères de réussite

Table de vérité correcte avec toutes les combinaisons. Identification des tautologies et contradictions justifiée.

## Séance(s) correspondante(s)

Séance dédiée.
