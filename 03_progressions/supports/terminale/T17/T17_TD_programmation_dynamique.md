---
title: "T17 - TD - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "td"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "État, récurrence, tabulation, débogage et transfert"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - TD - Programmation dynamique

## Organisation

Durée indicative : 70 minutes. Capacité travaillée dans chaque exercice : `T-ALGO-04`.

- Socle : exercices 1 et 2.
- Standard : exercices 3 à 5.
- Approfondissement : exercice 6.

Chaque livrable doit faire apparaître l'état, l'initialisation, la récurrence ou le choix d'ordre pertinent ; une valeur finale seule ne suffit pas.

## Exercices

### Exercice 1 — Lire une table [socle, 8 min]

Pour les pièces `[1, 5, 7]`, on donne la table :

```text
m     0 1 2 3 4 5 6 7 8 9 10 11
dp[m] 0 1 2 3 4 1 2 1 2 3  2  3
```

1. Formuler précisément ce que représente `dp[m]`.
2. Expliquer, à partir de trois candidats, pourquoi `dp[10] = 2`.
3. Proposer une décomposition optimale de 11.
4. Dire ce que vaut `dp[0]` et pourquoi.

**Livrable.** Définition d'état, calcul de candidats, décomposition et cas de base.

### Exercice 2 — Construire une table de trace [socle, 12 min]

Pièces `[1, 4, 5]`, montant 8.

1. Initialiser `dp[0..8]` avec 0 et l'infini.
2. Compléter la table de trace en donnant, pour chaque montant, les candidats accessibles et le minimum.
3. Entourer la dernière pièce retenue pour les montants 5, 7 et 8.
4. Reconstruire une solution optimale de montant 8.

**Livrable.** Table complète de 0 à 8 et reconstruction par soustractions successives.

### Exercice 3 — Produire un contre-exemple glouton [standard, 8 min]

Toujours avec `[1, 4, 5]` et le montant 8 :

1. Tracer la stratégie qui prend toujours la plus grande pièce possible.
2. Comparer son nombre de pièces au résultat de la table dynamique.
3. Expliquer en deux phrases pourquoi cet exemple invalide la règle gloutonne générale, sans prétendre que toute stratégie gloutonne échoue toujours.

**Livrable.** Deux décompositions, deux nombres de pièces et conclusion logique.

### Exercice 4 — Écrire l'algorithme [standard, 15 min]

Écrire une fonction `minimum_pieces(montant, pieces)` qui renvoie le nombre minimal de pièces, ou `None` si le montant est impossible.

Exigences :

- `dp[0] = 0` et les autres cases commencent à l'infini ;
- boucle extérieure sur les montants croissants ;
- une pièce trop grande est ignorée ;
- un prédécesseur impossible ne devient pas une solution ;
- cas testés : `(8, [1,4,5])`, `(0, [4,6])`, `(7, [4,6])`.

**Livrable.** Code ou pseudo-code structuré, résultats des trois tests, Complexité en temps et en mémoire.

### Exercice 5 — Déboguer [standard, 12 min]

```python
def minimum_pieces(montant, pieces):
    dp = [0] * (montant + 1)
    for m in range(1, montant + 1):
        for p in pieces:
            if p <= m:
                dp[m] = min(dp[m], dp[m - p] + 1)
    return dp[montant]
```

1. Tracer les cases `dp[1]` et `dp[2]` avec `pieces = [1, 4, 5]`.
2. Diagnostiquer l'erreur d'initialisation et expliquer pourquoi toutes les cases restent 0.
3. Corriger l'initialisation et le traitement du montant impossible.
4. Donner un test qui aurait détecté l'erreur immédiatement.

**Livrable.** Trace courte, cause, correction locale et test discriminant.

### Exercice 6 — Transfert sur une grille [approfondissement, 15 min]

On part en haut à gauche et l'on se déplace seulement à droite ou en bas.

```text
1 4 2
2 3 1
5 2 1
```

1. Définir `cout[i][j]`.
2. Donner les initialisations de la première case, de la première ligne et de la première colonne.
3. Écrire la récurrence pour une case intérieure.
4. Remplir la grille des coûts minimaux et donner le coût final.
5. Justifier l'ordre ligne par ligne et la Complexité temporelle.

