---
title: "T17 - Version aménagée - Programmation dynamique"
level: "terminale"
sequence_id: "T17"
document_type: "version_amenagee"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Algorithmique"
notion: "Construction guidée d'une table dynamique"
private_data: false
official_program:
  capacities:
    - "T-ALGO-04"
---

# T17 - Version aménagée - Programmation dynamique

## Objectif conservé

Construire puis utiliser une table dynamique pour `pieces = [1, 4, 6]` et `montant = 8`. Les étapes réduisent la charge de planification, mais les valeurs finales et le code restent à produire.

## Étape 1 — Définir avant de calculer

Compléter avec les mots `exactement`, `minimal`, `pièces`, `montant` :

> `dp[m]` est le nombre __________ de __________ nécessaires pour obtenir __________ le __________ `m`.

## Étape 2 — Initialiser

Choisir et justifier :

- `dp[0]` vaut : [ ] 0  [ ] 1  [ ] ∞
- avant calcul, `dp[1]` vaut : [ ] 0  [ ] 1  [ ] ∞

Compléter : zéro signifie `________________` ; l'infini signifie `________________`.

## Étape 3 — Calculer avec une fiche-candidat

Pour chaque montant `m`, remplir seulement les lignes correspondant à une pièce `p <= m`.

| `m` | pièce `p` | état précédent `m-p` | `dp[m-p]` | candidat `dp[m-p]+1` |
|---:|---:|---:|---:|---:|
| 4 | 1 |  |  |  |
| 4 | 4 |  |  |  |
| 6 | 1 |  |  |  |
| 6 | 4 |  |  |  |
| 6 | 6 |  |  |  |
| 8 | 1 |  |  |  |
| 8 | 4 |  |  |  |
| 8 | 6 |  |  |  |

Reporter ensuite les minima sans recopier un résultat fourni :

| `m` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp[m]` | 0 |  |  |  |  |  |  |  |  |

## Étape 4 — Assembler l'algorithme

Numéroter les actions dans l'ordre, puis compléter les blancs :

```text
initialiser dp[0] à _____ et les autres cases à _____
pour m allant de _____ à montant :
    pour chaque pièce p :
        si p <= _____ et l'état précédent est atteignable :
            candidat = dp[_____ - p] + _____
            dp[m] = min(________________, ________________)
```

## Étape 5 — Décider un impossible

Avec `[4,6]` et le montant 7, entourer les montants atteignables parmi 0 à 7. Écrire une phrase expliquant ce que la case finale doit provoquer dans la fonction.

### Espace de réponse guidé — table et récurrence

Utiliser cette grille pour préparer le calcul, sans recopier de valeurs finales.

| montant `m` | valeur précédente utilisée `m-p` | pièce choisie `p` | `dp[m]` à compléter |
|---:|---:|---:|---:|
| 4 |  |  |  |
| 6 |  |  |  |
| 8 |  |  |  |

- Montant impossible : [ ] oui  [ ] non ; montant concerné : `________________`.
- Récurrence : `dp[m] = ________________________________________________________________`.
- Le calcul suit l'ordre croissant parce que `________________________________________________`.

## Aides à dévoilement progressif

1. **Aide légère** : une pièce choisie en dernier laisse le montant `m-p`.
2. **Aide intermédiaire** : le montant courant compare un candidat par pièce admissible.
3. **Aide forte** : la boucle extérieure doit suivre 1, 2, 3, ..., montant pour que `m-p` soit déjà connu.

## Auto-contrôle

- [ ] Je peux expliquer une case avec une phrase.
- [ ] Je n'ai pas initialisé tous les montants à zéro.
- [ ] J'ai ignoré une pièce plus grande que le montant courant.
- [ ] J'ai comparé tous les candidats admissibles.
- [ ] Je distingue la sentinelle interne du résultat renvoyé à l'utilisateur.
