---
title: "T17 - Corrigé - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "corrige"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "État, récurrence, table, reconstruction et complexité"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - Corrigé - Programmation dynamique

## Corrigé du TD

### Exercice 1 — Lire une table

`dp[m]` est le nombre minimal de pièces de valeurs 1, 5 et 7 dont la somme vaut exactement `m`.

Pour 10 :

- dernière pièce 1 : `dp[9] + 1 = 4` ;
- dernière pièce 5 : `dp[5] + 1 = 2` ;
- dernière pièce 7 : `dp[3] + 1 = 4`.

Le minimum vaut 2, obtenu par `5 + 5`. Pour 11, `5 + 5 + 1` utilise trois pièces. Enfin `dp[0] = 0`, car aucun objet n'est nécessaire pour une somme nulle.

**Erreur typique.** Lire `dp[10] = 2` comme « on utilise la pièce 2 » confond valeur optimale et choix.

### Exercice 2 — Table `[1,4,5]`, montant 8

| `m` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp[m]` | 0 | 1 | 2 | 3 | 1 | 1 | 2 | 3 | 2 |

- Pour 5, la dernière pièce 5 donne `dp[0] + 1 = 1`.
- Pour 7, les meilleurs candidats par 1 et par 5 valent tous deux 3.
- Pour 8, la pièce 4 donne `dp[4] + 1 = 2`, meilleur que les candidats par 1 et 5.

Reconstruction : `choix[8] = 4`, reste 4 ; `choix[4] = 4`, reste 0. Solution `[4, 4]`.

### Exercice 3 — Contre-exemple glouton

La stratégie gloutonne choisit `5 + 1 + 1 + 1`, soit quatre pièces. La table dynamique fournit `4 + 4`, soit deux pièces. Un exemple où la règle donne une solution non optimale suffit à réfuter l'affirmation « cette règle est toujours optimale ». Il ne prouve pas que toute stratégie gloutonne échoue sur toute donnée.

### Exercice 4 — Algorithme

```python
def minimum_pieces(montant, pieces):
    infini = montant + 1
    dp = [0] + [infini] * montant
    for m in range(1, montant + 1):
        for p in pieces:
            if p <= m and dp[m - p] != infini:
                dp[m] = min(dp[m], dp[m - p] + 1)
    if dp[montant] == infini:
        return None
    return dp[montant]
```

Tests : `minimum_pieces(8, [1,4,5]) == 2`, `minimum_pieces(0, [4,6]) == 0`, `minimum_pieces(7, [4,6]) is None`. Temps `O(Mk)`, mémoire `O(M)`.

### Exercice 5 — Débogage

Avec une table remplie de zéros, `dp[1]` compare 0 à `dp[0]+1 = 1` et reste 0 ; le même phénomène se répète. Les zéros prétendent que les montants positifs sont déjà atteignables sans pièce.

Correction :

```python
infini = montant + 1
dp = [0] + [infini] * montant
```

Après les boucles, convertir `dp[montant] == infini` en `None`. Le test `minimum_pieces(1, [4,5]) is None` détecte immédiatement l'initialisation fautive.

### Exercice 6 — Grille

`cout[i][j]` est le coût minimal d'un chemin de `(0,0)` à `(i,j)`. La première case vaut 1. La première ligne se cumule depuis la gauche ; la première colonne depuis le haut. À l'intérieur :

```text
cout[i][j] = grille[i][j] + min(cout[i-1][j], cout[i][j-1])
```

Table obtenue :

```text
1 5 7
3 6 7
8 8 8
```

Le coût minimal final vaut 8. Un parcours ligne par ligne convient car les cases du haut et de gauche sont déjà calculées. Temps `O(nm)`, mémoire `O(nm)` pour une grille `n × m`.

## Corrigé de l'évaluation

### Question 1 — Modélisation

`dp[m]` est le nombre minimal de pièces de `[1,4,6]` dont la somme vaut exactement `m`. Initialisation : `dp[0]=0`, les autres cases valent `∞`. Récurrence :

```text
dp[m] = 1 + min(dp[m-p]) pour p dans pieces, p <= m, dp[m-p] fini
```

L'ordre croissant est valide car `m-p` est strictement inférieur à `m` pour toute pièce positive.

### Question 2 — Table et reconstruction

| `m` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp[m]` | 0 | 1 | 2 | 3 | 1 | 2 | 1 | 2 | 2 |

Pour 8 : par 1, `dp[7]+1=3` ; par 4, `dp[4]+1=2` ; par 6, `dp[2]+1=3`. Le minimum vaut 2. En mémorisant `choix[8]=4`, puis `choix[4]=4`, on reconstruit `[4,4]`.

### Question 3 — Algorithme

```python
def minimum_pieces(montant, pieces):
    infini = montant + 1
    dp = [0] + [infini] * montant
    for m in range(1, montant + 1):
        for p in pieces:
            if p <= m and dp[m - p] != infini:
                candidat = dp[m - p] + 1
                if candidat < dp[m]:
                    dp[m] = candidat
    return None if dp[montant] == infini else dp[montant]
```

Une variante calculant directement un `min` sur les candidats accessibles est acceptée.

### Question 4 — Impossible et complexité

| `m` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp[m]` | 0 | ∞ | ∞ | ∞ | 1 | ∞ | 1 | ∞ |

La sentinelle numérique `montant+1` signifie « aucun calcul n'a trouvé de solution » ; la renvoyer comme un nombre de pièces serait un contresens. Temps `O(Mk)` et mémoire `O(M)`.

## Principes de correction

- Une table correcte avec une formule imprécise conserve les points de calcul, pas ceux de modélisation.
- Une erreur sur une case ne doit pas annuler les cases ultérieures correctement recalculées à partir d'une table explicitement rectifiée.
- Un algorithme glouton, même juste sur l'exemple, ne répond pas à la consigne dynamique.
- Le montant impossible doit être signalé par `None` (conformément au TP, aux tests attendus et au barème) ; la sentinelle interne ne doit jamais être présentée comme un nombre de pièces.