**Livrable.** État, bases, récurrence, grille 3 × 3 remplie, résultat et analyse.

## Corrigé intégré enseignant

### Corrigé exercice 1

- **Donnée utilisée** : pièces `[1,5,7]`, table fournie jusqu'à 11.
- **Méthode** : interpréter `dp[m]`, puis comparer pour 10 les candidats 4, 2 et 4.
- **Résultat** : `dp[10]=2` par `5+5` ; `dp[11]=3` par `5+5+1` ; `dp[0]=0`.
- **Vérification** : chaque décomposition somme au montant et contient le nombre annoncé de pièces.

### Corrigé exercice 2

- **Donnée utilisée** : pièces `[1,4,5]`, montant 8.
- **Méthode** : initialisation 0/infini, récurrence sur les prédécesseurs atteignables, trace croissante.
- **Résultat** : table `[0,1,2,3,1,1,2,3,2]`, reconstruction `8 → 4 → 0`, donc `[4,4]`.
- **Erreur traitée** : la valeur `dp[8]=2` ne suffit pas à retrouver les pièces sans table `choix`.

### Corrigé exercice 3

- **Donnée utilisée** : même système, comparaison de deux méthodes.
- **Méthode** : tracer glouton et optimum séparément, puis comparer le nombre de décisions.
- **Résultat** : glouton `5+1+1+1`, quatre pièces ; dynamique `4+4`, deux pièces.
- **Contrôle logique** : ce contre-exemple réfute une garantie universelle, pas tous les usages possibles du glouton.

### Corrigé exercice 4

- **Méthode** : table initialisée par `[0] + [infini] * montant`, deux boucles et récurrence `dp[m-p]+1`.
- **Résultats** : `2`, `0`, puis `None` pour les trois tests demandés.
- **Invariant** : avant le montant `m`, les états d'indice plus petit sont optimaux.
- **Complexité** : `O(Mk)` en temps et `O(M)` en mémoire.

### Corrigé exercice 5

- **Trace** : avec des zéros, `min(0, dp[0]+1)` laisse `dp[1]=0`, puis toutes les cases restent nulles.
- **Méthode de correction** : utiliser l'infini pour les montants positifs et convertir la sentinelle finale en `None`.
- **Test discriminant** : `minimum_pieces(1, [4,5]) is None`.
- **Erreur traitée** : inconnu ou impossible ne signifie pas optimum nul.

### Corrigé exercice 6

- **État** : `cout[i][j]` est le coût minimal pour atteindre `(i,j)`.
- **Récurrence** : valeur de la case plus le minimum entre le haut et la gauche, après initialisation des bords.
- **Résultat** : grille des coûts `[[1,5,7],[3,6,7],[8,8,8]]`, coût final 8.
- **Complexité et contrôle** : `O(nm)` ; chaque dépendance est calculée avant la case courante.

## Aides graduées

1. Écrire « `dp[m]` représente ... » avant toute formule.
2. Pour un montant `m`, lister seulement les pièces `p <= m`.
3. Transformer chaque pièce en flèche `m → m-p`.
4. Si aucun prédécesseur n'est atteignable, conserver l'infini.

## Cas limites et erreurs fréquentes

- **Cas limite 1 — montant nul.** La table se réduit à `dp[0] = 0` et la reconstruction produit la liste vide ; aucune pièce ne doit être choisie artificiellement.
- **Cas limite 2 — montant impossible.** Avec `[4, 5]` et le montant 1, aucun prédécesseur n'est atteignable : la sentinelle doit être convertie en `None`.
- **Erreur fréquente 1 — initialiser toutes les cases à zéro.** Cela transforme « non calculé » en faux optimum. Antidote : réserver zéro au cas de base et utiliser une sentinelle pour les autres états.
- **Erreur fréquente 2 — mémoriser le minimum sans le choix.** La valeur optimale ne suffit pas à reconstruire les pièces. Antidote : mettre à jour `choix[m]` dans la même branche que `dp[m]`.

## Critères de réussite

- La définition de l'état permet d'interpréter une case sans relire l'algorithme.
- Chaque table commence par un cas de base correct.
- La relation utilise uniquement des états déjà calculés.
- Le cas impossible est distingué d'un grand nombre de pièces.
- Le code et les tables conduisent aux mêmes résultats.
