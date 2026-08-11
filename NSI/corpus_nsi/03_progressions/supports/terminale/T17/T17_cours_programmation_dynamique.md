---
title: "T17 - Cours - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "cours"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "Programmation dynamique : état, récurrence, tabulation et reconstruction"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - Cours - Programmation dynamique

## Objectifs spécifiques

À la fin de la séquence, l'élève doit savoir utiliser la programmation dynamique pour écrire un algorithme (`T-ALGO-04`) :

- définir un état qui résume un sous-problème ;
- choisir les cas de base et une valeur représentant l'impossibilité ;
- écrire une relation de récurrence et justifier l'ordre de calcul ;
- remplir une table, reconstruire une solution et analyser les coûts en temps et en mémoire ;
- expliquer sur un contre-exemple pourquoi un choix glouton local peut échouer.

## Prérequis

- Écrire et lire une boucle imbriquée.
- Utiliser une liste Python et la valeur `float("inf")`.
- Comprendre une fonction définie par récurrence.
- Distinguer une valeur optimale du choix qui permet de l'obtenir.

## Situation-problème

Un distributeur dispose de pièces de valeurs 1, 3 et 4. Pour rendre 6, la stratégie « prendre toujours la plus grande pièce possible » choisit 4, puis 1, puis 1 : trois pièces. Pourtant 3 + 3 n'en utilise que deux. Comment écrire un algorithme qui garantit le minimum sans essayer aveuglément toutes les suites de pièces ?

## Activité d'entrée — 8 minutes

1. Pour rendre 6 avec `[1, 3, 4]`, écrire la solution gloutonne puis une meilleure solution.
2. Pour trouver la meilleure solution de montant 6, de quels montants plus petits pourrait-on réutiliser la réponse après avoir choisi une dernière pièce ?
3. Compléter la phrase : « si la dernière pièce vaut `p`, il reste à résoudre le montant ... ».
4. Expliquer pourquoi connaître seulement la meilleure solution du montant 5 ne suffit pas.

Mise en commun : la dernière pièce peut valoir 1, 3 ou 4 ; les sous-problèmes utiles sont donc 5, 3 et 2. Il faut comparer plusieurs prédécesseurs, pas prolonger un seul choix local.

## Définitions et méthode générale

Un **état** associe à chaque sous-problème une valeur dont le sens est écrit explicitement. Une **récurrence** exprime la valeur d'un état à partir d'états plus petits déjà résolus. La méthode générale comporte cinq décisions : définir l'état, fixer les cas de base et la représentation de l'impossible, écrire la récurrence, choisir un ordre de calcul compatible avec les dépendances, puis mémoriser les choix si une solution concrète doit être reconstruite. Cette démarche précède toujours le code.

## 1. Quand parle-t-on de programmation dynamique ?

La programmation dynamique s'applique lorsqu'un problème peut être décomposé en sous-problèmes dont les solutions sont réutilisées. Elle repose ici sur deux propriétés :

- **sous-structure optimale** : une solution optimale de montant `m` contient une solution optimale du montant restant `m - p` ;
- **chevauchement** : les mêmes montants restants apparaissent dans plusieurs branches, donc il est inutile de les recalculer.

Deux organisations sont possibles :

- **mémoïsation** : résolution récursive à la demande, avec mémorisation des résultats déjà obtenus ;
- **tabulation** : calcul itératif des états dans un ordre qui garantit que leurs dépendances sont déjà connues.

Ce cours développe la tabulation, plus simple à tracer en classe.

## 2. Définir l'état avant la formule

Pour un ensemble de pièces `pieces`, on définit :

> `dp[m]` est le nombre minimal de pièces nécessaires pour obtenir exactement le montant `m`.

Cette phrase précise l'indice, la signification et ce qui est optimisé. Écrire seulement « `dp` contient les résultats » est un état ambigu.

### Cas de base et impossibilité

- `dp[0] = 0` : obtenir le montant nul ne demande aucune pièce.
- Au départ, tout montant positif vaut `infini` : il n'est pas encore connu comme atteignable.

Initialiser tous les états à 0 serait faux : cela annoncerait que tout montant peut être rendu sans pièce.

## 3. Écrire la récurrence

Si l'on termine une solution de montant `m` par une pièce `p`, le reste vaut `m - p`. Le candidat utilise donc `dp[m-p] + 1` pièces.

```text
dp[m] = min(dp[m - p] + 1)
        pour les pièces p telles que p <= m
        et dp[m - p] soit atteignable
```

La condition `p <= m` évite un indice négatif. Ignorer un prédécesseur infini évite de présenter une solution impossible comme réelle.

## 4. Construire une table complète

### Méthode autonome — tabuler le rendu minimal

