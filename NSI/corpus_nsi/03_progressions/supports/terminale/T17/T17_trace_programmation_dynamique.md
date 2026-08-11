---
title: "T17 - Trace écrite - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "trace"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "Méthode de programmation dynamique"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - Trace écrite - Programmation dynamique

## Définition

La programmation dynamique résout des sous-problèmes qui se chevauchent, mémorise leur solution et les combine pour obtenir une solution globale optimale.

## Quand l'utiliser ?

- Un état plus grand dépend de plusieurs états plus petits.
- Les mêmes sous-problèmes réapparaissent.
- Un choix local évident n'est pas toujours optimal.

## Méthode en six étapes

1. **État** : écrire une phrase définissant chaque case, par exemple « `dp[m]` est le nombre minimal de pièces pour obtenir exactement `m` ».
2. **Bases** : fixer `dp[0]=0` et une sentinelle infinie pour les états inconnus ou impossibles.
3. **Récurrence** : exprimer `dp[m]` à partir d'états plus petits.
4. **Ordre** : calculer un état seulement lorsque ses dépendances sont disponibles.
5. **Trace** : conserver candidats, minimum et éventuellement le choix retenu.
6. **Contrôles** : tester zéro, impossible et contre-exemple glouton.

## Exemple complet — pièces `[1,3,4]`, montant 6

```text
dp[m] = min(dp[m-p] + 1) pour p <= m
dp[0] = 0 ; autres cases = ∞
```

| `m` | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp[m]` | 0 | 1 | 2 | 1 | 1 | 2 | 2 |
| choix possible | — | 1 | 1 | 3 | 4 | 1 ou 4 | 3 |

Reconstruction : 6 → 3 → 0, donc `[3,3]`. Le glouton 4 + 1 + 1 utilise trois pièces et n'est pas optimal.

## Invariant de tabulation

Avant de calculer le montant `m`, toutes les cases d'indice strictement inférieur sont déjà optimales. Comme toute pièce est positive, `m-p < m`.

## Coûts

Avec un montant `M` et `k` pièces : temps `O(Mk)`, mémoire `O(M)`.

## Pièges et antidotes

| Piège | Antidote |
|---|---|
| état « `dp` contient les résultats » | préciser indice, sens, exactitude et grandeur optimisée |
| table initialisée à zéro | réserver zéro au cas de base, utiliser l'infini ailleurs |
| lire `dp[m-p]` avant calcul | dessiner les dépendances et remplir par montants croissants |
| renvoyer l'infini comme réponse | convertir l'état final impossible en `None` |
| confondre minimum et pièces choisies | mémoriser une seconde table `choix` |

## Cas limites

- `montant = 0` : réponse 0 et solution vide.
- pièce plus grande que le montant courant : elle est ignorée.
- aucun prédécesseur atteignable : la case reste infinie.
- liste de pièces vide pour un montant positif : impossible.

## Auto-vérification

1. Puis-je interpréter `dp[5]` sans lire le code ?
2. Ai-je écrit les bases avant la récurrence ?
3. Chaque candidat correspond-il à une dernière décision possible ?
4. La table prouve-t-elle le résultat final ?
5. Si une solution concrète est demandée, ai-je mémorisé les choix ?
