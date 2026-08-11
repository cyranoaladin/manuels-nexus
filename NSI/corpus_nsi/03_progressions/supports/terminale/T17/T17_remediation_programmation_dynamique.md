---
title: "T17 - Remédiation - Construire un raisonnement dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "remediation"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "Diagnostic état, initialisation et optimalité"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - Remédiation - Construire un raisonnement dynamique

## Diagnostic

Choisir le parcours correspondant à l'erreur observée :

| Production observée | Diagnostic | Parcours |
|---|---|---|
| « `dp[m]` est le résultat » | état non interprétable | A |
| `dp = [0] * (M+1)` | impossible confondu avec optimum nul | B |
| « je prends toujours la plus grande pièce » | glouton confondu avec dynamique | C |

## Parcours A — Reconstruire l'état

### Représentation alternative

Compléter quatre cases : **indice** `m` ; **objet** un montant exact ; **valeur** nombre de pièces ; **objectif** minimiser.

Assembler ensuite une phrase commençant par « `dp[m]` est... ». Vérifier qu'un autre élève peut expliquer `dp[7]=2` sans voir l'algorithme.

### Tâche de réparation

Pour `[1,5,7]`, interpréter en français `dp[0]=0`, `dp[7]=1` et `dp[10]=2`. Ne pas recalculer la table.

## Parcours B — Distinguer inconnu, impossible et zéro

### Représentation alternative

Utiliser trois étiquettes : **base connue** (`0`), **pas encore calculé** (`∞`), **valeur calculée** (entier positif). Initialiser la table des montants 0 à 6 avec `[4,6]`, puis ne calculer que 4 et 6.

### Tâche de réparation

Expliquer pourquoi le montant 5 doit rester `∞` et pourquoi cette valeur ne peut pas être renvoyée comme un nombre de pièces.

## Parcours C — Comparer deux arbres de choix

### Représentation alternative

Pour `[1,4,5]`, montant 8, dessiner :

- la branche gloutonne `8 → 3 → 2 → 1 → 0` ;
- la branche optimale `8 → 4 → 0`.

Chaque flèche est étiquetée par la pièce soustraite. Comparer le nombre de flèches.

### Tâche de réparation

Formuler ce que la table dynamique compare à l'état 8 et pourquoi elle ne s'engage pas définitivement sur la pièce 5.

## Tâche de sortie isomorphe — sans aide

Pièces `[1,5,6]`, montant 10.

1. Définir l'état et les bases.
2. Écrire la récurrence.
3. Remplir la table 0 à 10.
4. Comparer glouton et optimum.
5. Écrire le test de code qui vérifie le résultat et un test impossible avec les pièces `[6,8]`.

## Critères de sortie

- L'état est interprétable hors du code.
- Zéro et impossible sont distingués.
- Le minimum résulte d'une comparaison de candidats.
- Une table ou une trace justifie la conclusion.
- La tâche finale est réalisée sans reprendre les données des parcours.