Pour calculer la solution jusqu'à un montant cible `M`, on construit une table de tabulation `dp` :

1. **État** : `dp[m]` est le nombre minimal de pièces nécessaires pour obtenir exactement le montant `m`.
2. **Cas de base** : `dp[0] = 0`, car obtenir zéro ne demande aucune pièce.
3. **Impossible** : pour `m > 0`, on initialise `dp[m] = +∞` ; après le calcul, une valeur encore infinie signifie qu'aucune combinaison ne permet d'obtenir `m` et peut être traduite par `None` dans le résultat du programme.
4. **Récurrence** : pour chaque pièce `p <= m` telle que `dp[m-p]` est possible, on compare le candidat `1 + dp[m-p]`, puis on conserve
   `dp[m] = 1 + min(dp[m-p])` parmi ces prédécesseurs atteignables.
5. **Ordre de calcul** : on remplit la table pour `m = 0, 1, 2, ..., M`, parce que le calcul de `dp[m]` ne consulte que des montants `m-p` strictement plus petits et donc déjà calculés.

La table suivante applique ces cinq étapes aux pièces `[1, 3, 4]` et donne explicitement chaque état de `dp[0]` à `dp[6]`.

### Exemple corrigé 1 — pièces `[1, 3, 4]`, montant 6

Initialisation :

```text
dp = [0, ∞, ∞, ∞, ∞, ∞, ∞]
```

On calcule les montants dans l'ordre croissant.

| `m` | candidats accessibles | minimum retenu | `dp[m]` | dernière pièce possible |
|---:|---|---:|---:|---:|
| 0 | cas de base | 0 | 0 | — |
| 1 | `dp[0] + 1 = 1` | 1 | 1 | 1 |
| 2 | `dp[1] + 1 = 2` | 2 | 2 | 1 |
| 3 | `dp[2] + 1 = 3`, `dp[0] + 1 = 1` | 1 | 1 | 3 |
| 4 | `dp[3] + 1 = 2`, `dp[1] + 1 = 2`, `dp[0] + 1 = 1` | 1 | 1 | 4 |
| 5 | `dp[4] + 1 = 2`, `dp[2] + 1 = 3`, `dp[1] + 1 = 2` | 2 | 2 | 1 ou 4 |
| 6 | `dp[5] + 1 = 3`, `dp[3] + 1 = 2`, `dp[2] + 1 = 3` | 2 | 2 | 3 |

Table finale : `[0, 1, 2, 1, 1, 2, 2]`.

La dernière ligne donne `dp[6] = 2` grâce au candidat `dp[3] + 1 = 2` : comme `dp[3] = 1` avec une pièce de 3, la solution est `3 + 3`. Le choix glouton aurait pris `4 + 1 + 1`, soit trois pièces. **La programmation dynamique ne choisit pas localement la plus grande pièce ; elle conserve les meilleurs résultats des sous-problèmes déjà calculés.**

### Reconstruction

Mémoriser seulement `dp[6] = 2` donne la valeur optimale, pas les pièces. Une seconde table `choix[m]` mémorise une dernière pièce ayant produit le minimum. Ici `choix[6] = 3`, puis on passe à `6 - 3 = 3`, où `choix[3] = 3`. La solution reconstruite est `[3, 3]`.

## 5. Algorithme de tabulation

```python
def rendu_minimal(montant, pieces):
    infini = montant + 1
    dp = [0] + [infini] * montant
    choix = [None] * (montant + 1)

    for m in range(1, montant + 1):
        for p in pieces:
            if p <= m and dp[m - p] != infini:
                candidat = dp[m - p] + 1
                if candidat < dp[m]:
                    dp[m] = candidat
                    choix[m] = p

    if dp[montant] == infini:
        return None

    solution = []
    reste = montant
    while reste > 0:
        p = choix[reste]
        solution.append(p)
        reste = reste - p
    return dp[montant], solution
```

### Invariant utile

Au début du tour de montant `m`, toutes les valeurs `dp[0]` à `dp[m-1]` sont déjà optimales. Chaque candidat de `dp[m]` lit un indice strictement plus petit, donc déjà calculé.

### Complexité

Pour un montant `M` et `k` valeurs de pièces, les deux boucles examinent au plus `M × k` couples : temps `O(Mk)`. Les tables `dp` et `choix` occupent `O(M)` cases.

## 6. Cas impossible

### Exemple corrigé 2 — détecter un montant impossible

Avec les pièces `[4, 6]`, le montant 7 est impossible. Les états 1, 2, 3, 5 et 7 restent infinis. La fonction renvoie `None` lorsque le montant est impossible, jamais « 8 pièces » sous prétexte que l'infini avait été codé par `montant + 1`.

