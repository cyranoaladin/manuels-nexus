---
title: "T17 - Barème - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "bareme"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "Critères observables de programmation dynamique"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - Barème - Programmation dynamique

## Principes

- Total : 20 points.
- Les points d'état, d'initialisation, de récurrence, de trace et de code sont indépendants.
- Un résultat final sans table ni calcul ne reçoit pas les points de méthode.
- Une solution gloutonne est plafonnée aux points de lecture du problème, car elle ne répond pas à la capacité `T-ALGO-04`.

### Barème question 1 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Définit `dp[m]` comme minimum de pièces pour obtenir exactement `m` | 1 | 0,5 si « nombre de pièces » est dit sans minimum ou exactitude |
| Donne `dp[0]=0` | 0,5 | aucun pour `dp[0]=1` |
| Initialise les montants positifs à l'infini/impossible | 0,5 | aucun pour des zéros |
| Écrit le minimum sur `dp[m-p]+1` avec garde `p<=m` | 1,5 | 0,5 formule ; 0,5 ajout de 1 ; 0,5 garde |
| Justifie l'ordre par `m-p < m` | 0,5 | 0,25 pour « les cases précédentes sont connues » |

### Barème question 2 — 6 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Calcule correctement les cases 0 à 4 | 1,5 | 0,3 par case |
| Calcule correctement les cases 5 à 8 | 1,5 | 0,375 par case |
| Écrit pour 8 les candidats 3, 2 et 3 | 1,5 | 0,5 par candidat justifié |
| Donne la solution `[4,4]` | 0,75 | 0,25 pour la valeur minimale 2 seule |
| Explique les soustractions via une table `choix` | 0,75 | 0,25 si `choix` est cité sans reconstruction |

### Barème question 3 — 6 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Initialise table, base et sentinelle | 1,25 | 0,5 base ; 0,75 autres cases |
| Parcourt les montants dans l'ordre croissant | 0,75 | 0,25 pour une boucle non bornée précisément |
| Parcourt les pièces | 0,5 | aucun si une seule pièce est testée |
| Vérifie pièce admissible et prédécesseur atteignable | 1 | 0,5 par garde |
| Calcule et compare `dp[m-p]+1` | 1,25 | 0,75 candidat ; 0,5 minimum |
| Renvoie le minimum ou `None` si impossible | 1,25 | 0,5 retour nominal ; 0,75 décision impossible |

**Plafond.** Table initialisée à zéro partout : au plus 3/6, même si la structure des boucles est correcte.

### Barème question 4 — 4 points

| Critère observable | Points | Partiel |
|---|---:|---|
| Donne les huit états `[0,∞,∞,∞,1,∞,1,∞]` | 1,75 | 0,25 par état correct après le cas de base, plafond 1,75 |
| Explique que la sentinelle ne représente pas un nombre de pièces | 0,75 | 0,25 pour « résultat faux » sans signification |
| Donne `O(Mk)` en temps | 0,75 | 0,5 pour « montant × nombre de pièces » sans notation |
| Donne `O(M)` en mémoire | 0,75 | 0,5 pour « une table de taille M+1 » |

**Total : 4 + 6 + 6 + 4 = 20 points.**

## Grille formative du TD

Un exercice est maîtrisé si l'élève produit une définition interprétable, des bases, des dépendances déjà disponibles, une trace vérifiable, une décision sur l'impossible et une complexité reliée aux boucles.
