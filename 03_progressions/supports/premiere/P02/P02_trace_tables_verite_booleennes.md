---
title: "P02 - Trace - Tables de vérité booléennes"
level: "premiere"
sequence_id: "P02"
document_type: "trace"
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

# P02 - Trace - Tables de vérité booléennes

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

---

## Ce qu'il faut retenir

### Les quatre opérateurs logiques fondamentaux

**ET (AND)** : vaut 1 seulement si les deux opérandes valent 1.

**OU (OR)** : vaut 1 si au moins un opérande vaut 1.

**NON (NOT)** : inverse la valeur (0 devient 1, 1 devient 0).

**XOR (ou exclusif)** : vaut 1 si exactement un opérande vaut 1.

### Tables de référence

| a | b | a ET b | a OU b | a XOR b | Commentaire |
|---|---|--------|--------|---------|-------------|
| 0 | 0 |   0    |   0    |    0    | Aucun opérande vrai |
| 0 | 1 |   0    |   1    |    1    | Seul b est vrai |
| 1 | 0 |   0    |   1    |    1    | Seul a est vrai |
| 1 | 1 |   1    |   1    |    0    | Les deux sont vrais |

| a | NON a |
|---|-------|
| 0 |   1   |
| 1 |   0   |

### Nombre de lignes
Pour `n` variables, la table comporte `2^n` lignes (2 variables : 4 lignes ; 3 variables : 8 lignes).

---

## Méthode pour dresser la table d’une expression booléenne

1. **Identifier** les variables de l'expression.
2. **Compter** le nombre de lignes : `2^n`.
3. **Lister** toutes les combinaisons (compter en binaire).
4. **Décomposer** l'expression en sous-expressions intermédiaires.
5. **Évaluer** chaque ligne de l'intérieur vers l'extérieur.
6. **Contrôler** sur un cas limite (toutes les entrées à 0, toutes à 1).

---

## Exemple résolu : `(a OU b) ET (NON a)`

**Étape 1** : Variables : `a`, `b` (2 variables).

**Étape 2** : Nombre de lignes : `2^2 = 4`.

**Étape 3 et 4** : Sous-expressions : `a OU b`, `NON a`, puis le résultat final.

**Étape 5** : Évaluation ligne par ligne.

| a | b | a OU b | NON a | (a OU b) ET (NON a) | Justification |
|---|---|--------|-------|---------------------|---------------|
| 0 | 0 |   0    |   1   |         0           | OU faux, le ET donne faux |
| 0 | 1 |   1    |   1   |         1           | OU vrai et NON a vrai, le ET donne vrai |
| 1 | 0 |   1    |   0   |         0           | NON a faux, le ET donne faux |
| 1 | 1 |   1    |   0   |         0           | NON a faux, le ET donne faux |

**Étape 6** : Contrôle. Cas `a = 0, b = 0` : `OU` donne 0, `ET` avec 1 donne 0. Cas `a = 1, b = 1` : `NON a` donne 0 donc le `ET` donne 0. Résultats cohérents.

Conclusion : cette expression est équivalente à `(NON a) ET b`.

---

## Vocabulaire essentiel

- **Tautologie** : expression toujours vraie (exemple : `a OU NON a`).
- **Contradiction** : expression toujours fausse (exemple : `a ET NON a`).
- **XOR et addition binaire** : `a XOR b` donne le bit de somme, `a ET b` donne la retenue.

---

## Lois de De Morgan (à connaître)

- `NON(a ET b) = (NON a) OU (NON b)`
- `NON(a OU b) = (NON a) ET (NON b)`


## Situation-problème

Un ingénieur réseau reçoit un paquet de 8 bits et doit déterminer si les données représentent un entier positif ou négatif. Comment distinguer les deux cas sans information supplémentaire ?

## Activité d’entrée

Compléter la table de vérité de l'expression A ET (NON B) pour toutes les combinaisons possibles de A et B.

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