| `m` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp[m]` | 0 | ∞ | ∞ | ∞ | 1 | ∞ | 1 | ∞ |

Le montant 7 ne dispose d'aucun prédécesseur atteignable : `dp[7-4] = dp[3] = ∞` et `dp[7-6] = dp[1] = ∞`. Le résultat `None` vient donc de la table calculée, et non d'une supposition sur la parité.

### Cas limite 1 — montant nul

Pour `montant = 0`, la table contient seulement `[0]`, aucune boucle de reconstruction n'est exécutée et le résultat correct est `(0, [])`. Ce test vérifie que le cas de base est aussi un résultat complet.

### Cas limite 2 — montant positif sans solution

Pour `pieces = [4, 6]` et `montant = 7`, l'algorithme renvoie `None`. Il ne doit ni entrer dans la reconstruction avec `choix[7] = None`, ni confondre la sentinelle `montant + 1` avec un nombre réel de pièces.

## 7. Transfert vers une grille

### Exemple corrigé 3 — coût minimal dans une grille 3 × 3

On veut minimiser le coût d'un chemin de la case en haut à gauche à la case en bas à droite, avec seulement des déplacements vers la droite ou vers le bas.

Définition : `cout[i][j]` est le coût minimal pour atteindre la case `(i, j)`. Initialisation : première case, puis première ligne et première colonne. Récurrence intérieure :

```text
cout[i][j] = grille[i][j] + min(cout[i-1][j], cout[i][j-1])
```

Prenons la grille suivante :

| 1 | 4 | 2 |
|---:|---:|---:|
| 3 | 1 | 5 |
| 2 | 2 | 1 |

La première ligne cumulée vaut `[1, 5, 7]` et la première colonne `[1, 4, 6]`. Les quatre cases intérieures donnent ensuite `5`, `10`, `7` et `8`, d'où la table des coûts :

| 1 | 5 | 7 |
|---:|---:|---:|
| 4 | 5 | 10 |
| 6 | 7 | 8 |

Le coût minimal final est 8. Par exemple, pour la case centrale, `1 + min(5, 4) = 5` : la valeur dépend de voisins déjà calculés. Le principe est le même que pour les pièces : état précis, bases, dépendances ordonnées, choix optimal et table.

## 8. Non-exemples et erreurs fréquentes

| Erreur | Pourquoi elle est fausse | Antidote |
|---|---|---|
| prendre toujours la plus grande pièce | le choix local peut empêcher l'optimum global | chercher un contre-exemple, comme 6 avec `[1,3,4]` |
| initialiser `dp` avec des zéros | les états non calculés semblent déjà optimaux | réserver 0 au seul cas de base, utiliser l'infini ailleurs |
| écrire la récurrence sans définir `dp[m]` | on ne sait pas ce que minimise la formule | écrire une phrase complète avant tout code |
| remplir les montants dans un ordre quelconque | un candidat peut lire un état non calculé | dessiner les dépendances et choisir l'ordre croissant |
| renvoyer seulement `dp[M]` quand les pièces sont demandées | valeur et solution sont confondues | mémoriser aussi `choix[m]` |

### Erreur fréquente 1 — confondre une stratégie gloutonne et une récurrence dynamique

Choisir la plus grande pièce ne compare qu'un choix local. La programmation dynamique compare, pour chaque montant `m`, tous les prédécesseurs atteignables `m-p`. L'antidote est d'écrire la ligne complète des candidats avant de retenir un minimum.

### Erreur fréquente 2 — reconstruire sans mémoriser le choix

La valeur `dp[m]` indique combien de pièces sont nécessaires, pas lesquelles. Tenter de deviner la solution à partir de la seule valeur peut choisir un prédécesseur incompatible. L'antidote est de mettre à jour `choix[m]` exactement au même moment que `dp[m]`.

## Différenciation

### Appui

- Fournir la ligne des candidats et faire seulement choisir le minimum.
- Colorier chaque flèche `m → m-p` avant de remplir la table.
- Donner le squelette des boucles sans les conditions.

### Standard

- Définir l'état, produire la table complète, coder et tester un cas impossible.

### Approfondissement

- Adapter la méthode au coût minimal dans une grille.
- Comparer mémoire complète et mémoire réduite lorsque la reconstruction n'est pas demandée.

## Critères de révision et auto-vérification

1. Mon état dit-il exactement ce que représente chaque indice ?
2. Les cas de base sont-ils suffisants pour démarrer ?
3. Chaque dépendance est-elle calculée avant son utilisation ?
4. Ai-je distingué valeur optimale et reconstruction d'une solution ?
5. Ai-je testé zéro, impossible et une donnée où le glouton échoue ?
